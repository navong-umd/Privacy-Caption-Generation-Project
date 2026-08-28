# Graph-Based Classification (RGCN)

_Phase 11 deliverable. Companion to [BASELINES.md](BASELINES.md) and [PPG_SCHEMA.md](PPG_SCHEMA.md). Implementation in [`step2_convgnn/`](../step2_convgnn/); tensor contract enforced by [`tests/test_gnn_shapes.py`](../tests/test_gnn_shapes.py)._

Does the PPG structure improve Practice + Purpose classification over the text-only baselines? Phase 11 pins the model, the featurization, and the tensor contract so that question can be answered in the Phase 21 experiments matrix.

---

## 1. Architecture

Single model:

```
node features -> RGCN stack -> attention readout -> shared graph vector
                                                     |
                                                     +--> sigmoid head -> Practice (multi-label)
                                                     +--> sigmoid head -> Purpose  (multi-label)
```

Implemented in [`step2_convgnn/model.py::ConvGNNClassifier`](../step2_convgnn/model.py). Relation-aware (RGCN over 7 PPG edge types). Attention readout by default; mean pooling optional via `configs/convgnn.yaml::model.readout`.

The plan asks for GCN -> GAT/GGNN -> relation-aware. We went straight to relation-aware because the plan explicitly permits it and the PPG's whole point is different edge semantics per relation. A homogeneous GCN would collapse `TAINT_FLOW` and `HAS_STATEMENT` into one type, defeating the ablation in Phase 12.

Sigmoid heads because Practice and Purpose are both multi-label. Softmax would force mutually exclusive predictions.

---

## 2. Featurization (`step2_convgnn/data.py`)

Every subgraph node becomes a PyG `Data` node with two feature blocks:

**Learned block**: an integer `node_type` in `[0, len(PPG_NODE_LABELS))` gets embedded via `nn.Embedding(NUM_NODE_TYPES, type_embed_dim)`. Consumed by the model, not the featurizer.

**Structural / privacy block** (`FEAT_DIM = 2 + 1 + 6 + 13 + 8 = 30` floats per node):

| Slot | Purpose |
|------|---------|
| 0 | `is_source` (0 / 1) |
| 1 | `is_sink` (0 / 1) |
| 2 | `1` if `permission` is set, else `0` |
| 3-8 | Sink-type one-hot (6 buckets: network, storage, logging, ipc, serialization, heuristic_unknown) |
| 9-21 | PI-category one-hot (13 categories from LOCATION_INFORMATION through AUDIO to OTHER) |
| 22-29 | `TOKEN_HOOK_DIM = 8` reserved for statement-token features (empty by default; a hashing-trick encoder can populate them, see commit `f73d177`) |

Every edge becomes a `edge_index` column + an integer `edge_type` in `[0, NUM_RELATIONS)`. Relation vocabulary equals `PPG_EDGE_TYPES` (`HAS_METHOD`, `HAS_STATEMENT`, `CALLS`, `ICFG_NEXT`, `DATA_DEPENDS`, `TAINT_FLOW`, `PRIVACY_RELATION`).

The subgraph guarantees at least one edge (a self-loop) so the RGCN convolution is always defined.

---

## 3. Ablation controls (Phase 12 preview)

`record_to_data(rec, privacy_features=, token_features=)`:

- `privacy_features=False` -> APG-ONLY ablation. Structural / privacy block is zeroed. Node type embedding and edges are kept. Isolates the contribution of the PPG overlay.
- `token_features=True` -> fills the reserved `TOKEN_HOOK_DIM` slots with a hashing-trick bag of tokens over the node's `code + callee`. Enables a code-textual channel without a learned tokenizer.

Two knobs, exposed on `load_splits(...)` too. Phase 12 uses them to run the graph-vs-code ablation cleanly.

---

## 4. Training (`step2_convgnn/train.py`)

- Loss: BCEWithLogitsLoss on each head, summed.
- Optimizer: Adam (defaults from `configs/convgnn.yaml`).
- Batching: PyG `DataLoader`, standard graph batching (offsets into a single big graph).
- Determinism: single seed. Numeric drift across BLAS threads is tolerated (see [ENVIRONMENT.md §6](ENVIRONMENT.md#6-determinism)).
- Threshold: 0.5 at inference. Per-label calibration is a known gap flagged in [CODEBASE_ARCHITECTURE.md §2](CODEBASE_ARCHITECTURE.md#2-current-broken-components).

Device is currently CPU-only in `train.py`. A CUDA path is planned in Phase 14; nothing else in Phase 11 depends on it.

---

## 5. Inference contract

`ConvGNNClassifier(data) -> (practice_logits[B, 4], purpose_logits[B, 4])`. Two independent multi-label heads over `PRACTICE_LABELS` and `PURPOSE_LABELS`. Sigmoid at inference; threshold at 0.5 unless overridden.

The tensor contract, per graph:

- `x`: `float32`, shape `[num_nodes, FEAT_DIM]`.
- `node_type`: `int64`, shape `[num_nodes]`, values in `[0, NUM_NODE_TYPES)`.
- `edge_index`: `int64`, shape `[2, num_edges]`, values in `[0, num_nodes)`.
- `edge_type`: `int64`, shape `[num_edges]`, values in `[0, NUM_RELATIONS)`.
- `y_practice`: `float32`, shape `[1, len(PRACTICE_LABELS)]`, values in `{0.0, 1.0}`.
- `y_purpose`: `float32`, shape `[1, len(PURPOSE_LABELS)]`, values in `{0.0, 1.0}`.

Enforced by `tests/test_gnn_shapes.py`.

---

## 6. What Phase 11 explicitly did NOT do

- Did not run a hyperparameter sweep. `configs/convgnn.yaml` defaults are the Phase 21 starting point.
- Did not add per-label threshold calibration. It is a known gap; a Phase 21 concern.
- Did not switch to `HeteroData`. The `data.py` docstring explains why: PRCS graphs are small with low node-type cardinality, and RGCN over typed edges gives the same relation-awareness with far less plumbing. Justified in `docs/FINDINGS.md`.
- Did not add a code-only ablation classifier (the third leg of the graph-vs-code experiment). That is Phase 12, not Phase 11.
- Did not train + score the RGCN in this phase. The training path was already covered by `tests/test_step2_convgnn.py` and `tests/test_ablation.py`. Phase 21 owns the final numbers.
