"""Phase 3 APG schema-conformance tests.

Enforces the invariants documented in research/APG_SCHEMA.md §8 against the
committed synthetic APG fixtures. Any APG produced by any adapter (present or
future) MUST pass these checks; a violation surfaces here as a failing CI build
rather than an obscure crash deep in the PPG builder.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from pplib.io_utils import REPO_ROOT, method_class, stmt_method_id
from pplib.schema import (
    APG_EDGE_COLUMNS,
    APG_EDGE_TYPES,
    APG_NODE_COLUMNS,
    APG_NODE_LABELS,
)

VIEWS = ["AST", "MCG", "ICFG", "DDG"]
FIXTURE_DIRS = [
    REPO_ROOT / "data" / "fixtures" / "synthetic_apg",
    REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large",
]

# HAS_METHOD is reconstructed on load; the on-disk CSVs never emit it.
ON_DISK_EDGE_TYPES = set(APG_EDGE_TYPES) - {"HAS_METHOD"}


def _read(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)


@pytest.fixture(params=FIXTURE_DIRS, ids=lambda p: p.name)
def fixture_dir(request) -> Path:
    d = request.param
    if not d.exists():
        pytest.skip(f"fixture missing: {d}")
    return d


# --- 1. Column contract (APG_SCHEMA.md §8.1) ---

def test_all_nodes_csvs_use_exact_column_contract(fixture_dir):
    for v in VIEWS:
        df = _read(fixture_dir / f"{v}_nodes.csv")
        assert list(df.columns) == APG_NODE_COLUMNS, (
            f"{v}_nodes.csv columns {list(df.columns)} != {APG_NODE_COLUMNS}"
        )


def test_all_edges_csvs_use_exact_column_contract(fixture_dir):
    for v in VIEWS:
        df = _read(fixture_dir / f"{v}_edges.csv")
        assert list(df.columns) == APG_EDGE_COLUMNS, (
            f"{v}_edges.csv columns {list(df.columns)} != {APG_EDGE_COLUMNS}"
        )


# --- 2. Enum validity (APG_SCHEMA.md §8.2, §8.3) ---

def test_every_node_label_is_valid(fixture_dir):
    valid = set(APG_NODE_LABELS)
    for v in VIEWS:
        df = _read(fixture_dir / f"{v}_nodes.csv")
        if df.empty:
            continue
        bad = set(df["label"].unique()) - valid
        assert not bad, f"{v}_nodes.csv has invalid labels: {bad}"


def test_every_edge_type_is_valid_and_never_has_method(fixture_dir):
    for v in VIEWS:
        df = _read(fixture_dir / f"{v}_edges.csv")
        if df.empty:
            continue
        bad = set(df["type"].unique()) - ON_DISK_EDGE_TYPES
        assert not bad, f"{v}_edges.csv has invalid edge types: {bad}"


# --- 3. Identifier shape (APG_SCHEMA.md §8.4, §8.5) ---

def test_method_ids_contain_exactly_one_arrow(fixture_dir):
    df = _read(fixture_dir / "MCG_nodes.csv")
    if df.empty:
        return
    methods = df[df["label"] == "Method"]["id"].tolist()
    assert methods, "MCG_nodes.csv has no Method rows"
    bad = [m for m in methods if m.count("->") != 1]
    assert not bad, f"malformed Method ids: {bad[:5]}"


def test_statement_ids_encode_owning_method(fixture_dir):
    df = _read(fixture_dir / "AST_nodes.csv")
    if df.empty:
        return
    stmts = df[df["label"] == "Statement"]["id"].tolist()
    methods = set(df[df["label"] == "Method"]["id"].tolist())
    for sid in stmts:
        assert "_stmt_" in sid, f"Statement id missing _stmt_: {sid}"
        mid = stmt_method_id(sid)
        assert mid in methods, f"Statement {sid} references unknown Method {mid}"


# --- 4. Referential integrity (APG_SCHEMA.md §8.7) ---

def test_ast_has_statement_edges_reference_known_nodes(fixture_dir):
    nodes = set(_read(fixture_dir / "AST_nodes.csv")["id"].tolist())
    edges = _read(fixture_dir / "AST_edges.csv")
    if edges.empty:
        return
    bad = [(s, e) for s, e in zip(edges["start_id"], edges["end_id"])
           if s not in nodes or e not in nodes]
    assert not bad, f"AST_edges.csv has dangling endpoints: {bad[:3]}"


def test_ddg_edges_reference_known_statements(fixture_dir):
    nodes = set(_read(fixture_dir / "DDG_nodes.csv")["id"].tolist())
    edges = _read(fixture_dir / "DDG_edges.csv")
    if edges.empty:
        return
    bad = [(s, e) for s, e in zip(edges["start_id"], edges["end_id"])
           if s not in nodes or e not in nodes]
    assert not bad, f"DDG_edges.csv has dangling endpoints: {bad[:3]}"


def test_icfg_edges_reference_known_nodes(fixture_dir):
    nodes = set(_read(fixture_dir / "ICFG_nodes.csv")["id"].tolist())
    edges = _read(fixture_dir / "ICFG_edges.csv")
    if edges.empty:
        return
    bad = [(s, e) for s, e in zip(edges["start_id"], edges["end_id"])
           if s not in nodes or e not in nodes]
    assert not bad, f"ICFG_edges.csv has dangling endpoints: {bad[:3]}"


def test_mcg_calls_may_reference_external_callees(fixture_dir):
    """MCG is the one view where end_id may not exist as a node — external calls are allowed.

    We assert only that start_id (the caller) is always a known Method.
    """
    nodes = set(_read(fixture_dir / "MCG_nodes.csv")["id"].tolist())
    edges = _read(fixture_dir / "MCG_edges.csv")
    if edges.empty:
        return
    bad_start = [s for s in edges["start_id"] if s not in nodes]
    assert not bad_start, f"MCG_edges.csv has unknown callers: {bad_start[:3]}"


# --- 5. app_id populated (APG_SCHEMA.md §8.8, weaker form) ---
#
# The doc's stronger claim — "exactly one app_id per single-APK APG" — can only
# be verified against APGs that came from a single .apk. Both synthetic fixtures
# are multi-APK on purpose (they seed the dataset splitter). The universal
# invariant we CAN assert against every fixture is that no row has an empty
# app_id: provenance must never be lost.

def test_every_row_has_a_populated_app_id(fixture_dir):
    for v in VIEWS:
        for f in ("nodes", "edges"):
            df = _read(fixture_dir / f"{v}_{f}.csv")
            if df.empty or "app_id" not in df.columns:
                continue
            empties = int((df["app_id"] == "").sum())
            assert empties == 0, f"{v}_{f}.csv has {empties} rows with empty app_id"
