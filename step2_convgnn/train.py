"""
Purpose: STEP 2 - train/evaluate the ConvGNN (Practice + Purpose) on the ADPPG dataset.
Input:   --config configs/convgnn.yaml, --dataset data/dataset.
Output:  best checkpoint (best.pt), train_log.csv (per-epoch), metrics.csv (final test).

Deterministic seeds, BCEWithLogits + pos_weight, attention readout, early stopping on
val macro-F1, checkpointing, CSV + optional TensorBoard logs.

If the TEST split is WEAK-labeled, every reported metric is printed under a BOOTSTRAP banner
(not a real result). Metrics are reported on test, so a human-labeled test split (Gate G1)
clears the banner even while train stays weak (weak supervision) — see HANDOFF_G2.md.

Run: python -m step2_convgnn.train --config configs/convgnn.yaml --dataset data/dataset
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch_geometric.loader import DataLoader

from pplib.io_utils import ensure_dir, get_logger, load_yaml
from pplib.schema import BANNER_BOOTSTRAP, PRACTICE_LABELS, PURPOSE_LABELS
from step2_convgnn.data import load_splits
from step2_convgnn.metrics import multilabel_metrics
from step2_convgnn.model import ConvGNNClassifier

log = get_logger("train")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _pos_weight(graphs: List, attr: str, n_labels: int) -> torch.Tensor:
    """pos_weight = (#neg / #pos) per label, clamped to keep it finite."""
    y = torch.cat([getattr(g, attr) for g in graphs], dim=0) if graphs else torch.zeros((0, n_labels))
    pos = y.sum(dim=0)
    neg = y.shape[0] - pos
    w = torch.where(pos > 0, neg / pos.clamp(min=1), torch.ones_like(pos))
    return w.clamp(0.1, 10.0)


@torch.no_grad()
def _predict(model, loader, device) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    model.eval()
    yp_t, yp_p, yt_t, yt_p = [], [], [], []
    for batch in loader:
        batch = batch.to(device)
        lp, lu = model(batch)
        yp_t.append((torch.sigmoid(lp) > 0.5).int().cpu().numpy())
        yp_p.append((torch.sigmoid(lu) > 0.5).int().cpu().numpy())
        yt_t.append(batch.y_practice.int().cpu().numpy())
        yt_p.append(batch.y_purpose.int().cpu().numpy())
    cat = lambda xs, d: np.concatenate(xs) if xs else np.zeros((0, d), dtype=int)
    return (cat(yt_t, 4), cat(yp_t, 4), cat(yt_p, 4), cat(yp_p, 4))


def _evaluate(model, loader, device) -> Dict[str, float]:
    yt_pr, yp_pr, yt_pu, yp_pu = _predict(model, loader, device)
    m = {}
    m.update(multilabel_metrics(yt_pr, yp_pr, PRACTICE_LABELS, "practice"))
    m.update(multilabel_metrics(yt_pu, yp_pu, PURPOSE_LABELS, "purpose"))
    m["macro_f1"] = (m["practice_macro_f1"] + m["purpose_macro_f1"]) / 2
    return m


def train(config: str, dataset_dir: str, out_dir: str | None = None,
          epochs: int | None = None, privacy_features: bool = True,
          token_features: bool | None = None) -> Dict:
    cfg = load_yaml(config)
    tc = cfg["train"]
    set_seed(tc["seed"])
    device = torch.device("cpu")
    out = ensure_dir(out_dir or cfg["paths"]["out_dir"])

    # privacy_features=False -> APG-only ablation (privacy overlay zeroed in node features).
    # token_features -> fill the reserved statement-token hook (config default: train.token_features).
    if token_features is None:
        token_features = tc.get("token_features", False)
    splits = load_splits(dataset_dir, privacy_features=privacy_features, token_features=token_features)
    # Metrics are reported on the TEST split, so the BOOTSTRAP banner keys off test only:
    # training on weak labels but evaluating on a human-labeled test set is a real result.
    # (Matches step4_eval.evaluate, so a single human-labeled held-out app clears the banner.)
    eval_split = splits.get("test") or splits.get("val") or splits.get("train") or []
    is_weak = any(getattr(g, "label_source", "weak") == "weak" for g in eval_split)
    n_epochs = epochs or tc["epochs"]

    bs = tc["batch_size"]
    train_loader = DataLoader(splits["train"], batch_size=bs, shuffle=True)
    val_loader = DataLoader(splits["val"] or splits["train"], batch_size=bs)
    test_loader = DataLoader(splits["test"] or splits["val"] or splits["train"], batch_size=bs)

    model = ConvGNNClassifier(cfg).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    if tc.get("pos_weight", True):
        pw_pr = _pos_weight(splits["train"], "y_practice", 4).to(device)
        pw_pu = _pos_weight(splits["train"], "y_purpose", 4).to(device)
    else:
        pw_pr = pw_pu = None
    loss_pr = nn.BCEWithLogitsLoss(pos_weight=pw_pr)
    loss_pu = nn.BCEWithLogitsLoss(pos_weight=pw_pu)

    best_metric, best_state, patience = -1.0, None, 0
    monitor = tc.get("monitor", "val_macro_f1")
    log_rows: List[dict] = []

    for epoch in range(1, n_epochs + 1):
        model.train()
        total = 0.0
        for batch in train_loader:
            batch = batch.to(device)
            opt.zero_grad()
            lp, lu = model(batch)
            loss = loss_pr(lp, batch.y_practice) + loss_pu(lu, batch.y_purpose)
            loss.backward()
            opt.step()
            total += float(loss.detach())
        val_m = _evaluate(model, val_loader, device)
        score = val_m["macro_f1"]
        log_rows.append({"epoch": epoch, "train_loss": round(total, 4),
                         "val_macro_f1": round(score, 4),
                         "val_practice_macro_f1": round(val_m["practice_macro_f1"], 4),
                         "val_purpose_macro_f1": round(val_m["purpose_macro_f1"], 4)})
        if score > best_metric:
            best_metric, best_state, patience = score, {k: v.cpu().clone()
                                                         for k, v in model.state_dict().items()}, 0
        else:
            patience += 1
            if patience >= tc["early_stopping_patience"]:
                log.info("Early stopping at epoch %d (best %s=%.4f)", epoch, monitor, best_metric)
                break

    if best_state:
        model.load_state_dict(best_state)
    torch.save({"state_dict": model.state_dict(), "config": cfg}, out / "best.pt")

    test_m = _evaluate(model, test_loader, device)
    # write logs
    with open(out / "train_log.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(log_rows[0].keys()))
        w.writeheader(); w.writerows(log_rows)
    with open(out / "metrics.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        if is_weak:
            w.writerow(["BANNER", BANNER_BOOTSTRAP])
        for k, v in sorted(test_m.items()):
            w.writerow([k, round(v, 4)])

    _print_report(test_m, is_weak, len(splits["train"]), len(splits["test"]))
    return {"test": test_m, "is_weak": is_weak, "best_val_macro_f1": best_metric}


def _print_report(m: Dict[str, float], is_weak: bool, n_train: int, n_test: int) -> None:
    print("\n=== ConvGNN test metrics ===")
    if is_weak:
        print(f"  *** {BANNER_BOOTSTRAP} ***")
    print(f"  train graphs={n_train}  test graphs={n_test}")
    print(f"  practice: micro_f1={m['practice_micro_f1']:.3f} macro_f1={m['practice_macro_f1']:.3f} "
          f"subset_acc={m['practice_subset_acc']:.3f}")
    print(f"  purpose : micro_f1={m['purpose_micro_f1']:.3f} macro_f1={m['purpose_macro_f1']:.3f} "
          f"subset_acc={m['purpose_subset_acc']:.3f}")
    if is_weak:
        print("  (metrics computed on WEAK labels — not a real result; real numbers await G1.)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Train the ConvGNN (Step 2).")
    ap.add_argument("--config", default="configs/convgnn.yaml")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--out", default=None)
    ap.add_argument("--epochs", type=int, default=None)
    args = ap.parse_args()
    train(args.config, args.dataset, args.out, args.epochs)


if __name__ == "__main__":
    main()
