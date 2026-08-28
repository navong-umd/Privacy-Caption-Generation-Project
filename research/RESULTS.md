# Results

This document contains no numbers yet.

Numbers live only in `experiments/EXP???/manifest.json` records after a real run of a matrix arm from [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md). Rendering a table here without runs would violate the plan's rule:

> Never claim it as a result until the experiments support it.

## How this document gets populated

For each arm in the final matrix:

1. Run the concrete runner (classification for arms 4-8, caption generation for arms 1-3).
2. Score with the shared metric functions (`step3_caption.baselines.multilabel_metrics` for classification, `step4_eval.aggregate.aggregate` for captions).
3. Save the manifest via `pplib.experiment.save_experiment(run, "experiments")`.
4. Regenerate the tables in this file from `experiments/index.jsonl`.

## Table skeletons (to be filled)

### Classification matrix

Task: PAcT Practice + Purpose on the ADPPG test split.

| arm | practice_macro_f1 | practice_micro_f1 | purpose_macro_f1 | purpose_micro_f1 | seed | dataset_digest | banner |
|-----|---:|---:|---:|---:|---:|---|---|
| apg | | | | | | | |
| ppg | | | | | | | |
| ppg_code | | | | | | | |
| ppg_knowledge | | | | | | | |
| ppg_code_knowledge | | | | | | | |

### Caption matrix

Task: privacy caption on the same test-split PRCS.

| arm | grounding_pass_rate | bleu4_mean | rouge_l_mean | judge_mean | provider | banner |
|-----|---:|---:|---:|---:|---|---|
| code | | | | | | |
| code_api | | | | | | |
| code_taint | | | | | | |

BLEU / ROUGE columns stay empty until a reference caption set is on disk (see [CAPTION_EVAL.md](CAPTION_EVAL.md) §2). Judge column stays empty unless `caption_judge.py` was run.

### Baseline reference

Same metric family as the classification matrix, run through:

| baseline | practice_macro_f1 | purpose_macro_f1 | seed | banner |
|----------|---:|---:|---:|---|
| rule | | | | |
| tfidf | | | | |

## Bootstrap and banner rules

- Every row derived from weak labels carries `BANNER_BOOTSTRAP`.
- Every LLM-judge row carries `BANNER_JUDGE`.
- Human evaluation rows do not appear here; they appear only after the final human-eval gate.

## Related documents

- [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md) for the eight-arm plan.
- [BASELINES.md](BASELINES.md) for the rule and TF-IDF baselines.
- [CAPTION_EVAL.md](CAPTION_EVAL.md) for the aggregated caption metrics.
- [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md) for the taxonomy that will accompany the tables.
- [LIMITATIONS.md](LIMITATIONS.md) for what these numbers, when they exist, will and will not claim.
