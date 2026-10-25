"""
Purpose: G1 helper - turn an ADPPG dataset into a flat annotation spreadsheet humans can fill.
Input:   --dataset data/dataset (adppg.jsonl), --out annotation_sheet.csv, [--prefill].
Output:  one row per PRCS with code/API context + 8 blank label columns to mark (1 = applies).

Lets you do G1 in any spreadsheet (no Codr setup needed). The weak heuristic guess is shown in a
reference column; with --prefill the 8 label columns are pre-filled with it (faster, but verify each
to avoid anchoring bias). Convert the filled sheet back with ingest_annotations.py.

--kit DIR writes the two-annotator kit instead (calibration / overlap / solo sheets without weak
labels, plus manifest.json); see research/ANNOTATION_CODEBOOK.md.

Run: python -m step2_dataset.make_annotation_sheet --dataset data/dataset --out data/dataset/annotation_sheet.csv
     python -m step2_dataset.make_annotation_sheet --dataset data/corpus_run/dataset --kit data/annotation_kit
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path

from pplib.io_utils import dump_json, ensure_dir, get_logger
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS

log = get_logger("make_annotation_sheet")

PRACTICE_COLS = [f"P_{l}" for l in PRACTICE_LABELS]   # P_Processing, P_Collecting, ...
PURPOSE_COLS = [f"U_{l}" for l in PURPOSE_LABELS]     # U_Functionality, U_Advertisement, ...
META_COLS = ["prcs_id", "app_package", "class_name", "method_name", "source_api",
             "sink_api", "sink_type", "pi_type", "snippet", "weak_practice", "weak_purpose"]
SHEET_COLUMNS = META_COLS + PRACTICE_COLS + PURPOSE_COLS
# Two-annotator kit sheets: no weak-label columns (avoids anchoring) plus provenance columns.
KIT_COLUMNS = ([c for c in META_COLS if not c.startswith("weak_")] + PRACTICE_COLS + PURPOSE_COLS
               + ["not_personal", "annotator", "confidence", "notes"])

# Weak-labeler purpose classes that are rare in real corpora; worth forcing into the sample so G1
# annotators actually see (and correct) them instead of labeling an all-"Functionality" set.
RARE_PURPOSES = ("Analytics", "Advertisement")


def _select_records(records: list, sample: int, seed: int, oversample_rare: bool) -> list:
    """Stratify ~evenly across apps, optionally forcing in rare-purpose positives. sample<=0 -> all."""
    if sample <= 0 or sample >= len(records):
        return records
    rng = random.Random(seed)
    by_app: dict[str, list] = defaultdict(list)
    for r in records:
        by_app[r.get("app_package", "")].append(r)
    apps = sorted(by_app)
    chosen: dict[str, dict] = {}                      # prcs_id -> record (preserves uniqueness)

    if oversample_rare:
        rare = [r for r in records
                if any(p in RARE_PURPOSES for p in r.get("labels", {}).get("purpose", []))]
        # rarest class first (Analytics before Advertisement), then shuffle within class
        rng.shuffle(rare)
        rare.sort(key=lambda r: 0 if "Analytics" in r.get("labels", {}).get("purpose", []) else 1)
        for r in rare[: max(0, sample // 3)]:        # cap rare at ~1/3 of the budget
            chosen[r["prcs_id"]] = r

    pools = {a: [r for r in by_app[a] if r["prcs_id"] not in chosen] for a in apps}
    for a in apps:
        rng.shuffle(pools[a])
    per_app = max(1, (sample - len(chosen)) // max(1, len(apps)))
    for a in apps:                                   # even per-app pass
        for r in pools[a][:per_app]:
            chosen[r["prcs_id"]] = r
        pools[a] = pools[a][per_app:]
    leftovers = [r for a in apps for r in pools[a]]  # top up to the exact budget
    rng.shuffle(leftovers)
    for r in leftovers:
        if len(chosen) >= sample:
            break
        chosen[r["prcs_id"]] = r

    out = list(chosen.values())
    rng.shuffle(out)
    return out


def _row(r: dict, prefill: bool = False) -> dict:
    labels = r.get("labels", {})
    wp, wu = labels.get("practice", []), labels.get("purpose", [])
    row = {
        "prcs_id": r["prcs_id"], "app_package": r.get("app_package", ""),
        "class_name": r.get("class_name", ""), "method_name": r.get("method_name", ""),
        "source_api": r.get("source_api", ""), "sink_api": r.get("sink_api", ""),
        "sink_type": r.get("sink_type", ""), "pi_type": r.get("pi_type", ""),
        "snippet": (r.get("code_snippet", "") or "").replace("\n", " | ")[:1500],
        "weak_practice": "|".join(wp), "weak_purpose": "|".join(wu),
    }
    for l in PRACTICE_LABELS:
        row[f"P_{l}"] = 1 if (prefill and l in wp) else ""
    for l in PURPOSE_LABELS:
        row[f"U_{l}"] = 1 if (prefill and l in wu) else ""
    return row


def write_rows(out_csv: Path, columns: list, rows: list) -> None:
    ensure_dir(out_csv.parent)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _load(dataset_dir: str, split: str = "") -> list:
    records = [json.loads(l) for l in
               (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]
    if split:
        ids = set(json.loads((Path(dataset_dir) / "splits.json").read_text(encoding="utf-8"))
                  .get(split, []))
        records = [r for r in records if r["prcs_id"] in ids]
    return records


def make_sheet(dataset_dir: str, out_csv: str, prefill: bool = False,
               sample: int = 0, seed: int = 0, oversample_rare: bool = True,
               split: str = "") -> int:
    """Write the annotation sheet; returns the number of PRCS rows.

    split in {train,val,test} restricts to that split (label just the held-out test set).
    sample>0 writes a stratified subset (~even across apps, rare purposes forced in); sample<=0 = all.
    """
    records = _select_records(_load(dataset_dir, split), sample, seed, oversample_rare)
    write_rows(Path(out_csv), SHEET_COLUMNS, [_row(r, prefill) for r in records])
    log.info("Wrote %d annotation rows -> %s", len(records), out_csv)
    return len(records)


def make_kit(dataset_dir: str, out_dir: str, annotators: tuple = ("ali", "labmate"), seed: int = 0,
             n_calibration: int = 20, n_overlap: int = 100, n_solo: int = 150) -> dict:
    """Write the two-annotator kit: calibration sheets (validation split, never reported), overlap
    sheets (test split, labeled by both for agreement) and one solo sheet each (test split).
    Sheets hide the weak labels. Returns the manifest written to <out_dir>/manifest.json."""
    a, b = annotators
    test_pool = _load(dataset_dir, "test")
    need = n_overlap + 2 * n_solo
    if len(test_pool) < need:
        raise ValueError(f"test split has {len(test_pool)} PRCS; the kit needs {need}")
    rng = random.Random(seed)
    test = _select_records(test_pool, need, seed, oversample_rare=True)
    calibration = _select_records(_load(dataset_dir, "val"), n_calibration, seed, oversample_rare=True)
    rng.shuffle(test)                          # a full-pool selection comes back in file order
    rng.shuffle(calibration)
    overlap, solo_a, solo_b = test[:n_overlap], test[n_overlap:n_overlap + n_solo], test[n_overlap + n_solo:]
    plan = [(f"calibration_{a}.csv", a, calibration), (f"calibration_{b}.csv", b, calibration),
            (f"overlap_{a}.csv", a, overlap), (f"overlap_{b}.csv", b, overlap),
            (f"solo_{a}.csv", a, solo_a), (f"solo_{b}.csv", b, solo_b)]

    out = ensure_dir(out_dir)
    sheets = {}
    for fname, who, recs in plan:
        write_rows(out / fname, KIT_COLUMNS, [{**_row(r), "annotator": who} for r in recs])
        sheets[fname] = [r["prcs_id"] for r in recs]
    manifest = {"seed": seed, "annotators": [a, b],
                "source_splits": {"calibration": "val", "test": "test"},
                "calibration_ids": [r["prcs_id"] for r in calibration],
                "test_ids": [r["prcs_id"] for r in test], "sheets": sheets}
    dump_json(manifest, out / "manifest.json")
    log.info("Wrote annotation kit (%d test + %d calibration PRCS) -> %s", len(test), len(calibration), out)
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description="Make a human annotation sheet (G1).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--out", default="data/dataset/annotation_sheet.csv")
    ap.add_argument("--prefill", action="store_true",
                    help="pre-fill label columns with the WEAK guess (verify each to avoid bias)")
    ap.add_argument("--sample", type=int, default=0,
                    help="write a stratified subset of N rows (~even across apps); 0 = all")
    ap.add_argument("--seed", type=int, default=0, help="sampling seed (reproducible)")
    ap.add_argument("--no-oversample-rare", action="store_true",
                    help="do not force rare purposes (Analytics/Advertisement) into the sample")
    ap.add_argument("--split", default="", choices=["", "train", "val", "test"],
                    help="restrict to one split (e.g. test = label just the held-out eval app)")
    ap.add_argument("--kit", default=None, metavar="DIR",
                    help="write the two-annotator kit (calibration/overlap/solo sheets + manifest) to DIR")
    ap.add_argument("--annotators", default="ali,labmate", help="the kit's two annotator ids")
    args = ap.parse_args()
    if args.kit:
        m = make_kit(args.dataset, args.kit, tuple(args.annotators.split(",")), seed=args.seed)
        print(f"[+] kit -> {args.kit}: {len(m['test_ids'])} test + {len(m['calibration_ids'])} calibration PRCS")
        for name, ids in m["sheets"].items():
            print(f"    {name}: {len(ids)} rows")
        return
    n = make_sheet(args.dataset, args.out, args.prefill,
                   sample=args.sample, seed=args.seed,
                   oversample_rare=not args.no_oversample_rare, split=args.split)
    print(f"[+] {n} rows -> {args.out}")
    print("    Mark 1 in the P_* (Practice) and U_* (Purpose) columns that apply, then run:")
    print("    python -m step2_dataset.ingest_annotations --sheet "
          f"{args.out} --out data/dataset/human_labels.json")


if __name__ == "__main__":
    main()
