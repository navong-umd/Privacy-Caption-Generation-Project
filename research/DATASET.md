# ADPPG Dataset

_Phase 9 deliverable. Builds on [PRCS_SCHEMA.md](PRCS_SCHEMA.md) and [PACT_SCHEMA.md](PACT_SCHEMA.md). Implementation in [`step2_dataset/build_dataset.py`](../step2_dataset/build_dataset.py); leak-safety guarantee tested by [`tests/test_dataset_leakage.py`](../tests/test_dataset_leakage.py)._

The ADPPG dataset is the training corpus: one line per PRCS with its PAcT labels, split by APK so no app can leak between train, val, and test.

---

## 1. Storage layout

```
<dataset_dir>/
├── adppg.jsonl               one JSON per line, one PRCS + labels per line
├── labels.csv                flat label table for quick joins and stratification checks
├── splits.json               train / val / test lists of prcs_id
└── codr_export/
    └── prcs_<id>.json        per-PRCS export shaped for the Codr annotation tool
```

Sibling `data/starter/human_labels.json` is the human-label override map (Gate G1); build_dataset reads it if present.

---

## 2. `adppg.jsonl` records

Each line is a full PRCS record (see [PRCS_SCHEMA.md](PRCS_SCHEMA.md) for the field set) with an additional `labels` block:

```json
{
  "prcs_id": "prcs_abc123",
  "schema_version": "1.0.0",
  "app_package": "com.example.app",
  "apk_filename": "app.apk",
  "class_name": "com.example.LocationHelper",
  "method_name": "getLast",
  "source_api": "android.location.LocationManager->getLastKnownLocation",
  "sink_api": "android.util.Log->i",
  "sink_type": "logging",
  "pi_type": "user's coarse location",
  "pi_category": "LOCATION_INFORMATION",
  "permission": "ACCESS_FINE_LOCATION",
  "privacy_threat": "Data Disclosure;Detecting",
  "hop_count": 3,
  "taint_path": ["...stmt_0", "...stmt_1", "...stmt_2", "...stmt_3"],
  "taint_rules": ["source", "ddg", "call_arg", "ddg"],
  "involved_methods": ["...->getLast", "...->log"],
  "code_snippet": "...",
  "subgraph": { "nodes": [...], "edges": [...] },
  "labels": {
    "practice": ["Collecting", "Processing"],
    "purpose":  ["Functionality"],
    "label_source": "weak",
    "weak_banner": "WEAK...",
    "rationale": "sink_type=logging; no 3rd-party SDK -> Functionality",
    "schema_version": "1.0.0"
  }
}
```

`labels` follows the PAcT contract; `validate_label` accepts it.

---

## 3. `labels.csv`

One row per PRCS with columns:

`prcs_id, app_package, label_source, practice_Processing, practice_Collecting, practice_Sharing, practice_Other, purpose_Functionality, purpose_Advertisement, purpose_Analytics, purpose_Other`

Each `practice_*` / `purpose_*` column is 0 or 1. Useful for stratification checks and quick sklearn joins.

---

## 4. `splits.json`

Structure:

```json
{
  "train": ["prcs_..", "prcs_..", ...],
  "val":   ["prcs_..", ...],
  "test":  ["prcs_..", ...]
}
```

**Leak-safety guarantee**: `step2_dataset/build_dataset.py::_grouped_splits` groups by `configs/weak_labels.yaml::splits.group_by` (default `app_package`) and assigns whole groups to a single bucket. Consequences:

- Every `prcs_id` appears in exactly one split.
- Every `app_package` appears in at most one split (all its PRCS land in the same bucket).
- Deterministic given the same input records and `splits.seed` (default 13).

Tested by `tests/test_dataset_leakage.py` on the `synthetic_apg_large` fixture:

1. All splits are disjoint on `prcs_id`.
2. No `app_package` bridges two splits.
3. Two consecutive `build_dataset` runs with the same inputs and seed produce identical `splits.json`.

### Held-out test app

Pass `--test-app <package>` to pin one APK to the test split. The remaining APKs are randomly split into train and val proportional to their ratios. Used by the G1 workflow so a specific held-out app becomes the ground-truth eval set.

### Test subsampling

Pass `--test-cap N` alongside `--test-app` to keep only `N` flows in the test app (rare-purpose flows are preferred, so `Advertisement` and `Analytics` PRCS are kept over `Functionality`). Purpose: make the test set small enough to hand-label without breaking leak safety.

---

## 5. Label merge order

`step2_dataset/build_dataset.py::_apply_labels`:

1. If `human_labels.json` has an entry for the `prcs_id`, use it. `label_source` becomes `"human"`. Weak banner cleared.
2. Otherwise, `step2_dataset/weak_labeler.py::WeakLabeler.label(prcs)`. `label_source` = `"weak"`, `weak_banner` populated.

An LLM-assisted label (`label_source == "llm"`) is not produced by the current build; the schema accepts it for a future ingest step.

---

## 6. Codr export

Each PRCS also lands in `codr_export/<prcs_id>.json` shaped as the Codr annotation tool expects:

```json
{
  "id": "prcs_abc123",
  "app":        { "package": "...", "apk": "..." },
  "provenance": { "class": "...", "method": "...", "source_api": "...", "sink_api": "..." },
  "code": "...",
  "graph": { "nodes": [...], "edges": [...] },
  "candidate_labels": { "practice": [...], "purpose": [...] },
  "label_status": "unverified",
  "note": "WEAK..."
}
```

`label_status` is `unverified` when the record's label is weak, `verified` otherwise.

---

## 7. Regenerating the dataset

```
python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
python -m step2_dataset.build_dataset \
    --prcs data/corpus_run/prcs_all \
    --out data/corpus_run/dataset \
    --test-app com.example.tiktok_lite \
    --test-cap 50
```

The first form is the small synthetic bootstrap that ships checked-in fixtures. The second is the pattern the corpus driver uses to produce the blessed 10,721-PRCS real corpus.

---

## 8. What Phase 9 explicitly did NOT do

- Did not add a per-label stratification check. Grouping is by APK; class balance is a downstream evaluation concern.
- Did not touch the split ratios (`train=0.7 val=0.15 test=0.15`) or the default seed (13). Both are configurable via `configs/weak_labels.yaml::splits`.
- Did not remove `data/dataset/codr_export/` in favor of a single serialization. The recon flagged that as a Phase 22 cleanup and the Codr workflow depends on the per-file view.
- Did not migrate on-disk `data/dataset/adppg.jsonl` to include `schema_version` on the labels block. New writes carry it via the Phase 8 WeakLabeler change; legacy consumers already tolerate the absence.
