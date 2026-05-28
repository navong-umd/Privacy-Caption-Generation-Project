"""
Google Play (Cambodia) dataset builder - BY CATEGORY (genre) using google_play_scraper.list()

Why this version won't "get stuck" as easily:
- Uses list(collection=..., category=...) instead of many keyword searches
- Wraps app() calls in a hard-timeout thread so a single hang cannot block the run

Outputs:
- CSV with all fields from list() rows (prefixed list_)
- all fields from app() detail (prefixed app_)
- plus provenance fields + privacy policy reachability fields

Install:
pip install --upgrade google-play-scraper pandas tabulate tqdm requests
"""

import os
import time
import random
import json
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import requests
from tqdm import tqdm
from tabulate import tabulate

from google_play_scraper import app as gp_app
from google_play_scraper import list as gp_list
from google_play_scraper import collection, category


# --------------------------
# Config
# --------------------------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"

COUNTRY = "kh"
LANG = "en"

TOP_PER_CATEGORY = 5

# Choose which "chart" you want per category
# Common choices: TOP_FREE, TOP_PAID, GROSSING
TARGET_COLLECTION = collection.TOP_FREE

# Categories to fetch (must exist in google_play_scraper.category)
TARGET_CATEGORY_NAMES = [
    "APPLICATION",
    "ART_AND_DESIGN",
    "AUTO_AND_VEHICLES",
    "BEAUTY",
    "BOOKS_AND_REFERENCE",
    "BUSINESS",
    "COMICS",
    "COMMUNICATION",
    "DATING",
    "EDUCATION",
    "ENTERTAINMENT",
    "EVENTS",
    "FINANCE",
    "FOOD_AND_DRINK",
    "HEALTH_AND_FITNESS",
    "HOUSE_AND_HOME",
    "LIBRARIES_AND_DEMO",
    "LIFESTYLE",
    "MAPS_AND_NAVIGATION",
    "MEDICAL",
    "MUSIC_AND_AUDIO",
    "NEWS_AND_MAGAZINES",
    "PARENTING",
    "PERSONALIZATION",
    "PHOTOGRAPHY",
    "PRODUCTIVITY",
    "SHOPPING",
    "SOCIAL",
    "SPORTS",
    "TOOLS",
    "TRAVEL_AND_LOCAL",
    "VIDEO_PLAYERS",
    "WEATHER",
]

SLEEP_BETWEEN_APPS_SEC = (0.05, 0.15)
SLEEP_BETWEEN_CATEGORIES_SEC = (0.4, 0.8)

REQUEST_TIMEOUT_SEC = 10

# Hard timeout so gp_app() can't hang forever
APP_HARD_TIMEOUT_SEC = 12

# Retries for transient failures
APP_MAX_RETRIES = 2


# --------------------------
# Helpers
# --------------------------
def is_url_reachable(url: str, timeout: int = REQUEST_TIMEOUT_SEC) -> Tuple[str, Optional[int]]:
    if not url or not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return "Not Found", None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
    except requests.RequestException:
        pass

    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers, stream=True)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
        return "Not Reachable", code
    except requests.RequestException:
        return "Not Reachable", None


def to_jsonable(x: Any) -> Any:
    """Store nested structures as JSON strings so CSV stays valid."""
    if x is None or isinstance(x, (str, int, float, bool)):
        return x
    try:
        return json.dumps(x, ensure_ascii=False)
    except Exception:
        return str(x)


def normalize_record(prefix: str, d: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    if not isinstance(d, dict):
        return out
    for k, v in d.items():
        out[f"{prefix}{k}"] = to_jsonable(v)
    return out


def gp_app_with_hard_timeout(app_id: str, lang: str, country: str, hard_timeout_sec: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    Runs google_play_scraper.app() in a daemon thread with a hard timeout.
    Returns (detail_dict, error_string).
    """
    holder = {"detail": None, "error": None}

    def _worker():
        try:
            holder["detail"] = gp_app(app_id, lang=lang, country=country)
        except Exception as e:
            holder["error"] = str(e)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=hard_timeout_sec)

    if t.is_alive():
        return None, f"Timeout after {hard_timeout_sec}s"
    if holder["error"]:
        return None, holder["error"]
    return holder["detail"], None


def get_category_enum(name: str):
    """
    Convert string like 'TOOLS' into google_play_scraper.category.TOOLS.
    If not present, returns None.
    """
    return getattr(category, name, None)


# --------------------------
# Main
# --------------------------
def main():
    run_date_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    rows = []
    seen_global = set()

    total_target = TOP_PER_CATEGORY * len(TARGET_CATEGORY_NAMES)

    with tqdm(total=total_target, desc="Overall", unit="app") as overall_pbar:
        for cat_name in TARGET_CATEGORY_NAMES:
            cat_enum = get_category_enum(cat_name)
            if cat_enum is None:
                print(f"[!] Skipping unknown category enum: {cat_name}")
                overall_pbar.total -= TOP_PER_CATEGORY
                overall_pbar.refresh()
                continue

            # Fetch app list for this category
            try:
                listed = gp_list(
                    collection=TARGET_COLLECTION,
                    category=cat_enum,
                    num=TOP_PER_CATEGORY,
                    country=COUNTRY,
                    lang=LANG,
                    fullDetail=False,   # keep fast; we call app() ourselves
                )
            except Exception as e:
                print(f"[!] list() failed for category='{cat_name}': {e}")
                overall_pbar.total -= TOP_PER_CATEGORY
                overall_pbar.refresh()
                time.sleep(random.uniform(*SLEEP_BETWEEN_CATEGORIES_SEC))
                continue

            with tqdm(total=TOP_PER_CATEGORY, desc=f"{cat_name}", unit="app", leave=True) as cat_pbar:
                cat_count = 0

                for rank_in_category, item in enumerate(listed, start=1):
                    if cat_count >= TOP_PER_CATEGORY:
                        break

                    app_id = item.get("appId") if isinstance(item, dict) else None
                    if not app_id or app_id in seen_global:
                        continue

                    # Robust app() with retries + hard timeout
                    detail = None
                    last_err = None
                    for _ in range(APP_MAX_RETRIES + 1):
                        detail, last_err = gp_app_with_hard_timeout(app_id, LANG, COUNTRY, APP_HARD_TIMEOUT_SEC)
                        if detail is not None:
                            break
                        time.sleep(0.2)

                    if detail is None:
                        # Record minimal row so you can see failures in CSV
                        row = {
                            "category_name": cat_name,
                            "collection": str(TARGET_COLLECTION),
                            "category_rank": rank_in_category,
                            "country": COUNTRY.upper(),
                            "run_date_utc": run_date_utc,
                            "appId": app_id,
                            "app_fetch_error": last_err,
                        }
                        row.update(normalize_record("list_", item if isinstance(item, dict) else {}))
                        rows.append(row)
                        # Do NOT mark as seen, so it could be retried in another run if needed
                        cat_pbar.update(1)
                        overall_pbar.update(1)
                        continue

                    # Accepted
                    seen_global.add(app_id)
                    cat_count += 1

                    policy_url = detail.get("privacyPolicy")
                    policy_status, policy_http = is_url_reachable(policy_url)

                    row = {
                        "category_name": cat_name,
                        "collection": str(TARGET_COLLECTION),
                        "category_rank": rank_in_category,
                        "country": COUNTRY.upper(),
                        "run_date_utc": run_date_utc,
                        "privacy_policy_url": policy_url if policy_url else None,
                        "privacy_policy_status": policy_status,
                        "privacy_policy_http_code": policy_http,
                        "app_fetch_error": None,
                    }

                    row.update(normalize_record("list_", item))
                    row.update(normalize_record("app_", detail))
                    rows.append(row)

                    cat_pbar.update(1)
                    overall_pbar.update(1)
                    time.sleep(random.uniform(*SLEEP_BETWEEN_APPS_SEC))

                # If we got fewer than requested, reduce the overall bar total accordingly
                if cat_count < TOP_PER_CATEGORY:
                    missing = TOP_PER_CATEGORY - cat_count
                    overall_pbar.total -= missing
                    overall_pbar.refresh()

            time.sleep(random.uniform(*SLEEP_BETWEEN_CATEGORIES_SEC))

    df = pd.DataFrame(rows)
    df.insert(0, "rank", range(1, len(df) + 1))

    out_filename = f"apps_{COUNTRY}_{str(TARGET_COLLECTION).split('.')[-1]}_top{TOP_PER_CATEGORY}_by_category_allfields_{len(df)}_{run_date_utc}.csv"
    out_path = os.path.join(OUTPUT_FOLDER, out_filename)
    df.to_csv(out_path, index=False, encoding="utf-8")

    print(f"\n[✓] Saved {len(df)} rows to: {out_path}")
    preview_cols = [c for c in [
        "rank", "category_name", "category_rank", "appId",
        "app_title", "app_developer", "privacy_policy_status", "privacy_policy_http_code",
        "app_fetch_error"
    ] if c in df.columns]
    print(tabulate(df[preview_cols].head(10), headers="keys", tablefmt="grid", showindex=False))


if __name__ == "__main__":
    main()