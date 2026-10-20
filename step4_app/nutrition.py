"""
Purpose: STAGE 8 - distil per-app Privacy NUTRITION FACTS (privacy facts + security-risk
         facts) from the ADPPG dataset + captions, for the Privacy Nutrition Facts app.
Input:   --dataset data/dataset (adppg.jsonl facts+labels) + --captions data/captions.
Output:  data/nutrition/<package>/nutrition.json + nutrition.md, and nutrition_index.json.

Privacy facts = what data is collected, what leaves the device & to whom, and the purposes.
Security-risk facts = a TRANSPARENT, rule-based indicator (network egress, identifier access,
sensitive categories, LINDDUN threats). It is NOT a security audit; when any input label is
WEAK it carries the BOOTSTRAP banner. The scoring formula is documented in `_risk()`.

Run: python -m step4_app.nutrition --dataset data/dataset --captions data/captions --out data/nutrition
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_yaml
from pplib.schema import BANNER_BOOTSTRAP, PRACTICE_LABELS, PURPOSE_LABELS, is_gold

log = get_logger("nutrition")
REPO_ROOT = Path(__file__).resolve().parent.parent

# Categories that are sensitive personal data (drive the risk indicator + the "sensitive" list).
SENSITIVE = {
    "LOCATION_INFORMATION", "CONTACT_INFORMATION", "SMS_MMS", "CALENDAR_INFORMATION",
    "UNIQUE_IDENTIFIER", "PHONE_INFORMATION", "AUDIO_INPUT_OUTPUT", "ACCOUNT_INFORMATION",
    "BLUETOOTH_INFORMATION", "BROWSER_INFORMATION", "IMAGE",
}


def _human(cat: str, pi_names: Dict[str, str]) -> str:
    if not cat:
        return "personal data"
    return pi_names.get(cat, cat.replace("_", " ").title())


def _risk(facts: List[dict]) -> dict:
    """Transparent heuristic risk indicator (0-100) from detected flows. NOT an audit.

    +25 if any data leaves the device (network/ipc sink);
    +20 if a device identifier is accessed;
    +10 per distinct other sensitive category (capped +30);
    +15 if any flow's purpose is Advertisement; +10 if Analytics.
    level: <25 Low, 25-59 Medium, >=60 High.
    """
    score, factors = 0, []
    egress = [f for f in facts if f["sink_type"] in ("network", "ipc")]
    if egress:
        score += 25
        factors.append(f"{len(egress)} flow(s) send data off-device")
    if any(f["category"] == "UNIQUE_IDENTIFIER" for f in facts):
        score += 20
        factors.append("accesses a device identifier")
    other_sens = {f["category"] for f in facts
                  if f["category"] in SENSITIVE and f["category"] != "UNIQUE_IDENTIFIER"}
    if other_sens:
        bump = min(30, 10 * len(other_sens))
        score += bump
        factors.append(f"{len(other_sens)} sensitive data categor(y/ies) accessed")
    purposes = {p for f in facts for p in f["purpose"]}
    if "Advertisement" in purposes:
        score += 15
        factors.append("data used for advertising")
    if "Analytics" in purposes:
        score += 10
        factors.append("data used for analytics")
    score = min(100, score)
    level = "Low" if score < 25 else ("Medium" if score < 60 else "High")
    threats = sorted({t for f in facts for t in (f.get("privacy_threat") or "").split(";") if t})
    return {
        "score": score, "level": level, "factors": factors,
        "network_egress_flows": len(egress),
        "identifier_access_flows": sum(1 for f in facts if f["category"] == "UNIQUE_IDENTIFIER"),
        "linddun_threats": threats,
    }


def _app_facts(records: Dict[str, dict]) -> Dict[str, List[dict]]:
    by_app: Dict[str, List[dict]] = defaultdict(list)
    for pid, rec in records.items():
        labels = rec.get("labels", {})
        by_app[rec["app_package"]].append({
            "prcs_id": pid,
            "category": rec.get("pi_category", "") or rec.get("pi_type", ""),
            "sink_type": rec.get("sink_type", ""),
            "sink_label": rec.get("sink_label", "") or rec.get("sink_type", ""),
            "privacy_threat": rec.get("privacy_threat", ""),
            "practice": labels.get("practice", []),
            "purpose": labels.get("purpose", []),
            "label_source": labels.get("label_source", "weak"),
        })
    return by_app


def build_nutrition(dataset_dir: str, captions_dir: str | None, out_dir: str,
                    cmap_path: str | None = None) -> dict:
    """Build per-app Privacy Nutrition Facts. Returns the index summary."""
    cmap = load_yaml(cmap_path or REPO_ROOT / "configs" / "gdpr_ccpa_map.yaml")
    pi_names = cmap.get("pi_names", {})
    records = {}
    for line in (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        records[r["prcs_id"]] = r
    captions = {}
    if captions_dir and (Path(captions_dir) / "captions.json").exists():
        captions = {c["prcs_id"]: c for c in
                    json.loads((Path(captions_dir) / "captions.json").read_text(encoding="utf-8"))}

    out = ensure_dir(out_dir)
    index = {"apps": {}, "banner": ""}
    any_weak = False
    for pkg, facts in _app_facts(records).items():
        weak = any(not is_gold(f["label_source"]) for f in facts)
        any_weak = any_weak or weak

        collected = Counter(f["category"] for f in facts if f["category"])
        shared = defaultdict(set)
        for f in facts:
            if "Sharing" in f["practice"] and f["sink_type"] in ("network", "ipc"):
                shared[f["category"] or "personal data"].add(f["sink_label"])
        purposes = Counter(p for f in facts for p in f["purpose"])
        practices = Counter(p for f in facts for p in f["practice"])
        third_parties = sorted({f["sink_label"] for f in facts
                                if ({"Advertisement", "Analytics"} & set(f["purpose"]))
                                and f["sink_type"] in ("network", "ipc")   # only off-device recipients
                                and f.get("sink_label")})
        risk = _risk(facts)
        risk["sensitive_categories"] = sorted({_human(c, pi_names) for c in collected
                                               if c in SENSITIVE})
        caps = [captions[f["prcs_id"]]["caption"].replace("\n", " ")
                for f in facts if f["prcs_id"] in captions][:12]

        label = {
            "app_package": pkg, "weak": weak, "n_prcs": len(facts),
            "data_collected": [{"category": _human(c, pi_names), "raw": c, "count": n}
                               for c, n in collected.most_common()],
            "data_shared_offdevice": [{"category": _human(c, pi_names),
                                       "recipients": sorted(r), "count": len(r)}
                                      for c, r in sorted(shared.items())],
            "purposes": {p: purposes.get(p, 0) for p in PURPOSE_LABELS},
            "practices": {p: practices.get(p, 0) for p in PRACTICE_LABELS},
            "third_parties": third_parties,
            "security_risk": risk,
            "captions": caps,
            "banner": BANNER_BOOTSTRAP if weak else "",
        }
        app_out = ensure_dir(out / pkg.replace("/", "_"))
        dump_json(label, app_out / "nutrition.json")
        (app_out / "nutrition.md").write_text(_render_md(label), encoding="utf-8")
        index["apps"][pkg] = {"risk_level": risk["level"], "risk_score": risk["score"],
                              "n_prcs": len(facts), "weak": weak}
    index["banner"] = BANNER_BOOTSTRAP if any_weak else ""
    dump_json(index, out / "nutrition_index.json")
    log.info("Built nutrition facts for %d app(s) -> %s", len(index["apps"]), out)
    return index


def _render_md(label: dict) -> str:
    """A printable 'nutrition label' in Markdown."""
    r = label["security_risk"]
    lines = [f"# Privacy Nutrition Facts — {label['app_package']}", ""]
    if label["weak"]:
        lines += [f"> **{label['banner']}**", ""]
    lines += [f"**Risk indicator:** {r['level']} ({r['score']}/100) — heuristic, not a security audit.",
              ""]
    if r["factors"]:
        lines += ["_Why:_ " + "; ".join(r["factors"]) + ".", ""]
    lines += [f"Based on **{label['n_prcs']}** permission-requiring code segment(s).", ""]
    lines += ["## Data collected"]
    lines += [f"- {d['category']} ({d['count']})" for d in label["data_collected"]] or ["- (none detected)"]
    lines += ["", "## Data shared off-device"]
    if label["data_shared_offdevice"]:
        for d in label["data_shared_offdevice"]:
            lines.append(f"- {d['category']} → {', '.join(d['recipients'])}")
    else:
        lines.append("- (nothing detected leaving the device)")
    lines += ["", "## Purposes",
              *[f"- {p}: {n}" for p, n in label["purposes"].items() if n], ""]
    if label["third_parties"]:
        lines += ["## Third parties (ad / analytics)",
                  *[f"- {t}" for t in label["third_parties"]], ""]
    if r["linddun_threats"]:
        lines += ["## LINDDUN privacy threats", "- " + ", ".join(r["linddun_threats"]), ""]
    if label["captions"]:
        lines += ["## In plain language", *[f"- {c}" for c in label["captions"]]]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Build Privacy Nutrition Facts (Stage 8).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--out", default="data/nutrition")
    ap.add_argument("--map", default="configs/gdpr_ccpa_map.yaml")
    args = ap.parse_args()
    idx = build_nutrition(args.dataset, args.captions, args.out, args.map)
    print("\n=== Privacy Nutrition Facts ===")
    if idx["banner"]:
        print(f"  {idx['banner']}")
    for pkg, info in idx["apps"].items():
        tag = " [WEAK]" if info["weak"] else ""
        print(f"  {pkg}{tag}: risk={info['risk_level']} ({info['risk_score']}/100) "
              f"n_prcs={info['n_prcs']}")


if __name__ == "__main__":
    main()
