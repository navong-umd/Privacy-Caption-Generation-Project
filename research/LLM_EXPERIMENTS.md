# LLM Experiments (A through G)

_Phase 14 deliverable. Builds on [CAPTION_GENERATION.md](CAPTION_GENERATION.md), [PRCS_SCHEMA.md](PRCS_SCHEMA.md), and [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md). Implementation in [`step3_caption/experiments.py`](../step3_caption/experiments.py); tests in [`tests/test_llm_experiments.py`](../tests/test_llm_experiments.py)._

Which evidence representation produces the strongest privacy captions? The plan asks for a six-condition ablation on the same PRCS with the same provider so the answer is not confounded.

Phase 14 lands the harness (condition builders + a provider-agnostic runner that records provenance). Real cross-condition scoring is Phase 15 (automated) and the reserved human-eval gate (last).

---

## 1. The conditions

| Condition | Label | Sees | Everything above plus... |
|-----------|-------|------|--------------------------|
| A | `code_only` | `code_snippet` | (baseline) |
| B | `code_plus_api` | + `source_api`, `sink_api` | callee identity |
| C | `code_plus_taint_path` | + `taint_path`, `taint_rules`, `hop_count` | how data flows |
| D | `code_plus_ppg` | + subgraph shape, involved methods | structural context |
| E | `code_plus_ppg_plus_pact` | + PI category / type / permission / sink type / privacy threat / practice / purpose | KB + labels |
| F | `full_evidence` | + `app_package`, `apk_filename`, `class_name`, `method_name` | app identity |
| G | `code_plus_taint_path_plus_predicted_pact` | C + `practice` / `purpose` **predicted** by the classifier | predicted labels |

The conditions are monotone by design: every condition strictly extends the previous. That keeps the ablation interpretable: if F > A, we know where the delta came from because each intermediate condition is scored too.

Note that C branches off B (skips PPG) and E branches off D (skips taint path); F is the union of everything. G is C plus PAcT labels passed in by the caller (`build_evidence(rec, "G", predicted=...)`); it never reads `rec["labels"]` and refuses to run without predictions. The experiment matrix uses A, B, C and G as its caption arms (see [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md)), with G fed by the `ppg_code` seed-0 predictions. That matches the plan's ladder rather than a strict chain, so tests assert absence of the fields each condition is supposed to omit.

---

## 2. Provider abstraction

The runner takes any object with `generate(prompt, evidence) -> str`. It reads two optional attributes for provenance: `provider.name` and `provider.model`.

`step3_caption/llm_interface.py::MockProvider` and `RealProvider` already conform. Users plug in Anthropic, OpenAI, or a stub as needed.

A provider error is captured (`ConditionResult.error`) instead of raised, so one bad row does not sink a corpus-wide sweep. Downstream analysis filters on `error == ""`. Passing a `step3_caption.budget.Budget` as `run_condition(..., budget=...)` caps spend: a call the budget refuses is not made and its error is `BUDGET_REFUSED`.

---

## 3. Provenance recorded per run

`ConditionResult` fields:

- `prcs_id`, `condition`, `condition_label`
- `provider`, `model`, `temperature`
- `prompt` (full text), `evidence` (the exact dict shown to the model)
- `caption` (raw output), `prompt_chars`, `caption_chars`
- `latency_seconds`
- `prompt_tokens`, `completion_tokens` (populated by providers that surface them; None otherwise)
- `error` (empty on success)

`.to_dict()` is JSON-ready. The Phase 19 experiment platform will fold these into a per-run manifest.

---

## 4. Scoring: how the winner gets crowned

Phase 14 does not score. Phase 15 automated metrics (BLEU / ROUGE / BERTScore / LLM-as-judge) run each condition against reference captions and report per-condition means with confidence intervals. Human ratings (Phase 15 human eval gate, deferred to the very last) resolve any ambiguities the automated metrics leave.

Cost caps for real-provider sweeps live in `configs/llm.yaml` (`--per-app`, `--limit` on the generator). Never sweep the full corpus in six conditions without a budget in `.env` or a `--limit`.

---

## 5. Invariants tested

- `CONDITIONS == ("A", "B", "C", "D", "E", "F", "G")`.
- `A` exposes exactly `{prcs_id, code_snippet}`.
- `B` adds APIs and nothing else.
- `C` adds taint path and hop count, no PPG, no PAcT.
- `D` adds subgraph shape + involved methods, no PAcT, no taint path.
- `E` adds PAcT + KB fields, no taint path.
- `F` is the union of all fields.
- `G` equals `C` plus the predicted `practice` / `purpose`, never reads `rec["labels"]`, and raises without predictions.
- `run_all_conditions` includes `G` only when predictions are given.
- With a budget, a second call that would cross the limit is not made.
- Unknown condition raises `ValueError`.
- Prompt is stable across repeat calls with the same evidence.
- `run_condition` never raises; provider errors become populated `error` strings.
- `to_dict` is JSON-ready.

---

## 6. What Phase 14 explicitly did NOT do

- Did not run any real LLM. Would require API budget approval and would freeze numbers before Phase 15's evaluation harness lands.
- Did not add per-token accounting for providers that do not surface it. `prompt_tokens` / `completion_tokens` stay `None` on providers that only return text.
- Did not add streaming support. Every condition is a single blocking call. Streaming buys nothing in a comparison harness.
- Did not add a caching layer for repeated `(condition, provider, evidence)` triples. That belongs in the Phase 19 experiment platform once we know which triples we actually rerun.
- Did not change `configs/llm.yaml` defaults. Provider stays `mock` so `pytest tests/` remains offline and hermetic.
