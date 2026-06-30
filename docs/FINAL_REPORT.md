# FINAL REPORT — Stage 4 (PPG) + Step 2–4 Build

Branch: `stage4-ppg-convgnn`. Python 3.14.0. All new code is additive; Stage 1–3 scripts untouched.

## 1. "What I Found" (audit)
Full 20-bullet audit is in **FINDINGS.md §0**. Headlines:
- Repo already had **Stage 1–2** (`Static Code Analysis Module/` androguard APG → AST/MCG/ICFG/DDG
  CSV + Neo4j) and **Stage 3** (`Document Analysis Module/` API-doc → `personal_info_results.csv`).
- **APG schema (verified):** nodes `id,label,type,code,callee,app_id`; edges `start_id,end_id,type,app_id`;
  labels Method/Statement (Class + HAS_METHOD are **Neo4j-only**, reconstructed by our adapter);
  edges HAS_STATEMENT/CALLS/ICFG_NEXT/DATA_DEPENDS; `Statement.callee` is the source/sink join key.
- Stage 1–3 scripts have **hard-coded foreign paths** and need Neo4j → cannot run as-is; **no APG CSVs
  exist on this machine**; a **sample APK** is present. No research PDF is in the repo.
- All required deps have **Python 3.14 wheels** (torch 2.12.1, torch-geometric 2.8.0, androguard 4.1.4, neo4j 6.2.0).

## 2. What was built (per phase + files)
| Phase | What | Key files |
|---|---|---|
| 0 | Scaffolding, audit, synthetic fixture | `pplib/{schema,io_utils,apg_model}.py`, `data/fixtures/make_synthetic_apg.py`, `configs/*`, `pytest.ini`, `conftest.py` |
| A | **Stage 4 PPG** | `stage4_ppg/{catalogs,taint,build_ppg,neo4j_loader}.py` |
| B | PRCS extraction | `step2_prcs/extract_prcs.py` |
| C | ADPPG dataset + WEAK labels + Codr + splits | `step2_dataset/{weak_labeler,build_dataset}.py`, `configs/weak_labels.yaml` |
| D | **ConvGNN** (RGCN, 2 heads) | `step2_convgnn/{data,model,metrics,train}.py`, `configs/convgnn.yaml` |
| E | Caption generation (LLM + baseline) | `step3_caption/{llm_interface,code2seq_baseline,generate}.py`, `configs/llm.yaml` |
| F | Policy/notice assembly | `step3_policy/assemble.py`, `configs/gdpr_ccpa_map.yaml` |
| G | Evaluation harness | `step4_eval/{text_metrics,evaluate}.py` |
| H | User-study instrument | `step4_userstudy/{protocol,consent_template,build_study,ingest_ratings}` |
| I | One-command pipeline + APK adapter | `pipeline/run_pipeline.py`, `adapters/run_apg_csv.py` |
| J | **Neo4j display** (first-class) + per-node `what_it_does` | `stage4_ppg/{semantics,cypher_runner}.py`, `configs/{queries.cypher,neo4j.grass}`, `DISPLAY.md` |
| K | **Stage 8 Privacy Nutrition Facts** (labels + viewer app) | `step4_app/{nutrition,build_app}.py` |
Docs: `docs/{PROJECT,LEDGER,FINDINGS}.md`, `docs/handoffs/HANDOFF_G1..G4.md`, `DISPLAY.md`, this report.
Tests: `tests/` (**69**).

## 3. What RUNS vs what is STUBBED / bootstrap
**Runs for real (no caveat):** APG adapter + PPG build (sources/sinks/taint/LINDDUN overlay) +
per-node `what_it_does` + Neo4j Cypher query library/runner + PRCS slicing + ADPPG assembly +
Codr export + APK-grouped splits + ConvGNN training loop + caption generation (offline mock) +
policy assembly + GDPR/CCPA mapping + nutrition-facts labels + the Privacy Nutrition Facts app +
evaluation harness + user-study instrument + the single-command pipeline. 69 tests green.

**First preliminary real metric (G2):** on a 100-flow human-labeled TikTok test split the ConvGNN
scored practice micro-F1 0.848 / macro-F1 0.584; purpose micro-F1 0.847 / macro-F1 0.258. The test
labels are **LLM-annotated, not yet human-verified** — preliminary, not publishable ground truth.

**Bootstrap / placeholder (clearly banner-labeled, never ground truth):**
- **WEAK labels** (`configs/weak_labels.yaml`) — heuristic, await human Codr (G1). `BANNER_WEAK`.
- **SYNTHETIC APG fixture** — generated, not a real APK. `BANNER_SYNTHETIC`.
- **ConvGNN metrics** — computed on weak/synthetic labels → `BANNER_BOOTSTRAP` on every output.
- **Caption LLM** — defaults to a deterministic offline **mock**; real prose needs an API key.
- **Code2Seq baseline** — untrained placeholder (needs paired data from G1).
- **Caption BLEU/ROUGE** — only computed against real references; otherwise reported as "no references".

## 4. Copy-paste run commands
```
pip install -r requirements-stage4.txt
# whole pipeline on the synthetic fixture (no APK, no network):
python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run
# or on a real APK:
pip install androguard
python -m pipeline.run_pipeline --apk "Static Code Analysis Module/input/APK/sample.apk" --out data/run_sample
# individual stages:
python -m stage4_ppg.build_ppg     --apg data/fixtures/synthetic_apg_large --out data/ppg
python -m step2_prcs.extract_prcs  --ppg data/ppg --out data/prcs
python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
python -m step2_convgnn.train      --config configs/convgnn.yaml --dataset data/dataset
python -m step3_caption.generate   --dataset data/dataset --out data/captions
python -m step3_policy.assemble    --dataset data/dataset --captions data/captions --out data/policy
python -m step4_eval.evaluate      --dataset data/dataset --captions data/captions --policy data/policy --checkpoint data/convgnn/best.pt
python -m step4_userstudy.build_study --dataset data/dataset --captions data/captions --out data/userstudy
# tests:
python -m pytest tests/ -q
```

## 5. Test suite + coverage
**69 passed**, 0 failed. Three layers present: unit (catalogs, taint, weak labeler, metrics, text
metrics, semantics/what_it_does, Cypher library, nutrition risk), integration (PPG→PRCS→ADPPG→PyG→
policy I/O contracts; nutrition + app render from the dataset), end-to-end (`tests/test_pipeline_e2e.py`:
fixture → policy + eval in one call; the full `run_pipeline` now also emits Stage 8).
Uncovered: `adapters/run_apg_csv.py` (needs a real APK + androguard), `stage4_ppg/neo4j_loader.py` +
the runner's live `--run` path (need a running Neo4j) — external-resource paths, exercised manually.

## 6. Human gates (what I need from you)
- **G1 — Codr annotation** → `data/dataset/human_labels.json` (HANDOFF_G1.md). Target ≥300–500 PRCS / ≥30 apps.
- **G2 — real metrics** → automatic once G1 lands; retrain (HANDOFF_G2.md).
- **G3 — user study** → IRB approval + ≥12 developers; return rating CSVs (HANDOFF_G3.md).
- **G4 — APK corpus** → Androzoo key / APKs (HANDOFF_G4.md).

## 7. Completion estimate toward a publishable paper
**~70–75% of the engineering; ~40% of the paper.** Reasoning: the full method pipeline (novel PPG +
ConvGNN + caption/policy + eval), the Neo4j display, **Stage 8 nutrition facts + app**, the real APK
corpus (G4, 10,721 PRCS), and a first preliminary G2 metric are all done, reproducible, and tested —
the "systems" contribution is essentially complete. The remaining **scientific** work is human-gated:
verifying the LLM-assisted labels into real ground truth (G1), turning the preliminary G2 numbers into
audited metrics on a balanced labeled set, real-LLM caption tuning + BLEU/ROUGE vs human references,
and the developer/user study (G3). The user study is the longest pole.

## 8. Recommended next actions (in order)
1. **G4 first** (Androzoo key) → run `run_pipeline --apk` over a corpus to mass-produce PRCS.
2. **G1** annotate that PRCS in Codr → `human_labels.json`.
3. **G2** retrain ConvGNN on real labels; tune features (add the statement-token encoder via the
   reserved hook), thresholds, model size; report real P/R/F1, micro/macro, subset acc.
4. Plug a real LLM key; tune caption prompts; compute BLEU/ROUGE vs human references.
5. **G3** run the developer study (blind A/B vs Code2Seq); ingest ratings → RQ1–RQ3.
6. Scale-out, ablations (PPG vs APG-only; RGCN vs GGNN/R-GAT), and paper write-up.
