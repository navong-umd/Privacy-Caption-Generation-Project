# Fusion Ablation: Graph, Code Tokens and Knowledge Overlay

_Companion to [GNN_CLASSIFICATION.md](GNN_CLASSIFICATION.md), [BASELINES.md](BASELINES.md) and [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md). Arm definitions derive from [`pplib/experiment_matrix.py`](../pplib/experiment_matrix.py) through [`step2_convgnn/arms.py`](../step2_convgnn/arms.py); tests in [`tests/test_fusion_arms.py`](../tests/test_fusion_arms.py)._

Does the PPG privacy overlay help? Do statement tokens help? Does either still help once the other is present? The four RGCN arms answer this as a 2x2 over the two knobs `record_to_data` exposes.

---

## 1. The four RGCN arms and the text baseline

| Arm | Id | `privacy_features` | `token_features` | Sees |
|-----|----|---|---|------|
| `apg` | EXP001 | False | False | subgraph structure + node-type embedding |
| `apg_code` | EXP002 | False | True | + statement-token hashing trick |
| `ppg` | EXP003 | True | False | + PPG privacy overlay (source/sink, permission, sink type, PI category) |
| `ppg_code` | EXP004 | True | True | both (the full model) |
| `tfidf` | EXP006 | n/a | n/a | code snippet + API strings, no graph (`TfIdfBaseline`) |

`step2_convgnn.arms.arm_to_flags(arm)` returns `(privacy_features, token_features)` for the RGCN arms and raises `ValueError` for `rule` and `tfidf`, which are not RGCN configurations.

---

## 2. What each comparison isolates

- `ppg` vs `apg` and `ppg_code` vs `apg_code`: the privacy overlay, without and with code tokens.
- `apg_code` vs `apg` and `ppg_code` vs `ppg`: the code tokens, without and with the overlay.
- `ppg_code` vs `tfidf`: graph plus overlay against a text-only model, the headline classification claim.

Every arm reports a paired item bootstrap of macro-F1 against `ppg_code` seed 0 (see [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md) §2). Deltas on weak test labels carry the BOOTSTRAP banner.

---

## 3. Featurization invariants (`tests/test_fusion_arms.py`)

1. `FUSION_ARMS` equals the matrix's classification arms `("apg", "apg_code", "ppg", "ppg_code")`, with ids EXP001 to EXP004.
2. The four flag tuples are distinct and cover the 2x2.
3. Baseline arms raise a `ValueError` pointing at `step3_caption.baselines`; unknown and caption arms raise `unknown arm`.
4. On the stub record each arm populates exactly its feature blocks: the privacy block only when `privacy_features`, the token block only when `token_features`.
5. The four arms produce distinct `x` tensors; node types and edges are invariant across arms.

---

## 4. Relation to `step2_convgnn/ablation.py`

`run_ablation` is the older two-arm comparison (privacy overlay on vs off, tokens off, one seed). It is a quick check, not a reported result; reported numbers come only from the matrix runner.

The hashing trick (`TOKEN_HOOK_DIM=8`) stays as is. A learned code encoder is a separate research question.
