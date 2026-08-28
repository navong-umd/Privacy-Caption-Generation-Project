"""
Purpose: Classification BASELINES for PAcT (Practice + Purpose) prediction on a PRCS.
Input:   PRCS records (labeled for training; unlabeled for prediction).
Output:  Predicted practice + purpose label lists per PRCS.

Two baselines live here. The third baseline (Code2Seq) is in code2seq_baseline.py
as an explicit UNTRAINED placeholder for captions, not classification; it will be
replaced when we have real (PRCS -> caption) pairs.

    RuleBaseline    - wraps step2_dataset.weak_labeler.WeakLabeler
    TfIdfBaseline   - TF-IDF over code_snippet + one-vs-rest logistic regression

Kept dependency-light: sklearn only. No torch.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence

from pplib.pact_schema import PACT_SCHEMA_VERSION
from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS


BASELINE_NAMES = ("rule", "tfidf")


@dataclass
class BaselinePrediction:
    """A prediction from a baseline for one PRCS."""

    prcs_id: str
    practice: List[str]
    purpose: List[str]
    baseline: str
    schema_version: str = PACT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prcs_id": self.prcs_id,
            "practice": list(self.practice),
            "purpose": list(self.purpose),
            "baseline": self.baseline,
            "schema_version": self.schema_version,
        }


# ---------------------------------------------------------------------------
# Rule-based baseline
# ---------------------------------------------------------------------------

class RuleBaseline:
    """Rule-based classifier: sink_type + third-party SDK class match.

    Delegates to the WeakLabeler that already implements the same rule set
    (see configs/weak_labels.yaml + configs/sdk_catalog.yaml + docs/PACT_SCHEMA.md).
    Kept as a thin wrapper so callers can reason about baselines uniformly.
    """

    name = "rule"

    def __init__(self):
        from step2_dataset.weak_labeler import WeakLabeler
        self._labeler = WeakLabeler()

    def fit(self, _records: Iterable[Dict]) -> "RuleBaseline":
        return self                                  # rule baseline has no training

    def predict_one(self, prcs: Dict) -> BaselinePrediction:
        lab = self._labeler.label(prcs)
        return BaselinePrediction(
            prcs_id=prcs.get("prcs_id", ""),
            practice=lab["practice"],
            purpose=lab["purpose"],
            baseline=self.name,
        )

    def predict(self, records: Sequence[Dict]) -> List[BaselinePrediction]:
        return [self.predict_one(r) for r in records]


# ---------------------------------------------------------------------------
# Traditional-ML baseline: TF-IDF on the code snippet + OneVsRest LogReg
# ---------------------------------------------------------------------------

class TfIdfBaseline:
    """TF-IDF over the rendered code_snippet + logistic regression, one head per label.

    Trains two separate multi-label heads (practice + purpose) as
    OneVsRestClassifier(LogisticRegression). Text features come from the code
    snippet only; the graph structure is deliberately ignored so this is a
    proper text-only baseline for the graph vs code ablation in Phase 21.
    """

    name = "tfidf"

    def __init__(self, max_features: int = 5000):
        self.max_features = max_features
        self._vectorizer = None
        self._practice_head = None
        self._purpose_head = None
        self._is_fit = False

    @staticmethod
    def _text(prcs: Dict) -> str:
        # Snippet plus the two API strings so a callee alone is a signal.
        return " ".join([
            prcs.get("code_snippet", ""),
            prcs.get("source_api", ""),
            prcs.get("sink_api", ""),
        ])

    @staticmethod
    def _y_matrix(records: Sequence[Dict], head: str) -> List[List[int]]:
        labels = PRACTICE_LABELS if head == "practice" else PURPOSE_LABELS
        out = []
        for r in records:
            active = r.get("labels", {}).get(head, [])
            out.append([1 if lbl in active else 0 for lbl in labels])
        return out

    def fit(self, records: Sequence[Dict]) -> "TfIdfBaseline":
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.multiclass import OneVsRestClassifier

        if not records:
            raise ValueError("TfIdfBaseline requires at least one training record")

        X_text = [self._text(r) for r in records]
        self._vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            token_pattern=r"[A-Za-z_][A-Za-z0-9_]+",
            lowercase=True,
        )
        X = self._vectorizer.fit_transform(X_text)

        y_practice = self._y_matrix(records, "practice")
        y_purpose = self._y_matrix(records, "purpose")

        def _fit_head(y):
            # LogisticRegression with saga solver handles small n and multi-label well.
            base = LogisticRegression(max_iter=200, solver="liblinear")
            head = OneVsRestClassifier(base)
            head.fit(X, y)
            return head

        self._practice_head = _fit_head(y_practice)
        self._purpose_head = _fit_head(y_purpose)
        self._is_fit = True
        return self

    def _decode(self, row, labels: Sequence[str]) -> List[str]:
        return [lbl for i, lbl in enumerate(labels) if row[i] == 1]

    def predict_one(self, prcs: Dict) -> BaselinePrediction:
        if not self._is_fit:
            raise RuntimeError("TfIdfBaseline.predict_one called before fit()")
        X = self._vectorizer.transform([self._text(prcs)])
        p_row = self._practice_head.predict(X)[0]
        u_row = self._purpose_head.predict(X)[0]
        return BaselinePrediction(
            prcs_id=prcs.get("prcs_id", ""),
            practice=self._decode(p_row, PRACTICE_LABELS),
            purpose=self._decode(u_row, PURPOSE_LABELS),
            baseline=self.name,
        )

    def predict(self, records: Sequence[Dict]) -> List[BaselinePrediction]:
        return [self.predict_one(r) for r in records]


# ---------------------------------------------------------------------------
# Metrics helpers (multi-label): precision / recall / F1 per head, micro + macro.
# ---------------------------------------------------------------------------

def multilabel_metrics(preds: Sequence[BaselinePrediction],
                       records: Sequence[Dict]) -> Dict[str, Dict[str, float]]:
    """Compute precision / recall / F1 (micro + macro) for practice and purpose heads.

    Returns {"practice": {micro_f1, macro_f1, ...}, "purpose": {...}}.
    """
    from sklearn.metrics import precision_recall_fscore_support

    id_to_true = {r["prcs_id"]: r.get("labels", {}) for r in records}
    y_true_p: List[List[int]] = []
    y_pred_p: List[List[int]] = []
    y_true_u: List[List[int]] = []
    y_pred_u: List[List[int]] = []
    for p in preds:
        true = id_to_true.get(p.prcs_id, {})
        y_true_p.append([1 if l in true.get("practice", []) else 0 for l in PRACTICE_LABELS])
        y_pred_p.append([1 if l in p.practice else 0 for l in PRACTICE_LABELS])
        y_true_u.append([1 if l in true.get("purpose", []) else 0 for l in PURPOSE_LABELS])
        y_pred_u.append([1 if l in p.purpose else 0 for l in PURPOSE_LABELS])

    def _score(y_true, y_pred):
        micro = precision_recall_fscore_support(
            y_true, y_pred, average="micro", zero_division=0)
        macro = precision_recall_fscore_support(
            y_true, y_pred, average="macro", zero_division=0)
        return {
            "precision_micro": float(micro[0]), "recall_micro": float(micro[1]),
            "f1_micro": float(micro[2]),
            "precision_macro": float(macro[0]), "recall_macro": float(macro[1]),
            "f1_macro": float(macro[2]),
        }

    return {
        "practice": _score(y_true_p, y_pred_p),
        "purpose": _score(y_true_u, y_pred_u),
        "banner": BANNER_WEAK,   # weak labels flow through; downstream must surface this
    }
