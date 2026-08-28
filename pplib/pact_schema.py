"""
Purpose: Versioned schema for PAcT (Practice + Purpose) labels attached to a PRCS (Phase 8).
Input:   none (constants + validator).
Output:  PACT_SCHEMA_VERSION, PACT_LABEL_SOURCES, PACT_REQUIRED_FIELDS,
         validate_label(dict), HumanAnnotation dataclass.

Enforces the plan's rule that every annotation must include practice + purpose +
evidence trail. Weak (heuristic) labels are the automated bootstrap: they carry
rationale + a WEAK banner but no annotator. Human and LLM-assisted annotations
carry annotator + confidence + notes; consumers can filter by label_source.

Keep in sync with research/PACT_SCHEMA.md.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS

PACT_SCHEMA_VERSION = "1.0.0"

# All accepted values of `label_source`. Any other value must be rejected by the validator.
PACT_LABEL_SOURCES = ("weak", "human", "llm")

# Fields every label block must contain, regardless of source.
PACT_REQUIRED_FIELDS = ("practice", "purpose", "label_source", "schema_version")

# Extra fields required when label_source in {"human", "llm"}.
PACT_ANNOTATION_FIELDS = ("annotator", "confidence", "notes")


@dataclass
class HumanAnnotation:
    """One human (or LLM-assisted) PAcT annotation for a single PRCS.

    Written into human_labels.json (keyed by prcs_id) and consumed by
    step2_dataset/build_dataset.py::_apply_labels.
    """

    prcs_id: str
    practice: List[str]
    purpose: List[str]
    annotator: str
    confidence: float          # 0.0 to 1.0
    notes: str = ""
    timestamp: str = ""        # ISO-8601, optional
    label_source: str = "human"
    schema_version: str = PACT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prcs_id": self.prcs_id,
            "practice": list(self.practice),
            "purpose": list(self.purpose),
            "annotator": self.annotator,
            "confidence": float(self.confidence),
            "notes": self.notes,
            "timestamp": self.timestamp,
            "label_source": self.label_source,
            "schema_version": self.schema_version,
        }


def validate_label(label: Dict[str, Any]) -> None:
    """Raise ValueError if `label` is not a well-formed PAcT label block.

    - practice / purpose must be lists whose members come from the canonical sets.
    - label_source must be one of PACT_LABEL_SOURCES.
    - schema_version must be present (any string; consumers may enforce equality).
    - When label_source is 'human' or 'llm', annotator + confidence + notes must be present,
      and confidence must be a float in [0.0, 1.0].
    - When label_source is 'weak', weak_banner must be present and non-empty; rationale is optional.
    """
    if not isinstance(label, dict):
        raise ValueError(f"label must be a dict, got {type(label).__name__}")

    missing = [f for f in PACT_REQUIRED_FIELDS if f not in label]
    if missing:
        raise ValueError(f"label missing required fields: {missing}")

    src = label["label_source"]
    if src not in PACT_LABEL_SOURCES:
        raise ValueError(f"label_source {src!r} not in {PACT_LABEL_SOURCES}")

    for field_name, canonical in (("practice", PRACTICE_LABELS), ("purpose", PURPOSE_LABELS)):
        values = label[field_name]
        if not isinstance(values, list):
            raise ValueError(f"{field_name} must be a list, got {type(values).__name__}")
        bad = [v for v in values if v not in canonical]
        if bad:
            raise ValueError(f"{field_name} has non-canonical values: {bad}")

    if src == "weak":
        banner = label.get("weak_banner", "")
        if not banner:
            raise ValueError("weak label must carry a non-empty weak_banner")
    else:  # human or llm
        for f in PACT_ANNOTATION_FIELDS:
            if f not in label:
                raise ValueError(f"{src} label missing {f!r}")
        c = label["confidence"]
        if not isinstance(c, (int, float)) or not (0.0 <= float(c) <= 1.0):
            raise ValueError(f"confidence must be a float in [0,1], got {c!r}")


def weak_label_template() -> Dict[str, Any]:
    """Zero-argument default useful for tests / stubs. Consumers should use WeakLabeler instead."""
    return {
        "practice": [],
        "purpose": [],
        "label_source": "weak",
        "weak_banner": BANNER_WEAK,
        "rationale": "",
        "schema_version": PACT_SCHEMA_VERSION,
    }
