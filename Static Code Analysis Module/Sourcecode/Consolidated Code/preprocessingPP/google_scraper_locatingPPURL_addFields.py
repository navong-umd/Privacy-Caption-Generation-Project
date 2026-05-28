"""
Google Play (Cambodia) top free apps list builder - UPDATED (developer fields + safe WHOIS)

Input:
- None (queries are defined in QUERY_GROUPS and pulled from Google Play via google-play-scraper)

Output:
- OUTPUT_FOLDER/apps_{COUNTRY}_top{TOP_PER_GROUP}_per_group_with_privacy_{N}_{run_date_utc}.csv

Workflow implemented:
1) For each group, run multiple keyword queries using google-play-scraper search()
2) For each hit, fetch full app metadata using google-play-scraper app()
3) Deduplicate apps globally across groups and queries
4) Extract privacy policy URL and test URL reachability (HEAD then GET fallback)
5) Add developer contact fields from Play metadata (address, email, website)
6) Optional WHOIS enrichment (safe):
   - OFF by default
   - Only runs if developer_address is missing
   - Only one lookup per unique domain (cached)
   - Hard timeout so WHOIS cannot hang your run
7) Save CSV and print preview

Install:
pip install --upgrade google-play-scraper pandas tabulate tqdm requests
Optional WHOIS:
pip install python-whois

Notes:
- WHOIS is often privacy-protected and slow. Keep it OFF for bulk dataset creation.
- If enabled, WHOIS may still fail for some domains. Failures are recorded in whois_error.
"""

import os
import time
import random
import threading
from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
import requests
from tabulate import tabulate
from tqdm import tqdm
from google_play_scraper import app, search

# --------------------------
# Config
# --------------------------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"

COUNTRY = "kh"
LANG = "en"

TOP_PER_GROUP = 100
N_HITS_PER_QUERY = 30

SLEEP_BETWEEN_QUERIES_SEC = (0.5, 0.9)
SLEEP_BETWEEN_APPS_SEC = (0.05, 0.15)

REQUEST_TIMEOUT_SEC = 10

# WHOIS is OFF by default because it is slow and unreliable at scale.
ENABLE_WHOIS = False

# Only do WHOIS when developer address is missing (recommended).
WHOIS_ONLY_IF_NO_DEV_ADDRESS = True

# Prefer WHOIS based on developer website domain. If missing, fall back to privacy policy URL.
WHOIS_SOURCE_PRIORITY = "developerWebsite"  # "developerWebsite" or "privacyPolicy"

# Hard timeout to prevent WHOIS from hanging your run (Windows-safe).
WHOIS_HARD_TIMEOUT_SEC = 4

# Extra pacing for WHOIS calls
WHOIS_SLEEP_SEC = (0.2, 0.5)

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
    "WEATHER": ["weather", "forecast", "temperature"],
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
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    # Try HEAD first
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True, headers=headers)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
    except requests.RequestException:
        pass

    # Fallback to lightweight GET
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, headers=headers, stream=True)
        code = r.status_code
        if 200 <= code < 400:
            return "Reachable", code
        return "Not Reachable", code
    except requests.RequestException:
        return "Not Reachable", None


def extract_domain(url: str):
    if not url or not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return None
    try:
        host = urlparse(url).hostname
        return host.lower() if host else None
    except Exception:
        return None


def _normalize_to_str(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple, set)):
        items = [str(x) for x in value if x is not None]
        return "; ".join(items) if items else None
    return str(value)


def whois_lookup_domain_safe(domain: str, cache: dict, hard_timeout_sec: int = WHOIS_HARD_TIMEOUT_SEC):
    """
    Windows-safe WHOIS lookup with:
    - caching
    - hard timeout using a thread (so it cannot hang the main run)
    Returns a dict of flattened WHOIS fields.
    """
    if not domain:
        return {}

    if domain in cache:
        return cache[domain]

    out = {
        "whois_domain": domain,
        "whois_registrar": None,
        "whois_org": None,
        "whois_name": None,
        "whois_country": None,
        "whois_state": None,
        "whois_city": None,
        "whois_address": None,
        "whois_emails": None,
        "whois_creation_date": None,
        "whois_updated_date": None,
        "whois_expiration_date": None,
        "whois_status": None,
        "whois_name_servers": None,
        "whois_error": None,
    }

    result_holder = {"data": None, "error": None}

    def _worker():
        try:
            import whois  # python-whois
            w = whois.whois(domain)

            result_holder["data"] = {
                "whois_domain": domain,
                "whois_registrar": _normalize_to_str(getattr(w, "registrar", None)),
                "whois_org": _normalize_to_str(getattr(w, "org", None) or getattr(w, "organization", None)),
                "whois_name": _normalize_to_str(getattr(w, "name", None)),
                "whois_country": _normalize_to_str(getattr(w, "country", None)),
                "whois_state": _normalize_to_str(getattr(w, "state", None)),
                "whois_city": _normalize_to_str(getattr(w, "city", None)),
                "whois_address": _normalize_to_str(getattr(w, "address", None)),
                "whois_emails": _normalize_to_str(getattr(w, "emails", None)),
                "whois_creation_date": _normalize_to_str(getattr(w, "creation_date", None)),
                "whois_updated_date": _normalize_to_str(getattr(w, "updated_date", None)),
                "whois_expiration_date": _normalize_to_str(getattr(w, "expiration_date", None)),
                "whois_status": _normalize_to_str(getattr(w, "status", None)),
                "whois_name_servers": _normalize_to_str(getattr(w, "name_servers", None)),
                "whois_error": None,
            }
        except Exception as e:
            result_holder["error"] = str(e)

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=hard_timeout_sec)

    if t.is_alive():
        out["whois_error"] = f"Timeout after {hard_timeout_sec}s"
        cache[domain] = out
        return out

    if result_holder["error"]:
        out["whois_error"] = result_holder["error"]
        cache[domain] = out
        return out

    data = result_holder["data"] or {}
    out.update(data)

    cache[domain] = out
    return out


# --------------------------
# Main
# --------------------------
def main():
    run_date_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    seen_global = set()
    rows = []
    whois_cache = {}

    total_target = TOP_PER_GROUP * len(QUERY_GROUPS)

    with tqdm(total=total_target, desc="Overall", unit="app") as overall_pbar:
        for group_name, queries in QUERY_GROUPS.items():
            group_count = 0

            with tqdm(total=TOP_PER_GROUP, desc=f"{group_name}", unit="app", leave=True) as group_pbar:
                for q in queries:
                    if group_count >= TOP_PER_GROUP:
                        break

                    try:
                        hits = search(q, lang=LANG, country=COUNTRY, n_hits=N_HITS_PER_QUERY)
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

                        # developer fields from Play metadata
                        dev_email = detail.get("developerEmail")
                        dev_website = detail.get("developerWebsite")
                        dev_address = detail.get("developerAddress")

                        # optional WHOIS enrichment (safe)
                        whois_fields = {}
                        if ENABLE_WHOIS:
                            if WHOIS_ONLY_IF_NO_DEV_ADDRESS and dev_address:
                                whois_fields = {}
                            else:
                                if WHOIS_SOURCE_PRIORITY == "developerWebsite":
                                    seed_url = dev_website or policy_url
                                else:
                                    seed_url = policy_url or dev_website

                                domain = extract_domain(seed_url)
                                # Key optimization: only lookup a domain once
                                if domain:
                                    whois_fields = whois_lookup_domain_safe(domain, whois_cache)
                                    time.sleep(random.uniform(*WHOIS_SLEEP_SEC))

                        # provenance fields
                        detail["rank_in_query"] = rank_in_query
                        detail["source_group"] = group_name
                        detail["source_query"] = q
                        detail["group_rank"] = group_count
                        detail["country"] = COUNTRY.upper()
                        detail["run_date_utc"] = run_date_utc

                        # normalized policy fields
                        detail["privacy_policy_url"] = policy_url if policy_url else None
                        detail["privacy_policy_status"] = policy_status
                        detail["privacy_policy_http_code"] = policy_http

                        # normalized developer fields
                        detail["developer_email"] = dev_email
                        detail["developer_website"] = dev_website
                        detail["developer_address"] = dev_address

                        # attach whois fields (if any)
                        for k, v in whois_fields.items():
                            detail[k] = v

                        rows.append(detail)

                        group_pbar.update(1)
                        overall_pbar.update(1)

                        time.sleep(random.uniform(*SLEEP_BETWEEN_APPS_SEC))

                    time.sleep(random.uniform(*SLEEP_BETWEEN_QUERIES_SEC))

                # adjust overall if group does not reach TOP_PER_GROUP
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
        "developer_email", "developer_website", "developer_address",
        "score", "ratings", "reviews", "installs",
        "genre", "free", "price", "currency",
        "url",
        "privacy_policy_url", "privacy_policy_status", "privacy_policy_http_code",
        # WHOIS fields are included if ENABLE_WHOIS=True and lookup succeeded/failed
        "whois_domain", "whois_registrar", "whois_org", "whois_name",
        "whois_country", "whois_state", "whois_city", "whois_address",
        "whois_emails", "whois_creation_date", "whois_updated_date", "whois_expiration_date",
        "whois_status", "whois_name_servers", "whois_error",
        "country", "run_date_utc",
    ]

    df_out = df[[c for c in keep_cols if c in df.columns]].copy()

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    out_filename = f"apps_{COUNTRY}_top{TOP_PER_GROUP}_per_group_with_privacy_{len(df_out)}_{run_date_utc}.csv"
    output_path = os.path.join(OUTPUT_FOLDER, out_filename)

    df_out.to_csv(output_path, index=False, encoding="utf-8")

    print(f"\n[✓] Saved {len(df_out)} apps to: {output_path}")
    print(tabulate(df_out.head(10), headers="keys", tablefmt="grid", showindex=False))


if __name__ == "__main__":
    main()
