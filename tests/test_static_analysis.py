"""Phase 2 canonical-static-analysis tests.

Covers:
  1. APG_META.json provenance roundtrip (no heavy deps).
  2. Deterministic write_apg output (no heavy deps) — the same in-memory APG
     serializes byte-identical CSVs across independent write calls.
  3. Real-APK smoke test for adapters.run_apg_csv against the APK named by the
     PPCAP_SAMPLE_APK env var (APKs are never committed). Skipped cleanly when
     the variable is unset or androguard is not installed.
"""
from __future__ import annotations

import filecmp
import os
from pathlib import Path

import pytest

from pplib.apg_model import (
    APG_META_FILENAME,
    load_apg,
    load_apg_meta,
    sha256_file,
    write_apg,
    write_apg_meta,
)

APG_CSV_NAMES = [
    "AST_nodes.csv", "AST_edges.csv",
    "MCG_nodes.csv", "MCG_edges.csv",
    "ICFG_nodes.csv", "ICFG_edges.csv",
    "DDG_nodes.csv", "DDG_edges.csv",
]

SAMPLE_APK = Path(os.environ["PPCAP_SAMPLE_APK"]) if os.environ.get("PPCAP_SAMPLE_APK") else None


# ---------- 1. Metadata roundtrip ----------

def test_apg_meta_roundtrip(tmp_path):
    meta = {
        "apk_sha256": "a" * 64,
        "app_id": "com.example@app.apk",
        "generator": "adapters.run_apg_csv",
        "generator_version": "2.0.0",
        "summary": {"classes": 1, "methods": 2, "statements": 3},
    }
    path = write_apg_meta(meta, tmp_path)
    assert path.name == APG_META_FILENAME
    assert path.exists()

    loaded = load_apg_meta(tmp_path)
    assert loaded == meta  # exact roundtrip (sort_keys is deterministic, dict eq is order-agnostic)


def test_apg_meta_absent_returns_empty_dict(tmp_path):
    assert load_apg_meta(tmp_path) == {}


def test_sha256_file_deterministic(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"hello privacy")
    first = sha256_file(p)
    second = sha256_file(p)
    assert first == second
    assert len(first) == 64
    assert sha256_file(tmp_path / "missing.bin") == ""


# ---------- 2. Deterministic write_apg ----------

def test_write_apg_is_deterministic(synth_apg_dir, tmp_path):
    """Load an APG from the committed fixture, write it twice, assert byte-identical output.

    Guards against non-deterministic ordering in write_apg — every downstream stage
    depends on stable inputs to trust cross-run diffs.
    """
    apg = load_apg(synth_apg_dir)
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    write_apg(apg, out_a)
    write_apg(apg, out_b)

    for name in APG_CSV_NAMES:
        pa, pb = out_a / name, out_b / name
        assert pa.exists() and pb.exists(), f"missing {name}"
        assert filecmp.cmp(pa, pb, shallow=False), f"non-deterministic output: {name}"


def test_write_apg_roundtrip_preserves_shape(synth_apg_dir, tmp_path):
    """load -> write -> load produces an APG with the same node/edge counts."""
    a1 = load_apg(synth_apg_dir)
    write_apg(a1, tmp_path)
    a2 = load_apg(tmp_path)
    assert len(a1.classes) == len(a2.classes)
    assert len(a1.methods) == len(a2.methods)
    assert len(a1.statements) == len(a2.statements)
    assert len(a1.calls) == len(a2.calls)
    assert len(a1.icfg_next) == len(a2.icfg_next)
    assert len(a1.data_depends) == len(a2.data_depends)


# ---------- 3. Real-APK smoke test ----------

@pytest.mark.skipif(SAMPLE_APK is None or not SAMPLE_APK.exists(),
                    reason="set PPCAP_SAMPLE_APK to a local .apk to run the real-APK smoke test")
def test_run_apg_csv_on_sample_apk(tmp_path):
    """Exercises adapters.run_apg_csv end-to-end on a real APK.

    Guarded by importorskip('androguard') so the lean CI profile skips cleanly.
    Asserts:
      - all 8 APG CSVs are written and non-empty
      - APG_META.json is written with expected keys and a valid sha256 pin
      - the APG has at least one Class, Method, and Statement (the sample APK is not trivial)
    """
    pytest.importorskip("androguard")
    from adapters.run_apg_csv import run_apg_csv

    apg = run_apg_csv(str(SAMPLE_APK), str(tmp_path))

    # 3a. CSVs written and non-empty.
    for name in APG_CSV_NAMES:
        p = tmp_path / name
        assert p.exists(), f"missing {name}"
        assert p.stat().st_size > 0, f"empty {name}"

    # 3b. Meta written with expected keys.
    meta = load_apg_meta(tmp_path)
    assert meta, "APG_META.json missing"
    for key in ("apk_sha256", "apk_size_bytes", "app_id", "package_name",
                "generator", "generator_version", "androguard_version",
                "python_version", "generated_at", "summary"):
        assert key in meta, f"APG_META missing key: {key}"
    assert meta["generator"] == "adapters.run_apg_csv"
    assert len(meta["apk_sha256"]) == 64
    assert meta["apk_size_bytes"] == SAMPLE_APK.stat().st_size

    # 3c. APG is non-trivial (sample APK is a real 11 MB app).
    assert len(apg.classes) > 0
    assert len(apg.methods) > 0
    assert len(apg.statements) > 0

    # 3d. Meta summary matches in-memory APG (self-consistency).
    s = meta["summary"]
    assert s["classes"] == len(apg.classes)
    assert s["methods"] == len(apg.methods)
    assert s["statements"] == len(apg.statements)
