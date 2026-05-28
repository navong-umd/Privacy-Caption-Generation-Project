# -*- coding: utf-8 -*-
"""
Android MCG Reachability Analysis (Neo4j -> CSV)

- Pulls (:Method)-[:CALLS]->(:Method) from Neo4j
- Infers app entry points (Android lifecycle + callbacks + zero in-degree)
- BFS reachability to sensitive APIs/URIs
- Writes OUTPUT_FOLDER/reachability_check.csv

Requires: Python 3.11+, neo4j, pandas
    pip install neo4j pandas
"""

import os
import re
import csv
from collections import deque, defaultdict
from typing import Dict, List, Tuple, Set
import pandas as pd
from neo4j import GraphDatabase, basic_auth

# ============ CONFIG ============
NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output_csv"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_FOLDER, "reachability_check.csv")

# To avoid runaway traversals; set None for unlimited
MAX_DEPTH = 50

# -------- Entry points (suffix match on fully-qualified key "pkg.Class->method") --------
ENTRYPOINT_SUFFIXES: Set[str] = {
    # Activities / Fragments
    "->onCreate", "->onStart", "->onResume", "->onPause", "->onStop", "->onDestroy",
    "->onRestart", "->onSaveInstanceState", "->onRestoreInstanceState",
    "->onCreateView", "->onViewCreated", "->onAttach", "->onDetach",
    "->onActivityResult", "->onRequestPermissionsResult", "->onNewIntent",

    # Services / Receivers / Jobs / Providers
    "->onCreateOptionsMenu",   # not a true entry, but frequently top-level callback
    "->onStartCommand", "->onBind", "->onUnbind", "->onRebind",
    "->onReceive", "->onHandleWork", "->onHandleIntent", "->onJobStart", "->onJobStop",

    # Common UI callbacks
    "->onClick", "->onLongClick", "->onTouch", "->onItemClick", "->onItemSelected",
    "->onEditorAction", "->beforeTextChanged", "->onTextChanged", "->afterTextChanged",
    "->onCheckedChanged", "->onFocusChange", "->onMenuItemClick",
}

# -------- Sensitive API rules (exact / endswith / regex on "pkg.Class->method") --------
SENSITIVE_RULES: List[Tuple[str, str, str, str]] = [
    # WebView / URI
    ("exact",   "android.webkit.WebView->loadUrl",                         "Network/URI", "WebView.loadUrl"),
    ("endswith","->loadData",                                              "Network/URI", "WebView.loadData"),
    ("endswith","->loadDataWithBaseURL",                                   "Network/URI", "WebView.loadDataWithBaseURL"),

    # Networking
    ("exact",   "java.net.URL->openConnection",                            "Network",     "URL.openConnection"),
    ("endswith","->openConnection",                                        "Network",     "openConnection"),
    ("regex",   r"^okhttp3\.",                                             "Network",     "OkHttp"),
    ("regex",   r"^retrofit2\.",                                           "Network",     "Retrofit"),
    ("regex",   r"^org\.apache\.http\.",                                   "Network",     "ApacheHttp"),

    # Telephony / IDs
    ("exact",   "android.telephony.TelephonyManager->getDeviceId",         "Identifiers", "getDeviceId"),
    ("exact",   "android.telephony.TelephonyManager->getImei",             "Identifiers", "getImei"),
    ("exact",   "android.telephony.TelephonyManager->getSubscriberId",     "Identifiers", "getSubscriberId"),
    ("exact",   "android.telephony.TelephonyManager->getLine1Number",      "Identifiers", "getLine1Number"),
    ("exact",   "android.telephony.TelephonyManager->getSimSerialNumber",  "Identifiers", "getSimSerialNumber"),

    # Location
    ("regex",   r"^android\.location\.LocationManager->(requestLocationUpdates|getLastKnownLocation)",
                                                                            "Location",    "LocationManager"),

    # Accounts
    ("regex",   r"^android\.accounts\.AccountManager->(getAccounts|getAccountsByType)",
                                                                            "Accounts",    "AccountManager"),

    # ContentResolvers / Providers
    ("regex",   r"^android\.content\.ContentResolver->(query|insert|update|delete)",
                                                                            "ContentProvider", "ContentResolver"),
    ("regex",   r"^android\.provider\.",                                   "ContentProvider", "AndroidProviderAPI"),

    # Camera / Mic
    ("regex",   r"^android\.hardware\.Camera->(open|openLegacy)",          "Camera",       "Camera.open"),
    ("regex",   r"^android\.hardware\.camera2\.",                          "Camera",       "Camera2"),
    ("regex",   r"^android\.media\.MediaRecorder->start",                  "Microphone",   "MediaRecorder.start"),
    ("regex",   r"^android\.media\.AudioRecord->startRecording",           "Microphone",   "AudioRecord.startRecording"),

    # Clipboard
    ("exact",   "android.content.ClipboardManager->getPrimaryClip",        "Clipboard",    "Clipboard.getPrimaryClip"),
    ("exact",   "android.content.ClipboardManager->getText",               "Clipboard",    "Clipboard.getText"),

    # SMS
    ("regex",   r"^android\.telephony\.SmsManager->(sendTextMessage|sendMultipartTextMessage)",
                                                                            "Messaging",    "SmsManager.send"),

    # URI helpers
    ("exact",   "android.net.Uri->parse",                                  "URI",          "Uri.parse"),
    ("exact",   "android.content.Intent->setData",                         "URI",          "Intent.setData"),
]

# ================= Neo4j helpers =================

def _driver():
    return GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASS))

def fetch_mcg(driver) -> Tuple[Set[str], List[Tuple[str, str]]]:
    """
    Return:
      methods: set of method keys (coalesce(m.name, m.id))
      edges:   list of (src, dst) for [:CALLS]
    """
    q_edges = """
    MATCH (m1:Method)-[:CALLS]->(m2:Method)
    RETURN coalesce(m1.name, m1.id) AS src_name, coalesce(m2.name, m2.id) AS dst_name
    """
    q_methods = """
    MATCH (m:Method)
    RETURN DISTINCT coalesce(m.name, m.id) AS name
    """
    with driver.session() as sess:
        edges = [(r["src_name"], r["dst_name"]) for r in sess.run(q_edges)]
        methods = {r["name"] for r in sess.run(q_methods)}
    return methods, edges

def fetch_zero_indegree_entries(driver) -> Set[str]:
    """
    Methods with no incoming CALLS edges (robust, Neo4j 4.4+/5).
    """
    q = """
    MATCH (m:Method)
    WHERE NOT EXISTS {
        MATCH (:Method)-[:CALLS]->(m)
    }
    RETURN coalesce(m.name, m.id) AS name
    """
    with driver.session() as sess:
        return {r["name"] for r in sess.run(q)}

# ================= Graph + analysis =================

def build_adj(edges: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    adj: Dict[str, List[str]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    return adj

def identify_sensitive_nodes(all_methods: Set[str]) -> Dict[str, Dict[str, str]]:
    """
    Map: method_key -> {"category": ..., "label": ...} for methods present in graph
    """
    out: Dict[str, Dict[str, str]] = {}

    def match_sensitive(method_name: str):
        for kind, val, cat, label in SENSITIVE_RULES:
            if kind == "exact" and method_name == val:
                return cat, label
            elif kind == "endswith" and method_name.endswith(val):
                return cat, label
            elif kind == "regex" and re.search(val, method_name):
                return cat, label
        return None

    for m in all_methods:
        hit = match_sensitive(m)
        if hit:
            cat, label = hit
            out[m] = {"category": cat, "label": label}
    return out

def infer_entry_points(all_methods: Set[str], zero_indegree: Set[str]) -> Set[str]:
    ep = {m for m in all_methods if any(m.endswith(s) for s in ENTRYPOINT_SUFFIXES)}
    ep |= zero_indegree
    # Fallback: if still empty, pick nodes with no incoming edges computed locally
    return ep

def multi_source_bfs(adj: Dict[str, List[str]],
                     sources: Set[str],
                     max_depth: int | None = None):
    """
    BFS from multiple sources. Returns (parent, origin, depth) maps.
    """
    parent: Dict[str, str | None] = {}
    origin: Dict[str, str] = {}
    depth: Dict[str, int] = {}

    q = deque()
    for s in sources:
        if s in depth:
            continue
        depth[s] = 0
        origin[s] = s
        parent[s] = None
        q.append(s)

    while q:
        u = q.popleft()
        if max_depth is not None and depth[u] >= max_depth:
            continue
        for v in adj.get(u, []):
            if v not in depth:
                depth[v] = depth[u] + 1
                parent[v] = u
                origin[v] = origin[u]
                q.append(v)
    return parent, origin, depth

def reconstruct_path(parent: Dict[str, str | None], entry: str | None, target: str) -> List[str]:
    path: List[str] = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = parent.get(cur)
    path.reverse()
    # If entry provided and path[0] != entry, we still return shortest found path.
    return path

# ================= Main =================

def main():
    driver = _driver()

    # Pull MCG
    all_methods, edges = fetch_mcg(driver)
    if not all_methods:
        raise RuntimeError("No :Method nodes found in Neo4j.")
    if not edges:
        raise RuntimeError("No [:CALLS] edges found in Neo4j. Ensure the MCG is loaded.")

    adj = build_adj(edges)

    # Entry points = lifecycle/callback suffixes U zero-indegree
    zero_indegree = fetch_zero_indegree_entries(driver)
    entry_points = infer_entry_points(all_methods, zero_indegree)
    if not entry_points:
        # Local fallback using edges
        incoming = defaultdict(int)
        for u, v in edges:
            incoming[v] += 1
        entry_points = {m for m in all_methods if incoming[m] == 0}

    # Sensitive nodes present in graph
    sens_map = identify_sensitive_nodes(all_methods)
    sensitive_nodes = set(sens_map.keys())

    # BFS
    parent, origin, depth = multi_source_bfs(adj, entry_points, max_depth=MAX_DEPTH)

    rows: List[Dict[str, str | int]] = []
    for s in sorted(sensitive_nodes):
        reachable = s in depth
        status = "Feasible" if reachable else "Infeasible"
        via = origin.get(s)
        path = reconstruct_path(parent, via, s) if reachable else []
        rows.append({
            "sensitive_target": s,                           # e.g., android.webkit.WebView->loadUrl
            "category": sens_map[s]["category"],
            "label": sens_map[s]["label"],
            "reachable": status,                             # Feasible / Infeasible
            "via_entry_point": via if via else "",
            "path_length": (len(path) - 1) if path else 0,   # edge count
            "path": " -> ".join(path) if path else ""
        })

    # If no sensitive nodes found at all, emit a template row so CSV exists
    if not rows:
        rows.append({
            "sensitive_target": "",
            "category": "",
            "label": "",
            "reachable": "Infeasible",
            "via_entry_point": "",
            "path_length": 0,
            "path": ""
        })

    df = pd.DataFrame(rows, columns=[
        "sensitive_target", "category", "label",
        "reachable", "via_entry_point", "path_length", "path"
    ])
    df.to_csv(OUTPUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)

    print(f"[✓] Reachability analysis complete.")
    print(f"[i] Methods: {len(all_methods):,}  CALLS edges: {len(edges):,}")
    print(f"[i] Entry points considered: {len(entry_points):,}")
    print(f"[i] Sensitive methods detected in graph: {len(sensitive_nodes):,}")
    print(f"[→] CSV written: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
