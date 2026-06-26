# HANDOFF G1 — Human Annotation in Codr (real ADPPG ground truth)

**Why this is a gate:** the ConvGNN currently trains on **WEAK heuristic labels**
(`configs/weak_labels.yaml`), which are NOT ground truth. Real Practice/Purpose labels
require human annotation. Everything around this gate is built; only the human step is missing.

## What you do
1. **Generate the Codr-ready records** (already produced by the dataset builder):
   ```
   python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
   ```
   → one JSON per PRCS under `data/dataset/codr_export/<prcs_id>.json`. Each contains:
   `id`, `app`, `provenance`, `code` (snippet), `graph` (subgraph), `candidate_labels`
   (the WEAK guess, to accept/correct), `label_status: "unverified"`.

2. **Import into Codr** and annotate each PRCS with the PAcT taxonomy (multi-label, both heads):
   - **Practice:** Processing, Collecting, Sharing, Other
   - **Purpose:** Functionality, Advertisement, Analytics, Other
   Use the `code` + `graph` as evidence. Annotate ≥ the recommended set size below.

3. **Export verified labels** from Codr and convert them to a single file:
   **`data/dataset/human_labels.json`** — a JSON object keyed by `prcs_id`:
   ```json
   {
     "prcs_dd62840ec848": {"practice": ["Collecting", "Sharing"], "purpose": ["Advertisement"]},
     "prcs_219eb64f0f97": {"practice": ["Processing"], "purpose": ["Functionality"]}
   }
   ```
   (Labels outside the taxonomy are ignored; missing PRCS keep the weak label.)

## How the pipeline picks it up (automatic)
`build_dataset` checks for `data/dataset/human_labels.json` and **overrides** the weak label
for any `prcs_id` present, setting `label_source: "human"` and clearing the WEAK banner:
```
python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset \
    --human-labels data/dataset/human_labels.json
```
Then retrain — the BOOTSTRAP banner disappears once a split is fully human-labeled:
```
python -m step2_convgnn.train --config configs/convgnn.yaml --dataset data/dataset
```

## What I need from you
- **Target labeled-set size:** for a credible first result, ≥ **300–500 PRCS** spanning
  ≥ 30 apps (more is better; grouped splits need enough apps per split). Tell me the target.
- **Annotator count / adjudication:** ≥ 2 annotators with inter-annotator agreement (Cohen's κ)
  for the paper. Provide raw per-annotator files if you want κ computed by the eval harness.
- A real APK corpus to extract those PRCS from — see **HANDOFF_G4.md** (Androzoo).

## Definition of done for this gate
`data/dataset/human_labels.json` exists, covers the train/val/test PRCS, and a retrain run
reports `label_source=human` with no BOOTSTRAP banner on the test split.
