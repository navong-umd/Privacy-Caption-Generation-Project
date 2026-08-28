"""
Purpose: ADAPTER over Stage 2 output. Loads APG CSVs (AST/MCG/ICFG/DDG) into one graph.
Input:   a folder containing {AST,MCG,ICFG,DDG}_{nodes,edges}.csv (Stage 2 CSV style).
Output:  an in-memory APG object (dict views + a networkx graph) for the PPG builder.

FLAGGED ADAPTER: the Stage 2 script writes Class nodes / HAS_METHOD edges only into
Neo4j (not the CSVs). We reconstruct them here from method ids so downstream code sees
the full APG without touching the original Stage 2 script.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .io_utils import get_logger, method_class, method_short_name, stmt_method_id

log = get_logger("apg_model")

_GRAPHS = ["AST", "MCG", "ICFG", "DDG"]


@dataclass
class APG:
    """In-memory App Property Graph reconstructed from Stage 2 CSVs."""

    app_id: str
    classes: Dict[str, dict] = field(default_factory=dict)
    methods: Dict[str, dict] = field(default_factory=dict)
    statements: Dict[str, dict] = field(default_factory=dict)
    # edge lists of (src, dst)
    has_method: List[Tuple[str, str]] = field(default_factory=list)
    has_statement: List[Tuple[str, str]] = field(default_factory=list)
    calls: List[Tuple[str, str]] = field(default_factory=list)
    icfg_next: List[Tuple[str, str]] = field(default_factory=list)
    data_depends: List[Tuple[str, str]] = field(default_factory=list)

    def summary(self) -> str:
        return (
            f"app={self.app_id} classes={len(self.classes)} methods={len(self.methods)} "
            f"stmts={len(self.statements)} calls={len(self.calls)} "
            f"icfg={len(self.icfg_next)} ddg={len(self.data_depends)}"
        )


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_apg(apg_dir: str | Path) -> APG:
    """Load the four APG CSV pairs from `apg_dir` and rebuild the full graph."""
    apg_dir = Path(apg_dir)
    nodes: Dict[str, pd.DataFrame] = {}
    edges: Dict[str, pd.DataFrame] = {}
    for g in _GRAPHS:
        nodes[g] = _read_csv(apg_dir / f"{g}_nodes.csv")
        edges[g] = _read_csv(apg_dir / f"{g}_edges.csv")

    # Derive app_id from any node row (all rows share it for a single-APK run).
    app_id = ""
    for g in _GRAPHS:
        if not nodes[g].empty and "app_id" in nodes[g]:
            vals = [v for v in nodes[g]["app_id"].tolist() if v]
            if vals:
                app_id = vals[0]
                break

    apg = APG(app_id=app_id)

    # Collect Method + Statement nodes across all graphs (deduped).
    for g in _GRAPHS:
        df = nodes[g]
        if df.empty:
            continue
        for r in df.to_dict("records"):
            nid, label = r.get("id", ""), r.get("label", "")
            if not nid:
                continue
            if label == "Method":
                if nid not in apg.methods:
                    apg.methods[nid] = {
                        "id": nid, "class": method_class(nid),
                        "name": method_short_name(nid), "app_id": r.get("app_id", app_id),
                    }
            elif label == "Statement":
                if nid not in apg.statements:
                    apg.statements[nid] = {
                        "id": nid, "code": r.get("code", ""), "type": r.get("type", ""),
                        "callee": r.get("callee", ""), "method_id": stmt_method_id(nid),
                        "app_id": r.get("app_id", app_id),
                    }

    # Reconstruct Class nodes + HAS_METHOD edges from method ids (Neo4j-only in Stage 2).
    seen_hm = set()
    for mid, m in apg.methods.items():
        cls = m["class"]
        if cls not in apg.classes:
            apg.classes[cls] = {"name": cls, "app_id": m["app_id"]}
        key = (cls, mid)
        if key not in seen_hm:
            apg.has_method.append(key)
            seen_hm.add(key)

    # Edge lists from each graph's edge CSV.
    def _edges(df: pd.DataFrame) -> List[Tuple[str, str]]:
        if df.empty or "start_id" not in df:
            return []
        return [(r["start_id"], r["end_id"]) for r in df.to_dict("records")]

    apg.has_statement = _edges(edges["AST"])
    apg.calls = _edges(edges["MCG"])
    apg.icfg_next = _edges(edges["ICFG"])
    apg.data_depends = _edges(edges["DDG"])

    log.info("Loaded APG: %s", apg.summary())
    return apg


def write_apg(apg: APG, apg_dir: str | Path) -> None:
    """Write an APG back out in the exact Stage 2 CSV style (used by the fixture generator)."""
    apg_dir = Path(apg_dir)
    apg_dir.mkdir(parents=True, exist_ok=True)

    def _aid(nid: str) -> str:
        # per-node app_id preserves multi-app provenance through a merged dir.
        if nid in apg.methods:
            return apg.methods[nid].get("app_id", apg.app_id)
        if nid in apg.statements:
            return apg.statements[nid].get("app_id", apg.app_id)
        return apg.app_id

    def _node_row(nid, label, type_, code="", callee=""):
        return {"id": nid, "label": label, "type": type_, "code": code,
                "callee": callee, "app_id": _aid(nid)}

    def _edge_row(u, v, etype):
        return {"start_id": u, "end_id": v, "type": etype, "app_id": _aid(u)}

    # AST: methods + statements, HAS_STATEMENT edges.
    ast_nodes = [_node_row(m, "Method", "Method") for m in apg.methods]
    ast_nodes += [_node_row(s["id"], "Statement", s["type"], s["code"], s["callee"])
                  for s in apg.statements.values()]
    pd.DataFrame(ast_nodes).to_csv(apg_dir / "AST_nodes.csv", index=False)
    pd.DataFrame([_edge_row(u, v, "HAS_STATEMENT") for u, v in apg.has_statement]).to_csv(
        apg_dir / "AST_edges.csv", index=False)

    # MCG: methods, CALLS edges.
    pd.DataFrame([_node_row(m, "Method", "Method") for m in apg.methods]).to_csv(
        apg_dir / "MCG_nodes.csv", index=False)
    pd.DataFrame([_edge_row(u, v, "CALLS") for u, v in apg.calls]).to_csv(
        apg_dir / "MCG_edges.csv", index=False)

    # ICFG: methods + statements, ICFG_NEXT edges.
    icfg_nodes = [_node_row(m, "Method", "Method") for m in apg.methods]
    icfg_nodes += [_node_row(s["id"], "Statement", s["type"], s["code"], s["callee"])
                   for s in apg.statements.values()]
    pd.DataFrame(icfg_nodes).to_csv(apg_dir / "ICFG_nodes.csv", index=False)
    pd.DataFrame([_edge_row(u, v, "ICFG_NEXT") for u, v in apg.icfg_next]).to_csv(
        apg_dir / "ICFG_edges.csv", index=False)

    # DDG: statements, DATA_DEPENDS edges.
    ddg_stmts = {u for u, _ in apg.data_depends} | {v for _, v in apg.data_depends}
    pd.DataFrame([_node_row(apg.statements[s]["id"], "Statement", apg.statements[s]["type"],
                            apg.statements[s]["code"], apg.statements[s]["callee"])
                  for s in ddg_stmts if s in apg.statements]).to_csv(
        apg_dir / "DDG_nodes.csv", index=False)
    pd.DataFrame([_edge_row(u, v, "DATA_DEPENDS") for u, v in apg.data_depends]).to_csv(
        apg_dir / "DDG_edges.csv", index=False)


# ------------------------------------------------------------
# Provenance (Phase 2)
# ------------------------------------------------------------

APG_META_FILENAME = "APG_META.json"


def sha256_file(path: str | Path, chunk: int = 65536) -> str:
    """Streaming SHA-256 of a file (empty string if the file is missing)."""
    p = Path(path)
    if not p.exists():
        return ""
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for buf in iter(lambda: f.read(chunk), b""):
            h.update(buf)
    return h.hexdigest()


def write_apg_meta(meta: Dict[str, Any], apg_dir: str | Path) -> Path:
    """Write APG_META.json alongside the APG CSVs.

    Content is caller-supplied so tests / fixtures can produce byte-stable metadata.
    Adapters that generate metadata from a real APK should include at least:
        apk_path, apk_sha256, app_id, generator, generator_version,
        androguard_version, python_version, generated_at, summary
    See adapters/run_apg_csv.py for the canonical set.
    """
    apg_dir = Path(apg_dir)
    apg_dir.mkdir(parents=True, exist_ok=True)
    path = apg_dir / APG_META_FILENAME
    # sort_keys for byte-stable output; indent for human readability.
    path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_apg_meta(apg_dir: str | Path) -> Dict[str, Any]:
    """Load APG_META.json (empty dict if absent — meta is optional)."""
    p = Path(apg_dir) / APG_META_FILENAME
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))
