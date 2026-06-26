"""
Purpose: STEP 4 - assemble the developer user-study packet (blind A/B: PPG vs Code2Seq).
Input:   --dataset (code snippets) + --captions (both caption conditions), --out, --max-items.
Output:  study_tasks.json, study_packet.md, ratings_template.csv (BLANK — humans fill it in).

Produces NO ratings — only the instrument. Real ratings are collected from human subjects (G3)
and turned into metrics by ingest_ratings.py.

Run: python -m step4_userstudy.build_study --dataset data/dataset --captions data/captions --out data/userstudy
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Dict, List

from pplib.io_utils import dump_json, ensure_dir, get_logger

log = get_logger("build_study")


def build_study(dataset_dir: str, captions_dir: str, out_dir: str,
                max_items: int = 20, seed: int = 13) -> Dict:
    """Create the A/B task set + blank ratings template."""
    records = {json.loads(l)["prcs_id"]: json.loads(l)
               for l in (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()}
    caps = {c["prcs_id"]: c for c in
            json.loads((Path(captions_dir) / "captions.json").read_text(encoding="utf-8"))}

    ids = [pid for pid in caps if pid in records]
    random.Random(seed).shuffle(ids)
    ids = ids[:max_items]

    tasks: List[dict] = []
    for pid in ids:
        rec, cap = records[pid], caps[pid]
        # blind A/B: randomize which condition is shown as option_1 vs option_2
        conds = [("ppg", cap["caption"]), ("baseline", cap["baseline_caption"])]
        random.Random(hash(pid) & 0xffff).shuffle(conds)
        tasks.append({
            "prcs_id": pid, "app_package": rec["app_package"],
            "code_snippet": rec.get("code_snippet", ""),
            "option_1": {"condition": conds[0][0], "caption": conds[0][1]},
            "option_2": {"condition": conds[1][0], "caption": conds[1][1]},
        })

    out = ensure_dir(out_dir)
    dump_json({"tasks": tasks, "instrument": "blind A/B ppg vs baseline"}, out / "study_tasks.json")

    # human-readable packet (conditions hidden)
    md = ["# User-Study Packet (blind)", "", "Rate each option 1–5 on accuracy, clarity, "
          "completeness, and whether you would include it. Record answers in ratings_template.csv.", ""]
    for i, t in enumerate(tasks, 1):
        md += [f"## Task {i} — `{t['prcs_id']}`  (app: {t['app_package']})", "",
               "**Code:**", "```", t["code_snippet"], "```",
               f"- **Option A:** {t['option_1']['caption']}".replace("\n", " "),
               f"- **Option B:** {t['option_2']['caption']}".replace("\n", " "), ""]
    (out / "study_packet.md").write_text("\n".join(md), encoding="utf-8")

    # blank ratings template (one row per task x option)
    with open(out / "ratings_template.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant_id", "prcs_id", "option", "condition",
                    "accuracy_1_5", "clarity_1_5", "completeness_1_5", "would_include_yn", "comments"])
        for t in tasks:
            # condition is recorded so analysis can unblind after collection
            w.writerow(["", t["prcs_id"], "A", t["option_1"]["condition"], "", "", "", "", ""])
            w.writerow(["", t["prcs_id"], "B", t["option_2"]["condition"], "", "", "", "", ""])

    log.info("Built study: %d tasks -> %s", len(tasks), out)
    return {"n_tasks": len(tasks), "out": str(out)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the user-study packet (Step 4).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--out", default="data/userstudy")
    ap.add_argument("--max-items", type=int, default=20)
    args = ap.parse_args()
    s = build_study(args.dataset, args.captions, args.out, args.max_items)
    print(f"[+] Built {s['n_tasks']} study tasks -> {s['out']}")
    print("    Fill ratings_template.csv with human subjects (Gate G3), then run ingest_ratings.")


if __name__ == "__main__":
    main()
