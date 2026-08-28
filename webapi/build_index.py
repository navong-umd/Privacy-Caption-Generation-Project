"""Build (or rebuild) the cached PRCS index.

Reads the 10,721 per-PRCS files once and writes a compact index the API loads
instantly. Safe to re-run; it just overwrites the cache.

Run:  python -m webapi.build_index
"""
from __future__ import annotations

import time

from webapi import loader


def main() -> None:
    start = time.perf_counter()
    path = loader.build_and_cache_index()
    rows = loader.prcs_index.__wrapped__()  # bypass cache to report the fresh count
    elapsed = time.perf_counter() - start
    print(f"Wrote {len(rows)} PRCS index rows to {path} in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
