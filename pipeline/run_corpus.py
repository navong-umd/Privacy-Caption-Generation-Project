"""
Purpose: Build ONE ADPPG dataset from a CORPUS of APKs (multi-app, leakage-free splits).
Input:   --apks DIR (folder of .apk) or --apg-dirs "d1,d2" (pre-built APG dirs); --out.
Output:  <out>/dataset (combined ADPPG) + captions + policy + eval over all apps.

Each APK is processed independently (APG -> PPG -> PRCS) so only one app's graph is in memory
at a time — this scales to large real APKs. All PRCS are aggregated into one dataset whose
train/val/test split is grouped BY APK (no leakage), which is what the ConvGNN needs.

Run: python -m pipeline.run_corpus --apks data/corpus --out data/corpus_run --precision
"""
from __future__ import annotations

import argparse
import gc
import glob
from dataclasses import asdict
from pathlib import Path
from typing import Dict, List, Optional

from pplib.apg_model import APG, load_apg
from pplib.io_utils import dump_json, ensure_dir, get_logger, load_yaml
from stage4_ppg.build_ppg import PPGBuilder
from step2_prcs.extract_prcs import extract_from_graph
from step2_dataset.build_dataset import build_dataset
from step3_caption.generate import generate_captions
from step3_policy.assemble import assemble
from step4_eval.evaluate import run as run_eval
from pipeline.run_pipeline import _precision_config

log = get_logger("run_corpus")


def run_corpus(out_dir: str, apks_dir: Optional[str] = None,
               apg_dirs: Optional[List[str]] = None, ppg_config: str = "configs/ppg.yaml",
               llm_config: str = "configs/llm.yaml", precision: bool = True,
               train_model: bool = True, epochs: int = 40) -> Dict:
    """Process every APK/APG into a shared PRCS pool, then build one dataset + downstream."""
    out = ensure_dir(out_dir)
    cfg_path = _precision_config(ppg_config, out) if precision else ppg_config
    cfg = load_yaml(cfg_path)

    # resolve work items: (name, apg_dir_or_apk, is_apk)
    items: List[tuple] = []
    if apks_dir:
        for apk in sorted(glob.glob(str(Path(apks_dir) / "*.apk"))):
            items.append((Path(apk).stem, apk, True))
    for d in (apg_dirs or []):
        items.append((Path(d).name, d, False))
    if not items:
        raise ValueError("provide --apks DIR or --apg-dirs")

    prcs_all = ensure_dir(out / "prcs_all")
    per_app: Dict[str, dict] = {}
    for name, src, is_apk in items:
        log.info("=== processing %s ===", name)
        try:  # one bad/oversized APK must not kill the whole corpus run
            # Build APG -> PPG -> PRCS entirely in memory; persist ONLY the small PRCS JSONs.
            if is_apk:
                from adapters.run_apg_csv import run_apg_csv
                apg = run_apg_csv(src, None, write=False)   # no ~1 GB APG CSVs on disk
            else:
                apg = load_apg(src)
            builder = PPGBuilder(cfg)
            builder.build(apg)
            records = extract_from_graph(
                builder.G, [asdict(tp) for tp in builder.taint_paths])
            for r in records:
                dump_json({k: getattr(r, k) for k in r.__dataclass_fields__},
                          prcs_all / f"{r.prcs_id}.json")
            per_app[name] = {**builder.summary(), "package": apg.app_id.split("@")[0],
                             "prcs": len(records)}
            log.info("%s (%s): %d PRCS", name, apg.app_id.split("@")[0], len(records))
            del apg, builder, records
            gc.collect()
        except Exception as e:
            log.warning("Skipping %s (%s)", name, e)
            per_app[name] = {"error": str(e)}

    ds = build_dataset(str(prcs_all), str(out / "dataset"))
    summary = {"out": str(out), "apps": len(items), "per_app": per_app, "dataset": ds}

    if train_model:
        try:
            from step2_convgnn.train import train
            res = train("configs/convgnn.yaml", str(out / "dataset"), str(out / "convgnn"), epochs=epochs)
            summary["convgnn"] = {"is_weak": res["is_weak"], "best_val_macro_f1": res["best_val_macro_f1"]}
        except Exception as e:
            log.warning("ConvGNN training skipped (%s)", e)
            summary["convgnn"] = {"skipped": str(e)}

    generate_captions(str(out / "dataset"), str(out / "captions"), llm_config)
    assemble(str(out / "dataset"), str(out / "captions"), str(out / "policy"))
    ev = run_eval(str(out / "dataset"), str(out / "captions"), str(out / "policy"),
                  str(out / "eval"),
                  checkpoint=str(out / "convgnn" / "best.pt") if train_model else None)
    summary["eval"] = {"bootstrap": ev["bootstrap"],
                       "policy_completeness": ev["compliance"]["overall_completeness"]}
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a combined ADPPG dataset from an APK corpus.")
    ap.add_argument("--apks", default=None, help="folder of .apk files")
    ap.add_argument("--apg-dirs", default=None, help="comma-separated pre-built APG dirs")
    ap.add_argument("--out", default="data/corpus_run")
    ap.add_argument("--no-train", action="store_true")
    ap.add_argument("--no-precision", action="store_true")
    ap.add_argument("--epochs", type=int, default=40)
    args = ap.parse_args()
    apg_dirs = [d.strip() for d in args.apg_dirs.split(",")] if args.apg_dirs else None
    s = run_corpus(args.out, apks_dir=args.apks, apg_dirs=apg_dirs,
                   precision=not args.no_precision, train_model=not args.no_train, epochs=args.epochs)
    print("\n=== CORPUS RUN COMPLETE ===")
    for k, v in s.items():
        if k != "per_app":
            print(f"  {k}: {v}")
    print(f"  apps processed: {list(s['per_app'])}")


if __name__ == "__main__":
    main()
