"""
Purpose: ABLATION - does the PPG privacy overlay actually help PAcT classification?
Input:   --config configs/convgnn.yaml, --dataset data/dataset.
Output:  data/ablation/ablation.json + .md comparing FULL PPG vs APG-ONLY node features.

Trains the SAME ConvGNN twice on the SAME splits/seed, changing only the node features:
  - FULL    : node-type embedding + privacy overlay (is_source/is_sink/permission/sink-type/PI).
  - APG-ONLY: node-type embedding + graph structure, privacy overlay vector ZEROED.
The test macro-F1 delta isolates the contribution of the privacy overlay (the build's novelty).
If the TEST split is WEAK-labeled the result carries the BOOTSTRAP banner (directional only).

Run: python -m step2_convgnn.ablation --config configs/convgnn.yaml --dataset data/dataset
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict

from pplib.io_utils import dump_json, ensure_dir, get_logger
from pplib.schema import BANNER_BOOTSTRAP
from step2_convgnn.train import train

log = get_logger("ablation")


def run_ablation(config: str, dataset_dir: str, out_dir: str, epochs: int | None = None) -> Dict:
    """Train FULL vs APG-ONLY and return the comparison report."""
    out = ensure_dir(out_dir)
    full = train(config, dataset_dir, str(out / "full"), epochs, privacy_features=True)
    apg = train(config, dataset_dir, str(out / "apg_only"), epochs, privacy_features=False)

    def m(res, k):
        return round(res["test"][k], 4)

    rows = {}
    for k in ("practice_macro_f1", "purpose_macro_f1", "practice_micro_f1", "purpose_micro_f1"):
        rows[k] = {"full_ppg": m(full, k), "apg_only": m(apg, k),
                   "delta": round(m(full, k) - m(apg, k), 4)}
    overall_full = round((full["test"]["practice_macro_f1"] + full["test"]["purpose_macro_f1"]) / 2, 4)
    overall_apg = round((apg["test"]["practice_macro_f1"] + apg["test"]["purpose_macro_f1"]) / 2, 4)
    report = {
        "banner": BANNER_BOOTSTRAP if full["is_weak"] else "",
        "is_weak": full["is_weak"],
        "metrics": rows,
        "overall_macro_f1": {"full_ppg": overall_full, "apg_only": overall_apg,
                             "delta": round(overall_full - overall_apg, 4)},
        "privacy_overlay_helps": overall_full >= overall_apg,
    }
    dump_json(report, out / "ablation.json")
    (out / "ablation.md").write_text(_render_md(report), encoding="utf-8")
    log.info("Ablation: FULL macro-F1=%.3f vs APG-only=%.3f (delta %+.3f)",
             overall_full, overall_apg, report["overall_macro_f1"]["delta"])
    return report


def _render_md(r: Dict) -> str:
    lines = ["# Ablation — PPG privacy overlay vs APG-only", ""]
    if r["banner"]:
        lines += [f"> **{r['banner']}** — directional only until a human-labeled test split.", ""]
    lines += ["| Metric | Full PPG | APG-only | Δ (overlay) |", "|---|--:|--:|--:|"]
    for k, v in r["metrics"].items():
        lines.append(f"| {k} | {v['full_ppg']} | {v['apg_only']} | {v['delta']:+} |")
    o = r["overall_macro_f1"]
    lines += ["", f"**Overall macro-F1:** full PPG **{o['full_ppg']}** vs APG-only {o['apg_only']} "
              f"(Δ **{o['delta']:+}**). Privacy overlay helps: **{r['privacy_overlay_helps']}**."]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="PPG-vs-APG-only ablation (ConvGNN).")
    ap.add_argument("--config", default="configs/convgnn.yaml")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--out", default="data/ablation")
    ap.add_argument("--epochs", type=int, default=None)
    args = ap.parse_args()
    r = run_ablation(args.config, args.dataset, args.out, args.epochs)
    print("\n=== Ablation: PPG overlay vs APG-only ===")
    if r["banner"]:
        print(f"  *** {r['banner']} ***")
    o = r["overall_macro_f1"]
    print(f"  overall macro-F1: full PPG={o['full_ppg']}  APG-only={o['apg_only']}  delta={o['delta']:+}")
    for k, v in r["metrics"].items():
        print(f"    {k:22} full={v['full_ppg']:.3f}  apg={v['apg_only']:.3f}  d={v['delta']:+.3f}")


if __name__ == "__main__":
    main()
