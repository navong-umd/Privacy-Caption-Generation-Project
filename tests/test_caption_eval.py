"""Phase 15: automated caption-eval aggregator on the synthetic fixture."""
from __future__ import annotations

import pytest

from step4_eval.aggregate import NO_REFS_MESSAGE, aggregate


RECORDS = [
    {
        "prcs_id": "prcs_1",
        "app_package": "com.example.locate",
        "pi_category": "LOCATION_INFORMATION",
        "pi_type": "user's coarse location",
        "sink_type": "network",
        "sink_api":  "java.net.URL->openConnection",
        "source_api": "android.location.LocationManager->getLastKnownLocation",
        "privacy_threat": "Data Disclosure",
        "labels": {"practice": ["Collecting", "Sharing"], "purpose": ["Functionality"],
                   "label_source": "weak"},
    },
    {
        "prcs_id": "prcs_2",
        "app_package": "com.example.locate",
        "pi_category": "UNIQUE_IDENTIFIER",
        "pi_type": "device identifier",
        "sink_type": "logging",
        "sink_api":  "android.util.Log->i",
        "source_api": "android.telephony.TelephonyManager->getDeviceId",
        "privacy_threat": "Detecting",
        "labels": {"practice": ["Collecting"], "purpose": ["Analytics"],
                   "label_source": "weak"},
    },
]


def _cap(pid, text, label_source="weak"):
    return {"prcs_id": pid, "caption": text, "label_source": label_source}


def test_no_references_reports_the_honest_status():
    caps = [_cap("prcs_1", "reads location and sends over the network"),
            _cap("prcs_2", "reads device id and logs it")]
    report = aggregate(caps, RECORDS)
    assert report["summary"]["text_metrics"]["status"] == NO_REFS_MESSAGE
    assert report["summary"]["text_metrics"]["n_scored"] == 0
    # But grounding still runs and reports coverage.
    assert report["summary"]["grounding"]["total"] == 2
    assert report["summary"]["grounding"]["passed"] == 2


def test_references_produce_bleu_and_rouge_means():
    caps = [_cap("prcs_1", "reads location and sends it over the network"),
            _cap("prcs_2", "reads device id and logs it")]
    refs = {
        "prcs_1": "the app reads location and sends it over the network",
        "prcs_2": "the app reads device id and logs it",
    }
    report = aggregate(caps, RECORDS, references=refs)
    ts = report["summary"]["text_metrics"]
    assert ts["n_scored"] == 2
    assert 0.0 <= ts["bleu4_mean"] <= 1.0
    assert 0.0 <= ts["rouge_l_mean"] <= 1.0


def test_grounding_pass_rate_matches_content():
    caps = [_cap("prcs_1", "reads location and sends over the network"),  # passes
            _cap("prcs_2", "the app does something bad")]                  # fails both axes
    report = aggregate(caps, RECORDS)
    grounding = report["summary"]["grounding"]
    assert grounding["total"] == 2
    assert grounding["passed"] == 1
    assert grounding["pass_rate"] == 0.5


def test_judge_summary_averages_scores_when_provided():
    caps = [_cap("prcs_1", "any"), _cap("prcs_2", "any")]
    judge_rows = [{"prcs_id": "prcs_1", "score": 0.9, "verdict": "good"},
                  {"prcs_id": "prcs_2", "score": 0.5, "verdict": "meh"}]
    report = aggregate(caps, RECORDS, judge_rows=judge_rows)
    assert report["summary"]["judge"]["n"] == 2
    assert abs(report["summary"]["judge"]["mean"] - 0.7) < 1e-9


def test_judge_summary_reports_missing_rows():
    report = aggregate([_cap("prcs_1", "x")], RECORDS)
    assert report["summary"]["judge"]["status"] == "no judge rows"


def test_per_caption_rows_have_expected_shape():
    caps = [_cap("prcs_1", "reads location and sends over the network")]
    report = aggregate(caps, RECORDS,
                       references={"prcs_1": "reads location and sends over the network"},
                       judge_rows=[{"prcs_id": "prcs_1", "score": 0.8}])
    row = report["per_caption"][0]
    assert row["prcs_id"] == "prcs_1"
    assert row["caption"].startswith("reads location")
    assert row["text_metrics"]["bleu4"] is not None
    assert row["grounding"] is not None
    assert row["grounding"]["passes"] is True
    assert row["judge"]["score"] == 0.8


def test_summary_marks_human_eval_deferred():
    report = aggregate([_cap("prcs_1", "x")], RECORDS)
    assert report["summary"]["human_eval_deferred"] is True


def test_records_without_matching_caption_are_ignored():
    """Aggregator iterates captions; extra records do no harm."""
    caps = [_cap("prcs_1", "reads location and sends over the network")]
    report = aggregate(caps, RECORDS)
    assert report["summary"]["n_captions"] == 1
    assert report["summary"]["grounding"]["total"] == 1
