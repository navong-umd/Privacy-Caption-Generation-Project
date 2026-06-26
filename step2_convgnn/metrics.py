"""
Purpose: Multi-label classification metrics for the two PAcT heads.
Input:   binary y_true / y_pred arrays [N, L] + label names.
Output:  dict of per-label P/R/F1, micro/macro F1, and subset (exact-match) accuracy.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
from sklearn.metrics import f1_score, precision_recall_fscore_support


def multilabel_metrics(y_true: np.ndarray, y_pred: np.ndarray,
                       labels: List[str], prefix: str) -> Dict[str, float]:
    """Per-label + micro/macro F1 + subset accuracy for one head."""
    out: Dict[str, float] = {}
    p, r, f, _ = precision_recall_fscore_support(
        y_true, y_pred, average=None, labels=range(len(labels)), zero_division=0)
    for i, name in enumerate(labels):
        out[f"{prefix}_{name}_P"] = float(p[i])
        out[f"{prefix}_{name}_R"] = float(r[i])
        out[f"{prefix}_{name}_F1"] = float(f[i])
    out[f"{prefix}_micro_f1"] = float(f1_score(y_true, y_pred, average="micro", zero_division=0))
    out[f"{prefix}_macro_f1"] = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    out[f"{prefix}_subset_acc"] = float((y_true == y_pred).all(axis=1).mean()) if len(y_true) else 0.0
    return out
