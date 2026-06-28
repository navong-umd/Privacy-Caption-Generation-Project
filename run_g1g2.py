"""
One-shot G1->G2: take a filled annotation sheet -> human labels -> rebuild dataset -> retrain ->
print whether the BOOTSTRAP banner cleared + the headline metrics.

Run (after you've filled + saved the sheet):
    python run_g1g2.py                      # uses data/starter/*
    python run_g1g2.py --base data/corpus_run   # later, for the full corpus
"""
from __future__ import annotations
import argparse
from pathlib import Path

from step2_dataset.ingest_annotations import ingest_sheet
from step2_dataset.build_dataset import build_dataset
from step2_convgnn.train import train


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="data/starter", help="folder with prcs/ + annotation_sheet.csv")
    ap.add_argument("--epochs", type=int, default=30)
    args = ap.parse_args()
    base = Path(args.base)
    sheet = base / "annotation_sheet.csv"
    human = base / "human_labels.json"

    print(f"[1/3] reading your labels from {sheet}")
    h = ingest_sheet(str(sheet), str(human))
    print(f"      -> {len(h)} rows labeled")
    if not h:
        print("      !! No rows labeled yet. Put 1s in the P_/U_ columns, save as CSV, and re-run.")
        return

    print("[2/3] rebuilding dataset with YOUR labels")
    s = build_dataset(str(base / "prcs"), str(base / "dataset"), human_labels=str(human))
    print(f"      -> records={s['records']}  weak={s['weak']}  human={s['human']}")

    print("[3/3] retraining the model on your labels")
    r = train("configs/convgnn.yaml", str(base / "dataset"),
              out_dir=str(base / "model"), epochs=args.epochs)

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
