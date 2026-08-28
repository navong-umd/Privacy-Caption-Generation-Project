"""Phase 5: per-edge provenance on TAINT_FLOW.

The plan's rule for the PPG stage:
    A reviewer should be able to inspect a privacy relationship and
    determine: WHY does this edge exist?

Every TAINT_FLOW edge must carry a taint_rule tag in {ddg, icfg, call_arg,
call_ret}. Anything else (empty, 'unknown', or an unrecognized value)
would mean the edge cannot be defended.
"""
from __future__ import annotations

import pandas as pd
import pytest

from stage4_ppg.taint import TAINT_RULES, TaintPath, propagate
from pplib.apg_model import load_apg
from pplib.io_utils import REPO_ROOT, load_yaml


VALID_RULES = set(TAINT_RULES)


def test_taint_rules_constant_is_the_expected_set():
    # Guard the contract that other consumers (PPG builder, tests, docs) rely on.
    assert VALID_RULES == {"ddg", "icfg", "call_arg", "call_ret"}


def test_propagate_tags_every_hop_with_a_rule(synth_apg_dir):
    """propagate() must return TaintPaths whose reasons parallel the path."""
    apg = load_apg(synth_apg_dir)
    cfg = load_yaml(REPO_ROOT / "configs" / "ppg.yaml")
    # Grab a small set of source statements manually so the test does not depend
    # on SourceCatalog. Any call to a known PI API works.
    sources = {sid for sid, s in apg.statements.items()
               if "getLastKnownLocation" in s.get("callee", "")
               or "getDeviceId" in s.get("callee", "")}
    sinks = {sid for sid, s in apg.statements.items()
             if "openConnection" in s.get("callee", "")
             or s.get("callee", "").startswith("android.util.Log")}
    if not sources or not sinks:
        pytest.skip("synthetic fixture has no source-to-sink flow to trace")

    paths = propagate(apg, sources, sinks, cfg)
    assert paths, "expected at least one taint path in the synthetic fixture"

    for tp in paths:
        assert isinstance(tp, TaintPath)
        assert len(tp.reasons) == len(tp.path), (
            f"reasons ({len(tp.reasons)}) must parallel path ({len(tp.path)})"
        )
        assert tp.reasons[0] == "source"
        for r in tp.reasons[1:]:
            assert r in VALID_RULES, f"unrecognized taint_rule: {r!r}"


def test_every_taint_flow_edge_in_the_built_ppg_has_a_defensible_rule(ppg_builder):
    """End-to-end: every TAINT_FLOW row in PPG_edges.csv carries a valid taint_rule."""
    _, out_dir = ppg_builder
    edges_csv = out_dir / "PPG_edges.csv"
    df = pd.read_csv(edges_csv, dtype=str, keep_default_na=False)

    taint = df[df["type"] == "TAINT_FLOW"]
    if taint.empty:
        pytest.skip("no TAINT_FLOW edges in this fixture")

    # Every edge must have a non-empty taint_rule.
    empties = (taint["taint_rule"] == "").sum()
    assert empties == 0, f"{empties} TAINT_FLOW edges have empty taint_rule"

    # And every rule must be in the canonical set (no 'unknown', no typos).
    seen = set(taint["taint_rule"].unique())
    bad = seen - VALID_RULES
    assert not bad, f"TAINT_FLOW edges carry unrecognized rules: {bad}"


def test_non_taint_flow_edges_have_empty_taint_rule(ppg_builder):
    """taint_rule is a TAINT_FLOW-only column; other edges leave it empty."""
    _, out_dir = ppg_builder
    df = pd.read_csv(out_dir / "PPG_edges.csv", dtype=str, keep_default_na=False)

    non_taint = df[df["type"] != "TAINT_FLOW"]
    if non_taint.empty:
        return
    populated = (non_taint["taint_rule"] != "").sum()
    assert populated == 0, (
        f"{populated} non-TAINT_FLOW edges have a taint_rule set (should be empty)"
    )
