"""
Android API Documentation Analysis for Personal Information Extraction
(UPDATED – structured description header)

Purpose:
This script analyzes Android framework APIs referenced as sensitive targets
(e.g., permission-protected or privacy-relevant methods) and extracts
potential personal information semantics from their official documentation.

Input:
- CSV file containing Android API references:
  - Column name must be either:
      * 'sensitive_target'
      * 'api_or_uri'
  - Accepted formats include:
      android.telephony.TelephonyManager->getDeviceId()
      android.accounts.AccountManager -> getPassword (sensitive API)

Output:
- Console table summarizing analysis results
- CSV file:
    output/personal_info_results.csv

Workflow implemented:
1) Load sensitive Android API targets from CSV
2) Parse fully qualified class and method names
3) Deduplicate class–method pairs
4) Retrieve official Android documentation descriptions
5) Clean class and method names for NLP comparison
6) Compute DPR (Description–Permission Relatedness) scores:
   - Class vs description
   - Method vs description
7) Apply dependency-based NLP (Stanza) to extract:
   - Main predicate
   - Direct object
   - Extended noun phrases
8) Identify candidate personal-information terms
9) Save structured results to CSV

NLP Stack:
- Stanza (tokenization, POS, lemmatization, dependency parsing)

Install:
pip install pandas tqdm stanza tabulate

Notes:
- Designed for large-scale static analysis pipelines
- Robust to missing documentation or parsing failures
- Suitable for privacy-policy generation and compliance research
"""

# pip install pandas tqdm stanza tabulate

import os
import re
import math
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate

from utils_doc_des import get_android_doc_description
from utils_clean_method_name import clean_method_name
from utils_dpr_score import dpr_score

# === PATHS ===
BASE_PATH = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Document Analysis Module"
INPUT_CSV = os.path.join(BASE_PATH, "input", "reachability_check_feasible.csv")
OUTPUT_FOLDER = os.path.join(BASE_PATH, "output")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === NLP setup (Stanza) ===
import stanza
# Safe to run repeatedly; models are cached locally
stanza.download('en', processors='tokenize,pos,lemma,depparse', verbose=False)
nlp = stanza.Pipeline(
    lang='en',
    processors='tokenize,pos,lemma,depparse',
    tokenize_no_ssplit=False,
    verbose=False
)

# ---------- Helpers for dependency-based extraction ----------

def extract_verb(_, dependencies):
    # Main predicate: VERB whose head == 0 (root)
    for sent in dependencies.sentences:
        for w in sent.words:
            if w.upos == 'VERB' and w.head == 0:
                return w.text
    return ""


def extract_obj(_, dependencies):
    # Direct object: dependency label 'obj'
    for sent in dependencies.sentences:
        for w in sent.words:
            if w.deprel == 'obj':
                return w.text
    return ""


def match_obj(obj, name_method, name_class):
    if not obj:
        return False
    score_method = dpr_score(obj, name_method)
    score_class = dpr_score(obj, name_class)
    if (not math.isnan(score_method) and score_method > 0.5) or \
       (not math.isnan(score_class) and score_class > 0.5):
        return obj.lower() in (name_method + name_class).lower()
    return False


def find_info(_, dependencies, obj):
    # Extended noun phrase rooted at object
    if not obj:
        return ""
    for sent in dependencies.sentences:
        words = sent.words
        by_id = {w.id: w for w in words}
        obj_word = next((w for w in words if w.text.lower() == obj.lower()), None)
        if not obj_word:
            continue

        phrase_ids = set()
        to_visit = [obj_word.id]

        while to_visit:
            cur = to_visit.pop()
            phrase_ids.add(cur)
            for w in words:
                if w.head == cur and w.deprel in {'compound', 'amod', 'nmod', 'case', 'obl'}:
                    to_visit.append(w.id)

        sorted_words = sorted((by_id[i] for i in phrase_ids), key=lambda x: x.id)
        return ' '.join(w.text for w in sorted_words)

    return obj


def identify_personal_info(desc, name_method, name_class):
    if not desc or not desc.strip():
        return ""
    doc = nlp(desc)
    if not doc.sentences:
        return ""
    obj = extract_obj(None, doc)
    if match_obj(obj, name_method, name_class):
        return obj
    return find_info(None, doc, obj)

# ---------- Input parsing from CSV ----------

def parse_sensitive_target(value: str):
    """
    Parse entries like:
      android.telephony.TelephonyManager->getDeviceId()
    Returns (class_name, method_name) or None.
    """
    if not isinstance(value, str):
        return None

    v = value.strip()
    v = v.split(' (', 1)[0]
    v = v.split(' - ', 1)[0]
    v = v.split('#', 1)[0]

    m = re.match(r'^\s*([A-Za-z0-9_$\.]+)\s*->\s*([A-Za-z0-9_$\.]+)', v)
    if not m:
        return None

    cls = m.group(1).strip()
    mth = re.split(r'[\(\.\s]', m.group(2).strip(), maxsplit=1)[0]

    if '.' not in cls or not mth:
        return None
    return cls, mth


def load_inputs_from_csv(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    if 'sensitive_target' in df.columns:
        col_name = 'sensitive_target'
    elif 'api_or_uri' in df.columns:
        col_name = 'api_or_uri'
    else:
        raise KeyError("CSV must contain 'sensitive_target' or 'api_or_uri'.")

    seen = set()
    results = []
    for raw in df[col_name].dropna():
        parsed = parse_sensitive_target(raw)
        if parsed and parsed not in seen:
            seen.add(parsed)
            results.append(parsed)

    return results

# ---------- Main processing ----------

def main():
    inputs = load_inputs_from_csv(INPUT_CSV)

    if not inputs:
        print("[!] No valid sensitive targets found.")
        return

    print(f"[+] Parsed {len(inputs)} unique class/method pairs.")

    results = []

    for class_name, method_name in tqdm(inputs, desc="Analyzing Methods", unit="item"):
        try:
            description = get_android_doc_description(class_name, method_name) or ""
        except Exception:
            description = ""

        cleaned_class = class_name.split('.')[-1]
        cleaned_method = clean_method_name(method_name)

        try:
            score_class = dpr_score(cleaned_class, description)
        except Exception:
            score_class = float('nan')

        try:
            score_method = dpr_score(cleaned_method, description)
        except Exception:
            score_method = float('nan')

        try:
            personal_info = identify_personal_info(description, cleaned_method, cleaned_class)
        except Exception:
            personal_info = ""

        results.append([
            class_name,
            cleaned_class,
            round(score_class, 3) if not math.isnan(score_class) else "NaN",
            method_name,
            round(score_method, 3) if not math.isnan(score_method) else "NaN",
            cleaned_method,
            description,
            personal_info
        ])

    print(tabulate(
        results,
        headers=[
            "Classname", "Cleaned_Classname", "Classname_dpr_score",
            "Methodname", "Methodname_dpr_score",
            "Cleaned_Methodname", "Description", "Personal Information"
        ],
        tablefmt="grid"
    ))

    output_csv = os.path.join(OUTPUT_FOLDER, "personal_info_results.csv")
    pd.DataFrame(results, columns=[
        "Classname", "Cleaned_Classname", "Classname_dpr_score",
        "Methodname", "Methodname_dpr_score",
        "Cleaned_Methodname", "Description", "Personal Information"
    ]).to_csv(output_csv, index=False, encoding="utf-8-sig")

    print(f"[✓] Results saved to: {output_csv}")


if __name__ == "__main__":
    main()
