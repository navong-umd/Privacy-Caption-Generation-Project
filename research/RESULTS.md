# Results

This document contains no numbers yet.

Numbers live only in `experiments/EXP???/manifest.json` records after a real run of a matrix arm from [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md). Rendering a table here without runs would violate the plan's rule:

> Never claim it as a result until the experiments support it.

## How this document gets populated

1. Lock the human-labeled test split: `python -m pplib.testset --dataset <dataset>`.
2. Run the matrix: `python -m pplib.run_matrix --dataset <dataset>`. It writes one manifest per arm (EXP001 to EXP010) under `experiments/`.
3. Render this file from `experiments/` (Phase 5 renderer).

## Table skeletons (to be filled)

### Classification matrix

Task: PAcT Practice + Purpose on the locked test split. RGCN arms: mean and 95% t-interval over 5 seeds. Baselines: one run with a 95% item-bootstrap interval. Every row: paired bootstrap of macro-F1 against `ppg_code` seed 0.

| id | arm | macro_f1 | practice_macro_f1 | purpose_macro_f1 | delta vs ppg_code seed 0 | banner |
|----|-----|---:|---:|---:|---:|---|
| EXP001 | apg | | | | | |
| EXP002 | apg_code | | | | | |
| EXP003 | ppg | | | | | |
| EXP004 | ppg_code | | | | | |
| EXP005 | rule | | | | | |
| EXP006 | tfidf | | | | | |

### Caption matrix

Task: privacy captions for the 60-item rating sample, rated blind by experts (Phase 4).

| id | arm | accuracy | completeness | clarity | best-pick rate | grounding hallucination rate | banner |
|----|-----|---:|---:|---:|---:|---:|---|
| EXP007 | cap_code | | | | | | |
| EXP008 | cap_code_api | | | | | | |
| EXP009 | cap_code_taint | | | | | | |
| EXP010 | cap_code_taint_pred | | | | | | |

## Bootstrap and banner rules

- Every row derived from weak labels carries `BANNER_BOOTSTRAP`.
- Every LLM-judge row carries `BANNER_JUDGE`.
- Human evaluation rows do not appear here; they appear only after the final human-eval gate.

## Related documents

- [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md) for the ten-arm matrix.
- [BASELINES.md](BASELINES.md) for the rule and TF-IDF baselines.
- [CAPTION_EVAL.md](CAPTION_EVAL.md) for the aggregated caption metrics.
- [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md) for the taxonomy that will accompany the tables.
- [LIMITATIONS.md](LIMITATIONS.md) for what these numbers, when they exist, will and will not claim.
