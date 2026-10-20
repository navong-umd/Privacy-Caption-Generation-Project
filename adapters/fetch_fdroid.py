"""
Purpose: ADAPTER - fetch a small corpus of open-source APKs from F-Droid (no API key needed).
Input:   --packages "pkg1,pkg2" (or --list FILE), --out data/corpus, --max N.
Output:  downloaded .apk files in --out, ready for `python -m pipeline.run_pipeline --apk <file>`.

A no-credential way to start the G4 -> G1 loop while the AndroZoo key is pending (legacy/notes/handoffs/HANDOFF_G4.md).
Uses only the stdlib (urllib). The index-resolution logic is pure/offline-testable; the only
network calls are the explicit index + APK downloads the user asked for.
"""
from __future__ import annotations

import argparse
import io
import json
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

from pplib.io_utils import ensure_dir, get_logger

log = get_logger("fetch_fdroid")

FDROID_REPO = "https://f-droid.org/repo/"
INDEX_JAR = FDROID_REPO + "index-v1.jar"
_UA = "privacy-caption-research/1.0 (+fetch_fdroid)"

# Default starter set: open-source apps with real PII + network behavior, good for privacy analysis.
DEFAULT_PACKAGES = [
    "org.fdroid.fdroid",   # app store client (network)
    "org.connectbot",      # SSH client (network, credentials)
    "com.fsck.k9",         # K-9 Mail (accounts, contacts, network)
]


def _http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 (explicit user request)
        return r.read()


def fetch_index(index_url: str = INDEX_JAR, cache: Optional[Path] = None) -> dict:
    """Download + parse the F-Droid v1 index (a signed JAR holding index-v1.json)."""
    if cache and cache.exists():
        log.info("Using cached index: %s", cache)
        raw = cache.read_bytes()
    else:
        log.info("Downloading F-Droid index: %s", index_url)
        raw = _http_get(index_url)
        if cache:
            ensure_dir(cache.parent)
            cache.write_bytes(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        return json.loads(z.read("index-v1.json"))


def resolve_apk_names(index: dict, packages: List[str]) -> Dict[str, Optional[str]]:
    """Pure: map each package -> its suggested (or newest) apkName, or None if absent. Testable offline."""
    suggested = {a.get("packageName"): a.get("suggestedVersionCode")
                 for a in index.get("apps", [])}
    out: Dict[str, Optional[str]] = {}
    for pkg in packages:
        versions = index.get("packages", {}).get(pkg)
        if not versions:
            out[pkg] = None
            continue
        sv = suggested.get(pkg)
        chosen = next((v for v in versions if str(v.get("versionCode")) == str(sv)), None)
        chosen = chosen or max(versions, key=lambda v: int(v.get("versionCode", 0)))
        out[pkg] = chosen.get("apkName")
    return out


def download_apk(apk_name: str, out_dir: Path, repo_url: str = FDROID_REPO) -> Path:
    """Download one APK by its index apkName (skips if already present)."""
    dest = out_dir / apk_name
    if dest.exists() and dest.stat().st_size > 0:
        log.info("Already have %s", apk_name)
        return dest
    url = repo_url + apk_name
    log.info("Downloading %s", url)
    dest.write_bytes(_http_get(url))
    return dest


def fetch_fdroid(packages: List[str], out_dir: str, max_n: int = 3,
                 index_url: str = INDEX_JAR) -> Dict[str, str]:
    """Resolve + download up to max_n APKs; returns {package: local_path|status}."""
    out = ensure_dir(out_dir)
    index = fetch_index(index_url, cache=out / ".fdroid-index-v1.jar")
    names = resolve_apk_names(index, packages)
    result: Dict[str, str] = {}
    for pkg in packages:
        if len([v for v in result.values() if v.endswith(".apk")]) >= max_n:
            break
        apk = names.get(pkg)
        if not apk:
            log.warning("Not found in F-Droid index: %s", pkg)
            result[pkg] = "NOT_FOUND"
            continue
        try:
            result[pkg] = str(download_apk(apk, out))
        except Exception as e:  # network/HTTP error -> report, keep going
            log.warning("Download failed for %s: %s", pkg, e)
            result[pkg] = f"ERROR: {e}"
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch a small F-Droid APK corpus (no key needed).")
    ap.add_argument("--packages", default=",".join(DEFAULT_PACKAGES),
                    help="comma-separated package names")
    ap.add_argument("--list", default=None, help="file with one package name per line (overrides --packages)")
    ap.add_argument("--out", default="data/corpus")
    ap.add_argument("--max", type=int, default=3)
    args = ap.parse_args()

    if args.list:
        packages = [l.strip() for l in Path(args.list).read_text(encoding="utf-8").splitlines()
                    if l.strip() and not l.startswith("#")]
    else:
        packages = [p.strip() for p in args.packages.split(",") if p.strip()]

    res = fetch_fdroid(packages, args.out, args.max)
    print("\n=== F-Droid fetch ===")
    for pkg, status in res.items():
        print(f"  {pkg}: {status}")
    got = [v for v in res.values() if v.endswith(".apk")]
    print(f"\n[+] {len(got)} APK(s) in {args.out}. Next:")
    if got:
        print(f"    python -m pipeline.run_pipeline --apk \"{got[0]}\" --out data/run_corpus")


if __name__ == "__main__":
    main()
