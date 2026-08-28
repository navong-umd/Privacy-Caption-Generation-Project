# End-to-End Pipeline

_Phase 17 deliverable. The canonical run command and every artifact it produces. Driver at [`pipeline/run_pipeline.py`](../pipeline/run_pipeline.py); corpus variant at [`pipeline/run_corpus.py`](../pipeline/run_corpus.py); tested by [`tests/test_pipeline_e2e.py`](../tests/test_pipeline_e2e.py) and [`tests/test_pipeline_artifacts.py`](../tests/test_pipeline_artifacts.py)._

One command to go from an APK (or a fixture APG) to every artifact the research uses. All intermediates stay on disk under one output root.

---

## 1. The command

Fixture (no androguard needed):

```
python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run
```

Real APK (needs `pip install -r requirements-apk.txt`):

```
python -m pipeline.run_pipeline --apk path/to/app.apk --out data/run
```

Corpus (multi-APK, precision-tuned taint):

```
python -m pipeline.run_corpus --apks data/corpus_az --out data/corpus_run --precision
```

Flags on the single-APK driver:

- `--apg DIR` or `--apk FILE`: one is required. `--apk` runs the APG adapter first.
- `--out DIR`: run root; every stage writes under this directory. Default `data/run`.
- `--no-train`: skip ConvGNN training (useful in lean CI or when torch is missing).
- `--epochs N`: override the trainer's epoch count (default 40).
- `--neo4j`: also load the PPG into a live Neo4j at the URI in `configs/ppg.yaml`.
- `--precision`: tighten taint for large real APKs (`follow_icfg=false`, `max_paths_per_source=25`). Writes a derived `ppg.precision.yaml` next to the run.

---

## 2. Stage-by-stage artifact map

Everything below sits under `<out>/`:

| Stage | Directory | Files |
|-------|-----------|-------|
| 1. APK to APG (only when `--apk`) | `apg/` | `{AST,MCG,ICFG,DDG}_{nodes,edges}.csv`, `APG_META.json` |
| 2. PPG overlay | `ppg/` | `PPG_nodes.csv`, `PPG_edges.csv`, `ppg.pkl`, `ppg.graphml`, `taint_paths.json` |
| 3. PRCS slices | `prcs/` | `prcs_<id>.json` per slice, `prcs_index.csv` |
| 4. ADPPG dataset | `dataset/` | `adppg.jsonl`, `labels.csv`, `splits.json`, `codr_export/*.json` |
| 5. ConvGNN | `convgnn/` | `best.pt`, `metrics.csv` (skipped cleanly when torch is missing) |
| 6. Captions | `captions/` | `captions.json`, `captions.csv` |
| 7. Policy | `policy/` | per-app `notice.md`, `policy.md`, `policy.json` |
| 8. Evaluation | `eval/` | `eval_report.json`, `eval_report.md`, `caption_rating_sheet.csv` |
| 9. Human study kit | `userstudy/` | `study_tasks.json`, `study_packet.md`, `ratings_template.csv` |
| 10. Nutrition app | `app/` | `index.html` + per-package pages |

Nothing overwrites a prior stage's output. A partial rerun is safe as long as upstream directories are consistent.

---

## 3. Configs consumed

- `configs/ppg.yaml`: source catalog + sink catalog paths, taint knobs, LINDDUN map. Precision mode writes a derivative next to the run.
- `configs/sinks.yaml`: sink rule catalog + egress heuristic.
- `configs/convgnn.yaml`: model, optimizer, epochs default.
- `configs/llm.yaml`: caption provider (default `mock`).
- `configs/weak_labels.yaml`: rule labeler + split ratios and seed.
- `configs/sdk_catalog.yaml`: third-party SDK prefixes for the purpose head.
- `configs/gdpr_ccpa_map.yaml`: policy assembly.

Override any of the above with a non-default path via the driver's CLI (see `pipeline.run_pipeline --help`).

---

## 4. What the summary dict returns

`pipeline.run_pipeline.run_pipeline(...)` returns a dict a caller can log or assert on:

- `ppg`: `{sources, sinks, taint_paths, nodes, edges}` (from `PPGBuilder.summary()`)
- `prcs`: number of slices produced
- `dataset`: `{records, weak, human, splits: {train, val, test}}`
- `convgnn`: `{is_weak, best_val_macro_f1}` or `{skipped: reason}` if torch was missing
- `captions`: number of captions produced
- `policy_apps`: number of apps that got policy artifacts
- `eval`: `{bootstrap, policy_completeness}`
- `userstudy_tasks`: number of rating tasks in the human-study packet
- `nutrition_app`: `{apps, index}` (index is the static site entry)

---

## 5. Two invariants tested

The existing e2e test already asserts stage counts + key file paths. Phase 17 adds a small companion test that asserts the artifact catalog above matches on-disk output after a fresh run.

1. Every directory listed in section 2 (excluding `apg/` for a fixture run and `convgnn/` when torch was skipped) is non-empty on disk.
2. Every top-level artifact filename listed in section 2 exists.

Owners of a downstream stage can add narrower invariants next to their code without duplicating what the e2e test asserts.

---

## 6. What Phase 17 explicitly did NOT do

- Did not rename the driver. The plan's example was `python -m pipeline.run --apk ... --output ...`; the repo already uses `python -m pipeline.run_pipeline --apk ... --out ...`. Renaming would break every existing script; the existing name is documented and stable.
- Did not add a JSON schema for the `run_pipeline` summary dict. Contents are small and easy to inspect; a formal schema is a Phase 22 concern.
- Did not add automatic aggregation of the Phase 15 caption aggregator into `eval/`. The aggregator is standalone by design; wiring it into `eval/eval_report.json` is a follow-on task once Phase 21 knows which fields it wants highlighted.
- Did not touch the corpus driver's `--apks` semantics or its precision defaults.
