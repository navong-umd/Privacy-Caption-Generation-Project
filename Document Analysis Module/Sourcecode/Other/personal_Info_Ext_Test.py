import subprocess
import os

# Local path to ESA root directory
ESA_ROOT = r"C:\Users\2015n\OneDrive\Desktop\Static Code Analysis\Document Analysis Module\esalib"

def dpr_score(np_text: str, permission: str) -> float:
    """
    Calls the Java ESA analyzer tool to compute similarity score.
    Assumes 'run_analyzer' is a .bat or PowerShell script in ESA_ROOT.
    """
    perm_query = permission.lower().replace('_', ' ')
    
    # Construct command to call the analyzer (Windows format)
    run_analyzer_path = os.path.join(ESA_ROOT, "run_analyzer.bat")  # or .ps1 if using PowerShell
    cmd = [run_analyzer_path, np_text, perm_query]

    try:
        output = subprocess.check_output(cmd, cwd=ESA_ROOT, stderr=subprocess.DEVNULL, text=True, shell=True)
        lines = output.strip().splitlines()
        score_str = lines[-1]
        return float(score_str)
    except subprocess.CalledProcessError as e:
        print("[!] Error running ESA analyzer:", e)
        return -1.0

# === TEST CASES ===

print("contacts ↔ read contacts :", dpr_score("contacts", "READ_CONTACTS"))
print("camera   ↔ camera        :", dpr_score("camera", "CAMERA"))
print("This app accesses your contacts to send messages.", dpr_score("This app accesses your contacts to send messages.", "READ_CONTACTS"))

print("Special Testing:")
print("map ↔ map:", dpr_score("map ", "map"))
print("map ↔ map view:", dpr_score("map ", "map view"))
print("map ↔ interactive map:", dpr_score("map", "interactive map"))

print("app access contact ↔ contact:", dpr_score("app access contact", "contact"))
print("app access contact ↔ Read_Contact:", dpr_score("app access contact", "Read_Contact"))
print("getRunningAppProcesses ↔ list:", dpr_score("getRunningAppProcesses", "list"))
print("get Sim Serial Number ↔ number:", dpr_score("get Sim Serial Number", "number"))
