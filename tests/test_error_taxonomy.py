"""Phase 16: error taxonomy + ErrorRecord + validator + summarize."""
from __future__ import annotations

import pytest

from pplib.error_taxonomy import (
    ERROR_CATEGORIES,
    ERROR_STAGES,
    ERROR_TAXONOMY_VERSION,
    ErrorRecord,
    summarize,
    validate_error_record,
)


def _valid_record(category="incorrect_pi_type", stage="knowledge_base") -> dict:
    return {
        "error_id": "err_001",
        "category": category,
        "stage": stage,
        "input": {"prcs_id": "prcs_abc"},
        "prediction": {"pi_category": "UNIQUE_IDENTIFIER"},
        "ground_truth": {"pi_category": "LOCATION_INFORMATION"},
        "evidence": {"callee": "android.location.LocationManager->getLastKnownLocation"},
        "analysis": "SuSi match hit the wrong signature; curated allowlist would fix it.",
        "tags": ["susi-noise"],
        "schema_version": ERROR_TAXONOMY_VERSION,
    }


def test_taxonomy_matches_the_plan():
    assert "incorrect_source" in ERROR_CATEGORIES
    assert "incorrect_sink" in ERROR_CATEGORIES
    assert "missing_flow" in ERROR_CATEGORIES
    assert "incorrect_path" in ERROR_CATEGORIES
    assert "incorrect_pi_type" in ERROR_CATEGORIES
    assert "incorrect_practice" in ERROR_CATEGORIES
    assert "incorrect_purpose" in ERROR_CATEGORIES
    assert "insufficient_context" in ERROR_CATEGORIES
    assert "hallucinated_information" in ERROR_CATEGORIES
    assert "incomplete_caption" in ERROR_CATEGORIES
    assert "generic_caption" in ERROR_CATEGORIES
    assert ERROR_TAXONOMY_VERSION == "1.0.0"


def test_error_record_dataclass_serializes():
    er = ErrorRecord(
        error_id="err_002",
        category="incorrect_sink",
        stage="ppg",
        input={"prcs_id": "prcs_x"},
        prediction={"sink_type": "network"},
        ground_truth={"sink_type": "storage"},
        evidence={"callee": "com.example.DB->put"},
        analysis="regex rule too broad; matched storage as network.",
    )
    d = er.to_dict()
    assert d["schema_version"] == ERROR_TAXONOMY_VERSION
    validate_error_record(d)


def test_validator_accepts_valid_record():
    validate_error_record(_valid_record())


def test_validator_rejects_bad_category():
    r = _valid_record()
    r["category"] = "totally_made_up"
    with pytest.raises(ValueError, match="category"):
        validate_error_record(r)


def test_validator_rejects_bad_stage():
    r = _valid_record()
    r["stage"] = "not_a_stage"
    with pytest.raises(ValueError, match="stage"):
        validate_error_record(r)


def test_validator_rejects_empty_analysis():
    r = _valid_record()
    r["analysis"] = "   "
    with pytest.raises(ValueError, match="analysis"):
        validate_error_record(r)


def test_validator_rejects_missing_required_field():
    r = _valid_record()
    r.pop("evidence")
    with pytest.raises(ValueError, match="evidence"):
        validate_error_record(r)


def test_summarize_counts_categories_and_stages():
    records = [
        _valid_record(category="incorrect_pi_type", stage="knowledge_base"),
        _valid_record(category="incorrect_pi_type", stage="knowledge_base"),
        _valid_record(category="hallucinated_information", stage="caption"),
        {"bogus": True},                                                   # dropped
    ]
    s = summarize(records)
    assert s["total"] == 3
    assert s["by_category"]["incorrect_pi_type"] == 2
    assert s["by_category"]["hallucinated_information"] == 1
    assert s["by_stage"]["knowledge_base"] == 2
    assert s["by_stage"]["caption"] == 1
    assert abs(s["category_share"]["incorrect_pi_type"] - 2/3) < 1e-9


def test_summarize_empty_returns_zero_shares():
    s = summarize([])
    assert s["total"] == 0
    assert all(v == 0 for v in s["by_category"].values())
    assert all(v == 0.0 for v in s["category_share"].values())
