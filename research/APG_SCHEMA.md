# App Property Graph (APG) — Schema

_Phase 3 deliverable. Companion to [STATIC_ANALYSIS_PIPELINE.md](STATIC_ANALYSIS_PIPELINE.md). Authoritative schema constants live in [`pplib/schema.py`](../pplib/schema.py); this document explains the intent, the reconstruction rules, and every identifier pattern. Enforced by [`tests/test_apg_schema.py`](../tests/test_apg_schema.py)._

The APG is the single graph the rest of the pipeline consumes. Every PPG edge, every PRCS slice, every RGCN feature is derived from the APG — so the APG's schema is the contract that binds every downstream stage.

---

## 1. Storage layout

An APG is a directory of 8 CSVs + 1 provenance JSON:

```
<apg_dir>/
├── AST_nodes.csv   AST_edges.csv    # Method + Statement nodes; HAS_STATEMENT edges
├── MCG_nodes.csv   MCG_edges.csv    # Method nodes;              CALLS edges
├── ICFG_nodes.csv  ICFG_edges.csv   # Method + Statement nodes;  ICFG_NEXT edges
├── DDG_nodes.csv   DDG_edges.csv    # Statement nodes;           DATA_DEPENDS edges
└── APG_META.json                    # provenance (Phase 2)
```

Split across four view files rather than one large file because each downstream stage may consume only one or two views (e.g. the RGCN featurizer uses AST + DDG heavily; the call-graph traversal uses only MCG). Splitting keeps memory and read cost per view predictable.

**Class nodes** and **HAS_METHOD** edges are NOT stored in the CSVs. The original Stage-2 script wrote them only into Neo4j; the file-only pipeline reconstructs both from method ids on load (`pplib/apg_model.py::load_apg`). All downstream consumers see a full APG regardless of source. This is the single documented deviation from strict "everything on disk" storage; every other node/edge lives in a CSV.

---

## 2. Node schema

**Common columns** (`pplib.schema.APG_NODE_COLUMNS`, in fixed order — no CSV varies from this):

| Column | Type | Meaning |
|--------|------|---------|
| `id` | string | Globally unique node identifier. Format depends on label — see §5. |
| `label` | enum | `Class`, `Method`, or `Statement`. Constants in `pplib.schema.APG_NODE_LABELS`. |
| `type` | string | For a Statement, the Dalvik instruction mnemonic (`invoke-virtual`, `move`, `iput-object`, …). For Method/Class, the literal string `Method` / `Class`. |
| `code` | string | For a Statement, the raw Dalvik instruction body (`androguard.core.dex.get_output()`). Empty for Method/Class. |
| `callee` | string | For an `invoke-*` Statement, the parsed callee in `pkg.Class->method` form (see §5.4). Empty for everything else. |
| `app_id` | string | Multi-app provenance tag: `{package_name}@{apk_filename}`. Every row in a single-APK APG shares the same `app_id`; merged multi-APK dirs preserve the per-node origin. |

**Label populations by view:**

| View | Node labels present |
|------|--------------------|
| `AST_nodes.csv` | `Method` ∪ `Statement` (every statement plus every method that owns any statement) |
| `MCG_nodes.csv` | `Method` only |
| `ICFG_nodes.csv` | `Method` ∪ `Statement` (same set as AST, kept redundantly so the ICFG view is loadable standalone) |
| `DDG_nodes.csv` | `Statement` only (and only those participating in ≥1 `DATA_DEPENDS` edge) |
| _(reconstructed)_ | `Class` (materialised in memory from `method_class(mid)`; never on disk) |

---

## 3. Edge schema

**Common columns** (`pplib.schema.APG_EDGE_COLUMNS`, fixed order):

| Column | Type | Meaning |
|--------|------|---------|
| `start_id` | string | Source node id (must exist as a node in the corresponding view **or**, for MCG, may reference an external callee not in `Method` nodes — see §3.5). |
| `end_id` | string | Target node id. |
| `type` | enum | One of `HAS_METHOD`, `HAS_STATEMENT`, `CALLS`, `ICFG_NEXT`, `DATA_DEPENDS`. Constants in `pplib.schema.APG_EDGE_TYPES`. |
| `app_id` | string | Inherited from the source node's `app_id` (see `pplib.apg_model.write_apg._edge_row`). |

### 3.1 `HAS_METHOD` — Class → Method

**Not stored in any CSV.** Reconstructed on `load_apg` from the class part of every Method id (`method_class(mid)`). Ownership: exactly one `Class` node per distinct `pkg.Class` prefix.

### 3.2 `HAS_STATEMENT` — Method → Statement _(in `AST_edges.csv`)_

Every Statement belongs to exactly one Method. Method-owned order is preserved by the ICFG (see §3.4), not by HAS_STATEMENT.

### 3.3 `CALLS` — Method → Method _(in `MCG_edges.csv`)_

One edge per `invoke-*` instruction. The **callee may not exist as a node** in `MCG_nodes.csv` — external framework calls (e.g. `android.location.LocationManager->getLastKnownLocation`) are recorded as CALLS edges without a matching Method node. That is intentional and load-tolerant; consumers filter by whether `end_id` is a known method when they care.

### 3.4 `ICFG_NEXT` — Statement → Statement _(in `ICFG_edges.csv`)_

Intra-procedural successor. Emitted as a linear chain in disassembly order (`_stmt_i` → `_stmt_i+1`) inside each method. Branches / try/catch fall-through are not currently modelled — this is a conscious simplification of the true ICFG (see the Phase 2 canonical adapter comment): the PPG's taint analysis uses ICFG only as an "adjacency of last resort" when DDG is sparse, so a coarse linear chain is sufficient.

### 3.5 `DATA_DEPENDS` — Statement → Statement _(in `DDG_edges.csv`)_

Intra-procedural def-use. Emitted when a Statement reads a register that was last written by an earlier Statement in the same Method (`adapters/run_apg_csv.py::_read_vars` / `_written_var`). Register scope is per-method; the DDG is intra-procedural. Inter-procedural taint is a PPG concern (see PPG_SCHEMA.md, Phase 5).

---

## 4. Reserved & derived properties

Statements carry additional properties on disk (the PPG overlay writes them back to the same `Statement` rows in the PPG). At APG level they are absent; at PPG level `pplib.schema.PPG_STATEMENT_PROPS` extends the column set:

```
is_source, is_sink, pi_type, permission, sink_type,
privacy_threat, tainted, sdk, sdk_purpose
```

These are the domain of Phase 5 (PPG). The APG itself is program-structure-only and privacy-agnostic.

---

## 5. Identifiers — canonical formats

Every id in the APG is a Python string, ASCII, no whitespace. Formats are stable and parseable by simple string splits.

### 5.1 Class id

```
{package}.{ClassName}                 e.g.  com.example.foo.LocationHelper
```

Dot-separated, dollar-signs preserved for inner classes (`Foo$Bar`). Produced by `_cls_dots("Lcom/example/foo/LocationHelper;")` (strips leading `L`, trailing `;`, replaces `/` with `.`).

### 5.2 Method id

```
{ClassId}->{methodName}               e.g.  com.example.foo.LocationHelper->getLast
```

Parseable by `pplib.io_utils.method_class` / `method_short_name`. Signature is NOT included — an overload collapses to one Method id. This is a deliberate simplification the RGCN featurizer relies on (features indexed by method name, not signature).

### 5.3 Statement id

```
{MethodId}_stmt_{i}                   e.g.  com.example.foo.LocationHelper->getLast_stmt_0
```

`i` is the 0-indexed position within the method's Dalvik instruction list. Parseable by `pplib.io_utils.stmt_method_id` (splits on `_stmt_`).

### 5.4 Callee string (Statement property, not a node id)

```
{ClassId}->{methodName}
```

Same shape as a Method id — but a callee string may reference an external callee that has no matching Method node in the APG (see §3.3). SuSi source/sink matching and the Stage-5 PPG overlay both match on this exact string.

### 5.5 `app_id` (row-level provenance)

```
{package}@{apk_filename}              e.g.  com.example.foo@foo-1.2.3.apk
```

Parseable by `pplib.io_utils.parse_app_id`. Set by the adapter from `androguard.get_package()` + `Path(apk).name`; identical across every row in a **single-APK** APG.

Note: both committed fixtures (`data/fixtures/synthetic_apg/`, `synthetic_apg_large/`) are pre-merged multi-APK on purpose — they seed the dataset splitter with per-app groups. So a per-row `app_id` may vary across rows in those fixtures; each row's own `app_id` is authoritative for that row.

---

## 6. Provenance — `APG_META.json`

Added in Phase 2. Full schema in [STATIC_ANALYSIS_PIPELINE.md §3](STATIC_ANALYSIS_PIPELINE.md#3-apg_metajson-phase-2-provenance). Summary:

| Field | Type | Guarantee |
|-------|------|-----------|
| `apk_path`, `apk_sha256`, `apk_size_bytes` | string / string / int | Pin the input APK identity. `apk_sha256` is `hashlib.sha256` of the APK file. |
| `app_id`, `package_name` | string | Pin the app identity; must match the `app_id` column in the CSVs. |
| `generator`, `generator_version` | string | `adapters.run_apg_csv` + `ADAPTER_VERSION` from the same file. Bump when disassembly semantics change. |
| `androguard_version`, `python_version` | string | Pin tool identity for cross-machine reproducibility. |
| `generated_at` | ISO-8601 UTC | Timestamp; not consumed programmatically. |
| `summary` | object | Counter block (`classes`, `methods`, `statements`, `calls`, `icfg_edges`, `ddg_edges`). Must self-consistency-match the CSVs — asserted by `tests/test_static_analysis.py::test_run_apg_csv_on_sample_apk`. |

`load_apg_meta(dir)` returns `{}` when absent — fixtures and legacy artifacts without meta still load. Any new APG produced by the canonical adapter carries meta.

---

## 7. Source-code locations

Dalvik does **not** preserve source-file / line information in the general case. androguard exposes what debug info is available via `EncodedMethod.get_debug()`; the current adapter does not consume it.

Two implications:

1. **APG-level `code` field** — the `code` column on Statement is the Dalvik instruction body, not the original Java source line. This is the only "source code" available to the model without decompilation.
2. **Decompiled Java** (e.g. via jadx / cfr) is a separate concern. PriGenLocal/test_apk/ ships ~494 per-method decompiled Java snippets from an earlier attempt; they are archived, not wired in. See CODEBASE_ARCHITECTURE.md §4.

The PPG stage adds a rule-based `what_it_does` explanation per Source / Sink node (via `stage4_ppg/semantics.py`) — that is the closest thing to a human-readable "source location" the pipeline currently emits.

---

## 8. Invariants that must hold on every valid APG

Enforced by [`tests/test_apg_schema.py`](../tests/test_apg_schema.py) against every fixture:

1. **Column contract.** Every `{AST,MCG,ICFG,DDG}_nodes.csv` has exactly the columns in `APG_NODE_COLUMNS`, in order. Every `_edges.csv` has exactly `APG_EDGE_COLUMNS`, in order.
2. **Label validity.** Every `label` value in every nodes CSV is a member of `APG_NODE_LABELS`.
3. **Edge-type validity.** Every `type` value in every edges CSV is a member of `APG_EDGE_TYPES` (minus `HAS_METHOD`, which is reconstructed on load, never on disk).
4. **Method-id shape.** Every Method id contains exactly one `->`.
5. **Statement-id shape.** Every Statement id contains `_stmt_`, and its prefix (before `_stmt_`) is a valid Method id.
6. **Statement `method_id` consistency.** Every Statement's inferred owning method (via `stmt_method_id`) appears as a Method node.
7. **Edge referential integrity.** For AST/ICFG/DDG, every edge's `start_id` and `end_id` reference a node present in that view. Exception: `MCG_edges.csv` may reference external callees not present as `MCG_nodes.csv` rows (see §3.3).
8. **`app_id` populated.** Every row in every APG CSV has a non-empty `app_id` (provenance must never be lost). The stronger single-APK claim — "all rows share one `app_id`" — holds by construction on any APG produced by a single `run_apg_csv` invocation but is not asserted against the multi-app fixtures.

These are consumed as tests, not assertions, so a violation surfaces as a failing CI build rather than a runtime crash deep in the PPG builder.

---

## 9. Inspecting an APG

```python
from pplib.apg_model import load_apg, load_apg_meta

apg = load_apg("data/fixtures/synthetic_apg")
print(apg.summary())                  # classes / methods / statements / calls / icfg / ddg
print(load_apg_meta("data/apg_real")) # {} if the dir has no APG_META.json
```

Human-readable Neo4j view of the same graph: `stage4_ppg/neo4j_loader.py` (optional; see DISPLAY.md).

---

## 10. What Phase 3 explicitly did NOT do

- **Did not** add source-file / line reconstruction via `androguard.get_debug()`. Would enrich the `code` field but expose a fragile androguard API path; deferred until a Phase-5 or Phase-7 need arises.
- **Did not** move Class nodes / HAS_METHOD edges onto disk. Reconstruction on load is 100% deterministic and one line of code (`method_class(mid)`); persisting them doubles storage for zero information gain.
- **Did not** normalise the callee string on external callees (see §3.3). Downstream consumers do this themselves against SuSi / SDK catalogs; centralising it now would freeze the normalisation before Phase 5 owns it.
- **Did not** version the APG schema. `APG_META.json::generator_version` is currently the closest proxy. A formal `apg_schema_version` field can be added when a breaking change lands.
