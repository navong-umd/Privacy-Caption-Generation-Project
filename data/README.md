# data/ — Inputs, Fixtures, and Regenerable Pipeline Outputs

Only **`data/fixtures/`** is committed to git. Everything else is gitignored (see `.gitignore`) — it is either an input the researcher must download (APK corpus, AndroZoo index) or a derivative artifact that any of the pipeline drivers regenerate.

Inventory produced by Phase 1 recon (workflow `wf_125796bc-397`).

---

## Committed (checked into git)

| Path | Purpose | Producer |
|------|---------|----------|
| `data/fixtures/` | The two synthetic APG fixtures the 79-test pytest suite runs against — `synthetic_apg/` (small, used by `stage4_ppg` unit tests) and `synthetic_apg_large/` (8-app, used by dataset/split/ablation tests). 8-CSV APG schema each. | `python data/fixtures/make_synthetic_apg.py` |

Everything else in this document is gitignored.

---

## Real APK inputs (download / fetch)

| Path | Purpose | Producer | Size |
|------|---------|----------|------|
| `data/androzoo/` | AndroZoo index (`latest.csv.gz` ≈ 3.5 GB) + resolved-package manifests. | `python -m adapters.fetch_androzoo --download-index data/androzoo/latest.csv.gz` | 3.3 GB |
| `data/corpus/` | Small-set APK inputs (default `--out` for `fetch_androzoo` / `fetch_fdroid`). | `python -m adapters.fetch_androzoo --index data/androzoo/latest.csv.gz --packages "..." --out data/corpus` | 39 MB |
| `data/corpus_az/` | 8-APK AndroZoo download used for the blessed 10,721-PRCS real-corpus run. | `python -m adapters.fetch_androzoo --index data/androzoo/latest.csv.gz --packages "..." --out data/corpus_az` | 178 MB |

---

## Stage 1 — APG (per-APK disassembly)

| Path | Producer | Size |
|------|----------|------|
| `data/apg/` | **Empty placeholder** — legacy default named by `configs/ppg.yaml -> paths.apg_dir` before Phase 1 fixed it. Do not use. | — |
| `data/apg_real/` | `python -m adapters.run_apg_csv --apk <androzoo apk> --out data/apg_real` (also invoked in-memory by `pipeline/run_corpus.py`) | 1.3 GB |
| `data/apg_fdroid/` | `python -m adapters.run_apg_csv --apk <fdroid apk> --out data/apg_fdroid` (via `adapters/fetch_fdroid.py`) | 1.3 GB |

Each APG directory holds the standard 8-file schema: `{AST,MCG,ICFG,DDG}_{nodes,edges}.csv` (see `pplib/apg_model.py`).

---

## Stage 3 — PPG (privacy overlay on APG)

| Path | Producer | Size |
|------|----------|------|
| `data/ppg/` | `python -m stage4_ppg.build_ppg --apg data/fixtures/synthetic_apg --out data/ppg` | 660 KB |
| `data/ppg_large/` | `python -m stage4_ppg.build_ppg --apg data/fixtures/synthetic_apg_large --out data/ppg_large` | 592 KB |
| `data/ppg_real/` | `python -m stage4_ppg.build_ppg --apg data/apg_real --out data/ppg_real` | 3.7 GB |

Each PPG directory holds: `PPG_{nodes,edges}.csv`, `ppg.pkl`, `ppg.graphml`, `taint_paths.json`.

---

## Stage 4 — PRCS (Privacy-Relevant Code Slices)

| Path | Producer | Size |
|------|----------|------|
| `data/prcs/` | `python -m step2_prcs.extract_prcs --ppg data/ppg --out data/prcs` | 104 KB |
| `data/prcs_large/` | `python -m step2_prcs.extract_prcs --ppg data/ppg_large --out data/prcs_large` | 416 KB |

Each PRCS directory holds `prcs_<id>.json` per slice + `prcs_index.csv`.

---

## Stage 5 — ADPPG dataset (labelled PRCS)

| Path | Producer | Size |
|------|----------|------|
| `data/dataset/` | `python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset` | 165 KB |
| `data/dataset_large/` | `python -m step2_dataset.build_dataset --prcs data/prcs_large --out data/dataset_large` | 648 KB |

Each dataset directory holds `adppg.jsonl`, `labels.csv`, `splits.json` (APK-grouped), and a per-PRCS `codr_export/`.

⚠️ `data/dataset/splits.json` ships with `test: []` (the small-synthetic bootstrap has no test split); use `data/dataset_large/` or `data/corpus_run/dataset/` for eval.

---

## Stage 6 — RGCN classifier artifacts

| Path | Producer | Size |
|------|----------|------|
| `data/convgnn/` | `python -m step2_convgnn.train --dataset data/dataset --out data/convgnn` | 448 KB |
| `data/convgnn_large/` | `python -m step2_convgnn.train --dataset data/dataset_large --out data/convgnn_large` | 448 KB |

Each holds `best.pt` + `metrics.csv` (+ predictions).

---

## Stage 7 — Captions

| Path | Producer | Size |
|------|----------|------|
| `data/captions/` | `python -m step3_caption.generate --dataset data/dataset --out data/captions` (default `--provider mock`) | 56 KB |
| `data/captions_large/` | `python -m step3_caption.generate --dataset data/dataset_large --out data/captions_large` | 56 KB |

For real-LLM variants, the corpus driver writes to `data/corpus_run/captions_llm/` (see below).

---

## Stage 8 — Policy artifacts

| Path | Producer | Size |
|------|----------|------|
| `data/policy_large/` | `python -m step3_policy.assemble --dataset data/dataset_large --captions data/captions_large --out data/policy_large` | 84 KB |

Produces per-app `notice.md`, `policy.md`, `policy.json`.

---

## Stage 9 — Auto evaluation

| Path | Producer | Size |
|------|----------|------|
| `data/eval_large/` | `python -m step4_eval.evaluate --dataset data/dataset_large --captions data/captions_large --out data/eval_large` | 28 KB |
| `data/eval_run/` | `python -m step4_eval.evaluate --dataset data/corpus_run/dataset --captions data/corpus_run/captions --out data/eval_run` | 1.1 GB |

---

## Bundled output roots (multi-stage)

| Path | Producer | Size |
|------|----------|------|
| `data/run/` | Single-APK driver output — everything for one app. Layout: `app/`, `captions/`, `convgnn/`, `dataset/`, `eval/`, `policy/`, `ppg/`, `prcs/`, `userstudy/`. | `python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run` (or `--apk path/to/app.apk`) | 2.5 MB |
| `data/corpus_run/` | Multi-APK driver output — the blessed real-corpus root. Layout: `app/`, `app_llm/`, `captions/`, `captions_llm/`, `convgnn/`, `dataset/`, `eval/`, `caption_eval/`, `policy/`, `policy_llm/`, `prcs_all/`, plus runtime `ppg.precision.yaml`. | `python -m pipeline.run_corpus --apks data/corpus --out data/corpus_run --precision` | 1.8 GB |

---

## Human-annotation packages (G1 / G2 gates)

| Path | Purpose | Producer |
|------|---------|----------|
| `data/starter/` | Human-annotation starter package. `annotation_sheet.csv` (input) + `human_labels.json` + `dataset/` + `model/` + `prcs/`. Referenced by `run_g1g2.py --base data/starter`. | Assembled ad-hoc for G1/G2; upstream/downstream loose files under `data/` (`_annot_rows.json`, `_merged_labels.json`, `_review_shortlist.csv/md`) belong to this workflow. |

---

## Storage totals (approx.)

- Everything under `data/` at time of Phase 1 recon: **≈ 14 GB** (heaviest: `data/androzoo/latest.csv.gz` 3.3 GB, `data/ppg_real/` 3.7 GB, `data/corpus_run/` 1.8 GB, `data/eval_run/` 1.1 GB, `data/apg_real/` + `data/apg_fdroid/` 2.6 GB combined).
- Do not ever `git add data/*` outside `data/fixtures/`.

---

## Regenerating from scratch (golden path)

```
# 1. Committed synthetic fixtures — no download needed, no APK.
pytest tests/ -q                                 # 79 tests, all green

# 2. End-to-end on the small synthetic profile
python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run

# 3. Real-APK corpus (needs `pip install -r requirements-apk.txt`, a downloaded AndroZoo index, and APK inputs under data/corpus)
python -m pipeline.run_corpus --apks data/corpus --out data/corpus_run --precision
```
