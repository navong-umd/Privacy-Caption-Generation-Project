"""Tests for Step 4 evaluation harness (text metrics, caption/compliance/classification)."""
from __future__ import annotations

from pathlib import Path

import pytest

from pplib.io_utils import dump_json
from step3_caption.generate import generate_captions
from step3_policy.assemble import assemble
from step4_eval.evaluate import (evaluate_captions, evaluate_classification,
                                 evaluate_compliance, run)
from step4_eval.text_metrics import rouge_l, sentence_bleu


def _artifacts(dataset_dir: Path, tmp_path: Path):
    cap = tmp_path / "cap"
    generate_captions(str(dataset_dir), str(cap))
    pol = tmp_path / "pol"
    assemble(str(dataset_dir), str(cap), str(pol))
    return cap, pol


# ---------- text metrics ----------
def test_bleu_rouge_bounds():
    assert sentence_bleu("the app shares location", ["the app shares location"]) > 0.9
    assert rouge_l("the app shares location", ["the app shares location"]) == pytest.approx(1.0)
    # disjoint scores far below an exact match (smoothing keeps short-sentence BLEU non-zero)
    assert sentence_bleu("aaa bbb", ["zzz yyy"]) < sentence_bleu("aaa bbb", ["aaa bbb"])
    assert rouge_l("aaa bbb", ["zzz yyy"]) == 0.0


# ---------- caption eval ----------
def test_caption_eval_no_references_emits_sheet(dataset_dir, tmp_path):
    cap, _ = _artifacts(dataset_dir, tmp_path)
    out = tmp_path / "eval"; out.mkdir()
    res = evaluate_captions(str(cap), out, references=None)
    assert "no references" in res["status"]
    assert (out / "caption_rating_sheet.csv").exists()


def test_caption_eval_with_references_scores(dataset_dir, tmp_path):
    cap, _ = _artifacts(dataset_dir, tmp_path)
    out = tmp_path / "eval2"; out.mkdir()
    import json
    caps = json.loads((cap / "captions.json").read_text())
    refs = {caps[0]["prcs_id"]: caps[0]["caption"]}      # perfect ref for one item
    rp = tmp_path / "refs.json"; dump_json(refs, rp)
    res = evaluate_captions(str(cap), out, references=str(rp))
    assert res["status"] == "ok" and res["bleu4"] > 0.5 and res["rouge_l"] > 0.5


# ---------- compliance ----------
def test_compliance_completeness(dataset_dir, tmp_path):
    _, pol = _artifacts(dataset_dir, tmp_path)
    res = evaluate_compliance(str(pol), reference_policy=None)
    assert 0.0 <= res["overall_completeness"] <= 1.0
    assert all(0 <= a["completeness"] <= 1 for a in res["per_app"].values())


# ---------- classification ----------
def test_classification_skips_without_checkpoint(dataset_dir):
    res = evaluate_classification(str(dataset_dir), checkpoint=None)
    assert "skipped" in res["status"]


def test_classification_with_checkpoint(dataset_dir, tmp_path):
    pytest.importorskip("torch")
    from step2_convgnn.train import train
    train("configs/convgnn.yaml", str(dataset_dir), str(tmp_path / "cg"), epochs=5)
    res = evaluate_classification(str(dataset_dir), str(tmp_path / "cg" / "best.pt"))
    assert res["status"] == "ok" and res["is_weak"] is True
    assert 0.0 <= res["practice_macro_f1"] <= 1.0


# ---------- full run ----------
def test_run_report_has_bootstrap_banner(dataset_dir, tmp_path):
    cap, pol = _artifacts(dataset_dir, tmp_path)
    report = run(str(dataset_dir), str(cap), str(pol), str(tmp_path / "ev"))
    assert report["bootstrap"] is True       # weak labels + no refs
    assert (tmp_path / "ev" / "eval_report.md").exists()
