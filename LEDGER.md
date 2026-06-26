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
