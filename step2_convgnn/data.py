"""
Purpose: Convert ADPPG PRCS subgraphs into PyG graphs for the relation-aware ConvGNN.
Input:   data/dataset/adppg.jsonl + splits.json.
Output:  lists of torch_geometric.data.Data (one graph per PRCS) per split.

Each node carries an integer type id (-> learned embedding in the model) plus a structural/
privacy feature vector (is_source/is_sink/permission/sink-type/PI-category one-hots) with a
zero-filled slot reserved as the statement-token-embedding HOOK. Edges carry an integer
relation type for RGCN. Labels are graph-level multi-hot for the two heads.

Design note: we use a homogeneous Data with `edge_type` (RGCN) rather than HeteroData.
The PRCS graphs are small and sparse with low node/edge-type cardinality; RGCN over typed
edges gives the same relation-awareness with far less plumbing (justified in FINDINGS).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import torch
from torch_geometric.data import Data

from pplib.schema import PPG_EDGE_TYPES, PPG_NODE_LABELS, PRACTICE_LABELS, PURPOSE_LABELS

# Fixed vocabularies (stable feature layout).
NODE_TYPES = PPG_NODE_LABELS                       # 8 node labels
REL_TYPES = PPG_EDGE_TYPES                         # 7 relation types
SINK_TYPES = ["network", "storage", "logging", "ipc", "serialization", "heuristic_unknown"]
PI_CATEGORIES = [
    "LOCATION_INFORMATION", "UNIQUE_IDENTIFIER", "PHONE_INFORMATION", "ACCOUNT_INFORMATION",
    "CONTACT_INFORMATION", "CALENDAR_INFORMATION", "SMS_MMS", "BROWSER_INFORMATION",
    "NETWORK_INFORMATION", "BLUETOOTH_INFORMATION", "IMAGE", "AUDIO", "OTHER",
]

_NODE_TYPE_IX = {t: i for i, t in enumerate(NODE_TYPES)}
_REL_IX = {t: i for i, t in enumerate(REL_TYPES)}
_SINK_IX = {t: i for i, t in enumerate(SINK_TYPES)}
_PI_IX = {t: i for i, t in enumerate(PI_CATEGORIES)}

TOKEN_HOOK_DIM = 8        # reserved zero slot for future statement-token embeddings
FEAT_DIM = 2 + 1 + len(SINK_TYPES) + len(PI_CATEGORIES) + TOKEN_HOOK_DIM
NUM_NODE_TYPES = len(NODE_TYPES)
NUM_RELATIONS = len(REL_TYPES)


def _truthy(v) -> bool:
    return str(v).lower() in ("1", "true", "yes")


_TOKEN_BASE = FEAT_DIM - TOKEN_HOOK_DIM     # start index of the token-hook block


def _stable_hash(tok: str) -> int:
    """Deterministic hash (PYTHONHASHSEED-independent) for the hashing-trick token encoder."""
    return int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)


def _tokens(n: dict) -> List[str]:
    """Lexical tokens from a node's code + callee (camelCase + non-alnum split)."""
    text = f"{n.get('code', '')} {n.get('callee', '')}"
    parts = re.findall(r"[A-Z]+(?![a-z])|[A-Z][a-z]+|[a-z]+|\d+", text)
    return [p.lower() for p in parts if len(p) > 1]


def _node_features(n: dict, privacy_features: bool = True,
                   token_features: bool = False) -> Tuple[int, List[float]]:
    """Return (type_id, feature_vector) for one subgraph node.

    privacy_features=False is the APG-ONLY ablation: the node keeps its type embedding and the
    graph keeps its structure/edges, but the PPG privacy overlay vector (source/sink/permission/
    sink-type/PI-category) is zeroed — isolating the contribution of the overlay.
    token_features=True fills the reserved TOKEN_HOOK_DIM slots with a hashing-trick bag-of-tokens
    over the node's code+callee (the statement-token-embedding hook), L1-normalized.
    """
    type_id = _NODE_TYPE_IX.get(n.get("label", ""), _NODE_TYPE_IX["Statement"])
    feat = [0.0] * FEAT_DIM
    if privacy_features:
        feat[0] = 1.0 if _truthy(n.get("is_source")) else 0.0
        feat[1] = 1.0 if _truthy(n.get("is_sink")) else 0.0
        feat[2] = 1.0 if n.get("permission") else 0.0
        base = 3
        st = n.get("sink_type", "")
        if st in _SINK_IX:
            feat[base + _SINK_IX[st]] = 1.0
        base += len(SINK_TYPES)
        cat = n.get("category", "") or ""
        feat[base + _PI_IX.get(cat, _PI_IX["OTHER"])] = 1.0 if cat else 0.0
    if token_features:
        toks = _tokens(n)
        for tok in toks:
            feat[_TOKEN_BASE + (_stable_hash(tok) % TOKEN_HOOK_DIM)] += 1.0
        s = sum(feat[_TOKEN_BASE:])
        if s > 0:
            for i in range(_TOKEN_BASE, FEAT_DIM):
                feat[i] /= s
    return type_id, feat


def record_to_data(rec: dict, privacy_features: bool = True,
                   token_features: bool = False) -> Data:
    """Convert one ADPPG record (with subgraph + labels) into a PyG Data graph."""
    nodes = rec["subgraph"]["nodes"]
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    type_ids, feats = [], []
    for n in nodes:
        t, f = _node_features(n, privacy_features, token_features)
        type_ids.append(t)
        feats.append(f)

    src, dst, etype = [], [], []
    for e in rec["subgraph"]["edges"]:
        if e["start"] in idx and e["end"] in idx:
            src.append(idx[e["start"]])
            dst.append(idx[e["end"]])
            etype.append(_REL_IX.get(e["type"], 0))
    if not src:                       # guarantee at least a self-loop so conv is defined
        src, dst, etype = [0], [0], [0]

    labels = rec["labels"]
    y_pr = [1.0 if l in labels.get("practice", []) else 0.0 for l in PRACTICE_LABELS]
    y_pu = [1.0 if l in labels.get("purpose", []) else 0.0 for l in PURPOSE_LABELS]

    data = Data(
        x=torch.tensor(feats, dtype=torch.float),
        node_type=torch.tensor(type_ids, dtype=torch.long),
        edge_index=torch.tensor([src, dst], dtype=torch.long),
        edge_type=torch.tensor(etype, dtype=torch.long),
        y_practice=torch.tensor([y_pr], dtype=torch.float),
        y_purpose=torch.tensor([y_pu], dtype=torch.float),
    )
    data.prcs_id = rec["prcs_id"]
    data.label_source = labels.get("label_source", "weak")
    return data


def load_splits(dataset_dir: str | Path, privacy_features: bool = True,
                token_features: bool = False) -> Dict[str, List[Data]]:
    """Load adppg.jsonl + splits.json -> {split: [Data,...]}.

    privacy_features=False loads the APG-ONLY ablation view (privacy overlay zeroed).
    token_features=True fills the reserved statement-token-embedding hook.
    """
    dataset_dir = Path(dataset_dir)
    records = {}
    with open(dataset_dir / "adppg.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            records[r["prcs_id"]] = r
    with open(dataset_dir / "splits.json", encoding="utf-8") as f:
        splits = json.load(f)
    return {s: [record_to_data(records[pid], privacy_features, token_features)
                for pid in ids if pid in records]
            for s, ids in splits.items()}
