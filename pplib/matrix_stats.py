"""
Purpose: Statistics for the experiment matrix: per-item scoring at a fixed threshold, a 95%
         t-interval over seeds, and item bootstraps (one arm, or two arms paired on the same draws).
Input:   gold labels and predicted labels keyed by prcs_id ({"practice": [...], "purpose": [...]}).
Output:  plain dicts ready to go into an ExperimentRun manifest.

Macro-F1 matches step2_convgnn.metrics (sklearn, zero_division=0): a label with no gold and no
predicted positives scores 0 and still counts in the macro average, so a label without positives
in a split never crashes a run. Its support is reported next to the scores so readers can see it.
"""
from __future__ import annotations

import math
from typing import Dict, List, Mapping, Sequence, Tuple

import numpy as np

from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
from step2_convgnn.metrics import multilabel_metrics

HEADS: Tuple[Tuple[str, List[str]], ...] = (("practice", PRACTICE_LABELS), ("purpose", PURPOSE_LABELS))
SUMMARY_KEYS = ("macro_f1", "practice_macro_f1", "purpose_macro_f1",
                "practice_micro_f1", "purpose_micro_f1")


def label_matrix(ids: Sequence[str], labels: Mapping[str, Mapping]) -> Dict[str, np.ndarray]:
    """{head: [n, L] 0/1 array} for the given ids, in order."""
    return {head: np.array([[int(l in labels[i].get(head, [])) for l in names] for i in ids],
                           dtype=int).reshape(len(ids), len(names))
            for head, names in HEADS}


def score(gold: Dict[str, np.ndarray], pred: Dict[str, np.ndarray]) -> Dict[str, float]:
    """Same metric dict train() returns: per-label P/R/F1, micro/macro per head, overall macro_f1."""
    m: Dict[str, float] = {}
    for head, names in HEADS:
        m.update(multilabel_metrics(gold[head], pred[head], names, head))
    m["macro_f1"] = (m["practice_macro_f1"] + m["purpose_macro_f1"]) / 2
    return m


def label_support(gold: Dict[str, np.ndarray]) -> Dict[str, int]:
    return {f"{head}_{l}": int(gold[head][:, j].sum())
            for head, names in HEADS for j, l in enumerate(names)}


def t_interval(values: Sequence[float], confidence: float = 0.95) -> Dict[str, float]:
    """Mean and two-sided t-interval; the interval is null when fewer than two values exist."""
    from scipy import stats

    x = np.asarray(values, dtype=float)
    out = {"mean": float(x.mean()) if len(x) else float("nan"), "n": int(len(x))}
    if len(x) < 2:
        return {**out, "std": None, "ci_low": None, "ci_high": None}
    sd = float(x.std(ddof=1))
    half = float(stats.t.ppf(0.5 + confidence / 2, len(x) - 1)) * sd / math.sqrt(len(x))
    return {**out, "std": sd, "ci_low": out["mean"] - half, "ci_high": out["mean"] + half}


def _macro_f1_draws(gold: Dict[str, np.ndarray], pred: Dict[str, np.ndarray],
                    idx: np.ndarray) -> Dict[str, np.ndarray]:
    """Per-draw macro-F1 for every row of resample indices idx [B, n] (vectorized)."""
    out = {}
    for head, _ in HEADS:
        g, p = gold[head][idx].astype(bool), pred[head][idx].astype(bool)      # [B, n, L]
        tp = (g & p).sum(axis=1)
        fp = (~g & p).sum(axis=1)
        fn = (g & ~p).sum(axis=1)
        denom = 2 * tp + fp + fn
        f1 = np.divide(2 * tp, denom, out=np.zeros(denom.shape, dtype=float), where=denom > 0)
        out[f"{head}_macro_f1"] = f1.mean(axis=1)
    out["macro_f1"] = (out["practice_macro_f1"] + out["purpose_macro_f1"]) / 2
    return out


def _draws(n: int, draws: int, seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, n, size=(draws, n))


def _percentile(x: np.ndarray, confidence: float) -> Tuple[float, float]:
    a = (1 - confidence) / 2
    return float(np.quantile(x, a)), float(np.quantile(x, 1 - a))


def bootstrap_interval(gold: Dict[str, np.ndarray], pred: Dict[str, np.ndarray],
                       draws: int = 2000, seed: int = 0,
                       confidence: float = 0.95) -> Dict[str, Dict[str, float]]:
    """Percentile item-bootstrap interval of the macro-F1 scores of one prediction set."""
    n = len(gold["practice"])
    if n == 0:
        raise ValueError("bootstrap needs at least one test item")
    point = score(gold, pred)
    dist = _macro_f1_draws(gold, pred, _draws(n, draws, seed))
    out = {}
    for k, v in dist.items():
        lo, hi = _percentile(v, confidence)
        out[k] = {"estimate": point[k], "ci_low": lo, "ci_high": hi}
    return {"draws": draws, "seed": seed, "confidence": confidence, "metrics": out}


def paired_bootstrap(gold: Dict[str, np.ndarray], pred: Dict[str, np.ndarray],
                     ref: Dict[str, np.ndarray], draws: int = 2000, seed: int = 0,
                     confidence: float = 0.95) -> Dict:
    """Macro-F1 of `pred` minus `ref` on the same resampled items, with a percentile interval and
    a two-sided bootstrap p-value (share of draws on the far side of zero, doubled)."""
    n = len(gold["practice"])
    if n == 0:
        raise ValueError("bootstrap needs at least one test item")
    idx = _draws(n, draws, seed)
    a, b = _macro_f1_draws(gold, pred, idx), _macro_f1_draws(gold, ref, idx)
    observed = score(gold, pred)["macro_f1"] - score(gold, ref)["macro_f1"]
    d = a["macro_f1"] - b["macro_f1"]
    lo, hi = _percentile(d, confidence)
    p = min(1.0, 2 * min(float((d <= 0).mean()), float((d >= 0).mean())))
    return {"metric": "macro_f1", "delta": observed, "ci_low": lo, "ci_high": hi,
            "p_two_sided": p, "draws": draws, "seed": seed, "confidence": confidence}
