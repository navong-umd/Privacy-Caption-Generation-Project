"""
Google Play (Cambodia) top free apps list builder - UPDATED (adds workflow comments)

Input:
- None (queries are defined in QUERY_GROUPS and pulled from Google Play via google-play-scraper)

Output:
- OUTPUT_FOLDER/apps_{COUNTRY}_top{TOP_PER_GROUP}_per_group_with_privacy_{N}_{run_date_utc}.csv

Workflow implemented:
1) For each group (e.g., TOOLS, PRODUCTIVITY, COMMUNICATION), run multiple keyword queries using google-play-scraper search()
2) For each search hit, fetch full app metadata using google-play-scraper app()
3) Deduplicate apps globally so the same appId is not collected twice across groups/queries
4) Extract the privacy policy URL from app metadata and test URL reachability (HEAD first, fallback GET)
5) Add provenance fields (group name, query used, rank within query, rank within group, country, run date)
6) Save the consolidated dataset to CSV and print a small preview

Install:
pip install --upgrade google-play-scraper pandas tabulate tqdm requests

Notes:
- Google Play may throttle or block aggressive scraping. The random sleeps help reduce rate-limits.
- Some servers block HEAD; the script falls back to a lightweight GET for reachability checks.
- If a group has limited search results, the overall progress bar total is adjusted to avoid appearing stuck.
"""

# pip install --upgrade google-play-scraper pandas tabulate tqdm requests

import os
import time
import random
import pandas as pd
import requests

from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm
from google_play_scraper import app, search

# --------------------------
# Config
# --------------------------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"

# Country: Cambodia, Country Code: KH
COUNTRY = "kh"
LANG = "en"

TOP_PER_GROUP = 100
N_HITS_PER_QUERY = 30

# polite pacing to reduce blocking / throttling
SLEEP_BETWEEN_QUERIES_SEC = (0.5, 0.9)     # random range
SLEEP_BETWEEN_APPS_SEC = (0.05, 0.15)      # random range

REQUEST_TIMEOUT_SEC = 10

QUERY_GROUPS = {
    "APPLICATION": ["app", "application", "android app"],
    "ART_AND_DESIGN": ["art", "design", "drawing", "illustration", "graphic"],
    "AUTO_AND_VEHICLES": ["car", "vehicle", "parking", "auto", "driving"],
    "BEAUTY": ["beauty", "makeup", "skincare", "cosmetics"],
    "BOOKS_AND_REFERENCE": ["books", "ebook", "dictionary", "reference"],
    "BUSINESS": ["business", "invoicing", "crm", "accounting"],
    "COMICS": ["comics", "manga", "graphic novel"],
    "COMMUNICATION": ["messaging", "chat", "voip", "video call"],
    "DATING": ["dating", "match", "relationship"],
    "EDUCATION": ["education", "learning", "courses", "study"],
    "ENTERTAINMENT": ["entertainment", "movies", "tv", "shows"],
    "EVENTS": ["events", "ticket", "conference"],
    "FINANCE": ["finance", "bank", "wallet", "payments"],
    "FOOD_AND_DRINK": ["food", "delivery", "restaurant", "recipes"],
    "GAME": ["game", "puzzle game", "casual game", "action game"],
    "HEALTH_AND_FITNESS": ["fitness", "workout", "health", "step counter"],
    "HOUSE_AND_HOME": ["home", "smart home", "house", "interior"],
    "LIBRARIES_AND_DEMO": ["library", "demo", "sample"],
    "LIFESTYLE": ["lifestyle", "fashion", "daily life"],
    "MAPS_AND_NAVIGATION": ["maps", "navigation", "gps"],
    "MEDICAL": ["medical", "telemedicine", "clinic", "doctor"],
    "MUSIC_AND_AUDIO": ["music", "audio", "podcast", "radio"],
    "NEWS_AND_MAGAZINES": ["news", "magazine", "journal"],
    "PARENTING": ["parenting", "kids", "baby", "family"],
    "PERSONALIZATION": ["wallpaper", "launcher", "theme"],
    "PHOTOGRAPHY": ["photo", "camera", "photo editor", "filters"],
    "PRODUCTIVITY": ["productivity", "notes", "calendar", "task manager"],
    "SHOPPING": ["shopping", "ecommerce", "marketplace"],
    "SOCIAL": ["social", "community", "friends", "network"],
    "SPORTS": ["sports", "score", "live score"],
    "TOOLS": ["tools", "utility", "scanner", "cleaner", "calculator"],
    "TRAVEL_AND_LOCAL": ["travel", "hotel", "booking", "local guide"],
    "VIDEO_PLAYERS": ["video player", "media player", "streaming"],
    "WEATHER": ["weather", "forecast", "temperature"]
}

# --------------------------
# Helpers
# --------------------------
def safe_get(d: dict, key: str, default=None):
    return d.get(key, default) if isinstance(d, dict) else default


def is_url_reachable(url: str, timeout: int = REQUEST_TIMEOUT_SEC):
    """
    Returns: (status_string, http_code)
    status_string in {"Reachable", "Not Reachable", "Not Found"}
    """
    if not url or not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return "Not Found", None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    # Try HEAD first
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
    except requests.RequestException:
        pass

    # Fallback to lightweight GET (some servers block HEAD)
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers, stream=True)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
        return "Not Reachable", code
    except requests.RequestException:
        return "Not Reachable", None


# --------------------------
# Main
# --------------------------
def main():
    run_date_utc = datetime.utcnow().strftime("%Y-%m-%d")

    seen_global = set()
    rows = []

    total_target = TOP_PER_GROUP * len(QUERY_GROUPS)

    with tqdm(total=total_target, desc="Overall", unit="app") as overall_pbar:

        for group_name, queries in QUERY_GROUPS.items():
            group_count = 0

            with tqdm(
                total=TOP_PER_GROUP,
                desc=f"{group_name}",
                unit="app",
                leave=True
            ) as group_pbar:

                for q in queries:
                    if group_count >= TOP_PER_GROUP:
                        break

                    try:
                        hits = search(
                            q,
                            lang=LANG,
                            country=COUNTRY,
                            n_hits=N_HITS_PER_QUERY
                        )
                    except Exception as e:
                        print(f"[!] search() failed for query='{q}' ({group_name}): {e}")
                        time.sleep(random.uniform(*SLEEP_BETWEEN_QUERIES_SEC))
                        continue

                    for rank_in_query, hit in enumerate(hits, start=1):
                        if group_count >= TOP_PER_GROUP:
                            break

                        app_id = safe_get(hit, "appId")
                        if not app_id or app_id in seen_global:
                            continue

                        try:
                            detail = app(app_id, lang=LANG, country=COUNTRY)
                        except Exception as e:
                            print(f"[!] app() failed for appId='{app_id}': {e}")
                            continue

                        seen_global.add(app_id)
                        group_count += 1

                        # privacy policy + reachability
                        policy_url = detail.get("privacyPolicy")
                        policy_status, policy_http = is_url_reachable(policy_url)

                        # enrich record
                        detail["rank_in_query"] = rank_in_query
                        detail["source_group"] = group_name
                        detail["source_query"] = q
                        detail["group_rank"] = group_count
                        detail["country"] = COUNTRY.upper()
                        detail["run_date_utc"] = run_date_utc

                        detail["privacy_policy_url"] = policy_url if policy_url else None
                        detail["privacy_policy_status"] = policy_status
                        detail["privacy_policy_http_code"] = policy_http

                        rows.append(detail)

                        group_pbar.update(1)
                        overall_pbar.update(1)

                        time.sleep(random.uniform(*SLEEP_BETWEEN_APPS_SEC))

                    time.sleep(random.uniform(*SLEEP_BETWEEN_QUERIES_SEC))

                # If the group couldn't reach TOP_PER_GROUP (search results too limited),
                # adjust overall bar so "Overall" doesn't look stuck.
                # This just keeps the UI honest.
                if group_count < TOP_PER_GROUP:
                    missing = TOP_PER_GROUP - group_count
                    overall_pbar.total -= missing
                    overall_pbar.refresh()

    # ---------- Output ----------
    df = pd.DataFrame(rows)
    df.insert(0, "rank", range(1, len(df) + 1))

    keep_cols = [
        "rank", "source_group", "group_rank", "source_query", "rank_in_query",
        "appId", "title", "developer",
        "score", "ratings", "reviews", "installs",
        "genre", "free", "price", "currency",
        "url",
        "privacy_policy_url", "privacy_policy_status", "privacy_policy_http_code",
        "country", "run_date_utc"
    ]

    df_out = df[[c for c in keep_cols if c in df.columns]].copy()

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    out_filename = (
        f"apps_{COUNTRY}_top{TOP_PER_GROUP}_per_group_with_privacy_"
        f"{len(df_out)}_{run_date_utc}.csv"
    )
    output_path = os.path.join(OUTPUT_FOLDER, out_filename)

    df_out.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n[✓] Saved {len(df_out)} apps to: {output_path}")
    print(tabulate(df_out.head(10), headers="keys", tablefmt="grid", showindex=False))


if __name__ == "__main__":
    main()
