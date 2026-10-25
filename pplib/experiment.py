"""
Purpose: ExperimentRun schema + save / load helpers (Phase 19).
Input:   run metadata (name, config, seed, metrics, artifacts).
Output:  one JSON per run under experiments/<exp_id>/manifest.json plus a top-level
         experiments/index.jsonl every consumer can grep.

Every experiment reruns from its manifest alone: dataset digest, code version, config
digest, seed. Anything not on the manifest is untracked and cannot be reproduced.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

EXPERIMENT_SCHEMA_VERSION = "1.1.0"
MANIFEST_FILENAME = "manifest.json"
INDEX_FILENAME = "index.jsonl"

# Anything else is a warning at best.
_REQUIRED = ("exp_id", "name", "code_version", "config_digest",
             "dataset_digest", "seed", "metrics", "artifacts", "schema_version")

_EXP_ID_RE = re.compile(r"^EXP\d{3,}$")


@dataclass
class ExperimentRun:
    """One reproducible run manifest.

    exp_id:         'EXP001' style stable id. Must match ^EXP\\d{3,}$.
    name:           short human name (e.g. 'rgcn full ppg baseline').
    code_version:   git sha + branch of the code that produced the run.
    config_digest:  sha1 hash of every YAML config the run touched.
    dataset_digest: sha1 hash of the ADPPG dataset used.
    seed:           random seed.
    model_version:  optional model or provider tag (e.g. 'rgcn v0.4', 'anthropic claude-3.5-sonnet').
    metrics:        arbitrary dict of scalar metrics (e.g. {'practice_macro_f1': 0.71}).
    artifacts:      list of file paths produced (relative to the run directory).
    notes:          free-form annotator note.
    banner:         schema banner when the test labels are not all human ('' otherwise).
    test_set_digest: pplib.testset.digest_test_set of the split the run was scored on.
    seeds:          every seed the run aggregates (empty for single-run arms).
    """

    exp_id: str
    name: str
    code_version: str
    config_digest: str
    dataset_digest: str
    seed: int
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    model_version: str = ""
    notes: str = ""
    banner: str = ""
    test_set_digest: str = ""
    seeds: List[int] = field(default_factory=list)
    schema_version: str = EXPERIMENT_SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_experiment(record: Dict[str, Any]) -> None:
    """Raise ValueError if the record is not well-formed."""
    if not isinstance(record, dict):
        raise ValueError(f"experiment record must be a dict, got {type(record).__name__}")
    missing = [f for f in _REQUIRED if f not in record]
    if missing:
        raise ValueError(f"experiment record missing fields: {missing}")
    if not _EXP_ID_RE.match(str(record["exp_id"])):
        raise ValueError(f"exp_id {record['exp_id']!r} must match ^EXP\\d{{3,}}$")
    if not isinstance(record["metrics"], dict):
        raise ValueError("metrics must be a dict")
    if not isinstance(record["artifacts"], list):
        raise ValueError("artifacts must be a list of file paths")


def digest_configs(paths: List[str | Path]) -> str:
    """Deterministic sha1 over the concatenated bytes of every listed config."""
    h = hashlib.sha1()
    for p in sorted(str(x) for x in paths):
        try:
            with open(p, "rb") as f:
                h.update(f"{p}\n".encode("utf-8"))
                h.update(f.read())
        except FileNotFoundError:
            h.update(f"MISSING {p}\n".encode("utf-8"))
    return h.hexdigest()


def digest_dataset(dataset_dir: str | Path) -> str:
    """sha1 of adppg.jsonl + splits.json (the two files that define the dataset)."""
    p = Path(dataset_dir)
    h = hashlib.sha1()
    for name in ("adppg.jsonl", "splits.json"):
        f = p / name
        h.update(f"{name}\n".encode("utf-8"))
        if f.exists():
            h.update(f.read_bytes())
        else:
            h.update(b"MISSING\n")
    return h.hexdigest()


def current_code_version(repo_root: Optional[str | Path] = None) -> str:
    """Return 'branch@shortsha' from git, or 'unknown' if git is unavailable."""
    try:
        args = ["git", "-C", str(repo_root) if repo_root else ".", "rev-parse", "--short", "HEAD"]
        sha = subprocess.check_output(args, stderr=subprocess.DEVNULL).decode("utf-8").strip()
        branch = subprocess.check_output(
            ["git", "-C", str(repo_root) if repo_root else ".", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode("utf-8").strip()
        return f"{branch}@{sha}"
    except Exception:
        return "unknown"


def save_experiment(run: ExperimentRun, experiments_root: str | Path) -> Path:
    """Write experiments/<exp_id>/manifest.json AND append a line to experiments/index.jsonl.

    Returns the manifest path.
    """
    validate_experiment(run.to_dict())
    root = Path(experiments_root)
    exp_dir = root / run.exp_id
    exp_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = exp_dir / MANIFEST_FILENAME
    manifest_path.write_text(json.dumps(run.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    # Append to the flat index. Idempotent: rewrite the file with any duplicate exp_id
    # replaced so a rerun of the same id refreshes rather than duplicating.
    index_path = root / INDEX_FILENAME
    entries: List[Dict[str, Any]] = []
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    entries = [e for e in entries if e.get("exp_id") != run.exp_id]
    entries.append(run.to_dict())
    with open(index_path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, sort_keys=True) + "\n")

    return manifest_path


def load_experiment(experiments_root: str | Path, exp_id: str) -> Dict[str, Any]:
    """Load the manifest for `exp_id`. Raises FileNotFoundError if absent."""
    path = Path(experiments_root) / exp_id / MANIFEST_FILENAME
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_experiment(data)
    return data


def list_experiments(experiments_root: str | Path) -> List[Dict[str, Any]]:
    """Return every entry from experiments/index.jsonl."""
    index_path = Path(experiments_root) / INDEX_FILENAME
    if not index_path.exists():
        return []
    entries = []
    for line in index_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    return entries
