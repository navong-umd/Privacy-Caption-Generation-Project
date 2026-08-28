"""
Purpose: Heuristic taint propagation from PI sources to sinks over the APG.
Input:   an APG object + sets of source/sink statement ids + taint config.
Output:  a list of TaintPath(source_stmt, sink_stmt, path, reasons, app_id) per
         source->sink flow. `reasons[i]` explains why edge path[i-1] -> path[i]
         exists; `reasons[0]` is always the sentinel "source" for the origin.

Traversal is intra- AND inter-procedural over DATA_DEPENDS (+ optional ICFG_NEXT)
plus two inter-procedural rules: CALL-ARG (tainted invoke -> callee entry) and
CALL-RET (taint inside a method -> its call sites). This is an over-approximation
by design (the project explicitly asks for heuristic reach to known AND unknown sinks).

Phase 5: every hop now carries its rule tag (ddg | icfg | call_arg | call_ret)
so downstream consumers — and human reviewers — can answer "why does this
TAINT_FLOW edge exist?" without re-running analysis.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

from pplib.apg_model import APG
from pplib.io_utils import get_logger

log = get_logger("taint")

# Canonical per-hop provenance tags. Keep in sync with research/PPG_SCHEMA.md §Provenance.
TAINT_RULES = ("ddg", "icfg", "call_arg", "call_ret")
TAINT_RULE_SOURCE = "source"   # sentinel used for reasons[0] (the origin, no incoming edge)


@dataclass
class TaintPath:
    source_stmt: str
    sink_stmt: str
    path: List[str]
    app_id: str
    reasons: List[str] = field(default_factory=list)   # parallel to path; see module docstring


def _build_adjacency(
    apg: APG, follow_icfg: bool
) -> Tuple[Dict[str, List[Tuple[str, str]]], Dict[str, List[str]]]:
    """Return (statement-successor adjacency [(dst, rule)], callee_method -> call-site statements)."""
    adj: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    # intra-procedural data flow
    for u, v in apg.data_depends:
        adj[u].append((v, "ddg"))
    if follow_icfg:
        for u, v in apg.icfg_next:
            adj[u].append((v, "icfg"))

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
                adj[sid].append((entry, "call_arg"))   # args flow into callee
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
    # precision knobs (keep real APKs tractable; defaults are no-ops on small graphs)
    dedup_by_method = tcfg.get("dedup_by_method", True)
    max_paths_per_source = tcfg.get("max_paths_per_source", 0)  # 0 = unlimited

    adj, callsites = _build_adjacency(apg, follow_icfg)
    stmt_method = {sid: s["method_id"] for sid, s in apg.statements.items()}
    paths: List[TaintPath] = []

    for src in sources:
        parent: Dict[str, str] = {src: ""}
        # `reason_into[v]` = rule that caused v to be added to the frontier from parent[v].
        reason_into: Dict[str, str] = {src: TAINT_RULE_SOURCE}
        depth: Dict[str, int] = {src: 0}
        q: deque[str] = deque([src])
        tainted_methods: Set[str] = set()

        while q:
            u = q.popleft()
            if depth[u] >= max_depth:
                continue
            succ: List[Tuple[str, str]] = list(adj.get(u, []))

            # CALL-RET: once a method holds taint, its call sites become tainted (return value).
            if inter:
                m = stmt_method.get(u, "")
                if m and m not in tainted_methods:
                    tainted_methods.add(m)
                    for cs in callsites.get(m, []):
                        succ.append((cs, "call_ret"))

            for v, rule in succ:
                if v not in parent:
                    parent[v] = u
                    reason_into[v] = rule
                    depth[v] = depth[u] + 1
                    q.append(v)

        # record a path for every sink reached from this source (with precision caps)
        src_method = stmt_method.get(src, "")
        seen_pairs: Set[str] = set()
        n_kept = 0
        reached = sorted((s for s in sinks if s in parent and s != src), key=lambda s: depth[s])
        for snk in reached:
            if dedup_by_method:
                key = f"{src_method}|{stmt_method.get(snk, '')}"
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
            # Reconstruct path AND per-hop reasons walking parent pointers backwards.
            path: List[str] = []
            reasons: List[str] = []
            cur = snk
            while cur:
                path.append(cur)
                reasons.append(reason_into.get(cur, TAINT_RULE_SOURCE))
                cur = parent[cur]
            path.reverse()
            reasons.reverse()
            # After reverse: reasons[0] = "source" for the origin; reasons[i>=1] = rule for edge (i-1)->i.
            paths.append(TaintPath(
                source_stmt=src, sink_stmt=snk, path=path, reasons=reasons,
                app_id=apg.statements[src].get("app_id", apg.app_id),
            ))
            n_kept += 1
            if max_paths_per_source and n_kept >= max_paths_per_source:
                break

    log.info("Taint: %d sources, %d sinks -> %d source->sink paths",
             len(sources), len(sinks), len(paths))
    return paths
