"""Phase 6: explain_flow / summarize_flow return well-formed traces for real paths."""
from __future__ import annotations

import pytest

from pplib.apg_model import load_apg
from pplib.io_utils import REPO_ROOT, load_yaml
from stage4_ppg.taint import TAINT_RULES, TAINT_RULE_SOURCE, propagate
from stage4_ppg.traversal import RULE_EXPLANATIONS, explain_flow, summarize_flow


@pytest.fixture(scope="module")
def one_flow(synth_apg_dir):
    apg = load_apg(synth_apg_dir)
    cfg = load_yaml(REPO_ROOT / "configs" / "ppg.yaml")
    sources = {sid for sid, s in apg.statements.items()
               if "getLastKnownLocation" in s.get("callee", "")
               or "getDeviceId" in s.get("callee", "")}
    sinks = {sid for sid, s in apg.statements.items()
             if "openConnection" in s.get("callee", "")
             or s.get("callee", "").startswith("android.util.Log")}
    if not sources or not sinks:
        pytest.skip("fixture has no source-to-sink flow to trace")
    paths = propagate(apg, sources, sinks, cfg)
    if not paths:
        pytest.skip("propagate returned no paths")
    return paths[0], apg


def test_rule_explanations_cover_every_rule():
    for r in TAINT_RULES:
        assert r in RULE_EXPLANATIONS
    assert TAINT_RULE_SOURCE in RULE_EXPLANATIONS


def test_explain_flow_produces_one_row_per_step(one_flow):
    tp, apg = one_flow
    trace = explain_flow(tp, apg)
    assert len(trace) == len(tp.path)
    for i, row in enumerate(trace):
        assert row.step == i
        assert row.stmt_id == tp.path[i]
        assert row.reason  # non-empty for every step


def test_explain_flow_first_step_is_source(one_flow):
    tp, apg = one_flow
    trace = explain_flow(tp, apg)
    assert trace[0].rule == "source"


def test_explain_flow_middle_hops_carry_real_rules(one_flow):
    tp, apg = one_flow
    trace = explain_flow(tp, apg)
    valid = set(TAINT_RULES) | {"source"}
    for row in trace:
        assert row.rule in valid, f"unexpected rule at step {row.step}: {row.rule!r}"


def test_to_dict_json_ready(one_flow):
    import json
    tp, apg = one_flow
    for row in explain_flow(tp, apg):
        json.dumps(row.to_dict())


def test_summarize_flow_histograms_match_reasons(one_flow):
    tp, apg = one_flow
    s = summarize_flow(tp, apg)
    assert s["source_stmt"] == tp.source_stmt
    assert s["sink_stmt"] == tp.sink_stmt
    assert s["hops"] == max(0, len(tp.path) - 1)
    hist_total = sum(s["rule_histogram"].values())
    # +1 accounts for the "source" sentinel that summarize_flow skips
    assert hist_total == len(tp.reasons) - 1
