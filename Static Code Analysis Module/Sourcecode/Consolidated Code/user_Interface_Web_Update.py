# app.py
# Full flow with accurate progress bar (%), green completed ticks, and all sections/pages.
# Saves all user inputs to:
#   questionnaire_master.xlsx (single-row master, sample-aligned)
#   questionnaire_by_section.xlsx (one sheet per section, sample-aligned)
#
# Run:
#   pip install flask pandas openpyxl
#   python app.py  -> http://127.0.0.1:5000

from flask import (
    Flask, request, redirect, url_for, render_template_string,
    send_from_directory, send_file, flash, session
)
from pathlib import Path
from werkzeug.utils import secure_filename
import mimetypes
from io import BytesIO
import base64
from datetime import date, datetime
import pandas as pd
import uuid

from user_Interface_Web_PPGen_Update import generate_policy_docx

app = Flask(__name__)
app.secret_key = "dev"  # flash messages + session

# ====== Paths ======
APK_UPLOAD_DIR = Path(
    r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\uploadFile\APK"
)
APK_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

LOGO_DIR = Path(
    r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\input"
)

CSV_OUTPUT_FOLDER = Path(
    r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output_csv"
)
CSV_OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

POLICY_OUTPUT_DIR = Path(
    r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output_csv\policies"
)
POLICY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB

# ====== Progress tracking across ALL screens ======
PROG_ORDER = [
    "page1", "page2", "page3", "page4", "page5_age",
    "collection_direct", "use_marketing",
    # combined disclosure page (ads + affiliates + partners)
    "disclosure_ads",
    "disclosure_security",
    "tracking_main", "google_analytics",
    "user_rights_dsar",
    "final_company", "final_title", "final_version_date"
]
TOTAL_SCREENS = len(PROG_ORDER)
PROG_INDEX = {name: i for i, name in enumerate(PROG_ORDER, start=1)}  # 1-based position


def progress_state(endpoint: str):
    idx = PROG_INDEX.get(endpoint, 1)
    pct = int((idx / TOTAL_SCREENS) * 100)
    return idx, TOTAL_SCREENS, pct


# ====== Section labels for the stepper nodes ======
STEPS = [
    "Privacy Policy Uses",
    "User Information",
    "Collection of Information",
    "Use of Information",
    "Disclosure of Information",
    "Use of Tracking Technologies",
    "User Rights",
    "Final Details",
]

# ====== Session answer helpers ======
def answers():
    if "answers" not in session:
        session["answers"] = {}
    return session["answers"]


def set_section(section: str, data: dict):
    a = answers()
    a[section] = data
    session["answers"] = a


def add_file_list(section: str, key: str, filenames):
    a = answers()
    sec = a.get(section, {})
    sec[key] = list(filenames)
    a[section] = sec
    session["answers"] = a


def normalize_multi(val):
    if isinstance(val, list):
        return "; ".join(map(str, val))
    if isinstance(val, bool):
        return "yes" if val else "no"
    return val if val is not None else ""


# ====== Reset helpers ======
def reset_form_state(clear_uploads: bool = True):
    session.clear()
    if clear_uploads and APK_UPLOAD_DIR.exists():
        for p in APK_UPLOAD_DIR.glob("*"):
            try:
                if p.is_file():
                    p.unlink()
            except Exception:
                pass


# ====== Logo resolver ======
_LOGO_CANDIDATE_NAMES = [
    "logo.png", "Logo.png", "LOGO.png",
    "logo.jpg", "Logo.jpg", "LOGO.jpg",
    "logo.jpeg", "Logo.jpeg",
    "logo.svg", "Logo.svg",
    "logo.webp", "Logo.webp"
]
_LOGO_EXTS = (".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif")


def _find_logo_path():
    if not LOGO_DIR.exists():
        return None
    for name in _LOGO_CANDIDATE_NAMES:
        p = LOGO_DIR / name
        if p.exists() and p.is_file():
            return p
    for ext in _LOGO_EXTS:
        matches = list(LOGO_DIR.glob(f"*{ext}"))
        if matches:
            return matches[0]
    return None


_TRANSPARENT_PNG = base64.b64decode(
    b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABJm9n3QAAAABJRU5ErkJggg=="
)


@app.route("/branding/logo")
def branding_logo():
    p = _find_logo_path()
    if p and p.exists():
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        return send_file(p, mimetype=mime, conditional=True)
    return send_file(BytesIO(_TRANSPARENT_PNG), mimetype="image/png")


# ====== Base layout (adds contact toggles JS) ======
BASE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Privacy Policy Generator</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    :root{
      --bg:#f7f8fe; --card:#fff; --muted:#6b7280; --ink:#0f172a;
      --accent:#5865F2; --accent-ink:#fff; --line:#e5e7eb; --line-input:#d1d5db;
      --shadow: 0 8px 24px rgba(0,0,0,.08);
      --hint:#9ca3af; --danger:#ef4444; --success:#22c55e;
      --prog-track:#e9edf4; --prog-fill:#56c08a;
    }
    *{box-sizing:border-box}
    body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,Segoe UI,Roboto,Arial}
    .wrap{max-width:1200px;margin:24px auto;padding:0 16px}
    .brand{display:flex;align-items:center;gap:12px;margin-bottom:8px}
    .brand img{height:140px;width:auto;display:block}
    .title{font-size:28px;font-weight:800;margin:0}
    .card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:24px}

    /* Progress */
    .progressbox{margin:6px 0 18px}
    .progressrow{display:flex;align-items:center;gap:14px}
    .progresslabel{font-weight:800;color:#4b5563;letter-spacing:.08em}
    .progresstrack{position:relative;flex:1;height:10px;border-radius:999px;background:var(--prog-track);overflow:hidden}
    .progressfill{position:absolute;left:0;top:0;bottom:0;border-radius:999px;background:var(--prog-fill);width: {{ prog_pct }}%;transition:width .25s ease;}
    .progresspct{min-width:48px;text-align:right;font-weight:800;color:#111827}

    /* Stepper */
    .stepper{position:relative;margin:2px 0 12px 0;padding-top:6px}
    .stepper .nodes{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
    .node{display:flex;flex-direction:column;align-items:center;text-align:center;max-width:220px}
    .dot{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;background:#cbd5e1;border:3px solid #fff;box-shadow:0 0 0 1px #cbd5e1;font-size:12px;font-weight:700}
    .node.done .dot{background:var(--success);box-shadow:0 0 0 1px var(--success)}
    .node.current .dot{background:#fff;color:var(--accent);box-shadow:0 0 0 2px var(--accent)}
    .lbl{margin-top:8px;font-size:13px;color:var(--muted);font-weight:700}
    @media (max-width:700px){ .lbl{display:none} }

    .muted{color:var(--muted)}
    .help{color:var(--muted);font-size:12px;margin-top:6px}
    .subhelp{color:var(--muted);font-size:14px;font-style:italic;margin:6px 0 10px}
    .btn{appearance:none;border:0;border-radius:10px;padding:12px 18px;font-weight:700;cursor:pointer}
    .btn-accent{background:var(--accent);color:var(--accent-ink)}
    .btn-ghost{background:#f3f4f6;color:#111827}
    .btn-link{appearance:none;background:none;border:0;color:#5865F2;font-weight:700;cursor:pointer}
    .remove-link{appearance:none;background:none;border:0;color:var(--danger);font-weight:600;cursor:pointer;margin-left:12px}
    .btn:disabled{opacity:.55;cursor:not-allowed}
    .actions{display:flex;justify-content:flex-end;gap:10px;margin-top:24px}
    .group{margin:18px 0}
    .checkline{display:flex;align-items:center;gap:10px;margin:10px 0;font-size:16px}
    .radios{display:flex;gap:18px;margin-top:8px;align-items:center}
    .radios label{display:inline-flex;gap:8px;align-items:center;font-size:16px}

    input[type="text"], input[type="date"], select{
      width:100%;padding:12px;border:1px solid var(--line-input);border-radius:10px;
      font-size:16px;color:#111827;background:#fff
    }
    input[type="text"].hinted{ color: var(--hint); }
    input[type="text"]:focus, input[type="date"]:focus, select:focus{ outline:none; border-color:#c1c7d0; box-shadow:0 0 0 2px #eef2ff; }

    .filebox input[type="file"]{display:block;margin-top:10px}

    .qrow{display:flex; align-items:center; gap:8px; flex-wrap:wrap}
    .qhelp{position:relative; display:inline-flex; align-items:center}
    .info-btn{
      display:inline-flex; align-items:center; justify-content:center;
      width:22px; height:22px; border-radius:50%;
      background:#eef2ff; color:#334155; border:1px solid #c7d2fe;
      cursor:pointer; font-weight:700; line-height:1;
    }
    .popover{
      position:absolute; left:26px; top:-6px; z-index:20;
      width:min(560px, 85vw); background:#fff; border:1px solid var(--line);
      border-radius:10px; padding:16px; box-shadow:var(--shadow); display:none;
    }
    .popover h4{margin:0 0 10px 0; font-size:18px; line-height:1.25}
    .popover p{margin:8px 0 0 0; color:#475569}
    .popover em{color:#6b7280}
    .popover::before{
      content:""; position:absolute; left:180px; top:-6px;
      width:0; height:0; border-left:6px solid transparent; border-right:6px solid transparent;
      border-bottom:6px solid #fff; filter:drop-shadow(0 -1px 0 #e5e7eb);
    }
    .qhelp:hover .popover, .qhelp:focus-within .popover, .qhelp[data-open="1"] .popover{ display:block; }
  </style>
  <script>
    document.addEventListener('click', function(e){
      const t = e.target.closest('.info-btn');
      if(t){
        const wrap = t.closest('.qhelp');
        document.querySelectorAll('.qhelp[data-open="1"]').forEach(n=>n.dataset.open="0");
        wrap.dataset.open = wrap.dataset.open === "1" ? "0" : "1";
        e.preventDefault(); return;
      }
      if(!e.target.closest('.qhelp')){
        document.querySelectorAll('.qhelp[data-open="1"]').forEach(n=>n.dataset.open="0");
      }
      const rem = e.target.closest('.remove-item');
      if(rem){ e.preventDefault(); const row = rem.closest('.checkline'); if(row){ row.remove(); } }
    });

    document.addEventListener('DOMContentLoaded', function(){
      const hintedInputs = document.querySelectorAll('input[data-hint]');
      hintedInputs.forEach(function(input){
        const hint = input.getAttribute('data-hint') || '';
        const applyHint = ()=>{ if(!input.value.trim()){ input.value = hint; input.classList.add('hinted'); } };
        const clearHint = ()=>{ if(input.classList.contains('hinted') && input.value === hint){ input.value=''; } input.classList.remove('hinted'); };
        applyHint(); input.addEventListener('focus', clearHint); input.addEventListener('blur', applyHint);
        if(input.form){ input.form.addEventListener('submit', function(){ if(input.classList.contains('hinted') && input.value === hint){ input.value=''; } }); }
      });

      function bindToggle(chkId, blkId){
        const c = document.getElementById(chkId);
        const b = document.getElementById(blkId);
        if(!c || !b) return;
        const sync = ()=>{ b.style.display = c.checked ? 'block' : 'none'; };
        c.addEventListener('change', sync); sync();
      }

      // Existing toggles
      bindToggle('inc_yes','desc_block');
      const yes = document.getElementById('inc_yes'); const no = document.getElementById('inc_no'); const block = document.getElementById('desc_block');
      if(yes && no && block){ const sync=()=>{ block.style.display = yes.checked ? 'block':'none'; }; yes.addEventListener('change',sync); no.addEventListener('change',sync); sync(); }

      const uaYes = document.getElementById('ua_yes'); const uaNo = document.getElementById('ua_no'); const uaMore = document.getElementById('ua_more');
      if(uaYes && uaNo && uaMore){ const syncUA=()=>{ uaMore.style.display = uaYes.checked ? 'block':'none'; }; uaYes.addEventListener('change',syncUA); uaNo.addEventListener('change',syncUA); syncUA(); }

      const ageYes = document.getElementById('age_yes'); const ageNo  = document.getElementById('age_no'); const ageAdv = document.getElementById('age_advanced');
      if(ageYes && ageNo && ageAdv){ const syncAge = ()=>{ ageAdv.style.display = ageNo.checked ? 'block' : 'none'; }; ageYes.addEventListener('change', syncAge); ageNo.addEventListener('change', syncAge); syncAge(); }

      const mkYes = document.getElementById('mk_yes'); const mkNo  = document.getElementById('mk_no'); const mkMore = document.getElementById('mk_more');
      if(mkYes && mkNo && mkMore){ const sync = ()=>{ mkMore.style.display = mkYes.checked ? 'block' : 'none'; }; mkYes.addEventListener('change', sync); mkNo.addEventListener('change', sync); sync(); }

      const dsarYes = document.getElementById('dsar_yes'); const dsarNo = document.getElementById('dsar_no'); const dsarUrl = document.getElementById('dsar_url_row');
      if(dsarYes && dsarNo && dsarUrl){ const sync = ()=>{ dsarUrl.style.display = dsarYes.checked ? 'block' : 'none'; }; dsarYes.addEventListener('change', sync); dsarNo.addEventListener('change', sync); sync(); }

      const gaYes = document.getElementById('ga_yes'); const gaNo = document.getElementById('ga_no'); const gaBlk = document.getElementById('ga_features_blk');
      if(gaYes && gaNo && gaBlk){ const sync = ()=>{ gaBlk.style.display = gaYes.checked ? 'block' : 'none'; }; gaYes.addEventListener('change', sync); gaNo.addEventListener('change', sync); sync(); }

      // Security Measures (Step 11): show warning live when "No" is selected
      const secYes  = document.getElementById('sec_yes');
      const secNo   = document.getElementById('sec_no');
      const secWarn = document.getElementById('sec_warn');
      const secAck  = document.getElementById('sec_ack');

      if (secYes && secNo && secWarn) {
        const syncSec = () => {
          const noSelected = !!secNo.checked;
          secWarn.style.display = noSelected ? 'block' : 'none';
          if (secAck) {
            secAck.required = noSelected;
            if (!noSelected) secAck.checked = false;
          }
        };
        secYes.addEventListener('change', syncSec);
        secNo.addEventListener('change',  syncSec);
        syncSec();
      }
      
      // NEW: contact method toggles (Page 14)
      bindToggle('contact_email_chk', 'email_blk');
      bindToggle('contact_web_chk', 'web_blk');
      bindToggle('contact_phone_chk', 'phone_blk');
      bindToggle('contact_mail_chk', 'mail_blk');
    });
  </script>
</head>
<body>
  <div class="wrap">
    <div class="brand">
      <img src="{{ logo_url }}" alt="Logo">
      <h1 class="title">Privacy Policy Generator</h1>
    </div>

    <!-- Progress bar -->
    <div class="progressbox" aria-label="Progress">
      <div class="progressrow">
        <div class="progresslabel">PROGRESS</div>
        <div class="progresstrack" role="progressbar"
             aria-valuemin="0" aria-valuemax="100"
             aria-valuenow="{{ prog_pct }}">
          <div class="progressfill"></div>
        </div>
        <div class="progresspct">{{ prog_pct }}%</div>
      </div>
      <div class="help">Step {{ prog_idx }} of {{ prog_total }}</div>
    </div>

    <!-- Stepper -->
    <div class="stepper">
      <div class="nodes">
        {% for lbl in steps %}
          {% set i = loop.index %}
          <div class="node {{ 'done' if i < section_step else ('current' if i == section_step else 'todo') }}">
            <div class="dot">{% if i < section_step %}✓{% endif %}</div>
            <div class="lbl">{{ lbl }}</div>
          </div>
        {% endfor %}
      </div>
    </div>

    <div class="card">
      {{ body|safe }}
    </div>

    {% with msgs = get_flashed_messages() %}
      {% if msgs %}
        <div class="card" style="margin-top:12px">
          {% for m in msgs %}<div>{{ m }}</div>{% endfor %}
        </div>
      {% endif %}
    {% endwith %}
  </div>
</body>
</html>
"""

# ====== Page bodies (all inputs carry name=...) ======
PAGE1_BODY = """
<h2 style="margin:0 0 14px 0">Privacy Policy Uses</h2>
<div class="muted" style="margin-bottom:14px">What will this Privacy Policy be used for?</div>
<form method="post" action="{{ url_for('page1') }}">
  <div class="group">
    <label class="checkline greyed"><input type="checkbox" name="use_website" value="1" disabled> Website</label>
    <input type="hidden" name="mobile" value="1">
    <label class="checkline"><input type="checkbox" name="use_mobile" value="1" checked disabled> Mobile application</label>
    <label class="checkline greyed"><input type="checkbox" name="use_facebook" value="1" disabled> Facebook application</label>
  </div>
  <div class="actions">
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

PAGE2_BODY = """
<h2 style="margin:0 0 14px 0">Mobile Application</h2>
<form method="post" enctype="multipart/form-data" action="{{ url_for('page2') }}">
  <div class="group">
    <div class="qrow">
      <label for="app_name" style="font-weight:700;font-size:18px">What is the name of your mobile application?</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>How should I list the mobile app name in my Privacy Policy?</h4>
          <p>The name of your mobile app in your Privacy Policy should match your app-store listing.</p>
        </div>
      </span>
    </div>
    <div class="help">Enter the full name of your mobile app.</div>
    <input id="app_name" name="app_name" type="text" data-hint="e.g., Apple Music" value="{{ app_name or '' }}">
  </div>

  <div class="group filebox">
    <div class="help"><strong>Please upload your mobile application package file</strong></div>
    <div class="help">Mobile application package files (e.g., .apk or .xapk for Android, and .ipa for iOS.)</div>
    <input id="src_files" name="src_files" type="file" multiple accept=".apk,.xapk,.ipa">
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('page1') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

PAGE3_BODY = """
<h2 style="margin:0 0 14px 0">Use and Description</h2>
<form method="post" action="{{ url_for('page3') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Do you want to include a description about your product or service?</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>Why include a description?</h4>
          <p>A short description helps readers understand what your product or service does. Keep it concise.</p>
        </div>
      </span>
    </div>
    <div class="radios" role="radiogroup" aria-label="Include product or service description">
      <label><input type="radio" id="inc_yes" name="include_desc" value="yes" {{ 'checked' if include_desc=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="inc_no"  name="include_desc" value="no"  {{ 'checked' if include_desc!='yes' else '' }}> No</label>
    </div>
  </div>

  <div id="desc_block" class="group" style="display:none">
    <label for="product_desc" style="font-weight:700">Enter the name of your product or service</label>
    <div class="help">e.g., A design platform to design, prototype, gather feedback, and collaborate.</div>
    <input id="product_desc" name="product_desc" type="text" data-hint="Enter the name of your product or service" value="{{ product_desc or '' }}">
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('page2') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

PAGE4_BODY = """
<h2 style="margin:0 0 14px 0">User Accounts</h2>
<form method="post" action="{{ url_for('page4') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Can users create an account or register with your website or app?</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>Note:</h4>
          <p>If accounts are supported, we will include the processing activity to create/log in to accounts and keep them in working order.</p>
        </div>
      </span>
    </div>
    <div class="radios" role="radiogroup" aria-label="User accounts">
      <label><input type="radio" id="ua_yes" name="can_register" value="yes" {{ 'checked' if can_register=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="ua_no"  name="can_register" value="no"  {{ 'checked' if can_register!='yes' else '' }}> No</label>
    </div>
  </div>

  <div id="ua_more" style="display:none">
    <div class="group">
      <div class="qrow">
        <label style="font-weight:700;font-size:18px">How would you like to instruct users to update or delete their accounts?</label>
        <span class="qhelp" aria-live="polite">
          <button class="info-btn" type="button" aria-label="Help">?</button>
          <div class="popover" role="dialog" aria-modal="false">
            <h4>Note:</h4>
            <p>This text will appear as-is in your privacy policy. "Us" refers to your business and the contact details you provide.</p>
          </div>
        </span>
      </div>
      <div class="subhelp">Please select all that apply.</div>

      <div class="checkline">
        <input type="checkbox" name="update_opts" value="settings" {{ 'checked' if 'settings' in update_opts else '' }}>
        <span>Log in to your account settings and update your user account.</span>
      </div>
      <div class="checkline">
        <input type="checkbox" name="update_opts" value="contact" {{ 'checked' if 'contact' in update_opts else '' }}>
        <span>Contact us using the contact information provided.</span>
      </div>

      <div id="own_list">
        {% for item in custom_items %}
          <div class="checkline">
            <input type="checkbox" name="update_opts" value="custom::{{ item }}" {{ 'checked' if ('custom::'+item) in update_opts else '' }}>
            <span>{{ item }}</span>
            <button type="button" class="remove-link remove-item">Remove</button>
            <input type="hidden" name="custom_items" value="{{ item }}">
          </div>
        {% endfor %}
      </div>

      <div class="group">
        <div style="font-weight:700;margin:12px 0 8px">Add your own</div>
        <div style="display:flex;gap:10px;align-items:center">
          <input id="ua_text" name="ua_text" type="text" style="flex:1" value="">
          <button class="btn-link" type="submit" name="ua_add" value="1">+ ADD</button>
        </div>
      </div>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('page3') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

PAGE5_BODY = """
<h2 style="margin:0 0 14px 0">User Age</h2>
<form method="post" action="{{ url_for('page5_age') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Do you target users under the age of 18?</label>
    </div>
    <div class="radios" role="radiogroup" aria-label="Targeting minors">
      <label><input type="radio" id="age_yes" name="age_target" value="yes" {{ 'checked' if age_target=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="age_no"  name="age_target" value="no"  {{ 'checked' if age_target=='no' else '' }}> No</label>
    </div>
  </div>

  <div id="age_advanced" class="group" style="display:none">
    <div style="font-weight:700;margin-bottom:6px">Advanced Options (Not recommended for most users)</div>
    <div class="subhelp">
      The majority of users do not need to change these settings. By interacting with this section, you understand that you should
      carefully review the resulting policy text and consult with a lawyer before making any changes.
    </div>
    <label class="checkline">
      <input type="checkbox" name="minors_custom" value="1" {{ 'checked' if minors_custom else '' }}>
      <span>Add custom language regarding minors</span>
    </label>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('page4') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

# ===== Page 6 updated to include device-collected items =====
PAGE6_BODY = """
<h2 style="margin:0 0 14px 0">Personal Information Collected Directly</h2>

<form method="post" action="{{ url_for('collection_direct') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Please select the personal information you intend to collect directly from the user:</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>What are users?</h4>
          <p>Users are individuals that visit your website or app. They can be external or internal.</p>
          <p><strong>External users</strong> include individuals who:</p>
          <ul>
            <li>Browse your website</li>
            <li>Interact with your website</li>
            <li>Use your software/program/platform</li>
            <li>Purchase goods or services through your website</li>
          </ul>
          <p><strong>Internal users</strong> include:</p>
          <ul>
            <li>Employees</li>
            <li>Managers</li>
            <li>Internal auditors</li>
          </ul>
        </div>
      </span>
    </div>
    <div class="subhelp"><em>"Collect directly" means the user directly provides you with this information. For example, a user may give you their name and email address when signing up for an account on your site.</em></div>

    {% for val, label in pi_choices %}
      <label class="checkline">
        <input type="checkbox" name="pi_opts" value="{{ val }}" {{ 'checked' if val in pi_opts else '' }}>
        <span>{{ label }}</span>
      </label>
    {% endfor %}

    <div id="pi_list">
      {% for item in pi_items %}
        <div class="checkline">
          <input type="checkbox" name="pi_opts" value="custom::{{ item }}" {{ 'checked' if ('custom::'+item) in pi_opts else '' }}>
          <span>{{ item }}</span>
          <button type="button" class="remove-link remove-item">Remove</button>
          <input type="hidden" name="pi_items" value="{{ item }}">
        </div>
      {% endfor %}
    </div>

    <div class="group">
      <div style="font-weight:700;margin:12px 0 8px">Add your own</div>
      <div style="display:flex;gap:10px;align-items:center">
        <input id="pi_own" name="pi_own" type="text" style="flex:1" value="">
        <button class="btn-link" type="submit" name="pi_add" value="1">+ ADD</button>
      </div>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">

  <!-- NEW: Device-collected information (mobile/tablet) -->
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Select additional information you collect from a device (mobile/tablet)</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>Device-collected data</h4>
          <p>These are data gathered through device sensors or permissions (for example, GPS, Contacts, Camera). Choose only what your app actually uses.</p>
          <p><em>Tip:</em> Be consistent with your app permissions and any store disclosures.</p>
        </div>
      </span>
    </div>
    <div class="help">Skip selecting an option if none apply to you.</div>

    {% for val, label in device_choices %}
      <label class="checkline">
        <input type="checkbox" name="device_opts" value="{{ val }}" {{ 'checked' if val in device_opts else '' }}>
        <span>{{ label }}</span>
      </label>
    {% endfor %}
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('page5_age') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

USE_MARKETING_BODY = """
<h2 style="margin:0 0 14px 0">Marketing and Promotional Communications</h2>
<form method="post" action="{{ url_for('use_marketing') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Do you send marketing or promotional communications to your users?</label>
    </div>
    <div class="help">If yes, make sure you have selected "To send marketing and promotional communications" as a reason for using your users' personal information (on previous page).</div>
    <div class="radios" role="radiogroup" aria-label="Marketing comms">
      <label><input type="radio" id="mk_yes" name="mk_send" value="yes" {{ 'checked' if mk_send=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="mk_no"  name="mk_send" value="no"  {{ 'checked' if mk_send!='yes' else '' }}> No</label>
    </div>
  </div>

  <div id="mk_more" style="display:none">
    <div class="group">
      <div class="qrow">
        <label style="font-weight:700;font-size:18px">How can users unsubscribe to marketing and promotional communications?</label>
        <span class="qhelp" aria-live="polite">
          <button class="info-btn" type="button" aria-label="Help">?</button>
          <div class="popover" role="dialog" aria-modal="false">
            <h4>Note</h4>
            <p>By default, we will also add "Contact us using the contact information provided by us" as an option.</p>
          </div>
        </span>
      </div>

      <div class="checkline">
        <input type="checkbox" name="mk_opts" value="unsubscribe_link" {{ 'checked' if 'unsubscribe_link' in mk_opts else '' }}>
        <span>Clicking the unsubscribe link at the bottom of our emails</span>
      </div>
      <div class="checkline">
        <input type="checkbox" name="mk_opts" value="text_stop" {{ 'checked' if 'text_stop' in mk_opts else '' }}>
        <span>Texting “STOP” or “UNSUBSCRIBE”</span>
      </div>

      <div id="mk_own_list">
        {% for item in mk_items %}
          <div class="checkline">
            <input type="checkbox" name="mk_opts" value="custom::{{ item }}" {{ 'checked' if ('custom::'+item) in mk_opts else '' }}>
            <span>{{ item }}</span>
            <button type="button" class="remove-link remove-item">Remove</button>
            <input type="hidden" name="mk_items" value="{{ item }}">
          </div>
        {% endfor %}
      </div>

      <div class="group">
        <div style="font-weight:700;margin:12px 0 8px">Add your own</div>
        <div style="display:flex;gap:10px;align-items:center">
          <input id="mk_own" name="mk_own" type="text" style="flex:1" value="">
          <button class="btn-link" type="submit" name="mk_add" value="1">+ ADD</button>
        </div>
      </div>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('collection_direct') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

# ===== New combined Disclosure of Information page (ads + affiliates + partners) =====
DISCLOSURE_BODY = """
<h2 style="margin:0 0 14px 0">Disclosure of Information</h2>
<p class="muted">
  Please tell us whether you share your users' personal information with any of the following.
  Select "Yes" if you share any personal information, even if it is limited (for example, device identifiers or usage data).
</p>

<form method="post" action="{{ url_for('disclosure_ads') }}">

  <!-- Third-Party Advertisers -->
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Third-Party Advertisers</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>What are third-party advertisers?</h4>
          <p>
            A third-party advertiser is an external company or platform, such as Google AdMob,
            Facebook Audience Network, or AppLovin, that uses personal information collected from
            mobile apps (like device identifiers and usage data) to serve targeted advertisements.
          </p>
          <p>
            Select <strong>Yes</strong> if your app integrates one or more of these services.
          </p>
        </div>
      </span>
    </div>
    <div class="help">
      Example: You use an ad SDK in your app to show banner or interstitial ads.
    </div>
    <div class="radios">
      <label><input type="radio" name="ads" value="yes" {{ 'checked' if ads=='yes' else '' }}> Yes</label>
      <label><input type="radio" name="ads" value="no"  {{ 'checked' if ads!='yes' else '' }}> No</label>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:14px 0">

  <!-- Business Affiliates -->
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Business Affiliates</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>Who are business affiliates?</h4>
          <p>
            Business affiliates include your parent company, subsidiaries, or other entities that are under
            common ownership or control.
          </p>
          <p>
            Select <strong>Yes</strong> if you share user information with those entities so that they can
            support your services or provide related offerings.
          </p>
        </div>
      </span>
    </div>
    <div class="help">
      Example: You share user account information with another company in the same group to provide
      centralized customer support.
    </div>
    <div class="radios">
      <label><input type="radio" name="aff" value="yes" {{ 'checked' if aff=='yes' else '' }}> Yes</label>
      <label><input type="radio" name="aff" value="no"  {{ 'checked' if aff!='yes' else '' }}> No</label>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:14px 0">

  <!-- Business Partners -->
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700;font-size:18px">Business Partners</label>
      <span class="qhelp" aria-live="polite">
        <button class="info-btn" type="button" aria-label="Help">?</button>
        <div class="popover" role="dialog" aria-modal="false">
          <h4>Who are business partners?</h4>
          <p>
            A business partner is a person or company that works together with you, sharing responsibilities,
            risks, or resources to help achieve common business objectives.
          </p>
          <p>
            Select <strong>Yes</strong> if you share user information so that a partner can provide a service
            inside or alongside your app (for example, a payment provider or loyalty program partner).
          </p>
        </div>
      </span>
    </div>
    <div class="help">
      Example: You share purchase history with a partner to provide joint promotions or loyalty rewards.
    </div>
    <div class="radios">
      <label><input type="radio" name="partners" value="yes" {{ 'checked' if partners=='yes' else '' }}> Yes</label>
      <label><input type="radio" name="partners" value="no"  {{ 'checked' if partners!='yes' else '' }}> No</label>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('use_marketing') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

DISC_SECURITY_BODY = """
<h2 style="margin:0 0 14px 0">Security Measures</h2>
<form method="post" action="{{ url_for('disclosure_security') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700">Do you have appropriate security measures in place that protect your users’ personal information?</label>
    </div>
    <div class="help">If "Yes," we will include a general clause about security measures in your privacy policy.</div>
    <div class="radios">
      <label><input type="radio" id="sec_yes" name="sec" value="yes" {{ 'checked' if sec=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="sec_no"  name="sec" value="no"  {{ 'checked' if sec=='no' else '' }}> No</label>
    </div>
  </div>

  <div id="sec_warn" class="card" style="border-color:#fda58a;background:#fff7ed;margin:10px 0; display: {{ 'block' if sec=='no' else 'none' }}">
    <div style="font-weight:700;margin-bottom:6px">Please ensure that you are keeping personal information safe.</div>
    <div>We recommend consulting with an information security expert and updating your policy once you are confident you can protect your users’ privacy.</div>
    <label class="checkline" style="margin-top:10px">
      <input type="checkbox" id="sec_ack" name="sec_ack" value="1" {% if sec=='no' %}required{% endif %}>
      <span>Yes, I understand and acknowledge the above.</span>
    </label>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('disclosure_ads') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

TRACKING_BODY = """
<h2 style="margin:0 0 14px 0">Tracking Technologies</h2>
<form method="post" action="{{ url_for('tracking_main') }}">
  <div class="group">
    <div class="qrow"><label style="font-weight:700">Which of the following does your website or app use?</label></div>
    <div class="radios" style="flex-direction:column;align-items:flex-start">
      <label><input type="radio" name="tt" value="cookies" {{ 'checked' if tt=='cookies' else '' }}> Cookies and/or web beacons</label>
      <label><input type="radio" name="tt" value="maps" {{ 'checked' if tt=='maps' else '' }}> Google Maps APIs</label>
      <label><input type="radio" name="tt" value="both" {{ 'checked' if tt=='both' else '' }}> Both</label>
      <label><input type="radio" name="tt" value="neither" {{ 'checked' if tt=='neither' else '' }}> Neither</label>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('disclosure_security') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

GA_BODY = """
<h2 style="margin:0 0 14px 0">Google Analytics</h2>
<form method="post" action="{{ url_for('google_analytics') }}">

  <div class="group">
    <div class="qrow"><label style="font-weight:700">Do you use Google Analytics?</label></div>
    <div class="radios">
      <label><input type="radio" id="ga_yes" name="ga" value="yes" {{ 'checked' if ga=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="ga_no"  name="ga" value="no"  {{ 'checked' if ga=='no' else '' }}> No</label>
    </div>
  </div>

  <div id="ga_features_blk" style="display:none">
    <div class="group">
      <label style="font-weight:700">List the Google Analytics Advertising Features you have enabled:</label>
      <div class="help">Leave blank if you do not use any Google Advertising Features</div>
      <select name="ga_feature" id="ga_feature">
        <option value="">Select...</option>
        {% for v, lbl in ga_feature_choices %}
          <option value="{{ v }}" {{ 'selected' if ga_feature==v else '' }}>{{ lbl }}</option>
        {% endfor %}
      </select>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('tracking_main') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

USER_RIGHTS_BODY = """
<h2 style="margin:0 0 14px 0">Data Subject Access Request</h2>
<form method="post" action="{{ url_for('user_rights_dsar') }}">
  <div class="group">
    <div class="qrow">
      <label style="font-weight:700">Do you provide a service that allows users to send a request to view/edit/delete their personal information stored on your website and/or app?</label>
      <span class="qhelp"><button class="info-btn" type="button">?</button>
        <div class="popover">
          <h4>Is this required?</h4>
          <p>Some privacy laws require an online request method (e.g., CCPA). Provide a request form or another practical method.</p>
        </div>
      </span>
    </div>
    <div class="radios" style="flex-direction:column;align-items:flex-start">
      <label><input type="radio" id="dsar_yes" name="dsar" value="yes" {{ 'checked' if dsar=='yes' else '' }}> Yes</label>
      <label><input type="radio" id="dsar_no"  name="dsar" value="no"  {{ 'checked' if dsar=='no' else '' }}> No, I will use Third-party service</label>
    </div>
  </div>

  <div id="dsar_url_row" class="group" style="display:none">
    <label for="dsar_url">Please enter the URL to access this service</label>
    <input id="dsar_url" type="text" name="dsar_url" value="{{ dsar_url or '' }}" placeholder="www.example.com/data-request">
  </div>

  <div class="group">
    <label style="font-weight:700">Users may request access to their personal information:</label>
    <div class="radios" style="flex-direction:column;align-items:flex-start">
      <label><input type="radio" name="access_when" value="law" {{ 'checked' if access_when=='law' else '' }}> If their country’s privacy law grants the right to access (Recommended for most users)</label>
      <label><input type="radio" name="access_when" value="always" {{ 'checked' if access_when=='always' else '' }}> Always</label>
    </div>
  </div>

  <hr style="border:none;border-top:1px solid #e5e7eb;margin:12px 0">

  <!-- NEW: How can users contact you? -->
  <h3 style="margin:0 0 10px 0">How can users contact you for any questions regarding your Privacy Policy?</h3>
  <div class="help">Click all that apply.</div>

  <div class="group">
    <label class="checkline">
      <input type="checkbox" id="contact_email_chk" name="contact_email" value="1" {{ 'checked' if contact_email else '' }}>
      <span>By email</span>
    </label>
    <div id="email_blk" style="display:none; margin-left:28px">
      <label for="contact_email_addr" style="font-weight:700">What's the email?</label>
      <input id="contact_email_addr" name="contact_email_addr" type="text" value="{{ contact_email_addr or '' }}" placeholder="office@mycompany.com">
      <div class="help">e.g. office@mycompany.com</div>
    </div>

    <label class="checkline">
      <input type="checkbox" id="contact_web_chk" name="contact_web" value="1" {{ 'checked' if contact_web else '' }}>
      <span>By visiting a page on our website</span>
    </label>
    <div id="web_blk" style="display:none; margin-left:28px">
      <label for="contact_web_link" style="font-weight:700">What's the link?</label>
      <input id="contact_web_link" name="contact_web_link" type="text" value="{{ contact_web_link or '' }}" placeholder="http://www.mycompany.com/contact">
      <div class="help">e.g. http://www.mycompany.com/contact</div>
    </div>

    <label class="checkline">
      <input type="checkbox" id="contact_phone_chk" name="contact_phone" value="1" {{ 'checked' if contact_phone else '' }}>
      <span>By phone number</span>
    </label>
    <div id="phone_blk" style="display:none; margin-left:28px">
      <label for="contact_phone_number" style="font-weight:700">What's the phone number?</label>
      <input id="contact_phone_number" name="contact_phone_number" type="text" value="{{ contact_phone_number or '' }}" placeholder="e.g. 408.996.1010">
      <div class="help">e.g. 408.996.1010</div>
    </div>

    <label class="checkline">
      <input type="checkbox" id="contact_mail_chk" name="contact_mail" value="1" {{ 'checked' if contact_mail else '' }}>
      <span>By sending post mail</span>
    </label>
    <div id="mail_blk" style="display:none; margin-left:28px">
      <label for="contact_post_addr" style="font-weight:700">What's the address?</label>
      <input id="contact_post_addr" name="contact_post_addr" type="text" value="{{ contact_post_addr or '' }}" placeholder="767 Fifth Avenue New York, NY 10153, United States">
      <div class="help">e.g. 767 Fifth Avenue New York, NY 10153, United States</div>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('google_analytics') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

COMPANY_BODY = """
<h2 style="margin:0 0 14px 0">Company</h2>
<form method="post" action="{{ url_for('final_company') }}">
  <div class="group">
    <label for="company_name">Full legal name of company</label>
    <div class="help">Include corporate ending if applicable: Inc., LLC, etc.</div>
    <input id="company_name" type="text" name="company_name" value="{{ company_name or '' }}" placeholder="e.g., Apple Inc.">
  </div>

  <div class="group">
    <label for="privacy_email">Please provide an email address for privacy-related inquiries</label>
    <input id="privacy_email" type="text" name="privacy_email" value="{{ privacy_email or '' }}" placeholder="privacy@example.com">
  </div>

  <!-- NEW: Official website -->
  <div class="group">
    <label for="company_website">Official website (URL)</label>
    <div class="help">Enter your main website. Use https:// when possible.</div>
    <input id="company_website" type="text" name="website_url" value="{{ website_url or '' }}" placeholder="https://www.example.com">
  </div>

  <div class="group">
    <div class="qrow">
      <label for="phone">Phone number</label>
      <span class="qhelp"><button class="info-btn" type="button">?</button>
        <div class="popover">
          <h4>Do I need to include a phone number?</h4>
          <p>If your business is offline and you comply with the CCPA, a toll-free number may be required.</p>
        </div>
      </span>
    </div>
    <input id="phone" type="text" name="phone" value="{{ phone or '' }}" placeholder="e.g., 1-800-555-5555">
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('user_rights_dsar') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

POLICY_TITLE_BODY = """
<h2 style="margin:0 0 14px 0">Name Your Policy</h2>
<form method="post" action="{{ url_for('final_title') }}">
  <div class="group">
    <div class="qrow"><label style="font-weight:700">What do you want to call your policy?</label></div>
    <div class="radios" style="flex-direction:column;align-items:flex-start">
      <label><input type="radio" name="ptitle_opt" value="Privacy Policy" {{ 'checked' if ptitle_opt=='Privacy Policy' else '' }}> Privacy Policy</label>
      <label style="display:flex;gap:10px;align-items:center">
        <input type="radio" name="ptitle_opt" value="custom" {{ 'checked' if ptitle_opt=='custom' else '' }}>
        <input type="text" name="ptitle_custom" value="{{ ptitle_custom or '' }}" placeholder="Add your own here" style="flex:1">
      </label>
    </div>
  </div>

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('final_company') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="next" value="1">Next</button>
  </div>
</form>
"""

VERSION_DATE_BODY = """
<h2 style="margin:0 0 14px 0">Version Date</h2>
<form method="post" action="{{ url_for('final_version_date') }}">
  <div class="group">
    <div class="qrow"><label style="font-weight:700">What is the effective date for this Privacy Policy?</label></div>
    <div class="help">
      The effective date informs your users when your Privacy Policy was originally published or last updated.
      When you make an update requiring notice, ensure this date matches your communications.
    </div>
    <input type="date" name="effective_date" value="{{ effective_date or '' }}">
  </div>

  {% if ptitle_resolved %}
  <div class="card" style="margin-top:8px">Policy title: <strong>{{ ptitle_resolved }}</strong></div>
  {% endif %}

  {% if latest_policy_fname %}
  <div class="card" style="margin-top:12px; background:#eef2ff; border-color:#c7d2fe">
    <div style="font-weight:700; margin-bottom:6px;">Latest generated policy</div>
    <a href="{{ url_for('download_policy', fname=latest_policy_fname) }}"
       class="btn btn-accent"
       style="display:inline-block; text-decoration:none;">
       Download: {{ latest_policy_fname }}
    </a>
  </div>
  {% endif %}

  <div class="actions">
    <a class="btn btn-ghost" href="{{ url_for('final_title') }}">Back</a>
    <button class="btn btn-accent" type="submit" name="publish" value="1">Publish</button>
  </div>
</form>
"""

POLICY_READY_BODY = """
<h2>Your Privacy Policy is Ready</h2>

<div class="card" style="border:2px solid #16a34a; background:#f0fdf4; text-align:center; padding:20px; border-radius:12px;">
  {% if latest_policy_fname %}
    <p style="margin:0 0 16px 0; font-size:16px; color:#166534;">
      We generated your document successfully.
    </p>
    <a href="{{ url_for('download_policy', fname=latest_policy_fname) }}"
       style="display:inline-block; text-decoration:none; font-weight:600;
              padding:12px 24px; border-radius:8px; background:#16a34a; color:#fff;">
       Download Your Privacy Policy
    </a>
  {% else %}
    <p>No policy file is available in this session.</p>
  {% endif %}
</div>

<div class="actions" style="margin-top:24px; text-align:center;">
  <a class="btn btn-ghost" href="{{ url_for('final_version_date') }}">Back</a>
  <a class="btn btn-accent" href="{{ url_for('start_new') }}">Start New</a>
</div>
"""

# ====== render helper ======
def render_page(template_str: str, section_step: int, endpoint_name: str, **ctx):
    body_html = render_template_string(template_str, **ctx)
    prog_idx, prog_total, prog_pct = progress_state(endpoint_name)
    return render_template_string(
        BASE_HTML,
        body=body_html,
        logo_url=url_for('branding_logo'),
        steps=STEPS,
        section_step=section_step,
        prog_idx=prog_idx,
        prog_total=prog_total,
        prog_pct=prog_pct,
        **ctx
    )

# ====== routes ======
@app.route("/", methods=["GET"])
def root():
    reset_form_state(clear_uploads=True)
    flash("Started a new form. Previous inputs were cleared.")
    return redirect(url_for("page1"))


@app.route("/new", methods=["GET"])
def start_new():
    reset_form_state(clear_uploads=True)
    flash("Started a new form. Previous inputs were cleared.")
    return redirect(url_for("page1"))


# ====== Uses (1) ======
@app.route("/uses", methods=["GET", "POST"], endpoint="page1")
def page1():
    if request.method == "POST":
        set_section("Uses", {"use_mobile": "1"})
        return redirect(url_for("page2"))
    return render_page(PAGE1_BODY, section_step=1, endpoint_name="page1")


@app.route("/mobile", methods=["GET", "POST"], endpoint="page2")
def page2():
    app_name_saved = ""
    if request.method == "POST":
        app_name = (request.form.get("app_name") or "").strip()
        app_name_saved = app_name
        saved = []
        if "src_files" in request.files:
            for f in request.files.getlist("src_files"):
                if not f or not f.filename:
                    continue
                name = secure_filename(f.filename)
                if not name:
                    continue
                (APK_UPLOAD_DIR / name).write_bytes(f.read())
                saved.append(name)
        set_section("Mobile Application", {"app_name": app_name})
        if saved:
            add_file_list("Mobile Application", "uploaded_packages", saved)
        if app_name:
            flash(f"App name saved: {app_name}")
        if saved:
            flash(f"Uploaded {len(saved)} file(s) to {APK_UPLOAD_DIR.resolve()}")
        elif "src_files" in request.files:
            flash("No files were uploaded.")
        return redirect(url_for("page3"))

    existing_files = sorted([p.name for p in APK_UPLOAD_DIR.iterdir() if p.is_file()])
    app_name_saved = answers().get("Mobile Application", {}).get("app_name", "")
    return render_page(PAGE2_BODY, section_step=1, endpoint_name="page2",
                       existing_files=existing_files, upload_dir=str(APK_UPLOAD_DIR.resolve()),
                       app_name=app_name_saved)


@app.route("/product", methods=["GET", "POST"], endpoint="page3")
def page3():
    include_desc = answers().get("Use and Description", {}).get("include_desc", "no")
    product_desc = answers().get("Use and Description", {}).get("product_desc", "")
    if request.method == "POST":
        include_desc = request.form.get("include_desc", "no")
        product_desc = (request.form.get("product_desc") or "").strip()
        set_section("Use and Description", {
            "include_desc": include_desc,
            "product_desc": product_desc
        })
        if include_desc == "yes":
            msg = "Description will be included."
            if product_desc:
                msg += f" Value: {product_desc}"
            flash(msg)
        else:
            flash("No description will be included.")
        return redirect(url_for("page4"))

    return render_page(PAGE3_BODY, section_step=1, endpoint_name="page3",
                       include_desc=include_desc, product_desc=product_desc)


# ====== User Information (2) ======
@app.route("/accounts", methods=["GET", "POST"], endpoint="page4")
def page4():
    can_register = answers().get("User Accounts", {}).get("can_register", "no")
    update_opts_prev = set(answers().get("User Accounts", {}).get("update_opts", []))
    custom_items_prev = answers().get("User Accounts", {}).get("custom_items", [])

    if request.method == "POST":
        # If clicking "+ ADD": keep user on this page and auto-tick the new custom item
        if request.form.get("ua_add"):
            can_register = request.form.get("can_register", "no")
            update_opts = set(request.form.getlist("update_opts"))
            custom_items = list(request.form.getlist("custom_items"))

            own = (request.form.get("ua_text") or "").strip()
            if can_register == "yes" and own:
                if own not in custom_items:
                    custom_items.append(own)
                update_opts.add(f"custom::{own}")  # auto-tick the newly added item

            set_section("User Accounts", {
                "can_register": can_register,
                "update_opts": list(update_opts),
                "custom_items": custom_items
            })

            return render_page(
                PAGE4_BODY,
                section_step=2,
                endpoint_name="page4",
                can_register=can_register,
                update_opts=update_opts,
                custom_items=custom_items
            )

        # Normal submit path
        can_register = request.form.get("can_register", "no")
        update_opts = []
        custom_items = []
        if can_register == "yes":
            update_opts = list(request.form.getlist("update_opts"))
            custom_items = list(request.form.getlist("custom_items"))

            summary = ["User accounts enabled."]
            if update_opts:
                labels = [
                    (x.replace("custom::", "Custom: ") if x.startswith("custom::") else x)
                    for x in update_opts
                ]
                summary.append("Update/Delete options: " + ", ".join(sorted(labels)))
            if custom_items:
                summary.append("Custom items: " + ", ".join(sorted(custom_items)))
            flash(" | ".join(summary))
        else:
            flash("User accounts disabled.")

        set_section("User Accounts", {
            "can_register": can_register,
            "update_opts": update_opts,
            "custom_items": custom_items
        })
        return redirect(url_for("page5_age"))

    # GET
    return render_page(
        PAGE4_BODY, section_step=2, endpoint_name="page4",
        can_register=can_register, update_opts=update_opts_prev,
        custom_items=custom_items_prev
    )


@app.route("/age", methods=["GET", "POST"], endpoint="page5_age")
def page5_age():
    prev = answers().get("User Age", {})
    age_target = prev.get("age_target")
    minors_custom = bool(prev.get("minors_custom", False))
    if request.method == "POST":
        age_target = request.form.get("age_target")
        minors_custom = bool(request.form.get("minors_custom"))
        set_section("User Age", {
            "age_target": age_target,
            "minors_custom": minors_custom
        })
        return redirect(url_for("collection_direct"))
    return render_page(PAGE5_BODY, section_step=2, endpoint_name="page5_age",
                       age_target=age_target, minors_custom=minors_custom)


# ====== Collection of Info (3) ======
@app.route("/collection/direct", methods=["GET", "POST"], endpoint="collection_direct")
def collection_direct():
    pi_choices = [
        ("names", "Names"),
        ("phone_numbers", "Phone numbers"),
        ("email_addresses", "Email addresses"),
        ("mailing_addresses", "Mailing addresses"),
        ("job_titles", "Job titles"),
        ("usernames", "Usernames"),
        ("passwords", "Passwords"),
        ("contact_preferences", "Contact preferences"),
        ("auth_data", "Contact or authentication data"),
        ("billing_addresses", "Billing addresses"),
        ("card_numbers", "Debit/credit card numbers"),
    ]
    device_choices = [
        ("gps_location", "Location (GPS)"),
        ("contacts_list", "Phonebook (Contacts list)"),
        ("camera_photos", "Camera (Pictures)"),
    ]

    prev = answers().get("Collection (Direct)", {})
    pi_opts_prev = set(prev.get("pi_opts", []))
    pi_items_prev = prev.get("pi_items", [])
    device_opts_prev = set(prev.get("device_opts", []))

    if request.method == "POST":
        if request.form.get("pi_add"):
            pi_opts = set(request.form.getlist("pi_opts"))
            pi_items = list(request.form.getlist("pi_items"))
            device_opts = set(request.form.getlist("device_opts"))

            own = (request.form.get("pi_own") or "").strip()
            if own:
                if own not in pi_items:
                    pi_items.append(own)
                pi_opts.add(f"custom::{own}")

            set_section("Collection (Direct)", {
                "pi_opts": list(pi_opts),
                "pi_items": pi_items,
                "device_opts": list(device_opts),
            })

            return render_page(
                PAGE6_BODY, section_step=3, endpoint_name="collection_direct",
                pi_choices=pi_choices, pi_opts=pi_opts, pi_items=pi_items,
                device_choices=device_choices, device_opts=device_opts
            )

        pi_opts = set(request.form.getlist("pi_opts"))
        pi_items = list(request.form.getlist("pi_items"))
        device_opts = set(request.form.getlist("device_opts"))

        set_section("Collection (Direct)", {
            "pi_opts": list(pi_opts),
            "pi_items": pi_items,
            "device_opts": list(device_opts),
        })

        chosen_labels = []
        val_to_label = dict(pi_choices)
        for v in pi_opts:
            if v.startswith("custom::"):
                chosen_labels.append(v.replace("custom::", "Custom: "))
            else:
                chosen_labels.append(val_to_label.get(v, v))

        dev_map = dict(device_choices)
        dev_labels = [dev_map.get(v, v) for v in device_opts]

        if chosen_labels:
            flash("Selected (direct collection): " + ", ".join(sorted(chosen_labels)))
        else:
            flash("No items selected for direct collection.")
        if dev_labels:
            flash("Selected (device collection): " + ", ".join(sorted(dev_labels)))

        return redirect(url_for("use_marketing"))

    # GET
    return render_page(
        PAGE6_BODY, section_step=3, endpoint_name="collection_direct",
        pi_choices=pi_choices, pi_opts=pi_opts_prev, pi_items=pi_items_prev,
        device_choices=device_choices, device_opts=device_opts_prev
    )


# ====== Use of Information (4): Marketing page ======
@app.route("/use/marketing", methods=["GET", "POST"], endpoint="use_marketing")
def use_marketing():
    prev = answers().get("Use of Information - Marketing", {})
    mk_send = prev.get("mk_send", "no")
    mk_opts = set(prev.get("mk_opts", []))
    mk_items = prev.get("mk_items", [])
    if request.method == "POST":
        if request.form.get("mk_add"):
            mk_send = request.form.get("mk_send", "no")
            mk_opts = set(request.form.getlist("mk_opts"))
            mk_items = request.form.getlist("mk_items")
            own = (request.form.get("mk_own") or "").strip()
            if own:
                if own not in mk_items:
                    mk_items = list(mk_items) + [own]
                mk_opts.add(f"custom::{own}")
            set_section("Use of Information - Marketing", {
                "mk_send": mk_send, "mk_opts": list(mk_opts), "mk_items": mk_items
            })
            return render_page(USE_MARKETING_BODY, section_step=4, endpoint_name="use_marketing",
                               mk_send=mk_send, mk_opts=mk_opts, mk_items=mk_items)

        mk_send = request.form.get("mk_send", "no")
        mk_opts = set(request.form.getlist("mk_opts"))
        mk_items = request.form.getlist("mk_items")
        set_section("Use of Information - Marketing", {
            "mk_send": mk_send, "mk_opts": list(mk_opts), "mk_items": mk_items
        })
        if mk_send == "yes":
            flash("Marketing enabled. Unsubscribe options: " + (", ".join(sorted(mk_opts)) if mk_opts else "none selected"))
        else:
            flash("No marketing communications.")
        return redirect(url_for('disclosure_ads'))

    return render_page(USE_MARKETING_BODY, section_step=4, endpoint_name="use_marketing",
                       mk_send=mk_send, mk_opts=mk_opts, mk_items=mk_items)


# ====== Disclosure chain (5) – combined page ======
@app.route("/disclosure/ads", methods=["GET", "POST"], endpoint="disclosure_ads")
def disclosure_ads():
    prev_ads = answers().get("Disclosure - Ads", {})
    prev_aff = answers().get("Disclosure - Affiliates", {})
    prev_partners = answers().get("Disclosure - Partners", {})

    ads = prev_ads.get("ads", "no")
    aff = prev_aff.get("aff", "no")
    partners = prev_partners.get("partners", "no")

    if request.method == "POST":
        ads = request.form.get("ads", "no")
        aff = request.form.get("aff", "no")
        partners = request.form.get("partners", "no")

        set_section("Disclosure - Ads", {"ads": ads})
        set_section("Disclosure - Affiliates", {"aff": aff})
        set_section("Disclosure - Partners", {"partners": partners})

        flash(f"Third-party ads: {ads}")
        flash(f"Business affiliates: {aff}")
        flash(f"Business partners: {partners}")

        return redirect(url_for('disclosure_security'))

    return render_page(
        DISCLOSURE_BODY, section_step=5, endpoint_name="disclosure_ads",
        ads=ads, aff=aff, partners=partners
    )


@app.route("/disclosure/security", methods=["GET", "POST"], endpoint="disclosure_security")
def disclosure_security():
    prev = answers().get("Disclosure - Security", {})
    sec = prev.get("sec")
    if request.method == "POST":
        sec = request.form.get("sec", "no")
        sec_ack = request.form.get("sec_ack", "")
        if sec == "no" and not sec_ack:
            flash("Please acknowledge the notice before continuing.")
            return render_page(DISC_SECURITY_BODY, section_step=5, endpoint_name="disclosure_security", sec=sec)
        set_section("Disclosure - Security", {"sec": sec, "sec_acknowledged": bool(sec_ack)})
        flash(f"Security measures: {sec}")
        return redirect(url_for('tracking_main'))
    return render_page(DISC_SECURITY_BODY, section_step=5, endpoint_name="disclosure_security", sec=sec)


# ====== Tracking Technologies (6) ======
@app.route("/tracking", methods=["GET", "POST"], endpoint="tracking_main")
def tracking_main():
    prev = answers().get("Tracking Technologies", {})
    tt = prev.get("tt")
    if request.method == "POST":
        tt = request.form.get("tt", "neither")
        set_section("Tracking Technologies", {"tt": tt})
        flash(f"Tracking technology choice: {tt}")
        return redirect(url_for('google_analytics'))
    return render_page(TRACKING_BODY, section_step=6, endpoint_name="tracking_main", tt=tt)


@app.route("/tracking/ga", methods=["GET", "POST"], endpoint="google_analytics")
def google_analytics():
    prev = answers().get("Google Analytics", {})
    ga = prev.get("ga")
    ga_feature = prev.get("ga_feature", "")
    ga_feature_choices = [
        ("remarketing", "Remarketing with Google Analytics"),
        ("gdn_reporting", "Google Display Network Impression Reporting"),
        ("demo_interest", "Google Analytics Demographics and Interests Reporting"),
        ("integrated_services", "Integrated services requiring cookies/identifiers"),
    ]
    if request.method == "POST":
        ga = request.form.get("ga", "no")
        ga_feature = ""
        if ga == "yes":
            ga_feature = request.form.get("ga_feature", "")
            flash("Google Analytics enabled" + (f" with feature: {ga_feature}" if ga_feature else ""))
        else:
            flash("Google Analytics not used.")
        set_section("Google Analytics", {"ga": ga, "ga_feature": ga_feature})
        return redirect(url_for('user_rights_dsar'))
    return render_page(GA_BODY, section_step=6, endpoint_name="google_analytics",
                       ga=ga, ga_feature=ga_feature, ga_feature_choices=ga_feature_choices)


# ====== User Rights (Page 14) — UPDATED to store contact methods ======
@app.route("/user-rights/dsar", methods=["GET", "POST"], endpoint="user_rights_dsar")
def user_rights_dsar():
    prev = answers().get("User Rights - DSAR", {})
    dsar = prev.get("dsar", "no")
    dsar_url = prev.get("dsar_url", "")
    access_when = prev.get("access_when", "law")

    contact_email = prev.get("contact_email", False)
    contact_email_addr = prev.get("contact_email_addr", "")
    contact_web = prev.get("contact_web", False)
    contact_web_link = prev.get("contact_web_link", "")
    contact_phone = prev.get("contact_phone", False)
    contact_phone_number = prev.get("contact_phone_number", "")
    contact_mail = prev.get("contact_mail", False)
    contact_post_addr = prev.get("contact_post_addr", "")

    if request.method == "POST":
        dsar = request.form.get("dsar", "no")
        dsar_url = (request.form.get("dsar_url") or "").strip()
        access_when = request.form.get("access_when", "law")

        contact_email = bool(request.form.get("contact_email"))
        contact_email_addr = (request.form.get("contact_email_addr") or "").strip()
        contact_web = bool(request.form.get("contact_web"))
        contact_web_link = (request.form.get("contact_web_link") or "").strip()
        contact_phone = bool(request.form.get("contact_phone"))
        contact_phone_number = (request.form.get("contact_phone_number") or "").strip()
        contact_mail = bool(request.form.get("contact_mail"))
        contact_post_addr = (request.form.get("contact_post_addr") or "").strip()

        set_section("User Rights - DSAR", {
            "dsar": dsar,
            "dsar_url": dsar_url,
            "access_when": access_when,
            "contact_email": contact_email,
            "contact_email_addr": contact_email_addr,
            "contact_web": contact_web,
            "contact_web_link": contact_web_link,
            "contact_phone": contact_phone,
            "contact_phone_number": contact_phone_number,
            "contact_mail": contact_mail,
            "contact_post_addr": contact_post_addr,
        })

        contact_bits = []
        if contact_email and contact_email_addr:
            contact_bits.append(f"email: {contact_email_addr}")
        if contact_web and contact_web_link:
            contact_bits.append(f"web: {contact_web_link}")
        if contact_phone and contact_phone_number:
            contact_bits.append(f"phone: {contact_phone_number}")
        if contact_mail and contact_post_addr:
            contact_bits.append("postal address provided")
        if dsar == "yes":
            flash(f"DSAR provided at: {dsar_url or '(URL not supplied)'} | Access: {access_when}")
        else:
            flash(f"Using Third-party's service | Access: {access_when}")
        if contact_bits:
            flash("Contact methods — " + "; ".join(contact_bits))

        return redirect(url_for('final_company'))

    return render_page(
        USER_RIGHTS_BODY, section_step=7, endpoint_name="user_rights_dsar",
        dsar=dsar, dsar_url=dsar_url, access_when=access_when,
        contact_email=contact_email, contact_email_addr=contact_email_addr,
        contact_web=contact_web, contact_web_link=contact_web_link,
        contact_phone=contact_phone, contact_phone_number=contact_phone_number,
        contact_mail=contact_mail, contact_post_addr=contact_post_addr
    )


# ====== Final Details ======
@app.route("/final/company", methods=["GET", "POST"], endpoint="final_company")
def final_company():
    prev = answers().get("Final - Company", {})
    company_name = prev.get("company_name", "")
    dba = prev.get("dba", "no")
    privacy_email = prev.get("privacy_email", "")
    phone = prev.get("phone", "")
    website_url = prev.get("website_url", "")

    if request.method == "POST":
        company_name = (request.form.get("company_name") or "").strip()
        dba = request.form.get("dba", "no")
        privacy_email = (request.form.get("privacy_email") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        website_url = (request.form.get("website_url") or "").strip()

        set_section("Final - Company", {
            "company_name": company_name,
            "dba": dba,
            "privacy_email": privacy_email,
            "phone": phone,
            "website_url": website_url,
        })
        flash("Company details saved.")
        return redirect(url_for('final_title'))

    return render_page(
        COMPANY_BODY, section_step=8, endpoint_name="final_company",
        company_name=company_name, dba=dba,
        privacy_email=privacy_email, phone=phone,
        website_url=website_url,
    )


@app.route("/final/title", methods=["GET", "POST"], endpoint="final_title")
def final_title():
    prev = answers().get("Final - Title", {})
    ptitle_opt = prev.get("ptitle_opt", "Privacy Policy")
    ptitle_custom = prev.get("ptitle_custom", "")
    if request.method == "POST":
        ptitle_opt = request.form.get("ptitle_opt", "Privacy Policy")
        ptitle_custom = (request.form.get("ptitle_custom") or "").strip()
        set_section("Final - Title", {
            "ptitle_opt": ptitle_opt, "ptitle_custom": ptitle_custom
        })
        flash("Policy title option saved.")
        return redirect(url_for('final_version_date'))
    return render_page(POLICY_TITLE_BODY, section_step=8, endpoint_name="final_title",
                       ptitle_opt=ptitle_opt, ptitle_custom=ptitle_custom)

@app.route("/final/version-date", methods=["GET","POST"], endpoint="final_version_date")
def final_version_date():
    prev = answers().get("Final - Version Date", {})
    effective_date = prev.get("effective_date", date.today().isoformat())
    ttl = answers().get("Final - Title", {})
    ptitle_resolved = ttl.get("ptitle_custom") if ttl.get("ptitle_opt") == "custom" and ttl.get("ptitle_custom") else (ttl.get("ptitle_opt") or "Privacy Policy")

    if request.method == "POST":
        if request.form.get("publish"):
            eff = request.form.get("effective_date") or date.today().isoformat()
            set_section("Final - Version Date", {"effective_date": eff})

            if "submission_meta" not in session:
                session["submission_meta"] = {
                    "submission_id": str(uuid.uuid4()),
                    "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

            try:
                dump_answers_to_excels()
                generated = generate_policy_docx()
                session["last_policy_path"] = str(generated)
                flash(f"Policy ready. Effective date: {eff}. Answers saved to: {CSV_OUTPUT_FOLDER}")
                flash(f"Generated policy document: {generated.name}")
            except Exception as e:
                flash(f"Error saving questionnaires or generating policy: {e}")

            #return redirect(url_for('final_version_date'))
            return redirect(url_for('policy_ready'))

    # compute link for last generated file (if any)
    last_policy_path = session.get("last_policy_path")
    last_policy_name, last_policy_url = None, None
    if last_policy_path and Path(last_policy_path).exists():
        last_policy_name = Path(last_policy_path).name
        last_policy_url  = url_for('download_policy', fname=last_policy_name)

    return render_page(VERSION_DATE_BODY, section_step=8, endpoint_name="final_version_date",
                       effective_date=effective_date, ptitle_resolved=ptitle_resolved,
                       last_policy_name=last_policy_name, last_policy_url=last_policy_url)

@app.route("/policies/<path:fname>")
def download_policy(fname):
    # Serves files from POLICIES_OUTPUT_DIR
    return send_from_directory(POLICY_OUTPUT_DIR, fname, as_attachment=True)

@app.route("/final/policy-ready", methods=["GET"], endpoint="policy_ready")
def policy_ready():
    latest_policy_fname = session.get("latest_policy_fname")
    return render_page(
        POLICY_READY_BODY,
        section_step=17,
        endpoint_name="final_version_date",
        latest_policy_fname=latest_policy_fname
    )

# ====== Save to Excel helpers (updated to include contact methods) ======
def dump_answers_to_excels():
    a = answers()
    meta = session.get("submission_meta", {
        "submission_id": str(uuid.uuid4()),
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    def val(section, key, default=""):
        return a.get(section, {}).get(key, default)

    def yn_from_str(s: str, yes_value="yes") -> str:
        return "Yes" if (s or "").lower() == yes_value else "No"

    def join_labels(vals, mapping=None):
        out = []
        mapping = mapping or {}
        for v in (vals or []):
            if isinstance(v, str) and v.startswith("custom::"):
                out.append("Custom: " + v.split("custom::", 1)[1])
            else:
                out.append(mapping.get(v, v))
        return ", ".join(out)

    company_name = val("Final - Company", "company_name")
    # Prefer contact details chosen on Page 14; fall back to Final - Company if blank
    dsar_sec = a.get("User Rights - DSAR", {})
    privacy_email = (val("Final - Company", "privacy_email") or dsar_sec.get("contact_email_addr",""))
    phone = (val("Final - Company", "phone") or dsar_sec.get("contact_phone_number",""))
    website_url = (val("Final - Company", "website_url") or dsar_sec.get("contact_web_link",""))
    contact_address = dsar_sec.get("contact_post_addr","")

    app_name = val("Mobile Application", "app_name")
    apk_saved_path = str(APK_UPLOAD_DIR.resolve())
    jurisdictions = ""

    # Direct-collection choices
    pi_choices = dict([
        ("names", "Names"), ("phone_numbers", "Phone numbers"), ("email_addresses", "Email addresses"),
        ("mailing_addresses", "Mailing addresses"), ("job_titles", "Job titles"), ("usernames", "Usernames"),
        ("passwords", "Passwords"), ("contact_preferences", "Contact preferences"),
        ("auth_data", "Contact or authentication data"), ("billing_addresses", "Billing addresses"),
        ("card_numbers", "Debit/credit card numbers"),
    ])
    pi_opts = a.get("Collection (Direct)", {}).get("pi_opts", [])
    collect_personal_data = "Yes" if pi_opts else "No"
    data_categories = join_labels(pi_opts, mapping=pi_choices)

    # NEW: device-collected choices
    device_choices = dict([
        ("gps_location", "Location (GPS)"),
        ("contacts_list", "Phonebook (Contacts list)"),
        ("camera_photos", "Camera (Pictures)"),
    ])
    device_opts = a.get("Collection (Direct)", {}).get("device_opts", [])
    device_data_collected = "Yes" if device_opts else "No"
    device_data_categories = join_labels(device_opts, mapping=device_choices)

    can_register = val("User Accounts", "can_register", "no")
    collection_methods = "Forms" if can_register == "yes" else ""
    source_third_party = "No"

    age_target = val("User Age", "age_target")
    minors_data = yn_from_str(age_target, "yes")
    children_under_13 = "No"
    parental_consent = "No"

    mk_send = val("Use of Information - Marketing", "mk_send", "no")
    ga_used = yn_from_str(val("Google Analytics", "ga"), "yes")
    ga_feature = val("Google Analytics", "ga_feature", "")

    purpose_marketing = yn_from_str(mk_send, "yes")
    purpose_analytics = ga_used
    purpose_core_functions = "Yes" if can_register == "yes" else "No"
    purpose_personalization = "No"
    purpose_compliance = "Yes"

    tt = val("Tracking Technologies", "tt", "neither")
    cookies_flag = "Yes" if tt in ("cookies", "both") else "No"
    maps_apis = "Yes" if tt in ("maps", "both") else "No"

    ads = yn_from_str(val("Disclosure - Ads", "ads", "no"), "yes")
    affiliates = yn_from_str(val("Disclosure - Affiliates", "aff", "no"), "yes")
    partners = yn_from_str(val("Disclosure - Partners", "partners", "no"), "yes")

    sec = yn_from_str(val("Disclosure - Security", "sec", "no"), "yes")
    breach_notification = ""
    retention_policy = ""

    dsar = val("User Rights - DSAR", "dsar", "no")
    dsar_url = val("User Rights - DSAR", "dsar_url", "")
    access_when = val("User Rights - DSAR", "access_when", "law")

    # Build request process text using DSAR URL or chosen contact methods
    contact_parts = []
    if dsar_sec.get("contact_email") and dsar_sec.get("contact_email_addr"):
        contact_parts.append(f"Email: {dsar_sec.get('contact_email_addr')}")
    if dsar_sec.get("contact_web") and dsar_sec.get("contact_web_link"):
        contact_parts.append(f"Website: {dsar_sec.get('contact_web_link')}")
    if dsar_sec.get("contact_phone") and dsar_sec.get("contact_phone_number"):
        contact_parts.append(f"Phone: {dsar_sec.get('contact_phone_number')}")
    if dsar_sec.get("contact_mail") and dsar_sec.get("contact_post_addr"):
        contact_parts.append(f"Postal: {dsar_sec.get('contact_post_addr')}")

    rights_access = "Yes" if dsar in ("yes", "no") else "No"
    rights_delete = rights_access
    rights_correct = rights_access
    rights_portability = "No"
    rights_object = "No"
    rights_withdraw_consent = "No"
    if dsar == "yes":
        rights_request_process = dsar_url or ("; ".join(contact_parts) if contact_parts else "Use provided contact details")
    else:
        rights_request_process = "Third-party service"

    ccpa_sale_share = "No"
    mk_opts = set(a.get("Use of Information - Marketing", {}).get("mk_opts", []))
    opt_out_links = "Yes" if ("unsubscribe_link" in mk_opts or "text_stop" in mk_opts) else "No"
    sensitive_pi = "No"
    limit_sensitive_pi = "No"

    eff_date = val("Final - Version Date", "effective_date", date.today().isoformat())
    policy_update_process = ""
    last_update_date = eff_date
    additional_contacts = "; ".join([p for p in [
        ("Email" if dsar_sec.get("contact_email") and dsar_sec.get("contact_email_addr") else ""),
        ("Website" if dsar_sec.get("contact_web") and dsar_sec.get("contact_web_link") else ""),
        ("Phone" if dsar_sec.get("contact_phone") and dsar_sec.get("contact_phone_number") else ""),
        ("Postal" if dsar_sec.get("contact_mail") and dsar_sec.get("contact_post_addr") else "")
    ] if p])
    notes_internal = ""

    MASTER_COLUMNS = [
        "org_name", "website_url", "app_name", "contact_email", "contact_address", "jurisdictions",
        "collect_personal_data", "data_categories", 
        # NEW device columns
        "device_data_collected", "device_data_categories",
        "collection_methods", "source_third_party",
        "minors_data",
        "purpose_core_functions", "purpose_analytics", "purpose_marketing", "purpose_personalization", "purpose_compliance",
        "cookies", "maps_apis", "ga_used", "ga_feature",
        "share_advertisers", "share_affiliates", "share_partners",
        "rights_access", "rights_correct", "rights_delete", "rights_portability", "rights_object", "rights_withdraw_consent", "rights_request_process",
        "retention_policy", "security_measures", "breach_notification",
        "transfer_outside_region", "transfer_mechanisms",
        "children_under_13", "parental_consent",
        "ccpa_sale_share", "opt_out_links", "sensitive_pi", "limit_sensitive_pi",
        "policy_update_process", "last_update_date", "additional_contacts", "notes_internal",
        "submission_id", "submitted_at", "apk_saved_path"
    ]

    master_row = {
        "org_name": company_name,
        "website_url": website_url,
        "app_name": app_name,
        "contact_email": privacy_email,
        "contact_address": contact_address,
        "jurisdictions": jurisdictions,
        "collect_personal_data": collect_personal_data,
        "data_categories": data_categories,
        "device_data_collected": device_data_collected,            # NEW
        "device_data_categories": device_data_categories,          # NEW
        "collection_methods": collection_methods,
        "source_third_party": source_third_party,
        "minors_data": minors_data,
        "purpose_core_functions": purpose_core_functions,
        "purpose_analytics": purpose_analytics,
        "purpose_marketing": purpose_marketing,
        "purpose_personalization": purpose_personalization,
        "purpose_compliance": purpose_compliance,
        "cookies": cookies_flag,
        "maps_apis": maps_apis,
        "ga_used": ga_used,
        "ga_feature": ga_feature,
        "share_advertisers": ads,
        "share_affiliates": affiliates,
        "share_partners": partners,
        "rights_access": rights_access,
        "rights_correct": rights_correct,
        "rights_delete": rights_delete,
        "rights_portability": rights_portability,
        "rights_object": rights_object,
        "rights_withdraw_consent": rights_withdraw_consent,
        "rights_request_process": rights_request_process,
        "retention_policy": retention_policy,
        "security_measures": sec,
        "breach_notification": breach_notification,
        "transfer_outside_region": "No",
        "transfer_mechanisms": "",
        "children_under_13": children_under_13,
        "parental_consent": parental_consent,
        "ccpa_sale_share": ccpa_sale_share,
        "opt_out_links": opt_out_links,
        "sensitive_pi": sensitive_pi,
        "limit_sensitive_pi": limit_sensitive_pi,
        "policy_update_process": policy_update_process,
        "last_update_date": last_update_date,
        "additional_contacts": additional_contacts,
        "notes_internal": notes_internal,
        "submission_id": meta["submission_id"],
        "submitted_at": meta["submitted_at"],
        "apk_saved_path": apk_saved_path,
    }

    df_master = pd.DataFrame([[master_row.get(c, "") for c in MASTER_COLUMNS]], columns=MASTER_COLUMNS)
    master_path = CSV_OUTPUT_FOLDER / "questionnaire_master.xlsx"
    df_master.to_excel(master_path, index=False)

    by_path = CSV_OUTPUT_FOLDER / "questionnaire_by_section.xlsx"
    with pd.ExcelWriter(by_path, engine="openpyxl") as xw:
        # Organization
        org_cols = ["apk_saved_path","app_name","contact_address","contact_email","jurisdictions","org_name","submission_id","submitted_at","website_url","phone"]
        org_row = {
            "apk_saved_path": apk_saved_path,
            "app_name": app_name,
            "contact_address": contact_address,
            "contact_email": privacy_email,
            "jurisdictions": jurisdictions,
            "org_name": company_name,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"],
            "website_url": website_url,
            "phone": phone,
        }
        pd.DataFrame([[org_row.get(c,"") for c in org_cols]], columns=org_cols).to_excel(xw, sheet_name="Organization", index=False)

        # Data Collection  (UPDATED to include device columns)
        dc_cols = [
            "apk_saved_path",
            "collect_personal_data","data_categories",
            "device_data_collected","device_data_categories",   # NEW
            "collection_methods","source_third_party",
            "submission_id","submitted_at"
        ]
        dc_row = {
            "apk_saved_path": apk_saved_path,
            "collect_personal_data": collect_personal_data,
            "data_categories": data_categories,
            "device_data_collected": device_data_collected,        # NEW
            "device_data_categories": device_data_categories,      # NEW
            "collection_methods": collection_methods,
            "source_third_party": source_third_party,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[dc_row.get(c,"") for c in dc_cols]], columns=dc_cols).to_excel(xw, sheet_name="Data Collection", index=False)

        # Purposes of Use
        pu_cols = ["apk_saved_path","purpose_core_functions","purpose_analytics","purpose_marketing","purpose_personalization","purpose_compliance","other_purposes","submission_id","submitted_at"]
        pu_row = {
            "apk_saved_path": apk_saved_path,
            "purpose_core_functions": purpose_core_functions,
            "purpose_analytics": purpose_analytics,
            "purpose_marketing": purpose_marketing,
            "purpose_personalization": purpose_personalization,
            "purpose_compliance": purpose_compliance,
            "other_purposes": "",
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[pu_row.get(c,"") for c in pu_cols]], columns=pu_cols).to_excel(xw, sheet_name="Purposes of Use", index=False)

        # Tracking & Cookies
        tk_cols = ["apk_saved_path","cookies","maps_apis","ga_used","ga_feature","submission_id","submitted_at"]
        tk_row = {
            "apk_saved_path": apk_saved_path,
            "cookies": cookies_flag,
            "maps_apis": maps_apis,
            "ga_used": ga_used,
            "ga_feature": ga_feature,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[tk_row.get(c,"") for c in tk_cols]], columns=tk_cols).to_excel(xw, sheet_name="Tracking & Cookies", index=False)

        # Sharing & Disclosure
        sd_cols = ["apk_saved_path","share_advertisers","share_affiliates","share_partners","submission_id","submitted_at"]
        sd_row = {
            "apk_saved_path": apk_saved_path,
            "share_advertisers": ads,
            "share_affiliates": affiliates,
            "share_partners": partners,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[sd_row.get(c,"") for c in sd_cols]], columns=sd_cols).to_excel(xw, sheet_name="Sharing & Disclosure", index=False)

        # User Rights
        ur_cols = ["apk_saved_path","rights_access","rights_correct","rights_delete","rights_portability","rights_object","rights_withdraw_consent","rights_request_process","submission_id","submitted_at"]
        ur_row = {
            "apk_saved_path": apk_saved_path,
            "rights_access": rights_access,
            "rights_correct": rights_correct,
            "rights_delete": rights_delete,
            "rights_portability": rights_portability,
            "rights_object": rights_object,
            "rights_withdraw_consent": rights_withdraw_consent,
            "rights_request_process": rights_request_process,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[ur_row.get(c,"") for c in ur_cols]], columns=ur_cols).to_excel(xw, sheet_name="User Rights", index=False)

        # Retention & Security
        rs_cols = ["apk_saved_path","retention_policy","security_measures","breach_notification","submission_id","submitted_at"]
        rs_row = {
            "apk_saved_path": apk_saved_path,
            "retention_policy": retention_policy,
            "security_measures": sec,
            "breach_notification": breach_notification,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[rs_row.get(c,"") for c in rs_cols]], columns=rs_cols).to_excel(xw, sheet_name="Retention & Security", index=False)

        # International Transfers
        it_cols = ["apk_saved_path","transfer_mechanisms","transfer_outside_region","submission_id","submitted_at"]
        it_row = {
            "apk_saved_path": apk_saved_path,
            "transfer_mechanisms": "",
            "transfer_outside_region": "No",
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[it_row.get(c,"") for c in it_cols]], columns=it_cols).to_excel(xw, sheet_name="International Transfers", index=False)

        # Children
        ch_cols = ["apk_saved_path","children_under_13","parental_consent","submission_id","submitted_at"]
        ch_row = {
            "apk_saved_path": apk_saved_path,
            "children_under_13": children_under_13,
            "parental_consent": parental_consent,
            "submission_id": meta["submission_id"],
            "submitted_at": meta["submitted_at"]
        }
        pd.DataFrame([[ch_row.get(c,"") for c in ch_cols]], columns=ch_cols).to_excel(xw, sheet_name="Children", index=False)

# Dev-only download route
@app.route("/uploads/<path:fname>")
def downloads(fname):
    return send_from_directory(APK_UPLOAD_DIR, fname, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
