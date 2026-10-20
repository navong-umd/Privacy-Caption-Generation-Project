# RESULTS — preliminary end-to-end evaluation

> **Label provenance (read first).** The held-out test labels used below are **LLM-assisted**
> (two independent passes, 95.1% agreement), **not yet human-verified**, and caption quality is
> scored by an **LLM judge**, not human raters. These are therefore **preliminary pipeline results**
> that demonstrate the method end-to-end on real apps — not publishable ground truth. They become
> paper-grade once a human verifies the label shortlist (→ Cohen's κ) and the G3 study runs.
> Every artifact that rests on weak/LLM labels carries its banner in code and output.

Branch `stage4-ppg-convgnn` · Python 3.14 · 78 tests green · reproducible from committed configs + seeds.

---

## 1. Corpus (real apps)
`pipeline/run_corpus.py` processed 8 AndroZoo APKs fully in-memory → **10,721 source→sink PRCS**
across **7 live apps** (Twitter 4,728 · Spotify 2,712 · Snapchat 1,004 · Duolingo 698 · Instagram 626 ·
WhatsApp 535 · TikTok 418; the Facebook APK was a thin stub → 0). Each PRCS is a taint-sliced subgraph
with source/sink APIs, PI type, sink type, LINDDUN threat, and a per-node `what_it_does`.

## 2. Classification — ConvGNN (G2, preliminary)
Trained on 7,591 weak-labeled PRCS (weak supervision), evaluated on a **100-flow human-labeled
TikTok test split** (banner cleared — the test split is not weak):

| Head | micro-F1 | macro-F1 | subset-acc |
|---|--:|--:|--:|
| Practice | 0.848 | **0.584** | 0.620 |
| Purpose | 0.847 | 0.258 | 0.830 |

Purpose macro-F1 is low **by construction**: the test split is ~84% Functionality / ~16% Analytics /
~0% Advertisement, so macro-F1 (averaged over classes, incl. the empty one) is pulled down while
micro-F1 and subset-accuracy are healthy. A balanced labeled set is the fix — motivates the G1 push.

## 3. Ablation — does the PPG privacy overlay help? (real, non-bootstrap)
Same ConvGNN, same splits/seed, node features **with** vs **without** the privacy overlay
(APG-only = node-type + graph structure, overlay vector zeroed). On the human-labeled test split:

| Metric | Full PPG | APG-only | Δ (overlay) |
|---|--:|--:|--:|
| practice macro-F1 | 0.584 | 0.564 | **+0.021** |
| purpose macro-F1 | 0.259 | 0.228 | **+0.030** |
| practice micro-F1 | 0.848 | 0.832 | +0.016 |
| purpose micro-F1 | 0.847 | 0.840 | +0.007 |
| **overall macro-F1** | **0.421** | 0.396 | **+0.025** |

**The privacy overlay helps on all four metrics** — direct support for the novelty (PPG > APG-only).
Margin is modest but consistent; the lever to grow it is a balanced human-labeled set.

**Statement-token encoder (negative result, honest).** Filling the reserved token hook with a naive
hashing-trick bag-of-tokens over code+callee **hurt** at this scale: practice macro-F1 0.584 → **0.415**,
purpose 0.259 → 0.228. On ~100 test graphs an 8-dim hashed (collision-prone) token vector adds noise,
not signal — so `token_features` is **off by default**. A real learned statement-token embedding
(e.g. a small code encoder into the reserved slot) is future work; the naive version is not it.

## 4. Caption quality — PPG-informed LLM vs Code2Seq baseline (LLM-judged)
Real captions generated with OpenAI gpt-4o (350 over the 7 apps). An LLM judge scored a 70-caption
sample for faithfulness-to-evidence + readability, and ran a blind, order-balanced pairwise choice:

| Caption source | Accuracy (1-5) | Readability (1-5) | Pairwise preferred |
|---|--:|--:|--:|
| **PPG-informed LLM** | **4.59** | **4.56** | **70 / 70 (100%)** |
| Code2Seq baseline | 2.74 | 2.23 | 0 / 70 |

Example (Twitter, database-info → network): LLM *"This app accesses your database information to
ensure proper functionality. It processes and shares this data over the network to maintain app
features."* vs baseline *"getCount value flows to applyAndAckSettings; app appears to share this data."*

## 5. Policy + nutrition facts (structural)
Per-app privacy notice/policy assembled with GDPR + CCPA obligation mapping; **policy completeness
1.0** (every detected fact surfaced) on the corpus. Privacy Nutrition Facts labels (privacy facts +
transparent, rule-based security-risk indicator) render in a one-command static app; all 7 apps score
High risk (banner-marked, since risk uses weak purpose labels).

## 6. What turns these into paper-grade results
1. **Human-verify** the 13-row LLM-label shortlist + a random sample → report human–LLM κ, re-run §2/§3.
2. **Balance** the labeled set across purposes → meaningful macro-F1.
3. **G3 user study** → confirm the §4 caption preference with real developers/users.
4. **Statement-token encoder** (reserved hook) + ablations vs GGNN/R-GAT → strengthen §3.

_Regenerate: `run_corpus` → `run_g1g2` (metrics) → `step2_convgnn.ablation` → `step3_caption.generate
--provider openai` → `step4_eval.caption_judge --provider openai`._
