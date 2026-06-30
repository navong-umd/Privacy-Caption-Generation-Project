"""
Apply LLM-annotated Practice/Purpose labels to the G1 annotation sheets.

Pipeline:
  data/_annot_rows.json   gid -> {sheet, prcs_id, ...}   (the rows we sent to the LLM)
  data/_merged_labels.json [{gid, prcs_id, practice[], purpose[], agree, needs_human, ...}]
        (output of the two-pass LLM annotation workflow, merged)

For each sheet it:
  1. fills the P_*/U_* columns of <sheet>/annotation_sheet.csv from the merged labels,
  2. writes <sheet_dir>/human_labels.json  ({prcs_id: {practice, purpose}}),
  3. writes data/_review_shortlist.csv + .md  (only the rows where the two passes
     disagreed or were low-confidence -> the human spot-check list).

These are LLM labels, NOT human ground truth. The shortlist is what a human should
review/adjudicate so we can report human-LLM agreement and disclose the method.

Run:  python tools/apply_annotations.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRACTICE = ["Processing", "Collecting", "Sharing", "Other"]
PURPOSE = ["Functionality", "Advertisement", "Analytics", "Other"]

SHEETS = {
    "starter": ROOT / "data" / "starter" / "annotation_sheet.csv",
    "eval": ROOT / "data" / "eval_run" / "annotation_sheet.csv",
}


def main() -> None:
    rowmap = {r["gid"]: r for r in json.loads((ROOT / "data" / "_annot_rows.json").read_text("utf-8"))}
    merged = json.loads((ROOT / "data" / "_merged_labels.json").read_text("utf-8"))
    # merged may be {"rows": [...]} or a bare list
    mrows = merged["rows"] if isinstance(merged, dict) else merged

    # gid -> labels
    by_gid = {m["gid"]: m for m in mrows}

    # group label decisions per sheet, keyed by prcs_id
    per_sheet: dict[str, dict[str, dict]] = {s: {} for s in SHEETS}
    shortlist = []
    for gid, src in rowmap.items():
        m = by_gid.get(gid)
        if not m or m.get("missing"):
            shortlist.append({**src, "reason": "no LLM label (missing)",
                              "practice": "", "purpose": "", "practice_b": "", "purpose_b": ""})
            continue
        practice = m.get("practice", []) or []
        purpose = m.get("purpose", []) or []
        per_sheet[src["sheet"]][src["prcs_id"]] = {"practice": practice, "purpose": purpose}
        if m.get("needs_human"):
            shortlist.append({
                "sheet": src["sheet"], "prcs_id": src["prcs_id"], "app": src["app"],
                "cls": src["cls"], "method": src["method"],
                "source_api": src["source_api"], "sink_api": src["sink_api"],
                "sink_type": src["sink_type"], "pi_type": src["pi_type"],
                "reason": ("passes disagree" if not m.get("agree") else "low confidence"),
                "practice": "|".join(practice), "purpose": "|".join(purpose),
                "practice_b": "|".join(m.get("practice_b", []) or []),
                "purpose_b": "|".join(m.get("purpose_b", []) or []),
                "why": m.get("why", ""), "why_b": m.get("why_b", ""),
            })

    # 1 + 2: fill each sheet's CSV and write human_labels.json
    for sheet, path in SHEETS.items():
        labels = per_sheet[sheet]
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)
        filled = 0
        for r in rows:
            lab = labels.get(r["prcs_id"])
            if not lab:
                continue
            for p in PRACTICE:
                r[f"P_{p}"] = "1" if p in lab["practice"] else ""
            for u in PURPOSE:
                r[f"U_{u}"] = "1" if u in lab["purpose"] else ""
            filled += 1
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)

        human = {pid: {"practice": v["practice"], "purpose": v["purpose"]} for pid, v in labels.items()}
        hpath = path.parent / "human_labels.json"
        hpath.write_text(json.dumps(human, indent=2), encoding="utf-8")
        print(f"[{sheet}] filled {filled}/{len(rows)} rows in {path.name} -> {hpath.name} ({len(human)} labels)")

    # 3: shortlist
    sl_csv = ROOT / "data" / "_review_shortlist.csv"
    cols = ["sheet", "prcs_id", "app", "cls", "method", "source_api", "sink_api",
            "sink_type", "pi_type", "reason", "practice", "purpose", "practice_b", "purpose_b", "why", "why_b"]
    with sl_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(shortlist)

    sl_md = ROOT / "data" / "_review_shortlist.md"
    with sl_md.open("w", encoding="utf-8") as f:
        f.write(f"# Human review shortlist ({len(shortlist)} rows)\n\n")
        f.write("Rows where the two LLM passes disagreed or were low-confidence. "
                "Review only these; everything else both passes agreed on.\n\n")
        for s in shortlist:
            f.write(f"## {s.get('sheet')} · `{s['prcs_id']}` — {s.get('app','')}\n")
            f.write(f"- {s.get('cls','')}->{s.get('method','')}  |  sink_type=`{s.get('sink_type','')}`  pi=`{s.get('pi_type','')}`\n")
            f.write(f"- source `{s.get('source_api','')}`  ->  sink `{s.get('sink_api','')}`\n")
            f.write(f"- **reason:** {s.get('reason','')}\n")
            f.write(f"- pass A: practice=[{s.get('practice','')}] purpose=[{s.get('purpose','')}] — {s.get('why','')}\n")
            f.write(f"- pass B: practice=[{s.get('practice_b','')}] purpose=[{s.get('purpose_b','')}] — {s.get('why_b','')}\n\n")

    print(f"[shortlist] {len(shortlist)} rows -> {sl_csv.name} + {sl_md.name}")


if __name__ == "__main__":
    main()
