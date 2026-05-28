# 1. Install required packages:
# pip install google-play-scraper requests pandas tabulate chardet

import os
import pandas as pd
import requests
from google_play_scraper import search, app
from tabulate import tabulate
import chardet

# 2. Define input/output paths (update this to your local file system)
INPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\input\APK"
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"
APP_CSV_PATH = os.path.join(INPUT_FOLDER, 'app_name.csv')

# === FUNCTIONS ===

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def find_privacy_policy_url(app_name, lang='en', country='us'):
    try:
        results = search(app_name, lang=lang, country=country)
        if not results:
            return app_name, None
        top = results[0]
        pkg = top['appId']
        title = top['title']
        info = app(pkg, lang=lang, country=country)
        return title, info.get('privacyPolicy')
    except Exception as e:
        print(f"[!] Error fetching data for '{app_name}': {e}")
        return app_name, None

def is_url_reachable(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False

# === MAIN EXECUTION ===

# Detect encoding
encoding = detect_encoding(APP_CSV_PATH)
print(f"[i] Detected encoding: {encoding}")

# Read app names
df_in = pd.read_csv(APP_CSV_PATH, encoding=encoding)
if 'App Name' not in df_in.columns:
    raise ValueError("Input CSV must have an 'App Name' column.")

# Process each app
records = []
for name in df_in['App Name'].dropna().unique():
    print(f"[+] Searching: {name}")
    # Get category for current app
    matched_row = df_in[df_in['App Name'] == name]
    category = matched_row['Categories'].iloc[0] if not matched_row.empty else 'Unknown'
    title, policy_url = find_privacy_policy_url(name)
    status = 'Not Reachable'
    if policy_url:
        status = 'Reachable' if is_url_reachable(policy_url) else 'Not Reachable'
    records.append({
        'App Name': title,
        'Categories': category,
        'Privacy Policy URL': policy_url or 'Not Found',
        'Status': status
    })

# Save output
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
output_path = os.path.join(OUTPUT_FOLDER, 'app_privacy_policy.csv')
df_out = pd.DataFrame(records)
df_out.to_csv(output_path, index=False)

# Print summary
print(f"\n[✓] Saved {len(df_out)} entries to {output_path}")
print(tabulate(df_out, headers="keys", tablefmt="grid"))
