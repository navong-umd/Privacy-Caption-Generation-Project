# Final Experiments Matrix

_Companion to [BASELINES.md](BASELINES.md), [FUSION_ABLATION.md](FUSION_ABLATION.md), [LLM_EXPERIMENTS.md](LLM_EXPERIMENTS.md) and [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md). Matrix in [`pplib/experiment_matrix.py`](../pplib/experiment_matrix.py), runner in [`pplib/run_matrix.py`](../pplib/run_matrix.py), statistics in [`pplib/matrix_stats.py`](../pplib/matrix_stats.py), test-set lock in [`pplib/testset.py`](../pplib/testset.py); tests in `tests/test_experiment_matrix.py`, `tests/test_run_matrix.py` and `tests/test_matrix_stats.py`. This document contains no numbers; numbers come only from `experiments/EXPnnn/manifest.json`._

---

## 1. The ten arms

`pplib/experiment_matrix.py` is the only arm list. `step2_convgnn/arms.py` derives its RGCN arms from it. Every arm has a fixed experiment id, so a rerun updates the same manifest.

| Id | Arm | Task | Definition | Replication |
|---|---|---|---|---|
| EXP001 | `apg` | classification | `privacy_features=False, token_features=False` | 5 seeds |
| EXP002 | `apg_code` | classification | `False, True` | 5 seeds |
| EXP003 | `ppg` | classification | `True, False` | 5 seeds |
| EXP004 | `ppg_code` | classification | `True, True` (full model) | 5 seeds |
| EXP005 | `rule` | baseline | `step3_caption.baselines.RuleBaseline` | deterministic, 1 run |
| EXP006 | `tfidf` | baseline | `step3_caption.baselines.TfIdfBaseline` | deterministic, 1 run |
| EXP007 | `cap_code` | captions | condition A, code only (PCapGen-style input, an approximation, not a reimplementation) | 1 run on the rating sample |
| EXP008 | `cap_code_api` | captions | condition B, code + source/sink APIs | same |
| EXP009 | `cap_code_taint` | captions | condition C, code + taint path | same |
| EXP010 | `cap_code_taint_pred` | captions | condition G: C + PAcT labels **predicted** by `ppg_code` seed 0 | same |

The four classification arms are a 2x2 over the two featurizer flags of `step2_convgnn.data.record_to_data`: `privacy_features` (the PPG privacy overlay from the knowledge base) and `token_features` (the statement-token hashing trick). The earlier `ppg_knowledge` arm is gone: its features would have come from the same `sdk_catalog.yaml` that generates the weak purpose labels.

Condition G reads its labels from `EXP004/seed_0/predictions.jsonl` and never from `rec["labels"]`; `build_evidence(rec, "G")` refuses to run without them. It measures the pipeline as deployed, not an oracle.

---

## 2. Replication and statistics

- **Classification arms.** Five seeds (`SEEDS = (0, 1, 2, 3, 4)`, passed to `train(..., seed=s)`). Metrics come from `train()`'s return value at a fixed 0.5 threshold; nothing re-scores a model with a different featurization. The manifest reports every seed's metrics and, for macro-F1, per-head macro-F1 and micro-F1, the mean with a 95% t-interval.
- **Baselines.** Fit on the train split, one deterministic run on the test split, with a 95% percentile item-bootstrap interval (2,000 draws).
- **Comparison.** Every classification and baseline arm reports a paired item bootstrap (2,000 draws, same resampled items for both) of macro-F1 against `ppg_code` seed 0: the observed delta, a 95% interval and a two-sided bootstrap p-value. For `ppg_code` itself the delta is 0 by construction.
- **Labels without positives.** Macro-F1 follows `step2_convgnn.metrics` (sklearn, `zero_division=0`): a label with no gold and no predicted positives scores 0 and still counts in the macro. Each manifest lists `label_support` so a reader can see which labels have no support (Advertisement currently has none in the training split).
- **Captions.** Only the 60-item rating sample, drawn once with a fixed seed from the locked test ids and written to `experiments/RATING_SAMPLE.json` (ids, seed, test-set digest). Quality ratings and grounding rates are added in Phase 4.

---

## 3. Running it

```bash
# exercise every arm on weak labels; writes data/scratch_experiments/, never experiments/
python -m pplib.run_matrix --dry-run --dataset data/corpus_run/dataset

# lock the human-labeled test split once (Phase 2), then the reported run
python -m pplib.testset --dataset data/corpus_run/dataset
python -m pplib.run_matrix --dataset data/corpus_run/dataset --provider anthropic --budget-usd 3
```

- `--arms` runs only the named arms (space or comma separated); other manifests are untouched.
- An arm whose manifest and outputs exist for the current test split is skipped. Per-seed `predictions.jsonl` / `test_metrics.json` and per-item caption rows are reused when present, so a rerun retrains nothing that already finished and makes no caption call for an item already captioned.
- `--force` recomputes the named arms from scratch, including new caption calls.
- `--budget-usd` caps caption spend for the whole run through `step3_caption.budget.Budget` (default 0, which still allows the free offline mock). A call whose upper-bound cost would cross the cap is not made; the arm's manifest records calls, tokens, spend (cumulative across resumed runs, plus `this_run`) and `stopped_by_budget`. Rerunning with a larger cap continues where it stopped.
- A real run refuses to start unless `<experiments-root>/TEST_SET.json` matches `digest_test_set` of the current test split (sorted test ids with their labels and label sources, so train-side rebuilds do not change it). `--dry-run` skips that check and forces the root to `data/scratch_experiments/`.

Each manifest carries its fixed `exp_id`, the test-set digest, the config digest, dataset digest, code version, seeds, banner and artifact paths. Caption rows hold no prompt or evidence, so no decompiled code lands in `experiments/`.

---

## 4. Fair-comparison discipline

Same test split, same records, same configs. Arms differ only in the featurization, baseline or caption condition the table names. Caption arms use the same provider, model and prompt template apart from the evidence subset. Any intentional exception goes in the manifest `notes`.

---

## 5. Banners and honesty

Every manifest carries `BANNER_BOOTSTRAP` while any test label is not `human`, so the dry run on weak labels keeps its banners. The reported run on the locked human split carries none. `research/RESULTS.md` is rendered from `experiments/` and never averages across banners.
