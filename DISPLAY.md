# DISPLAY.md — viewing the Privacy Property Graph in Neo4j

The PPG is a **first-class visual deliverable**: one App Property Graph per app, every node
carrying both the **raw code** (`code`) and a human-readable **`what_it_does`** description,
coloured by privacy role. This guide shows how to load an app, style it, and slice it.

Everything here is optional — the pipeline, PRCS slicing, and tests run fully without a
database (the PPG is also written as `PPG_nodes.csv` / `PPG_edges.csv` / `ppg.pkl` / `ppg.graphml`).

---

## 1. Load one app into Neo4j

Start a local Neo4j (Desktop or Docker), then either:

**A. Build straight into Neo4j**
```bash
pip install neo4j
python -m stage4_ppg.build_ppg --apg data/fixtures/synthetic_apg_large \
    --out data/ppg --neo4j
```
Connection settings come from `NEO4J_URI`, `NEO4J_USER` and `NEO4J_PASSWORD` in `.env` (see `.env.example`). The uri and user fall back to `configs/ppg.yaml` → `neo4j:`; the password is never read from config.

**B. Import the CSVs** (`PPG_nodes.csv` / `PPG_edges.csv`) with `LOAD CSV` if you prefer.

Every node/edge is tagged with **`app_id`** (`"package@file.apk"`), so many apps can live in
one instance and stay independently queryable. List what's loaded:
```bash
python -m stage4_ppg.cypher_runner --run list_apps
```

## 2. Apply the styling

In Neo4j Browser run `:style`, then drag in [`configs/neo4j.grass`](configs/neo4j.grass)
(or paste its contents). Colour legend:

| Colour | Node | Meaning |
|---|---|---|
| 🔵 cyan | `Source` | reads personal data |
| 🔴 red | `Sink` | data leaves / is written |
| 🟠 orange | `DataItem` | a personal-data item (by category) |
| 🟡 yellow | `Store` | local persistence target |
| 🟣 pink | `Component` | IPC / app-component endpoint |
| 🟢 green | `Statement` | a code statement (red **taint** edges trace flows) |

Node captions show `what_it_does`; click any node to read its `code` + `what_it_does`.

## 3. Query / slice the graph

The query library lives in [`configs/queries.cypher`](configs/queries.cypher) and is driven by
a thin runner. Inspect a query offline (no DB needed), or run it live:

```bash
python -m stage4_ppg.cypher_runner --list                       # all queries + params
python -m stage4_ppg.cypher_runner --show app_ppg_overlay --app-id "com.x@x.apk"   # print Cypher
python -m stage4_ppg.cypher_runner --run  list_sources    --app-id "com.x@x.apk"   # execute
```

| Query | What it renders |
|---|---|
| `app_apg` | one app's full APG + PPG |
| `app_ppg_overlay` | only the privacy lens (Source/Sink/DataItem + PRIVACY_RELATION/TAINT_FLOW) |
| `list_sources` / `list_sinks` | sources / sinks with `pi_type` / `sink_type` + `what_it_does` |
| `flows_for_app` | every source→sink flow with its LINDDUN threat |
| `prcs_subgraph` | the PRCS subgraph for one `--source-id`→`--sink-id` flow |
| `taint_path_snippets` | that path as a table: each hop's `code` + `what_it_does` |
| `node_detail` | one node's code/description + neighbours |
| `app_summary` | #sources / #sinks / #tainted / #flows for an app |
| `clear_app` | **destructive** — delete one app (run manually) |

## 4. Reading a flow (typical demo)

1. `app_ppg_overlay --app-id <app>` → see the privacy structure.
2. `flows_for_app --app-id <app>` → pick an interesting source→sink (note the threat).
3. `prcs_subgraph --source-id <s> --sink-id <k>` → the exact tainted path (red edges).
4. Click each hop, or run `taint_path_snippets`, to read `code` + `what_it_does` per statement.

## Notes
- `what_it_does` is generated **offline and deterministically** by default
  (`stage4_ppg/semantics.py`). Wiring a real LLM provider (via `configs/llm.yaml`) enriches
  source/sink/tainted nodes with LLM prose; that text is cached and tagged
  `what_it_does_src = "llm:<provider>"` so LLM-derived descriptions are always marked.
- The runner never auto-runs `clear_app`; destructive deletes are left to you in the Browser.
