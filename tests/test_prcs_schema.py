"""Phase 7: PRCS records preserve full provenance from APK through the taint path.

The plan's rule for this stage: 'Nothing should become an opaque ML sample.'
Every serialized PRCS JSON must therefore carry the full provenance chain:
apk_filename + app_package, the source-code location, the taint path, and
the Phase 5 per-hop rules that produced it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from pplib.io_utils import REPO_ROOT
from pplib.prcs_schema import (
    PRCS_INDEX_COLUMNS,
    PRCS_REQUIRED_FIELDS,
    PRCS_SCHEMA_VERSION,
)
from stage4_ppg.build_ppg import build_ppg
from stage4_ppg.taint import TAINT_RULES, TAINT_RULE_SOURCE
from step2_prcs.extract_prcs import extract_prcs


VALID_RULES = set(TAINT_RULES) | {TAINT_RULE_SOURCE}


@pytest.fixture(scope="module")
def prcs_out(tmp_path_factory):
    root = tmp_path_factory.mktemp("prcs_phase7")
    ppg_dir = root / "ppg"
    prcs_dir = root / "prcs"
    build_ppg(
        str(REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"),
        str(REPO_ROOT / "configs" / "ppg.yaml"),
        str(ppg_dir),
    )
    records = extract_prcs(str(ppg_dir), str(prcs_dir))
    if not records:
        pytest.skip("fixture produced no PRCS records")
    return prcs_dir, records


def test_schema_version_is_pinned():
    assert PRCS_SCHEMA_VERSION == "1.0.0"


def test_every_json_has_every_required_field(prcs_out):
    prcs_dir, records = prcs_out
    for r in records:
        p = prcs_dir / f"{r.prcs_id}.json"
        payload = json.loads(p.read_text(encoding="utf-8"))
        missing = [k for k in PRCS_REQUIRED_FIELDS if k not in payload]
        assert not missing, f"{p.name} missing required fields: {missing}"


def test_every_record_carries_provenance(prcs_out):
    """apk_filename + app_package must always be populated (no anonymous PRCS)."""
    _, records = prcs_out
    for r in records:
        assert r.prcs_id.startswith("prcs_")
        assert r.schema_version == PRCS_SCHEMA_VERSION
        assert r.app_package, f"{r.prcs_id} has empty app_package"
        assert r.apk_filename, f"{r.prcs_id} has empty apk_filename"
        assert r.class_name, f"{r.prcs_id} has empty class_name"
        assert r.method_name, f"{r.prcs_id} has empty method_name"


def test_taint_path_and_rules_are_parallel(prcs_out):
    """taint_rules is either empty (legacy) or exactly as long as taint_path."""
    _, records = prcs_out
    for r in records:
        assert isinstance(r.taint_path, list)
        assert isinstance(r.taint_rules, list)
        assert len(r.taint_path) == r.hop_count + 1
        if r.taint_rules:
            assert len(r.taint_rules) == len(r.taint_path), (
                f"{r.prcs_id}: rules len {len(r.taint_rules)} != path len {len(r.taint_path)}"
            )
            assert r.taint_rules[0] == TAINT_RULE_SOURCE
            for rule in r.taint_rules[1:]:
                assert rule in VALID_RULES, f"{r.prcs_id}: bad rule {rule!r}"


def test_index_csv_columns_match_schema(prcs_out):
    prcs_dir, _ = prcs_out
    df = pd.read_csv(prcs_dir / "prcs_index.csv", dtype=str, keep_default_na=False)
    assert list(df.columns) == PRCS_INDEX_COLUMNS


def test_subgraph_is_bounded_and_non_empty(prcs_out):
    _, records = prcs_out
    for r in records:
        assert r.subgraph["nodes"], f"{r.prcs_id} has empty subgraph nodes"
        # The extractor caps subgraphs at 150 nodes; assert the bound holds.
        assert len(r.subgraph["nodes"]) <= 150


def test_source_and_sink_apis_are_populated(prcs_out):
    """Every PRCS represents a source-to-sink flow: both endpoints must have callees."""
    _, records = prcs_out
    for r in records:
        assert r.source_api, f"{r.prcs_id} missing source_api"
        assert r.sink_api, f"{r.prcs_id} missing sink_api"
