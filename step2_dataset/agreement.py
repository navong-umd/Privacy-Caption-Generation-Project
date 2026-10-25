"""
Purpose: G1 helper - inter-annotator agreement on the overlap set, plus the adjudication sheet.
Input:   --a / --b labels files from the two annotators' overlap sheets (ingest_annotations output),
         optional --llm labels file (llm_label output) for human-vs-LLM agreement,
         optional --sheet + --disagreements to write the items the annotators disagree on.
Output:  --out JSON + .md: Cohen's kappa per PAcT label, macro kappa per head, raw agreement.

Agreement on not_personal (the flow carries no personal data) is reported over every shared item;
PAcT kappa is computed only on items both raters judged personal. A label that both raters marked
identically on every item has no defined kappa; it is reported as undefined with its prevalence
and left out of the head macro.
Resolve the disagreement sheet, then ingest it with `--annotator adjudicated --merge`.

Run: python -m step2_dataset.agreement --a kit/overlap_ali.json --b kit/overlap_labmate.json \
         --llm kit/llm_overlap.json --sheet kit/overlap_ali.csv --disagreements kit/adjudicate.csv
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List, Optional

from sklearn.metrics import cohen_kappa_score

from pplib.io_utils import REPO_ROOT, dump_json, get_logger, load_json
from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
from step2_dataset.make_annotation_sheet import KIT_COLUMNS, PRACTICE_COLS, PURPOSE_COLS, write_rows

log = get_logger("agreement")

HEADS = (("practice", PRACTICE_LABELS), ("purpose", PURPOSE_LABELS))


def _same_labels(x: dict, y: dict) -> bool:
    return (x["practice"] == y["practice"] and x["purpose"] == y["purpose"]
            and x.get("not_personal", False) == y.get("not_personal", False))


def _binary_agreement(ya: List[int], yb: List[int]) -> Dict:
    """Raw agreement, prevalence and Cohen's kappa (undefined when both raters are constant)."""
    n = len(ya)
    entry = {"raw_agreement": round(sum(a == b for a, b in zip(ya, yb)) / n, 4),
             "prevalence": round((sum(ya) + sum(yb)) / (2 * n), 4)}
    if len(set(ya) | set(yb)) < 2:
        entry.update({"kappa": None, "undefined": True})
    else:
        entry.update({"kappa": round(float(cohen_kappa_score(ya, yb)), 4), "undefined": False})
    return entry


def pairwise(x: Dict[str, dict], y: Dict[str, dict]) -> Dict:
    """Agreement between two labels files on the items both labeled.

    not_personal is scored on every shared item; PAcT labels only on items both raters judged to
    carry personal data, so agreeing that a flow is not personal does not inflate PAcT kappa."""
    ids = sorted(set(x) & set(y))
    out: Dict = {"n_items": len(ids), "not_personal": None, "n_personal_items": 0, "labels": {},
                 "macro_kappa": {}, "defined_labels": {}, "exact_match": None}
    if not ids:
        return out
    out["not_personal"] = _binary_agreement([int(x[i].get("not_personal", False)) for i in ids],
                                            [int(y[i].get("not_personal", False)) for i in ids])
    personal = [i for i in ids if not x[i].get("not_personal") and not y[i].get("not_personal")]
    out["n_personal_items"] = len(personal)
    for head, names in HEADS:
        defined = []
        for name in names:
            if not personal:
                break
            entry = _binary_agreement([int(name in x[i][head]) for i in personal],
                                      [int(name in y[i][head]) for i in personal])
            if not entry["undefined"]:
                defined.append(entry["kappa"])
            out["labels"][f"{head}_{name}"] = entry
        out["macro_kappa"][head] = round(sum(defined) / len(defined), 4) if defined else None
        out["defined_labels"][head] = len(defined)
    out["exact_match"] = round(sum(_same_labels(x[i], y[i]) for i in ids) / len(ids), 4)
    return out


def disagreement_rows(sheet_csv: str, a: Dict[str, dict], b: Dict[str, dict]) -> List[dict]:
    """Sheet rows (label columns blank) for items whose two labels differ, showing both choices."""
    rows = []
    for r in csv.DictReader(Path(sheet_csv).open(encoding="utf-8")):
        pid = r["prcs_id"]
        if pid not in a or pid not in b or _same_labels(a[pid], b[pid]):
            continue
        row = {**r, **{c: "" for c in PRACTICE_COLS + PURPOSE_COLS},
               "not_personal": "", "annotator": "", "confidence": "", "notes": ""}
        for tag, lab in (("a", a[pid]), ("b", b[pid])):
            row[f"{tag}_practice"] = "not personal" if lab.get("not_personal") else "|".join(lab["practice"])
            row[f"{tag}_purpose"] = "|".join(lab["purpose"])
        rows.append(row)
    return rows


def _render_md(report: Dict) -> str:
    lines = ["# Inter-annotator agreement", ""]
    for pair, res in report["pairs"].items():
        np_ = res["not_personal"] or {}
        lines += [f"## {pair} ({res['n_items']} items, {res['n_personal_items']} judged personal by both)", "",
                  f"Not-personal kappa: {'undefined' if np_.get('undefined') else np_.get('kappa')} "
                  f"(raw agreement {np_.get('raw_agreement')}, prevalence {np_.get('prevalence')}).", "",
                  f"Macro kappa on personal items: practice {res['macro_kappa'].get('practice')}, "
                  f"purpose {res['macro_kappa'].get('purpose')}. Exact match: {res['exact_match']}.", "",
                  "| Label | Kappa | Raw agreement | Prevalence |", "|---|---|---|---|"]
        for name, e in res["labels"].items():
            k = "undefined" if e["undefined"] else e["kappa"]
            lines.append(f"| {name} | {k} | {e['raw_agreement']} | {e['prevalence']} |")
        lines.append("")
    return "\n".join(lines)


def agreement(a_json: str, b_json: str, out_json: str, llm_json: Optional[str] = None,
              sheet_csv: Optional[str] = None, disagreements_csv: Optional[str] = None) -> Dict:
    a, b = load_json(a_json), load_json(b_json)
    report = {"inputs": {"a": a_json, "b": b_json, "llm": llm_json}, "pairs": {"a_vs_b": pairwise(a, b)}}
    if llm_json:
        llm = load_json(llm_json)
        report["pairs"]["a_vs_llm"] = pairwise(a, llm)
        report["pairs"]["b_vs_llm"] = pairwise(b, llm)
    if sheet_csv and disagreements_csv:
        rows = disagreement_rows(sheet_csv, a, b)
        extra = ["a_practice", "a_purpose", "b_practice", "b_purpose"]
        write_rows(Path(disagreements_csv), KIT_COLUMNS + extra, rows)
        report["disagreements"] = {"path": disagreements_csv, "n_items": len(rows)}
    dump_json(report, out_json)
    Path(out_json).with_suffix(".md").write_text(_render_md(report), encoding="utf-8")
    log.info("Agreement on %d overlap items -> %s", report["pairs"]["a_vs_b"]["n_items"], out_json)
    return report


def main() -> None:
    ap = argparse.ArgumentParser(description="Inter-annotator agreement + adjudication sheet (G1).")
    ap.add_argument("--a", required=True, help="first annotator's overlap labels file")
    ap.add_argument("--b", required=True, help="second annotator's overlap labels file")
    ap.add_argument("--llm", default=None, help="LLM labels file for the same items (optional)")
    ap.add_argument("--sheet", default=None, help="an overlap sheet (source of the item context columns)")
    ap.add_argument("--disagreements", default=None, help="write items to adjudicate to this CSV")
    ap.add_argument("--out", default=str(REPO_ROOT / "experiments" / "AGREEMENT.json"))
    args = ap.parse_args()
    r = agreement(args.a, args.b, args.out, args.llm, args.sheet, args.disagreements)
    ab = r["pairs"]["a_vs_b"]
    print(f"[+] {ab['n_items']} items  macro kappa {ab['macro_kappa']}  exact match {ab['exact_match']}")
    if "disagreements" in r:
        print(f"    {r['disagreements']['n_items']} items to adjudicate -> {r['disagreements']['path']}")


if __name__ == "__main__":
    main()
