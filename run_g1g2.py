"""
One-shot G1->G2: take a filled annotation sheet -> human labels -> rebuild dataset -> retrain ->
print whether the BOOTSTRAP banner cleared + the headline metrics.

Run (after you've filled + saved the sheet):
    python run_g1g2.py                      # uses data/starter/*
    python run_g1g2.py --base data/corpus_run   # later, for the full corpus
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Windows consoles default to cp1252, which can't encode the ✅ banner glyph. Make
# stdout UTF-8 so the result line never crashes the run (no-op where already UTF-8).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from step2_dataset.ingest_annotations import ingest_sheet
from step2_dataset.build_dataset import build_dataset
from step2_convgnn.train import train


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/starter", help="folder with prcs/ + annotation_sheet.csv")
    ap.add_argument("--prcs", default=None, help="override PRCS dir (default: <base>/prcs)")
    ap.add_argument("--dataset", default=None, help="override dataset dir (default: <base>/dataset)")
    ap.add_argument("--sheet", default=None, help="override sheet (default: <base>/annotation_sheet.csv)")
    ap.add_argument("--test-app", default=None, help="pin this app as the held-out test split")
    ap.add_argument("--test-cap", type=int, default=None, help="subsample the test app to N flows")
    ap.add_argument("--epochs", type=int, default=30)
    args = ap.parse_args()
    base = Path(args.base)
    prcs = args.prcs or str(base / "prcs")
    dataset = args.dataset or str(base / "dataset")
    sheet = Path(args.sheet) if args.sheet else base / "annotation_sheet.csv"
    human = Path(dataset).parent / "human_labels.json"

    print(f"[1/3] reading your labels from {sheet}")
    h = ingest_sheet(str(sheet), str(human))
    print(f"      -> {len(h)} rows labeled")
    if not h:
        print("      !! No rows labeled yet. Put 1s in the P_/U_ columns, save as CSV, and re-run.")
        return

    print("[2/3] rebuilding dataset with YOUR labels")
    s = build_dataset(prcs, dataset, human_labels=str(human),
                      test_app=args.test_app, test_cap=args.test_cap)
    print(f"      -> records={s['records']}  weak={s['weak']}  human={s['human']}")

    print("[3/3] retraining the model on your labels")
    r = train("configs/convgnn.yaml", dataset,
              out_dir=str(Path(dataset).parent / "model"), epochs=args.epochs)

    print("\n================= RESULT =================")
    if r["is_weak"]:
        print("  Banner: STILL BOOTSTRAP (some rows are unlabeled -> finish labeling to clear it)")
    else:
        print("  Banner: CLEARED  ✅  these are REAL metrics")
    t = r["test"]
    print(f"  Practice macro-F1: {t.get('practice_macro_f1', 0):.3f}")
    print(f"  Purpose  macro-F1: {t.get('purpose_macro_f1', 0):.3f}")


if __name__ == "__main__":
    main()
