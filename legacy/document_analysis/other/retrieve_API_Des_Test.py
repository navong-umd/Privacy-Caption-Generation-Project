#!pip install beautifulsoup4 requests
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

        anchor_id = f"{method_name}()"
        method_anchor = soup.find('a', id=anchor_id)
        if method_anchor:
            method_header = method_anchor.find_parent(lambda tag: tag.name in ['h2', 'h3', 'h4'])
        else:
            headers = soup.find_all(['h2', 'h3', 'h4'])
            method_header = None
            for h in headers:
                if method_name.lower() in h.get_text(strip=True).lower():
                    method_header = h
                    break

        if not method_header:
            return "Method description not found."

        paragraphs = []
        for p in method_header.find_all_next('p'):
            prev_header = p.find_previous(lambda tag: tag.name in ['h2', 'h3', 'h4'])
            if prev_header and prev_header == method_header:
                paragraphs.append(p)
            else:
                break

        def extract_first_sentence(text):
            match = re.search(r'([A-Z][^.!?]*[.!?])', text)
            if match:
                return match.group(1).strip()
            return text.strip()

        def classify_paragraph(p):
            if not p or p.name != 'p':
                return 'skip'
            text = p.get_text(strip=True)
            lower_text = text.lower()
            if p.get('class') and 'caution' in p.get('class'):
                return 'skip'
            if lower_text.startswith('note:') or lower_text.startswith('note'):
                return 'skip'
            if lower_text.startswith('this method was deprecated') or lower_text.startswith('deprecated'):
                return 'deprecated'
            if not text:
                return 'skip'
            return 'valid'

        valid_para = None
        deprecated_para = None

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


# === Testing the function with sample input ===

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
    results.append([class_name, method_name, description])

print(tabulate(results, headers=["Classname", "Methodname", "Description"], tablefmt="grid"))
