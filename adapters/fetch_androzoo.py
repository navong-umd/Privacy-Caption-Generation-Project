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
import ssl
import urllib.request
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from pplib.io_utils import ensure_dir, get_logger, load_dotenv, redact

log = get_logger("fetch_androzoo")


def _ssl_ctx() -> ssl.SSLContext:
    """Verified TLS context using the Mozilla certifi CA bundle when available."""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_CTX = _ssl_ctx()

API_URL = "https://androzoo.uni.lu/api/download"
# Candidate locations for the AndroZoo index list (tried in order; key appended if needed).
INDEX_URLS = [
    "https://androzoo.uni.lu/static/lists/latest.csv.gz",
    "https://androzoo.uni.lu/api/get_list?name=latest.csv.gz",
]
DEFAULT_KEY_ENVS = ["ANDRO_ZOO_KEY", "ANDROZOO_API_KEY", "ANDROZOO_KEY"]
_UA = "privacy-caption-research/1.0 (+fetch_androzoo)"


def _with_key(url: str, key: str) -> str:
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}apikey={key}"


def probe_index_url(key: str) -> Optional[str]:
    """Cheaply find a working index URL via a 1 KB range request (no big download)."""
    for base in INDEX_URLS:
        for url in (base, _with_key(base, key)):
            try:
                req = urllib.request.Request(
                    url, headers={"User-Agent": _UA, "Range": "bytes=0-1023"})
                with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:  # noqa: S310
                    chunk = r.read(1024)
                if chunk[:2] == b"\x1f\x8b" or len(chunk) >= 512:  # gzip magic or real data
                    log.info("Index URL OK: %s", redact(url))
                    return url
            except Exception as e:
                log.info("Index URL not usable (%s): %s", redact(url), redact(str(e)))
    return None


def download_index(dest: str, key: str, url: Optional[str] = None) -> Path:
    """Stream the AndroZoo index list to disk (skips if already present and non-empty)."""
    out = Path(dest)
    if out.exists() and out.stat().st_size > 1_000_000:
        log.info("Index already present: %s (%.0f MB)", out, out.stat().st_size / 1e6)
        return out
    url = url or probe_index_url(key)
    if not url:
        raise RuntimeError("Could not locate the AndroZoo index URL; check key / AndroZoo docs.")
    ensure_dir(out.parent)
    log.info("Downloading index -> %s (this is large)", out)
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=600, context=_CTX) as r, open(out, "wb") as f:  # noqa: S310
        total = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    log.info("Index downloaded: %.0f MB", total / 1e6)
    return out


def get_api_key(env_names: Optional[List[str]] = None) -> str:
    """Load the AndroZoo key from .env / environment. Returns the key (never logs it)."""
    load_dotenv()  # populate os.environ from .env if present (values not returned)
    for name in (env_names or DEFAULT_KEY_ENVS):
        val = os.environ.get(name, "").strip()
        if val:
            return val
    raise RuntimeError(
        f"No AndroZoo key found. Set one of {DEFAULT_KEY_ENVS} in .env or the environment.")


def pick_from_rows(rows: Iterable[dict], packages: List[str],
                   max_mb: Optional[float] = None) -> Dict[str, dict]:
    """Pure: pick a sha256 per package. Default = newest (highest vercode).

    With max_mb set, prefer the newest version whose apk_size <= max_mb; if a package has no
    version under the cap, fall back to its smallest available version. Offline-testable.
    """
    want = set(packages)
    cap = max_mb * 1e6 if max_mb else None
    best: Dict[str, dict] = {}
    for r in rows:
        pkg = r.get("pkg_name")
        if pkg not in want:
            continue
        try:
            vc = int(r.get("vercode") or 0)
        except ValueError:
            vc = 0
        try:
            size = int(r.get("apk_size") or 0)
        except ValueError:
            size = 0
        cand = {"sha256": r.get("sha256"), "vercode": vc, "apk_size": size,
                "markets": r.get("markets")}
        cur = best.get(pkg)
        if cap is None:
            if cur is None or vc > cur["vercode"]:
                best[pkg] = cand
            continue
        under = 0 < size <= cap
        cur_under = cur and 0 < cur["apk_size"] <= cap
        if cur is None:
            best[pkg] = cand
        elif under and not cur_under:
            best[pkg] = cand                          # prefer any under-cap version
        elif under and cur_under and vc > cur["vercode"]:
            best[pkg] = cand                          # newest among under-cap
        elif not under and not cur_under and 0 < size < cur["apk_size"]:
            best[pkg] = cand                          # no under-cap yet -> keep smallest
    return best


def resolve_from_index(index_path: str, packages: List[str],
                       max_mb: Optional[float] = None) -> Dict[str, dict]:
    """Stream the AndroZoo index (csv or csv.gz) and resolve packages -> sha256."""
    p = Path(index_path)
    opener = gzip.open if p.suffix == ".gz" else open
    with opener(p, "rt", encoding="utf-8", newline="") as f:
        return pick_from_rows(csv.DictReader(f), packages, max_mb=max_mb)


def download_by_sha256(sha256: str, out_dir: Path, key: str, timeout: int = 120) -> Path:
    """Download one APK by sha256 (skips if present). Key is redacted in all logs."""
    dest = out_dir / f"{sha256}.apk"
    if dest.exists() and dest.stat().st_size > 0:
        log.info("Already have %s.apk", sha256)
        return dest
    url = f"{API_URL}?apikey={key}&sha256={sha256}"
    log.info("Downloading %s", redact(url))
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:  # noqa: S310 (explicit user request)
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
    ap.add_argument("--probe-index", action="store_true", help="find the index URL cheaply (no big download)")
    ap.add_argument("--download-index", default=None, help="download the AndroZoo index to this path")
    args = ap.parse_args()

    if args.check:
        try:
            key = get_api_key()
            print(f"[+] AndroZoo key loaded OK (length {len(key)}, value hidden).")
        except RuntimeError as e:
            print(f"[!] {e}")
        return

    if args.probe_index:
        url = probe_index_url(get_api_key())
        print(f"[+] usable index URL: {redact(url)}" if url else "[!] no usable index URL found")
        return

    if args.download_index:
        path = download_index(args.download_index, get_api_key())
        print(f"[+] index at {path}. Next: --index {path} --packages \"pkg1,pkg2\"")
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
