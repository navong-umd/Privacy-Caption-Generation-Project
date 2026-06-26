"""
Purpose: ADAPTER - download APKs from AndroZoo using an API key (HANDOFF_G4).
Input:   --sha256 "h1,h2" (direct), OR --index latest.csv[.gz] + --packages "pkg1,pkg2".
         Key is read from .env / env var ANDRO_ZOO_KEY (never printed or logged).
Output:  downloaded <sha256>.apk in --out, ready for `python -m pipeline.run_pipeline --apk`.

SECURITY: the API key is loaded from the environment and redacted in every log/URL. The .env
file is gitignored. Network calls go only to androzoo.uni.lu and are the explicit user request.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import os
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pplib.io_utils import ensure_dir, get_logger, load_dotenv, redact

log = get_logger("fetch_androzoo")

API_URL = "https://androzoo.uni.lu/api/download"
DEFAULT_KEY_ENVS = ["ANDRO_ZOO_KEY", "ANDROZOO_API_KEY", "ANDROZOO_KEY"]
_UA = "privacy-caption-research/1.0 (+fetch_androzoo)"


def get_api_key(env_names: Optional[List[str]] = None) -> str:
    """Load the AndroZoo key from .env / environment. Returns the key (never logs it)."""
    load_dotenv()  # populate os.environ from .env if present (values not returned)
    for name in (env_names or DEFAULT_KEY_ENVS):
        val = os.environ.get(name, "").strip()
        if val:
            return val
    raise RuntimeError(
        f"No AndroZoo key found. Set one of {DEFAULT_KEY_ENVS} in .env or the environment.")


def pick_from_rows(rows: Iterable[dict], packages: List[str]) -> Dict[str, dict]:
    """Pure: from AndroZoo index rows, pick the highest-vercode sha256 per package. Offline-testable."""
    want = set(packages)
    best: Dict[str, dict] = {}
    for r in rows:
        pkg = r.get("pkg_name")
        if pkg not in want:
            continue
        try:
            vc = int(r.get("vercode") or 0)
        except ValueError:
            vc = 0
        if pkg not in best or vc > best[pkg]["vercode"]:
            best[pkg] = {"sha256": r.get("sha256"), "vercode": vc,
                         "apk_size": r.get("apk_size"), "markets": r.get("markets")}
    return best


def resolve_from_index(index_path: str, packages: List[str]) -> Dict[str, dict]:
    """Stream the AndroZoo index (csv or csv.gz) and resolve packages -> sha256."""
    p = Path(index_path)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8", newline="") as f:
        return pick_from_rows(csv.DictReader(f), packages)


def download_by_sha256(sha256: str, out_dir: Path, key: str, timeout: int = 120) -> Path:
    """Download one APK by sha256 (skips if present). Key is redacted in all logs."""
    dest = out_dir / f"{sha256}.apk"
    if dest.exists() and dest.stat().st_size > 0:
        log.info("Already have %s.apk", sha256)
        return dest
    url = f"{API_URL}?apikey={key}&sha256={sha256}"
    log.info("Downloading %s", redact(url))
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (explicit user request)
        data = r.read()
    if len(data) < 1000:  # AndroZoo returns a short error body on bad key/hash
        raise RuntimeError(f"download too small ({len(data)} bytes) — check key/sha256")
    dest.write_bytes(data)
    return dest


def fetch_androzoo(out_dir: str, sha256s: Optional[List[str]] = None,
                   index_path: Optional[str] = None, packages: Optional[List[str]] = None,
                   max_n: int = 5) -> Dict[str, str]:
    """Download by sha256 list, or resolve packages via a local index then download."""
    key = get_api_key()
    out = ensure_dir(out_dir)
    targets: List[str] = list(sha256s or [])
    if index_path and packages:
        resolved = resolve_from_index(index_path, packages)
        for pkg, info in resolved.items():
            log.info("%s -> %s (vercode %s)", pkg, info["sha256"], info["vercode"])
            if info["sha256"]:
                targets.append(info["sha256"])

    result: Dict[str, str] = {}
    for sha in targets[:max_n]:
        try:
            result[sha] = str(download_by_sha256(sha, out, key))
        except Exception as e:
            log.warning("Failed %s: %s", sha, redact(str(e)))
            result[sha] = f"ERROR: {redact(str(e))}"
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch APKs from AndroZoo (key from .env).")
    ap.add_argument("--sha256", default=None, help="comma-separated sha256 hashes")
    ap.add_argument("--index", default=None, help="AndroZoo latest.csv[.gz] for package resolution")
    ap.add_argument("--packages", default=None, help="comma-separated package names (needs --index)")
    ap.add_argument("--out", default="data/corpus")
    ap.add_argument("--max", type=int, default=5)
    ap.add_argument("--check", action="store_true", help="verify the key is loaded (prints no secret)")
    args = ap.parse_args()

    if args.check:
        try:
            key = get_api_key()
            print(f"[+] AndroZoo key loaded OK (length {len(key)}, value hidden).")
        except RuntimeError as e:
            print(f"[!] {e}")
        return

    shas = [s.strip() for s in args.sha256.split(",")] if args.sha256 else None
    pkgs = [p.strip() for p in args.packages.split(",")] if args.packages else None
    if not shas and not (args.index and pkgs):
        ap.error("provide --sha256, or --index together with --packages")
    res = fetch_androzoo(args.out, shas, args.index, pkgs, args.max)
    print("\n=== AndroZoo fetch ===")
    for k, v in res.items():
        print(f"  {k[:16]}...: {v}")
    got = [v for v in res.values() if v.endswith(".apk")]
    if got:
        print(f"\n[+] {len(got)} APK(s) in {args.out}. Next:")
        print(f"    python -m pipeline.run_pipeline --apk \"{got[0]}\" --out data/run_corpus --precision")


if __name__ == "__main__":
    main()
