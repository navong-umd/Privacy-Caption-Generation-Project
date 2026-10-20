# HANDOFF G2 — Real Classification (and Caption) Metrics

**Why this is a gate:** the ConvGNN runs end-to-end today, but it is trained and evaluated on
**WEAK heuristic labels** (and a SYNTHETIC graph fixture). Every metric it prints carries the
`BOOTSTRAP — not a real result` banner. Real Practice/Purpose metrics depend on **G1** (human
labels) and, for scale, **G4** (a real APK corpus).

## What is already built (no action needed)
- `step2_convgnn/` — PyG conversion, RGCN model (2 multi-label heads), deterministic training
  with pos_weight, early stopping, checkpointing, CSV logs. `python -m step2_convgnn.train ...`.
- The metrics harness computes per-label P/R/F1, micro/macro F1, and subset accuracy.

## What turns BOOTSTRAP into a real result (your steps)
1. Complete **HANDOFF_G1** (human labels → `data/dataset/human_labels.json`).
2. Rebuild the dataset so labels become `human`:
   ```
   python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset \
       --human-labels data/dataset/human_labels.json
   ```
3. Retrain — the BOOTSTRAP banner is suppressed once **no split is WEAK-labeled**:
   ```
   python -m step2_convgnn.train --config configs/convgnn.yaml --dataset data/dataset
   ```
4. Read `data/convgnn/metrics.csv` (no `BANNER` row = real metrics).

## What I need from you
- Confirm the labeled set from G1 and the APK corpus from G4.
- Optional: a held-out test set of apps you want reported separately for the paper.
- A target metric bar (e.g., macro-F1) so I can tune model size / features / thresholds.

## Definition of done for this gate
`metrics.csv` has no `BANNER` row, is computed on a human-labeled, APK-grouped test split,
and the run is reproducible from the committed config + seed.
