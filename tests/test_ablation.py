"""Tests for the PPG-vs-APG ablation (offline; tiny training on the synthetic fixture)."""
from __future__ import annotations

from step2_convgnn.data import _node_features, _tokens, FEAT_DIM, TOKEN_HOOK_DIM
from step2_convgnn.ablation import run_ablation


def test_apg_only_zeroes_privacy_features_but_keeps_type():
    node = {"label": "Source", "is_source": "1", "permission": "READ_X",
            "sink_type": "network", "category": "LOCATION_INFORMATION"}
    t_full, f_full = _node_features(node, privacy_features=True)
    t_apg, f_apg = _node_features(node, privacy_features=False)
    assert t_full == t_apg                      # node-type id (APG structure) preserved
    assert any(v != 0 for v in f_full)          # full PPG carries privacy signal
    assert f_apg == [0.0] * FEAT_DIM            # APG-only zeroes the overlay vector (no tokens)


def test_statement_token_hook_fills_reserved_slots():
    node = {"label": "Statement", "code": "v0",
            "callee": "android.telephony.TelephonyManager->getDeviceId"}
    assert _tokens(node)                        # camelCase/identifier tokens extracted
    _, f_off = _node_features(node, privacy_features=False, token_features=False)
    _, f_on = _node_features(node, privacy_features=False, token_features=True)
    base = FEAT_DIM - TOKEN_HOOK_DIM
    assert f_off[base:] == [0.0] * TOKEN_HOOK_DIM          # hook empty by default
    assert any(v > 0 for v in f_on[base:])                # hook filled when enabled
    assert abs(sum(f_on[base:]) - 1.0) < 1e-6             # L1-normalized token block


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
