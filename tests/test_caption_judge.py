"""Tests for the LLM-as-judge caption evaluation (offline mock judge; no network/keys)."""
from __future__ import annotations

from step4_eval.caption_judge import _heuristic_score, _heuristic_pairwise, judge_captions


def test_heuristic_score_rewards_grounding():
    f = {"pi": "LOCATION_INFORMATION", "pi_term": "location",
         "practice": ["Collecting", "Sharing"], "purpose": ["Advertisement"], "sink_type": "network"}
    good = _heuristic_score(
        "This app collects your location and shares it over the network for advertising.", f)
    bad = _heuristic_score("getX value flows to y; app appears to share this data.", f)
    assert good["accuracy"] > bad["accuracy"]
    assert good["readability"] >= bad["readability"]
    assert good["faithful"] is True


def test_pairwise_prefers_grounded_caption():
    f = {"pi": "UNIQUE_IDENTIFIER", "pi_term": "identifier", "practice": ["Collecting"],
         "purpose": ["Analytics"], "sink_type": "network"}
    win = _heuristic_pairwise(
        "This app reads your device identifier and sends it to an analytics service.",
        "getDeviceId flows to send.", f)
    assert win == "llm"


def test_judge_over_dataset_mock(dataset_dir, tmp_path):
    from step3_caption.generate import generate_captions
    caps_dir = tmp_path / "caps"
    generate_captions(str(dataset_dir), str(caps_dir))            # mock captions + baseline
    rep = judge_captions(str(dataset_dir), str(caps_dir), str(tmp_path / "judge"), provider_name="mock")
    assert rep["banner"].startswith("LLM-JUDGED") and rep["n_captions"] > 0
    assert 0.0 <= rep["pairwise"]["llm_win_rate"] <= 1.0
    # the grounded mock caption should read at least as well as the terse code2seq baseline
    assert rep["llm_mean"]["readability"] >= rep["baseline_mean"]["readability"]
    assert (tmp_path / "judge" / "caption_eval.json").exists()
    assert (tmp_path / "judge" / "caption_eval.md").exists()
