#Install dependencies
#pip install pandas nltk

#Consolidate Code
#import library and prepare env.
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from tabulate import tabulate
from utilsTest_doc_des import get_android_doc_description

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
    results.append([class_name, cleaned_class_name, method_name, cleaned_method_name, description])

print(tabulate(results, headers=["Classname", "Cleaned_Classname", "Methodname", "Cleaned_Methodname", "Description"], tablefmt="grid"))