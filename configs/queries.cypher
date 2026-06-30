// PPG Cypher query library — render & slice the Privacy Property Graph in Neo4j.
// Parsed by stage4_ppg/cypher_runner.py: each query starts with `// name: <name>`,
// following `//` lines are its description, the rest is the Cypher (params are $name).
// Per-app isolation: every node carries app_id ("package@file.apk"); pass --app-id to scope.
// Query style follows the Cypher property-graph paper (subgraph slicing via path patterns).

// name: app_apg
// Render one app's full APG+PPG (all node/edge types between nodes sharing the app_id).
// Use this as the default "show me this app's graph" view.
MATCH (n {app_id: $app_id})-[r]->(m {app_id: $app_id})
RETURN n, r, m;

// name: app_ppg_overlay
// Render ONLY the privacy overlay for one app: Source/Sink/DataItem/Store/Component
// nodes and PRIVACY_RELATION / TAINT_FLOW edges. The privacy "lens" on the APG.
MATCH (n {app_id: $app_id})-[r:PRIVACY_RELATION|TAINT_FLOW]->(m {app_id: $app_id})
RETURN n, r, m;

// name: list_sources
// All PI sources in an app with the data type, permission, and what_it_does description.
MATCH (s:Source {app_id: $app_id})
RETURN s.api AS api, s.pi_type AS pi_type, s.permission AS permission,
       s.category AS category, s.what_it_does AS what_it_does
ORDER BY pi_type;

// name: list_sinks
// All data sinks in an app with the sink type, recipient label, and what_it_does.
MATCH (s:Sink {app_id: $app_id})
RETURN s.api AS api, s.sink_type AS sink_type, s.sink_label AS recipient,
       s.known AS known, s.what_it_does AS what_it_does
ORDER BY sink_type;

// name: flows_for_app
// Every source->sink privacy flow in an app with its LINDDUN threat tag.
MATCH (src:Source {app_id: $app_id})-[f:PRIVACY_RELATION {relation: 'FLOWS_TO'}]->(snk:Sink)
RETURN src.api AS source_api, src.pi_type AS pi_type,
       snk.api AS sink_api, snk.sink_type AS sink_type, f.privacy_threat AS threat;

// name: prcs_subgraph
// Slice the PRCS subgraph for one source->sink flow: the taint path plus the statements
// on it (with code + what_it_does). $source_id and $sink_id are Statement ids.
MATCH p = (s:Statement {id: $source_id})-[:TAINT_FLOW*1..25]->(t:Statement {id: $sink_id})
RETURN p;

// name: taint_path_snippets
// The same source->sink path as a readable table: each hop's code and what_it_does.
MATCH p = (s:Statement {id: $source_id})-[:TAINT_FLOW*1..25]->(t:Statement {id: $sink_id})
WITH nodes(p) AS ns
UNWIND range(0, size(ns) - 1) AS i
RETURN i AS hop, ns[i].id AS stmt_id, ns[i].pi_type AS pi_type,
       ns[i].sink_type AS sink_type, ns[i].code AS code, ns[i].what_it_does AS what_it_does;

// name: node_detail
// Click-through for a single node: its code + what_it_does + immediate neighbours.
MATCH (n {id: $node_id})
OPTIONAL MATCH (n)-[r]-(m)
RETURN n.id AS id, n.label AS label, n.code AS code, n.what_it_does AS what_it_does,
       type(r) AS rel, m.id AS neighbour, m.what_it_does AS neighbour_does;

// name: app_summary
// One-row privacy summary for an app: #sources, #sinks, #tainted statements, #flows.
MATCH (s:Source {app_id: $app_id})
WITH count(s) AS sources
MATCH (k:Sink {app_id: $app_id})
WITH sources, count(k) AS sinks
OPTIONAL MATCH (t:Statement {app_id: $app_id}) WHERE t.tainted = true OR t.tainted = 'True'
WITH sources, sinks, count(t) AS tainted
OPTIONAL MATCH (:Source {app_id: $app_id})-[f:PRIVACY_RELATION {relation: 'FLOWS_TO'}]->(:Sink)
RETURN sources, sinks, tainted, count(f) AS flows;

// name: list_apps
// All apps currently loaded in this Neo4j instance (for the per-app picker).
MATCH (n) WHERE exists(n.app_id)
RETURN DISTINCT n.app_id AS app_id ORDER BY app_id;

// name: clear_app
// DESTRUCTIVE — delete every node/edge for one app (re-import cleanup). Run deliberately.
MATCH (n {app_id: $app_id}) DETACH DELETE n;
