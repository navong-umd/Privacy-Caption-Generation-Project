import os
import time
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm

from google_play_scraper import app, search

# ---------- Config ----------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"
COUNTRY = "kh"
LANG = "en"

TOP_PER_GROUP = 100
N_HITS_PER_QUERY = 30

QUERY_GROUPS = {
    "TOOLS": ["tools", "utility", "scanner", "cleaner", "calculator"],
    "PRODUCTIVITY": ["productivity", "notes", "calendar", "task manager", "pdf"],
    "COMMUNICATION": ["messaging", "chat", "voip", "video call"],
    "SOCIAL": ["social", "community", "friends", "dating"],
    "VIDEO_PLAYERS": ["video player", "media player", "streaming"],
    "MUSIC_AND_AUDIO": ["music", "audio", "podcast", "radio"],
    "ENTERTAINMENT": ["entertainment", "movies", "tv"],
    "PHOTOGRAPHY": ["photo editor", "camera", "filters"],
    "FINANCE": ["finance", "bank", "wallet", "payments"],
    "SHOPPING": ["shopping", "ecommerce", "marketplace"],
    "BUSINESS": ["business", "invoicing", "crm"],
    "EDUCATION": ["education", "learn", "courses"],
    "HEALTH_AND_FITNESS": ["fitness", "workout", "health", "step counter"],
    "NEWS_AND_MAGAZINES": ["news", "magazine"],
    "MAPS_AND_NAVIGATION": ["maps", "navigation", "gps"],
    "TRAVEL_AND_LOCAL": ["travel", "hotel", "booking"],
    "FOOD_AND_DRINK": ["food", "delivery", "restaurant"],
    "LIFESTYLE": ["lifestyle", "beauty", "fashion"],
    "HOUSE_AND_HOME": ["home", "smart home", "house"],
    "PERSONALIZATION": ["wallpaper", "launcher", "theme"],
    "BOOKS_AND_REFERENCE": ["books", "dictionary", "reference"],
    "WEATHER": ["weather", "forecast"],
    "SPORTS": ["sports", "score", "live score"],
    "EVENTS": ["events", "ticket"],
    "AUTO_AND_VEHICLES": ["car", "vehicle", "parking"],
    "MEDICAL": ["medical", "telemedicine", "clinic"],
    "GAMES": ["game", "puzzle game", "casual game", "action game"],
}

run_date_utc = datetime.utcnow().strftime("%Y-%m-%d")

seen_global = set()
rows = []

def safe_get(d: dict, key: str, default=None):
    return d.get(key, default) if isinstance(d, dict) else default

# ---------- Main loop ----------
for group_name, queries in QUERY_GROUPS.items():

    group_count = 0

    with tqdm(
        total=TOP_PER_GROUP,
        desc=f"{group_name}",
        unit="app",
        leave=True
    ) as pbar:

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
                pbar.update(1)

                detail["group_rank"] = group_count
                detail["rank_in_query"] = rank_in_query
                detail["source_group"] = group_name
                detail["source_query"] = q
                detail["country"] = COUNTRY.upper()
                detail["run_date_utc"] = run_date_utc

                rows.append(detail)

            time.sleep(0.6)

# ---------- Output ----------
df = pd.DataFrame(rows)
df.insert(0, "rank", range(1, len(df) + 1))

keep_cols = [
    "rank", "group_rank", "rank_in_query",
    "source_group", "source_query",
    "appId", "title", "developer",
    "score", "ratings", "reviews", "installs",
    "genre", "free", "price", "currency",
    "url", "country", "run_date_utc"
]

df_out = df[[c for c in keep_cols if c in df.columns]].copy()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
out_filename = f"apps_{COUNTRY}_top{TOP_PER_GROUP}_per_group_{len(df_out)}_{run_date_utc}.csv"
output_path = os.path.join(OUTPUT_FOLDER, out_filename)

df_out.to_csv(output_path, index=False, encoding="utf-8")

print(f"[✓] Saved {len(df_out)} apps to: {output_path}")
print(tabulate(df_out.head(5), headers="keys", tablefmt="grid", showindex=False))
