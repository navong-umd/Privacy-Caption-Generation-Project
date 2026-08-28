# Privacy Graph Traversal

_Phase 6 deliverable. Builds on [PPG_SCHEMA.md](PPG_SCHEMA.md) and [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md). Implementation in [`stage4_ppg/taint.py`](../stage4_ppg/taint.py); reviewer helpers in [`stage4_ppg/traversal.py`](../stage4_ppg/traversal.py); tests in [`tests/test_ppg_provenance.py`](../tests/test_ppg_provenance.py) and [`tests/test_traversal.py`](../tests/test_traversal.py)._

Answers one question: **given a PI source statement, which sinks are reachable and how did the data get there?** Every hop carries the propagation rule that produced it (Phase 5), so any resulting `TaintPath` is fully explainable after the fact.

---

## 1. Algorithm

Per source statement, breadth-first search over the APG until every reachable sink is found or `max_depth` is hit. Parent pointers are kept for path reconstruction; a parallel `reason_into` map records the rule that added each node to the frontier. Result: `TaintPath(source_stmt, sink_stmt, path, reasons, app_id)`.

```
for src in sources:
    parent[src] = ""; reason_into[src] = "source"; depth[src] = 0
    frontier = [src]
    tainted_methods = {}
    while frontier:
        u = frontier.pop()
        if depth[u] >= max_depth: continue
        successors = adj[u]                       # DDG + optional ICFG + CALL-ARG
        if inter_procedural:
            m = method_of(u)
            if m not in tainted_methods:          # CALL-RET
                tainted_methods.add(m)
                successors += callsites(m) tagged "call_ret"
        for (v, rule) in successors:
            if v not seen:
                parent[v] = u; reason_into[v] = rule; depth[v] = depth[u] + 1
                frontier.append(v)
    for snk in sinks reached from src (sorted by depth):
        emit TaintPath from parent-walk (path) and reason_into-walk (reasons)
```

BFS gives the shortest path in hop count. Sinks are enumerated by ascending depth; consumers with a `max_paths_per_source` cap keep the closest sinks and drop the deep ones.

---

## 2. The four rules

Every edge added to the frontier carries a tag. These are the rules; nothing else can create a hop.

| Tag | Predecessor to successor | Config gate | Rationale |
|-----|--------------------------|-------------|-----------|
| `ddg` | Statement writes register `r`, successor reads `r` in the same method. | Always on. | Ground-truth data dependence. |
| `icfg` | Successor is the next Dalvik instruction in the same method. | `taint.follow_icfg` in `configs/ppg.yaml` (default `true`). | Adjacency of last resort when DDG is sparse. Weakest signal. |
| `call_arg` | Predecessor is `invoke-*` of an internal method, successor is that method's entry statement. | `taint.inter_procedural` (default `true`). | Argument flow into a callee. |
| `call_ret` | Predecessor is inside a method that just got tainted, successor is any known call site of that method. | `taint.inter_procedural` (default `true`). | Tainted return value flows to every caller. |

The rules are documented in `configs/ppg.yaml::taint`, in code comments in `stage4_ppg/taint.py::_build_adjacency`, and in `stage4_ppg/traversal.py::RULE_EXPLANATIONS`.

---

## 3. Precision knobs

Real-APK graphs explode with the default rules. `configs/ppg.yaml::taint` exposes:

| Knob | Default | Effect |
|------|---------|--------|
| `max_depth` | 25 | Cap on BFS hops. Bigger = more recall + longer runtime. |
| `inter_procedural` | true | Turn off to disable CALL-ARG and CALL-RET. Intra-method reach only. |
| `follow_icfg` | true | Turn off to drop the `icfg` rule. Higher precision, misses control-only flows. |
| `dedup_by_method` | true | Keep at most one path per (source_method, sink_method) pair. Cuts corpus PRCS count by orders of magnitude on real APKs without losing any source-to-sink pair. |
| `max_paths_per_source` | 0 (unlimited) | Cap flows per origin. Set to a small integer for real APKs; 0 for synthetic fixtures. |

`pipeline._precision_config` writes a `ppg.precision.yaml` at runtime when `--precision` is passed to the corpus driver: `follow_icfg=false`, `max_paths_per_source=25`. That is the setting behind the blessed 10,721-PRCS real-corpus run.

---

## 4. Source and sink identification

- Sources come from `stage4_ppg/catalogs.py::SourceCatalog.classify` (three tiers: curated allowlist, SuSi exact match, opt-in SuSi method-name match), tagged with a category, permission, and PI type. See [KNOWLEDGE_BASE.md §1](KNOWLEDGE_BASE.md).
- Sinks come from `SinkCatalog.classify` (rule catalog: exact / endswith / regex) with `sink_type in {network, storage, logging, ipc, serialization}`, plus the `classify_unknown` egress-verb heuristic for external callees. Heuristic hits carry `sink_known=False`; downstream consumers filter on that when they want precision.

The PPG builder resolves a Statement that matches both a curated source and a sink signature as a source (`build_ppg.py::PPGBuilder.build` precedence rule). This is the only place the two catalogs can conflict, and the tie-break is documented in [PPG_SCHEMA.md §6](PPG_SCHEMA.md).

---

## 5. Deduplication and context expansion

- **Path-level dedup** (`dedup_by_method`): one path per `(source_method, sink_method)` pair. On the blessed corpus this reduced ~1M candidate hops to 10,721 distinct PRCS-eligible flows.
- **Context expansion**: the traversal itself does not expand context beyond the shortest path. PRCS extraction (Phase 7) grows a subgraph around each `TaintPath` to include the immediate DDG/ICFG neighborhood of every hop; that is where the "relevant context" required by the plan lives.

---

## 6. Reviewer helpers

`stage4_ppg/traversal.py` provides two zero-config helpers, both consume a completed `TaintPath` plus the source APG:

- `explain_flow(taint_path, apg) -> list[HopTrace]`: one row per statement on the path. Fields: `step`, `stmt_id`, `method_id`, `callee`, `rule`, `reason` (human string). `HopTrace.to_dict()` is JSON-ready.
- `summarize_flow(taint_path, apg) -> dict`: one-glance summary. Fields: source/sink callee strings, hop count, rule histogram, app id. Handy for corpus-level QA.

The rule strings match the Phase 5 `taint_rule` values in `PPG_edges.csv`; anything that renders one can render the other.

---

## 7. Guarantees

1. Every hop in every returned `TaintPath` carries a rule tag in `{ddg, icfg, call_arg, call_ret}` (asserted by `test_ppg_provenance.py::test_propagate_tags_every_hop_with_a_rule`).
2. Every `TAINT_FLOW` edge in the built PPG carries a `taint_rule` column with a value in that same set (asserted by `test_ppg_provenance.py::test_every_taint_flow_edge_in_the_built_ppg_has_a_defensible_rule`).
3. `explain_flow(tp, apg)` returns exactly `len(tp.path)` rows and every row's `rule` is one of `{source, ddg, icfg, call_arg, call_ret}` (asserted by `test_traversal.py`).
4. BFS gives the shortest-hop path from any source to any sink reachable under the current config. The set of sinks reached is deterministic given the same APG, source set, sink set, and config.

---

## 8. What Phase 6 explicitly did NOT do

- Did not add a min-precision filter mode (`taint_rule in {ddg, call_arg}` only). It is a one-line filter for consumers; adding a config knob only makes sense once we have precision/recall numbers to justify a default.
- Did not implement flow-sensitive taint (branches, exceptions, aliasing). The plan asks for heuristic reach, and the four rules deliver it. A soundness upgrade is a separate research project.
- Did not touch the PRCS neighborhood expansion. That is Phase 7's job.
- Did not change any output paths, CSV columns, or the `TaintPath` fields consumers already depend on. `reasons` is a new field on `TaintPath`; every existing consumer that reads `path` keeps working unchanged.
