"""Phase 10: rule + TF-IDF baselines run and produce well-shaped predictions."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pplib.io_utils import REPO_ROOT
from pplib.pact_schema import PACT_SCHEMA_VERSION
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
from stage4_ppg.build_ppg import build_ppg
from step2_prcs.extract_prcs import extract_prcs
from step2_dataset.build_dataset import build_dataset
from step3_caption.baselines import (
    BASELINE_NAMES,
    BaselinePrediction,
    RuleBaseline,
    TfIdfBaseline,
    multilabel_metrics,
)


@pytest.fixture(scope="module")
def labeled_records(tmp_path_factory) -> list[dict]:
    root = tmp_path_factory.mktemp("baselines_phase10")
    build_ppg(
        str(REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"),
        str(REPO_ROOT / "configs" / "ppg.yaml"),
        str(root / "ppg"),
    )
    extract_prcs(str(root / "ppg"), str(root / "prcs"))
    build_dataset(str(root / "prcs"), str(root / "dataset"))
    return [json.loads(line) for line in
            (root / "dataset" / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]


def test_baseline_names_are_the_expected_two():
    assert BASELINE_NAMES == ("rule", "tfidf")


def test_rule_baseline_predicts_valid_labels(labeled_records):
    preds = RuleBaseline().fit(labeled_records).predict(labeled_records)
    assert len(preds) == len(labeled_records)
    for p in preds:
        assert isinstance(p, BaselinePrediction)
        assert p.baseline == "rule"
        assert p.schema_version == PACT_SCHEMA_VERSION
        for lbl in p.practice:
            assert lbl in PRACTICE_LABELS
        for lbl in p.purpose:
            assert lbl in PURPOSE_LABELS


def test_tfidf_baseline_fits_and_predicts(labeled_records):
    baseline = TfIdfBaseline(max_features=1000).fit(labeled_records)
    preds = baseline.predict(labeled_records)
    assert len(preds) == len(labeled_records)
    for p in preds:
        assert p.baseline == "tfidf"
        # Predictions must be a subset of the canonical label set (possibly empty).
        for lbl in p.practice:
            assert lbl in PRACTICE_LABELS
        for lbl in p.purpose:
            assert lbl in PURPOSE_LABELS


def test_tfidf_predict_before_fit_raises():
    with pytest.raises(RuntimeError):
        TfIdfBaseline().predict_one({"code_snippet": "x"})


def test_multilabel_metrics_shape(labeled_records):
    preds = RuleBaseline().fit(labeled_records).predict(labeled_records)
    m = multilabel_metrics(preds, labeled_records)
    assert set(m) >= {"practice", "purpose", "banner"}
    for head in ("practice", "purpose"):
        for k in ("precision_micro", "recall_micro", "f1_micro",
                  "precision_macro", "recall_macro", "f1_macro"):
            assert k in m[head], f"missing metric {head}/{k}"
            assert 0.0 <= m[head][k] <= 1.0


def test_rule_baseline_matches_weak_labels_exactly(labeled_records):
    """Rule baseline is defined as the WeakLabeler; predictions on WEAK-labeled records must
    reproduce the labels themselves (up to set equality)."""
    baseline = RuleBaseline()
    for r in labeled_records:
        if r["labels"]["label_source"] != "weak":
            continue
        pred = baseline.predict_one(r)
        assert set(pred.practice) == set(r["labels"]["practice"])
        assert set(pred.purpose) == set(r["labels"]["purpose"])


def test_baseline_prediction_to_dict_is_json_ready(labeled_records):
    preds = RuleBaseline().fit(labeled_records).predict(labeled_records[:3])
    for p in preds:
        json.dumps(p.to_dict())
