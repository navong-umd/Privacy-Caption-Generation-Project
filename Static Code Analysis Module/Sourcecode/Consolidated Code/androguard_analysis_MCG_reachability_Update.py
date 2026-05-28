# -*- coding: utf-8 -*-
"""
Android MCG Reachability Analysis (Neo4j -> CSV)

- Loads (:Method)-[:CALLS]->(:Method) with optional (:Class)-[:HAS_METHOD]->(:Method)
- Infers app entry points (Android lifecycle + callbacks + zero in-degree fallback)
- BFS reachability to sensitive APIs/URIs
- Writes:
    - OUTPUT_FOLDER/reachability_check_full.csv
    - OUTPUT_FOLDER/reachability_check_feasible.csv

Requires: Python 3.11+, neo4j, pandas
    pip install neo4j pandas
"""

import os
import re
import csv
import time
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

CSV_FULL     = os.path.join(OUTPUT_FOLDER, "reachability_check_full.csv")
CSV_FEASIBLE = os.path.join(OUTPUT_FOLDER, "reachability_check_feasible.csv")

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
    "->onCreateOptionsMenu",    # not a true entry, but frequently top-level callback
    "->onStartCommand", "->onBind", "->onUnbind", "->onRebind",
    "->onReceive", "->onHandleWork", "->onHandleIntent", "->onJobStart", "->onJobStop",

    # Common UI callbacks
    "->onClick", "->onLongClick", "->onTouch", "->onItemClick", "->onItemSelected",
    "->onEditorAction", "->beforeTextChanged", "->onTextChanged", "->afterTextChanged",
    "->onCheckedChanged", "->onFocusChange", "->onMenuItemClick",
}

# Also accept by class suffix for coarse inference
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

# -------- Sensitive API rules (exact / endswith / regex on "pkg.Class->method") --------
# Precise hits and URI-oriented calls
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

# Broader prefix classifiers (fallbacks)
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

# ============ Helpers ============

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
    if "->" in s:
        left, right = s.split("->", 1)
        cls = normalize_class(left)
        m = right.split("(", 1)[0]
        return cls, m
    return "", s

def connect_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASS))

def load_graph(session):
    """
    Returns:
      method_info: eid -> {'name','signature','class'}  (raw strings from DB)
      adj: caller_eid -> [callee_eid,...]
      indeg: callee_eid -> count
    """
    method_info: Dict[str, dict] = {}
    adj: Dict[str, List[str]] = defaultdict(list)
    indeg: Dict[str, int] = defaultdict(int)

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
        src, dst = r["src"], r["dst"]
        adj[src].append(dst)
        indeg[dst] += 1

    return method_info, adj, indeg

def method_key_readable(meta: dict) -> str:
    """
    Returns a readable 'Class->method' if possible; otherwise falls back to meta['name'].
    """
    raw_cls = meta.get("class", "") or ""
    raw_name = meta.get("name", "") or ""
    norm_cls = normalize_class(raw_cls)

    # If name already composite 'X->y', try to normalize it
    if "->" in raw_name:
        c2, m2 = normalize_method_name(raw_name)
        if c2 or m2:
            return f"{c2}->{m2}" if c2 and m2 else raw_name.split("(")[0]

    # Otherwise combine class + simple method if we can
    if norm_cls and raw_name:
        # strip signature if present
        m = raw_name.split("->", 1)[-1].split("(", 1)[0]
        return f"{norm_cls}->{m}"
    return raw_name or ""

def identify_sensitive_nodes(method_info: Dict[str, dict]) -> Dict[str, Dict[str, str]]:
    """
    Map: method_eid -> {"category": ..., "label": ..., "api_or_uri": ..., "kind": "API"}
    Uses precise SENSITIVE_RULES first, then falls back to prefix/keywords classifier.
    """
    out: Dict[str, Dict[str, str]] = {}

    def match_sensitive(fullname: str):
        for kind, val, cat, label in SENSITIVE_RULES:
            if kind == "exact" and fullname == val:
                return cat, label
            elif kind == "endswith" and fullname.endswith(val):
                return cat, label
            elif kind == "regex" and re.search(val, fullname):
                return cat, label
        return None

    # First pass: exact / endswith / regex on normalized "Class->method"
    for mid, meta in method_info.items():
        key = method_key_readable(meta)  # aim for "pkg.Class->method"
        if not key:
            continue
        hit = match_sensitive(key)
        if hit:
            cat, label = hit
            out[mid] = {"category": cat, "label": label, "api_or_uri": key, "kind": "API"}

    # Second pass: broader prefixes/combos where not already captured
    for mid, meta in method_info.items():
        if mid in out:
            continue
        cls_norm = normalize_class(meta.get("class", "") or "")
        name_raw = meta.get("name", "") or ""
        c2, m2 = normalize_method_name(name_raw)

        # 1) class prefix
        cat = ""
        if cls_norm:
            for pref, ccat in SENSITIVE_PREFIXES.items():
                if cls_norm.startswith(pref):
                    cat = ccat
                    break

        # 2) specific combo
        if not cat:
            candidates = []
            if cls_norm and name_raw:
                m_simple = name_raw.split("->", 1)[-1].split("(", 1)[0]
                candidates.append(f"{cls_norm}->{m_simple}")
            if c2 and m2:
                candidates.append(f"{c2}->{m2}")
            for combo in candidates:
                if combo in SENSITIVE_METHODS:
                    cat = SENSITIVE_METHODS[combo]
                    break

        # 3) simple-name fallback
        if not cat:
            simple_hits = set()
            for token, ccat in SIMPLE_CLASS_KEYWORDS.items():
                if token and (token == cls_norm or token in cls_norm or token in name_raw):
                    simple_hits.add(ccat)
            if simple_hits:
                cat = sorted(simple_hits)[0]

        if cat:
            key = method_key_readable(meta) or (f"{cls_norm}->{m2}" if cls_norm and m2 else name_raw)
            out[mid] = {"category": cat, "label": cat, "api_or_uri": key, "kind": "API"}

    return out

def infer_entry_points(method_info: Dict[str, dict], indeg: Dict[str, int]) -> Set[str]:
    """
    Heuristic union of:
      - lifecycle/callback suffixes over readable "Class->method"
      - class suffixes (Activity/Service/Receiver/Provider)
      - zero in-degree methods
    """
    eps: Set[str] = set()

    # Lifecycle / callbacks using readable form
    for mid, meta in method_info.items():
        key = method_key_readable(meta)
        if key and any(key.endswith(suf) for suf in ENTRYPOINT_SUFFIXES):
            eps.add(mid)

    # Class-suffix heuristic & explicit callback names
    for mid, meta in method_info.items():
        raw_cls = meta.get("class", "") or ""
        name = meta.get("name", "") or ""
        cls_norm = normalize_class(raw_cls)
        if cls_norm.endswith(ENTRYPOINT_CLASS_SUFFIXES):
            eps.add(mid)
        # try short method names
        _, m2 = normalize_method_name(name)
        if m2 in ENTRYPOINT_METHOD_NAMES:
            eps.add(mid)

    # Zero in-degree fallback
    zero_indegree = {mid for mid in method_info.keys() if indeg.get(mid, 0) == 0}
    eps |= zero_indegree

    return eps

def multi_source_bfs(adj: Dict[str, List[str]],
                     sources: Set[str],
                     max_depth: int | None = None):
    """
    BFS from multiple sources. Returns (parent, origin, depth) maps keyed by node id.
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

def reconstruct_path(parent: Dict[str, str | None],
                     start_eid: str | None,
                     target_eid: str) -> List[str]:
    path_ids: List[str] = []
    cur = target_eid
    while cur is not None:
        path_ids.append(cur)
        cur = parent.get(cur)
    path_ids.reverse()
    return path_ids

def atomic_write_csv(df: pd.DataFrame, path: str) -> str:
    tmp = os.path.join(os.path.dirname(path), f".tmp_{os.getpid()}_{os.path.basename(path)}")
    df.to_csv(tmp, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)
    try:
        os.replace(tmp, path)
        return path
    except PermissionError:
        ts = time.strftime("%Y%m%d_%H%M%S")
        fb = os.path.join(os.path.dirname(path), f"{os.path.splitext(os.path.basename(path))[0]}_{ts}.csv")
        os.replace(tmp, fb)
        return fb

# ============ Main ============

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASS))
    with driver.session() as sess:
        method_info, adj, indeg = load_graph(sess)
        if not method_info:
            raise RuntimeError("No :Method nodes found in Neo4j.")
        total_edges = sum(len(v) for v in adj.values())
        if total_edges == 0:
            raise RuntimeError("No [:CALLS] edges found in Neo4j. Ensure the MCG is loaded.")

        entry_points = infer_entry_points(method_info, indeg)
        sens_map = identify_sensitive_nodes(method_info)
        sensitive_nodes = set(sens_map.keys())

        parent, origin, depth = multi_source_bfs(adj, entry_points, max_depth=MAX_DEPTH)

        # Build rows
        rows: List[Dict[str, object]] = []
        for mid in sorted(sensitive_nodes):
            meta = method_info.get(mid, {})
            reachable = mid in depth
            via = origin.get(mid)
            path_ids = reconstruct_path(parent, via, mid) if reachable else []
            # Render readable path
            path_strs = [method_key_readable(method_info.get(eid, {})) or eid for eid in path_ids]

            # entrypoint readable
            ep_cls = ""
            ep_mth = ""
            if via:
                ep_meta = method_info.get(via, {})
                ep_cls = normalize_class(ep_meta.get("class", "") or "")
                # prefer simple name
                _, ep_m = normalize_method_name(ep_meta.get("name", "") or "")
                ep_mth = ep_m or ep_meta.get("name", "") or ""

            info = sens_map[mid]
            rows.append({
                "api_or_uri": info["api_or_uri"],              # unified field
                "category": info["category"],
                "label": info["label"],
                "kind": info.get("kind", "API"),
                "reachable": "Feasible" if reachable else "Infeasible",
                "reached_from_entrypoint_class": ep_cls,
                "reached_from_entrypoint_method": ep_mth,
                "path_length": (len(path_ids) - 1) if path_ids else 0,
                "path": " -> ".join(path_strs),
                "dfs_depth": depth.get(mid, "")
            })

        # If no sensitive nodes found at all, emit a template row so CSV exists
        if not rows:
            rows.append({
                "api_or_uri": "",
                "category": "",
                "label": "",
                "kind": "API",
                "reachable": "Infeasible",
                "reached_from_entrypoint_class": "",
                "reached_from_entrypoint_method": "",
                "path_length": 0,
                "path": "",
                "dfs_depth": ""
            })

        # Write outputs
        df = pd.DataFrame(rows, columns=[
            "api_or_uri", "category", "label", "kind",
            "reachable", "reached_from_entrypoint_class", "reached_from_entrypoint_method",
            "path_length", "path", "dfs_depth"
        ]).drop_duplicates()

        written_full = atomic_write_csv(df, CSV_FULL)
        feas_df = df[df["reachable"] == "Feasible"].copy()
        written_feas = atomic_write_csv(feas_df, CSV_FEASIBLE)

        # Summary
        print(f"[✓] Reachability analysis complete.")
        print(f"[i] Methods: {len(method_info):,}  CALLS edges: {total_edges:,}")
        print(f"[i] Entry points considered: {len(entry_points):,}")
        print(f"[i] Sensitive methods detected in graph: {len(sensitive_nodes):,}")
        print(f"[→] Full CSV: {written_full} (rows: {len(df)})")
        print(f"[→] Feasible-only CSV: {written_feas} (rows: {len(feas_df)})")

    driver.close()

if __name__ == "__main__":
    main()
