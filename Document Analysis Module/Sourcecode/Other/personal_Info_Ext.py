import os
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from tabulate import tabulate

# === Function to Get Android API Method Description ===

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

# === Load CSV and Extract Descriptions ===

# Update this to your actual path
BASE_PATH = r"C:\Users\2015n\OneDrive\Desktop\Static Code Analysis\Document Analysis Module"
INPUT_FOLDER = os.path.join(BASE_PATH, 'input')
output_folder = os.path.join(BASE_PATH, 'output')

# Define input file paths
sink_file = os.path.join(output_folder, 'formatted_sinks.csv')
source_file = os.path.join(output_folder, 'formatted_sources.csv')

# Load CSV files
sink_df = pd.read_csv(sink_file)
source_df = pd.read_csv(source_file)

# === Process Sink Inputs ===

print("\n=== Sink Table Preview ===")
sink_inputs = sink_df[['Class Name', 'Method Name']].values.tolist()
sink_results = []

for class_name, method_name in sink_inputs:
    description = get_android_doc_description(class_name, method_name)
    sink_results.append([class_name, method_name, description])

print(tabulate(sink_results, headers=["Classname", "Methodname", "Description"], tablefmt="grid"))

sink_results_df = pd.DataFrame(sink_results, columns=["Class Name", "Method Name", "Description"])
sink_output_csv = os.path.join(output_folder, 'sink_inputs_descriptions.csv')
sink_results_df.to_csv(sink_output_csv, index=False)

# === Process Source Inputs ===

print("\n=== Source Table Preview ===")
source_inputs = source_df[['Class Name', 'Method Name']].values.tolist()
source_results = []

for class_name, method_name in source_inputs:
    description = get_android_doc_description(class_name, method_name)
    source_results.append([class_name, method_name, description])

print(tabulate(source_results, headers=["Classname", "Methodname", "Description"], tablefmt="grid"))

source_results_df = pd.DataFrame(source_results, columns=["Class Name", "Method Name", "Description"])
source_output_csv = os.path.join(output_folder, 'source_inputs_descriptions.csv')
source_results_df.to_csv(source_output_csv, index=False)

print("\n== Descriptions saved to CSV files ==")
