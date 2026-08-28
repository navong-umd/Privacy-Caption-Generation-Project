# Error Analysis

_Phase 16 deliverable. Companion to [BASELINES.md](BASELINES.md), [PPG_SCHEMA.md](PPG_SCHEMA.md), and [CAPTION_GENERATION.md](CAPTION_GENERATION.md). Constants and validator in [`pplib/error_taxonomy.py`](../pplib/error_taxonomy.py); tests in [`tests/test_error_taxonomy.py`](../tests/test_error_taxonomy.py)._

A failing prediction that no one records is a lesson lost. Phase 16 pins the vocabulary + record shape so every error surfaces the same way regardless of who logged it.

---

## 1. Categories

`ERROR_CATEGORIES` (`pplib/error_taxonomy.py`) mirrors the plan verbatim:

| Category | Meaning |
|----------|---------|
| `incorrect_source` | Something flagged as a PI source that is not. |
| `incorrect_sink` | Something flagged as a sink that is not. |
| `missing_flow` | Real source-to-sink flow that taint failed to find. |
| `incorrect_path` | Path found but wrong or spurious hops. |
| `incorrect_pi_type` | PI type on the source is wrong. |
| `incorrect_practice` | Practice head mislabels the PRCS. |
| `incorrect_purpose` | Purpose head mislabels the PRCS. |
| `insufficient_context` | PRCS subgraph too small to caption correctly. |
| `hallucinated_information` | Caption invents a data type, recipient, or purpose absent from evidence. |
| `incomplete_caption` | Caption skips an axis (PI or sink) it should have covered. |
| `generic_caption` | Caption is technically right but useless (no specifics). |

Consumers must use these exact strings. Anything else fails `validate_error_record`.

---

## 2. Stages

`ERROR_STAGES` names which pipeline stage produced the error. Routing fixes needs this:

`static_analysis | knowledge_base | ppg | traversal | prcs | labeling | classifier | caption | policy | evaluation`

---

## 3. Record schema

`ErrorRecord`:

- `error_id`: string, stable across runs (a good default is `err_<sha1(prcs_id + category)[:12]>`)
- `category`: one of `ERROR_CATEGORIES`
- `stage`: one of `ERROR_STAGES`
- `input`: dict of the record that produced the error (PRCS id + key fields)
- `prediction`: whatever the pipeline emitted (label list, caption string, sink hit, etc.)
- `ground_truth`: correct answer, when known
- `evidence`: KB / PPG / PRCS facts that should have driven the prediction
- `analysis`: short human note explaining the root cause (non-empty required)
- `tags`: optional list of ad-hoc labels for grouping (e.g. `"susi-noise"`, `"weak-label"`)
- `schema_version`: `1.0.0`

`.to_dict()` is JSON-ready and passes `validate_error_record`.

---

## 4. Summary aggregator

`summarize(records)` returns per-category and per-stage counts and fractional shares:

```json
{
  "total": 42,
  "by_category":   { "incorrect_pi_type": 12, "hallucinated_information": 5, ... },
  "by_stage":      { "knowledge_base": 12, "caption": 5, ... },
  "category_share":{ "incorrect_pi_type": 0.286, ... },
  "stage_share":   { "knowledge_base": 0.286, ... }
}
```

Malformed rows are silently dropped. `Phase 22` finalization surfaces the summary in `RESULTS.md`; Phase 21 uses it to route the biggest-share errors back to earlier phases.

---

## 5. Where errors get logged

Currently nowhere automatically. Three natural entry points:

- Phase 15 caption aggregator: on `passes == False` and specific axis failures, emit an `incomplete_caption` or `hallucinated_information` record.
- Phase 21 experiments matrix: on any A vs B condition where B loses at multiple metrics, log the category and evidence.
- G1 / G3 human review: annotators file `incorrect_practice` or `generic_caption` records with an `analysis` string.

Wiring is not part of Phase 16. The taxonomy plus the validator are the durable contract; wiring lives close to the emission site and can vary per phase.

---

## 6. What Phase 16 explicitly did NOT do

- Did not wire error logging into any pipeline stage. Cross-phase concern; belongs to Phase 21 / Phase 22.
- Did not add a UI for error triage. `step4_app` may grow one when needed.
- Did not add automatic clustering / dedup of records. That is a Phase 22 concern once we have enough real records.
- Did not enumerate a taxonomy of "why" reasons within each category. The `analysis` field is free text on purpose; a controlled sub-vocabulary would freeze prematurely.
