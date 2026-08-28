# Performance Analysis

_Phase 20 deliverable. Timing helper in [`pplib/timing.py`](../pplib/timing.py); tests in [`tests/test_timing.py`](../tests/test_timing.py). Actual numbers land in Phase 21 (RESULTS.md)._

Only after correctness. This phase drops in the measurement infrastructure so Phase 21 can report timing + memory without inventing a new harness.

---

## 1. What to measure

The plan lists eight measurements. Each maps onto one pipeline stage:

| Metric | Stage | Instrument |
|--------|-------|-----------|
| APK analysis time | `adapters/run_apg_csv` | `stage_timer("apk_analysis", rows)` around `run_apg_csv(...)` |
| Graph construction time | `stage4_ppg/build_ppg` | `stage_timer("ppg_build", rows)` around `build_ppg(...)` |
| Graph size | Same stage | `extra["ppg_nodes"] = builder.summary()["nodes"]` etc. |
| Memory consumption | All stages | `stage_timer` uses `tracemalloc` and records `peak_kb` |
| PRCS extraction time | `step2_prcs/extract_prcs` | `stage_timer("prcs_extract", rows)` |
| Training time | `step2_convgnn/train` | `stage_timer("convgnn_train", rows)` |
| Inference time | Same or `step4_eval/evaluate` | `stage_timer("convgnn_infer", rows)` |
| Caption generation latency | `step3_caption/generate` | `stage_timer("captions", rows)` per PRCS if per-caption latency is wanted |

---

## 2. The helper

```python
from pplib.timing import stage_timer, write_timing_report

rows = []
with stage_timer("ppg_build", rows) as extra:
    builder = build_ppg(apg_dir, cfg, out_dir)
    extra["ppg_nodes"] = builder.summary()["nodes"]
    extra["ppg_edges"] = builder.summary()["edges"]
    extra["taint_paths"] = builder.summary()["taint_paths"]

write_timing_report(rows, out / "timing.json")
```

`stage_timer(stage, rows, measure_memory=True)`:

- Times the block with `time.perf_counter()`.
- Measures peak Python heap via `tracemalloc` unless `measure_memory=False` (skip when the caller is already tracing memory).
- Yields a mutable `extra` dict the caller can populate with stage-specific counts.
- Appends one `StageTiming` row on exit whether the block raised or not; re-raises the exception unchanged.

`write_timing_report(rows, path)` produces JSON with sorted keys so two runs on the same input diff cleanly.

`summarize(rows)` groups by stage and returns `{total_wall_seconds, by_stage: {stage: {count, wall_seconds, peak_kb_max, errors}}, n_rows}`.

---

## 3. Where to wire it

Not yet wired. Phase 20 lands the helper. Concrete wiring:

- `pipeline/run_pipeline.py`: wrap each stage call in a `stage_timer(...)` and write `timing.json` next to `eval_report.json`.
- `pipeline/run_corpus.py`: same, per-APK, aggregated at the corpus level.
- `step2_convgnn/train.py`: wrap the training loop and record `epochs`, `best_val_macro_f1`, and any per-epoch subtotals.

Every wire-up is a small local change (add rows list at the top of the driver, wrap stage calls, dump the report at the end). Consumers of `timing.json` include Phase 21 comparisons and Phase 22 finalization.

---

## 4. Reproducibility caveats

- Wall clock varies with hardware and load. Report medians across a small `k` (5, 10) for numbers that go into a paper.
- `tracemalloc` measures Python-visible allocation, not RSS. Native memory (androguard, torch) is invisible. Note this in `RESULTS.md` and use `/usr/bin/time -v` alongside when native memory is the story.
- `time.perf_counter()` is monotonic so short stages report zero-safe deltas; there is no need to add manual epsilon guards.

---

## 5. What Phase 20 explicitly did NOT do

- Did not run any timing. The plan says measure only after correctness; correctness is what Phases 0 through 19 established.
- Did not wire the timer into any driver. Wiring is a per-driver concern with narrow test surface; the helper stays reusable across all of them.
- Did not add resource limits or per-stage caps. Those belong in configs, not in the timer.
- Did not add asynchronous or parallel measurement. Every current pipeline stage is single-threaded; adding concurrent instrumentation before there is a real workload is scope creep.
