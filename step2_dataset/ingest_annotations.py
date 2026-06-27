"""
Purpose: G1 helper - convert a filled annotation sheet into human_labels.json.
Input:   --sheet annotation_sheet.csv (with P_*/U_* columns marked), --out human_labels.json.
Output:  data/dataset/human_labels.json: {prcs_id: {practice:[...], purpose:[...]}}.

Only rows with at least one label marked are emitted (partial annotation is fine; unmarked PRCS
keep their weak label). build_dataset then auto-overrides weak labels with these (Gate G1 done).

Run: python -m step2_dataset.ingest_annotations --sheet data/dataset/annotation_sheet.csv --out data/dataset/human_labels.json
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict

from pplib.io_utils import dump_json, get_logger
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS

log = get_logger("ingest_annotations")


def _marked(v) -> bool:
    return str(v).strip().lower() in ("1", "x", "y", "yes", "true", "✓")


def ingest_sheet(sheet_csv: str, out_json: str) -> Dict[str, dict]:
    """Parse the filled sheet into a human_labels.json mapping."""
    rows = list(csv.DictReader(Path(sheet_csv).open(encoding="utf-8")))
    human: Dict[str, dict] = {}
    for r in rows:
        practice = [l for l in PRACTICE_LABELS if _marked(r.get(f"P_{l}"))]
        purpose = [l for l in PURPOSE_LABELS if _marked(r.get(f"U_{l}"))]
        if practice or purpose:                       # skip unannotated rows
            human[r["prcs_id"]] = {"practice": practice, "purpose": purpose}
    dump_json(human, out_json)
    log.info("Ingested %d/%d annotated PRCS -> %s", len(human), len(rows), out_json)
    return human


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest a filled annotation sheet into human_labels.json (G1).")
    ap.add_argument("--sheet", default="data/dataset/annotation_sheet.csv")
    ap.add_argument("--out", default="data/dataset/human_labels.json")
    args = ap.parse_args()
    human = ingest_sheet(args.sheet, args.out)
    print(f"[+] {len(human)} annotated PRCS -> {args.out}")
    print("    Now rebuild + retrain (weak labels auto-overridden, BOOTSTRAP banner clears):")
    print("    python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset "
          "--human-labels data/dataset/human_labels.json")
    print("    python -m step2_convgnn.train --config configs/convgnn.yaml --dataset data/dataset")


if __name__ == "__main__":
    main()
