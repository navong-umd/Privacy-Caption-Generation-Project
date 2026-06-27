"""
Purpose: G1 helper - turn an ADPPG dataset into a flat annotation spreadsheet humans can fill.
Input:   --dataset data/dataset (adppg.jsonl), --out annotation_sheet.csv, [--prefill].
Output:  one row per PRCS with code/API context + 8 blank label columns to mark (1 = applies).

Lets you do G1 in any spreadsheet (no Codr setup needed). The weak heuristic guess is shown in a
reference column; with --prefill the 8 label columns are pre-filled with it (faster, but verify each
to avoid anchoring bias). Convert the filled sheet back with ingest_annotations.py.

Run: python -m step2_dataset.make_annotation_sheet --dataset data/dataset --out data/dataset/annotation_sheet.csv
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from pplib.io_utils import ensure_dir, get_logger
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS

log = get_logger("make_annotation_sheet")

PRACTICE_COLS = [f"P_{l}" for l in PRACTICE_LABELS]   # P_Processing, P_Collecting, ...
PURPOSE_COLS = [f"U_{l}" for l in PURPOSE_LABELS]     # U_Functionality, U_Advertisement, ...
META_COLS = ["prcs_id", "app_package", "class_name", "method_name", "source_api",
             "sink_api", "sink_type", "pi_type", "snippet", "weak_practice", "weak_purpose"]
SHEET_COLUMNS = META_COLS + PRACTICE_COLS + PURPOSE_COLS


def make_sheet(dataset_dir: str, out_csv: str, prefill: bool = False) -> int:
    """Write the annotation sheet; returns the number of PRCS rows."""
    records = [json.loads(l) for l in
               (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]
    out = Path(out_csv)
    ensure_dir(out.parent)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHEET_COLUMNS)
        w.writeheader()
        for r in records:
            labels = r.get("labels", {})
            wp, wu = labels.get("practice", []), labels.get("purpose", [])
            row = {
                "prcs_id": r["prcs_id"], "app_package": r.get("app_package", ""),
                "class_name": r.get("class_name", ""), "method_name": r.get("method_name", ""),
                "source_api": r.get("source_api", ""), "sink_api": r.get("sink_api", ""),
                "sink_type": r.get("sink_type", ""), "pi_type": r.get("pi_type", ""),
                "snippet": (r.get("code_snippet", "") or "").replace("\n", " ")[:300],
                "weak_practice": "|".join(wp), "weak_purpose": "|".join(wu),
            }
            for l in PRACTICE_LABELS:
                row[f"P_{l}"] = 1 if (prefill and l in wp) else ""
            for l in PURPOSE_LABELS:
                row[f"U_{l}"] = 1 if (prefill and l in wu) else ""
            w.writerow(row)
    log.info("Wrote %d annotation rows -> %s", len(records), out)
    return len(records)


def main() -> None:
    ap = argparse.ArgumentParser(description="Make a human annotation sheet (G1).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--out", default="data/dataset/annotation_sheet.csv")
    ap.add_argument("--prefill", action="store_true",
                    help="pre-fill label columns with the WEAK guess (verify each to avoid bias)")
    args = ap.parse_args()
    n = make_sheet(args.dataset, args.out, args.prefill)
    print(f"[+] {n} rows -> {args.out}")
    print("    Mark 1 in the P_* (Practice) and U_* (Purpose) columns that apply, then run:")
    print("    python -m step2_dataset.ingest_annotations --sheet "
          f"{args.out} --out data/dataset/human_labels.json")


if __name__ == "__main__":
    main()
