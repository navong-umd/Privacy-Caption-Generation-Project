import os
import pandas as pd
from datetime import datetime
from tabulate import tabulate
from gplay_scraper import GPlayScraper

# ---------- Config ----------
OUTPUT_FOLDER = r"C:\Users\2015n\OneDrive\Desktop\Privacy Policy Generation Project\Static Code Analysis Module\output"
COUNTRY = "kh"   # Cambodia
LANG = "en"
N = 500

scraper = GPlayScraper()

# ---------- Fetch Top Free Apps ----------
apps_list = scraper.list_analyze(
    collection="TOP_FREE",
    category="APPLICATION",
    count=N,
    lang=LANG,
    country=COUNTRY
)

# ---------- Add rank + metadata ----------
run_date_utc = datetime.utcnow().strftime("%Y-%m-%d")

for rank, item in enumerate(apps_list, start=1):
    item["rank"] = rank
    item["country"] = COUNTRY.upper()
    item["run_date_utc"] = run_date_utc

df = pd.DataFrame(apps_list)

# ---------- Select columns ----------
keep_cols = [
    "rank", "appId", "title", "developer",
    "score", "ratings", "reviews", "installs",
    "genre", "free", "price", "currency",
    "url", "country", "run_date_utc"
]
df_out = df[[c for c in keep_cols if c in df.columns]].copy()
df_out = df_out.sort_values("rank")

# ---------- Save CSV ----------
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
out_filename = f"top_free_{COUNTRY}_{N}_{run_date_utc}.csv"
output_path = os.path.join(OUTPUT_FOLDER, out_filename)
df_out.to_csv(output_path, index=False, encoding="utf-8")

print(f"[✓] Saved {len(df_out)} apps to: {output_path}")
print("requested:", N, "received:", len(apps_list))
print("\nPreview (first 10 rows):")
print(df_out.head(10))
print("\nTable preview (first 25 rows):")
print(tabulate(df_out.head(25), headers="keys", tablefmt="grid", showindex=False))
