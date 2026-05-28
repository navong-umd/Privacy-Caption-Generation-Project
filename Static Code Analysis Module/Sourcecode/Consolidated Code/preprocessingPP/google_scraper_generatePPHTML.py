"""
Clean privacy policy dataset builder (KH top free apps) - UPDATED (fixes IndexError in list merging)

Input:
- CSV with columns: appId, title, privacy_policy_url
  Example: apps_kh_top_per_group.csv

Output:
- OUTPUT_FOLDER/Clean_Dataset/
    - policies_txt/            (one .txt per appId)
    - policies_html/           (optional: raw html snapshots)
    - dataset_index.csv        (metadata + status for each app)
    - run_log.txt

Workflow implemented:
1) Download HTML via Selenium (headless Chrome) to execute JS/dynamic content
2) Remove non-relevant + hidden text (script/style/nav/video/comments + hidden elements)
3) Flatten/convert HTML -> Markdown (html2text) to preserve readable structure
4) Merge formatted lists into preceding clauses (colon + bullet/number patterns + nesting-ish handling)
5) Markdown -> final plaintext (strip markdown syntax, normalize unicode)
6) Language detection with langid; keep only English-dominant docs

Install:
pip install pandas selenium webdriver-manager beautifulsoup4 lxml html2text langid tqdm

Notes:
- Some sites block automation; those will be logged as failed/unreachable.
- If you already have chromedriver configured, you can remove webdriver-manager usage.
"""

import os
import re
import time
import json
import html
import hashlib
import unicodedata
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List

import pandas as pd
from tqdm import tqdm

import langid
import html2text
from bs4 import BeautifulSoup, Comment

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service as ChromeService
    WEBDRIVER_MANAGER_AVAILABLE = True
except Exception:
    WEBDRIVER_MANAGER_AVAILABLE = False


# -------------------------
# Config (EDIT THESE)
# -------------------------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"
INPUT_CSV = os.path.join(OUTPUT_FOLDER, "apps_kh_top_per_group.csv")

OUT_ROOT = os.path.join(OUTPUT_FOLDER, "Clean_Dataset")
OUT_TXT = os.path.join(OUT_ROOT, "policies_txt")
OUT_HTML = os.path.join(OUT_ROOT, "policies_html")
OUT_INDEX = os.path.join(OUT_ROOT, "dataset_index.csv")
OUT_LOG = os.path.join(OUT_ROOT, "run_log.txt")

SAVE_RAW_HTML = True
PAGELOAD_TIMEOUT_SEC = 40
WAIT_AFTER_LOAD_SEC = 2.5
MAX_RETRIES_PER_URL = 2

MIN_TEXT_CHARS = 400
ENGLISH_DOMINANCE_THRESHOLD = 0.60

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# -------------------------
# Utilities
# -------------------------
def ensure_dirs() -> None:
    os.makedirs(OUT_ROOT, exist_ok=True)
    os.makedirs(OUT_TXT, exist_ok=True)
    if SAVE_RAW_HTML:
        os.makedirs(OUT_HTML, exist_ok=True)


def log_line(msg: str) -> None:
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}"
    print(line)
    with open(OUT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def safe_filename(s: str, max_len: int = 160) -> str:
    s = re.sub(r"[^\w\-.]+", "_", (s or "").strip())
    return s[:max_len] if len(s) > max_len else s


def stable_id(app_id: str, url: str) -> str:
    if isinstance(app_id, str) and app_id.strip():
        return app_id.strip()
    h = hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:16]
    return f"no_appid_{h}"


# -------------------------
# Selenium setup + fetch
# -------------------------
def build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1365,900")
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument("--disable-blink-features=AutomationControlled")

    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.default_content_setting_values.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)

    if WEBDRIVER_MANAGER_AVAILABLE:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(PAGELOAD_TIMEOUT_SEC)
    return driver


def fetch_html(driver: webdriver.Chrome, url: str) -> Tuple[Optional[str], Optional[str]]:
    if not isinstance(url, str) or not url.strip():
        return None, "missing_url"

    url = url.strip()
    last_err = None

    for attempt in range(1, MAX_RETRIES_PER_URL + 1):
        try:
            driver.get(url)
            WebDriverWait(driver, PAGELOAD_TIMEOUT_SEC).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(WAIT_AFTER_LOAD_SEC)

            page_source = driver.page_source
            if not page_source or len(page_source) < 200:
                last_err = "empty_page_source"
                continue

            return page_source, None

        except (TimeoutException, WebDriverException) as e:
            last_err = f"selenium_error: {type(e).__name__}"
            time.sleep(1.5 * attempt)

    return None, last_err or "unknown_fetch_error"


# -------------------------
# Cleaning HTML (remove non-relevant + hidden text)
# -------------------------
def _safe_get_attr(tag, key: str, default=None):
    """
    bs4 Tag normally has attrs as a dict, but malformed HTML can lead to attrs=None.
    This avoids AttributeError seen in the trace.
    """
    try:
        attrs = getattr(tag, "attrs", None)
        if not isinstance(attrs, dict):
            return default
        return attrs.get(key, default)
    except Exception:
        return default


def remove_hidden_elements(soup: BeautifulSoup) -> None:
    hidden_style_patterns = [
        r"display\s*:\s*none",
        r"visibility\s*:\s*hidden",
        r"opacity\s*:\s*0(\.0+)?\b",
        r"height\s*:\s*0(px)?\b",
        r"width\s*:\s*0(px)?\b",
        r"font-size\s*:\s*0(px)?\b",
        r"clip\s*:\s*rect",
    ]
    hidden_re = re.compile("|".join(hidden_style_patterns), flags=re.IGNORECASE)

    # Remove tags with hidden attribute
    for tag in soup.find_all(attrs={"hidden": True}):
        try:
            tag.decompose()
        except Exception:
            pass

    # aria-hidden="true"
    for tag in soup.find_all(attrs={"aria-hidden": re.compile(r"true", re.I)}):
        try:
            tag.decompose()
        except Exception:
            pass

    # Inline style hidden patterns (hardened)
    for tag in soup.find_all(style=True):
        style = _safe_get_attr(tag, "style", "") or ""
        if isinstance(style, list):
            style = " ".join([str(x) for x in style])
        if hidden_re.search(str(style)):
            try:
                tag.decompose()
            except Exception:
                pass


def strip_non_relevant_tags(soup: BeautifulSoup) -> None:
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        try:
            c.extract()
        except Exception:
            pass

    for name in ["script", "style", "nav", "video", "audio", "noscript", "svg", "canvas", "iframe", "form"]:
        for tag in soup.find_all(name):
            try:
                tag.decompose()
            except Exception:
                pass

    for selector in [
        {"role": "navigation"},
        {"role": "banner"},
        {"role": "dialog"},
    ]:
        for tag in soup.find_all(attrs=selector):
            try:
                tag.decompose()
            except Exception:
                pass


def remove_navigation_like_links(soup: BeautifulSoup) -> None:
    nav_text_patterns = re.compile(
        r"\b(learn more|back to top|return to top|top|home|menu|skip to|cookie settings|cookies settings|privacy settings)\b",
        flags=re.IGNORECASE,
    )

    for a in soup.find_all("a"):
        try:
            text = (a.get_text(" ", strip=True) or "").strip()
            href = (_safe_get_attr(a, "href", "") or "").strip()

            if not text and href:
                a.decompose()
                continue

            if nav_text_patterns.search(text):
                a.decompose()
                continue

            a.replace_with(text)
        except Exception:
            # If anything weird happens, drop the anchor safely
            try:
                a.decompose()
            except Exception:
                pass


def html_clean_to_markdown(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "lxml")

    main = soup.find("main")
    article = soup.find("article")
    container = article or main or soup.body or soup

    soup2 = BeautifulSoup(str(container), "lxml")

    strip_non_relevant_tags(soup2)
    remove_hidden_elements(soup2)
    remove_navigation_like_links(soup2)

    h = html2text.HTML2Text()
    h.ignore_images = True
    h.ignore_emphasis = False
    h.ignore_links = True
    h.body_width = 0
    h.single_line_break = False

    md = h.handle(str(soup2))
    md = md.replace("\r\n", "\n").replace("\r", "\n")
    md = re.sub(r"\n{3,}", "\n\n", md).strip()
    return md


# -------------------------
# Merge formatted lists into preceding clauses
# -------------------------
BULLET_RE = re.compile(
    r"^\s*(?:"
    r"[*\-•]|"
    r"\d+[\).\]]|"
    r"\([a-zA-Z0-9]+\)|"
    r"[a-zA-Z][\).\]]"
    r")\s+(?P<item>.+?)\s*$"
)
COLON_END_RE = re.compile(r":\s*$")


def is_list_item(line: str) -> bool:
    return BULLET_RE.match(line.strip()) is not None


def strip_list_marker(line: str) -> str:
    m = BULLET_RE.match(line.strip())
    if not m:
        return line.strip()
    return (m.group("item") or "").strip()


def merge_lists_in_markdown(md: str) -> str:
    lines = md.split("\n")
    out: List[str] = []
    i = 0

    while i < len(lines):
        line = lines[i].rstrip()

        if not line.strip():
            out.append("")
            i += 1
            continue

        if COLON_END_RE.search(line.strip()):
            j = i + 1
            items: List[str] = []
            blank_budget = 1

            while j < len(lines):
                nxt = lines[j].rstrip()

                if not nxt.strip():
                    if blank_budget > 0:
                        blank_budget -= 1
                        j += 1
                        continue
                    break

                if is_list_item(nxt):
                    items.append(strip_list_marker(nxt))
                    j += 1
                    continue

                break

            if items:
                merged = line.strip()
                merged_items = "; ".join([it for it in items if it])

                if merged_items:
                    merged = merged + " " + merged_items
                    if not merged.endswith("."):
                        merged += "."
                    out.append(merged)
                    i = j
                    continue

        out.append(line)
        i += 1

    merged_md = "\n".join(out)
    merged_md = re.sub(r"\n{3,}", "\n\n", merged_md).strip()
    return merged_md


# -------------------------
# Markdown -> final plaintext
# -------------------------
MD_ARTIFACTS_RE = [
    (re.compile(r"^\s{0,3}#{1,6}\s+", re.M), ""),
    (re.compile(r"[*_]{1,3}([^*_]+)[*_]{1,3}"), r"\1"),
    (re.compile(r"`{1,3}([^`]+)`{1,3}"), r"\1"),
    (re.compile(r"\[([^\]]+)\]\([^)]+\)"), r"\1"),
    (re.compile(r"^\s{0,3}>\s?", re.M), ""),
]


def markdown_to_text(md: str) -> str:
    txt = md
    txt = re.sub(r"```.*?```", " ", txt, flags=re.S)

    for rgx, repl in MD_ARTIFACTS_RE:
        txt = rgx.sub(repl, txt)

    txt = re.sub(
        r"^\s*(?:[*\-•]|\d+[\).\]]|\([a-zA-Z0-9]+\)|[a-zA-Z][\).\]])\s+",
        "",
        txt,
        flags=re.M,
    )

    txt = html.unescape(txt)
    txt = unicodedata.normalize("NFKC", txt)
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip()


# -------------------------
# Language detection and filtering
# -------------------------
def english_dominance_score(text: str) -> Tuple[str, float]:
    text = text.strip()
    if len(text) < 200:
        lang, _ = langid.classify(text)
        return lang, 1.0 if lang == "en" else 0.0

    chunk_size = 1200
    chunks = [text[i:i + chunk_size] for i in range(0, min(len(text), 12000), chunk_size)]
    if not chunks:
        lang, _ = langid.classify(text)
        return lang, 1.0 if lang == "en" else 0.0

    en_hits = 0
    for ch in chunks:
        lang, _ = langid.classify(ch)
        if lang == "en":
            en_hits += 1

    frac_en = en_hits / max(1, len(chunks))
    overall_lang, _ = langid.classify(text[:4000])
    return overall_lang, float(frac_en)


# -------------------------
# Pipeline per HTML
# -------------------------
def process_policy_html(raw_html: str) -> Tuple[str, Dict[str, Any]]:
    md = html_clean_to_markdown(raw_html)
    md2 = merge_lists_in_markdown(md)
    txt = markdown_to_text(md2)

    meta: Dict[str, Any] = {
        "md_chars": len(md),
        "md_merged_chars": len(md2),
        "txt_chars": len(txt),
    }
    return txt, meta


# -------------------------
# Main
# -------------------------
def main() -> None:
    ensure_dirs()
    log_line(f"Input CSV: {INPUT_CSV}")
    log_line(f"Output root: {OUT_ROOT}")

    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    df = pd.read_csv(INPUT_CSV)
    required_cols = {"appId", "title", "privacy_policy_url"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")

    index_rows: List[Dict[str, Any]] = []

    driver = None
    try:
        driver = build_driver()

        for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing policies"):
            app_id_raw = str(row.get("appId", "") if pd.notna(row.get("appId", "")) else "")
            title = str(row.get("title", "") if pd.notna(row.get("title", "")) else "")
            url = str(row.get("privacy_policy_url", "") if pd.notna(row.get("privacy_policy_url", "")) else "")

            app_id = stable_id(app_id_raw, url)
            base_name = safe_filename(app_id)

            out_txt_path = os.path.join(OUT_TXT, f"{base_name}.txt")
            out_html_path = os.path.join(OUT_HTML, f"{base_name}.html") if SAVE_RAW_HTML else ""

            if os.path.exists(out_txt_path):
                index_rows.append({
                    "appId": app_id_raw,
                    "appId_used": app_id,
                    "title": title,
                    "privacy_policy_url": url,
                    "status": "skipped_exists",
                    "txt_path": out_txt_path,
                    "html_path": out_html_path if SAVE_RAW_HTML else "",
                    "lang": "",
                    "english_fraction": "",
                    "txt_chars": os.path.getsize(out_txt_path),
                    "notes": "",
                })
                continue

            raw_html, fetch_err = fetch_html(driver, url)
            if fetch_err or not raw_html:
                index_rows.append({
                    "appId": app_id_raw,
                    "appId_used": app_id,
                    "title": title,
                    "privacy_policy_url": url,
                    "status": "failed_fetch",
                    "txt_path": "",
                    "html_path": "",
                    "lang": "",
                    "english_fraction": "",
                    "txt_chars": 0,
                    "notes": fetch_err or "no_html",
                })
                continue

            if SAVE_RAW_HTML:
                try:
                    with open(out_html_path, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(raw_html)
                except Exception:
                    pass

            # HARDEN: never crash the run on one bad HTML
            try:
                txt, meta = process_policy_html(raw_html)
            except Exception as e:
                index_rows.append({
                    "appId": app_id_raw,
                    "appId_used": app_id,
                    "title": title,
                    "privacy_policy_url": url,
                    "status": "failed_processing",
                    "txt_path": "",
                    "html_path": out_html_path if SAVE_RAW_HTML else "",
                    "lang": "",
                    "english_fraction": "",
                    "txt_chars": 0,
                    "notes": f"processing_error: {type(e).__name__}: {e}",
                })
                continue

            if len(txt) < MIN_TEXT_CHARS:
                index_rows.append({
                    "appId": app_id_raw,
                    "appId_used": app_id,
                    "title": title,
                    "privacy_policy_url": url,
                    "status": "dropped_too_short",
                    "txt_path": "",
                    "html_path": out_html_path if SAVE_RAW_HTML else "",
                    "lang": "",
                    "english_fraction": "",
                    "txt_chars": len(txt),
                    "notes": f"text_too_short<{MIN_TEXT_CHARS}",
                })
                continue

            lang, frac_en = english_dominance_score(txt)
            if frac_en < ENGLISH_DOMINANCE_THRESHOLD or lang != "en":
                index_rows.append({
                    "appId": app_id_raw,
                    "appId_used": app_id,
                    "title": title,
                    "privacy_policy_url": url,
                    "status": "dropped_non_english",
                    "txt_path": "",
                    "html_path": out_html_path if SAVE_RAW_HTML else "",
                    "lang": lang,
                    "english_fraction": frac_en,
                    "txt_chars": len(txt),
                    "notes": f"lang={lang}, frac_en={frac_en:.2f}",
                })
                continue

            with open(out_txt_path, "w", encoding="utf-8") as f:
                f.write(f"APP_ID: {app_id}\n")
                f.write(f"TITLE: {title}\n")
                f.write(f"URL: {url}\n")
                f.write(f"COLLECTED_AT_LOCAL: {datetime.now().isoformat(timespec='seconds')}\n\n")
                f.write(txt.strip() + "\n")

            index_rows.append({
                "appId": app_id_raw,
                "appId_used": app_id,
                "title": title,
                "privacy_policy_url": url,
                "status": "ok",
                "txt_path": out_txt_path,
                "html_path": out_html_path if SAVE_RAW_HTML else "",
                "lang": lang,
                "english_fraction": frac_en,
                "txt_chars": len(txt),
                "notes": json.dumps(meta, ensure_ascii=False),
            })

    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

    out_df = pd.DataFrame(index_rows)
    out_df.to_csv(OUT_INDEX, index=False, encoding="utf-8-sig")

    status_counts = out_df["status"].value_counts(dropna=False).to_dict()
    log_line(f"Done. Status counts: {status_counts}")
    log_line(f"Index written: {OUT_INDEX}")
    log_line(f"TXT folder: {OUT_TXT}")
    if SAVE_RAW_HTML:
        log_line(f"HTML folder: {OUT_HTML}")


if __name__ == "__main__":
    main()
