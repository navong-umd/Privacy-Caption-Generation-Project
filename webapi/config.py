"""Runtime configuration for the research API.

The data root is resolved from the RESEARCH_DATA_DIR environment variable,
falling back to the committed blessed corpus run. Nothing here is a secret;
the API is read-only over local research artifacts.
"""
from __future__ import annotations

import os
from pathlib import Path

# Repo root = parent of this package.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Which pipeline run the API serves. Default: the blessed 7-app / 10,721-PRCS run.
DATA_ROOT = Path(os.environ.get("RESEARCH_DATA_DIR", REPO_ROOT / "data" / "corpus_run"))

# Where the research markdown docs live.
RESEARCH_DOCS_DIR = REPO_ROOT / "research"

# Small on-disk cache for the derived PRCS index (built once from the 10,721
# per-PRCS files, then reused). Lives next to the data so it is regenerable.
CACHE_DIR = DATA_ROOT / "_webapi_cache"

# CORS origins allowed to call the API (the Vite dev server + common local ports).
ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "RESEARCH_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173",
    ).split(",")
    if o.strip()
]

# Human-friendly display names for the 7 real apps in the corpus.
APP_DISPLAY_NAMES = {
    "com.twitter.android": "Twitter / X",
    "com.duolingo": "Duolingo",
    "com.snapchat.android": "Snapchat",
    "com.spotify.music": "Spotify",
    "com.instagram.android": "Instagram",
    "com.zhiliaoapp.musically": "TikTok",
    "com.whatsapp": "WhatsApp",
}
