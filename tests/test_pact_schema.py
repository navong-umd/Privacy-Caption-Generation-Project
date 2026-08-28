"""Phase 8: PAcT label schema + validator."""
from __future__ import annotations

import pytest

from pplib.pact_schema import (
    HumanAnnotation,
    PACT_LABEL_SOURCES,
    PACT_REQUIRED_FIELDS,
    PACT_SCHEMA_VERSION,
    validate_label,
    weak_label_template,
)
from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS


def test_taxonomy_constants_match_plan():
    assert PRACTICE_LABELS == ["Processing", "Collecting", "Sharing", "Other"]
    assert PURPOSE_LABELS == ["Functionality", "Advertisement", "Analytics", "Other"]
    assert PACT_LABEL_SOURCES == ("weak", "human", "llm")
    assert PACT_SCHEMA_VERSION == "1.0.0"


def test_weak_label_template_validates():
    label = weak_label_template()
    label["practice"] = ["Collecting"]
    label["purpose"] = ["Functionality"]
    validate_label(label)   # must not raise


def test_human_annotation_dataclass_serializes():
    a = HumanAnnotation(
        prcs_id="prcs_abc123",
        practice=["Sharing"],
        purpose=["Advertisement"],
        annotator="ali",
        confidence=0.9,
        notes="cross-checked with SDK docs",
        timestamp="2026-08-28T01:00:00Z",
    )
    d = a.to_dict()
    assert d["label_source"] == "human"
    assert d["schema_version"] == PACT_SCHEMA_VERSION
    validate_label(d)


def test_llm_source_is_accepted():
    label = {
        "practice": ["Collecting"],
        "purpose": ["Analytics"],
        "label_source": "llm",
        "schema_version": PACT_SCHEMA_VERSION,
        "annotator": "gpt-4o",
        "confidence": 0.72,
        "notes": "two-pass agreement",
    }
    validate_label(label)


def test_validator_rejects_missing_required_fields():
    for missing in PACT_REQUIRED_FIELDS:
        label = weak_label_template()
        label.pop(missing)
        with pytest.raises(ValueError, match=missing):
            validate_label(label)


def test_validator_rejects_bad_label_source():
    label = weak_label_template()
    label["label_source"] = "wild-guess"
    with pytest.raises(ValueError, match="label_source"):
        validate_label(label)


def test_validator_rejects_non_canonical_practice_or_purpose():
    label = weak_label_template()
    label["practice"] = ["Snooping"]
    with pytest.raises(ValueError, match="non-canonical"):
        validate_label(label)

    label = weak_label_template()
    label["purpose"] = ["Marketing"]
    with pytest.raises(ValueError, match="non-canonical"):
        validate_label(label)


def test_validator_requires_weak_banner_on_weak_labels():
    label = weak_label_template()
    label["weak_banner"] = ""
    with pytest.raises(ValueError, match="weak_banner"):
        validate_label(label)


def test_validator_requires_annotator_and_confidence_on_human_labels():
    base = {
        "practice": ["Collecting"],
        "purpose": ["Functionality"],
        "label_source": "human",
        "schema_version": PACT_SCHEMA_VERSION,
    }
    # missing annotator
    with pytest.raises(ValueError, match="annotator"):
        validate_label({**base, "confidence": 0.9, "notes": ""})
    # bad confidence range
    with pytest.raises(ValueError, match="confidence"):
        validate_label({**base, "annotator": "ali", "confidence": 1.5, "notes": ""})


def test_weak_labeler_output_passes_validator():
    """End-to-end: WeakLabeler emits validator-clean output for a minimal PRCS."""
    from step2_dataset.weak_labeler import WeakLabeler
    labeler = WeakLabeler()
    stub_prcs = {
        "sink_type": "network",
        "involved_methods": ["com.google.ads.AdRequestHelper->flow"],
        "subgraph": {"nodes": []},
    }
    label = labeler.label(stub_prcs)
    validate_label(label)
    assert "Advertisement" in label["purpose"]
