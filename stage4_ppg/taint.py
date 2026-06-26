"""
Purpose: Heuristic taint propagation from PI sources to sinks over the APG.
Input:   an APG object + sets of source/sink statement ids + taint config.
Output:  a list of TaintPath(source_stmt, sink_stmt, path, app_id) per source->sink flow.

Traversal is intra- AND inter-procedural over DATA_DEPENDS (+ optional ICFG_NEXT) plus
two inter-procedural rules: CALL-ARG (tainted invoke -> callee entry) and CALL-RET
(taint inside a method -> its call sites). This is an over-approximation by design
(the project explicitly asks for heuristic reach to known AND unknown sinks).
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from pplib.apg_model import APG
from pplib.io_utils import get_logger

log = get_logger("taint")


@dataclass
class TaintPath:
    source_stmt: str
    sink_stmt: str
    path: List[str]
    app_id: str


def _build_adjacency(apg: APG, follow_icfg: bool) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """Return (statement-successor adjacency, callee_method -> call-site statements)."""
    adj: Dict[str, List[str]] = defaultdict(list)

    # intra-procedural data flow
    for u, v in apg.data_depends:
        adj[u].append(v)
    if follow_icfg:
        for u, v in apg.icfg_next:
            adj[u].append(v)

    # inter-procedural CALL-ARG: invoke of an internal method -> that method's entry stmt.
    # also index call sites per callee method for the CALL-RET rule.
    callsites: Dict[str, List[str]] = defaultdict(list)
    method_entry: Dict[str, str] = {}
    for sid, s in apg.statements.items():
        # entry statement = lowest index per method
        mid = s["method_id"]
        if mid not in method_entry or _idx(sid) < _idx(method_entry[mid]):
            method_entry[mid] = sid
    for sid, s in apg.statements.items():
        callee = s.get("callee", "")
        if callee and callee in apg.methods:          # internal call
            callsites[callee].append(sid)
            entry = method_entry.get(callee)
            if entry:
                adj[sid].append(entry)                 # args flow into callee
    return adj, callsites


def _idx(stmt_id: str) -> int:
    try:
        return int(stmt_id.rsplit("_stmt_", 1)[1])
    except Exception:
        return 0


def propagate(apg: APG, sources: Set[str], sinks: Set[str], cfg: dict) -> List[TaintPath]:
    """BFS from each source statement to any reachable sink statement."""
    tcfg = cfg.get("taint", {})
    max_depth = tcfg.get("max_depth", 25)
    inter = tcfg.get("inter_procedural", True)
    follow_icfg = tcfg.get("follow_icfg", True)

    adj, callsites = _build_adjacency(apg, follow_icfg)
    stmt_method = {sid: s["method_id"] for sid, s in apg.statements.items()}
    paths: List[TaintPath] = []

    for src in sources:
        parent: Dict[str, str] = {src: ""}
        depth: Dict[str, int] = {src: 0}
        q: deque[str] = deque([src])
        tainted_methods: Set[str] = set()

        while q:
            u = q.popleft()
            if depth[u] >= max_depth:
                continue
            succ = list(adj.get(u, []))

            # CALL-RET: once a method holds taint, its call sites become tainted (return value).
            if inter:
                m = stmt_method.get(u, "")
                if m and m not in tainted_methods:
                    tainted_methods.add(m)
                    succ.extend(callsites.get(m, []))

            for v in succ:
                if v not in parent:
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    q.append(v)

        # record a path for every sink reached from this source
        for snk in sinks:
            if snk in parent and snk != src:
                path, cur = [], snk
                while cur:
                    path.append(cur)
                    cur = parent[cur]
                path.reverse()
                paths.append(TaintPath(
                    source_stmt=src, sink_stmt=snk, path=path,
                    app_id=apg.statements[src].get("app_id", apg.app_id),
                ))

    log.info("Taint: %d sources, %d sinks -> %d source->sink paths",
             len(sources), len(sinks), len(paths))
    return paths
