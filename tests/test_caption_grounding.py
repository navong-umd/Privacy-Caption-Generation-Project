"""Phase 13: post-hoc caption grounding verifier."""
from __future__ import annotations

import pytest

from step3_caption.grounding import (
    GroundingReport,
    batch_check,
    check_grounding,
)


BASE_EVIDENCE = {
    "category": "LOCATION_INFORMATION",
    "pi_type": "user's coarse location",
    "practice": ["Collecting", "Sharing"],
    "purpose":  ["Functionality"],
    "sink_type": "network",
    "sink_api":  "java.net.URL->openConnection",
    "source_api": "android.location.LocationManager->getLastKnownLocation",
    "app_package": "com.example.locate",
}


def test_grounded_caption_passes():
    caption = "The app reads your location and sends it to a remote server over the network."
    r = check_grounding(caption, BASE_EVIDENCE)
    assert isinstance(r, GroundingReport)
    assert r.mentions_pi
    assert r.mentions_sink
    assert not r.contains_forbidden_recipient
    assert r.passes


def test_caption_missing_pi_fails():
    caption = "The app writes some information over the network to a server."
    r = check_grounding(caption, BASE_EVIDENCE)
    assert not r.mentions_pi
    assert not r.passes
    assert any("PI category" in n for n in r.notes)


def test_caption_missing_sink_fails():
    caption = "The app reads your location."
    r = check_grounding(caption, BASE_EVIDENCE)
    assert r.mentions_pi
    assert not r.mentions_sink
    assert not r.passes


def test_pi_type_synonym_counts():
    """The natural-language pi_type text should count as PI mention."""
    ev = {**BASE_EVIDENCE, "category": ""}
    caption = "The app reads user's coarse location and logs it."
    r = check_grounding(caption, {**ev, "sink_type": "logging"})
    assert r.mentions_pi


def test_sink_alias_via_sink_api_last_token():
    """If a caption names the sink method (e.g. openConnection) it counts as a sink mention."""
    ev = {**BASE_EVIDENCE, "sink_type": ""}
    caption = "The app reads your location and calls openConnection to send it."
    r = check_grounding(caption, ev)
    assert r.mentions_sink


def test_forbidden_vendor_hallucination_flagged():
    """A caption inventing a vendor absent from the evidence must be flagged."""
    ev = {**BASE_EVIDENCE}
    caption = "The app sends your location to AdMob over the network for ads."
    r = check_grounding(caption, ev)
    # AdMob is not in the evidence: forbidden_vendor heuristic must fire.
    assert r.contains_forbidden_recipient
    assert not r.passes


def test_vendor_in_evidence_is_allowed():
    ev = {**BASE_EVIDENCE, "sink_api": "com.google.admob.Reporter->send"}
    caption = "The app sends your location to admob over the network."
    r = check_grounding(caption, ev)
    assert not r.contains_forbidden_recipient
    # network sink present + location PI present
    assert r.passes


def test_batch_check_shape_and_pass_rate():
    caption_a = "The app reads location and sends it over the network."
    caption_b = "The app does something."
    records = [
        {"prcs_id": "prcs_1", **BASE_EVIDENCE, "labels": {"practice": [], "purpose": []}},
        {"prcs_id": "prcs_2", **BASE_EVIDENCE, "labels": {"practice": [], "purpose": []}},
    ]
    captions = [
        {"prcs_id": "prcs_1", "caption": caption_a},
        {"prcs_id": "prcs_2", "caption": caption_b},
    ]
    # Massage the ADPPG-style records so _evidence(rec) recovers the same fields.
    for r in records:
        r["pi_category"] = r["category"]
        r["pi_type"] = BASE_EVIDENCE["pi_type"]
        r["sink_type"] = BASE_EVIDENCE["sink_type"]
        r["sink_api"] = BASE_EVIDENCE["sink_api"]
        r["source_api"] = BASE_EVIDENCE["source_api"]
    summary = batch_check(captions, records)
    assert summary["n"] == 2
    assert summary["passed"] == 1
    assert summary["pass_rate"] == 0.5


def test_empty_caption_fails_cleanly():
    r = check_grounding("", BASE_EVIDENCE)
    assert not r.passes
    assert not r.mentions_pi
    assert not r.mentions_sink
