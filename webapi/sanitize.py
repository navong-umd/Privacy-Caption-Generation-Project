"""Repair the double-encoded UTF-8 (mojibake) some committed artifacts contain.

A few JSON files were written with ensure_ascii=False and then re-encoded once
too many times, so an em dash shows up as 'â€"', a section sign as 'Â§', and so
on. We fix the common, unambiguous sequences on read so the website renders
clean text. Pure-ASCII text is never touched.
"""
from __future__ import annotations

from typing import Any

# Known bad -> intended, in a safe order (longer sequences first).
_REPLACEMENTS = [
    ("â€™", "’"),   # right single quote
    ("â€œ", "“"),   # left double quote
    ("â€\x9d", "”"),  # right double quote
    ("â€”", "—"),   # em dash
    ("â€“", "–"),   # en dash
    ("â€¦", "…"),   # ellipsis
    ("Â§", "§"),    # section sign
    ("Â©", "©"),    # copyright
    ("Â®", "®"),    # registered
    ("Â ", " "),          # non-breaking space artifact
    ("Ã©", "é"),    # e-acute
    ("â€", "—"),    # trailing em-dash remnant (last, catch-all)
]


def fix_text(value: str) -> str:
    if not value or ("â" not in value and "Ã" not in value and "Â" not in value):
        return value
    out = value
    for bad, good in _REPLACEMENTS:
        if bad in out:
            out = out.replace(bad, good)
    return out


def fix_deep(obj: Any) -> Any:
    """Recursively fix strings inside dicts / lists returned to the client."""
    if isinstance(obj, str):
        return fix_text(obj)
    if isinstance(obj, list):
        return [fix_deep(x) for x in obj]
    if isinstance(obj, dict):
        return {k: fix_deep(v) for k, v in obj.items()}
    return obj
