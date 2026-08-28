# Privacy-Relevant Code Slice (PRCS) — Schema

_Phase 7 deliverable. Builds on [PPG_SCHEMA.md](PPG_SCHEMA.md) and [PRIVACY_TRAVERSAL.md](PRIVACY_TRAVERSAL.md). Schema constants live in [`pplib/prcs_schema.py`](../pplib/prcs_schema.py). Extractor in [`step2_prcs/extract_prcs.py`](../step2_prcs/extract_prcs.py); tests in [`tests/test_prcs_schema.py`](../tests/test_prcs_schema.py)._

A PRCS is one privacy-relevant slice of one APK: everything needed to reason about, learn from, caption, or audit a single source-to-sink flow, with **full provenance** from APK back through the taint path.

The plan's rule for this stage: **"Nothing should become an opaque ML sample."** Every PRCS must trace back to the APK, the method, the callees, the path, and the rule that produced each hop.

---

## 1. Storage layout

```
<prcs_dir>/
├── prcs_<id>.json     one JSON per slice (schema below)
└── prcs_index.csv     flat table for filtering / joining (subset of fields)
```

`<id>` is a stable 12-hex hash of `f"{app_id}|{source_stmt}|{sink_stmt}"`, so the same source-to-sink flow always gets the same id across runs.

---

## 2. Fields (`PRCS_REQUIRED_FIELDS`)

Every serialized PRCS JSON has all of these, populated, with `schema_version == "1.0.0"`.

### Identity + schema

| Field | Type | Purpose |
|-------|------|---------|
| `prcs_id` | string | `"prcs_" + sha1("{app_id}|{src}|{snk}")[:12]` — stable across runs. |
| `schema_version` | string | `"1.0.0"`. Bump on any breaking change to the field set or semantics. |

### Provenance (which APK)

| Field | Type | Purpose |
|-------|------|---------|
| `app_package` | string | `com.example.app` from `androguard.get_package()`. |
| `apk_filename` | string | The `.apk` file name at extraction time. |

Together `f"{app_package}@{apk_filename}"` equals the APG-level `app_id`.

### Source-code location

| Field | Type | Purpose |
|-------|------|---------|
| `class_name` | string | Class holding the source statement. |
| `method_name` | string | Method holding the source statement. |
| `method_signature` | string | Full method id (`class->method`). |
| `involved_methods` | `List[string]` | Every method the path traverses, in order, deduped. |

Dalvik strips source file / line info in the general case; the code snippet + involved methods stand in for line ranges. See APG_SCHEMA.md §7 for background.

### Privacy semantics (from the KB via PPG)

| Field | Type | Purpose |
|-------|------|---------|
| `source_api` | string | Callee at the source statement (`pkg.Class->method`). |
| `sink_api` | string | Callee at the sink statement. |
| `sink_type` | string | `network` \| `storage` \| `logging` \| `ipc` \| `serialization` \| `heuristic_unknown`. |
| `sink_label` | string | Human-friendly sink label. |
| `pi_type` | string | Natural-language PI type when available, else the SuSi category. |
| `pi_category` | string | SuSi category (e.g. `LOCATION_INFORMATION`). |
| `permission` | string | Android permission inferred via `configs/ppg.yaml::permission_map`. Empty if unmapped. |
| `privacy_threat` | string | LINDDUN(GO) threats, semicolon-joined. |

### Trace (Phase 5 provenance chain)

| Field | Type | Purpose |
|-------|------|---------|
| `hop_count` | int | `len(taint_path) - 1`. |
| `taint_path` | `List[string]` | Every statement id from source to sink, in order. |
| `taint_rules` | `List[string]` | Parallel to `taint_path`. `taint_rules[0] == "source"`; `taint_rules[i>=1]` is the rule that produced edge `taint_path[i-1] -> taint_path[i]`, one of `{ddg, icfg, call_arg, call_ret}`. Empty for PRCS extracted from a pre-Phase-5 PPG (`taint_paths.json` without `reasons`). |

### Rendered + structural

| Field | Type | Purpose |
|-------|------|---------|
| `code_snippet` | string | Flow rendered as text, grouped by method. Ready for captions and human review. |
| `subgraph` | `{"nodes": [...], "edges": [...]}` | Bounded subgraph around the path: enclosing method(s), privacy overlay (Source/Sink/DataItem), plus a 1-hop neighborhood. Node cap: 150. |

---

## 3. `prcs_index.csv`

Flat table with `PRCS_INDEX_COLUMNS` (`pplib/prcs_schema.py`). One row per PRCS. Fields:

`prcs_id, schema_version, app_package, apk_filename, class_name, method_name, method_signature, source_api, sink_api, sink_type, pi_type, permission, privacy_threat, hop_count, n_nodes, n_edges`

Subgraph and snippet live in the per-PRCS JSON; the index is for grouping, filtering, and joining with labels.

---

## 4. Invariants (`tests/test_prcs_schema.py`)

1. Every PRCS JSON contains every entry in `PRCS_REQUIRED_FIELDS`.
2. `schema_version == "1.0.0"` on every record.
3. `app_package`, `apk_filename`, `class_name`, `method_name` are all non-empty (no anonymous PRCS).
4. `len(taint_path) == hop_count + 1`.
5. If `taint_rules` is non-empty, it is exactly as long as `taint_path`, its first element is `"source"`, and every other element is in `{ddg, icfg, call_arg, call_ret}`.
6. `source_api` and `sink_api` are both non-empty.
7. `subgraph["nodes"]` is non-empty and at most 150 nodes (the extractor cap).
8. `prcs_index.csv` columns exactly equal `PRCS_INDEX_COLUMNS`.

---

## 5. Consumers

- **`step2_dataset/build_dataset.py`** reads per-PRCS JSON to assemble the ADPPG dataset.
- **`step3_caption/generate.py`** reads the PRCS to build the evidence dict for caption generation.
- **`step3_policy/assemble.py`** reads the same fields for GDPR/CCPA policy assembly.
- **`step4_eval/evaluate.py`** joins predictions against the PRCS index for evaluation.

Any of these can validate an incoming PRCS by checking `schema_version == PRCS_SCHEMA_VERSION` and `set(payload) >= set(PRCS_REQUIRED_FIELDS)`.

---

## 6. What Phase 7 explicitly did NOT do

- Did not add source-file / line-range fields. Dalvik strips them; `code_snippet` + `involved_methods` stand in. Extractor stays byte-stable.
- Did not migrate existing on-disk PRCS to schema 1.0.0. Old JSONs without `schema_version` still load in existing consumers because those consumers already tolerate missing fields; new writes carry the version.
- Did not collapse `data/prcs/prcs_<id>.json` and `data/dataset/codr_export/prcs_<id>.json` into one serialization. The recon flagged that as a Phase 22 cleanup; touching it now would break the Codr export the annotation workflow depends on.
- Did not change the subgraph slicing rules or the 150-node cap. Those are performance and label-quality knobs; belong to a separate experiment.
