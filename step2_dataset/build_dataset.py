"""
Purpose: STEP 2 - build the ADPPG dataset from PRCS records: WEAK labels (or human
         overrides), Codr-ingestible export, and leakage-free APK-grouped splits.
Input:   PRCS dir (data/prcs), weak-label config, optional human_labels.json.
Output:  data/dataset/adppg.jsonl, splits.json, labels.csv, codr_export/<id>.json.

Entries in the labels file (human or LLM, each tagged with its label_source) override weak
labels when present. --test-ids pins the test split to an annotated id list.

Run: python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
"""
from __future__ import annotations

import argparse
import glob
import json
import random
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_json, load_yaml
from pplib.pact_schema import validate_label
from pplib.schema import (BANNER_BOOTSTRAP, PRACTICE_LABELS, PURPOSE_LABELS, is_gold,
                          label_banner)
from step2_dataset.weak_labeler import WeakLabeler

log = get_logger("build_dataset")
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_prcs(prcs_dir: Path) -> List[dict]:
    files = sorted(glob.glob(str(prcs_dir / "prcs_*.json")))
    return [load_json(f) for f in files]


def _apply_labels(prcs: List[dict], labeler: WeakLabeler,
                  overrides: Dict[str, dict]) -> List[dict]:
    """Attach labels to each PRCS; labels-file entries override weak ones when available."""
    out = []
    for p in prcs:
        pid = p["prcs_id"]
        if pid in overrides:
            h = overrides[pid]
            if "label_source" not in h:
                raise ValueError(
                    f"labels entry {pid} has no label_source; tag legacy files with "
                    "`python -m step2_dataset.ingest_annotations --retag-llm <labels.json>`")
            try:
                validate_label(h)
            except ValueError as e:
                raise ValueError(f"labels entry {pid}: {e}") from None
            src = h["label_source"]
            labels = {"practice": [l for l in PRACTICE_LABELS if l in h.get("practice", [])],
                      "purpose": [l for l in PURPOSE_LABELS if l in h.get("purpose", [])],
                      "label_source": src, "weak_banner": label_banner(src)}
            if h.get("not_personal"):
                labels["not_personal"] = True
        else:
            labels = labeler.label(p)
        out.append({**p, "labels": labels})
    return out


def _subsample_test_app(records: List[dict], app: str, cap: int, seed: int,
                        group_key: str = "app_package") -> List[dict]:
    """Keep only `cap` flows of `app` (rare purposes first); drop the rest so the held-out test
    app is small enough to hand-label. Other apps untouched -> still leakage-free."""
    app_recs = [r for r in records if r.get(group_key) == app]
    if not app_recs or len(app_recs) <= cap:
        return records
    rng = random.Random(seed)
    rare = [r for r in app_recs
            if any(p in ("Advertisement", "Analytics") for p in r["labels"]["purpose"])]
    rare_ids = {r["prcs_id"] for r in rare}
    common = [r for r in app_recs if r["prcs_id"] not in rare_ids]
    rng.shuffle(rare); rng.shuffle(common)
    keep_ids = {r["prcs_id"] for r in (rare + common)[:cap]}
    log.info("Subsampled test app %s: %d -> %d flows (%d rare-purpose available)",
             app, len(app_recs), len(keep_ids), len(rare))
    return [r for r in records if r.get(group_key) != app or r["prcs_id"] in keep_ids]


def _pin_test_ids(records: List[dict], test_ids: Set[str], group_key: str) -> tuple[List[dict], Set[str]]:
    """Keep exactly `test_ids` from the apps they belong to (other flows of those apps are dropped,
    so no held-out app leaks into train/val). Returns (records, held-out groups)."""
    missing = test_ids - {r["prcs_id"] for r in records}
    if missing:
        raise ValueError(f"{len(missing)} pinned test ids are not in the PRCS set, e.g. {sorted(missing)[:3]}")
    held_out = {r.get(group_key, "?") for r in records if r["prcs_id"] in test_ids}
    kept = [r for r in records if r["prcs_id"] in test_ids or r.get(group_key, "?") not in held_out]
    log.info("Pinned %d test PRCS from %d held-out app(s); dropped %d other flows of those apps",
             len(test_ids), len(held_out), len(records) - len(kept))
    return kept, held_out


def _grouped_splits(records: List[dict], cfg: dict,
                    held_out: Optional[Set[str]] = None) -> Dict[str, List[str]]:
    """Assign whole APK groups to train/val/test so no app leaks across splits.
    If splits.test_app (one app or a comma-separated list) or `held_out` is set, those apps are
    pinned to test and the rest split into train/val."""
    sc = cfg.get("splits", {})
    seed = sc.get("seed", 13)
    ratios = sc.get("ratios", {"train": 0.7, "val": 0.15, "test": 0.15})
    group_key = sc.get("group_by", "app_package")
    test_apps = set(held_out or (str(sc["test_app"]).split(",") if sc.get("test_app") else []))

    groups: Dict[str, List[str]] = {}
    for r in records:
        groups.setdefault(r.get(group_key, "?"), []).append(r["prcs_id"])

    if test_apps & set(groups):
        test_g = [k for k in groups if k in test_apps]
        rest = [k for k in groups if k not in test_apps]
        random.Random(seed).shuffle(rest)
        denom = ratios["train"] + ratios["val"] or 1
        n_val = round(len(rest) * ratios["val"] / denom) if len(rest) > 1 else 0
        val_g = rest[:n_val]
        train_g = rest[n_val:]
    else:
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
             group_key, len(groups), len(splits["train"]), len(splits["val"]), len(splits["test"]))
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
        "label_status": "verified" if is_gold(rec["labels"]["label_source"]) else "unverified",
        "note": label_banner(rec["labels"]["label_source"]),
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
                  human_labels: Optional[str] = None, test_app: Optional[str] = None,
                  test_cap: Optional[int] = None, test_ids: Optional[List[str]] = None) -> dict:
    """Build the ADPPG dataset; returns a summary dict.

    test_app pins one app (or a comma-separated list) as the held-out test split; test_cap
    subsamples each of those apps to that many flows.
    test_ids pins the test split to exactly those PRCS (e.g. the annotated set)."""
    cfg = load_yaml(config or REPO_ROOT / "configs" / "weak_labels.yaml")
    if test_app:
        cfg.setdefault("splits", {})["test_app"] = test_app
    labeler = WeakLabeler()
    overrides = load_json(human_labels) if human_labels and Path(human_labels).exists() else {}
    if overrides:
        log.info("Loaded %d label overrides (%s)", len(overrides),
                 dict(Counter(h.get("label_source", "?") for h in overrides.values())))

    prcs = _load_prcs(Path(prcs_dir))
    records = _apply_labels(prcs, labeler, overrides)
    if test_app and test_cap:
        for app in test_app.split(","):
            records = _subsample_test_app(records, app, test_cap,
                                          cfg.get("splits", {}).get("seed", 13))
    held_out = None
    if test_ids:
        group_key = cfg.get("splits", {}).get("group_by", "app_package")
        records, held_out = _pin_test_ids(records, set(test_ids), group_key)
    splits = _grouped_splits(records, cfg, held_out)

    out = ensure_dir(out_dir)
    with open(out / "adppg.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    dump_json(splits, out / "splits.json")
    _labels_csv(records).to_csv(out / "labels.csv", index=False, encoding="utf-8")
    codr = ensure_dir(out / "codr_export")
    for r in records:
        dump_json(_codr_record(r), codr / f"{r['prcs_id']}.json")

    counts = Counter(r["labels"]["label_source"] for r in records)
    source = {r["prcs_id"]: r["labels"]["label_source"] for r in records}
    return {"records": len(records), "weak": counts["weak"], "llm": counts["llm"],
            "human": counts["human"],
            "test_all_human": bool(splits["test"]) and all(is_gold(source[i]) for i in splits["test"]),
            "splits": {k: len(v) for k, v in splits.items()}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the ADPPG dataset (Step 2).")
    ap.add_argument("--prcs", default="data/prcs")
    ap.add_argument("--out", default="data/dataset")
    ap.add_argument("--config", default="configs/weak_labels.yaml")
    ap.add_argument("--human-labels", default="data/dataset/human_labels.json",
                    help="optional label overrides (human or llm, each tagged); used if the file exists")
    ap.add_argument("--test-app", default=None,
                    help="pin this app_package (or a comma-separated list) as the held-out test split")
    ap.add_argument("--test-cap", type=int, default=None,
                    help="subsample the test app to this many flows (small enough to hand-label)")
    ap.add_argument("--test-ids", default=None,
                    help="annotation manifest.json whose test_ids become exactly the test split")
    args = ap.parse_args()
    test_ids = load_json(args.test_ids)["test_ids"] if args.test_ids else None
    s = build_dataset(args.prcs, args.out, args.config, args.human_labels,
                      test_app=args.test_app, test_cap=args.test_cap, test_ids=test_ids)
    print("\n=== ADPPG summary ===")
    if not s["test_all_human"]:
        print(f"  [{BANNER_BOOTSTRAP}]")
    print(f"  records={s['records']}  weak={s['weak']}  llm={s['llm']}  human={s['human']}")
    print(f"  splits={s['splits']}")


if __name__ == "__main__":
    main()
