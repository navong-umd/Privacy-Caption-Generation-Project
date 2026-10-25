"""Matrix statistics: scoring, t-interval, item and paired bootstraps."""
from __future__ import annotations

import numpy as np
import pytest

from pplib.matrix_stats import (_macro_f1_draws, bootstrap_interval, label_matrix, label_support,
                                paired_bootstrap, score, t_interval)
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
from step2_convgnn.metrics import multilabel_metrics

IDS = [f"p{i}" for i in range(8)]
GOLD = {i: {"practice": ["Collecting"] + (["Sharing"] if n % 2 else []),
            "purpose": ["Functionality"] if n < 5 else ["Analytics"]}
        for n, i in enumerate(IDS)}
PRED = {i: {"practice": ["Collecting"] + (["Sharing"] if n % 3 == 0 else []),
            "purpose": ["Functionality"] if n < 6 else ["Analytics"]}
        for n, i in enumerate(IDS)}


def test_label_matrix_layout():
    m = label_matrix(IDS, GOLD)
    assert m["practice"].shape == (8, len(PRACTICE_LABELS))
    assert m["purpose"].shape == (8, len(PURPOSE_LABELS))
    assert m["practice"][:, PRACTICE_LABELS.index("Collecting")].sum() == 8


def test_score_matches_the_training_metrics():
    g, p = label_matrix(IDS, GOLD), label_matrix(IDS, PRED)
    s = score(g, p)
    ref = multilabel_metrics(g["practice"], p["practice"], PRACTICE_LABELS, "practice")
    assert s["practice_macro_f1"] == ref["practice_macro_f1"]
    assert s["macro_f1"] == pytest.approx((s["practice_macro_f1"] + s["purpose_macro_f1"]) / 2)


def test_vectorized_draws_match_sklearn_on_each_resample():
    g, p = label_matrix(IDS, GOLD), label_matrix(IDS, PRED)
    idx = np.random.default_rng(1).integers(0, len(IDS), size=(5, len(IDS)))
    draws = _macro_f1_draws(g, p, idx)
    for b in range(5):
        sub = lambda m: {h: m[h][idx[b]] for h in m}
        assert draws["macro_f1"][b] == pytest.approx(score(sub(g), sub(p))["macro_f1"])


def test_label_without_positives_does_not_crash():
    g, p = label_matrix(IDS, GOLD), label_matrix(IDS, PRED)
    assert label_support(g)["purpose_Advertisement"] == 0
    s = score(g, p)
    assert s["purpose_Advertisement_F1"] == 0.0
    bi = bootstrap_interval(g, p, draws=200)
    m = bi["metrics"]["macro_f1"]
    assert m["ci_low"] <= m["estimate"] <= m["ci_high"]


def test_t_interval_known_values():
    t = t_interval([1.0, 2.0, 3.0, 4.0, 5.0])
    assert t["mean"] == 3.0 and t["n"] == 5
    assert t["ci_low"] == pytest.approx(3.0 - 2.776445 * np.sqrt(2.5) / np.sqrt(5), rel=1e-5)
    assert t_interval([0.5])["ci_low"] is None
    flat = t_interval([0.4] * 5)
    assert flat["ci_low"] == flat["ci_high"] == pytest.approx(0.4)


def test_paired_bootstrap_of_identical_predictions_is_zero():
    g, p = label_matrix(IDS, GOLD), label_matrix(IDS, PRED)
    r = paired_bootstrap(g, p, p, draws=300)
    assert r["delta"] == 0 and r["ci_low"] == 0 and r["ci_high"] == 0 and r["p_two_sided"] == 1.0


def test_paired_bootstrap_sign_and_determinism():
    g, p = label_matrix(IDS, GOLD), label_matrix(IDS, PRED)
    r1 = paired_bootstrap(g, g, p, draws=500)
    r2 = paired_bootstrap(g, g, p, draws=500)
    assert r1 == r2
    assert r1["delta"] > 0 and r1["ci_low"] >= 0
    assert r1["draws"] == 500
