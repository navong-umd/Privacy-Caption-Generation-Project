"""Tests for Step 3 caption generation (offline mock; no network/keys)."""
from __future__ import annotations

import json

import pytest

from step3_caption.code2seq_baseline import Code2SeqBaseline
from step3_caption.generate import build_prompt, generate_captions
from step3_caption.llm_interface import MockProvider, get_provider


def test_mock_provider_is_deterministic_and_grounded():
    ev = {"category": "LOCATION_INFORMATION", "practice": ["Collecting", "Sharing"],
          "purpose": ["Advertisement"], "sink_type": "network",
          "privacy_threat": "Data Disclosure"}
    a = MockProvider().generate("", ev)
    b = MockProvider().generate("", ev)
    assert a == b                                   # deterministic
    assert "location" in a and "advertising" in a   # grounded in evidence
    assert "network" in a and "LINDDUN" in a


def test_mock_reads_pi_category_and_reports_zero_usage():
    out = MockProvider().generate("", {"pi_category": "LOCATION_INFORMATION", "practice": ["Collecting"]})
    assert "location" in out
    assert out.prompt_tokens == 0 and out.completion_tokens == 0


def test_condition_result_carries_provider_usage():
    from step3_caption.experiments import run_condition
    from step3_caption.llm_interface import GenerationResult

    class _Paid:
        name, model = "paid", "m"

        def generate(self, prompt, evidence):
            return GenerationResult("caption", 120, 30)

    res = run_condition({"prcs_id": "p", "code_snippet": "x"}, "A", _Paid())
    assert (res.prompt_tokens, res.completion_tokens) == (120, 30) and type(res.caption) is str


def test_get_provider_defaults_to_mock():
    assert isinstance(get_provider({"provider": "mock"}), MockProvider)


def test_real_provider_without_key_raises_clearly(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    cfg = {"provider": "anthropic",
           "providers": {"anthropic": {"model": "claude-opus-4-8", "api_key_env": "ANTHROPIC_API_KEY"}}}
    with pytest.raises(RuntimeError, match="needs env var"):
        get_provider(cfg)


def test_code2seq_baseline():
    rec = {"source_api": "android.location.LocationManager->getLastKnownLocation",
           "sink_api": "java.net.URL->openConnection", "labels": {"practice": ["Sharing"]}}
    cap = Code2SeqBaseline().caption(rec)
    assert "getLastKnownLocation" in cap and "share" in cap


def test_build_prompt_contains_evidence():
    p = build_prompt({"pi_type": "location", "practice": ["Sharing"], "purpose": ["Analytics"],
                      "sink_type": "network", "sink_api": "x", "source_api": "y"}, [])
    assert "location" in p and "Analytics" in p


def test_generate_captions_over_dataset(dataset_dir, tmp_path):
    caps = generate_captions(str(dataset_dir), str(tmp_path / "cap"))
    records = (dataset_dir / "adppg.jsonl").read_text().splitlines()
    assert len(caps) == len(records)
    assert all(c["caption"] and c["baseline_caption"] for c in caps)
    # weak labels -> banner carried on caption records
    assert all(c["weak_banner"] for c in caps)
    saved = json.loads((tmp_path / "cap" / "captions.json").read_text())
    assert len(saved) == len(caps)


def test_caption_sampling_caps_calls(dataset_dir, tmp_path):
    # --limit bounds total; --per-app bounds per package (so real-LLM runs stay cheap)
    lim = generate_captions(str(dataset_dir), str(tmp_path / "lim"), limit=3)
    assert len(lim) == 3
    per = generate_captions(str(dataset_dir), str(tmp_path / "per"), per_app=1)
    apps = [c["app_package"] for c in per]
    assert len(apps) == len(set(apps))              # at most one caption per app


def test_provider_override_does_not_need_config_change(dataset_dir, tmp_path):
    # explicit provider='mock' override path (keeps the file's default untouched)
    caps = generate_captions(str(dataset_dir), str(tmp_path / "ov"), provider="mock", limit=2)
    assert len(caps) == 2 and all(c["provider"] == "mock" for c in caps)
