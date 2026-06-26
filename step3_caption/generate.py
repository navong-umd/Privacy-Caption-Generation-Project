"""
Purpose: STEP 3 - generate a human-readable privacy caption per PRCS.
Input:   --dataset data/dataset (adppg.jsonl), --config configs/llm.yaml,
         optional --predictions (ConvGNN outputs) to caption predicted labels instead of stored ones.
Output:  data/captions/captions.json (+ captions.csv): LLM caption + Code2Seq baseline per PRCS.

Provider defaults to the OFFLINE mock (no network/keys). Captions derived from WEAK labels
inherit `label_source: weak` so downstream/eval can banner them.

Run: python -m step3_caption.generate --dataset data/dataset --out data/captions
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_json, load_yaml
from pplib.schema import BANNER_WEAK
from step3_caption.code2seq_baseline import BASELINE_TAG, Code2SeqBaseline
from step3_caption.llm_interface import get_provider

log = get_logger("caption")


def build_prompt(evidence: Dict, icl: List[Dict]) -> str:
    """Build an ICL prompt for a real LLM (the mock ignores it and uses evidence directly)."""
    shots = "\n".join(
        f"- PI={e['pi']}, practice={e['practice']}, purpose={e['purpose']} -> {e['caption']}"
        for e in icl)
    return (
        "You write short, accurate, user-facing privacy captions (4-5 short lines).\n"
        "Given the analyzed privacy behavior of an Android code segment, write one caption.\n"
        f"Examples:\n{shots}\n\n"
        f"Now write a caption for:\n"
        f"  personal_data: {evidence.get('pi_type') or evidence.get('category')}\n"
        f"  practice: {evidence.get('practice')}\n"
        f"  purpose: {evidence.get('purpose')}\n"
        f"  sink: {evidence.get('sink_type')} ({evidence.get('sink_api')})\n"
        f"  source_api: {evidence.get('source_api')}\n"
        "Caption:")


def _evidence(rec: Dict) -> Dict:
    labels = rec.get("labels", {})
    return {
        "category": rec.get("pi_category", ""), "pi_type": rec.get("pi_type", ""),
        "practice": labels.get("practice", []), "purpose": labels.get("purpose", []),
        "sink_type": rec.get("sink_type", ""), "sink_api": rec.get("sink_api", ""),
        "source_api": rec.get("source_api", ""),
        "privacy_threat": rec.get("privacy_threat", ""),
        "app_package": rec.get("app_package", ""),
    }


def generate_captions(dataset_dir: str, out_dir: str, config: Optional[str] = None,
                      predictions: Optional[str] = None) -> List[Dict]:
    """Generate captions for every PRCS in the dataset."""
    cfg = load_yaml(config) if config else load_yaml(Path("configs/llm.yaml"))
    provider = get_provider(cfg)
    icl = cfg.get("icl_examples", [])
    baseline = Code2SeqBaseline()

    records = [json.loads(l) for l in
               (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]
    preds = load_json(predictions) if predictions and Path(predictions).exists() else {}

    out: List[Dict] = []
    for rec in records:
        if rec["prcs_id"] in preds:                 # use model-predicted labels if provided
            rec = {**rec, "labels": {**rec.get("labels", {}), **preds[rec["prcs_id"]]}}
        ev = _evidence(rec)
        caption = provider.generate(build_prompt(ev, icl), ev)
        label_source = rec.get("labels", {}).get("label_source", "weak")
        out.append({
            "prcs_id": rec["prcs_id"], "app_package": rec.get("app_package", ""),
            "caption": caption, "baseline_caption": baseline.caption(rec),
            "baseline_tag": BASELINE_TAG, "provider": cfg.get("provider", "mock"),
            "label_source": label_source,
            "weak_banner": BANNER_WEAK if label_source == "weak" else "",
        })

    out_p = ensure_dir(out_dir)
    dump_json(out, out_p / "captions.json")
    pd.DataFrame([{"prcs_id": c["prcs_id"], "caption": c["caption"].replace("\n", " "),
                   "baseline": c["baseline_caption"], "label_source": c["label_source"]}
                  for c in out]).to_csv(out_p / "captions.csv", index=False, encoding="utf-8")
    log.info("Generated %d captions (provider=%s)", len(out), cfg.get("provider", "mock"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate privacy captions (Step 3).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--out", default="data/captions")
    ap.add_argument("--config", default="configs/llm.yaml")
    ap.add_argument("--predictions", default=None)
    args = ap.parse_args()
    caps = generate_captions(args.dataset, args.out, args.config, args.predictions)
    weak = any(c["label_source"] == "weak" for c in caps)
    print("\n=== Captions ===")
    if weak:
        print(f"  [{BANNER_WEAK}]")
    for c in caps[:3]:
        print(f"\n  {c['prcs_id']} ({c['app_package']}):")
        for line in c["caption"].splitlines():
            print(f"    {line}")
        print(f"    [baseline] {c['baseline_caption']}")


if __name__ == "__main__":
    main()
