"""Tests for the Neo4j display layer: what_it_does semantics + the Cypher query library."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from stage4_ppg.semantics import WhatItDoesCache, describe, describe_node, enrich_graph
from stage4_ppg.cypher_runner import load_library, DEFAULT_LIB

REPO_ROOT = Path(__file__).resolve().parent.parent


# ---------- what_it_does (semantics) ----------
def test_describe_node_roles_are_human_readable():
    src = describe_node("s1", {"label": "Source", "api": "android.telephony.TelephonyManager->getDeviceId",
                               "pi_type": "UNIQUE_IDENTIFIER", "permission": "READ_PHONE_STATE"})
    assert "device identifier" in src and "TelephonyManager.getDeviceId" in src

    snk = describe_node("k1", {"label": "Sink", "api": "okhttp3.RealCall->execute", "sink_type": "network"})
    assert "remote server" in snk and "RealCall.execute" in snk

    stmt = describe_node("st1", {"label": "Statement", "tainted": True, "pi_type": "LOCATION_INFORMATION",
                                 "callee": "java.util.Map->put"})
    assert "tainted" in stmt and "location" in stmt


def test_describe_is_deterministic_offline():
    d = {"label": "Sink", "api": "android.util.Log->d", "sink_type": "logging"}
    a, sa = describe("n", d)
    b, sb = describe("n", d)
    assert a == b and sa == "rule" and sb == "rule"


def test_what_it_does_cache_preserves_provenance(tmp_path):
    cache = WhatItDoesCache(tmp_path / "wid.json")
    d = {"label": "Source", "api": "x->y", "pi_type": "CONTACT_INFORMATION"}
    text, src = describe("n1", d, cache=cache)
    cache.save()
    # a fresh cache over the same file returns the cached text AND the ORIGINAL provenance
    # (not a generic "cache") so LLM-derived descriptions stay marked llm:<provider>.
    cache2 = WhatItDoesCache(tmp_path / "wid.json")
    text2, src2 = describe("n1", d, cache=cache2)
    assert text2 == text and src2 == src == "rule"


# ---------- enrichment on a real (synthetic) PPG ----------
def test_enrich_sets_what_it_does_on_every_node(ppg_builder):
    builder, _ = ppg_builder
    missing = [n for n, d in builder.G.nodes(data=True) if not d.get("what_it_does")]
    assert not missing, f"{len(missing)} nodes without what_it_does"
    # sources/sinks get role-specific prose
    src_descs = [d["what_it_does"] for _, d in builder.G.nodes(data=True) if d.get("label") == "Source"]
    assert src_descs and all("Reads the user's" in s for s in src_descs)


def test_ppg_csv_has_what_it_does_column(ppg_builder):
    _, out = ppg_builder
    nodes = pd.read_csv(out / "PPG_nodes.csv", dtype=str, keep_default_na=False)
    assert "what_it_does" in nodes.columns
    src_rows = nodes[nodes["label"] == "Source"]
    assert len(src_rows) and (src_rows["what_it_does"].str.len() > 0).all()


# ---------- Cypher query library ----------
def test_query_library_parses_expected_queries():
    lib = load_library(DEFAULT_LIB)
    expected = {"app_apg", "app_ppg_overlay", "list_sources", "list_sinks", "flows_for_app",
                "prcs_subgraph", "taint_path_snippets", "node_detail", "app_summary",
                "list_apps", "clear_app"}
    assert expected <= set(lib), f"missing: {expected - set(lib)}"
    for q in lib.values():
        assert q.cypher.strip(), f"{q.name} has empty cypher"
        assert q.description, f"{q.name} has no description"


def test_query_params_and_render():
    lib = load_library(DEFAULT_LIB)
    assert "app_id" in lib["app_ppg_overlay"].params()
    rendered = lib["app_ppg_overlay"].render(app_id="com.x@x.apk")
    assert "'com.x@x.apk'" in rendered and "$app_id" not in rendered
    # prcs_subgraph needs both endpoint ids
    assert set(lib["prcs_subgraph"].params()) == {"source_id", "sink_id"}


def test_clear_app_marked_destructive():
    lib = load_library(DEFAULT_LIB)
    assert lib["clear_app"].destructive is True
