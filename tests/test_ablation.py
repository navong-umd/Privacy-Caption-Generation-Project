"""Tests for the PPG-vs-APG ablation (offline; tiny training on the synthetic fixture)."""
from __future__ import annotations

from step2_convgnn.data import _node_features, FEAT_DIM
from step2_convgnn.ablation import run_ablation


def test_apg_only_zeroes_privacy_features_but_keeps_type():
    node = {"label": "Source", "is_source": "1", "permission": "READ_X",
            "sink_type": "network", "category": "LOCATION_INFORMATION"}
    t_full, f_full = _node_features(node, privacy_features=True)
    t_apg, f_apg = _node_features(node, privacy_features=False)
    assert t_full == t_apg                      # node-type id (APG structure) preserved
    assert any(v != 0 for v in f_full)          # full PPG carries privacy signal
    assert f_apg == [0.0] * FEAT_DIM            # APG-only zeroes the overlay vector


def test_ablation_runs_and_compares(dataset_dir, tmp_path):
    rep = run_ablation("configs/convgnn.yaml", str(dataset_dir), str(tmp_path / "abl"), epochs=5)
    assert "overall_macro_f1" in rep
    o = rep["overall_macro_f1"]
    assert {"full_ppg", "apg_only", "delta"} <= set(o)
    assert isinstance(rep["privacy_overlay_helps"], bool)
    assert (tmp_path / "abl" / "ablation.json").exists()
    assert (tmp_path / "abl" / "ablation.md").exists()
    # both conditions produced the four compared metrics
    assert {"practice_macro_f1", "purpose_macro_f1"} <= set(rep["metrics"])
