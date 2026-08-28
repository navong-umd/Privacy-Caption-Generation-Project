# Privacy Property Graph (PPG) — Schema

_Phase 5 deliverable. Builds on [APG_SCHEMA.md](APG_SCHEMA.md) and [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md). Schema constants in [`pplib/schema.py`](../pplib/schema.py). Enforced by [`tests/test_ppg_provenance.py`](../tests/test_ppg_provenance.py) and [`tests/test_stage4_ppg.py`](../tests/test_stage4_ppg.py)._

The PPG is the APG plus a privacy overlay: privacy-related nodes (Source, Sink, DataItem, Store, Component), privacy-related edges (PRIVACY_RELATION sub-typed, TAINT_FLOW), and per-Statement overlay properties (is_source, is_sink, pi_type, permission, sink_type, privacy_threat, tainted, sdk, sdk_purpose, what_it_does).

The plan's rule for this stage is absolute: **do not create relationships without a defensible analysis rule, and every edge must be explainable after the fact.** Phase 5 makes that testable by tagging every TAINT_FLOW edge with its rule.

---

## 1. Storage layout

A PPG output directory contains:

```
<ppg_dir>/
├── PPG_nodes.csv       APG nodes + overlay nodes with privacy props
├── PPG_edges.csv       APG edges + PRIVACY_RELATION + TAINT_FLOW
├── ppg.pkl             pickled networkx.MultiDiGraph (canonical for downstream)
├── ppg.graphml         GraphML export for viewers (sanitized; may be skipped on real APKs)
└── taint_paths.json    every source-to-sink path with per-hop reasons
```

`ppg.pkl` is the authoritative artifact for PRCS extraction and PyG featurization. `PPG_nodes.csv` / `PPG_edges.csv` mirror the APG CSV style for easy inspection; `ppg.graphml` is a best-effort export for Cytoscape / Gephi / Neo4j Browser.

Column contracts in `pplib.schema`:

- `PPG_NODE_COLUMNS` = `APG_NODE_COLUMNS` + `PPG_STATEMENT_PROPS` + `["what_it_does"]`
- `PPG_STATEMENT_PROPS` = `["is_source", "is_sink", "pi_type", "permission", "sink_type", "privacy_threat", "tainted", "sdk", "sdk_purpose"]`
- `PPG_EDGE_COLUMNS` = `["start_id", "end_id", "type", "app_id", "pi_type", "privacy_threat", "taint_rule"]`
  - `taint_rule` is Phase 5 provenance; empty on non-TAINT_FLOW edges.

---

## 2. Nodes

Everything on the APG (§APG_SCHEMA.md §2) plus:

| Node label | Id format | Purpose |
|------------|-----------|---------|
| `Source` | `src::<statement_id>` | Materializes "this Statement calls a PI API." Carries `api`, `pi_type`, `permission`, `category`. One Source per PI-source Statement. |
| `Sink` | `sink::<statement_id>` | Materializes "this Statement calls a data-sink API." Carries `api`, `sink_type`, `sink_label`, `known` (True if from catalog rule, False if from egress heuristic). One Sink per sink Statement. |
| `DataItem` | `data::<PI_CATEGORY>` | Deduped node for the data type collected. e.g. `data::LOCATION_INFORMATION`. Cross-Source aggregator. |
| `Store` | `store::<sink_label>` | Emitted for `sink_type == storage`. Represents the storage destination (SharedPreferences, SQLite, FileIO). |
| `Component` | `component::<sink_label>` | Emitted for `sink_type == ipc`. Represents the Android component the data is sent to. |

The Statement it originated from also gets overlay props written back onto its APG node (see `PPG_STATEMENT_PROPS`); a downstream consumer can read the same information either from the Statement row or by following its outgoing PRIVACY_RELATION edge.

---

## 3. Edges

Everything on the APG (§APG_SCHEMA.md §3) plus:

### 3.1 PRIVACY_RELATION

Sub-typed via the `relation` property. Every emission has a documented producing rule (in `stage4_ppg/build_ppg.py::PPGBuilder.build`).

| `relation` | Endpoints | Rule that emits it |
|------------|-----------|--------------------|
| `ACCESSES` | Statement to Source | Emitted when SourceCatalog classifies the Statement's callee as a PI source. |
| `OF_TYPE` | Source to DataItem | Emitted alongside every `ACCESSES` edge, connecting the Source to the PI category it accesses. |
| `WRITES_TO` | Statement to Sink | Emitted when the Statement's callee is a sink (catalog or egress heuristic) and the Statement is not itself already claimed as a Source. |
| `PERSISTS_IN` | Sink to Store | Emitted for `sink_type == storage`. |
| `SENDS_VIA` | Sink to Component | Emitted for `sink_type == ipc`. |
| `FLOWS_TO` | Source to Sink | Emitted per taint path (`taint_paths[i]`) connecting the Source overlay node to the Sink overlay node with the derived `privacy_threat`. |

### 3.2 TAINT_FLOW

Statement to Statement. Emitted per hop along a `TaintPath`. Carries:

- `type = "TAINT_FLOW"`
- `pi_type` = the source PI category (propagated along the path)
- `privacy_threat` = the LINDDUN(GO) threats derived from `(sink_type, pi_category)` via `configs/ppg.yaml::linddun_map` + `identifying_pi_categories`
- `taint_rule` (Phase 5) = one of `ddg | icfg | call_arg | call_ret` (or `unknown` for legacy TaintPaths without a reasons list)

The `taint_rule` tag is the answer to "why does this edge exist?" for a reviewer inspecting the PPG. Semantics:

| `taint_rule` | Producing rule | Analysis intent |
|--------------|----------------|-----------------|
| `ddg` | Predecessor writes a register the successor reads (intra-procedural def-use). | The most defensible taint edge, a direct data dependence. |
| `icfg` | Successor immediately follows the predecessor in the method's Dalvik instruction stream. Only emitted when `configs/ppg.yaml::taint.follow_icfg=true` (default). | Adjacency of last resort when the DDG is sparse. Weakest signal but harmless when DDG covers the true flow. |
| `call_arg` | Predecessor is an `invoke-*` of an internal method; successor is the entry statement of that method. | Inter-procedural: taint flows into the callee via its arguments. |
| `call_ret` | Predecessor is inside a method already marked tainted; successor is a call site of that method. | Inter-procedural: any caller of a tainted method sees the (potentially) tainted return value. |
| `unknown` | Legacy TaintPath produced before the Phase 5 upgrade (no `reasons` list). | Emitted only for backward compatibility; new runs never produce it. |

---

## 4. LINDDUN(GO) threat tagging

Every TAINT_FLOW edge (and the `FLOWS_TO` PRIVACY_RELATION edge) carries a `privacy_threat` string derived deterministically from the `(sink_type, pi_category)` pair:

- `configs/ppg.yaml::linddun_map` maps `sink_type -> [threats]` (e.g. `network -> [Data Disclosure, Linking, Detecting]`).
- `configs/ppg.yaml::identifying_pi_categories` escalates any flow whose PI category is an identifying type (e.g. `UNIQUE_IDENTIFIER`, `PHONE_INFORMATION`, `ACCOUNT_INFORMATION`, `EMAIL`) by adding the `Identifying` threat.

Threats are semicolon-joined for CSV/PyG friendliness.

---

## 5. Overlay properties written back onto Statement nodes

When the Statement is classified as a Source, Sink, or relay in a taint path, the PPG builder writes these back:

| Prop | Set by |
|------|--------|
| `is_source` = True | Source classification (see §3.1 ACCESSES). |
| `pi_type`, `permission`, `category` | SourceCatalog hit. |
| `is_sink` = True | Sink classification (see §3.1 WRITES_TO). |
| `sink_type`, `sink_label` | SinkCatalog hit (or egress heuristic). |
| `tainted` = True | Statement appears in any TaintPath (source, relay, or sink). |
| `privacy_threat` | Only on the sink Statement of each TaintPath. LINDDUN string. |
| `what_it_does` | Semantic overlay (rule-based; optional LLM enrichment) via `stage4_ppg/semantics.enrich_graph`. Every node gets one. |

---

## 6. Precedence and de-conflicting rules

`PPGBuilder.build` classifies each Statement in order:

1. If it's a **curated source** (Tier 1 known), mark as Source even if it's also a sink signature.
2. Else if it's a **sink** (catalog or heuristic), mark as Sink.
3. Else if it's a **SuSi source** (Tier 2), mark as Source.

This precedence keeps a `Log.i(location)` call on the sink side of the flow, not the source side, unless the callee itself is a known PI accessor.

---

## 7. Provenance guarantee (the plan's rule made testable)

For any edge in `PPG_edges.csv`:

- **PRIVACY_RELATION**: the `relation` sub-type in `ppg.pkl` (and reconstructable from `sink_type` on the endpoint node in CSV form) tells you exactly which rule in `PPGBuilder.build` emitted it. Each rule is one file, one function, ~5 lines.
- **TAINT_FLOW**: the `taint_rule` column in `PPG_edges.csv` tells you which of the four taint propagation rules produced this edge. Reviewers who want to filter to precision-only edges can `taint_rule in {ddg, call_arg}`; recall analysis includes `icfg, call_ret`.

Enforced by `tests/test_ppg_provenance.py::test_every_taint_flow_edge_has_a_defensible_rule` against the synthetic fixture.

---

## 8. Where the KB feeds this stage

The Source, Sink, and DataItem overlay nodes are direct materializations of `pplib.knowledge.KnowledgeBase.lookup(callee)`. Every claim propagates: `pi_category` from `KnowledgeHit.pi_category`; `permission` from `KnowledgeHit.permission`; `sink_type` from `KnowledgeHit.sink_type`; `sink_known` from `KnowledgeHit.sink_known`; SDK purpose (used at the PRCS aggregation layer) from `KnowledgeHit.sdk_purpose`. The KB's `source_provenance` and `source_tier` are not currently written onto the Source node — they should be, and Phase 5 flags this as a follow-on `note-improvement` rather than adding load-bearing schema fields under time pressure.

---

## 9. What Phase 5 explicitly did NOT do

- Did not route `PPGBuilder` through `pplib.knowledge.KnowledgeBase.lookup`. The builder still calls `SourceCatalog.classify` and `SinkCatalog.classify` directly. Their return objects already carry everything the KB exposes, so the visible schema is unchanged; the rewire is cosmetic and belongs to a later cleanup pass.
- Did not persist per-Source `source_tier` and `source_provenance` onto the Source overlay node. The `KnowledgeBase.lookup` output has them; the PPG schema does not surface them yet. Add via a `note-improvement` when consumers ask.
- Did not touch the `FLOWS_TO` PRIVACY_RELATION edge to carry its own aggregate rule set. The per-hop `taint_rule` on TAINT_FLOW is finer-grained and reconstructs the same information.
- Did not change the flat CSV layout, the pickle format, or the GraphML export path. All three still land in `<ppg_dir>/` unchanged.
