"""
Purpose: Lock the test split. digest_test_set hashes the sorted test ids with their labels and
         label sources, so a train-side rebuild leaves it unchanged while any change to a test item
         or its labels breaks it. The matrix runner refuses a real run when the lock does not match.
Input:   --dataset (adppg.jsonl + splits.json), --experiments-root.
Output:  <experiments-root>/TEST_SET.json (digest, ids, label counts).

Run once the test split is fully human-labeled (Phase 2):
    python -m pplib.testset --dataset data/corpus_run/dataset
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List

from pplib.experiment import current_code_version
from pplib.io_utils import REPO_ROOT, dump_json, load_json
from pplib.schema import BANNER_BOOTSTRAP, PRACTICE_LABELS, PURPOSE_LABELS, is_gold

LOCK_FILENAME = "TEST_SET.json"
DEFAULT_ROOT = REPO_ROOT / "experiments"


class TestSetLockError(RuntimeError):
    """The current test split does not match experiments/TEST_SET.json (or there is no lock)."""

    __test__ = False


def locked_items(dataset_dir: str | Path) -> List[Dict]:
    """The test split as [{prcs_id, practice, purpose, label_source}], sorted by id."""
    d = Path(dataset_dir)
    ids = set(load_json(d / "splits.json").get("test", []))
    items = []
    with open(d / "adppg.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["prcs_id"] in ids:
                lab = r["labels"]
                items.append({"prcs_id": r["prcs_id"],
                              "practice": [l for l in PRACTICE_LABELS if l in lab.get("practice", [])],
                              "purpose": [l for l in PURPOSE_LABELS if l in lab.get("purpose", [])],
                              "label_source": lab.get("label_source", "weak")})
    missing = ids - {i["prcs_id"] for i in items}
    if missing:
        raise ValueError(f"{len(missing)} test ids are not in adppg.jsonl, e.g. {sorted(missing)[:3]}")
    return sorted(items, key=lambda i: i["prcs_id"])


def digest_test_set(dataset_dir: str | Path) -> str:
    """sha256 over the canonical JSON of the sorted test items and their labels."""
    blob = json.dumps(locked_items(dataset_dir), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def lock_test_set(dataset_dir: str | Path, experiments_root: str | Path = DEFAULT_ROOT,
                  allow_non_gold: bool = False) -> Dict:
    """Write <experiments_root>/TEST_SET.json for the current test split.

    Refuses a split that is not entirely human-labeled unless allow_non_gold, in which case the
    lock carries the BOOTSTRAP banner."""
    items = locked_items(dataset_dir)
    if not items:
        raise ValueError("the test split is empty; nothing to lock")
    sources = Counter(i["label_source"] for i in items)
    all_gold = all(is_gold(s) for s in sources)
    if not all_gold and not allow_non_gold:
        raise ValueError(f"test split is not all human-labeled ({dict(sources)}); "
                         "finish annotation first or pass --allow-non-gold for a scratch lock")
    lock = {"digest": digest_test_set(dataset_dir), "n_items": len(items),
            "label_sources": dict(sources), "banner": "" if all_gold else BANNER_BOOTSTRAP,
            "code_version": current_code_version(REPO_ROOT),
            "test_ids": [i["prcs_id"] for i in items]}
    dump_json(lock, Path(experiments_root) / LOCK_FILENAME)
    return lock


def check_test_set(dataset_dir: str | Path, experiments_root: str | Path = DEFAULT_ROOT) -> str:
    """Return the current digest if it matches the lock; raise TestSetLockError otherwise."""
    path = Path(experiments_root) / LOCK_FILENAME
    if not path.exists():
        raise TestSetLockError(f"no {LOCK_FILENAME} under {experiments_root}; lock the human-labeled "
                               "test split with `python -m pplib.testset` or use --dry-run")
    digest = digest_test_set(dataset_dir)
    locked = load_json(path).get("digest")
    if digest != locked:
        raise TestSetLockError(f"test split digest {digest[:12]} does not match {LOCK_FILENAME} "
                               f"({str(locked)[:12]}); the test set changed since it was locked")
    return digest


def main() -> None:
    ap = argparse.ArgumentParser(description="Lock the test split into experiments/TEST_SET.json.")
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--experiments-root", default=str(DEFAULT_ROOT))
    ap.add_argument("--allow-non-gold", action="store_true",
                    help="lock a split that is not all human-labeled (scratch use; carries a banner)")
    args = ap.parse_args()
    lock = lock_test_set(args.dataset, args.experiments_root, args.allow_non_gold)
    if lock["banner"]:
        print(f"  [{lock['banner']}]")
    print(f"[+] locked {lock['n_items']} test PRCS, digest {lock['digest'][:12]} "
          f"-> {Path(args.experiments_root) / LOCK_FILENAME}")


if __name__ == "__main__":
    main()
