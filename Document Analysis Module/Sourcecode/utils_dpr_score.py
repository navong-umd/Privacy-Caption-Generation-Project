import subprocess
import os

# Path to ESA tool directory and script
ESA_ROOT = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Document Analysis Module\esalib"
ANALYZER_SCRIPT = os.path.join(ESA_ROOT, "run_analyzer.bat")  # Use .bat for Windows

def dpr_score(np_text: str, permission: str) -> float:
    """
    Runs ESA analyzer to compute similarity score between input and permission phrase.
    Returns float score from the last line of output.
    """
    # Normalize permission text
    perm_query = permission.lower().replace('_', ' ')

    try:
        # Compose command as list of arguments
        cmd = [ANALYZER_SCRIPT, np_text, perm_query]
        
        out = subprocess.check_output(cmd, cwd=ESA_ROOT, stderr=subprocess.DEVNULL, shell=True)
        lines = out.decode('utf-8').strip().splitlines()
        score_str = lines[-1]
        return float(score_str)
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running ESA analyzer: {e}")
        return -1.0
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return -1.0
