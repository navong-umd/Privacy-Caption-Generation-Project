"""Phase 4 unified knowledge-base lookup tests.

Exercises pplib.knowledge.KnowledgeBase against the real configs/ppg.yaml,
configs/sinks.yaml, configs/sdk_catalog.yaml, and the data/knowledge_base/ CSVs.

The knowledge base is the single source of truth every downstream consumer must
share for API classification. These tests guarantee:
  - a curated Tier-1 source resolves with tier='known' + a full provenance string
  - a SuSi Tier-2 source resolves with tier='susi'
  - permission maps are wired end-to-end
  - a documented sink resolves with is_sink=True + sink_type
  - the egress-verb heuristic only fires for external callees, never internal
  - an ad SDK package prefix is tagged advertisement, analytics tagged analytics
  - an unknown callee returns is_source=False and is_sink=False (no invention)
"""
from __future__ import annotations

import pytest

from pplib.knowledge import KnowledgeBase, KnowledgeHit


@pytest.fixture(scope="module")
def kb() -> KnowledgeBase:
    return KnowledgeBase()


def test_stats_are_nontrivial(kb):
    s = kb.stats()
    # Sanity: catalog was actually loaded. SuSi ships 17,801 rows in the CSV but many
    # collide on the same class->method key after dedup + exclude_categories filtering;
    # ~6,000 distinct signatures survive load.
    assert s["curated_sources"] >= 10        # 16 in configs/ppg.yaml at time of writing
    assert s["susi_sources"] > 5_000         # dedup'd SuSi load, minus exclude_categories
    assert s["sink_rules"] >= 20             # configs/sinks.yaml at time of writing
    assert s["sdk_prefixes"] > 50            # advertisement + analytics + functionality_hint


def test_curated_source_has_full_provenance(kb):
    # LocationManager.getLastKnownLocation is in configs/ppg.yaml::known_sources.
    hit = kb.lookup("android.location.LocationManager->getLastKnownLocation")
    assert hit.is_source is True
    assert hit.pi_category == "LOCATION_INFORMATION"
    assert hit.permission == "ACCESS_FINE_LOCATION"     # from permission_map
    assert hit.source_tier == "known"
    assert "known_sources" in hit.source_provenance     # provenance string is populated


def test_curated_source_permission_wiring(kb):
    hit = kb.lookup("android.telephony.TelephonyManager->getDeviceId")
    assert hit.is_source is True
    assert hit.pi_category == "UNIQUE_IDENTIFIER"
    assert hit.permission == "READ_PHONE_STATE"
    assert hit.source_tier == "known"


def test_susi_source_falls_back_to_tier_2(kb):
    # A SuSi signature that is NOT in known_sources (framework-internal path).
    # com.android.internal.telephony.cdma.CDMAPhone->getDeviceId ships in SuSi as UNIQUE_IDENTIFIER.
    hit = kb.lookup("com.android.internal.telephony.cdma.CDMAPhone->getDeviceId")
    assert hit.is_source is True
    assert hit.pi_category == "UNIQUE_IDENTIFIER"
    assert hit.source_tier == "susi"
    assert "SuSi" in hit.source_provenance


def test_documented_sink(kb):
    # Log is in configs/sinks.yaml (regex ^android\.util\.Log->).
    hit = kb.lookup("android.util.Log->i")
    assert hit.is_sink is True
    assert hit.sink_type == "logging"
    assert hit.sink_known is True


def test_heuristic_sink_fires_only_on_external_callees(kb):
    # 'sendLog' contains an egress verb ('send' / 'log') — external → heuristic sink.
    external = kb.lookup("com.example.tracker.Reporter->sendLog", is_internal=False)
    assert external.is_sink is True
    assert external.sink_type == "heuristic_unknown"
    assert external.sink_known is False

    # Same callee but marked internal — heuristic must NOT fire.
    internal = kb.lookup("com.example.tracker.Reporter->sendLog", is_internal=True)
    assert internal.is_sink is False


def test_unknown_callee_returns_empty_hit(kb):
    """The plan's rule: 'Never silently invent the meaning of an Android API.'"""
    hit = kb.lookup("com.example.totally.unknown.ClassXYZ->someRandomMethod")
    assert hit.is_source is False
    assert hit.is_sink is False
    assert hit.pi_category == ""
    assert hit.permission == ""
    assert hit.source_tier == ""
    assert hit.sdk_purpose == ""


def test_malformed_callee_is_safe(kb):
    for bad in ("", "no-arrow-here", "->orphan"):
        hit = kb.lookup(bad)
        assert isinstance(hit, KnowledgeHit)
        assert hit.is_source is False
        assert hit.is_sink is False


def test_ad_sdk_prefix_tagged_advertisement(kb):
    hit = kb.lookup("com.google.ads.AdRequestHelper0->flow0")
    assert hit.sdk_purpose == "advertisement"


def test_analytics_sdk_prefix_tagged_analytics(kb):
    hit = kb.lookup("com.appsflyer.Sender0->send5")
    assert hit.sdk_purpose == "analytics"


def test_functionality_hint_prefix(kb):
    # android.* is in functionality_hint -> purpose='functionality'.
    hit = kb.lookup("android.location.LocationManager->getLastKnownLocation")
    assert hit.sdk_purpose == "functionality"


def test_longest_prefix_wins(kb):
    """Ensure com.google.android.gms.analytics beats a shorter com.google.* prefix."""
    hit = kb.lookup("com.google.android.gms.analytics.Tracker->send")
    assert hit.sdk_purpose == "analytics"


def test_to_dict_serializable(kb):
    """The KnowledgeHit is a dataclass — asdict must produce a plain JSON-serializable dict."""
    import json
    hit = kb.lookup("android.location.LocationManager->getLastKnownLocation")
    d = hit.to_dict()
    # No NaN / non-string keys / exotic types.
    json.dumps(d)
