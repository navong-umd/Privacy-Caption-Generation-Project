import os
import time
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from gplay_scraper import GPlayScraper

# ---------- Config ----------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"
COUNTRY = "kh"
LANG = "en"
TARGET_UNIQUE = 1000

# Pull up to 200 per category (since you're seeing a hard stop at ~200 anyway)
PER_CATEGORY = 200

# Categories (from gplay-scraper docs)
CATEGORIES = [
    "APPLICATION",
    "TOOLS", "PRODUCTIVITY", "COMMUNICATION", "SOCIAL", "VIDEO_PLAYERS",
    "MUSIC_AND_AUDIO", "ENTERTAINMENT", "PHOTOGRAPHY", "FINANCE",
    "SHOPPING", "BUSINESS", "EDUCATION", "HEALTH_AND_FITNESS",
    "NEWS_AND_MAGAZINES", "MAPS_AND_NAVIGATION", "TRAVEL_AND_LOCAL",
    "FOOD_AND_DRINK", "LIFESTYLE", "HOUSE_AND_HOME", "PERSONALIZATION",
    "BOOKS_AND_REFERENCE", "WEATHER", "SPORTS", "DATING",
    "FAMILY", "PARENTING", "EVENTS", "AUTO_AND_VEHICLES", "MEDICAL",
    # Games (optional but helps reach 500 fast)
    "GAME", "GAME_CASUAL", "GAME_PUZZLE", "GAME_ACTION", "GAME_ARCADE",
]

scraper = GPlayScraper()
run_date_utc = datetime.utcnow().strftime("%Y-%m-%d")

seen = set()
rows = []

for cat in CATEGORIES:
    apps = scraper.list_analyze(
        collection="TOP_FREE",
        category=cat,
        count=PER_CATEGORY,
        lang=LANG,
        country=COUNTRY
    )

    for rank_in_cat, item in enumerate(apps, start=1):
        app_id = item.get("appId")
        if not app_id or app_id in seen:
            continue

        seen.add(app_id)

        item["rank_in_category"] = rank_in_cat
        item["source_category"] = cat
        item["country"] = COUNTRY.upper()
        item["run_date_utc"] = run_date_utc

        rows.append(item)

        if len(seen) >= TARGET_UNIQUE:
            break

    if len(seen) >= TARGET_UNIQUE:
        break

    # small pause to be polite to the endpoint
    time.sleep(0.5)

df = pd.DataFrame(rows)

# Create a stable global rank = order of collection (not a true Play “overall” rank)
df.insert(0, "rank", range(1, len(df) + 1))

keep_cols = [
    "rank", "rank_in_category", "source_category",
    "appId", "title", "developer",
    "score", "ratings", "reviews", "installs",
    "genre", "free", "price", "currency",
    "url", "country", "run_date_utc"
]
df_out = df[[c for c in keep_cols if c in df.columns]].copy()

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
out_filename = f"top_free_{COUNTRY}_merged_{len(df_out)}_{run_date_utc}.csv"
output_path = os.path.join(OUTPUT_FOLDER, out_filename)
df_out.to_csv(output_path, index=False, encoding="utf-8")

print(f"[✓] Saved {len(df_out)} unique apps to: {output_path}")
print(tabulate(df_out.head(10), headers="keys", tablefmt="grid", showindex=False))
