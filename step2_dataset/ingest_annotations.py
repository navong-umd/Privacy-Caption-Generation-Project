"""
Purpose: G1 helper - convert a filled annotation sheet into a labels file (human_labels.json).
Input:   --sheet annotation_sheet.csv (P_*/U_* columns marked, plus annotator/confidence/notes),
         --out human_labels.json, [--annotator NAME] [--merge].
Output:  {prcs_id: {practice, purpose, label_source, annotator, confidence, notes, schema_version,
         not_personal (only when the annotator marked the flow as carrying no personal data)}}.

Only rows with at least one label marked are emitted (unmarked PRCS keep their weak label).
Every row needs an annotator (sheet column or --annotator) and is validated against the PAcT
label schema. --merge adds rows to an existing labels file, replacing entries with the same
prcs_id (used for adjudicated overlap items). --retag-llm marks entries written before labels
carried a label_source as LLM-assigned.

Run: python -m step2_dataset.ingest_annotations --sheet ali_solo.csv --out human_labels.json --annotator ali
     python -m step2_dataset.ingest_annotations --retag-llm data/eval_run/human_labels.json
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Optional

from pplib.io_utils import dump_json, get_logger, load_json
from pplib.pact_schema import PACT_SCHEMA_VERSION, validate_label
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS

log = get_logger("ingest_annotations")

# Sheet confidence is a 1-3 scale (1 = unsure, 3 = sure); the label schema stores [0, 1].
CONFIDENCE_SCALE = {"1": 0.33, "2": 0.67, "3": 1.0, "": 1.0}


def _marked(v) -> bool:
    return str(v).strip().lower() in ("1", "x", "y", "yes", "true", "✓")


def ingest_sheet(sheet_csv: str, out_json: str, annotator: Optional[str] = None,
                 merge: bool = False) -> Dict[str, dict]:
    """Parse the filled sheet into labels-file entries and write (or merge into) out_json."""
    rows = list(csv.DictReader(Path(sheet_csv).open(encoding="utf-8")))
    labels: Dict[str, dict] = {}
    for r in rows:
        practice = [l for l in PRACTICE_LABELS if _marked(r.get(f"P_{l}"))]
        purpose = [l for l in PURPOSE_LABELS if _marked(r.get(f"U_{l}"))]
        not_personal = _marked(r.get("not_personal"))
        if not_personal and (practice or purpose):
            raise ValueError(f"{sheet_csv}: row {r['prcs_id']} is marked not_personal and also has "
                             "PAcT labels; leave the P_/U_ columns blank for non-personal flows")
        if not (practice or purpose or not_personal):    # skip unannotated rows
            continue
        who = (r.get("annotator") or "").strip() or annotator
        if not who:
            raise ValueError(f"{sheet_csv}: row {r['prcs_id']} has no annotator; "
                             "fill the annotator column or pass --annotator")
        conf = str(r.get("confidence") or "").strip()
        if conf not in CONFIDENCE_SCALE:
            raise ValueError(f"{sheet_csv}: row {r['prcs_id']} confidence {conf!r} is not 1, 2 or 3")
        entry = {"practice": practice, "purpose": purpose, "label_source": "human",
                 "annotator": who, "confidence": CONFIDENCE_SCALE[conf],
                 "notes": (r.get("notes") or "").strip(), "schema_version": PACT_SCHEMA_VERSION}
        if not_personal:
            entry["not_personal"] = True
        validate_label(entry)
        labels[r["prcs_id"]] = entry
    out = {**load_json(out_json), **labels} if merge and Path(out_json).exists() else labels
    dump_json(out, out_json)
    log.info("Ingested %d/%d annotated PRCS -> %s (%d entries)", len(labels), len(rows), out_json, len(out))
    return labels


def retag_llm(labels_json: str) -> int:
    """Mark entries that predate label provenance as LLM-assigned. Returns how many changed."""
    labels = load_json(labels_json)
    changed = 0
    for entry in labels.values():
        if "label_source" in entry:
            continue
        entry.update({"label_source": "llm", "annotator": "llm-2pass-2026-06", "confidence": 1.0,
                      "notes": "pre-provenance LLM label", "schema_version": PACT_SCHEMA_VERSION})
        validate_label(entry)
        changed += 1
    dump_json(labels, labels_json)
    log.info("Re-tagged %d/%d entries as llm -> %s", changed, len(labels), labels_json)
    return changed


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest a filled annotation sheet into a labels file (G1).")
    ap.add_argument("--sheet", default="data/dataset/annotation_sheet.csv")
    ap.add_argument("--out", default="data/dataset/human_labels.json")
    ap.add_argument("--annotator", default=None, help="annotator id for rows without one in the sheet")
    ap.add_argument("--merge", action="store_true",
                    help="merge into an existing --out file, replacing entries with the same prcs_id")
    ap.add_argument("--retag-llm", metavar="LABELS_JSON", default=None,
                    help="mark entries without a label_source in this file as LLM-assigned, then exit")
    args = ap.parse_args()
    if args.retag_llm:
        print(f"[+] {retag_llm(args.retag_llm)} entries re-tagged as llm in {args.retag_llm}")
        return
    labels = ingest_sheet(args.sheet, args.out, annotator=args.annotator, merge=args.merge)
    print(f"[+] {len(labels)} annotated PRCS -> {args.out}")
    print("    Check agreement on the overlap sheet, then rebuild with the pinned test split:")
    print("    python -m step2_dataset.agreement --a <ali_overlap.json> --b <labmate_overlap.json>")
    print(f"    python -m step2_dataset.build_dataset --prcs <prcs dir> --out <dataset dir> "
          f"--human-labels {args.out} --test-ids <manifest.json>")


if __name__ == "__main__":
    main()
