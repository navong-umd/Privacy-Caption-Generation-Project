"""Unit + integration tests for Step 2 PRCS extraction."""
from __future__ import annotations

import pandas as pd

from step2_prcs.extract_prcs import INDEX_COLUMNS, extract_prcs, extract_from_graph
from pplib.io_utils import load_json


def test_prcs_extraction_counts(ppg_builder):
    builder, out = ppg_builder
    records = extract_prcs(str(out), str(out / "prcs"))
    # one PRCS per taint path
    assert len(records) == builder.summary()["taint_paths"] == 12


def test_prcs_record_fields_and_subgraph(ppg_builder):
    _, out = ppg_builder
    records = extract_prcs(str(out), str(out / "prcs"))
    r = records[0]
    assert r.source_api and r.sink_api and r.prcs_id.startswith("prcs_")
    assert r.app_package and r.apk_filename
    labels = {n["label"] for n in r.subgraph["nodes"]}
    etypes = {e["type"] for e in r.subgraph["edges"]}
    assert {"Source", "Sink", "Statement", "Method"} <= labels
    assert "TAINT_FLOW" in etypes and "PRIVACY_RELATION" in etypes


def test_prcs_interprocedural_spans_two_methods(ppg_builder):
    _, out = ppg_builder
    records = extract_prcs(str(out), str(out / "prcs"))
    multi = [r for r in records if len(r.involved_methods) >= 2]
    assert multi, "expected at least one inter-procedural PRCS"


def test_prcs_id_is_deterministic(ppg_builder):
    builder, _ = ppg_builder
    import pickle, json
    paths = [{"source_stmt": tp.source_stmt, "sink_stmt": tp.sink_stmt,
              "path": tp.path, "app_id": tp.app_id} for tp in builder.taint_paths]
    a = {r.prcs_id for r in extract_from_graph(builder.G, paths)}
    b = {r.prcs_id for r in extract_from_graph(builder.G, paths)}
    assert a == b and len(a) == len(paths)


def test_prcs_index_csv_contract(ppg_builder):
    _, out = ppg_builder
    extract_prcs(str(out), str(out / "prcs"))
    df = pd.read_csv(out / "prcs" / "prcs_index.csv", dtype=str, keep_default_na=False)
    assert list(df.columns) == INDEX_COLUMNS
    assert len(df) == 12
    # the per-PRCS JSON written by the extractor loads back (cross-stage I/O contract)
    rec = load_json(out / "prcs" / f"{df.iloc[0]['prcs_id']}.json")
    assert "subgraph" in rec and "code_snippet" in rec
