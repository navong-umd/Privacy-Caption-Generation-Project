"""
Purpose: STEP 2 - slice one Permission-Requiring Code Segment (PRCS) per source->sink flow.
Input:   a PPG (ppg.pkl + taint_paths.json from Stage 4), or a live PPGBuilder.
Output:  data/prcs/<prcs_id>.json (record + subgraph) and prcs_index.csv (metadata, no subgraph).

A PRCS = the subgraph of every method touched by a taint path (all their statements +
intra/inter edges) plus the privacy overlay (Source/Sink/DataItem) — enough structure for
the ConvGNN and a readable snippet for Codr/captioning.

Run: python -m step2_prcs.extract_prcs --ppg data/ppg --out data/prcs
"""
from __future__ import annotations

import argparse
import hashlib
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx
import pandas as pd

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_json, parse_app_id
from pplib.io_utils import method_class, method_short_name, stmt_method_id

log = get_logger("extract_prcs")

# fields written to the flat index CSV (subgraph/snippet live in the per-PRCS JSON)
INDEX_COLUMNS = [
    "prcs_id", "app_package", "apk_filename", "class_name", "method_name",
    "method_signature", "source_api", "sink_api", "sink_type", "pi_type",
    "permission", "privacy_threat", "hop_count", "n_nodes", "n_edges",
]


@dataclass
class PRCS:
    prcs_id: str
    app_package: str
    apk_filename: str
    class_name: str
    method_name: str
    method_signature: str
    source_api: str
    sink_api: str
    sink_type: str
    sink_label: str
    pi_type: str
    pi_category: str
    permission: str
    privacy_threat: str
    hop_count: int
    code_snippet: str
    subgraph: dict
    involved_methods: List[str] = field(default_factory=list)

    def index_row(self) -> dict:
        return {
            "prcs_id": self.prcs_id, "app_package": self.app_package,
            "apk_filename": self.apk_filename, "class_name": self.class_name,
            "method_name": self.method_name, "method_signature": self.method_signature,
            "source_api": self.source_api, "sink_api": self.sink_api,
            "sink_type": self.sink_type, "pi_type": self.pi_type,
            "permission": self.permission, "privacy_threat": self.privacy_threat,
            "hop_count": self.hop_count,
            "n_nodes": len(self.subgraph["nodes"]), "n_edges": len(self.subgraph["edges"]),
        }


def _stable_id(app_id: str, src: str, snk: str) -> str:
    return "prcs_" + hashlib.sha1(f"{app_id}|{src}|{snk}".encode()).hexdigest()[:12]


def _method_statements(G: nx.MultiDiGraph, method_id: str) -> List[str]:
    """Statement ids of a method, ordered by statement index."""
    stmts = [v for _, v, k in G.out_edges(method_id, keys=True)
             if k == "HAS_STATEMENT"]
    return sorted(stmts, key=lambda s: _idx(s))


def _idx(stmt_id: str) -> int:
    try:
        return int(stmt_id.rsplit("_stmt_", 1)[1])
    except Exception:
        return 0


def _slice(G: nx.MultiDiGraph, methods: Set[str]) -> Set[str]:
    """Collect nodes for the PRCS: methods, their classes/statements, and overlay nodes."""
    nodes: Set[str] = set()
    for m in methods:
        if m not in G:
            continue
        nodes.add(m)
        nodes.add(method_class(m))                       # class node
        for s in _method_statements(G, m):
            nodes.add(s)
            # privacy overlay attached to this statement (Source/Sink + their DataItem/Store/...)
            for _, ov, k in G.out_edges(s, keys=True):
                if k == "PRIVACY_RELATION":
                    nodes.add(ov)
                    for _, ov2, k2 in G.out_edges(ov, keys=True):
                        if k2 == "PRIVACY_RELATION":
                            nodes.add(ov2)
    return nodes


def _build_snippet(G: nx.MultiDiGraph, methods: List[str]) -> str:
    """Render a readable code snippet: one block per involved method."""
    blocks = []
    for m in methods:
        if m not in G:
            continue
        lines = [f"// {m}"]
        for s in _method_statements(G, m):
            code = G.nodes[s].get("code", "") or G.nodes[s].get("type", "")
            lines.append(f"  {code}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def extract_from_graph(G: nx.MultiDiGraph, taint_paths: List[dict]) -> List[PRCS]:
    """Build one PRCS per taint path from a PPG graph + taint paths."""
    out: List[PRCS] = []
    for tp in taint_paths:
        src, snk = tp["source_stmt"], tp["sink_stmt"]
        path = tp["path"]
        app_id = tp.get("app_id") or G.nodes.get(src, {}).get("app_id", "")
        pkg, apk = parse_app_id(app_id)

        # involved methods = every method on the path (ordered, deduped)
        methods: List[str] = []
        for s in path:
            mid = G.nodes.get(s, {}).get("method_id") or stmt_method_id(s)
            if mid not in methods:
                methods.append(mid)

        node_ids = _slice(G, set(methods))
        sub = G.subgraph(node_ids)
        nodes = [{"id": n, **{k: G.nodes[n].get(k) for k in
                              ("label", "type", "callee", "code", "is_source", "is_sink",
                               "pi_type", "category", "permission", "sink_type",
                               "sink_label", "privacy_threat")
                              if k in G.nodes[n]}} for n in sub.nodes()]
        edges = [{"start": u, "end": v, "type": k} for u, v, k in sub.edges(keys=True)]

        src_d, snk_d = G.nodes.get(src, {}), G.nodes.get(snk, {})
        src_method = G.nodes.get(src, {}).get("method_id") or stmt_method_id(src)
        prcs = PRCS(
            prcs_id=_stable_id(app_id, src, snk),
            app_package=pkg, apk_filename=apk,
            class_name=method_class(src_method),
            method_name=method_short_name(src_method),
            method_signature=src_method,
            source_api=src_d.get("callee", ""),
            sink_api=snk_d.get("callee", ""),
            sink_type=snk_d.get("sink_type", ""),
            sink_label=snk_d.get("sink_label", ""),
            pi_type=src_d.get("pi_type", ""),
            pi_category=src_d.get("category", ""),
            permission=src_d.get("permission", ""),
            privacy_threat=snk_d.get("privacy_threat", ""),
            hop_count=len(path) - 1,
            code_snippet=_build_snippet(G, methods),
            subgraph={"nodes": nodes, "edges": edges},
            involved_methods=methods,
        )
        out.append(prcs)
    log.info("Extracted %d PRCS records", len(out))
    return out


def load_ppg_graph(ppg_dir: str | Path) -> nx.MultiDiGraph:
    with open(Path(ppg_dir) / "ppg.pkl", "rb") as f:
        return pickle.load(f)


def extract_prcs(ppg_dir: str, out_dir: str) -> List[PRCS]:
    """File-based entry point: load PPG, slice PRCS, write JSON + index."""
    G = load_ppg_graph(ppg_dir)
    taint_paths = load_json(Path(ppg_dir) / "taint_paths.json")
    records = extract_from_graph(G, taint_paths)

    out = ensure_dir(out_dir)
    for r in records:
        dump_json({k: getattr(r, k) for k in r.__dataclass_fields__}, out / f"{r.prcs_id}.json")
    pd.DataFrame([r.index_row() for r in records], columns=INDEX_COLUMNS).to_csv(
        out / "prcs_index.csv", index=False, encoding="utf-8")
    log.info("Wrote %d PRCS JSON files + prcs_index.csv to %s", len(records), out)
    return records


def main() -> None:
    ap = argparse.ArgumentParser(description="Extract PRCS subgraphs from a PPG (Step 2).")
    ap.add_argument("--ppg", default="data/ppg")
    ap.add_argument("--out", default="data/prcs")
    args = ap.parse_args()
    records = extract_prcs(args.ppg, args.out)
    print(f"\n=== PRCS summary ===\n  records={len(records)}")
    for r in records[:3]:
        print(f"    {r.prcs_id}  [{r.pi_type}] {r.source_api} -> {r.sink_api} "
              f"({r.sink_type}, {r.hop_count} hops, {len(r.subgraph['nodes'])} nodes)")


if __name__ == "__main__":
    main()
