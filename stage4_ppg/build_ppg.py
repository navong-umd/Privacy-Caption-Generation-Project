"""
Purpose: STAGE 4 - build the Privacy Property Graph (PPG) from the Stage 2 APG.
Input:   APG CSV dir (--apg), ppg config (--config). Uses Stage 3 PI catalogs.
Output:  PPG_nodes.csv, PPG_edges.csv (APG-style), ppg.graphml, ppg.pkl (PyG-ready),
         taint_paths.json, and a console summary (#sources/#sinks/#paths/examples).

Overlay: marks Statement nodes with is_source/is_sink/pi_type/permission/sink_type/
privacy_threat/tainted, adds Source/Sink/DataItem/Store/Component nodes and
TAINT_FLOW + PRIVACY_RELATION edges, and tags flows with LINDDUN(GO) categories.

Run: python -m stage4_ppg.build_ppg --apg data/fixtures/synthetic_apg --config configs/ppg.yaml --out data/ppg
"""
from __future__ import annotations

import argparse
import pickle
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional, Set

import networkx as nx
import pandas as pd

from pplib.apg_model import APG, load_apg
from pplib.io_utils import dump_json, ensure_dir, get_logger, load_yaml
from pplib.schema import PPG_EDGE_COLUMNS, PPG_NODE_COLUMNS
from stage4_ppg.catalogs import SinkCatalog, SourceCatalog
from stage4_ppg.taint import TaintPath, propagate

log = get_logger("build_ppg")
REPO_ROOT = Path(__file__).resolve().parent.parent


def _linddun(sink_type: str, category: str, cfg: dict) -> List[str]:
    """Map a tainted flow to LINDDUN(GO) threat categories."""
    threats = list(cfg.get("linddun_map", {}).get(sink_type, []))
    if category in cfg.get("identifying_pi_categories", []) and "Identifying" not in threats:
        threats.append("Identifying")
    return threats


class PPGBuilder:
    """Builds the PPG graph and overlay from an APG plus PI catalogs."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.sources = SourceCatalog(cfg, REPO_ROOT)
        self.sinks = SinkCatalog(REPO_ROOT / cfg["paths"]["sinks_catalog"])
        self.G = nx.MultiDiGraph()
        self.taint_paths: List[TaintPath] = []
        self.stmt_props: Dict[str, dict] = {}

    # ---- node/edge helpers ----
    def _add_node(self, nid: str, label: str, **props) -> None:
        if nid in self.G:
            self.G.nodes[nid].update({k: v for k, v in props.items() if v not in ("", None)})
        else:
            self.G.add_node(nid, label=label, **props)

    def _add_edge(self, u: str, v: str, etype: str, **props) -> None:
        self.G.add_edge(u, v, key=etype, type=etype, **props)

    def build(self, apg: APG) -> None:
        """Populate the PPG graph from the APG and run the privacy overlay."""
        # 1. carry over APG structure
        for cls, c in apg.classes.items():
            self._add_node(cls, "Class", app_id=c["app_id"])
        for mid, m in apg.methods.items():
            self._add_node(mid, "Method", name=m["name"], cls=m["class"], app_id=m["app_id"])
        for sid, s in apg.statements.items():
            self._add_node(sid, "Statement", type=s["type"], code=s["code"],
                           callee=s["callee"], method_id=s["method_id"], app_id=s["app_id"])
            self.stmt_props[sid] = {}
        for u, v in apg.has_method:
            self._add_edge(u, v, "HAS_METHOD")
        for u, v in apg.has_statement:
            self._add_edge(u, v, "HAS_STATEMENT")
        for u, v in apg.calls:
            self._add_edge(u, v, "CALLS")
        for u, v in apg.icfg_next:
            self._add_edge(u, v, "ICFG_NEXT")
        for u, v in apg.data_depends:
            self._add_edge(u, v, "DATA_DEPENDS")

        # 2. classify sources and sinks
        source_stmts: Set[str] = set()
        sink_stmts: Set[str] = set()
        for sid, s in apg.statements.items():
            callee = s.get("callee", "")
            src_hit = self.sources.classify(callee)
            sink_hit = self.sinks.classify(callee)
            # Precedence: curated source > explicit catalog sink > SuSi-recall source > heuristic sink.
            is_curated_source = src_hit is not None and src_hit.tier == "known"
            hit = src_hit if is_curated_source else (None if sink_hit else src_hit)
            if hit:
                source_stmts.add(sid)
                self.stmt_props[sid].update(
                    is_source=True, pi_type=hit.pi_type, permission=hit.permission,
                    category=hit.category)
                src_node = f"src::{sid}"
                self._add_node(src_node, "Source", api=callee, pi_type=hit.pi_type,
                               permission=hit.permission, category=hit.category,
                               app_id=s["app_id"])
                self._add_edge(sid, src_node, "PRIVACY_RELATION", relation="ACCESSES")
                di = f"data::{hit.category}"
                self._add_node(di, "DataItem", category=hit.category, app_id=s["app_id"])
                self._add_edge(src_node, di, "PRIVACY_RELATION", relation="OF_TYPE")
                continue
            shit = self.sinks.classify(callee)
            if not shit:
                shit = self.sinks.classify_unknown(callee, is_internal=callee in apg.methods)
            if shit:
                sink_stmts.add(sid)
                self.stmt_props[sid].update(is_sink=True, sink_type=shit.sink_type,
                                            sink_label=shit.label)
                snk_node = f"sink::{sid}"
                self._add_node(snk_node, "Sink", api=callee, sink_type=shit.sink_type,
                               sink_label=shit.label, known=shit.known, app_id=s["app_id"])
                self._add_edge(sid, snk_node, "PRIVACY_RELATION", relation="WRITES_TO")
                # storage -> Store node; ipc -> Component node
                if shit.sink_type == "storage":
                    store = f"store::{shit.label}"
                    self._add_node(store, "Store", store_label=shit.label, app_id=s["app_id"])
                    self._add_edge(snk_node, store, "PRIVACY_RELATION", relation="PERSISTS_IN")
                elif shit.sink_type == "ipc":
                    comp = f"component::{shit.label}"
                    self._add_node(comp, "Component", component_label=shit.label, app_id=s["app_id"])
                    self._add_edge(snk_node, comp, "PRIVACY_RELATION", relation="SENDS_VIA")

        # 3. taint propagation
        self.taint_paths = propagate(apg, source_stmts, sink_stmts, self.cfg)

        # 4. overlay: TAINT_FLOW edges + LINDDUN threats on each flow
        for tp in self.taint_paths:
            scat = self.stmt_props.get(tp.source_stmt, {}).get("category", "")
            stype = self.stmt_props.get(tp.sink_stmt, {}).get("sink_type", "")
            threats = _linddun(stype, scat, self.cfg)
            threat_str = ";".join(threats)
            for a, b in zip(tp.path, tp.path[1:]):
                self._add_edge(a, b, "TAINT_FLOW", pi_type=scat, privacy_threat=threat_str)
                for sid in (a, b):
                    self.stmt_props.setdefault(sid, {})["tainted"] = True
            # connect Source -> Sink overlay nodes with the threat
            self._add_edge(f"src::{tp.source_stmt}", f"sink::{tp.sink_stmt}",
                           "PRIVACY_RELATION", relation="FLOWS_TO", privacy_threat=threat_str)
            self.stmt_props[tp.sink_stmt]["privacy_threat"] = threat_str

        # 5. write overlay props back onto Statement nodes
        for sid, props in self.stmt_props.items():
            if sid in self.G:
                self.G.nodes[sid].update(props)

    # ---- outputs ----
    def export_csv(self, out_dir: Path) -> None:
        """Write PPG_nodes.csv / PPG_edges.csv mirroring the APG CSV style."""
        node_rows = []
        for nid, d in self.G.nodes(data=True):
            row = {c: "" for c in PPG_NODE_COLUMNS}
            row["id"] = nid
            row["label"] = d.get("label", "")
            row["type"] = d.get("type", d.get("label", ""))
            row["code"] = d.get("code", "")
            row["callee"] = d.get("callee", "")
            row["app_id"] = d.get("app_id", "")
            for p in ("is_source", "is_sink", "pi_type", "permission", "sink_type",
                      "privacy_threat", "tainted", "sdk", "sdk_purpose"):
                if p in d:
                    row[p] = d[p]
            node_rows.append(row)
        pd.DataFrame(node_rows, columns=PPG_NODE_COLUMNS).to_csv(
            out_dir / "PPG_nodes.csv", index=False, encoding="utf-8")

        edge_rows = []
        for u, v, d in self.G.edges(data=True):
            edge_rows.append({
                "start_id": u, "end_id": v, "type": d.get("type", ""),
                "app_id": self.G.nodes[u].get("app_id", ""),
                "pi_type": d.get("pi_type", ""), "privacy_threat": d.get("privacy_threat", ""),
            })
        pd.DataFrame(edge_rows, columns=PPG_EDGE_COLUMNS).to_csv(
            out_dir / "PPG_edges.csv", index=False, encoding="utf-8")

    def export_graph(self, out_dir: Path) -> None:
        """Write a GraphML and a NetworkX pickle (PyG-ready serialization)."""
        # GraphML needs scalar attrs; stringify everything for safety.
        H = nx.MultiDiGraph()
        for nid, d in self.G.nodes(data=True):
            H.add_node(nid, **{k: str(v) for k, v in d.items()})
        for u, v, d in self.G.edges(data=True):
            H.add_edge(u, v, **{k: str(v2) for k, v2 in d.items()})
        nx.write_graphml(H, out_dir / "ppg.graphml")
        with open(out_dir / "ppg.pkl", "wb") as f:
            pickle.dump(self.G, f)

    def export_taint(self, out_dir: Path) -> None:
        dump_json([asdict(tp) for tp in self.taint_paths], out_dir / "taint_paths.json")

    def summary(self) -> dict:
        n_src = sum(1 for d in self.stmt_props.values() if d.get("is_source"))
        n_snk = sum(1 for d in self.stmt_props.values() if d.get("is_sink"))
        return {"sources": n_src, "sinks": n_snk, "taint_paths": len(self.taint_paths),
                "nodes": self.G.number_of_nodes(), "edges": self.G.number_of_edges()}


def build_ppg(apg_dir: str, config: str, out_dir: str,
              neo4j: bool = False) -> PPGBuilder:
    """Programmatic entry point used by tests and the pipeline."""
    cfg = load_yaml(config)
    apg = load_apg(apg_dir)
    builder = PPGBuilder(cfg)
    builder.build(apg)
    out = ensure_dir(out_dir)
    builder.export_csv(out)
    builder.export_graph(out)
    builder.export_taint(out)
    if neo4j:
        from stage4_ppg.neo4j_loader import load_ppg_to_neo4j
        load_ppg_to_neo4j(builder.G, cfg.get("neo4j", {}))
    return builder


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the Privacy Property Graph (Stage 4).")
    ap.add_argument("--apg", default="data/fixtures/synthetic_apg")
    ap.add_argument("--config", default="configs/ppg.yaml")
    ap.add_argument("--out", default="data/ppg")
    ap.add_argument("--neo4j", action="store_true", help="also load into local Neo4j")
    args = ap.parse_args()

    builder = build_ppg(args.apg, args.config, args.out, neo4j=args.neo4j)
    s = builder.summary()
    print("\n=== PPG summary ===")
    print(f"  sources={s['sources']}  sinks={s['sinks']}  taint_paths={s['taint_paths']}")
    print(f"  nodes={s['nodes']}  edges={s['edges']}")
    print("  example flows:")
    for tp in builder.taint_paths[:3]:
        sp = builder.stmt_props
        pi = sp.get(tp.source_stmt, {}).get("pi_type", "?")
        st = sp.get(tp.sink_stmt, {}).get("sink_type", "?")
        print(f"    [{pi}] {tp.source_stmt}  ==>  {tp.sink_stmt} [{st}]  ({len(tp.path)} hops)")


if __name__ == "__main__":
    main()
