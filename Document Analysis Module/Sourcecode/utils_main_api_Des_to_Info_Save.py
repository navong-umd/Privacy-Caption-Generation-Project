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
# This is safe to run repeatedly; Stanza skips re-download if the model exists
stanza.download('en', processors='tokenize,pos,lemma,depparse', verbose=False)
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse', tokenize_no_ssplit=False, verbose=False)

# ---------- Helpers for dependency-based extraction ----------

def extract_verb(_, dependencies):
    # main predicate: VERB whose head == 0 (root)
    for sent in dependencies.sentences:
        for w in sent.words:
            if w.upos == 'VERB' and w.head == 0:
                return w.text
    return ""

def extract_obj(_, dependencies):
    # direct object: 'obj' dependency
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
    if (not math.isnan(score_method) and score_method > 0.5) or (not math.isnan(score_class) and score_class > 0.5):
        return obj.lower() in (name_method + name_class).lower()
    return False

def find_info(_, dependencies, obj):
    # extended NP rooted at object (collect compounds/modifiers/obliques)
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

        for w in words:
            if w.head == obj_word.id and w.deprel in {'compound', 'amod', 'nmod', 'case'}:
                phrase_ids.add(w.id)

        sorted_words = sorted((by_id[i] for i in phrase_ids), key=lambda x: x.id)
        phrase = ' '.join(w.text for w in sorted_words)
        return phrase
    return obj

def identify_personal_info(desc, name_method, name_class):
    if not desc or not desc.strip():
        return ""
    doc = nlp(desc)
    # Use first sentence as anchor if present
    if not doc.sentences:
        return ""
    verb = extract_verb(None, doc)
    obj = extract_obj(None, doc)
    if match_obj(obj, name_method, name_class):
        return obj
    return find_info(None, doc, obj)

# ---------- Input parsing from CSV ----------

def parse_sensitive_target(value: str):
    """
    Accept forms like:
      'android.content.ClipboardManager->getPrimaryClip'
      'android.telephony.TelephonyManager->getDeviceId()'
      'android.accounts.AccountManager -> getPassword (sensitive API)'
    Returns (class_name, method_name) or None if not parseable.
    """
    if not isinstance(value, str):
        return None

    # Drop trailing comments like " (sensitive API ...)" or " - something"
    v = value.strip()
    v = v.split(' (', 1)[0]
    v = v.split(' - ', 1)[0]
    v = v.split('#', 1)[0]  # just in case of inline notes
    v = v.strip()

    # Core pattern: <fqcn> -> <methodName>(optional-args)
    m = re.match(r'^\s*([A-Za-z0-9_$\.]+)\s*->\s*([A-Za-z0-9_$\.]+)', v)
    if not m:
        return None

    cls = m.group(1).strip()
    mth = m.group(2).strip()
    # If method has parentheses or trailing qualifiers, keep simple name before '(' or '.'
    mth = re.split(r'[\(\.\s]', mth, maxsplit=1)[0]

    # Basic sanity
    if '.' not in cls or not mth:
        return None
    return (cls, mth)

def load_inputs_from_csv(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    df = pd.read_csv(csv_path, dtype=str)

    # Accept either 'sensitive_target' or 'api_or_uri'
    if 'sensitive_target' in df.columns:
        col_name = 'sensitive_target'
    elif 'api_or_uri' in df.columns:
        col_name = 'api_or_uri'
    else:
        raise KeyError("CSV must contain a column named 'sensitive_target' or 'api_or_uri'.")

    pairs = []
    for raw in df[col_name].dropna():
        parsed = parse_sensitive_target(raw)
        if parsed:
            pairs.append(parsed)

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for cls, mth in pairs:
        key = (cls, mth)
        if key not in seen:
            seen.add(key)
            deduped.append(key)

    return deduped

# ---------- Main processing ----------

def main():
    inputs = load_inputs_from_csv(INPUT_CSV)

    if not inputs:
        print("[!] No valid 'sensitive_target' entries parsed from input CSV.")
        return

    print(f"[+] Parsed {len(inputs)} unique class/method pairs from CSV.")

    results = []
    for class_name, method_name in tqdm(inputs, desc="Analyzing Methods", unit="item"):
        try:
            description = get_android_doc_description(class_name, method_name) or ""
        except Exception as e:
            description = ""
        cleaned_class_name = class_name.split('.')[-1]
        cleaned_method_name = clean_method_name(method_name)

        # DPR scores (guard against NaN)
        try:
            score_class = dpr_score(cleaned_class_name, description)
        except Exception:
            score_class = float('nan')
        try:
            score_method = dpr_score(cleaned_method_name, description)
        except Exception:
            score_method = float('nan')

        try:
            personal_info = identify_personal_info(description, cleaned_method_name, cleaned_class_name) or ""
        except Exception:
            personal_info = ""

        results.append([
            class_name,
            cleaned_class_name,
            round(score_class, 3) if not math.isnan(score_class) else "NaN",
            method_name,
            round(score_method, 3) if not math.isnan(score_method) else "NaN",
            cleaned_method_name,
            description,
            personal_info
        ])

    # Console table
    print(tabulate(
        results,
        headers=[
            "Classname", "Cleaned_Classname", "Classname_dpr_score",
            "Methodname", "Methodname_dpr_score",
            "Cleaned_Methodname", "Description", "Personal Information"
        ],
        tablefmt="grid"
    ))

    # CSV output
    output_csv_path = os.path.join(OUTPUT_FOLDER, "personal_info_results.csv")
    df_results = pd.DataFrame(results, columns=[
        "Classname", "Cleaned_Classname", "Classname_dpr_score",
        "Methodname", "Methodname_dpr_score",
        "Cleaned_Methodname", "Description", "Personal Information"
    ])
    df_results.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"[+] Results saved to: {output_csv_path}")

if __name__ == "__main__":
    main()
