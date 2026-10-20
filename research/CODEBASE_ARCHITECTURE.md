# Codebase Architecture

_Phase 0 deliverable. Source: 12-agent parallel reconnaissance, workflow `wf_69d16800-c79`, 2026-08-28._

> Snapshot from 2026-08-28. Since then the legacy trees moved: `Static Code Analysis Module/` to `legacy/static_analysis/`, the `Document Analysis Module/` scripts to `legacy/document_analysis/` and its CSV/TXT data to `data/knowledge_base/`, `PriGenLocal/` was removed (empty submodule stubs, orphan APKs, decompiled third-party code), and the old `docs/` notes to `legacy/notes/`. Paths below are updated where the file still exists.

Branch: `Ali-F/Branch` (forked from `stage4-ppg-convgnn`). 79 tests green as of the last committed state on the parent branch. Pipeline runs end-to-end on a committed synthetic fixture and on a real 8-APK AndroZoo corpus (10,721 PRCS across 7 apps).

---

## 1. Current Working Pipeline

The canonical flow is **APK → APG → PPG → PRCS → ADPPG → RGCN → Caption → Policy → Eval/App**. Two drivers wire it together:

- Single app: `pipeline/run_pipeline.py` (`python -m pipeline.run_pipeline --apk <path> --out <dir>`)
- Corpus: `pipeline/run_corpus.py` (`python -m pipeline.run_corpus --apks <dir> --out <dir>`) — processes each APK in-memory to keep PPG pickles off disk, then aggregates into one ADPPG.

Stage-by-stage (file → produces → consumed by):

| # | Stage | Canonical file | Output | Downstream |
|---|-------|---------------|--------|-----------|
| 1 | APK disassembly + APG | `adapters/run_apg_csv.py` (uses `androguard`) | `{AST,MCG,ICFG,DDG}_{nodes,edges}.csv` + in-memory `pplib.apg_model.APG` | Stage 4 |
| 2 | APG schema/IO | `pplib/apg_model.py`, `pplib/schema.py` | column contract + `load_apg`/`write_apg` | all downstream |
| 3 | PPG overlay | `stage4_ppg/build_ppg.py` (+ `catalogs.py`, `taint.py`, `semantics.py`) | `PPG_{nodes,edges}.csv`, `ppg.pkl`, `ppg.graphml`, `taint_paths.json` | PRCS, Neo4j viewer |
| 4 | PRCS slicing | `step2_prcs/extract_prcs.py` | `data/prcs/prcs_<id>.json` + `prcs_index.csv` | dataset assembly |
| 5 | ADPPG dataset | `step2_dataset/build_dataset.py` (+ `weak_labeler.py`) | `adppg.jsonl`, `labels.csv`, `splits.json` (APK-grouped), `codr_export/*.json` | RGCN, captions |
| 6 | RGCN classifier | `step2_convgnn/train.py` (+ `data.py`, `model.py`, `metrics.py`) | `best.pt`, `metrics.csv` | eval, caption predictions overlay |
| 7 | Captions | `step3_caption/generate.py` (+ `llm_interface.py`, `code2seq_baseline.py`) | `captions.json`, `captions.csv` | policy, eval, nutrition app |
| 8 | Policy | `step3_policy/assemble.py` (+ `configs/gdpr_ccpa_map.yaml`) | per-app `notice.md`, `policy.md`, `policy.json` | eval, nutrition app |
| 9 | Auto eval | `step4_eval/evaluate.py` (+ `text_metrics.py`) | `eval_report.json/md`, `caption_rating_sheet.csv` | — |
| 10 | User study scaffold | `step4_userstudy/build_study.py` | `study_tasks.json`, `ratings_template.csv`, `protocol.md`, `consent_template.md` | G3 gate |
| 11 | Nutrition Facts app | `step4_app/build_app.py` (+ `nutrition.py`) | static `index.html` + per-package pages | — |

Shared spine: every module goes through `pplib/io_utils.py` (YAML/JSON/logging) and `pplib/schema.py` (label constants, column names, `BANNER_WEAK`/`BANNER_BOOTSTRAP`/`BANNER_JUDGE`).

Configs live in `configs/`: `ppg.yaml`, `sinks.yaml`, `convgnn.yaml`, `llm.yaml` (default `provider: mock`), `weak_labels.yaml`, `sdk_catalog.yaml`, `gdpr_ccpa_map.yaml`, `queries.cypher`, `neo4j.grass`.

Neo4j is an **optional viewer** (`stage4_ppg/neo4j_loader.py` + `stage4_ppg/cypher_runner.py` + `DISPLAY.md`). Ground truth is always the CSV/pkl/graphml on disk.

---

## 2. Current Broken Components

**Empty or unrunnable:**

- `PriGenLocal/PDroid/` and `PriGenLocal/code2seq/` — both are empty directories. No module, no checkpoint, no vocab, no entry point.
- `esalib/` — empty. `utils_main_api_Des_to_Info_final.py` shells out to `esalib/run_analyzer.bat` which does not exist; re-running the API→PI extraction is impossible without restoring the Java ESA tool.
- `legacy/document_analysis/*.py` — hard-coded absolute paths `<user-home>\...` in every script. Only the pre-computed CSVs under `data/knowledge_base/` are usable.
- `legacy/static_analysis/consolidated/androguard_analysis_APG_III_Update1Fixed_14.py` and the five `MCG_reachability*` variants — same hard-coded personal absolute paths (since replaced with folder-relative paths) and require a running Neo4j at `bolt://localhost:7687`. Cannot execute in this checkout.
- `data/apg/` — empty placeholder, yet `configs/ppg.yaml` still points `paths.apg_dir: data/apg`. Real runs write to `data/apg_real/` or `data/apg_fdroid/`.
- `data/dataset/splits.json` — ships with `test: []` (synthetic bootstrap has no test split). Real eval requires `data/dataset_large/` or `data/eval_run/`.

**Known pipeline gaps that block the golden path from being fully honest:**

- **`step3_caption/code2seq_baseline.py` is an untrained placeholder** — `BASELINE_TAG = "code2seq-baseline (untrained placeholder)"`. Regex-over-method-tokens template. No real prior-work baseline exists.
- **No human reference captions on disk.** `step4_eval/evaluate.py::evaluate_captions` therefore always returns "no references" and BLEU-4/ROUGE-L never actually run.
- **G1 (human PAcT labels) and G3 (human user study) are open.** All labels driving the current numbers are `WEAK`. `BANNER_BOOTSTRAP` fires end-to-end.
- **`step4_eval/caption_judge.py` is not wired into either pipeline driver.** G2 numbers in `legacy/notes/RESULTS.md` come from a manual out-of-band invocation.
- **Real LLM provider paths are untested** (`_ApiProvider.generate`, `_llm_score`, `_llm_pairwise` all carry `# pragma: no cover`).
- **Neo4j credentials were baked as literals** in `stage4_ppg/neo4j_loader.py`. Since fixed: `connection_settings` reads `NEO4J_URI` / `NEO4J_USER` / `NEO4J_PASSWORD` (password never from config).
- **Taint recall vs precision is unresolved.** Default `ppg.yaml` uses the recall settings (`follow_icfg: true`, unbounded flows per source, CALL-RET propagation to every callsite of any tainted method). `pipeline._precision_config` writes a `ppg.precision.yaml` at runtime only when `--precision` is passed. TAINT_FLOW edges carry no per-edge provenance to filter after the fact.
- **Device hardcoded to CPU** in `step2_convgnn/train.py:82`; no CUDA path.
- **Threshold hardcoded to 0.5** in `step2_convgnn/train.py::_predict`; no per-label calibration despite imbalanced PAcT labels.

---

## 3. Duplicate Implementations

| Concern | Canonical | Legacy / Duplicate | Notes |
|---------|-----------|--------------------|-------|
| APK → APG disassembly | `adapters/run_apg_csv.py` | `legacy/static_analysis/consolidated/androguard_analysis_APG_III_Update1Fixed_14.py` (+ 5 `MCG_reachability*` variants + `androguard_analysis_APG_Bar.py`) | Adapter is a line-copy mirror of the legacy script. Only `pplib/schema.py` enforces they stay in sync — no test asserts it. |
| API → PI knowledge base | `data/knowledge_base/personal_info_results.csv` (frozen CSV, canonical input to `stage4_ppg/catalogs.py`) | `legacy/document_analysis/utils_main_api_Des_to_Info{.py, _Save.py, _Save_Test.py, _final.py}` — four near-clones; `Sourcecode/Other/api_Des_to_Info_Test.py`, `personal_Info_Ext.py`, `retrieve_API_Des.py` are byte-identical (5031 bytes) | The `.py` scripts are frozen; only the produced CSV is load-bearing. |
| Code2Seq baseline | `step3_caption/code2seq_baseline.py` (in-repo untrained placeholder) | `PriGenLocal/code2seq/` (empty) | PriGenLocal is dead reference material. |
| PRCS artifacts | `data/dataset/adppg.jsonl` (one line per PRCS with labels) | `data/prcs/prcs_<id>.json` + `data/dataset/codr_export/prcs_<id>.json` | Three serializations of each PRCS. `codr_export/` is redundant unless Codr requires one-file-per-record. |
| Sink egress catalog | `stage4_ppg/catalogs.py::SinkCatalog` (reads `configs/sinks.yaml`) + heuristic verb list | Legacy `MCG_reachability*` scripts embed their own sensitive-API list | Legacy is unreferenced. |
| Reachability from entry to sensitive API | `stage4_ppg/taint.py` (in-memory BFS over DDG/ICFG/CALLS) | `androguard_analysis_MCG_reachability{,_Feasible,_Full,_Update}.py` (Neo4j BFS) | Legacy is unreferenced. |
| SuSi source/sink parsing | `stage4_ppg/catalogs.py::SourceCatalog._load_susi` (consumer) + `data/knowledge_base/formatted_sources.csv` (checked-in artifact) | `legacy/document_analysis/structure_input_data.py` (producer, frozen) | Not truly redundant — one produces, one consumes — but both know the SuSi schema. |
| ConvGNN training call sites | `step2_convgnn.train.train()` invoked from `pipeline/run_pipeline.py`, `pipeline/run_corpus.py`, `run_g1g2.py` (since removed) | — | Three call sites with drifted defaults (epochs 40 vs 40 vs 30; out dirs `convgnn/` vs `convgnn/` vs `model/`). No shared wrapper. |
| Rating sheet format | `step4_eval/evaluate.py::evaluate_captions` → `caption_rating_sheet.csv` (solo grading) | `step4_userstudy/build_study.py` → `ratings_template.csv` (blind A/B) | Complementary instruments; overlapping columns (`accuracy_1_5`, `clarity_1_5`, `completeness_1_5`); no shared schema module. |
| Evidence dict for downstream text | `step3_caption/generate.py::_evidence(rec)` | `step3_policy/assemble.py::_app_section_data` / per-fact dict | Same keys, two implementations; a PRCS field rename must be made in both. |
| Weak-label banner rendering | `step3_caption/generate.py` | `step3_policy/assemble.py` | Both consume `pplib.schema.BANNER_WEAK` but decide independently how to render. |
| Runtime derived configs | Committed `configs/ppg.yaml` | Auto-generated `data/corpus_run/ppg.precision.yaml` (from `pipeline._precision_config`) | Coexist next to each other with no marker; invites confusion. |
| Output roots | `data/run/` (single-app) | `data/corpus_run/` (corpus), plus `data/*_large/` synthetic siblings, plus mock/`_llm` variant pairs (`captions/` vs `captions_llm/`, etc.) | Provenance not recorded. |
| APG source folders | `data/apg_real/` (AndroZoo), `data/apg_fdroid/` (F-Droid) | `data/apg/` (empty placeholder still named in `configs/ppg.yaml`) | — |

Directory-name overload: "Stage 3" refers to `legacy/document_analysis/` (API-docs → PI) in the old plan and `step3_caption/` + `step3_policy/` (captions + policy) in the current pipeline. These do entirely different jobs.

---

## 4. Reusable Components

Preserve and pull into the canonical pipeline (or, where already inputs, freeze the artifacts and cite provenance):

**From `legacy/document_analysis/` (frozen, input-only):**
- `output/personal_info_results.csv` — NL-derived PI types for Android APIs. Tier 3 input to `stage4_ppg/catalogs.py::SourceCatalog`.
- `output/formatted_sources.csv` and `output/formatted_sinks.csv` — SuSi parsed catalogs. Tier 2 input.
- `input/CatSources_v0_9.txt`, `input/CatSinks_v0_9.txt` — raw SuSi corpus (recover if the CSVs need regenerating).
- `Sourcecode/utils_main_api_Des_to_Info_final.py`, `utils_doc_des.py`, `utils_clean_method_name.py`, `utils_dpr_score.py`, `structure_input_data.py` — the pipeline that produced the CSVs. **Fix hard-coded paths + restore `esalib/`** to make re-runnable.

**From `legacy/static_analysis/`:**
- `input/APK/sample.apk` — the only checked-in small APK. Wire into a real-APK adapter test.
- `legacy/static_analysis/consolidated/androguard_analysis_APG_III_Update1Fixed_14.py` — retain as **reference** for the exact disassembly semantics the mirror in `adapters/run_apg_csv.py` must preserve. Should become the fixture the mirror is diffed against in CI.
- The SuSi source-key → callee-normalization comments in `parse_invoke_callee` / `extract_written_variables` / `extract_read_variables` — these are the ground truth for `adapters/run_apg_csv._parse_callee` / `_written_var` / `_read_vars`.

**From `PriGenLocal/`:**
- `test_apk/F-Droid/PRCS_*.java`, `test_apk/F-Droid_1/PRCS_*.java`, `test_apk/TikTok Lite/PRCS_*.java` — ~494 decompiled per-method Java snippets. Potentially useful as seed source→caption pairs **if** G1 annotation produces matching captions; otherwise archive.
- Nothing else. `PDroid/` and `code2seq/` are empty. `test_apk/sample.apk` and `test_apk/tiktok.apk` are unreferenced orphans.

**In-repo, already reusable but not yet reused everywhere:**
- `pplib/schema.py` — the single-source column and label contract. Extend to formally version the PRCS JSON schema.
- `pplib/io_utils.py` — the only sanctioned YAML/JSON/logging path. All new code should route through it.
- `pplib/apg_model.py::APG` dataclass + `load_apg`/`write_apg` — the exchange format between disassembly and PPG. Do not fork.
- `stage4_ppg/semantics.py::WhatItDoesCache` — the rule-then-LLM enrichment with `what_it_does_src` provenance. Reuse for any node-level explanation elsewhere.
- `step4_eval/text_metrics.py` — stdlib BLEU-4 + ROUGE-L. Keep as the zero-dep baseline; add BERTScore later behind an optional import.

---

## 5. Missing Research Components

Against the 22-phase plan, the following are not present:

**Data / reproducibility infrastructure**
- **Reproducible environment (Phase 1).** No `pyproject.toml`, no lockfile, no Dockerfile, no CI workflow (`.github/workflows/` is absent), no `tox.ini`. Only `requirements-stage4.txt`. Pipeline reproducibility depends on the reader manually installing pinned wheels on CPython 3.14.
- **Manifest for `data/` (Phase 1-2).** Everything except `data/fixtures/` is gitignored with no README explaining what any subdir should hold, how it was produced, or where to download it.
- **Provenance metadata for the corpus (Phase 2).** `data/androzoo/` and `data/corpus_az/` have no cadence, no license note, no `NOTICE`/attribution for the F-Droid and TikTok Lite decompiled Java under `PriGenLocal/test_apk/`.

**Labels and evaluation (Phases 4-8, 15-18)**
- **Human PAcT labels (G1).** Only WEAK labels exist. 13-row LLM two-pass disagreement shortlist (`data/_review_shortlist.*`) awaits human check.
- **Human reference captions.** Zero on disk. Blocks BLEU-4 / ROUGE-L from running honestly.
- **Human ratings (G3).** `step4_userstudy` has the instrument but no returned sheets. `ingest_ratings.py` computes a per-condition mean and a pairwise |Δ| proxy; the **Wilcoxon signed-rank / McNemar / Krippendorff's α** promised in `protocol.md` are unimplemented.
- **Trained Code2Seq baseline.** Only the untrained placeholder. Blocks any honest A/B against prior work.
- **Third ablation arm (code-only classifier).** `step2_convgnn/ablation.py` compares only FULL PPG vs APG-only. No code-only baseline.
- **Statistical envelope on ablation.** Single seed, single run, no confidence interval.
- **Per-label threshold calibration** and **per-edge taint provenance** are both missing (see Section 2).

**Modelling (Phases 9-14)**
- **Learned token encoder.** `TOKEN_HOOK_DIM=8` slots reserved in `step2_convgnn/data.py`, but the only implementation is an MD5 hashing trick. Commit `f73d177` documents it as an honest-negative result at bootstrap scale. A real learned token embedding path (`code2vec`-style path contexts, `codeBERT`, or `tokenizers` + `nn.Embedding`) is absent.
- **CUDA / distributed training path** (Phase 14).
- **Real-APK adapter tests** (Phase 12). No test invokes `adapters/run_apg_csv.py` against the local APK named by `PPCAP_SAMPLE_APK`.
- **Live Neo4j integration test** (Phase 13). `neo4j_loader.py` is entirely untested; Cypher queries are lint-only.

**Downstream products (Phases 19-22)**
- **Interactive Nutrition Facts app.** `step4_app/build_app.py` produces a stdlib-only static site — no filtering, sorting, search, or query execution UI. Neo4j Cypher is emitted as text to paste manually.
- **Grounded-caption verifier.** Post-hoc check that a returned LLM caption actually mentions the PI/sink/purpose in the evidence dict. Only the MockProvider is deterministically grounded; real providers can hallucinate silently.
- **API → permission mapping from analysis** (planned in `legacy/document_analysis/NOTES.txt`). Currently only a hand-curated `permission_map` in `configs/ppg.yaml`.
- **PScout-style permission trace** — never implemented.

---

## 6. Recommended Architecture

Keep the current module boundaries — they are clean and 1:1 with the pipeline stages. Consolidate around what works; do not rewrite.

```
Privacy-Caption-Generation-Project/
├── pplib/                       # SHARED SPINE — do not fork
│   ├── schema.py                # + PRCS JSON schema (new)
│   ├── io_utils.py
│   └── apg_model.py             # APG dataclass + load/write
│
├── adapters/                    # APK -> APG (single mirror of legacy)
│   ├── run_apg_csv.py
│   └── fetch_androzoo.py, fetch_fdroid.py
│
├── stage4_ppg/                  # APG -> PPG (canonical, sole builder)
│   ├── build_ppg.py, catalogs.py, taint.py, semantics.py
│   └── neo4j_loader.py, cypher_runner.py     # optional viewer
│
├── step2_prcs/                  # PPG -> PRCS
├── step2_dataset/               # PRCS -> ADPPG + splits + G1 sheets
├── step2_convgnn/               # ADPPG -> RGCN (train, ablate, predict)
│
├── step3_caption/               # PRCS + preds -> captions (+ code2seq baseline)
├── step3_policy/                # captions + PRCS -> notice.md / policy.md
│
├── step4_eval/                  # auto metrics + LLM-as-judge
├── step4_userstudy/             # G3 instrument + ingestion
├── step4_app/                   # static Nutrition Facts site
│
├── pipeline/                    # thin CLI drivers ONLY
│   ├── run_pipeline.py          # single APK/APG
│   └── run_corpus.py            # multi-APK -> pooled ADPPG
│
├── configs/                     # canonical YAML/Cypher/GraSS
├── data/
│   ├── fixtures/                # committed synthetic APG
│   ├── corpus/, corpus_az/      # APK inputs (gitignored)
│   ├── run/, corpus_run/        # blessed output roots
│   └── starter/, eval_run/      # human-label packages (G1/G2)
├── tests/                       # pytest suite (79 tests)
└── archive/                     # NEW
    ├── PriGenLocal/             # move here (dead)
    ├── Document_Analysis_Legacy_Scripts/   # frozen .py, hard-coded paths
    └── Static_Code_Analysis_Legacy/         # 6 unreferenced androguard variants
```

**Concrete consolidation moves:**

1. **Move `PriGenLocal/` under `archive/`** with a one-line `README.md` explaining it is legacy. Delete `PriGenLocal/PDroid/` and `PriGenLocal/code2seq/` (empty stubs). Delete `PriGenLocal/test_apk/sample.apk` and `tiktok.apk` (orphans).
2. **Move the six unreferenced legacy androguard scripts** (`legacy/static_analysis/consolidated/androguard_analysis_APG_III_Update1Fixed_14_Bar.py`, `androguard_analysis_APG_Bar.py`, all four `androguard_analysis_MCG_reachability*.py`) under `archive/Static_Code_Analysis_Legacy/`. Keep `androguard_analysis_APG_III_Update1Fixed_14.py` in place as the mirror reference, and add a CI test that diffs the parse helpers against `adapters/run_apg_csv.py`.
3. **Move the four `utils_main_api_Des_to_Info*` clones** and the three byte-identical `Sourcecode/Other/*` duplicates under `archive/Document_Analysis_Legacy_Scripts/`. Keep only `utils_main_api_Des_to_Info_final.py` as the canonical regenerator (path-fixed).
4. **Freeze `data/knowledge_base/*.csv` and `data/knowledge_base/CatS*.txt` as versioned data inputs**, cited by hash in `configs/ppg.yaml`. Update the paths in the config to their new home under `data/knowledge_base/`.
5. **Add `pplib/prcs_schema.py`** — a versioned dataclass/JSON schema for the PRCS record. Have `step2_prcs`, `step2_dataset`, `step3_caption`, `step3_policy`, and `step4_eval` all import it. Kill the two independent evidence-dict constructors.
6. **Collapse `data/prcs/` + `data/dataset/codr_export/` into a single serialization**; keep `adppg.jsonl` as the primary and generate the Codr-per-file view on demand.
7. **Fix `configs/ppg.yaml`**: point `paths.apg_dir` at a real dir, add the missing `neo4j:` section documented in `DISPLAY.md`, split the six unrelated concerns into files with header comments.
8. **Delete `data/apg/`** (empty).
9. **Promote `pipeline/_precision_config` to `pplib/precision.py`** so the private cross-module import between the two drivers goes away. Add a single `train_convgnn(...)` wrapper the three call sites (`run_pipeline`, `run_corpus`, `run_g1g2`) share.
10. **Wire `step4_eval/caption_judge.py` into `pipeline/run_pipeline.py` step 7b** behind a `--judge` flag so G2 numbers come from the same command that produces everything else.
11. **Add a real-APK adapter smoke test** using the local APK named by `PPCAP_SAMPLE_APK`, guarded by `pytest.importorskip("androguard")`.
12. **Add per-edge provenance to `TAINT_FLOW`** (which of DDG-only / ICFG / CALL-ARG / CALL-RET produced it) so downstream consumers can filter without a config rebuild.

---

## Smallest Defensible First Milestone

**Goal: `git clone` → `<one command>` → 79 green tests on any machine.**

Concretely: **make the environment reproducible and CI-verified.** Everything else in the plan (G1 labels, trained Code2Seq, real-APK tests, LLM judge wiring, ablation confidence intervals) is currently blocked by the fact that a fresh contributor cannot reliably reproduce the current numbers. This milestone unlocks every other phase.

Scope (nothing outside this list):

1. **Add `pyproject.toml`** pinning the wheels currently in `requirements-stage4.txt` (`torch==2.12.1`, `torch_geometric==2.8.0`, `pandas==2.3.3`, `numpy==2.3.5`, `networkx==3.6.1`, `PyYAML==6.0.3`, `pytest==8.4.2`, `androguard==4.1.4`). Declare CPython 3.14 as the supported interpreter.
2. **Add a `uv.lock` (or `poetry.lock`)** so the environment is bit-reproducible.
3. **Add `Dockerfile`** built on `python:3.14-slim` with the lockfile installed. Entry point runs `pytest tests/ -q`.
4. **Add `.github/workflows/ci.yml`** that (a) builds the image and (b) runs `pytest tests/ -q` on push. This alone will surface the current README ↔ FINAL_REPORT test-count mismatch (69 vs 79) as a build fact.
5. **Add `data/README.md`** with a one-line description per subdirectory, marking which are checked in (`data/fixtures/`) and which are regenerable by which command.
6. **Fix the two config drifts that block a clean run:** point `configs/ppg.yaml -> paths.apg_dir` at `data/fixtures/synthetic_apg_large`, and add the `neo4j:` section `DISPLAY.md` promises.
7. **Register `pytest.importorskip` on the two tests that need heavy deps** (`test_step2_convgnn.py`, `test_ablation.py`, the torch case in `test_step4_eval.py`) so CI can also run a lean profile without torch.

Explicitly out of scope for this milestone: any model change, any new labels, any refactor of the module layout in Section 6, any of the `archive/` moves. Those come next, but only after CI is green on a clean clone.

---

## Evidence trail

- Workflow: `wf_69d16800-c79` (12 agents, 297 tool uses, 885K subagent tokens, 541 s wall).
- Prior progress captured in commits `4707c01…f73d177` on parent branch `stage4-ppg-convgnn` and in `legacy/notes/FINAL_REPORT.md`, `legacy/notes/RESULTS.md`.
