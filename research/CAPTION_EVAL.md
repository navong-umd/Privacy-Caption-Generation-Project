# Caption Evaluation (Automated Only)

_Phase 15 deliverable. Builds on [CAPTION_GENERATION.md](CAPTION_GENERATION.md), [LLM_EXPERIMENTS.md](LLM_EXPERIMENTS.md), and [BASELINES.md](BASELINES.md). Implementation in [`step4_eval/aggregate.py`](../step4_eval/aggregate.py); tests in [`tests/test_caption_eval.py`](../tests/test_caption_eval.py). Existing text-metrics helpers in [`step4_eval/text_metrics.py`](../step4_eval/text_metrics.py); LLM-as-judge in [`step4_eval/caption_judge.py`](../step4_eval/caption_judge.py)._

**Human evaluation is not in this phase.** Per the user's rule, human eval is the very last gate. Phase 15 covers only automated signals that can run in CI without a human in the loop.

The plan asks for four automated axes. Phase 15 wires them into one aggregator so a run produces a single JSON report and one row per caption.

---

## 1. What the aggregator combines

`step4_eval.aggregate.aggregate(captions, records, references=None, judge_rows=None)` returns:

```json
{
  "per_caption": [
    {
      "prcs_id": "prcs_1",
      "caption": "...",
      "label_source": "weak",
      "text_metrics": { "bleu4": 0.31, "rouge_l": 0.42 },
      "grounding":    { "passes": true, "mentions_pi": true, "mentions_sink": true, ... },
      "judge":        { "score": 0.8, "verdict": "faithful" }
    },
    ...
  ],
  "summary": {
    "n_captions":         120,
    "text_metrics":       { "bleu4_mean": 0.29, "rouge_l_mean": 0.38, "n_scored": 120 },
    "grounding":          { "passed": 106, "total": 120, "pass_rate": 0.883 },
    "judge":              { "mean": 0.79, "n": 120 },
    "human_eval_deferred": true
  }
}
```

Every axis is independent: a missing input (no references, no judge rows) collapses that section to an honest status string rather than fabricating a score.

---

## 2. Text metrics: BLEU-4 and ROUGE-L

Live in `step4_eval/text_metrics.py`. Zero-dep, deterministic:

- BLEU-4 with +1 smoothing so short captions do not collapse to 0.
- ROUGE-L F1 against the best-matching reference in the list.

**Only meaningful against real human reference captions.** With no references on disk, the aggregator reports `text_metrics: {status: "no references on disk, BLEU / ROUGE-L not computed"}`. It never invents a score.

BERTScore is not currently in-tree. Adding it means a torch dependency and a model download; scoped for Phase 21 when it can piggyback on the existing torch install. When it lands, `text_metrics` grows a `bertscore_f1` field with the same rules (present only when references exist).

---

## 3. Grounding (Phase 13)

`step3_caption.grounding.check_grounding(caption, evidence)` returns a per-axis pass/fail:

- Mentions the PI category or one of its natural-language aliases.
- Mentions the sink type or a sink alias.
- Does not name a third-party vendor absent from the evidence (conservative hallucination check).

This is the axis that runs on every caption unconditionally: it needs no reference caption, only the evidence dict `_evidence(rec)` already reconstructs from the PRCS record. The Phase 21 automated caption metric is `grounding.pass_rate` on the test split.

---

## 4. LLM-as-judge (`step4_eval/caption_judge.py`)

Existing module. Two modes:

- Mock (default, offline): heuristic scoring based on evidence-term coverage. Deterministic; safe for CI.
- Real judge (`--provider openai|anthropic`): scores each caption for faithfulness and readability against the evidence, plus a blind pairwise comparison between the PPG-informed caption and the Code2Seq baseline (order-balanced).

The aggregator does not run the judge itself. It consumes the judge's output (`caption_eval.json` rows with `prcs_id` and `score`) and folds them into the per-caption + summary tables.

Every judge output must carry the `LLM-JUDGED (not human ratings)` banner. That banner propagates through the aggregator into any downstream report. Human ratings are the only replacement.

---

## 5. Bootstrap / weak banner propagation

Every per-caption row includes `label_source` from the input caption. Downstream reports MUST surface `BANNER_BOOTSTRAP` if any row has `label_source == "weak"`. `pipeline/run_pipeline.py::print` already does this. The aggregator sets `summary.human_eval_deferred = True` so a report reader is reminded that automated metrics stand in for, but do not replace, human judgment.

---

## 6. Where this is wired

Not yet in `pipeline/run_pipeline.py` or `pipeline/run_corpus.py`. Phase 15 lands the aggregator itself and its test suite. Wiring is a two-line change on each driver: build the `judge_rows` from `caption_judge.py --provider mock` and pass it into `aggregate(captions, records, references, judge_rows)`. Landing the wire without also introducing schema drift in `docs/RESULTS.md` is a separate task; keeping the aggregator standalone lets Phase 21 own the numbers.

---

## 7. Human evaluation gate

The human eval instrument lives in `step4_userstudy/build_study.py` today (blind A/B pairs, rating sheet, protocol, consent template). It is deliberately **not** run in this phase and not scored here. It stands as the final gate per the user's plan:

> **"human eval should be last, so u should never stop working until each phase is completely done, waterfall style, tested, reviewed."**

Phase 22 packages everything; the human eval executes as the final gate after Phase 22.

---

## 8. Invariants tested

- With no references, `text_metrics.status` reports NO_REFS_MESSAGE and `n_scored == 0`.
- With references, `bleu4_mean` and `rouge_l_mean` are in `[0, 1]` and are computed against the reference list.
- Grounding runs on every caption regardless of references and pass rate matches content.
- LLM-judge summary averages provided scores; reports "no judge rows" when absent.
- Per-caption rows carry `text_metrics`, `grounding`, and `judge` blocks with the expected shape.
- `summary.human_eval_deferred == True` on every run.
- Extra records in `records` that have no matching caption are ignored cleanly.

---

## 9. What Phase 15 explicitly did NOT do

- Did not add BERTScore. Deferred to Phase 21 to piggyback on the torch install.
- Did not run the human evaluation. Reserved for the final gate per user rule.
- Did not wire the aggregator into `pipeline/run_pipeline.py` or `pipeline/run_corpus.py`. Belongs to Phase 17 (end-to-end canonical command).
- Did not add per-provider comparison. `LLM_EXPERIMENTS.md` covers the six conditions on one provider; multi-provider is a Phase 21 concern.
- Did not touch the existing `step4_eval/evaluate.py` classification / policy paths. Those are stable and orthogonal to caption quality.
