# HANDOFF G4 — Real APK Corpus (Androzoo)

**Why this is a gate:** real Practice/Purpose metrics and a publishable evaluation need a corpus
of real APKs (e.g., **Androzoo**), which requires **your API key / credentials**. The pipeline
already runs on a real APK end-to-end — it just needs APKs to point at.

## What is already built (no action needed)
- `adapters/run_apg_csv.py` — turns a real `.apk` into Stage 2 APG CSVs **without Neo4j**
  (mirrors the Stage 2 builder; the original script is untouched). Needs `pip install androguard`.
- `pipeline/run_pipeline.py --apk <file>` — runs APK → APG → … → policy → eval in one command.

## What you do
1. Get an **Androzoo API key** (https://androzoo.uni.lu/) and accept its terms.
2. Download a sample/corpus of APKs (your selection criteria — e.g., top free apps, F-Droid, by
   category). Place them in a folder, e.g. `data/corpus/*.apk`.
3. Run the pipeline per APK (or loop over the folder):
   ```
   pip install androguard            # one-time, for disassembly
   python -m pipeline.run_pipeline --apk data/corpus/<app>.apk --out data/run_<app>
   ```
   The local sample APK already present can be used as a first smoke test:
   ```
   python -m adapters.run_apg_csv --apk "Static Code Analysis Module/input/APK/sample.apk" --out data/apg
   python -m pipeline.run_pipeline --apg data/apg --out data/run_sample
   ```
4. Aggregate the per-APK PRCS into one dataset for annotation (G1) and training (G2).

## What I need from you
- The Androzoo key (or the downloaded APKs).
- Target corpus size + selection criteria (for representativeness in the paper).
- Confirmation it is acceptable to run androguard locally on these APKs (no external calls are made
  by our code beyond optional, key-gated LLM requests).

## Definition of done for this gate
A real APK corpus is processed through `run_pipeline --apk`, producing per-APK PRCS that feed G1
(annotation) and G2 (training), with results reproducible from the committed configs.
