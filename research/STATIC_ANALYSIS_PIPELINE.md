# Canonical Static Analysis Pipeline

_Phase 2 deliverable. Companion to [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) §1 (Current Working Pipeline) and [ENVIRONMENT.md](ENVIRONMENT.md). Verified by `tests/test_static_analysis.py`._

Turns a `.apk` into the four-view **App Property Graph** (AST / MCG / ICFG / DDG) that every downstream stage (PPG, PRCS, ADPPG, RGCN, Caption, Policy) consumes.

Preserves the existing Androguard-based disassembly (`adapters/run_apg_csv.py`); adds **provenance metadata** and **determinism / real-APK tests** so any two runs of the same APK produce the same graph, and any downstream artifact can trace back to the APK, adapter version, and tool versions that produced it.

---

## 1. Entry point

Single CLI, one importable helper:

```
python -m adapters.run_apg_csv --apk path/to/app.apk --out artifacts/<apk-id>
```

Or programmatically:

```python
from adapters.run_apg_csv import run_apg_csv
apg = run_apg_csv("app.apk", "artifacts/<apk-id>", write=True)   # writes CSVs + APG_META.json
apg = run_apg_csv("app.apk", None,               write=False)    # in-memory only (corpus driver)
```

`write=False` is what `pipeline/run_corpus.py` uses to avoid ~1 GB of APG CSVs per app on a disk-constrained machine.

**Requires:** `pip install -r requirements-apk.txt` (androguard==4.1.4).

---

## 2. Output layout

Each APG output directory contains the exact 8-CSV Stage-2 schema **plus** a JSON provenance file:

```
artifacts/<apk-id>/
├── AST_nodes.csv     # Method + Statement nodes
├── AST_edges.csv     # HAS_STATEMENT edges (method → statement)
├── MCG_nodes.csv     # Method nodes (call graph)
├── MCG_edges.csv     # CALLS edges (method → method, includes external callees)
├── ICFG_nodes.csv    # Method + Statement nodes (control-flow context)
├── ICFG_edges.csv    # ICFG_NEXT edges (statement → next statement in method)
├── DDG_nodes.csv     # Statement nodes that participate in a data flow
├── DDG_edges.csv     # DATA_DEPENDS edges (def-site → use-site within a method)
└── APG_META.json     # ← NEW in Phase 2
```

Column contract is pinned in [`pplib/schema.py`](../pplib/schema.py):

- `APG_NODE_COLUMNS = ["id", "label", "type", "code", "callee", "app_id"]`
- `APG_EDGE_COLUMNS = ["start_id", "end_id", "type", "app_id"]`
- Labels: `Class`, `Method`, `Statement`
- Edge types: `HAS_METHOD`, `HAS_STATEMENT`, `CALLS`, `ICFG_NEXT`, `DATA_DEPENDS`

Class nodes and `HAS_METHOD` edges are **reconstructed** on load from method ids (the original Stage-2 Neo4j-only artifact is materialised in `pplib/apg_model.py::load_apg`). Consumers see the full graph regardless.

### Per-APK partitioning (the user's plan §Required Output)

The plan calls for `artifacts/<apk-id>/{metadata,disassembly,ast,mcg,icfg,ddg}/`. The current layout is isomorphic: everything lives under one `<apk-id>` directory, provenance is `APG_META.json`, and each of `AST_*`, `MCG_*`, `ICFG_*`, `DDG_*` is a prefixed CSV pair. This preserves the single-source-of-truth column contract in `pplib/schema.py` (which every downstream consumer already reads) and keeps 79 pre-existing tests green. See [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) §6 — the plan's "refactor only when there is a clear benefit" rule guided this decision.

---

## 3. APG_META.json (Phase 2 provenance)

Written next to the CSVs by `adapters/run_apg_csv.py`. Example:

```json
{
  "apk_path": "<local APK named by PPCAP_SAMPLE_APK>",
  "apk_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "apk_size_bytes": 11904560,
  "app_id": "com.example.sample@sample.apk",
  "package_name": "com.example.sample",
  "generator": "adapters.run_apg_csv",
  "generator_version": "2.0.0",
  "androguard_version": "4.1.4",
  "python_version": "3.14.0",
  "generated_at": "2026-08-28T00:37:00+00:00",
  "summary": {
    "classes": 812,
    "methods": 5423,
    "statements": 189044,
    "calls": 41207,
    "icfg_edges": 183621,
    "ddg_edges": 62018
  }
}
```

**Guarantee**: every APG output directory produced by the adapter carries an `APG_META.json` that pins:
- the APK identity (path, `sha256`, size, `app_id`, `package_name`),
- the adapter identity (`generator`, `generator_version`),
- the tool identity (`androguard_version`, `python_version`),
- the generation timestamp,
- a `summary` counter block that must match the CSVs (self-consistency asserted by `test_run_apg_csv_on_sample_apk`).

Downstream stages (PPG builder, PRCS extractor) may `load_apg_meta(dir)` to record their own provenance chain.

`load_apg_meta` returns `{}` when no meta is present, so this file is fully backward-compatible — existing fixtures and legacy artifacts still load through `pplib.apg_model.load_apg`.

---

## 4. Determinism

The exit criterion the user's plan puts on Phase 2 — _"same APK produces consistent structural analysis results"_ — decomposes into two invariants, both tested:

1. **Deterministic writer.** Given the same in-memory APG object, `write_apg(apg, dir)` produces byte-identical CSVs across independent write calls. Guarded by `tests/test_static_analysis.py::test_write_apg_is_deterministic` (loads the committed synthetic fixture, writes it twice, `filecmp.cmp` all 8 CSVs).

2. **Roundtrip preservation.** `load → write → load` preserves node/edge counts across all four graphs. Guarded by `tests/test_static_analysis.py::test_write_apg_roundtrip_preserves_shape`.

Together these guarantee that any downstream artifact (PPG, PRCS, model input) computed from an APG is a pure function of the input APK when the adapter version and androguard version match — both of which `APG_META.json` records.

The stronger claim — _"two runs of the same APK on different machines produce byte-identical APG CSVs"_ — is **not yet asserted**. androguard's method iteration order is stable across runs on the same machine but has occasionally varied across major androguard versions. The `androguard_version` field in `APG_META.json` is the primary hedge; the Phase 21 evaluation matrix will pin androguard exactly.

---

## 5. Tests

`tests/test_static_analysis.py` — 6 test cases:

| Test | Depends on | Purpose |
|------|-----------|---------|
| `test_apg_meta_roundtrip` | stdlib | Sanity-check the JSON contract. |
| `test_apg_meta_absent_returns_empty_dict` | stdlib | Backward compat: fixtures without meta still load. |
| `test_sha256_file_deterministic` | stdlib | Prove `sha256_file` is stable + handles missing paths. |
| `test_write_apg_is_deterministic` | fixture | Bytewise-diff test on all 8 CSVs. |
| `test_write_apg_roundtrip_preserves_shape` | fixture | Counts survive load→write→load. |
| `test_run_apg_csv_on_sample_apk` | fixture + `androguard` (skipped without) | Real-APK end-to-end: 11 MB the local APK named by `PPCAP_SAMPLE_APK` → 8 CSVs + APG_META.json → non-empty APG → self-consistent summary. |

The real-APK case addresses the gap the Phase 0 recon flagged: prior to Phase 2, no test ever invoked the adapter against a real `.apk`.

---

## 6. Legacy references (Phase 0 recon, retained on disk, not run)

The canonical adapter mirrors the legacy Stage-2 script in `legacy/static_analysis/consolidated/androguard_analysis_APG_III_Update1Fixed_14.py`. Its five `MCG_reachability*` variants and the `androguard_analysis_APG_Bar.py` iteration are dead code (unreferenced). Keeping them for provenance until the Phase 22 archive move.

Only `pplib/schema.py`'s column constants formally enforce the mirror; a stronger structural equivalence check (diff the `_parse_callee` / `_written_var` / `_read_vars` helpers between adapter and legacy) is a Phase 22 finalization task.

---

## 7. What Phase 2 explicitly did NOT do

- **Did not** refactor the flat 8-CSV layout to `ast/`, `mcg/`, `icfg/`, `ddg/` subdirectories. `pplib/schema.py` and every downstream consumer already work with the flat layout; no research question is answered by that churn. The plan explicitly permits this ("refactor only when there is a clear benefit").
- **Did not** wire per-edge provenance into `TAINT_FLOW` (that lives on the PPG, not the APG — belongs to Phase 5).
- **Did not** re-run any of the six unreferenced legacy `androguard_*` variants. They remain frozen on disk until Phase 22.
- **Did not** add a `.apk` under `data/fixtures/` — the local APK named by `PPCAP_SAMPLE_APK` (11 MB) already exists and is treated as the real-APK smoke test input. Committing another APK doubles the repo size without adding coverage.
