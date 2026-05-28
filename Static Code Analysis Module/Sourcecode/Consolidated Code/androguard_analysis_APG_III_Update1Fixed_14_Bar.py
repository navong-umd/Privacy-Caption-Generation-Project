import os
from pathlib import Path
from typing import List, Dict, Any, Iterable

import pandas as pd
import networkx as nx
from androguard.misc import AnalyzeAPK
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

# === CONFIG ===
INPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\input"
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output_csv"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

APK_FILE = next((f for f in os.listdir(INPUT_FOLDER) if f.endswith(".apk")), None)
if not APK_FILE:
    raise FileNotFoundError("No APK found in input folder.")
APK_PATH = os.path.join(INPUT_FOLDER, APK_FILE)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

BATCH_SIZE = 2000
WIPE_APP_BEFORE_INSERT = False  # True to delete previous data for the same app

# === ANALYZE APK ===
print(f"[+] Analyzing APK: {APK_PATH}")
a, d, dx = AnalyzeAPK(APK_PATH)
APP_ID = f"{a.get_package()}@{Path(APK_PATH).name}"

# === HELPERS ===
def cls_dots(raw: str) -> str:
    return raw.strip("L;").replace("/", ".")

def full_method_name(class_name: str, method_name: str) -> str:
    return f"{class_name}->{method_name}"

def parse_invoke_callee(output: str) -> str:
    if "->" in output:
        tokens = [t.strip() for t in output.split(",")]
        part = ""
        for tok in reversed(tokens):
            if "->" in tok:
                part = tok
                break
        if not part:
            part = tokens[-1]
        try:
            klass, rest = part.split("->", 1)
            return f"{cls_dots(klass)}->{rest.split('(')[0]}"
        except Exception:
            return part
    return ""

# === BUILD GRAPHS & PAYLOADS ===
AST = nx.DiGraph(); MCG = nx.DiGraph(); ICFG = nx.DiGraph(); DDG = nx.DiGraph()
method_edges = set()

classes_payload: List[Dict[str, Any]] = []
methods_payload: List[Dict[str, Any]] = []
has_method_payload: List[Dict[str, Any]] = []
statements_payload: List[Dict[str, Any]] = []
has_statement_payload: List[Dict[str, Any]] = []
calls_payload: List[Dict[str, Any]] = []
icfg_next_payload: List[Dict[str, Any]] = []
ddg_payload: List[Dict[str, Any]] = []

seen_class = set(); seen_method = set(); seen_stmt = set()
seen_has_method = set(); seen_has_stmt = set()
seen_call = set(); seen_icfg = set(); seen_ddg = set()

for method in dx.get_methods():
    if method.is_external():
        continue
    method_name = method.name
    class_name = cls_dots(method.class_name)
    full_m = full_method_name(class_name, method_name)

    AST.add_node(full_m, label="Method", type="Method", app_id=APP_ID)
    MCG.add_node(full_m, label="Method", type="Method", app_id=APP_ID)
    ICFG.add_node(full_m, label="Method", type="Method", app_id=APP_ID)

    if class_name not in seen_class:
        classes_payload.append({"name": class_name, "app_id": APP_ID}); seen_class.add(class_name)
    if full_m not in seen_method:
        methods_payload.append({"id": full_m, "name": method_name, "class": class_name,
                                "short_name": method_name, "app_id": APP_ID})
        seen_method.add(full_m)
    if (class_name, full_m) not in seen_has_method:
        has_method_payload.append({"class": class_name, "method": full_m, "app_id": APP_ID})
        seen_has_method.add((class_name, full_m))

    for _, call, _ in method.get_xref_to():
        callee_full = full_method_name(cls_dots(call.class_name), call.name)
        if (full_m, callee_full) not in method_edges:
            method_edges.add((full_m, callee_full))
            MCG.add_edge(full_m, callee_full, type="CALLS", app_id=APP_ID)
            if (full_m, callee_full) not in seen_call:
                calls_payload.append({"src": full_m, "dst": callee_full, "app_id": APP_ID})
                seen_call.add((full_m, callee_full))

    m = method.get_method()
    if not m:
        continue
    prev_stmt_id = None
    for i, ins in enumerate(m.get_instructions()):
        stmt_id = f"{full_m}_stmt_{i}"
        mnemonic = ins.get_name()
        code_text = ins.get_output() or ""
        callee = parse_invoke_callee(code_text) if mnemonic.startswith("invoke") else ""

        AST.add_node(stmt_id, label="Statement", type=mnemonic, code=code_text, callee=callee, app_id=APP_ID)
        AST.add_edge(full_m, stmt_id, type="HAS_STATEMENT", app_id=APP_ID)

        if prev_stmt_id is not None:
            ICFG.add_edge(prev_stmt_id, stmt_id, type="ICFG_NEXT", app_id=APP_ID)
        prev_stmt_id = stmt_id

        if stmt_id not in seen_stmt:
            statements_payload.append({"id": stmt_id, "idx": i, "code": code_text, "type": mnemonic,
                                       "callee": callee, "method_id": full_m, "app_id": APP_ID})
            seen_stmt.add(stmt_id)
        if (full_m, stmt_id) not in seen_has_stmt:
            has_statement_payload.append({"method": full_m, "stmt": stmt_id, "app_id": APP_ID})
            seen_has_stmt.add((full_m, stmt_id))
        if i > 0:
            prev = f"{full_m}_stmt_{i-1}"
            if (prev, stmt_id) not in seen_icfg:
                icfg_next_payload.append({"src": prev, "dst": stmt_id, "app_id": APP_ID})
                seen_icfg.add((prev, stmt_id))

def extract_written_variables(insn) -> str | None:
    name = insn.get_name()
    try:
        out = insn.get_output()
    except Exception:
        out = ""
    if not out:
        return None
    if name.startswith(("move", "iput", "aput", "sput", "astore", "istore")):
        return out.split(",")[0].strip()
    return None

def extract_read_variables(insn) -> List[str]:
    try:
        args = insn.get_output().split(",")
    except Exception:
        return []
    if len(args) <= 1:
        return []
    return [a.strip() for a in args[1:] if a.strip()]

for mref in dx.get_methods():
    if mref.is_external():
        continue
    m = mref.get_method()
    if not m:
        continue
    full_m = full_method_name(cls_dots(mref.class_name), mref.name)
    defs: Dict[str, str] = {}
    for i, ins in enumerate(m.get_instructions()):
        sid = f"{full_m}_stmt_{i}"
        w = extract_written_variables(ins)
        rs = extract_read_variables(ins)
        if w:
            defs[w] = sid
        for v in rs:
            if v in defs:
                prev = defs[v]
                DDG.add_edge(prev, sid, type="DATA_DEPENDS", app_id=APP_ID)
                if (prev, sid) not in seen_ddg:
                    ddg_payload.append({"src": prev, "dst": sid, "app_id": APP_ID})
                    seen_ddg.add((prev, sid))

print(f"[+] Package: {a.get_package()}")
print(f"[+] Total unique CALL edges (MCG): {len(method_edges)}")

# === EXPORT CSVs ===
def export_graph(graph: nx.DiGraph, name: str):
    nodes = [{"id": n,
              "label": d.get("label",""),
              "type": d.get("type",""),
              "code": d.get("code",""),
              "callee": d.get("callee",""),
              "app_id": d.get("app_id", APP_ID)} for n,d in graph.nodes(data=True)]
    pd.DataFrame(nodes).drop_duplicates().to_csv(os.path.join(OUTPUT_FOLDER, f"{name}_nodes.csv"), index=False, encoding="utf-8")

    edges = [{"start_id": u, "end_id": v,
              "type": d.get("type",""),
              "app_id": d.get("app_id", APP_ID)} for u,v,d in graph.edges(data=True)]
    pd.DataFrame(edges).drop_duplicates().to_csv(os.path.join(OUTPUT_FOLDER, f"{name}_edges.csv"), index=False, encoding="utf-8")
    print(f"[✓] Exported {name}: {len(nodes)} nodes, {len(edges)} edges")

export_graph(AST, "AST")
export_graph(MCG, "MCG")
export_graph(ICFG, "ICFG")
export_graph(DDG, "DDG")

# === NEO4J LOAD ===
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def chunked(it: Iterable[Dict[str, Any]], size: int):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) >= size:
            yield buf; buf = []
    if buf:
        yield buf

def cypher_run(query: str, params: Dict[str, Any] | None = None):
    with driver.session() as s:
        s.run(query, params or {})

def show_indexes() -> List[Dict[str, Any]]:
    q = "SHOW INDEXES YIELD name, type, entityType, labelsOrTypes, properties RETURN name, type, entityType, labelsOrTypes, properties"
    with driver.session() as s:
        return [dict(zip(["name","type","entityType","labelsOrTypes","properties"], r.values())) for r in s.run(q)]

def list_indexes_for(label: str, prop: str) -> List[str]:
    rows = show_indexes()
    names = []
    for r in rows:
        if r["entityType"] == "NODE" and r["labelsOrTypes"] == [label] and r["properties"] == [prop]:
            names.append(r["name"])
    return names

def show_constraints() -> List[Dict[str, Any]]:
    q = "SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties RETURN name, type, entityType, labelsOrTypes, properties"
    with driver.session() as s:
        return [dict(zip(["name","type","entityType","labelsOrTypes","properties"], r.values())) for r in s.run(q)]

def constraint_exists(label: str, prop: str) -> bool:
    for r in show_constraints():
        if r["entityType"] == "NODE" and r["labelsOrTypes"] == [label] and r["properties"] == [prop] and r["type"].upper() == "UNIQUENESS":
            return True
    return False

def drop_index_by_name(name: str):
    # Neo4j 5.x: DROP INDEX `name` IF EXISTS
    try:
        cypher_run(f"DROP INDEX `{name}` IF EXISTS")
    except Neo4jError:
        # fallback for older syntax
        cypher_run(f"DROP INDEX IF EXISTS `{name}`")

def ensure_unique_constraint(label: str, prop: str, constraint_name: str):
    # If uniqueness already exists, skip
    if constraint_exists(label, prop):
        return
    # Drop any simple index on the same key to avoid “IndexAlreadyExists”
    for idx_name in list_indexes_for(label, prop):
        drop_index_by_name(idx_name)
    # Create uniqueness (Neo4j 5 syntax)
    cypher_run(f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS FOR (n:{label}) REQUIRE n.{prop} IS UNIQUE")

def ensure_index(label: str, prop: str, name: str):
    cypher_run(f"CREATE INDEX {name} IF NOT EXISTS FOR (n:{label}) ON (n.{prop})")

def ensure_composite_index(label: str, props: list[str], name: str):
    props_expr = ", ".join([f"n.{p}" for p in props])
    cypher_run(f"CREATE INDEX {name} IF NOT EXISTS FOR (n:{label}) ON ({props_expr})")

if WIPE_APP_BEFORE_INSERT:
    print(f"[!] Deleting existing graph for app_id={APP_ID}")
    cypher_run("MATCH ()-[r {app_id:$app}]->() DELETE r", {"app": APP_ID})
    cypher_run("MATCH (n {app_id:$app}) DETACH DELETE n", {"app": APP_ID})

print("[+] Inserting into Neo4j...")

# ---- SCHEMA (idempotent & conflict-safe) ----
ensure_unique_constraint("Method", "id", "method_id_unique")
ensure_unique_constraint("Statement", "id", "stmt_id_unique")
# optional: ensure_unique_constraint("Class", "name", "class_name_unique")

# Helpful filters
ensure_index("Method", "app_id", "method_app_idx")
ensure_index("Statement", "app_id", "stmt_app_idx")
ensure_index("Class", "app_id", "class_app_idx")
ensure_composite_index("Class", ["name", "app_id"], "class_name_app_idx")

# ---- Upserts ----
q_class = """
UNWIND $rows AS row
MERGE (c:Class {name: row.name})
ON CREATE SET c.app_id = row.app_id
ON MATCH  SET c.app_id = row.app_id
"""
for b in chunked(classes_payload, BATCH_SIZE): cypher_run(q_class, {"rows": b})

q_method = """
UNWIND $rows AS row
MERGE (m:Method {id: row.id})
SET m.name = row.name, m.class = row.class, m.short_name = row.short_name, m.app_id = row.app_id
"""
for b in chunked(methods_payload, BATCH_SIZE): cypher_run(q_method, {"rows": b})

q_has_method = """
UNWIND $rows AS row
MATCH (c:Class {name: row.class}), (m:Method {id: row.method})
MERGE (c)-[:HAS_METHOD {app_id: row.app_id}]->(m)
"""
for b in chunked(has_method_payload, BATCH_SIZE): cypher_run(q_has_method, {"rows": b})

q_stmt = """
UNWIND $rows AS row
MERGE (s:Statement {id: row.id})
SET s.idx = row.idx, s.code = row.code, s.type = row.type, s.callee = row.callee,
    s.method_id = row.method_id, s.app_id = row.app_id
"""
for b in chunked(statements_payload, BATCH_SIZE): cypher_run(q_stmt, {"rows": b})

q_has_stmt = """
UNWIND $rows AS row
MATCH (m:Method {id: row.method}), (s:Statement {id: row.stmt})
MERGE (m)-[:HAS_STATEMENT {app_id: row.app_id}]->(s)
"""
for b in chunked(has_statement_payload, BATCH_SIZE): cypher_run(q_has_stmt, {"rows": b})

q_calls = """
UNWIND $rows AS row
MERGE (m1:Method {id: row.src})
MERGE (m2:Method {id: row.dst})
MERGE (m1)-[:CALLS {app_id: row.app_id}]->(m2)
"""
for b in chunked(calls_payload, BATCH_SIZE): cypher_run(q_calls, {"rows": b})

q_icfg = """
UNWIND $rows AS row
MERGE (s1:Statement {id: row.src})
MERGE (s2:Statement {id: row.dst})
MERGE (s1)-[:ICFG_NEXT {app_id: row.app_id}]->(s2)
"""
for b in chunked(icfg_next_payload, BATCH_SIZE): cypher_run(q_icfg, {"rows": b})

q_ddg = """
UNWIND $rows AS row
MERGE (s1:Statement {id: row.src})
MERGE (s2:Statement {id: row.dst})
MERGE (s1)-[:DATA_DEPENDS {app_id: row.app_id}]->(s2)
"""
for b in chunked(ddg_payload, BATCH_SIZE): cypher_run(q_ddg, {"rows": b})

print("[✓] Neo4j insert completed.")
print(f"[+] CALLS inserted (unique): {len(calls_payload)}")

# === SHOW ===
def show(title: str, query: str, params: Dict[str, Any], fmt):
    print(f"\n=== {title} ===")
    with driver.session() as s:
        rec = s.run(query, params).single()
        if rec: print(fmt(rec))
        else: print("No matching result.")

show(
    "AST Sample",
    """
    MATCH (c:Class)-[:HAS_METHOD {app_id:$app}]->(m:Method {app_id:$app})
          -[:HAS_STATEMENT {app_id:$app}]->(s:Statement {app_id:$app})
    WHERE s.type STARTS WITH 'invoke'
    RETURN c.name AS class, m.name AS method, m.class AS mclass, s.callee AS callee
    LIMIT 1
    """,
    {"app": APP_ID},
    lambda r: f"Class={r['class']}  Method={r['method']}  Callee={r['callee'] or ''}"
)

show(
    "MCG Sample",
    "MATCH (m1:Method {app_id:$app})-[:CALLS {app_id:$app}]->(m2:Method {app_id:$app}) RETURN m1.id AS m1, m2.id AS m2 LIMIT 1",
    {"app": APP_ID},
    lambda r: f"{r['m1']} -> {r['m2']}"
)

show(
    "ICFG Sample",
    "MATCH (s1:Statement {app_id:$app})-[:ICFG_NEXT {app_id:$app}]->(s2:Statement {app_id:$app}) RETURN s1.id AS id1, s2.id AS id2 LIMIT 1",
    {"app": APP_ID},
    lambda r: f"{r['id1']} -> {r['id2']}"
)

show(
    "DDG Sample",
    "MATCH (s1:Statement {app_id:$app})-[:DATA_DEPENDS {app_id:$app}]->(s2:Statement {app_id:$app}) RETURN s1.id AS id1, s2.id AS id2 LIMIT 1",
    {"app": APP_ID},
    lambda r: f"{r['id1']} -> {r['id2']}"
)

driver.close()
print("\n[✓] Done.")
