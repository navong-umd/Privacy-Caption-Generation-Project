"""Tests for Stage 8 — Privacy Nutrition Facts label generation + the viewer app."""
from __future__ import annotations

import json
from pathlib import Path

from step4_app.nutrition import build_nutrition, _risk
from step4_app.build_app import build_app


# ---------- risk indicator (transparent heuristic) ----------
def test_risk_is_monotonic_and_explained():
    low = _risk([{"category": "DATABASE_INFORMATION", "sink_type": "storage",
                  "purpose": [], "privacy_threat": ""}])
    high = _risk([{"category": "UNIQUE_IDENTIFIER", "sink_type": "network",
                   "purpose": ["Advertisement"], "privacy_threat": "Identifying;Linking"}])
    assert low["level"] == "Low" and high["score"] > low["score"]
    assert high["level"] in ("Medium", "High")
    assert high["factors"], "risk must explain its factors"
    assert high["network_egress_flows"] == 1 and high["identifier_access_flows"] == 1
    assert "Identifying" in high["linddun_threats"]


# ---------- nutrition facts ----------
def test_build_nutrition_outputs(dataset_dir, tmp_path):
    out = tmp_path / "nutrition"
    index = build_nutrition(str(dataset_dir), None, str(out))
    assert index["apps"], "expected at least one app"
    # weak fixture -> bootstrap banner present
    assert index["banner"], "weak labels must carry the BOOTSTRAP banner"
    pkg = next(iter(index["apps"]))
    label = json.loads((out / pkg.replace("/", "_") / "nutrition.json").read_text("utf-8"))
    assert label["security_risk"]["level"] in ("Low", "Medium", "High")
    assert set(label["purposes"]) == {"Functionality", "Advertisement", "Analytics", "Other"}
    assert set(label["practices"]) == {"Processing", "Collecting", "Sharing", "Other"}
    assert (out / pkg.replace("/", "_") / "nutrition.md").exists()
    assert (out / "nutrition_index.json").exists()


# ---------- the app ----------
def test_build_app_static_site(dataset_dir, tmp_path):
    out = tmp_path / "app"
    index = build_app(str(dataset_dir), None, str(out))
    idx_html = (out / "index.html").read_text("utf-8")
    assert "Privacy Nutrition Facts" in idx_html
    pkg = next(iter(index["apps"]))
    page = (out / (pkg.replace("/", "_") + ".html")).read_text("utf-8")
    assert pkg in page
    # the Neo4j panel renders the app_ppg_overlay cypher with the exact app_id (package@apk)
    assert "app_id" in page and "@" in page and "MATCH" in page
    assert "risk" in page.lower()
