# Experiment Platform

_Phase 19 deliverable. Schema + helpers in [`pplib/experiment.py`](../pplib/experiment.py); tests in [`tests/test_experiment.py`](../tests/test_experiment.py)._

Every experiment reruns from its manifest alone. Anything not on the manifest is untracked and cannot be reproduced.

---

## 1. Directory layout

```
experiments/
├── index.jsonl                     one line per experiment, keyed by exp_id
├── EXP001/
│   ├── manifest.json               the reproducible record
│   └── (optional artifacts)
├── EXP002/
│   ├── manifest.json
│   └── ...
└── EXP003/ ...
```

`experiments/` sits at the repo root (or wherever `experiments_root` points; the helpers accept an explicit path so parallel runs on different machines can write into different roots).

---

## 2. Manifest schema

`ExperimentRun` (`pplib/experiment.py`):

| Field | Type | Meaning |
|-------|------|---------|
| `exp_id` | `str` matching `^EXP\d{3,}$` | Stable id. `EXP001`, `EXP002`, ... `EXP1234`. |
| `name` | `str` | Short human name. |
| `code_version` | `str` | `branch@shortsha` (via `current_code_version()`) or `"unknown"`. |
| `config_digest` | `str` (sha1) | `digest_configs([configs/ppg.yaml, configs/convgnn.yaml, ...])`. |
| `dataset_digest` | `str` (sha1) | `digest_dataset(dataset_dir)` over `adppg.jsonl` + `splits.json`. |
| `seed` | `int` | Random seed. |
| `metrics` | `dict` | Scalars: `{"practice_macro_f1": 0.71, ...}`. |
| `artifacts` | `list[str]` | Paths (relative to the run directory) produced by the run. |
| `model_version` | `str` | Optional: e.g. `"rgcn v0.4"`, `"anthropic claude-3.5-sonnet"`. |
| `notes` | `str` | Free-form annotator note. |
| `schema_version` | `str` | `"1.0.0"`. |

`validate_experiment(dict)` enforces every required field, the `exp_id` pattern, and the types of `metrics` and `artifacts`.

---

## 3. Save / load / index

```python
from pplib.experiment import ExperimentRun, save_experiment, load_experiment, list_experiments

run = ExperimentRun(exp_id="EXP001", name="rgcn full ppg baseline", ...)
save_experiment(run, "experiments")             # writes manifest + appends to index

loaded = load_experiment("experiments", "EXP001")
all_runs = list_experiments("experiments")
```

- `save_experiment` is idempotent for the same `exp_id`: rerunning replaces the manifest and rewrites the index entry, never duplicates.
- Manifests are `json.dumps(indent=2, sort_keys=True)`: byte-stable, diff-friendly.
- The flat `experiments/index.jsonl` file is the canonical listing every downstream consumer greps. `RESULTS.md` in Phase 22 will render it as a table.

---

## 4. Digest helpers

Two zero-config digests keep the manifest honest:

- `digest_configs([paths])`: sha1 over the concatenated bytes of every listed config, order-independent (we sort first). Two runs with the same digest have byte-identical configs.
- `digest_dataset(dataset_dir)`: sha1 over `adppg.jsonl` + `splits.json`. Two runs with the same digest saw the exact same records and splits.

`current_code_version()` shells out to `git rev-parse --short HEAD` and `--abbrev-ref HEAD`; returns `"branch@sha"` or `"unknown"` when git is unavailable.

---

## 5. When to log an experiment

Log a run whenever it will appear in `RESULTS.md`, `EXPERIMENT_LOG.md`, or any comparison. In practice:

- Baseline sweeps (Phase 10 / 21): one exp per (baseline, split) pair.
- Fusion arms (Phase 12): one exp per (arm, seed) pair.
- LLM experiments (Phase 14): one exp per (condition, provider) pair.
- Any ablation with a claimed delta: log both arms.

Do not log the following:

- Individual test invocations.
- Sanity-run pipeline invocations that produce no metric worth quoting.
- Failed runs (the record would carry stale metrics). Log the retry that succeeded.

---

## 6. What the manifest cannot capture

- The exact wheel versions installed. Pin them in `requirements.txt` (Phase 1) and reproduce environment via `Dockerfile`.
- Runtime hardware. Note in `notes` when it matters for latency comparisons.
- Random non-determinism from provider APIs. Note temperature + provider version in `model_version`.

If a rerun of the same manifest produces different metrics, one of these was not fixed. That is a real bug that needs finding, not a rounding tolerance.

---

## 7. What Phase 19 explicitly did NOT do

- Did not run any experiment. The platform stores runs; Phase 21 produces the numbers.
- Did not wire logging into `pipeline/run_pipeline.py` or `step2_convgnn/train.py`. Wiring is a per-experiment concern; call sites vary.
- Did not add a UI. `list_experiments` is enough to render tables in `RESULTS.md`.
- Did not migrate existing ad-hoc metric files (`data/convgnn/metrics.csv`, `data/ablation/ablation.json`) into the manifest format. Legacy consumers still work; Phase 21 or 22 folds those into fresh `EXP###` records with a note pointing at their source file.
