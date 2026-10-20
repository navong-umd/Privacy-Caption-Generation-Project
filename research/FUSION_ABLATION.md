# Fusion Ablation: Graph + Code + Knowledge

_Phase 12 deliverable. Companion to [GNN_CLASSIFICATION.md](GNN_CLASSIFICATION.md) and [BASELINES.md](BASELINES.md). Arm definitions in [`step2_convgnn/arms.py`](../step2_convgnn/arms.py); tests in [`tests/test_fusion_arms.py`](../tests/test_fusion_arms.py)._

Does the graph help? Does code text help on top of the graph? Does the knowledge-base privacy overlay help on top of that? Phase 12 pins the four comparison arms the plan asks for so Phase 21 can produce clean numbers.

---

## 1. The four arms

| Arm | Sees | Ignores | Model |
|-----|------|---------|-------|
| `code` | Rendered `code_snippet` + source/sink API strings | Graph structure, KB overlay | `step3_caption.baselines.TfIdfBaseline` |
| `graph` | RGCN over PRCS subgraph + node-type embedding | Code tokens, KB overlay | `ConvGNNClassifier`, `record_to_data(privacy_features=False, token_features=False)` |
| `code_graph` | RGCN over subgraph + statement-token hashing trick | KB overlay | `ConvGNNClassifier`, `record_to_data(privacy_features=False, token_features=True)` |
| `code_graph_knowledge` | RGCN over subgraph + statement tokens + PPG overlay | Nothing | `ConvGNNClassifier`, `record_to_data(privacy_features=True, token_features=True)` |

The RGCN arm names map onto the two flags already exposed by `record_to_data`. The `code` arm is the odd one out because it does not use RGCN at all.

`step2_convgnn.arms.arm_to_flags(arm)` returns the exact `(privacy_features, token_features)` pair for the RGCN arms. The `code` arm raises a `ValueError` from that helper by design.

---

## 2. Read this vs. `step2_convgnn/ablation.py`

`step2_convgnn/ablation.py::run_ablation` implements a two-arm comparison today: `graph_knowledge` (the current default: privacy on, tokens off) vs `graph` (privacy off, tokens off). It answers "does the KB overlay help?"

Phase 12 does not change that entry point. It extends the doc / test surface with the full four-arm matrix so Phase 21 can run the whole matrix through a single driver. Naming the arms explicitly now prevents an ad-hoc grid from being invented later.

---

## 3. What each arm is trying to isolate

- `graph` vs `code`: does the PPG's structure carry more signal than the text?
- `code_graph` vs `graph`: does adding the statement-token channel help on top of structure?
- `code_graph_knowledge` vs `code_graph`: does the KB overlay (source/sink/pi_type/permission bits from Phase 4) still add signal after tokens are already in the vector?
- `code_graph_knowledge` vs `code`: the headline claim of the whole research project.

Any per-head macro-F1 or micro-F1 delta must be reported alongside its BOOTSTRAP or WEAK banner when the underlying test labels are heuristic. Gate G1 clears the banner for records overridden by human labels.

---

## 4. Featurization invariants (`tests/test_fusion_arms.py`)

1. `FUSION_ARMS == ("code", "graph", "code_graph", "code_graph_knowledge")`.
2. `arm_to_flags(ARM_CODE)` raises `ValueError` (code arm is not RGCN).
3. `arm_to_flags(ARM_GRAPH)` == `(False, False)`.
4. `arm_to_flags(ARM_CODE_GRAPH)` == `(False, True)`.
5. `arm_to_flags(ARM_CODE_GRAPH_KNOWLEDGE)` == `(True, True)`.
6. On the stub record: `graph` zeros both the privacy block and the token block; `code_graph` zeros the privacy block only; `code_graph_knowledge` populates both.
7. The three RGCN arms produce distinct `x` tensors on the same record.
8. Node types and edges are invariant across arms: only `x` changes.

---

## 5. What Phase 12 explicitly did NOT do

- Did not run the four-arm matrix on the blessed corpus. Numbers live in Phase 21 or nowhere.
- Did not fold `code` into RGCN via a separate encoder branch that would deliver the code tokens through a text embedder instead of the hashing trick. That is a real extension for a future paper; the plan asks for a fair baseline, and TF-IDF is the fair baseline.
- Did not extend `step2_convgnn/ablation.py::run_ablation` to a four-arm matrix. That refactor should follow the Phase 21 driver, not lead it, because the current two-arm entry point is wired into `pipeline/run_pipeline.py` and `legacy/notes/RESULTS.md`; a churn now would confuse the record.
- Did not change the `TOKEN_HOOK_DIM=8` hashing trick to a learned tokenizer. Commit `f73d177` documents the current hashing trick as an honest-negative at bootstrap scale; upgrading is a separate research question.
