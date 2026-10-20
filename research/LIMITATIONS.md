# Limitations

Every limitation below is a real gap in this repository at the end of the Phase 0 through Phase 22 waterfall. Fixing them is future work.

## Data and labels

- **Weak labels only.** Practice and Purpose labels on `data/dataset/adppg.jsonl` come from the WeakLabeler (rule + SDK-prefix heuristics). Every metric derived from them carries `BANNER_BOOTSTRAP`. Gate G1 (human labels via Codr) is open. See [PACT_SCHEMA.md](PACT_SCHEMA.md) and [DATASET.md](DATASET.md).
- **No human reference captions on disk.** BLEU / ROUGE-L are honestly reported as "no references" until a reference set exists. See [CAPTION_EVAL.md](CAPTION_EVAL.md) §2.
- **No human ratings on disk.** The user-study packet exists (`step4_userstudy/`), but the ingester's promised statistical tests (Wilcoxon signed-rank / McNemar / Krippendorff alpha) are not implemented. The final human-eval gate is reserved for after this documentation set.

## Analysis and coverage

- **Taint is heuristic.** Over-approximates by design (DDG plus optional ICFG plus CALL-ARG plus CALL-RET). Precision knobs in `configs/ppg.yaml::taint` and `--precision` on `pipeline.run_corpus` mitigate the explosion on real APKs, but there is no soundness proof.
- **SuSi personal-info enrichment is sparse.** Only ~52 of 382 rows in `personal_info_results.csv` have a non-empty PI type; the rest fall back to SuSi category text. See [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) §4.
- **Permission map is hand-curated.** 17 entries mapping SuSi category to Android permission. A PScout-style trace from the framework source is planned but not implemented.
- **Sink catalog and egress heuristic are English-only.** A localized APK with sink method names in another language would slip the egress-verb heuristic entirely.
- **No source-file / line info.** Dalvik strips it. `code_snippet` and `involved_methods` stand in.

## Modelling

- **Threshold hardcoded to 0.5.** Per-label calibration is a real gap for imbalanced labels. Flagged in [CODEBASE_ARCHITECTURE.md §2](CODEBASE_ARCHITECTURE.md#2-current-broken-components).
- **CPU-only training.** No CUDA path yet.
- **Statement-token encoder is a hashing trick.** Commit `f73d177` documents it as an honest negative at bootstrap scale; a learned token embedding path is future work.
- **No confidence intervals on ablation deltas.** Single seed today.

## Evaluation

- **No BERTScore.** Deferred so the eval harness stays sklearn-only until Phase 21 numbers justify a torch import in eval. Slot exists in the aggregator's `text_metrics` block.
- **LLM-as-judge is not wired into the driver.** `step4_eval/caption_judge.py` runs standalone. Numbers get pulled into `RESULTS.md` by hand once produced.
- **Grounding verifier is heuristic.** Alias tables per PI category and sink type are conservative but not exhaustive. A caption that names the right data with a phrasing outside the alias set gets a false negative.
- **Forbidden-vendor list is three entries.** `admob`, `adsense`, `doubleclick`. Widening is a config change; the current list catches only the obvious hallucinations.

## Reproducibility

- **`legacy/document_analysis/` scripts are frozen.** Hard-coded absolute paths and a missing `esalib/` Java tool mean the CSV inputs to the KB cannot be regenerated on this checkout. Only the pre-computed CSVs are usable.
- **Real-APK smoke test is skipped without androguard.** Fixture-based coverage stays green in the lean CI profile; real APKs require the extras install.

## Scope reservations that are not bugs

- **Human evaluation is deferred to the final gate.** Every automated metric explicitly stops short of it.
- **`FINAL_EXPERIMENTS.md::plan_runs` produces empty metrics** by design. Numbers appear only in real `manifest.json` files.
- **The UI is not the research.** `step4_app` is a static site meant for reader inspection, not a research artifact by itself.
- **`data/apg/` and other empty placeholders remain on disk.** Phase 22 archive moves (proposed in [CODEBASE_ARCHITECTURE.md §6](CODEBASE_ARCHITECTURE.md#6-recommended-architecture)) are not landed in this documentation waterfall; they belong to a separate refactor pass.

## Known drift

- README top banner still says `69 green`. Actual count as of the end of this waterfall is `260 green`. Fixing the README banner is a Phase 22 finalization task not landed here to keep the doc waterfall small.
- The recon called out three serializations of each PRCS (`data/prcs/prcs_<id>.json`, `data/dataset/adppg.jsonl`, `data/dataset/codr_export/prcs_<id>.json`). The Codr export stays because it is what the annotation tool consumes; a Phase 22 cleanup would collapse it if annotation moves to a JSONL sink.

## What is not a limitation

- The synthetic fixtures. They exist to make CI reproducible; every experiment quotes numbers from real corpora, not from fixtures.
- The two-arm ablation in `step2_convgnn/ablation.py`. It answers "does the overlay help" cleanly; the eight-arm matrix is where the broader question lives.
- The `research/` documentation structure itself. If a future contributor disagrees with the schema, editing the module docs and the tests is a single-file change.
