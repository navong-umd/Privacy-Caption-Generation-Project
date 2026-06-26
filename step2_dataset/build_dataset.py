"""
Purpose: STEP 2 - build the ADPPG dataset from PRCS records: WEAK labels (or human
         overrides), Codr-ingestible export, and leakage-free APK-grouped splits.
Input:   PRCS dir (data/prcs), weak-label config, optional human_labels.json.
Output:  data/dataset/adppg.jsonl, splits.json, labels.csv, codr_export/<id>.json.

Human labels (Gate G1) override weak labels automatically when present — see HANDOFF_G1.md.

Run: python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
"""
from __future__ import annotations

import argparse
import glob
import json
import random
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_json, load_yaml
from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS
from step2_dataset.weak_labeler import WeakLabeler

log = get_logger("build_dataset")
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_prcs(prcs_dir: Path) -> List[dict]:
    files = sorted(glob.glob(str(prcs_dir / "prcs_*.json")))
    return [load_json(f) for f in files]


def _apply_labels(prcs: List[dict], labeler: WeakLabeler,
                  human: Dict[str, dict]) -> List[dict]:
    """Attach labels to each PRCS; human labels override weak ones when available."""
    out = []
    for p in prcs:
        pid = p["prcs_id"]
        if pid in human:
            h = human[pid]
            labels = {"practice": [l for l in PRACTICE_LABELS if l in h.get("practice", [])],
                      "purpose": [l for l in PURPOSE_LABELS if l in h.get("purpose", [])],
                      "label_source": "human", "weak_banner": ""}
        else:
            labels = labeler.label(p)
        out.append({**p, "labels": labels})
    return out


def _grouped_splits(records: List[dict], cfg: dict) -> Dict[str, List[str]]:
    """Assign whole APK groups to train/val/test so no app leaks across splits."""
    sc = cfg.get("splits", {})
    seed = sc.get("seed", 13)
    ratios = sc.get("ratios", {"train": 0.7, "val": 0.15, "test": 0.15})
    group_key = sc.get("group_by", "app_package")

    groups: Dict[str, List[str]] = {}
    for r in records:
        groups.setdefault(r.get(group_key, "?"), []).append(r["prcs_id"])
    keys = sorted(groups)
    random.Random(seed).shuffle(keys)

    n = len(keys)
    n_train = max(1, round(n * ratios["train"])) if n else 0
    n_val = round(n * ratios["val"]) if n > 2 else (1 if n == 2 else 0)
    train_g = keys[:n_train]
    val_g = keys[n_train:n_train + n_val]
    test_g = keys[n_train + n_val:]
    # ensure test is non-empty when we have >=3 groups
    if n >= 3 and not test_g:
        test_g = [val_g.pop()] if val_g else [train_g.pop()]

    splits = {"train": [], "val": [], "test": []}
    for g, ids in groups.items():
        bucket = "train" if g in train_g else "val" if g in val_g else "test"
        splits[bucket].extend(ids)
    log.info("Splits by %s: %d groups -> train=%d val=%d test=%d PRCS",
             group_key, n, len(splits["train"]), len(splits["val"]), len(splits["test"]))
    return splits


def _codr_record(rec: dict) -> dict:
    """A Codr-ingestible JSON: metadata + snippet + subgraph + candidate labels to verify."""
    return {
        "id": rec["prcs_id"],
        "app": {"package": rec["app_package"], "apk": rec["apk_filename"]},
        "provenance": {"class": rec["class_name"], "method": rec["method_name"],
                       "source_api": rec["source_api"], "sink_api": rec["sink_api"]},
        "code": rec["code_snippet"],
        "graph": rec["subgraph"],
        "candidate_labels": {"practice": rec["labels"]["practice"],
                             "purpose": rec["labels"]["purpose"]},
        "label_status": "unverified" if rec["labels"]["label_source"] == "weak" else "verified",
        "note": BANNER_WEAK if rec["labels"]["label_source"] == "weak" else "",
    }


def _labels_csv(records: List[dict]) -> pd.DataFrame:
    rows = []
    for r in records:
        row = {"prcs_id": r["prcs_id"], "app_package": r["app_package"],
               "label_source": r["labels"]["label_source"]}
        for l in PRACTICE_LABELS:
            row[f"practice_{l}"] = int(l in r["labels"]["practice"])
        for l in PURPOSE_LABELS:
            row[f"purpose_{l}"] = int(l in r["labels"]["purpose"])
        rows.append(row)
    return pd.DataFrame(rows)


def build_dataset(prcs_dir: str, out_dir: str, config: Optional[str] = None,
                  human_labels: Optional[str] = None) -> dict:
    """Build the ADPPG dataset; returns a summary dict."""
    cfg = load_yaml(config or REPO_ROOT / "configs" / "weak_labels.yaml")
    labeler = WeakLabeler()
    human = load_json(human_labels) if human_labels and Path(human_labels).exists() else {}
    if human:
        log.info("Loaded %d HUMAN label overrides (Gate G1)", len(human))

    prcs = _load_prcs(Path(prcs_dir))
    records = _apply_labels(prcs, labeler, human)
    splits = _grouped_splits(records, cfg)

    out = ensure_dir(out_dir)
    with open(out / "adppg.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    dump_json(splits, out / "splits.json")
    _labels_csv(records).to_csv(out / "labels.csv", index=False, encoding="utf-8")
    codr = ensure_dir(out / "codr_export")
    for r in records:
        dump_json(_codr_record(r), codr / f"{r['prcs_id']}.json")

    n_weak = sum(1 for r in records if r["labels"]["label_source"] == "weak")
    return {"records": len(records), "weak": n_weak, "human": len(records) - n_weak,
            "splits": {k: len(v) for k, v in splits.items()}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the ADPPG dataset (Step 2).")
    ap.add_argument("--prcs", default="data/prcs")
    ap.add_argument("--out", default="data/dataset")
    ap.add_argument("--config", default="configs/weak_labels.yaml")
    ap.add_argument("--human-labels", default="data/dataset/human_labels.json",
                    help="optional human label overrides (Gate G1); used if the file exists")
    args = ap.parse_args()
    s = build_dataset(args.prcs, args.out, args.config, args.human_labels)
    print("\n=== ADPPG summary ===")
    if s["human"] == 0:
        print(f"  [{BANNER_WEAK}]")
    print(f"  records={s['records']}  weak={s['weak']}  human={s['human']}")
    print(f"  splits={s['splits']}")


if __name__ == "__main__":
    main()
