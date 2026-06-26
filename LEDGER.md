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
- **Status:** done. **Commit:** (Phase 0+A boundary).
