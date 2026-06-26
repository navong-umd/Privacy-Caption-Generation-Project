"""Unit + integration tests for Stage 4 (APG loader, catalogs, taint, PPG build)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from pplib.apg_model import load_apg
from pplib.schema import PPG_EDGE_COLUMNS, PPG_NODE_COLUMNS
from stage4_ppg.catalogs import SinkCatalog, SourceCatalog
from pplib.io_utils import load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------- APG adapter ----------
def test_apg_loader_reconstructs_classes(synth_apg_dir):
    apg = load_apg(synth_apg_dir)
    assert apg.methods and apg.statements
    # Class nodes + HAS_METHOD are reconstructed from method ids (Neo4j-only in Stage 2).
    assert apg.classes, "classes should be reconstructed"
    assert all("->" not in c for c in apg.classes)
    assert len(apg.has_method) == len(apg.methods)


def test_apg_loader_preserves_multi_app(synth_apg_dir):
    apg = load_apg(synth_apg_dir)
    app_ids = {m["app_id"] for m in apg.methods.values()}
    assert len(app_ids) == 2  # two synthetic apps


# ---------- catalogs ----------
def test_source_catalog_known_signature():
    cfg = load_yaml(REPO_ROOT / "configs" / "ppg.yaml")
    cat = SourceCatalog(cfg, REPO_ROOT)
    hit = cat.classify("android.telephony.TelephonyManager->getDeviceId")
    assert hit is not None and hit.category == "UNIQUE_IDENTIFIER" and hit.tier == "known"
    assert cat.classify("java.lang.String->length") is None


def test_sink_catalog_rules_and_heuristic():
    cat = SinkCatalog(REPO_ROOT / "configs" / "sinks.yaml")
    assert cat.classify("android.util.Log->d").sink_type == "logging"
    assert cat.classify("okhttp3.RealCall->execute").sink_type == "network"
    # unknown sink: external callee with an egress verb in the method name
    h = cat.classify_unknown("com.acme.net.Uploader->uploadBlob", is_internal=False)
    assert h is not None and h.known is False
    # internal callee is never a heuristic sink
    assert cat.classify_unknown("com.app.Foo->uploadBlob", is_internal=True) is None


# ---------- taint + build (integration) ----------
def test_ppg_build_finds_flows(ppg_builder):
    builder, _ = ppg_builder
    s = builder.summary()
    assert s["sources"] == 12 and s["sinks"] == 12
    assert s["taint_paths"] == 12


def test_ppg_interprocedural_flow(ppg_builder):
    builder, _ = ppg_builder
    # at least one taint path crosses a method boundary (source method != sink method)
    crossed = [tp for tp in builder.taint_paths
               if tp.source_stmt.split("_stmt_")[0] != tp.sink_stmt.split("_stmt_")[0]]
    assert crossed, "expected an inter-procedural taint flow"


def test_ppg_csv_schema_and_overlay(ppg_builder):
    _, out = ppg_builder
    nodes = pd.read_csv(out / "PPG_nodes.csv", dtype=str, keep_default_na=False)
    edges = pd.read_csv(out / "PPG_edges.csv", dtype=str, keep_default_na=False)
    assert list(nodes.columns) == PPG_NODE_COLUMNS
    assert list(edges.columns) == PPG_EDGE_COLUMNS
    # overlay labels present
    assert set(nodes["label"]) >= {"Source", "Sink", "DataItem"}
    assert "TAINT_FLOW" in set(edges["type"])
    assert "PRIVACY_RELATION" in set(edges["type"])
    # LINDDUN threat tagged on at least one flow
    assert any(t for t in edges["privacy_threat"].tolist())


def test_ppg_graph_serializations_exist(ppg_builder):
    _, out = ppg_builder
    assert (out / "ppg.graphml").exists()
    assert (out / "ppg.pkl").exists()
    assert (out / "taint_paths.json").exists()
