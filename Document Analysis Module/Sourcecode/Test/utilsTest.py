#Install dependencies
#pip install stanza pandas tabulate

import math
import stanza
import pandas as pd
from tabulate import tabulate

#Consolidate Code
#import library and prepare env.
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# One-time NLTK download
nltk.download('punkt')
nltk.download('stopwords')

# Define stopwords
stop_words = set(stopwords.words('english'))

# Prefixes to identify and strip
method_prefixes = [
    "get", "set", "is", "has", "add", "remove", "update",
    "load", "save", "read", "write", "create", "find",
    "clear", "start", "stop", "reset", "show", "hide"
]

# Initialize NLP pipeline
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency,depparse', verbose=False)

#import library of BeautifulSoup Retreive Official API Description
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from tabulate import tabulate

def get_android_doc_description(class_name, method_name):
    class_path = class_name.split('$')[0].replace('.', '/')
    base_url = f'https://developer.android.com/reference/{quote(class_path)}'
    print("base_url:", base_url)

    try:
        res = requests.get(base_url, timeout=10)
        if res.status_code != 200:
            return "Documentation not found."

        soup = BeautifulSoup(res.text, 'html.parser')

        # First try: find an <a> whose id is the method name with "()" appended.
        anchor_id = f"{method_name}()"
        method_anchor = soup.find('a', id=anchor_id)
        if method_anchor:
            method_header = method_anchor.find_parent(lambda tag: tag.name in ['h2', 'h3', 'h4'])
        else:
            # Fallback: search for a header containing the method name text
            headers = soup.find_all(['h2','h3','h4'])
            method_header = None
            for h in headers:
                if method_name.lower() in h.get_text(strip=True).lower():
                    method_header = h
                    break

        if not method_header:
            return "Method description not found."

        # Gather all paragraphs that follow the header and occur before the next header.
        paragraphs = []
        for p in method_header.find_all_next('p'):
            # Check if the previous header (h2/h3/h4) of this paragraph is the same as method_header.
            prev_header = p.find_previous(lambda tag: tag.name in ['h2','h3','h4'])
            if prev_header and prev_header == method_header:
                paragraphs.append(p)
            else:
                break  # We've left the current method section

        def extract_first_sentence(text):
            # Try to capture a sentence ending with . ! or ?
            match = re.search(r'([A-Z][^.!?]*[.!?])', text)
            if match:
                return match.group(1).strip()
            return text.strip()

        def classify_paragraph(p):
            if not p or p.name != 'p':
                return 'skip'
            text = p.get_text(strip=True)
            lower_text = text.lower()
            # Skip paragraphs that start with "Note:" or "Note" or contain a caution indicator
            if p.get('class') and 'caution' in p.get('class'):
                return 'skip'
            if lower_text.startswith('note:') or lower_text.startswith('note'):
                return 'skip'
            # If the paragraph begins with a deprecation message, mark it as "deprecated"
            if lower_text.startswith('this method was deprecated') or lower_text.startswith('deprecated'):
                return 'deprecated'
            if not text:
                return 'skip'
            return 'valid'

        valid_para = None
        deprecated_para = None

        # Look over all paragraphs in this section.
        for p in paragraphs:
            cls = classify_paragraph(p)
            if cls == 'valid' and valid_para is None:
                valid_para = p
            elif cls == 'deprecated' and deprecated_para is None:
                deprecated_para = p

        if valid_para:
            return extract_first_sentence(valid_para.get_text(strip=True))
        elif deprecated_para:
            return extract_first_sentence(deprecated_para.get_text(strip=True))
        else:
            return "Method description not found."

    except Exception as e:
        return f"Error: {str(e)}"


# Split prefix and return both prefix and stripped name
def split_prefix(method_name: str):
    for prefix in method_prefixes:
        if method_name.startswith(prefix):
            return prefix, method_name[len(prefix):]
    return None, method_name

# Split CamelCase into individual words
def split_camel_case(name: str):
    import re
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)

# Clean and tokenize stripped method name
def clean_method_name(method_name: str):
    _, stripped_name = split_prefix(method_name)
    words = split_camel_case(stripped_name)
    filtered = [w for w in words if w.lower() not in stop_words]
    return ' '.join(filtered)


def dpr_score(a, b):
    # Very basic similarity score, replace with ESA or another model
    if not a or not b:
        return float('nan')
    a, b = a.lower(), b.lower()
    return len(set(a.split()) & set(b.split())) / max(1, len(set(a.split()) | set(b.split())))

# === NLP Extraction Functions ===

def extract_verb(tree, dependencies):
    for sent in dependencies.sentences:
        for word in sent.words:
            if word.upos == 'VERB' and word.head == 0:
                return word.text
    return ""

def extract_obj(tree, dependencies):
    for sent in dependencies.sentences:
        for word in sent.words:
            if word.deprel == 'obj':
                return word.text
    return ""

def match_obj(obj, name_method, name_class):
    score_method = dpr_score(obj, name_method)
    score_class = dpr_score(obj, name_class)

    print("obj:", obj)
    print("name_method:", name_method)
    print("dpr_score (method):", score_method)
    print("name_class:", name_class)
    print("dpr_score (class):", score_class)

    if (not math.isnan(score_method) and score_method > 0.5) or \
       (not math.isnan(score_class) and score_class > 0.5):
        return obj.lower() in (name_method + name_class).lower()
    return False

def find_info(tree, dependencies, obj):
    if not obj:
        return ""

    for sent in dependencies.sentences:
        words = sent.words
        word_by_id = {w.id: w for w in words}
        obj_word = next((w for w in words if w.text.lower() == obj.lower()), None)
        if not obj_word:
            continue

        phrase_ids = set()
        to_visit = [obj_word.id]

        while to_visit:
            current_id = to_visit.pop()
            phrase_ids.add(current_id)
            for w in words:
                if w.head == current_id and w.deprel in {
                    'compound', 'amod', 'nmod', 'case', 'obl'
                }:
                    to_visit.append(w.id)

        for w in words:
            if w.head == obj_word.id and w.deprel in {'compound', 'amod', 'nmod', 'case'}:
                phrase_ids.add(w.id)

        sorted_words = sorted([word_by_id[i] for i in phrase_ids], key=lambda w: w.id)
        phrase = ' '.join(w.text for w in sorted_words)
        return phrase

    return obj

def identify_personal_info(desc, name_method, name_class):
    desc_nlp = nlp(desc)
    desc_tree = desc_nlp.sentences[0].constituency
    desc_dept = desc_nlp

    verb = extract_verb(desc_tree, desc_dept)
    obj = extract_obj(desc_tree, desc_dept)

    if match_obj(obj, name_method, name_class):
        return obj
    else:
        info = find_info(desc_tree, desc_dept, obj)
        return info

# === Test Inputs ===
inputs = [
    ("android.app.ActivityManager", "getRunningAppProcesses"),
    ("android.app.ActivityManager", "getRunningTasks"),
    ("android.telephony.TelephonyManager", "getDeviceId"),
    ("android.telephony.TelephonyManager", "getDeviceSoftwareVersion"),
    ("android.telephony.TelephonyManager", "getVoiceMailNumber"),
    ("android.accounts.AccountManager", "getPassword"),
    ("android.accounts.AccountManager", "getAuthenticatorTypes"),
    ("android.accounts.AccountManager", "setUserData"),
    ("android.bluetooth.BluetoothDevice", "setPairingConfirmation"),
    ("android.app.ActivityManagerProxy", "getTaskForActivity"),
    ("android.media.Metadata", "getLong"),
    ("com.android.browser.DeviceAccountLogin", "getAccountNames"),
    ("android.telephony.TelephonyManager", "getSimSerialNumber"),
    ("android.telephony.TelephonyManager", "getSubscriberId")
]

# === Run pipeline ===
results = []

for class_name, method_name in inputs:
    description = get_android_doc_description(class_name, method_name)
    cleaned_class_name = class_name.split('.')[-1]
    cleaned_method_name = clean_method_name(method_name)

    score_class = dpr_score(cleaned_class_name, description)
    score_method = dpr_score(cleaned_method_name, description)

    personal_info = identify_personal_info(description, cleaned_method_name, cleaned_class_name)

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

# === Display Table ===
print(tabulate(
    results,
    headers=[
        "Classname", "Cleaned_Classname", "Classname_dpr_score",
        "Methodname", "Methodname_dpr_score",
        "Cleaned_Methodname", "Description", "Personal Information"
    ],
    tablefmt="grid"
))
