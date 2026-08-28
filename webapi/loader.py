"""Cached, read-only loaders over the pipeline artifacts.

Everything is loaded lazily and memoized. The only expensive item is the PRCS
index, which is derived once from the 10,721 per-PRCS files and cached to disk
so later starts are instant. Nothing here writes into the pipeline outputs.
"""
from __future__ import annotations

import csv
import functools
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from webapi.config import APP_DISPLAY_NAMES, CACHE_DIR, DATA_ROOT, RESEARCH_DOCS_DIR
from webapi.sanitize import fix_deep, fix_text

PRACTICE_LABELS = ["Processing", "Collecting", "Sharing", "Other"]
PURPOSE_LABELS = ["Functionality", "Advertisement", "Analytics", "Other"]


def _read_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Small artifacts (loaded whole, memoized)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def policy() -> Dict[str, Any]:
    p = DATA_ROOT / "policy" / "policy.json"
    return fix_deep(_read_json(p)) if p.exists() else {"apps": {}}


@functools.lru_cache(maxsize=1)
def eval_report() -> Dict[str, Any]:
    p = DATA_ROOT / "eval" / "eval_report.json"
    return fix_deep(_read_json(p)) if p.exists() else {}


@functools.lru_cache(maxsize=1)
def caption_eval() -> Dict[str, Any]:
    p = DATA_ROOT / "caption_eval" / "caption_eval.json"
    return fix_deep(_read_json(p)) if p.exists() else {}


@functools.lru_cache(maxsize=1)
def model_metrics() -> Dict[str, str]:
    """convgnn/metrics.csv -> {metric: value} (values kept as strings + parsed floats)."""
    p = DATA_ROOT / "convgnn" / "metrics.csv"
    out: Dict[str, str] = {}
    if not p.exists():
        return out
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out[row["metric"]] = fix_text(row["value"])
    return out


@functools.lru_cache(maxsize=1)
def splits() -> Dict[str, str]:
    """prcs_id -> split name."""
    p = DATA_ROOT / "dataset" / "splits.json"
    out: Dict[str, str] = {}
    if not p.exists():
        return out
    data = _read_json(p)
    for split_name, ids in data.items():
        for pid in ids:
            out[pid] = split_name
    return out


@functools.lru_cache(maxsize=1)
def labels() -> Dict[str, Dict[str, Any]]:
    """prcs_id -> {app_package, label_source, practice[], purpose[]}."""
    p = DATA_ROOT / "dataset" / "labels.csv"
    out: Dict[str, Dict[str, Any]] = {}
    if not p.exists():
        return out
    with open(p, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            practice = [l for l in PRACTICE_LABELS if row.get(f"practice_{l}") == "1"]
            purpose = [l for l in PURPOSE_LABELS if row.get(f"purpose_{l}") == "1"]
            out[row["prcs_id"]] = {
                "app_package": row.get("app_package", ""),
                "label_source": row.get("label_source", ""),
                "practice": practice,
                "purpose": purpose,
            }
    return out


def _captions_map(filename: str) -> Dict[str, Dict[str, Any]]:
    p = DATA_ROOT / filename
    out: Dict[str, Dict[str, Any]] = {}
    if not p.exists():
        return out
    for entry in _read_json(p):
        out[entry["prcs_id"]] = fix_deep(entry)
    return out


@functools.lru_cache(maxsize=1)
def captions_mock() -> Dict[str, Dict[str, Any]]:
    return _captions_map("captions/captions.json")


@functools.lru_cache(maxsize=1)
def captions_llm() -> Dict[str, Dict[str, Any]]:
    return _captions_map("captions_llm/captions.json")


# ---------------------------------------------------------------------------
# PRCS index (derived once from the 10,721 per-PRCS files, cached to disk)
# ---------------------------------------------------------------------------

_INDEX_FIELDS = (
    "prcs_id", "app_package", "class_name", "method_name",
    "source_api", "sink_api", "sink_type", "sink_label",
    "pi_type", "pi_category", "permission", "privacy_threat", "hop_count",
)


def _build_prcs_index() -> List[Dict[str, Any]]:
    prcs_dir = DATA_ROOT / "prcs_all"
    lab = labels()
    spl = splits()
    rows: List[Dict[str, Any]] = []
    if not prcs_dir.exists():
        return rows
    for name in sorted(name for name in _listdir(prcs_dir) if name.endswith(".json")):
        try:
            rec = _read_json(prcs_dir / name)
        except (OSError, json.JSONDecodeError):
            continue
        pid = rec.get("prcs_id", name[:-5])
        sub = rec.get("subgraph", {})
        row: Dict[str, Any] = {k: rec.get(k, "") for k in _INDEX_FIELDS}
        row["prcs_id"] = pid
        row["n_nodes"] = len(sub.get("nodes", []))
        row["n_edges"] = len(sub.get("edges", []))
        meta = lab.get(pid, {})
        row["label_source"] = meta.get("label_source", "")
        row["practice"] = meta.get("practice", [])
        row["purpose"] = meta.get("purpose", [])
        row["split"] = spl.get(pid, "")
        rows.append(fix_deep(row))
    return rows


def _listdir(path: Path) -> List[str]:
    import os
    return os.listdir(path)


def build_and_cache_index() -> Path:
    """Force a rebuild of the PRCS index cache. Returns the cache file path."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    rows = _build_prcs_index()
    out = CACHE_DIR / "prcs_index.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f)
    return out


@functools.lru_cache(maxsize=1)
def prcs_index() -> List[Dict[str, Any]]:
    """The light PRCS index (one small record per PRCS). Built + cached on first use."""
    cache = CACHE_DIR / "prcs_index.json"
    if cache.exists():
        try:
            return _read_json(cache)
        except (OSError, json.JSONDecodeError):
            pass
    rows = _build_prcs_index()
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        with open(cache, "w", encoding="utf-8") as f:
            json.dump(rows, f)
    except OSError:
        pass
    return rows


@functools.lru_cache(maxsize=1)
def prcs_index_by_id() -> Dict[str, Dict[str, Any]]:
    return {r["prcs_id"]: r for r in prcs_index()}


def prcs_detail(prcs_id: str) -> Optional[Dict[str, Any]]:
    """Read one full PRCS record (code_snippet + subgraph) on demand."""
    if not re.fullmatch(r"prcs_[0-9a-fA-F]+", prcs_id):
        return None
    p = DATA_ROOT / "prcs_all" / f"{prcs_id}.json"
    if not p.exists():
        return None
    try:
        return fix_deep(_read_json(p))
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Apps (aggregated from labels + policy)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def app_packages() -> List[str]:
    pkgs = {r["app_package"] for r in prcs_index() if r.get("app_package")}
    pkgs |= set(policy().get("apps", {}).keys())
    return sorted(pkgs)


def display_name(pkg: str) -> str:
    return APP_DISPLAY_NAMES.get(pkg, pkg)


# ---------------------------------------------------------------------------
# Research docs
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=1)
def research_docs() -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not RESEARCH_DOCS_DIR.exists():
        return out
    for p in sorted(RESEARCH_DOCS_DIR.glob("*.md")):
        title = p.stem.replace("_", " ").title()
        # Prefer the first markdown H1 as the title.
        try:
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except OSError:
            pass
        out.append({"slug": p.stem.lower().replace("_", "-"), "file": p.name, "title": title})
    return out


def research_doc(slug: str) -> Optional[Dict[str, str]]:
    for d in research_docs():
        if d["slug"] == slug:
            p = RESEARCH_DOCS_DIR / d["file"]
            try:
                return {"slug": slug, "title": d["title"], "markdown": p.read_text(encoding="utf-8")}
            except OSError:
                return None
    return None
