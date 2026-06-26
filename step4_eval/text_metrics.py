"""
Purpose: Self-contained BLEU + ROUGE-L for caption-quality evaluation (no heavy deps).
Input:   hypothesis string + one or more reference strings.
Output:  BLEU-4 (smoothed) and ROUGE-L F1 in [0,1].

These ONLY produce meaningful numbers against real human reference captions. With no
references the harness must not invent scores — it reports "no references" instead.
"""
from __future__ import annotations

import math
from collections import Counter
from typing import List


def _tokens(s: str) -> List[str]:
    return s.lower().split()


def _ngrams(toks: List[str], n: int) -> Counter:
    return Counter(tuple(toks[i:i + n]) for i in range(len(toks) - n + 1))


def sentence_bleu(hyp: str, refs: List[str], max_n: int = 4) -> float:
    """Smoothed sentence-level BLEU-`max_n` against the best-matching reference."""
    h = _tokens(hyp)
    if not h:
        return 0.0
    precisions = []
    for n in range(1, max_n + 1):
        h_ng = _ngrams(h, n)
        if not h_ng:
            break  # hypothesis too short for this order; average over existing orders only
        max_ref = Counter()
        for ref in refs:
            r_ng = _ngrams(_tokens(ref), n)
            for g, c in r_ng.items():
                max_ref[g] = max(max_ref[g], c)
        overlap = sum(min(c, max_ref[g]) for g, c in h_ng.items())
        # +1 smoothing keeps short captions from collapsing to 0
        precisions.append((overlap + 1.0) / (sum(h_ng.values()) + 1.0))
    if not precisions:
        return 0.0
    geo = math.exp(sum(math.log(p) for p in precisions) / len(precisions))
    ref_len = min((len(_tokens(r)) for r in refs), key=lambda rl: abs(rl - len(h)))
    bp = 1.0 if len(h) > ref_len else math.exp(1 - ref_len / max(len(h), 1))
    return bp * geo


def _lcs(a: List[str], b: List[str]) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            dp[i][j] = dp[i - 1][j - 1] + 1 if a[i - 1] == b[j - 1] else max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l(hyp: str, refs: List[str]) -> float:
    """ROUGE-L F1 against the best-matching reference."""
    h = _tokens(hyp)
    best = 0.0
    for ref in refs:
        r = _tokens(ref)
        if not h or not r:
            continue
        lcs = _lcs(h, r)
        if lcs == 0:
            continue
        prec, rec = lcs / len(h), lcs / len(r)
        best = max(best, 2 * prec * rec / (prec + rec))
    return best
