# Final Experiments Matrix

_Phase 21 deliverable. Companion to [BASELINES.md](BASELINES.md), [FUSION_ABLATION.md](FUSION_ABLATION.md), [LLM_EXPERIMENTS.md](LLM_EXPERIMENTS.md), and [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md). Matrix in [`pplib/experiment_matrix.py`](../pplib/experiment_matrix.py); tests in [`tests/test_experiment_matrix.py`](../tests/test_experiment_matrix.py). This document does not contain numbers; numbers come only from real runs saved under `experiments/EXP???/manifest.json`._

The plan's eight comparison arms, pinned in one place, plus a stub assembler that refuses to invent metrics.

---

## 1. The eight arms

`FINAL_ARMS` in `pplib/experiment_matrix.py`, verbatim from the plan:

| # | Arm | Task | What it sees |
|---|-----|------|-------------|
| 1 | `code` | captions (LLM condition A) | Code snippet only. |
| 2 | `code_api` | captions (LLM condition B) | Code + source / sink API strings. |
| 3 | `code_taint` | captions (LLM condition C) | Code + taint path + per-hop rules. |
| 4 | `apg` | classification (RGCN) | Structure + node-type embedding only. |
| 5 | `ppg` | classification (RGCN) | + PPG privacy overlay from the KB. |
| 6 | `ppg_code` | classification (RGCN) | + statement-token hashing trick. |
| 7 | `ppg_knowledge` | classification (RGCN) | Same as `ppg`, kept because the plan names it. |
| 8 | `ppg_code_knowledge` | classification (RGCN) | Everything. |

Arms 1 to 3 exercise the LLM caption harness (Phase 14 conditions). Arms 4 to 8 exercise the RGCN classifier (Phase 12 fusion knobs plus an APG-only baseline).

The matrix spans both tasks on purpose. Reporting them side by side is what lets a reader see whether the caption story tracks the classification story.

---

## 2. Mapping to existing knobs

Nothing here is a new configuration. Every arm reuses knobs already defined in earlier phases:

- Caption arms map onto `step3_caption.experiments.build_evidence(rec, condition)`. `code` -> A, `code_api` -> B, `code_taint` -> C.
- Classification arms map onto `step2_convgnn.data.record_to_data(rec, privacy_features=?, token_features=?)`. See table:

| Arm | `privacy_features` | `token_features` |
|-----|---------------------|-------------------|
| `apg` | False | False |
| `ppg` | True | False |
| `ppg_code` | False | True |
| `ppg_knowledge` | True | False |
| `ppg_code_knowledge` | True | True |

`ppg` and `ppg_knowledge` share flags. That is intentional: the plan names them separately so a reader can see the KB overlay contribution in isolation; the RGCN featurization does not distinguish them because the KB signal already IS the PPG overlay in the featurizer. If a future arm splits them (e.g. an ablation that toggles individual PI fields), the flag map is where that lives.

---

## 3. The assembler

`plan_runs(dataset_digest, config_digest, code_version, seed=13, provider="mock", start_from=1)` returns one `ExperimentRun` stub per arm. Each stub has:

- Stable `exp_id` in the canonical order (`EXP001` through `EXP008` by default).
- Populated identity fields (name, code_version, config_digest, dataset_digest, seed).
- **Empty** `metrics` and `artifacts`.
- A `notes` string that names the arm, the task, and the provider.

**Metrics are never pre-populated.** The plan's honesty rule is:

> Never claim it as a result until the experiments support it.

`plan_runs` refuses to invent numbers. Actually running the matrix belongs to a real compute job with a budget approval; the stubs are the plan that job executes.

Default provider is `mock`. Caption arms with `provider="mock"` produce deterministic template output at no cost; only a budget-approved run overrides that to `anthropic` or `openai` explicitly.

---

## 4. How to actually run one arm

Pattern (not wired into a driver; the runner is per-arm because compute cost differs):

```python
from pplib.experiment import ExperimentRun, current_code_version, digest_configs, digest_dataset, save_experiment
from pplib.experiment_matrix import arm_spec, plan_runs

dataset_dir = "data/corpus_run/dataset"
configs = ["configs/ppg.yaml", "configs/sinks.yaml", "configs/convgnn.yaml",
           "configs/llm.yaml", "configs/weak_labels.yaml", "configs/sdk_catalog.yaml"]

stubs = plan_runs(
    dataset_digest=digest_dataset(dataset_dir),
    config_digest=digest_configs(configs),
    code_version=current_code_version(),
)

# For a classification arm:
spec = arm_spec("ppg_code_knowledge")
# call step2_convgnn.train.train(...) with the flags in spec.flags,
# fill stub.metrics with practice_macro_f1 / purpose_macro_f1 / micro_f1 / ...
# fill stub.artifacts with the paths under experiments/EXP008/.
# then save_experiment(stub, "experiments").

# For a caption arm:
spec = arm_spec("code")
# call step3_caption.experiments.run_condition(rec, spec.condition, provider)
# for the test-split PRCS, run step4_eval.aggregate.aggregate(...) to get metrics,
# fill stub.metrics + stub.artifacts, save_experiment(stub, "experiments").
```

Each concrete runner lives close to the code it exercises. This module is only the plan.

---

## 5. Fair-comparison discipline

Same test split. Same seed. Same PRCS records. Different only in the featurization / condition the arm dictates. If any of the following differ between two arms, the comparison is invalid:

- `dataset_digest`.
- `config_digest` (except for the ONE config the arm changes).
- `seed`.
- Underlying weights of the RGCN (arms 4 to 8 must retrain from the same init).
- Underlying provider + model for caption arms (arms 1 to 3 must use the same provider and same prompt template beyond the evidence subset).

The `ExperimentRun.notes` field is where any intentional exception gets recorded.

---

## 6. Banners and honesty

Every `manifest.json` produced from these arms MUST carry the applicable banner:

- `BANNER_BOOTSTRAP` when the test split still runs on weak labels.
- `BANNER_JUDGE` when caption quality is scored by an LLM judge.
- Any human-eval numbers appear only after the final human-eval gate.

`RESULTS.md` in Phase 22 renders per-arm rows from `experiments/index.jsonl`. It does not average across banners or hide them.

---

## 7. What Phase 21 explicitly did NOT do

- Did not execute any arm. Real runs need budget approval and dedicated compute; the matrix is the plan those runs follow.
- Did not fabricate numbers. `metrics == {}` on every stub. Trying to render `RESULTS.md` today shows the plan, not results.
- Did not fold BERTScore into the caption metrics list. It is still a Phase 15 gap (torch dependency); when it lands, the caption arms grow one more column.
- Did not split `ppg_knowledge` from `ppg` in the flag table. The plan names them separately; the featurizer does not. If a future ablation isolates individual KB fields, `_CLASSIFICATION_FLAGS` is where the new mapping lives.
- Did not add a `--budget-approved` flag to the concrete runners. That approval is a human review, not a config toggle.
