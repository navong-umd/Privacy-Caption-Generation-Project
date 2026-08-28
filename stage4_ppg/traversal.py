"""
Phase 6: reviewer-facing traversal helpers.

The heavy lifting (BFS from source to sink with rule-tagged hops) lives in
stage4_ppg/taint.py::propagate. This module wraps a completed TaintPath into a
per-hop trace a human can inspect, using the Phase 5 taint_rule tags.

Typical use in a notebook or a debug script:

    from stage4_ppg.build_ppg import build_ppg
    from stage4_ppg.traversal import explain_flow

    builder = build_ppg("data/fixtures/synthetic_apg", "configs/ppg.yaml", "/tmp/ppg")
    apg = load_apg("data/fixtures/synthetic_apg")
    for tp in builder.taint_paths[:3]:
        print(explain_flow(tp, apg))
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from pplib.apg_model import APG
from stage4_ppg.taint import TAINT_RULES, TAINT_RULE_SOURCE, TaintPath

# Human-readable one-liner per rule, keyed by the tag propagate() emits.
RULE_EXPLANATIONS: Dict[str, str] = {
    TAINT_RULE_SOURCE: "origin (PI source statement)",
    "ddg": "intra-procedural data dependence (predecessor writes a register the successor reads)",
    "icfg": "intra-procedural control fallback (successor is the next Dalvik instruction in the method)",
    "call_arg": "inter-procedural argument flow (tainted invoke of an internal method flows into its entry)",
    "call_ret": "inter-procedural return flow (tainted method taints all its callers)",
    "unknown": "legacy TaintPath without provenance (pre-Phase-5 artifact)",
}


@dataclass
class HopTrace:
    """One row of the human trace for a taint path."""

    step: int
    stmt_id: str
    method_id: str
    callee: str
    rule: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "stmt_id": self.stmt_id,
            "method_id": self.method_id,
            "callee": self.callee,
            "rule": self.rule,
            "reason": self.reason,
        }


def explain_flow(taint_path: TaintPath, apg: APG) -> List[HopTrace]:
    """Turn a TaintPath into a list of HopTrace rows, one per statement on the path.

    step 0 is the source (rule == "source"). Every subsequent step carries the
    rule that produced the edge from step i-1 to step i (ddg | icfg | call_arg |
    call_ret). Reviewers can print this list and know why the taint reached the
    sink without re-running propagate().
    """
    trace: List[HopTrace] = []
    reasons = taint_path.reasons or []
    for i, sid in enumerate(taint_path.path):
        stmt = apg.statements.get(sid, {})
        rule = reasons[i] if i < len(reasons) else "unknown"
        trace.append(
            HopTrace(
                step=i,
                stmt_id=sid,
                method_id=stmt.get("method_id", ""),
                callee=stmt.get("callee", ""),
                rule=rule,
                reason=RULE_EXPLANATIONS.get(rule, rule),
            )
        )
    return trace


def summarize_flow(taint_path: TaintPath, apg: APG) -> Dict[str, Any]:
    """One-glance summary: source, sink, length, and a rule histogram.

    Handy for corpus-level QA where you want per-flow stats without full traces.
    """
    reasons = taint_path.reasons or []
    hist: Dict[str, int] = {r: 0 for r in TAINT_RULES}
    for r in reasons[1:]:                              # skip the "source" sentinel
        if r in hist:
            hist[r] += 1
    src_stmt = apg.statements.get(taint_path.source_stmt, {})
    snk_stmt = apg.statements.get(taint_path.sink_stmt, {})
    return {
        "source_stmt": taint_path.source_stmt,
        "source_callee": src_stmt.get("callee", ""),
        "sink_stmt": taint_path.sink_stmt,
        "sink_callee": snk_stmt.get("callee", ""),
        "hops": max(0, len(taint_path.path) - 1),
        "rule_histogram": hist,
        "app_id": taint_path.app_id,
    }
