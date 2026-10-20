"""
Purpose: STEP 3 - assemble per-app privacy NOTICE + POLICY from PRCS captions and facts.
Input:   --dataset data/dataset (facts) + --captions data/captions (caption text) +
         --map configs/gdpr_ccpa_map.yaml.
Output:  data/policy/<package>/notice.md, policy.md, and data/policy/policy.json (structured).

Sections: what is collected / how it is used / who it is shared with / purposes, each mapped to
GDPR & CCPA obligations. WEAK-labeled inputs produce a clearly banner-marked DRAFT.

Run: python -m step3_policy.assemble --dataset data/dataset --captions data/captions --out data/policy
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_yaml
from pplib.schema import label_banner

log = get_logger("policy")
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_records(dataset_dir: Path) -> Dict[str, dict]:
    out = {}
    for line in (dataset_dir / "adppg.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        out[r["prcs_id"]] = r
    return out


def _collect_requirements(facts: List[dict], cmap: dict) -> Dict[str, List[str]]:
    """Union the GDPR/CCPA obligations triggered by an app's facts."""
    gdpr, ccpa = set(), set()
    sens = cmap.get("sensitive", {})
    for f in facts:
        for p in f["practice"]:
            req = cmap.get("practice", {}).get(p, {})
            gdpr.update(req.get("gdpr", [])); ccpa.update(req.get("ccpa", []))
        for p in f["purpose"]:
            req = cmap.get("purpose", {}).get(p, {})
            gdpr.update(req.get("gdpr", [])); ccpa.update(req.get("ccpa", []))
        if f["category"] in sens.get("categories", []):
            gdpr.update(sens.get("gdpr", [])); ccpa.update(sens.get("ccpa", []))
    return {"gdpr": sorted(gdpr), "ccpa": sorted(ccpa)}


def _app_section_data(facts: List[dict], cmap: dict) -> dict:
    pi_names = cmap.get("pi_names", {})
    collected = sorted({pi_names.get(f["category"], f["category"] or "personal data")
                        for f in facts if f["category"] or f["pi_type"]})
    purposes = sorted({p for f in facts for p in f["purpose"]})
    shared_with = sorted({f["sink_label"] for f in facts
                          if "Sharing" in f["practice"] and f.get("sink_label")})
    return {"collected": collected, "purposes": purposes, "shared_with": shared_with}


def _render_notice(pkg: str, sec: dict, captions: List[str], banner: str) -> str:
    lines = [f"# Privacy Notice — {pkg}", ""]
    if banner:
        lines += [f"> **DRAFT — {banner}**", ""]
    lines += ["## What we collect", *([f"- {c}" for c in sec["collected"]] or ["- (none detected)"]), ""]
    lines += ["## How it is used",
              *([f"- {p}" for p in sec["purposes"]] or ["- (unspecified)"]), ""]
    lines += ["## Who it is shared with",
              *([f"- {s}" for s in sec["shared_with"]] or ["- (not shared off-device)"]), ""]
    lines += ["## In plain language"]
    lines += [f"- {c}" for c in captions]
    return "\n".join(lines) + "\n"


def _render_policy(pkg: str, sec: dict, reqs: dict, captions: List[str], banner: str) -> str:
    lines = [f"# Privacy Policy — {pkg}", ""]
    if banner:
        lines += [f"> **DRAFT — {banner}.** Not legal advice; verify before publishing.", ""]
    lines += ["## 1. Personal data we process",
              *([f"- {c}" for c in sec["collected"]] or ["- (none detected)"]), ""]
    lines += ["## 2. Purposes", *([f"- {p}" for p in sec["purposes"]] or ["- (unspecified)"]), ""]
    lines += ["## 3. Recipients / sharing",
              *([f"- {s}" for s in sec["shared_with"]] or ["- We do not share data off-device."]), ""]
    lines += ["## 4. Behavior summary (auto-generated captions)"]
    lines += [f"- {c}" for c in captions]
    lines += ["", "## 5. Regulatory mapping", "", "### GDPR",
              *([f"- {g}" for g in reqs["gdpr"]] or ["- (none triggered)"]), "", "### CCPA",
              *([f"- {c}" for c in reqs["ccpa"]] or ["- (none triggered)"])]
    return "\n".join(lines) + "\n"


def assemble(dataset_dir: str, captions_dir: str, out_dir: str,
             cmap_path: str | None = None) -> dict:
    """Build per-app notice + policy; returns a structured summary."""
    cmap = load_yaml(cmap_path or REPO_ROOT / "configs" / "gdpr_ccpa_map.yaml")
    records = _load_records(Path(dataset_dir))
    captions = {c["prcs_id"]: c for c in
                json.loads((Path(captions_dir) / "captions.json").read_text(encoding="utf-8"))}

    by_app: Dict[str, List[dict]] = defaultdict(list)
    for pid, rec in records.items():
        labels = rec.get("labels", {})
        by_app[rec["app_package"]].append({
            "prcs_id": pid, "category": rec.get("pi_category", ""),
            "pi_type": rec.get("pi_type", ""), "sink_type": rec.get("sink_type", ""),
            "sink_label": rec.get("sink_label", "") or rec.get("sink_type", ""),
            "practice": labels.get("practice", []), "purpose": labels.get("purpose", []),
            "label_source": labels.get("label_source", "weak"),
        })

    out = ensure_dir(out_dir)
    summary = {"apps": {}}
    for pkg, facts in by_app.items():
        banner = "; ".join(sorted({label_banner(f["label_source"]) for f in facts} - {""}))
        weak = bool(banner)
        sec = _app_section_data(facts, cmap)
        reqs = _collect_requirements(facts, cmap)
        caps = [captions[f["prcs_id"]]["caption"].replace("\n", " ")
                for f in facts if f["prcs_id"] in captions]
        app_out = ensure_dir(out / pkg.replace("/", "_"))
        (app_out / "notice.md").write_text(_render_notice(pkg, sec, caps, banner), encoding="utf-8")
        (app_out / "policy.md").write_text(_render_policy(pkg, sec, reqs, caps, banner), encoding="utf-8")
        summary["apps"][pkg] = {"sections": sec, "requirements": reqs,
                                "n_prcs": len(facts), "weak": weak}
    dump_json(summary, out / "policy.json")
    log.info("Assembled policies for %d app(s) -> %s", len(by_app), out)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Assemble privacy notice + policy (Step 3).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--out", default="data/policy")
    ap.add_argument("--map", default="configs/gdpr_ccpa_map.yaml")
    args = ap.parse_args()
    s = assemble(args.dataset, args.captions, args.out, args.map)
    print("\n=== Policy assembly ===")
    for pkg, info in s["apps"].items():
        tag = " [DRAFT/WEAK]" if info["weak"] else ""
        print(f"  {pkg}{tag}: collects={info['sections']['collected']} "
              f"purposes={info['sections']['purposes']} "
              f"GDPR_reqs={len(info['requirements']['gdpr'])} CCPA_reqs={len(info['requirements']['ccpa'])}")


if __name__ == "__main__":
    main()
