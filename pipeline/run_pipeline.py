"""
Purpose: ONE command to run the whole pipeline end-to-end on a fixture or a real APK.
Input:   --apg DIR (APG CSVs) or --apk FILE (runs the adapter first); --out RUN_DIR.
Output:  RUN_DIR/{apg,ppg,prcs,dataset,convgnn,captions,policy,eval,userstudy} populated.

Chains: [APK->APG] -> PPG -> PRCS -> ADPPG -> ConvGNN(train) -> captions -> policy -> eval -> study.
ConvGNN training is skipped automatically if torch/PyG are not installed (pipeline still completes).

Run (fixture):  python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run
Run (real APK): python -m pipeline.run_pipeline --apk path/to/app.apk --out data/run
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Optional

import yaml

from pplib.io_utils import ensure_dir, get_logger, load_yaml
from stage4_ppg.build_ppg import build_ppg
from step2_prcs.extract_prcs import extract_prcs
from step2_dataset.build_dataset import build_dataset
from step3_caption.generate import generate_captions
from step3_policy.assemble import assemble
from step4_eval.evaluate import run as run_eval
from step4_userstudy.build_study import build_study

log = get_logger("pipeline")


def _precision_config(ppg_config: str, out: Path) -> str:
    """Write a derived PPG config tuned for precision on large real APKs."""
    cfg = load_yaml(ppg_config)
    cfg.setdefault("taint", {})
    cfg["taint"]["follow_icfg"] = False        # DDG-only data flow (precision)
    cfg["taint"]["max_paths_per_source"] = 25  # bound the per-source explosion
    derived = out / "ppg.precision.yaml"
    with open(derived, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)
    return str(derived)


def run_pipeline(out_dir: str, apg_dir: Optional[str] = None, apk: Optional[str] = None,
                 ppg_config: str = "configs/ppg.yaml", llm_config: str = "configs/llm.yaml",
                 train_model: bool = True, epochs: int = 40, neo4j: bool = False,
                 precision: bool = False) -> Dict:
    """Run every stage; returns a summary dict of artifact paths + key counts."""
    out = ensure_dir(out_dir)
    summary: Dict = {"out": str(out)}

    # 0. real APK -> APG CSVs (adapter)
    if apk:
        from adapters.run_apg_csv import run_apg_csv
        apg_dir = str(out / "apg")
        run_apg_csv(apk, apg_dir)
    if not apg_dir:
        raise ValueError("provide --apg DIR or --apk FILE")
    if precision:                              # tighten taint for real-APK scale
        ppg_config = _precision_config(ppg_config, out)

    # 1. PPG
    builder = build_ppg(apg_dir, ppg_config, str(out / "ppg"), neo4j=neo4j)
    summary["ppg"] = builder.summary()
    # 2. PRCS
    prcs = extract_prcs(str(out / "ppg"), str(out / "prcs"))
    summary["prcs"] = len(prcs)
    # 3. ADPPG dataset (WEAK labels unless human_labels.json present in out/dataset)
    ds = build_dataset(str(out / "prcs"), str(out / "dataset"))
    summary["dataset"] = ds
    # 4. ConvGNN (optional)
    checkpoint = None
    if train_model:
        try:
            from step2_convgnn.train import train
            res = train("configs/convgnn.yaml", str(out / "dataset"), str(out / "convgnn"),
                        epochs=epochs)
            checkpoint = str(out / "convgnn" / "best.pt")
            summary["convgnn"] = {"is_weak": res["is_weak"], "best_val_macro_f1": res["best_val_macro_f1"]}
        except Exception as e:  # torch/PyG missing -> continue without the model
            log.warning("ConvGNN training skipped (%s)", e)
            summary["convgnn"] = {"skipped": str(e)}
    # 5. captions
    caps = generate_captions(str(out / "dataset"), str(out / "captions"), llm_config)
    summary["captions"] = len(caps)
    # 6. policy
    pol = assemble(str(out / "dataset"), str(out / "captions"), str(out / "policy"))
    summary["policy_apps"] = len(pol["apps"])
    # 7. evaluation
    ev = run_eval(str(out / "dataset"), str(out / "captions"), str(out / "policy"),
                  str(out / "eval"), checkpoint=checkpoint)
    summary["eval"] = {"bootstrap": ev["bootstrap"],
                       "policy_completeness": ev["compliance"]["overall_completeness"]}
    # 8. user-study packet
    us = build_study(str(out / "dataset"), str(out / "captions"), str(out / "userstudy"))
    summary["userstudy_tasks"] = us["n_tasks"]
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the full privacy-caption pipeline.")
    ap.add_argument("--apg", default=None, help="APG CSV dir (Stage 2 output / fixture)")
    ap.add_argument("--apk", default=None, help="real APK (runs the APG adapter first)")
    ap.add_argument("--out", default="data/run")
    ap.add_argument("--no-train", action="store_true", help="skip ConvGNN training")
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--neo4j", action="store_true")
    ap.add_argument("--precision", action="store_true",
                    help="tighten taint for large real APKs (DDG-only, cap paths/source)")
    args = ap.parse_args()
    apg = args.apg or (None if args.apk else "data/fixtures/synthetic_apg_large")
    s = run_pipeline(args.out, apg_dir=apg, apk=args.apk, train_model=not args.no_train,
                     epochs=args.epochs, neo4j=args.neo4j, precision=args.precision)
    print("\n=== PIPELINE COMPLETE ===")
    for k, v in s.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
