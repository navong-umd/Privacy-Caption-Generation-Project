"""
Purpose: OPTIONAL loader pushing the PPG into a local Neo4j (new labels/rels only).
Input:   a networkx PPG graph + neo4j connection config.
Output:  nodes/relationships in Neo4j. No-op-safe: import only happens when --neo4j is set.

Mirrors the Stage 2 loader conventions (MERGE on id). Never required for the pipeline
or tests; the PPG is fully usable from CSV/GraphML/pickle without a database.
"""
from __future__ import annotations

from typing import Dict

import networkx as nx

from pplib.io_utils import chunked, get_logger

log = get_logger("neo4j_loader")

_DEFAULTS = {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"}


def load_ppg_to_neo4j(G: nx.MultiDiGraph, cfg: Dict) -> None:
    """Upsert PPG nodes/edges into Neo4j. Requires the `neo4j` package + a running server."""
    from neo4j import GraphDatabase  # local import: optional dependency

    conf = {**_DEFAULTS, **(cfg or {})}
    driver = GraphDatabase.driver(conf["uri"], auth=(conf["user"], conf["password"]))

    nodes_by_label: Dict[str, list] = {}
    for nid, d in G.nodes(data=True):
        label = d.get("label", "Node")
        props = {k: (str(v) if not isinstance(v, (int, float, bool, str)) else v)
                 for k, v in d.items() if k != "label"}
        props["id"] = nid
        nodes_by_label.setdefault(label, []).append(props)

    with driver.session() as s:
        for label, rows in nodes_by_label.items():
            q = f"UNWIND $rows AS r MERGE (n:{label} {{id: r.id}}) SET n += r"
            for b in chunked(rows, 1000):
                s.run(q, {"rows": b})
        # edges grouped by type
        edges_by_type: Dict[str, list] = {}
        for u, v, d in G.edges(data=True):
            etype = d.get("type", "REL")
            edges_by_type.setdefault(etype, []).append(
                {"u": u, "v": v, "props": {k: str(val) for k, val in d.items() if k != "type"}})
        for etype, rows in edges_by_type.items():
            q = (f"UNWIND $rows AS r MATCH (a {{id: r.u}}), (b {{id: r.v}}) "
                 f"MERGE (a)-[e:{etype}]->(b) SET e += r.props")
            for b in chunked(rows, 1000):
                s.run(q, {"rows": b})
    driver.close()
    log.info("Loaded PPG into Neo4j: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
