# pip install tqdm (for processing bar)

from tabulate import tabulate
from tqdm import tqdm
from utils_doc_des import get_android_doc_description
from utils_clean_method_name import clean_method_name
from utils_dpr_score import dpr_score
import os
import math
import pandas as pd

# === PATHS ===
BASE_PATH = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Document Analysis Module"
OUTPUT_FOLDER = os.path.join(BASE_PATH, 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)  # Create output folder if not exists

# Download English models (only runs once)
import stanza
stanza.download('en')

# Initialize the NLP pipeline
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

# Function: extract verb (main predicate)
def extract_verb(tree, dependencies):
    for sent in dependencies.sentences:
        for word in sent.words:
            if word.upos == 'VERB' and word.head == 0:
                return word.text
    return ""

# Function: extract direct object
def extract_obj(tree, dependencies):
    for sent in dependencies.sentences:
        for word in sent.words:
            if word.deprel == 'obj':
                return word.text
    return ""

# Function: check if the object is present in method/class name using dpr_score
def match_obj(obj, name_method, name_class):
    score_method = dpr_score(obj, name_method)
    score_class = dpr_score(obj, name_class)

    if (not math.isnan(score_method) and score_method > 0.5) or \
       (not math.isnan(score_class) and score_class > 0.5):
        return obj.lower() in (name_method + name_class).lower()
    return False

# Extract extended noun phrase rooted at the object
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

# NLP Analysis Function
def identify_personal_info(desc, name_method, name_class):
    desc_nlp = nlp(desc)
    desc_tree = desc_nlp.sentences[0].constituency
    desc_dept = desc_nlp

    verb = extract_verb(desc_tree, desc_dept)
    obj = extract_obj(desc_tree, desc_dept)

    if match_obj(obj, name_method, name_class):
        return obj
    else:
        return find_info(desc_tree, desc_dept, obj)

# Input list
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

results = []

# Processing with progress bar
for class_name, method_name in tqdm(inputs, desc="Analyzing Methods", unit="item"):
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

# Output result table in console
print(tabulate(
    results,
    headers=[
        "Classname", "Cleaned_Classname", "Classname_dpr_score",
        "Methodname", "Methodname_dpr_score",
        "Cleaned_Methodname", "Description", "Personal Information"
    ],
    tablefmt="grid"
))

# Save results to CSV
output_csv_path = os.path.join(OUTPUT_FOLDER, "personal_info_results.csv")
df_results = pd.DataFrame(results, columns=[
    "Classname", "Cleaned_Classname", "Classname_dpr_score",
    "Methodname", "Methodname_dpr_score",
    "Cleaned_Methodname", "Description", "Personal Information"
])
df_results.to_csv(output_csv_path, index=False, encoding='utf-8-sig')

print(f"[+] Results saved to: {output_csv_path}")
