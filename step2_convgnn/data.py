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

import json
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


def _node_features(n: dict) -> Tuple[int, List[float]]:
    """Return (type_id, feature_vector) for one subgraph node."""
    type_id = _NODE_TYPE_IX.get(n.get("label", ""), _NODE_TYPE_IX["Statement"])
    feat = [0.0] * FEAT_DIM
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
    # remaining TOKEN_HOOK_DIM slots stay zero (hook).
    return type_id, feat


def record_to_data(rec: dict) -> Data:
    """Convert one ADPPG record (with subgraph + labels) into a PyG Data graph."""
    nodes = rec["subgraph"]["nodes"]
    idx = {n["id"]: i for i, n in enumerate(nodes)}
    type_ids, feats = [], []
    for n in nodes:
        t, f = _node_features(n)
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


def load_splits(dataset_dir: str | Path) -> Dict[str, List[Data]]:
    """Load adppg.jsonl + splits.json -> {split: [Data,...]}."""
    dataset_dir = Path(dataset_dir)
    records = {}
    with open(dataset_dir / "adppg.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            records[r["prcs_id"]] = r
    with open(dataset_dir / "splits.json", encoding="utf-8") as f:
        splits = json.load(f)
    return {s: [record_to_data(records[pid]) for pid in ids if pid in records]
            for s, ids in splits.items()}
