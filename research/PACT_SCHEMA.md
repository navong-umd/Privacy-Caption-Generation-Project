# PAcT — Practice and Purpose Labels

_Phase 8 deliverable. Companion to [PRCS_SCHEMA.md](PRCS_SCHEMA.md). Constants and validator in [`pplib/pact_schema.py`](../pplib/pact_schema.py); enforced by [`tests/test_pact_schema.py`](../tests/test_pact_schema.py)._

Every PRCS carries a PAcT label block. This document pins the taxonomy, the source ladder, the required fields, and the invariants a downstream consumer can enforce with one call.

---

## 1. Taxonomy

Both heads are multi-label. Canonical sets in `pplib/schema.py`:

- **Practice** (`PRACTICE_LABELS`): `Processing`, `Collecting`, `Sharing`, `Other`.
- **Purpose** (`PURPOSE_LABELS`): `Functionality`, `Advertisement`, `Analytics`, `Other`.

No label outside these sets is accepted; the validator rejects a record with an unknown value.

---

## 2. Label sources

`label_source` names where a label came from. Consumers use it to gate trust.

| Source | Meaning | Banner rule |
|--------|---------|-------------|
| `weak` | Bootstrap heuristic (`step2_dataset/weak_labeler.py`). Not ground truth. | Must carry a non-empty `weak_banner` (`pplib.schema.BANNER_WEAK`). Every downstream product (captions, policy, eval reports) must surface it. |
| `human` | Annotator produced the label directly (Gate G1). Ground truth for that record. | No weak banner. `annotator`, `confidence`, `notes` required. |
| `llm` | LLM-assisted labeling (LLM-as-judge, LLM shortlist). Not ground truth by itself. | Same required fields as `human`; consumers may still discount by `confidence`. |

Order of precedence when combining: `human > llm > weak`. `step2_dataset/build_dataset.py::_apply_labels` implements this today.

---

## 3. Required fields on every label block

Enforced by `validate_label(dict)`.

Always required (`PACT_REQUIRED_FIELDS`):

- `practice`: list of Practice labels from the canonical set. Empty list is allowed but discouraged.
- `purpose`: list of Purpose labels from the canonical set. Empty list is allowed but discouraged.
- `label_source`: one of `PACT_LABEL_SOURCES`.
- `schema_version`: string. Current: `"1.0.0"`.

Extra required when `label_source` is `human` or `llm` (`PACT_ANNOTATION_FIELDS`):

- `annotator`: string (identifier for the human or LLM).
- `confidence`: float in `[0.0, 1.0]`.
- `notes`: string (may be empty, but the field must exist).

Extra required when `label_source` is `weak`:

- `weak_banner`: non-empty string (the module-level `BANNER_WEAK` constant).

Optional in all cases: `rationale` (weak labels use it for explanation), `timestamp` (ISO-8601), `evidence` (list of PRCS-local references such as node ids, currently unused but reserved).

---

## 4. `HumanAnnotation` dataclass

Convenience dataclass for producing valid `human` labels programmatically:

```python
from pplib.pact_schema import HumanAnnotation

ann = HumanAnnotation(
    prcs_id="prcs_abc123",
    practice=["Sharing"],
    purpose=["Advertisement"],
    annotator="ali",
    confidence=0.9,
    notes="cross-checked with SDK docs",
    timestamp="2026-08-28T01:00:00Z",
)
label = ann.to_dict()   # passes validate_label; can be written into human_labels.json
```

`label_source` defaults to `"human"`; override to `"llm"` for LLM-assisted annotations.

---

## 5. Storage

- **Per-PRCS label** lives inside the ADPPG dataset record (`data/dataset/adppg.jsonl`, each line has a `labels` block).
- **Human overrides** live in `data/starter/human_labels.json`, a mapping `prcs_id -> annotation dict`. `build_dataset.py` reads them and lets a `human` label replace a `weak` one for that PRCS.
- **Weak-label rules** in `configs/weak_labels.yaml`. **SDK -> purpose prefix table** in `configs/sdk_catalog.yaml`. Both are documented in [KNOWLEDGE_BASE.md §1](KNOWLEDGE_BASE.md).

---

## 6. Invariants (`tests/test_pact_schema.py`)

1. `PRACTICE_LABELS` and `PURPOSE_LABELS` match the plan exactly.
2. `PACT_LABEL_SOURCES == ("weak", "human", "llm")`.
3. `PACT_SCHEMA_VERSION == "1.0.0"`.
4. `weak_label_template()` produces a valid weak label after populating `practice` + `purpose`.
5. `HumanAnnotation.to_dict()` passes `validate_label`.
6. `WeakLabeler().label(prcs)` output passes `validate_label`.
7. Validator rejects: missing required fields, non-canonical Practice or Purpose values, bad `label_source`, weak label with empty banner, human label missing `annotator` / bad `confidence`.

---

## 7. What Phase 8 explicitly did NOT do

- Did not extend the weak label with `annotator` / `confidence` / `notes`. Weak labels are automated and traceable via `rationale`; adding a placeholder `annotator="weak_labeler_v1"` would give the false impression of human review.
- Did not migrate existing on-disk `data/dataset/adppg.jsonl` records to include `schema_version`. New writes carry it; validators can tolerate legacy records by treating missing `schema_version` as `"0"` if they wish.
- Did not remove `label_source == "human"` acceptance for records without `notes` in `data/starter/human_labels.json`. `build_dataset.py::_apply_labels` still tolerates the legacy short form; only newly produced records via `HumanAnnotation` guarantee the full field set.
- Did not add an `evidence` field to the label block. The plan lists it as required per annotation, but a PRCS already carries `taint_path` + `taint_rules` + `subgraph` (Phase 7), which are the evidence. Adding a redundant field on the label would only invite drift.
