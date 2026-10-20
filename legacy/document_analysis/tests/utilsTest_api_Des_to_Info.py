from tabulate import tabulate
from utilsTest_doc_des import get_android_doc_description
from utilsTest_clean_method_name import clean_method_name
from utilsTest_dpr_score import dpr_score
# Download English models
import stanza
stanza.download('en')

# Initialize the NLP pipeline
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

from difflib import SequenceMatcher

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

# Function: check if the object is present in method/class name
#def match_obj(obj, name_method, name_class):
    #return obj.lower() in (name_method + name_class).lower()


import math

# Function: check if the object is present in method/class name using dpr_score
def match_obj(obj, name_method, name_class):
    score_method = dpr_score(obj, name_method)
    score_class = dpr_score(obj, name_class)

    print("obj:", obj)
    print("name_method:", name_method)
    print("dpr_score (method):", score_method)
    print("name_class:", name_class)
    print("dpr_score (class):", score_class)

    # Check if either score is not NaN and greater than 0.5
    if (not math.isnan(score_method) and score_method > 0.5) or \
       (not math.isnan(score_class) and score_class > 0.5):
        return obj.lower() in (name_method + name_class).lower()

# Enhanced FindInfo: extract noun phrase rooted at object
def find_info(tree, dependencies, obj):
    if not obj:
        return ""

    for sent in dependencies.sentences:
        words = sent.words
        word_by_id = {w.id: w for w in words}
        obj_word = next((w for w in words if w.text.lower() == obj.lower()), None)
        if not obj_word:
            continue

        # Step 1: collect all words that are part of the NP rooted at the object
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

        # Step 2: include relevant modifiers pointing *to* the object (e.g., compounds)
        for w in words:
            if w.head == obj_word.id and w.deprel in {'compound', 'amod', 'nmod', 'case'}:
                phrase_ids.add(w.id)

        # Step 3: sort and form phrase
        sorted_words = sorted([word_by_id[i] for i in phrase_ids], key=lambda w: w.id)
        phrase = ' '.join(w.text for w in sorted_words)

        return phrase
    return obj

# Main pipeline
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
    
    # For testing, use the input list and display as a table.

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

print(tabulate(
    results,
    headers=[
        "Classname", "Cleaned_Classname", "Classname_dpr_score",
        "Methodname", "Methodname_dpr_score",
        "Cleaned_Methodname", "Description", "Personal Information"
    ],
    tablefmt="grid"
))