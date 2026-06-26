"""
Purpose: Small I/O helpers (config, logging, app_id parsing, JSON/CSV) reused everywhere.
Input:   file paths / dicts.
Output:  loaded configs, parsed identifiers, logger instances.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent


def get_logger(name: str) -> logging.Logger:
    """Return a console logger with a consistent format (idempotent)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger


def load_yaml(path: str | Path) -> Dict[str, Any]:
    """Load a YAML config into a dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(path: str | Path) -> Any:
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def dump_json(obj: Any, path: str | Path) -> None:
    """Write an object to JSON, creating parent dirs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def parse_app_id(app_id: str) -> Tuple[str, str]:
    """Split an APG app_id 'pkg@file.apk' into (package, apk_filename)."""
    if "@" in app_id:
        pkg, apk = app_id.split("@", 1)
        return pkg, apk
    return app_id, ""


def method_class(method_id: str) -> str:
    """Class part of a method id 'pkg.Class->name'."""
    return method_id.split("->", 1)[0] if "->" in method_id else method_id


def method_short_name(method_id: str) -> str:
    """Method name part of a method id 'pkg.Class->name'."""
    return method_id.split("->", 1)[1] if "->" in method_id else method_id


def stmt_method_id(stmt_id: str) -> str:
    """Recover the owning method id from a statement id '{method}_stmt_{i}'."""
    return stmt_id.rsplit("_stmt_", 1)[0] if "_stmt_" in stmt_id else stmt_id


def chunked(it: Iterable[Any], size: int) -> Iterable[List[Any]]:
    """Yield lists of at most `size` items."""
    buf: List[Any] = []
    for x in it:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if missing and return it."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_dotenv(path: str | Path = ".env", override: bool = False) -> List[str]:
    """Load KEY=VALUE pairs from a .env into os.environ. Returns the KEY NAMES only.

    Values are never returned or logged (they are secrets). Existing env vars win
    unless override=True.
    """
    p = Path(path)
    if not p.exists():
        return []
    names: List[str] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if override or k not in os.environ:
            os.environ[k] = v
        names.append(k)
    return names


def redact(text: str) -> str:
    """Mask apikey=... query params so secrets never reach logs/output."""
    import re
    return re.sub(r"(apikey=)[^&\s]+", r"\1***", text)
