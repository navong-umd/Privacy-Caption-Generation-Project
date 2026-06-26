"""
Purpose: Code2Seq-style NMT BASELINE for captions (the prior approach we compare against).
Input:   a PRCS record (code snippet + source/sink APIs + labels).
Output:  a terse, seq2seq-style caption string.

PLACEHOLDER BASELINE: a trained Code2Seq model needs paired (code-path -> caption) data,
which only exists after human annotation (G1). Until then this emits a deterministic,
template caption from extracted AST-path tokens so the comparison harness has a baseline to
run against. Marked clearly so it is never mistaken for a trained model's output.
"""
from __future__ import annotations

import re
from typing import Dict, List

BASELINE_TAG = "code2seq-baseline (untrained placeholder)"


def _short(api: str) -> str:
    """Last path token of a 'pkg.Class->method' signature."""
    if not api:
        return "data"
    method = api.split("->")[-1]
    return re.sub(r"[^A-Za-z0-9]", " ", method).strip() or method


def _terminals(snippet: str) -> List[str]:
    """Crude AST-path terminals: identifier tokens from the code snippet."""
    toks = re.findall(r"[A-Za-z_][A-Za-z0-9_]+", snippet or "")
    return [t for t in toks if t not in ("invoke", "virtual", "move", "result", "object")][:8]


class Code2SeqBaseline:
    """Deterministic stand-in for a trained Code2Seq captioner."""

    def caption(self, rec: Dict) -> str:
        src = _short(rec.get("source_api", ""))
        snk = _short(rec.get("sink_api", ""))
        practice = rec.get("labels", {}).get("practice", [])
        act = "share" if "Sharing" in practice else "use"
        return f"{src} value flows to {snk}; app appears to {act} this data."
