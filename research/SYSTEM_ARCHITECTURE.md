# System Architecture

One page. Full detail lives in the per-subsystem docs.

## The pipeline

```
APK
 |
 v  adapters/run_apg_csv.py            (Phase 2)
APG               ---> APG_META.json      (Phase 2 provenance)
 |
 v  stage4_ppg/build_ppg.py            (Phases 4-5)
PPG               ---> PPG_edges.taint_rule column (Phase 5 per-hop rules)
 |                     |
 |                     +-- stage4_ppg/taint.py    (Phase 6)
 |                     +-- pplib/knowledge.py     (Phase 4)
 v  step2_prcs/extract_prcs.py         (Phase 7)
PRCS              ---> pplib/prcs_schema.py       (Phase 7 versioned schema)
 |
 v  step2_dataset/build_dataset.py     (Phases 8-9)
ADPPG             ---> pplib/pact_schema.py       (Phase 8 label contract)
                   +-- splits.json (leak-safe, Phase 9)
 |
 +-> step3_caption/generate.py         (Phase 13)
 |    +-- experiments A-F              (Phase 14)
 |    +-- grounding.py                  (Phase 13)
 |    v
 |    captions.json
 |
 +-> step2_convgnn/train.py             (Phase 11)
 |    +-- arms.py fusion matrix         (Phase 12)
 |    v
 |    best.pt
 |
 v  step4_eval/                         (Phases 10, 15)
     +-- baselines.py    (RuleBaseline, TfIdfBaseline)
     +-- aggregate.py    (BLEU / ROUGE / grounding / judge)
     v
     eval report + rating sheet
 |
 v  step3_policy/assemble.py + step4_app/ + step4_userstudy/    (Phase 18)
GDPR/CCPA notice.md + policy.md + Nutrition Facts app + study packet
```

Every module here is documented in its own file under `research/`.

## Layers

Three layers, all interlocked:

1. **Program layer** (APG). Structure, control flow, data dependence. `adapters/run_apg_csv.py` + `pplib/apg_model.py`.
2. **Privacy layer** (PPG). Sources, sinks, taint edges, LINDDUN threat tags, KB provenance. `stage4_ppg/*`.
3. **Learning layer** (ADPPG + RGCN + captions + policy + eval). `step2_dataset/*`, `step2_convgnn/*`, `step3_caption/*`, `step3_policy/*`, `step4_*`.

The knowledge base (`pplib/knowledge.py`) sits perpendicular to all three layers: `stage4_ppg/catalogs.py` reads it, and everything downstream inherits the tags.

## Contracts that bind the layers

Every layer boundary has a versioned schema:

- APG boundary: `pplib/schema.py::APG_*` + `APG_META.json`.
- PPG boundary: `pplib/schema.py::PPG_*` + per-edge `taint_rule` column.
- PRCS boundary: `pplib/prcs_schema.py::PRCS_SCHEMA_VERSION` + required fields.
- Label boundary: `pplib/pact_schema.py::PACT_SCHEMA_VERSION` + validator.
- Experiment boundary: `pplib/experiment.py::EXPERIMENT_SCHEMA_VERSION` + manifest layout.
- Error boundary: `pplib/error_taxonomy.py::ERROR_TAXONOMY_VERSION` + categories + stages.

Break any of these and the whole pipeline can be audited by re-reading one doc.

## Drivers

Two canonical drivers assemble the whole system:

- `pipeline/run_pipeline.py`: single APK (or fixture APG) to every artifact.
- `pipeline/run_corpus.py`: multi-APK to a pooled ADPPG dataset.

Both are thin. All logic lives in the modules above.

## Storage roots

Everything under `data/` is regenerable. Only `data/fixtures/` is committed. See [DATASET.md](DATASET.md) and repo-root `data/README.md`.

Experiment manifests live under `experiments/EXP???/manifest.json` with a flat `experiments/index.jsonl`. See [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md).
