"""
Purpose: Error taxonomy + ErrorRecord schema for post-hoc analysis (Phase 16).
Input:   none (constants + dataclass + validator).
Output:  ERROR_CATEGORIES, ERROR_STAGES, ErrorRecord dataclass, validate_error_record.

The plan asks for error records that carry input, prediction, ground truth, evidence,
and analysis. This module pins the taxonomy so every consumer that logs an error uses
the same category names, and every downstream summary can group by them.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

ERROR_TAXONOMY_VERSION = "1.0.0"

# Every distinct failure mode named in the plan. Consumers must use these exact strings.
ERROR_CATEGORIES: tuple[str, ...] = (
    "incorrect_source",              # PPG marked something a Source that is not one
    "incorrect_sink",                # PPG marked something a Sink that is not one
    "missing_flow",                  # Real source-to-sink flow was not found by taint
    "incorrect_path",                # Path found but wrong / spurious hops
    "incorrect_pi_type",             # PI type on the Source is wrong
    "incorrect_practice",            # Practice head prediction wrong
    "incorrect_purpose",             # Purpose head prediction wrong
    "insufficient_context",          # PRCS subgraph too small for a correct caption
    "hallucinated_information",      # Caption invented a data type / recipient / purpose
    "incomplete_caption",            # Caption missed an axis (PI or sink) it should have covered
    "generic_caption",               # Caption is technically correct but useless
)

# Which pipeline stage produced the error. Helps route fixes.
ERROR_STAGES: tuple[str, ...] = (
    "static_analysis",   # adapters/run_apg_csv
    "knowledge_base",    # pplib/knowledge, stage4_ppg/catalogs
    "ppg",               # stage4_ppg/build_ppg
    "traversal",         # stage4_ppg/taint
    "prcs",              # step2_prcs/extract_prcs
    "labeling",          # step2_dataset (weak or human)
    "classifier",        # step2_convgnn
    "caption",           # step3_caption
    "policy",            # step3_policy
    "evaluation",        # step4_eval
)

_REQUIRED_FIELDS = ("error_id", "category", "stage", "input", "prediction",
                    "ground_truth", "evidence", "analysis", "schema_version")


@dataclass
class ErrorRecord:
    """One structured error case.

    input:         the record that produced the error (e.g. PRCS id + code snippet)
    prediction:    what the pipeline emitted
    ground_truth:  the correct answer, when known
    evidence:      the KB / PPG / PRCS facts that should have driven the prediction
    analysis:      short human note explaining the root cause
    """

    error_id: str
    category: str
    stage: str
    input: Dict[str, Any]
    prediction: Any
    ground_truth: Any
    evidence: Dict[str, Any]
    analysis: str
    tags: List[str] = field(default_factory=list)
    schema_version: str = ERROR_TAXONOMY_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_error_record(record: Dict[str, Any]) -> None:
    """Raise ValueError if `record` is not a well-formed error record."""
    if not isinstance(record, dict):
        raise ValueError(f"error record must be a dict, got {type(record).__name__}")
    missing = [f for f in _REQUIRED_FIELDS if f not in record]
    if missing:
        raise ValueError(f"error record missing fields: {missing}")
    if record["category"] not in ERROR_CATEGORIES:
        raise ValueError(f"unknown category {record['category']!r}")
    if record["stage"] not in ERROR_STAGES:
        raise ValueError(f"unknown stage {record['stage']!r}")
    if not isinstance(record["analysis"], str) or not record["analysis"].strip():
        raise ValueError("analysis must be a non-empty string")
    if not isinstance(record["evidence"], dict):
        raise ValueError("evidence must be a dict")


def summarize(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Group a list of error records by category and by stage.

    Silently skips malformed rows (records that fail validate_error_record).
    Returns totals + per-category counts + per-stage counts + fraction shares.
    """
    ok: List[Dict[str, Any]] = []
    for r in records:
        try:
            validate_error_record(r)
            ok.append(r)
        except ValueError:
            continue

    by_category: Dict[str, int] = {c: 0 for c in ERROR_CATEGORIES}
    by_stage: Dict[str, int] = {s: 0 for s in ERROR_STAGES}
    for r in ok:
        by_category[r["category"]] += 1
        by_stage[r["stage"]] += 1
    total = len(ok)
    return {
        "total": total,
        "by_category": by_category,
        "by_stage": by_stage,
        "category_share": {c: (n / total if total else 0.0) for c, n in by_category.items()},
        "stage_share": {s: (n / total if total else 0.0) for s, n in by_stage.items()},
    }
