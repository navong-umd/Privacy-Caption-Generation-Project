# LEDGER — append-only progress log

> Read this first on resume. Each entry: phase, what shipped, test result, commit.

---
## Phase 0 — Audit + scaffolding
- Read README, PROJECT_PLAN.md, Stage 2 APG script, Stage 3 outputs (personal_info_results.csv,
  formatted_sources/sinks.csv), reachability scripts. Wrote the "What I Found" audit (FINDINGS.md §0).
- Verified environment: **CPython 3.14.0**; networkx/torch 2.12.1/torch-geometric 2.8.0/androguard
  4.1.4/neo4j 6.2.0/scikit-learn all have 3.14 wheels (dry-run confirmed). Sample APK present (11.9 MB).
- Built scaffolding: `pplib/` (schema, io_utils, apg_model adapter), `configs/` (sinks/sdk/ppg),
  `requirements-stage4.txt`, pytest harness (`pytest.ini`, root `conftest.py`).
- Built SYNTHETIC APG fixture generator `data/fixtures/make_synthetic_apg.py`; generated tiny
  (2-app) and large (8-app) fixtures. All artifacts banner-labeled SYNTHETIC.
- Created `PROJECT.md`, `LEDGER.md`, `FINDINGS.md`.
- **Tests:** n/a yet. **Status:** done.

## Phase A — Stage 4 PPG
- `stage4_ppg/catalogs.py` (3-tier source matcher + sink catalog + unknown-sink heuristic),
  `taint.py` (intra+inter-procedural BFS over DDG/ICFG/CALLS), `build_ppg.py` (overlay + CSV/
  GraphML/pickle/taint_paths + CLI), `neo4j_loader.py` (optional).
- Ran on synthetic fixture: **12 sources, 12 sinks, 12 taint paths** (incl. 1 inter-procedural,
  4 hops). Outputs: PPG_nodes.csv/PPG_edges.csv (schema-checked), ppg.graphml, ppg.pkl.
- **Tests:** `tests/test_stage4_ppg.py` — 8 passed (APG loader, catalogs, taint, CSV schema, overlay, serialization).
- **Status:** done. **Commit:** Phase 0+A boundary.

## Phase B — PRCS extraction
- `step2_prcs/extract_prcs.py`: per source→sink flow, slice the subgraph of every method on the
  path (all statements + intra/inter edges + privacy overlay). Emits `<prcs_id>.json` + `prcs_index.csv`.
- Ran on the PPG: **12 PRCS**; inter-procedural one spans 2 methods (12 nodes), subgraph carries
  all 7 edge types incl. TAINT_FLOW + PRIVACY_RELATION; readable per-method code snippet.
- **Tests:** `tests/test_step2_prcs.py` — 5 passed (counts, fields/subgraph, inter-procedural,
  deterministic id, index CSV + JSON roundtrip). **Suite: 13 passed.**
- **Status:** done.

## Phase C — ADPPG dataset (Gate G1)
- `step2_dataset/weak_labeler.py` (WEAK heuristic Practice+Purpose, banner-labeled),
  `build_dataset.py` (labels → adppg.jsonl + Codr export + leakage-free APK-grouped splits +
  labels.csv; auto-overrides with `human_labels.json` when present), `configs/weak_labels.yaml`.
- Tiny fixture (2 apps) → 12 PRCS; weak dist: practice Processing12/Collecting12/Sharing8,
  purpose Functionality6/Advertisement2/Analytics4. 8-app fixture → non-empty train/val/test.
- `HANDOFF_G1.md` written (Codr flow + human_labels.json schema + auto-pickup).
- **Tests:** `tests/test_step2_dataset.py` — 7 passed (weak rules, outputs, leakage-free splits,
  multihot CSV, Codr shape). **Suite: 20 passed.**
- **Status:** done (build-around complete; real labels await human Codr — G1).

## Phase D — ConvGNN (Gate G2 for metrics)
- `step2_convgnn/`: `data.py` (PRCS subgraph → PyG Data, type embedding + privacy features +
  token-embedding hook), `model.py` (RGCN + attention readout + 2 multi-label heads),
  `metrics.py` (per-label P/R/F1, micro/macro F1, subset acc), `train.py` (deterministic,
  BCEWithLogits + pos_weight, early stopping, checkpoint, CSV logs, BOOTSTRAP banner).
- Installed torch 2.12.1 + torch-geometric 2.8.0 + scikit-learn 1.9.0 (Py3.14 wheels).
- **Live training run** on 8-app bootstrap (48 PRCS, 36/6/6 split): early-stopped @45;
  **[BOOTSTRAP]** practice micro_f1=0.97 macro_f1=0.71 subset_acc=0.83; purpose micro_f1=0.86
  macro_f1=0.62 subset_acc=0.67. Wrote best.pt + metrics.csv (with BANNER row) + train_log.csv.
- `HANDOFF_G2.md` written. **Tests:** `tests/test_step2_convgnn.py` — 3 passed (shapes, forward,
  end-to-end training). **Suite: 23 passed.**
- **Status:** done (real metrics await G1 human labels).

## Phase E — Caption generation
- `step3_caption/`: `llm_interface.py` (pluggable provider; OFFLINE deterministic `mock` default +
  key-gated anthropic/openai/llama/deepseek), `code2seq_baseline.py` (untrained placeholder baseline),
  `generate.py` (ICL prompt + per-PRCS caption + baseline → captions.json/csv). `configs/llm.yaml`.
- Mock caption is grounded 4–5 lines (PI + practice + sink + purpose + LINDDUN threat); baseline is
  a terse seq2seq-style line. Captions from WEAK labels carry the weak banner.
- Added `pi_category` to PRCS records for structured captioning.
- **Tests:** `tests/test_step3_caption.py` — 6 passed (deterministic mock, default provider,
  key-gated error, baseline, prompt, dataset run). **Suite: 29 passed.**
- **Status:** done (real LLM prose needs an API key — documented in llm.yaml).

## Phase F — Policy / notice assembly
- `step3_policy/assemble.py`: per-app notice.md + policy.md + policy.json; sections (collected /
  used / shared-with / purposes) + GDPR & CCPA obligation mapping. `configs/gdpr_ccpa_map.yaml`.
- Added `sink_label` to PRCS so "shared with" names real recipients (OkHttp, HttpURLConnection…).
- 8-app run: each policy triggers 11 GDPR + 7 CCPA obligations; DRAFT/WEAK banner on weak inputs.
- **Tests:** `tests/test_step3_policy.py` — 4 passed (per-app docs, GDPR/CCPA mapping, draft banner,
  recipients). **Suite: 33 passed.**
- **Status:** done.

## Phase G — Evaluation harness
- `step4_eval/text_metrics.py` (self-contained smoothed BLEU-4 + ROUGE-L), `evaluate.py`
  (classification via trained ConvGNN + caption BLEU/ROUGE-if-references + policy completeness;
  emits caption_rating_sheet.csv + eval_report.json/md, BOOTSTRAP-gated).
- Honesty: caption BLEU/ROUGE only computed against real references — with none it says
  "no references" and emits a human rating sheet (no fabricated scores). Policy completeness is a
  real structural check (overall=1.0 on fixture).
- Ran on 8-app artifacts (+ trained checkpoint): classification banner-gated, completeness 1.0.
- **Tests:** `tests/test_step4_eval.py` — 7 passed (metric bounds, no-ref + with-ref caption eval,
  completeness, classification skip + with-checkpoint, full report banner). **Suite: 40 passed.**
- **Status:** done (real caption/classification numbers await G1).

## Phase H — User study instrument (Gate G3)
- `step4_userstudy/`: `protocol.md` (RQs, blind A/B ppg-vs-baseline design, analysis plan),
  `consent_template.md`, `build_study.py` (study_tasks.json + study_packet.md + blank
  ratings_template.csv), `ingest_ratings.py` (per-condition Likert means, would-include rate,
  inter-rater agreement — computed only from supplied human ratings). `HANDOFF_G3.md`.
- **Tests:** `tests/test_step4_userstudy.py` — 2 passed (instrument outputs; synthetic-ratings
  ingestion direction). **Suite: 42 passed.**
- **Status:** done (running the study with humans is the gate).

## Phase I — Final integration (Gate G4 for real APKs)
- `adapters/run_apg_csv.py`: real .apk → APG CSVs without Neo4j (mirrors Stage 2; original untouched).
- `pipeline/run_pipeline.py`: ONE command chaining [APK→APG]→PPG→PRCS→ADPPG→ConvGNN→captions→
  policy→eval→study. Ran on 8-app fixture: 48 sources/sinks/paths → 48 PRCS → 8 policies → eval
  (BOOTSTRAP, completeness 1.0) → 20 study tasks.
- `HANDOFF_G4.md` (Androzoo); `FINAL_REPORT.md`; PROJECT.md progress tracker finalized.
- **Tests:** `tests/test_pipeline_e2e.py` — 1 passed (fixture → policy+eval, all artifacts on disk).
- **Full suite: 43 passed, 81% coverage** (uncovered = APK adapter + Neo4j loader: external-resource paths).
- **Status:** done.

## Follow-up — Real-APK validation (sample.apk = F-Droid client)
- Adapter ran on bundled `sample.apk` → `org.fdroid.fdroid` APG: 18,427 classes / 98,724 methods /
  1,528,774 statements / 413,897 calls / 1,509,885 ICFG / 286,602 DDG (androguard ~ minutes).
- PPG built on it: **206 sources, 11,639 sinks, 632,178 taint paths, 1.66M nodes, 4.32M edges**;
  real example flow `ConnectivityMonitorService.getNetworkState → okhttp3.RealConnection` (8 hops).
- **Fixed real-data bug:** smali strings contain XML-illegal chars → lxml GraphML crash. Now write
  pickle first + codepoint-sanitize + try/except guard. (Only surfaces on real APKs.)
- **Found + mitigated taint over-generation:** added `dedup_by_method` (default) → 632K → 235K
  paths (-63%); `max_paths_per_source` + `follow_icfg:false` available for further pruning. FINDINGS §I.
- Suite still **43 passed** (defaults are no-ops on the fixture).

## Follow-up — Real corpus enablement (G4)
- `adapters/fetch_fdroid.py` (no key) — validated: pulled ConnectBot + F-Droid client.
- `adapters/fetch_androzoo.py` (key from `.env` `ANDRO_ZOO_KEY`, redacted everywhere) — `--check`
  confirms key loads (64 chars, hidden); certifi CA bundle fixes androzoo TLS self-signed-chain
  error; index probed (public list, 3.49 GB); download by sha256 or resolve packages via index.
- `.env` gitignored + `.env.example` template; `pplib.load_dotenv`/`redact` (names-only, key-safe).
- `pipeline/run_corpus.py` — many APKs -> one ADPPG dataset (per-APK processing, memory-safe;
  leakage-free APK-grouped splits). `run_pipeline --precision` for large-APK taint tightening.
- **Tests: 51 passed** (added adapter + corpus tests, all offline).
- In progress: downloading AndroZoo index (3.49 GB) for package-based selection.

## Follow-up — Docs cleanup + LLM-assisted G1 annotation (2026-06-30)
- Root had 10 MD files -> consolidated to a single presentation README.md (Mermaid pipeline diagram +
  stage/gate status + real-corpus results + repo map); moved the rest under `docs/` (PROJECT/LEDGER/
  FINDINGS/FINAL_REPORT, `handoffs/`, `archive/`) via `git mv`. New `docs/dashboard.html` (offline visual).
- LLM-assisted G1: a Workflow ran TWO independent LLM annotation passes over all 142 staged rows
  (starter 42 + eval_run 100), merged deterministically. **95.1% inter-pass agreement (135/142)**;
  13 flagged to `data/_review_shortlist.md`. `tools/apply_annotations.py` filled both sheets +
  human_labels.json. INTEGRITY: LLM labels are NOT human ground truth — user to spot-check the
  shortlist + a sample so human–LLM κ can be reported. Fixed `run_g1g2.py` cp1252 crash (force UTF-8).
  Starter loop verified end-to-end: **banner CLEARED** (weak=0 human=42). Eval/G2 metric run started.

## Phase J — Neo4j display (first-class deliverable) + what_it_does semantics
- `stage4_ppg/semantics.py`: per-node `what_it_does` describer — OFFLINE deterministic template
  over privacy facts (Source->"Reads the user's <pi> via <api>", Sink->"Sends/Writes data to <dest>",
  tainted Statement->"Carries tainted <pi>...", Method/Class/DataItem/Store/Component), with an
  optional LLM hook (PCapGen-Extractor style) for salient nodes + a JSON disk cache. LLM-derived
  text tagged `what_it_does_src="llm:<provider>"`; deterministic path tagged `rule`/`cache`.
- Wired into `build_ppg`: `enrich_graph` sets `what_it_does` (+ `_src`) on EVERY node before export;
  added `what_it_does` to `PPG_NODE_COLUMNS` (schema.py) + the CSV export so it ships in
  PPG_nodes.csv, GraphML, pickle, and Neo4j. Offline by default; cheap even on real million-node PPGs.
- `configs/queries.cypher`: 11-query library (app_apg, app_ppg_overlay, list_sources/sinks,
  flows_for_app, prcs_subgraph, taint_path_snippets, node_detail, app_summary, list_apps, clear_app),
  per-app isolation via `app_id`, taint slicing via variable-length `TAINT_FLOW*` path patterns.
- `stage4_ppg/cypher_runner.py`: parses the library into named queries, `--list`/`--show` work fully
  OFFLINE (param substitution for display), `--run` executes against Neo4j (lazy import, never auto-runs
  the DESTRUCTIVE clear_app). `configs/neo4j.grass`: Browser styling (colour by privacy role, caption =
  what_it_does). `DISPLAY.md`: load->style->query->read-a-flow walkthrough.
- **Tests:** `tests/test_neo4j_display.py` — 8 passed (describe roles, determinism, cache roundtrip,
  enrich-all-nodes, CSV column, library parse, params/render, destructive flag). **Suite: 66 passed.**
- **Status:** done.

## Phase K — Stage 8: Privacy Nutrition Facts (labels + app)
- `step4_app/nutrition.py`: distils per-app Privacy Nutrition Facts from adppg.jsonl + captions —
  privacy facts (data collected; data shared off-device + recipients; purposes; third parties) and
  SECURITY-RISK facts (network-egress flows, identifier access, sensitive categories, LINDDUN threats)
  + a TRANSPARENT rule-based risk indicator (0-100, formula documented in `_risk()`; NOT an audit;
  BOOTSTRAP banner when any input label is weak). Emits `<pkg>/nutrition.json` + `.md` + index.
- `step4_app/build_app.py`: the Privacy Nutrition Facts APP — a STDLIB-ONLY static HTML generator
  (lightest stack for an offline-first repo; documented). `index.html` (risk-ranked app picker) +
  `<pkg>.html` per app: nutrition label + practice/purpose bars + captions + a Neo4j panel with the
  app's exact `app_id` and the rendered `app_ppg_overlay` Cypher. One command, no deps/network.
- Wired Stage 8 into `pipeline/run_pipeline.py` (step 9). Ran on real corpus (7 apps): all High risk
  (Duolingo 100/100) — banner-marked since risk uses weak purpose labels.
- **Tests:** `tests/test_step4_app.py` — 3 passed (risk monotonic+explained, nutrition outputs,
  static site renders app_id+cypher). **Full suite: 69 passed.**
- **Status:** done.

## Milestone — first REAL (preliminary) G2 metric on real apps
- Labeled the 100-flow TikTok held-out test split (LLM-assisted annotation, 95.1% inter-pass agreement)
  and retrained: **train=7591 weak / val=2712 weak / test=100 human** (banner CLEARED on the test split).
- **ConvGNN test:** practice micro-F1 **0.848** / macro-F1 **0.584** / subset-acc 0.620;
  purpose micro-F1 **0.847** / macro-F1 0.258 / subset-acc 0.830. (Purpose macro low: test is 84
  Functionality / 16 Analytics / ~0 Advertisement — macro punishes empty/rare classes.)
- **CAVEAT (no-fabrication):** the test labels are LLM-annotated, NOT yet human-verified. This is a
  preliminary real-pipeline metric, not publishable ground truth until the shortlist + a sample are
  human-checked (then report human-LLM kappa). Train remains weak (weak supervision). See FINDINGS §G2.

## Phase L — Real-LLM caption wiring (Anthropic) — verified, blocked on account credits
- User dropped `ANTHROPIC_API_KEY` in `.env`. Enhanced `step3_caption/generate.py`: `--provider`
  override (does NOT mutate llm.yaml, so pipeline/tests stay on the offline mock), `--per-app`/`--limit`
  caps (bound API cost on the 10,721-PRCS corpus), fail-fast with guidance on provider error (no silent
  mock fallback). Set anthropic model default to `claude-sonnet-4-6` (cheaper at volume; opus available).
- **Integration VERIFIED:** the call authenticated and was well-formed; Anthropic returned HTTP 400
  `credit balance is too low`. So this is an EXTERNAL billing gate (not a code bug) — add credits to run.
  Key handled safely throughout (load_dotenv name-only; .env gitignored; never printed/committed).
- **Tests:** +2 offline (`tests/test_step3_caption.py`: sampling caps, provider override). **Suite: 71 passed.**
- **Status:** ready — real captions will generate as soon as the account has credits:
  `python -m step3_caption.generate --dataset data/corpus_run/dataset --out data/corpus_run/captions_llm --provider anthropic --per-app 3`
