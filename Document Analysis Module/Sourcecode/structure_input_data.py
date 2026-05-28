import os
import pandas as pd
import re

# === SETUP LOCAL FOLDERS ===
# Replace this path with your actual local path
BASE_PATH = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Document Analysis Module"
INPUT_FOLDER = os.path.join(BASE_PATH, 'input')
OUTPUT_FOLDER = os.path.join(BASE_PATH, 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# === READ FILES ===
sink_file_path = os.path.join(INPUT_FOLDER, 'CatSinks_v0_9.txt')
source_file_path = os.path.join(INPUT_FOLDER, 'CatSources_v0_9.txt')

with open(sink_file_path, 'r', encoding='utf-8') as f:
    sink_data = f.read()

with open(source_file_path, 'r', encoding='utf-8') as f:
    source_data = f.read()

# === PARSE EACH LINE ===
sink_lines = [line.strip() for line in sink_data.strip().splitlines() if line.strip()]
source_lines = [line.strip() for line in source_data.strip().splitlines() if line.strip()]

def parse_to_columns(line):
    match = re.match(r"<([^:]+):\s+([^\s]+)\s+([^\(]+)\(([^)]*)\)> \(([^)]+)\)", line)
    if match:
        return {
            "Class Name": match.group(1),
            "Return Type": match.group(2),
            "Method Name": match.group(3),
            "Parameter Types": match.group(4),
            "Category": match.group(5)
        }
    return None

# === BUILD DATAFRAMES ===
sink_rows = [parse_to_columns(line) for line in sink_lines if parse_to_columns(line)]
source_rows = [parse_to_columns(line) for line in source_lines if parse_to_columns(line)]

sink_df = pd.DataFrame(sink_rows)
source_df = pd.DataFrame(source_rows)

# === EXPORT TO CSV ===
sink_df.to_csv(os.path.join(OUTPUT_FOLDER, 'formatted_sinks.csv'), index=False)
source_df.to_csv(os.path.join(OUTPUT_FOLDER, 'formatted_sources.csv'), index=False)

# === PREVIEW OUTPUT ===
print("Sink Table Preview:")
print(sink_df.head(), "\n")

print("Source Table Preview:")
print(source_df.head())
