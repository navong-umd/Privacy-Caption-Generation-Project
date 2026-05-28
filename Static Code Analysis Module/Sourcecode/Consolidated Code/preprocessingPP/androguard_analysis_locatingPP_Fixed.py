"""
APK Privacy & Call-Graph Analyzer (Androguard + axmlparserpy) - WORKFLOW OVERVIEW

Input:
- INPUT_FOLDER/*.apk

Output (per APK, under OUTPUT_FOLDER/<apk_base>/):
- <apk_base>_permissions.csv                   (declared Android permissions)
- <apk_base>_layouts/*.xml                     (decoded res/layout XML files)

Console output:
- Manifest privacy-related meta-data values (if any)
- GUI privacy URLs (if any) + GUI element IDs containing “privacy” text
- Bytecode hits of WebView.loadUrl(...) followed by a const-string URL (best-effort)

Workflow implemented:
1) Iterate over APK files in INPUT_FOLDER.
2) Analyze each APK using Androguard AnalyzeAPK() to obtain:
   - a: APK object (files, manifest, resources)
   - d: DalvikVMFormat / DEX representation (not heavily used here)
   - dx: Analysis object (cross-references, method enumeration)
3) Export declared permissions:
   - Read a.get_permissions()
   - Save as <apk_base>_permissions.csv
4) Manifest privacy discovery (best-effort heuristic):
   - Parse AndroidManifest.xml as XML via a.get_android_manifest_xml()
   - Scan <meta-data> tags where android:name or android:value contains “privacy”
   - Collect matching android:value entries (often URLs or keys)
5) Resource string loading (best-effort):
   - Read res/values/strings.xml (if present and parseable)
   - Build a map of string resource keys -> lowercase text
6) Layout extraction (binary XML -> text XML):
   - For each res/layout/*.xml inside the APK:
     - Decode binary AXML using axmlparserpy.AXMLPrinter
     - Write decoded XML into OUTPUT_FOLDER/<apk_base>_layouts/
7) Layout analysis for privacy UI signals:
   - Parse each decoded layout XML with ElementTree
   - Resolve android:text="@string/..." using the loaded strings map
   - If resolved text contains “privacy”:
     - Collect android:href (only if it starts with http)
     - Collect android:id (store as view IDs)
8) Bytecode scan for privacy policy URLs loaded in WebView:
   - Iterate over dx.get_methods()
   - Skip ExternalMethod entries (framework/external)
   - Walk bytecode instructions:
     - Detect an invoke-* to WebView;->loadUrl
     - If seen, capture the next const-string as a candidate URL
   - Record hits as (method_full_name, url_string)
9) (Optional, currently commented out) Build a call graph and push to Neo4j:
   - build_call_graph(dx): nodes=methods, edges=CALLS based on xref_to
   - push_to_neo4j(): clears DB, inserts Method nodes + CALLS edges,
     then tags privacy-referencing methods with REFERENCES_PRIVACY_POLICY

Notes / limitations:
- Manifest and layout “privacy” checks are keyword heuristics; they will miss non-obvious patterns.
- Layout parsing relies on successfully decoding binary XML and on strings.xml being parseable.
- The WebView.loadUrl scan is simplistic:
  - it only captures direct const-string URLs following a loadUrl invoke,
  - it will miss URLs assembled dynamically or passed through variables/fields.
- The Neo4j push deletes all nodes in the target DB (MATCH (n) DETACH DELETE n).
"""

import os
import csv
import xml.etree.ElementTree as ET
from io import BytesIO

from androguard.misc import AnalyzeAPK
from androguard.core.analysis.analysis import ExternalMethod
from axmlparserpy.axmlprinter import AXMLPrinter
import networkx as nx
from neo4j import GraphDatabase

# === CONFIGURATION ===
INPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Static Code Analysis Module\input"
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Static Code Analysis Module\output"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "password"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === 1. Analyze APK ===
def analyze_apk(apk_path):
    a, d, dx = AnalyzeAPK(apk_path)
    return a, d, dx

# === 2. Save permissions ===
def save_permissions(a, apk_name, apk_output_folder):
    perms = a.get_permissions()
    out_csv = os.path.join(apk_output_folder, f"{apk_name}_permissions.csv")
    with open(out_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Permission"])
        for p in perms:
            writer.writerow([p])
    print(f"[+] Permissions saved to: {out_csv}")

# === 3. Extract manifest privacy
def extract_manifest_privacy(a):
    root = a.get_android_manifest_xml()
    urls = []
    for md in root.findall(".//meta-data"):
        name = md.get('{http://schemas.android.com/apk/res/android}name', '')
        val  = md.get('{http://schemas.android.com/apk/res/android}value', '')
        if 'privacy' in name.lower() or 'privacy' in val.lower():
            urls.append(val)
    return urls

# === 4. Extract layout files using axmlparserpy ===
def extract_layout_files(a, apk_name, apk_output_folder):
    temp_dir = os.path.join(apk_output_folder, f"{apk_name}_layouts")
    os.makedirs(temp_dir, exist_ok=True)

    layout_paths = []

    for file_name in a.get_files():
        if file_name.startswith("res/layout") and file_name.endswith(".xml"):
            try:
                bin_data = a.get_file(file_name)
                axml = AXMLPrinter(bin_data)
                xml_str = axml.get_xml_string()
                out_path = os.path.join(temp_dir, os.path.basename(file_name))
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(xml_str)
                layout_paths.append(out_path)
            except Exception as e:
                print(f"[!] Failed to decode {file_name}: {e}")
    return layout_paths

# === 5. Load strings.xml ===
def load_strings(a, apk_name, apk_output_folder):
    string_map = {}
    temp_dir = os.path.join(apk_output_folder, f"{apk_name}_strings")
    os.makedirs(temp_dir, exist_ok=True)
    try:
        xml_data = a.get_file("res/values/strings.xml")
        tree = ET.parse(BytesIO(xml_data))
        for elem in tree.findall("string"):
            key = elem.get("name")
            val = elem.text or ""
            string_map[key] = val.lower()
    except Exception as e:
        print(f"[!] strings.xml parsing failed: {e}")
    return string_map

# === 6. Analyze layout XMLs ===
def analyze_layouts(layout_paths, string_map):
    found_urls = []
    found_ids  = []
    for path in layout_paths:
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for e in root.iter():
                txt = e.attrib.get("{http://schemas.android.com/apk/res/android}text", "")
                txt = txt.lower()
                if txt.startswith("@string/"):
                    key = txt.split("/", 1)[1]
                    txt = string_map.get(key, "")
                if "privacy" in txt:
                    href = e.attrib.get("{http://schemas.android.com/apk/res/android}href", "")
                    if href.startswith("http"):
                        found_urls.append(href)
                    rid = e.attrib.get("{http://schemas.android.com/apk/res/android}id", "")
                    if rid:
                        found_ids.append(rid.replace("@+id/", ""))
        except Exception as e:
            print(f"[!] Failed to parse {path}: {e}")
    return found_urls, found_ids

# === 7. Bytecode scan for WebView.loadUrl(...) ===
def find_privacy_in_code(dx):
    hits = []
    for m in dx.get_methods():
        meth = m.get_method()
        if isinstance(meth, ExternalMethod):
            continue
        code_obj = meth.get_code()
        if code_obj is None:
            continue
        bc = code_obj.get_bc()
        saw_load = False
        for ins in bc.get_instructions():
            opname = ins.get_name()
            out = ins.get_output()
            if opname.startswith('invoke-') and 'WebView;->loadUrl' in out:
                saw_load = True
            if saw_load and ins.get_name() == 'const-string':
                url = ins.get_string()
                hits.append((m.full_name, url))
                break
    return hits

# === 8. Call Graph ===
def build_call_graph(dx):
    G = nx.DiGraph()
    for method in dx.get_methods():
        caller = method.full_name
        G.add_node(caller)
        for callee, _, _ in method.get_xref_to():
            callee_name = callee.full_name
            G.add_node(callee_name)
            G.add_edge(caller, callee_name)
    return G

# === 9. Push to Neo4j ===
def push_to_neo4j(G, privacy_methods):
    drv = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
    with drv.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        for name in G.nodes:
            session.run("MERGE (:Method {name:$n})", n=name)
        for u, v in G.edges:
            session.run("MATCH (a:Method {name:$u}), (b:Method {name:$v}) "
                        "MERGE (a)-[:CALLS]->(b)", u=u, v=v)
        for name, _ in privacy_methods:
            session.run("MATCH (m:Method {name:$n}) "
                        "MERGE (m)-[:REFERENCES_PRIVACY_POLICY]->(:PrivacyPolicy)", n=name)
    drv.close()
    print("[+] Graph pushed to Neo4j")

# === MAIN WORKFLOW ===
def main():
    for apk in os.listdir(INPUT_FOLDER):
        if not apk.lower().endswith(".apk"):
            continue
        path = os.path.join(INPUT_FOLDER, apk)
        base = os.path.splitext(apk)[0]
        print(f"\n[>] Processing {apk}")
        apk_output_folder = os.path.join(OUTPUT_FOLDER, base)
        os.makedirs(apk_output_folder, exist_ok=True)

        a, d, dx = analyze_apk(path)
        save_permissions(a, base, apk_output_folder)

        m_urls = extract_manifest_privacy(a)
        print("Manifest privacy URLs:", m_urls or "None")

        strs = load_strings(a, base, apk_output_folder)
        lays = extract_layout_files(a, base, apk_output_folder)
        l_urls, l_ids = analyze_layouts(lays, strs)
        print("GUI privacy URLs:", l_urls or "None")
        print("GUI elements:", l_ids or "None")

        code_hits = find_privacy_in_code(dx)
        if code_hits:
            print("Code privacy hits:")
            for m, src in code_hits:
                print(" -", m)
        else:
            print("No loadUrl privacy references found in code.")

        # Optional: Push to Neo4j
        # G = build_call_graph(dx)
        # push_to_neo4j(G, code_hits)

if __name__ == "__main__":
    main()
