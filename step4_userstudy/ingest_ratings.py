"""
Purpose: STEP 4 - turn returned human rating sheets into study metrics.
Input:   --ratings (a completed ratings CSV or a dir of them), --out.
Output:  data/userstudy/study_metrics.json — per-condition means, would-include rate, agreement.

Computes ONLY from supplied human ratings (no fabrication). If given a synthetic/demo file the
numbers reflect that file — the caller is responsible for using real returned sheets for results.

Run: python -m step4_userstudy.ingest_ratings --ratings data/userstudy/ratings_completed.csv --out data/userstudy
"""
from __future__ import annotations

import argparse
import csv
import glob
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from pplib.io_utils import dump_json, ensure_dir, get_logger

log = get_logger("ingest_ratings")
LIKERT = ["accuracy_1_5", "clarity_1_5", "completeness_1_5"]


def _rows(ratings: str) -> List[dict]:
    paths = ([ratings] if Path(ratings).is_file() else glob.glob(str(Path(ratings) / "*.csv")))
    rows: List[dict] = []
    for p in paths:
        with open(p, newline="", encoding="utf-8") as f:
            rows.extend(r for r in csv.DictReader(f))
    return rows


def _to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def ingest(ratings: str, out_dir: str) -> Dict:
    """Aggregate ratings into per-condition Likert means + would-include rate + agreement."""
    rows = [r for r in _rows(ratings) if any(_to_float(r.get(k)) is not None for k in LIKERT)]
    by_cond: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    include: Dict[str, List[int]] = defaultdict(list)
    per_item: Dict[str, List[float]] = defaultdict(list)  # accuracy by prcs for agreement

    for r in rows:
        cond = r.get("condition", "unknown")
        for k in LIKERT:
            v = _to_float(r.get(k))
            if v is not None:
                by_cond[cond][k].append(v)
        inc = str(r.get("would_include_yn", "")).strip().lower()
        if inc in ("y", "yes", "1", "true"):
            include[cond].append(1)
        elif inc in ("n", "no", "0", "false"):
            include[cond].append(0)
        acc = _to_float(r.get("accuracy_1_5"))
        if acc is not None:
            per_item[f"{cond}|{r.get('prcs_id','')}"].append(acc)

    conditions = {}
    for cond, metrics in by_cond.items():
        conditions[cond] = {
            **{k: round(statistics.mean(v), 3) for k, v in metrics.items() if v},
            "would_include_rate": round(statistics.mean(include[cond]), 3) if include[cond] else None,
            "n_ratings": len(metrics.get("accuracy_1_5", [])),
        }
    # mean pairwise |Δ| on accuracy across raters of the same item (lower = more agreement)
    diffs = []
    for vals in per_item.values():
        if len(vals) >= 2:
            diffs += [abs(a - b) for i, a in enumerate(vals) for b in vals[i + 1:]]
    agreement = {"mean_pairwise_abs_diff_accuracy": round(statistics.mean(diffs), 3) if diffs else None,
                 "n_items_with_multiple_raters": sum(1 for v in per_item.values() if len(v) >= 2)}

    result = {"n_rows": len(rows), "conditions": conditions, "agreement": agreement}
    out = ensure_dir(out_dir)
    dump_json(result, out / "study_metrics.json")
    log.info("Ingested %d ratings across %d conditions", len(rows), len(conditions))
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="Ingest user-study ratings (Step 4).")
    ap.add_argument("--ratings", required=True, help="completed ratings CSV or dir of CSVs")
    ap.add_argument("--out", default="data/userstudy")
    args = ap.parse_args()
    r = ingest(args.ratings, args.out)
    print("\n=== Study metrics ===")
    for cond, m in r["conditions"].items():
        print(f"  [{cond}] {m}")
    print(f"  agreement: {r['agreement']}")


if __name__ == "__main__":
    main()
