# Helper functions like dpr_score
import subprocess
import os

ESA_ROOT = r"C:\Users\2015n\OneDrive\Desktop\Static Code Analysis\Document Analysis Module\esalib"

def dpr_score(np_text: str, permission: str) -> float:
    try:
        run_analyzer_path = os.path.join(ESA_ROOT, "run_analyzer.bat")
        result = subprocess.run(
            [run_analyzer_path, np_text, permission],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        score = float(result.stdout.strip())
        return score
    except Exception as e:
        print(f"[!] Error running ESA analyzer: {e}")
        return -1.0

# Quick sanity check
print("contacts ↔ read contacts :", dpr_score("contacts", "READ_CONTACTS"))
print("camera   ↔ camera        :", dpr_score("camera", "CAMERA"))
print("This app accesses your contacts to send messages.", dpr_score("This app accesses your contacts to send messages.", "READ_CONTACTS"))

#Testing
print("Special Testing:")
print("map ↔ map:", dpr_score("map ", "map"))
print("map ↔ map view:", dpr_score("map ", "map view"))
print("map ↔ interactive map:", dpr_score("map", "interactive map"))

#'app access contact', 'contact'
print("app access contact ↔ contact:", dpr_score("app access contact", "contact"))
print("app access contact ↔ Read_Contact:", dpr_score("app access contact", "Read_Contact"))
print("getRunningAppProcesses ↔ list:", dpr_score("getRunningAppProcesses", "list"))
print("get Sim Serial Number ↔ number:", dpr_score("get Sim Serial Number", "number"))