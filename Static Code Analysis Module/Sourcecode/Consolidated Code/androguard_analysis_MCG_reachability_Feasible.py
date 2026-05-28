# -*- coding: utf-8 -*-
"""
MCG reachability -> sensitive API feasibility (with Dalvik normalization).
Relies only on:
  :Method (props: name?, signature?)
  :Class  (props: name?)
  (Class)-[:HAS_METHOD]->(Method)
  (Method)-[:CALLS]->(Method)
"""

import os
import sys
import time
from typing import Dict, List, Set, Tuple
from collections import defaultdict

import pandas as pd
from neo4j import GraphDatabase, basic_auth

# === CONFIG ===
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output_csv"
TARGET = os.path.join(OUTPUT_FOLDER, "reachability_check_full.csv")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

# Entry-point inference
ENTRYPOINT_CLASS_SUFFIXES = ("Activity", "Service", "BroadcastReceiver", "ContentProvider")
ENTRYPOINT_METHOD_NAMES = {
    "onCreate", "onStart", "onResume", "onPause", "onStop", "onDestroy",
    "onNewIntent", "onSaveInstanceState", "onRestoreInstanceState",
    "onCreateView", "onViewCreated", "onActivityCreated", "onAttach", "onDetach",
    "onStartCommand", "onBind", "onUnbind", "onRebind",
    "onReceive",
    "query", "insert", "update", "delete",
    "onRequestPermissionsResult", "onActivityResult",
    "onClick", "onLongClick", "onTouch", "onKey", "onFocusChange",
    "onCheckedChanged", "onTextChanged", "beforeTextChanged", "afterTextChanged",
}

# Sensitive classifiers
SENSITIVE_PREFIXES = {
    "android.location.": "Location",
    "android.telephony.": "Telephony",
    "android.hardware.camera": "Camera",
    "android.media.": "Media",
    "android.accounts.": "Accounts",
    "android.net.wifi.": "WiFi",
    "android.bluetooth.": "Bluetooth",
    "android.provider.ContactsContract": "Contacts",
    "android.provider.CalendarContract": "Calendar",
    "android.provider.CallLog": "CallLog",
    "android.provider.MediaStore": "MediaStore",
    "android.provider.Settings": "Settings",
    "android.webkit.WebView": "WebView",
    "android.content.ContentResolver": "ContentResolver",
    "android.net.Uri": "URI",
    "java.net.": "Network",
    "javax.net.": "Network",
    "okhttp3.": "Network",
    "org.apache.http.": "Network",
}
SENSITIVE_METHODS = {
    # “Class->method” combos (after normalization)
    "android.webkit.WebView->loadUrl": "WebView",
    "android.location.LocationManager->getLastKnownLocation": "Location",
    "android.location.LocationManager->requestLocationUpdates": "Location",
    "android.content.ContentResolver->query": "ContentResolver",
    "android.hardware.Camera->open": "Camera",
    "android.telephony.TelephonyManager->getDeviceId": "Telephony",
}

# If only simple names exist in your graph
SIMPLE_CLASS_KEYWORDS = {
    "WebView": "WebView",
    "LocationManager": "Location",
    "TelephonyManager": "Telephony",
    "ContentResolver": "ContentResolver",
    "Uri": "URI",
    "Camera": "Camera",
    "OkHttpClient": "Network",
    "HttpURLConnection": "Network",
    "BluetoothAdapter": "Bluetooth",
    "WifiManager": "WiFi",
}

def normalize_class(cls: str) -> str:
    """Dalvik → dotted: Landroid/webkit/WebView;  -> android.webkit.WebView"""
    if not cls:
        return ""
    s = cls.strip()
    if s.startswith("L"):
        s = s[1:]
    s = s.replace("/", ".")
    if s.endswith(";"):
        s = s[:-1]
    return s

def normalize_method_name(n: str) -> Tuple[str, str]:
    """
    Accepts either:
      - short name: 'loadUrl'  -> ('', 'loadUrl')
      - combo: 'android.webkit.WebView->loadUrl' -> ('android.webkit.WebView', 'loadUrl')
      - Dalvik: 'Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V'
                -> ('android.webkit.WebView', 'loadUrl')
    Returns (class_dotted_maybe_empty, method_simple_maybe_empty)
    """
    if not n:
        return "", ""
    s = n.strip()
    # Dalvik combo?
    if "->" in s:
        left, right = s.split("->", 1)
        # class side may be Dalvik or dotted
        cls = normalize_class(left)
        # method side may include signature
        m = right.split("(", 1)[0]
        return cls, m
    # just a short method name
    return "", s

def connect_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASS))

def load_graph(session):
    """
    method_info: eid -> {'name','signature','class'}
    adj: caller_eid -> [callee_eid,...]
    """
    method_info: Dict[str, dict] = {}
    adj: Dict[str, List[str]] = defaultdict(list)

    q_methods = """
    MATCH (m:Method)
    OPTIONAL MATCH (c:Class)-[:HAS_METHOD]->(m)
    RETURN elementId(m) AS mid, m.name AS name, m.signature AS signature, c.name AS class
    """
    for r in session.run(q_methods):
        method_info[r["mid"]] = {
            "name": r.get("name") or "",
            "signature": r.get("signature") or "",
            "class": r.get("class") or "",
        }

    q_edges = """
    MATCH (m1:Method)-[:CALLS]->(m2:Method)
    RETURN elementId(m1) AS src, elementId(m2) AS dst
    """
    for r in session.run(q_edges):
        adj[r["src"]].append(r["dst"])

    return method_info, adj

def infer_entrypoints(method_info: Dict[str, dict]) -> Set[str]:
    eps: Set[str] = set()
    for mid, meta in method_info.items():
        cls = meta.get("class", "") or ""
        name = meta.get("name", "") or ""

        if cls.endswith(ENTRYPOINT_CLASS_SUFFIXES):
            eps.add(mid)
            continue

        if name in ENTRYPOINT_METHOD_NAMES:
            eps.add(mid)
            continue

        # If name is Dalvik/composite, try to extract simple method
        cls2, m2 = normalize_method_name(name)
        if m2 in ENTRYPOINT_METHOD_NAMES:
            eps.add(mid)
            continue

    return eps

def classify_sensitive(callee_class_raw: str, callee_name_raw: str) -> str:
    """
    Classify using:
      1) normalized class prefix
      2) normalized "Class->method"
      3) simple-name fallback
    """
    cls = normalize_class(callee_class_raw)
    cls2, name2 = normalize_method_name(callee_name_raw)

    # 1) by class prefix
    if cls:
        for pref, cat in SENSITIVE_PREFIXES.items():
            if cls.startswith(pref):
                return cat

    # 2) by combo from either (cls + name) or (cls2 + name2)
    combo_candidates = []
    if cls and callee_name_raw:
        m_simple = callee_name_raw.split("->", 1)[-1].split("(", 1)[0]
        combo_candidates.append(f"{cls}->{m_simple}")
    if cls2 and name2:
        combo_candidates.append(f"{cls2}->{name2}")

    for combo in combo_candidates:
        if combo in SENSITIVE_METHODS:
            return SENSITIVE_METHODS[combo]

    # 3) simple-name fallback (no package info)
    simple_hits = set()
    for token, cat in SIMPLE_CLASS_KEYWORDS.items():
        if token and (token == cls or token in cls or token in callee_name_raw):
            simple_hits.add(cat)
    # choose a stable category if multiple
    if simple_hits:
        return sorted(simple_hits)[0]

    return ""

def collect_sensitive_edges(session) -> List[dict]:
    """
    Use only MCG + class links; get both callee class and callee name.
    """
    rows: List[dict] = []
    q = """
    MATCH (m1:Method)-[:CALLS]->(m2:Method)
    OPTIONAL MATCH (c1:Class)-[:HAS_METHOD]->(m1)
    OPTIONAL MATCH (c2:Class)-[:HAS_METHOD]->(m2)
    RETURN elementId(m1) AS caller_id, elementId(m2) AS callee_id,
           coalesce(c1.name,'') AS caller_cls, coalesce(m1.name,'') AS caller_name, coalesce(m1.signature,'') AS caller_sig,
           coalesce(c2.name,'') AS callee_cls, coalesce(m2.name,'') AS callee_name, coalesce(m2.signature,'') AS callee_sig
    """
    for r in session.run(q):
        cat = classify_sensitive(r["callee_cls"], r["callee_name"])
        if cat:
            rows.append({
                "caller_id": r["caller_id"],
                "caller_class": r["caller_cls"],
                "caller_method": r["caller_name"],
                "caller_signature": r["caller_sig"],
                "callee_id": r["callee_id"],
                "callee_class": normalize_class(r["callee_cls"]) or r["callee_cls"],
                "callee_method": r["callee_name"],
                "callee_signature": r["callee_sig"],
                "category": cat,
            })
    return rows

def dfs_from_entries(adj: Dict[str, List[str]], entries: Set[str]):
    reachable: Set[str] = set()
    parent: Dict[str, str] = {}
    depth: Dict[str, int] = {}

    stack: List[Tuple[str, int]] = []
    for e in entries:
        reachable.add(e); parent[e] = e; depth[e] = 0
        stack.append((e, 0))

    while stack:
        u, d = stack.pop()
        for v in adj.get(u, []):
            if v not in reachable:
                reachable.add(v); parent[v] = parent[u]; depth[v] = d + 1
                stack.append((v, d + 1))
    return reachable, parent, depth

def atomic_write_csv(df: pd.DataFrame, path: str) -> str:
    tmp = os.path.join(os.path.dirname(path), f".tmp_{os.getpid()}_{os.path.basename(path)}")
    df.to_csv(tmp, index=False, encoding="utf-8")
    try:
        os.replace(tmp, path)
        return path
    except PermissionError:
        ts = time.strftime("%Y%m%d_%H%M%S")
        fb = os.path.join(os.path.dirname(path), f"reachability_check_full_{ts}.csv")
        os.replace(tmp, fb)
        return fb

def main():
    driver = connect_driver()
    with driver.session() as s:
        method_info, adj = load_graph(s)
        entries = infer_entrypoints(method_info)
        print(f"[i] Inferred entry points: {len(entries)}")

        sens = collect_sensitive_edges(s)
        if not sens:
            print("[i] No sensitive calls detected. This usually means callee classes/methods "
                  "are stored in Dalvik form and not normalized, or SDK calls are not materialized as Method nodes.")
        reachable, src_of, depth = dfs_from_entries(adj, entries)

        out = []
        for rec in sens:
            callee_id = rec["callee_id"]
            feas = "Feasible" if callee_id in reachable else "Infeasible"
            src = src_of.get(callee_id, "")
            src_cls = method_info.get(src, {}).get("class", "") if src else ""
            src_name = method_info.get(src, {}).get("name", "") if src else ""

            api_str = f"{rec['callee_class']}->{rec['callee_method']}" if rec['callee_class'] or rec['callee_method'] else rec['callee_id']

            out.append({
                "stmt_id": "",  # no statement layer in this schema
                "class": rec["caller_class"],
                "method": rec["caller_method"],
                "signature": rec["caller_signature"],
                "api_or_uri": api_str,
                "category": rec["category"],
                "kind": "API",
                "reachable": feas,
                "reached_from_entrypoint_class": src_cls,
                "reached_from_entrypoint_method": src_name,
                "dfs_depth": depth.get(callee_id, ""),
            })

        # === Write outputs ===
        df = pd.DataFrame(out, columns=[
            "stmt_id", "class", "method", "signature",
            "api_or_uri", "category", "kind",
            "reachable", "reached_from_entrypoint_class",
            "reached_from_entrypoint_method", "dfs_depth"
        ]).drop_duplicates()

        written_full = atomic_write_csv(df, TARGET)
        print(f"[✓] Reachability results written to: {written_full}")
        print(f"[i] Total sensitive occurrences: {len(df)}")
        if len(df):
            print(f"[i] Feasible: {(df['reachable']=='Feasible').sum()} | Infeasible: {(df['reachable']=='Infeasible').sum()}")

        # --- Feasible-only CSV ---
        feasible_df = df[df["reachable"] == "Feasible"].copy()
        feasible_target = os.path.join(OUTPUT_FOLDER, "reachability_check_feasible.csv")
        written_feas = atomic_write_csv(feasible_df, feasible_target)
        print(f"[✓] Feasible-only results written to: {written_feas} (rows: {len(feasible_df)})")

    driver.close()

if __name__ == "__main__":
    main()
