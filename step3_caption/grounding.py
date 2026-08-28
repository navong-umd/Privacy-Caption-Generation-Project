"""
Purpose: Post-hoc grounding check for a generated privacy caption (Phase 13).
Input:   a caption string + the evidence dict fed to the LLM (`step3_caption/generate.py::_evidence`).
Output:  GroundingReport with per-axis pass/fail and a summary.

The plan's rule for captions: the model must NOT introduce data types, purposes,
recipients, storage behaviors, or sharing behaviors that are not in the evidence.
Provider MockProvider is deterministically grounded by construction; real
providers (anthropic, openai) can hallucinate silently. Run this check post-hoc
on every real-provider caption before it reaches a user.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Sequence


# Text aliases per PI category. A caption gets credit for mentioning any surface form.
_PI_ALIASES: Dict[str, tuple[str, ...]] = {
    "LOCATION_INFORMATION": ("location", "gps", "geolocation", "whereabouts"),
    "UNIQUE_IDENTIFIER":    ("device id", "device identifier", "imei", "advertising id",
                             "unique identifier", "mac address"),
    "PHONE_INFORMATION":    ("phone number", "phone info", "phone information"),
    "ACCOUNT_INFORMATION":  ("account", "accounts"),
    "CONTACT_INFORMATION":  ("contact", "contacts", "address book"),
    "CALENDAR_INFORMATION": ("calendar",),
    "SMS_MMS":              ("sms", "text message", "mms"),
    "BROWSER_INFORMATION":  ("browser history", "browsing", "bookmarks"),
    "NETWORK_INFORMATION":  ("network info", "network information", "connectivity"),
    "BLUETOOTH_INFORMATION":("bluetooth",),
    "IMAGE":                ("image", "photo", "picture", "camera"),
    "AUDIO":                ("audio", "microphone", "recording"),
    "EMAIL":                ("email", "e-mail"),
    "OTHER":                (),
}

# Text aliases per sink type.
_SINK_ALIASES: Dict[str, tuple[str, ...]] = {
    "network":           ("network", "server", "upload", "send", "http", "internet"),
    "storage":           ("storage", "disk", "file", "database", "shared preferences"),
    "logging":           ("log", "logs", "logging"),
    "ipc":               ("intent", "broadcast", "service", "component"),
    "serialization":     ("json", "gson", "serialize", "serialization"),
    "heuristic_unknown": ("send", "share", "write", "upload"),
}


@dataclass
class GroundingReport:
    """Per-axis grounding report for one caption."""

    prcs_id: str
    mentions_pi: bool
    mentions_sink: bool
    contains_forbidden_recipient: bool
    passes: bool
    notes: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalise(text: str) -> str:
    # Collapse whitespace + lowercase.
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(needle_variants: Sequence[str], haystack: str) -> bool:
    return any(v in haystack for v in needle_variants if v)


def check_grounding(caption: str, evidence: Dict[str, Any],
                    prcs_id: str = "") -> GroundingReport:
    """Return a GroundingReport for one (caption, evidence) pair.

    The report is FAIL if:
      - the caption does not mention the PI category / type from evidence, OR
      - the caption does not mention the sink type from evidence.

    Additionally flags obvious fabrications: if the caption mentions a
    concrete third-party recipient name (advertising / analytics vendor)
    that is NOT in the evidence's involved classes, it is a likely
    hallucination. This is heuristic and intentionally conservative.
    """
    caption_norm = _normalise(caption or "")
    notes: List[str] = []

    # 1. PI grounding: must mention the PI category or one of its aliases.
    pi_cat = (evidence.get("category") or "").upper()
    pi_type = _normalise(evidence.get("pi_type") or "")
    pi_variants = list(_PI_ALIASES.get(pi_cat, ()))
    if pi_type:
        pi_variants.append(pi_type)
    if pi_cat:
        pi_variants.append(pi_cat.lower().replace("_", " "))
    mentions_pi = _contains_any(pi_variants, caption_norm)
    if not mentions_pi and pi_cat:
        notes.append(f"caption does not mention PI category {pi_cat} or any known alias")

    # 2. Sink grounding: must mention the sink type or its aliases.
    sink_type = (evidence.get("sink_type") or "").lower()
    sink_variants = list(_SINK_ALIASES.get(sink_type, ()))
    sink_label = _normalise(evidence.get("sink_api") or "").split("->")[-1]
    if sink_label:
        sink_variants.append(sink_label)
    mentions_sink = _contains_any(sink_variants, caption_norm)
    if not mentions_sink and sink_type:
        notes.append(f"caption does not mention sink type {sink_type} or a related term")

    # 3. Forbidden recipient heuristic: mentions a specific vendor not in the evidence.
    #    Cheap version: look for the token 'google', 'facebook', 'admob', 'firebase'
    #    and require the same token appears in the evidence's involved classes.
    evidence_lower = _normalise(
        " ".join([
            str(evidence.get("app_package") or ""),
            str(evidence.get("source_api") or ""),
            str(evidence.get("sink_api") or ""),
        ])
    )
    forbidden_vendors = ("admob", "adsense", "doubleclick")
    hits = [v for v in forbidden_vendors if v in caption_norm and v not in evidence_lower]
    contains_forbidden = bool(hits)
    if contains_forbidden:
        notes.append(f"caption mentions vendor(s) not in evidence: {hits}")

    passes = mentions_pi and mentions_sink and not contains_forbidden
    return GroundingReport(
        prcs_id=prcs_id,
        mentions_pi=mentions_pi,
        mentions_sink=mentions_sink,
        contains_forbidden_recipient=contains_forbidden,
        passes=passes,
        notes=notes,
    )


def batch_check(captions: Sequence[Dict[str, Any]],
                records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Run check_grounding on many (caption, evidence) pairs. Returns a summary.

    `captions` is the list produced by `generate_captions` (each item has
    prcs_id + caption). `records` is the parallel ADPPG record list.
    """
    from step3_caption.generate import _evidence  # local import to avoid cycle at load

    id_to_rec = {r["prcs_id"]: r for r in records}
    reports: List[GroundingReport] = []
    for c in captions:
        rec = id_to_rec.get(c.get("prcs_id"))
        if rec is None:
            continue
        reports.append(check_grounding(c.get("caption", ""), _evidence(rec), rec["prcs_id"]))
    n = len(reports)
    passed = sum(1 for r in reports if r.passes)
    pi_ok = sum(1 for r in reports if r.mentions_pi)
    sink_ok = sum(1 for r in reports if r.mentions_sink)
    forbidden = sum(1 for r in reports if r.contains_forbidden_recipient)
    return {
        "n": n,
        "passed": passed,
        "pass_rate": (passed / n) if n else 0.0,
        "mentions_pi": pi_ok,
        "mentions_sink": sink_ok,
        "contains_forbidden_recipient": forbidden,
        "reports": [r.to_dict() for r in reports],
    }
