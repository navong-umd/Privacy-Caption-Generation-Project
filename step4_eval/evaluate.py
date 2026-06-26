"""
Purpose: STEP 4 - evaluation harness: classification + caption quality + policy compliance.
Input:   --dataset (labels), --captions, --policy, optional --checkpoint (ConvGNN),
         optional --references (human caption refs), optional --reference-policy.
Output:  data/eval/eval_report.json + eval_report.md + caption_rating_sheet.csv (for humans).

Honesty rules:
 - Classification metrics on WEAK labels print under a BOOTSTRAP banner.
 - Caption BLEU/ROUGE are computed ONLY against real human references; with none, the harness
   says "no references" and emits a rating sheet — it never fabricates a score.
 - Policy "completeness" is a real structural check (facts surfaced in the policy), not a quality claim.

Run: python -m step4_eval.evaluate --dataset data/dataset --captions data/captions --policy data/policy
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_json
from pplib.schema import BANNER_BOOTSTRAP
from step4_eval.text_metrics import rouge_l, sentence_bleu

log = get_logger("evaluate")


# ---------- classification ----------
def evaluate_classification(dataset_dir: str, checkpoint: Optional[str]) -> Dict:
    """Run the trained ConvGNN on the test split and score it (if torch + checkpoint present)."""
    try:
        import torch
        from torch_geometric.loader import DataLoader
        from step2_convgnn.data import load_splits
        from step2_convgnn.model import ConvGNNClassifier
        from step2_convgnn.train import _predict
        from step2_convgnn.metrics import multilabel_metrics
        from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
    except Exception as e:  # torch not installed
        return {"status": f"skipped (torch unavailable: {e})"}

    ckpt_path = Path(checkpoint) if checkpoint else None
    if not ckpt_path or not ckpt_path.exists():
        return {"status": "skipped (no checkpoint; train the ConvGNN first)"}

    splits = load_splits(dataset_dir)
    test = splits["test"] or splits["val"] or splits["train"]
    is_weak = any(getattr(g, "label_source", "weak") == "weak" for g in test)
    ckpt = torch.load(ckpt_path, weights_only=False)
    model = ConvGNNClassifier(ckpt["config"])
    model.load_state_dict(ckpt["state_dict"])
    yt_pr, yp_pr, yt_pu, yp_pu = _predict(model, DataLoader(test, batch_size=16), torch.device("cpu"))
    m = {}
    m.update(multilabel_metrics(yt_pr, yp_pr, PRACTICE_LABELS, "practice"))
    m.update(multilabel_metrics(yt_pu, yp_pu, PURPOSE_LABELS, "purpose"))
    return {"status": "ok", "is_weak": is_weak, "n_test": len(test),
            "practice_macro_f1": m["practice_macro_f1"], "purpose_macro_f1": m["purpose_macro_f1"],
            "practice_micro_f1": m["practice_micro_f1"], "purpose_micro_f1": m["purpose_micro_f1"],
            "practice_subset_acc": m["practice_subset_acc"], "purpose_subset_acc": m["purpose_subset_acc"]}


# ---------- caption quality ----------
def evaluate_captions(captions_dir: str, out_dir: Path,
                      references: Optional[str]) -> Dict:
    """BLEU/ROUGE vs human references if given; always emit a human-rating sheet."""
    caps = load_json(Path(captions_dir) / "captions.json")
    refs = load_json(references) if references and Path(references).exists() else {}

    # rating sheet for human evaluators (accuracy/clarity/completeness 1-5)
    with open(out_dir / "caption_rating_sheet.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prcs_id", "caption", "accuracy_1_5", "clarity_1_5", "completeness_1_5", "notes"])
        for c in caps:
            w.writerow([c["prcs_id"], c["caption"].replace("\n", " "), "", "", "", ""])

    if not refs:
        return {"status": "no references — BLEU/ROUGE not computed (rating sheet emitted)",
                "n_captions": len(caps)}

    bleu, rl, n = 0.0, 0.0, 0
    for c in caps:
        r = refs.get(c["prcs_id"])
        if not r:
            continue
        ref_list = r if isinstance(r, list) else [r]
        bleu += sentence_bleu(c["caption"], ref_list)
        rl += rouge_l(c["caption"], ref_list)
        n += 1
    if n == 0:
        return {"status": "references present but no prcs_id overlap", "n_captions": len(caps)}
    return {"status": "ok", "n_scored": n, "bleu4": bleu / n, "rouge_l": rl / n}


# ---------- policy compliance / completeness ----------
def evaluate_compliance(policy_dir: str, reference_policy: Optional[str]) -> Dict:
    """Structural completeness: are detected facts surfaced in each app's policy.md?"""
    summary = load_json(Path(policy_dir) / "policy.json")
    results = {}
    for pkg, info in summary["apps"].items():
        policy_md = (Path(policy_dir) / pkg.replace("/", "_") / "policy.md").read_text(encoding="utf-8").lower()
        facts = info["sections"]["collected"] + info["sections"]["purposes"] + info["sections"]["shared_with"]
        surfaced = sum(1 for fct in facts if str(fct).lower() in policy_md)
        results[pkg] = {"facts": len(facts), "surfaced": surfaced,
                        "completeness": round(surfaced / max(len(facts), 1), 3),
                        "gdpr_reqs": len(info["requirements"]["gdpr"]),
                        "ccpa_reqs": len(info["requirements"]["ccpa"])}
    overall = round(sum(r["completeness"] for r in results.values()) / max(len(results), 1), 3)
    out = {"status": "ok", "overall_completeness": overall, "per_app": results}
    if reference_policy and Path(reference_policy).exists():
        ref = Path(reference_policy).read_text(encoding="utf-8").lower()
        # crude coverage vs a reference policy: fraction of detected categories it also mentions
        cats = {c for info in summary["apps"].values() for c in info["sections"]["collected"]}
        out["reference_coverage"] = round(
            sum(1 for c in cats if c.lower() in ref) / max(len(cats), 1), 3)
    return out


def run(dataset_dir: str, captions_dir: str, policy_dir: str, out_dir: str,
        checkpoint: Optional[str] = None, references: Optional[str] = None,
        reference_policy: Optional[str] = None) -> Dict:
    out = ensure_dir(out_dir)
    report = {
        "classification": evaluate_classification(dataset_dir, checkpoint),
        "captions": evaluate_captions(captions_dir, out, references),
        "compliance": evaluate_compliance(policy_dir, reference_policy),
    }
    cls = report["classification"]
    report["bootstrap"] = bool(cls.get("is_weak")) or report["captions"]["status"].startswith("no references")
    dump_json(report, out / "eval_report.json")
    _write_md(report, out / "eval_report.md")
    _print(report)
    return report


def _write_md(r: Dict, path: Path) -> None:
    L = ["# Evaluation Report", ""]
    if r["bootstrap"]:
        L += [f"> **{BANNER_BOOTSTRAP}**", ""]
    L += ["## Classification (ConvGNN)", "```", json.dumps(r["classification"], indent=2), "```",
          "## Caption quality", "```", json.dumps(r["captions"], indent=2), "```",
          "## Policy completeness / compliance", "```", json.dumps(r["compliance"], indent=2), "```"]
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def _print(r: Dict) -> None:
    print("\n=== Evaluation ===")
    if r["bootstrap"]:
        print(f"  *** {BANNER_BOOTSTRAP} ***")
    c = r["classification"]
    if c.get("status") == "ok":
        print(f"  classification: practice_macro_f1={c['practice_macro_f1']:.3f} "
              f"purpose_macro_f1={c['purpose_macro_f1']:.3f} (n_test={c['n_test']})")
    else:
        print(f"  classification: {c.get('status')}")
    print(f"  captions: {r['captions'].get('status')}")
    print(f"  policy completeness: {r['compliance']['overall_completeness']}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluation harness (Step 4).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--policy", default="data/policy")
    ap.add_argument("--out", default="data/eval")
    ap.add_argument("--checkpoint", default="data/convgnn/best.pt")
    ap.add_argument("--references", default=None, help="human caption references (BLEU/ROUGE)")
    ap.add_argument("--reference-policy", default=None)
    args = ap.parse_args()
    run(args.dataset, args.captions, args.policy, args.out, args.checkpoint,
        args.references, args.reference_policy)


if __name__ == "__main__":
    main()
