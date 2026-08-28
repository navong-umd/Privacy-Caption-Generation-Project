# PAcT Classification Baselines

_Phase 10 deliverable. Companion to [PACT_SCHEMA.md](PACT_SCHEMA.md) and [DATASET.md](DATASET.md). Implementation in [`step3_caption/baselines.py`](../step3_caption/baselines.py); tests in [`tests/test_baselines.py`](../tests/test_baselines.py). The Code2Seq baseline for captions is separate; see §4 below._

Baselines exist so the graph model's numbers mean something. Every downstream comparison quotes P / R / F1 (micro and macro) against these three references.

The plan asks for three: rule-based, traditional ML, and Code2Seq / PriGen. Phase 10 lands the first two as runnable code plus one shared metrics helper. Code2Seq stays as an explicit untrained placeholder until we have real (PRCS -> caption) pairs.

---

## 1. Rule baseline (`RuleBaseline`)

**Architecture.** Sink type + third-party SDK class prefix -> multi-label Practice + Purpose.

**Rules** live in `configs/weak_labels.yaml` (`practice_by_sink`, `practice_source_default`, `purpose_advertisement`, `purpose_analytics`, `purpose_default`, `purpose_fallback`). SDK prefixes live in `configs/sdk_catalog.yaml`. Both are hand-edited YAML; a rule change is a config diff, not a code change.

**Input**: PRCS record (needs `sink_type`, `involved_methods`, `subgraph.nodes`).

**Training**: none. `.fit()` is a no-op.

**Inference**: same code path that produces the WEAK bootstrap labels in `step2_dataset/weak_labeler.py::WeakLabeler.label(prcs)`.

**Why it lives here at all**: it is a real baseline. On real APKs it hits precision from `sink_type` inference and recall from SDK-prefix matching. It is also the source of the WEAK training labels, so a graph model that only ties the rule baseline should be treated as suspicious.

**Test**: `tests/test_baselines.py::test_rule_baseline_matches_weak_labels_exactly` asserts predictions equal the record's own WEAK labels for WEAK-sourced records.

---

## 2. Traditional ML baseline (`TfIdfBaseline`)

**Architecture.** TF-IDF (max features 5000, alphanumeric identifier tokens, lowercased) over the PRCS's `code_snippet + source_api + sink_api` text. Two `OneVsRestClassifier(LogisticRegression(solver='liblinear', max_iter=200))` heads: one for Practice, one for Purpose.

**Input**: PRCS records (need `code_snippet`, `source_api`, `sink_api`, `labels.practice`, `labels.purpose` for training). The graph structure is deliberately ignored so this is a proper text-only baseline for the graph-vs-code ablation in Phase 21.

**Training**: `.fit(train_records)`. Wall-clock is a few seconds on the synthetic fixture. On the blessed 10,721-PRCS corpus it fits in under a minute on CPU.

**Inference**: `.predict(records) -> List[BaselinePrediction]`. Each prediction carries `prcs_id`, `practice`, `purpose`, `baseline="tfidf"`, `schema_version`.

**Dependencies**: `scikit-learn` only. No torch. Runs in the lean CI profile.

**Where it will fail** (documented so error analysis has a starting point):

- Non-word tokens in Dalvik output pass through the identifier regex. Not a signal; adds noise.
- Rare classes with fewer than a handful of training examples get 0 F1 on macro. Solutions come with a bigger, human-labeled corpus (Gate G1), not with a smarter tokenizer.
- No token order sensitivity. `source flows to sink` and `sink flows to source` look identical. A bigram TF-IDF partly fixes it but blows out `max_features`; skipped for now.

---

## 3. Metrics helper (`multilabel_metrics`)

Shared across every baseline and the graph model. Returns:

```json
{
  "practice": {
    "precision_micro": 0.83, "recall_micro": 0.79, "f1_micro": 0.81,
    "precision_macro": 0.71, "recall_macro": 0.68, "f1_macro": 0.69
  },
  "purpose":  { ... same shape ... },
  "banner":   "WEAK - not ground truth"
}
```

`sklearn.metrics.precision_recall_fscore_support` under the hood. Zero-division treated as 0.

Every consumer that reports these numbers on a corpus with any weak-labeled records MUST surface the `banner`. The pipeline drivers already do this via `pplib.schema.BANNER_WEAK`.

---

## 4. Code2Seq baseline (`step3_caption/code2seq_baseline.py`)

**Status**: explicit untrained placeholder. `BASELINE_TAG = "code2seq-baseline (untrained placeholder)"`. Renders a template caption from source and sink API names plus the (weak) Practice label. Does not touch a trained model.

**Why untrained**: a trained Code2Seq captioner needs paired (code path -> caption) data. Those pairs only exist after human annotation (Gate G1) produces reference captions. `docs/RESULTS.md` records this as an open gate.

**Roadmap to a real Code2Seq baseline**:

1. Produce reference captions for a stratified sample of PRCS (human, or LLM with a two-pass agreement step).
2. Reuse `step3_caption/code2seq_baseline.py::_terminals` as the AST-path terminal extractor.
3. Train a small seq2seq (transformer decoder over BPE tokens, or the reference Code2Seq architecture) on the reference captions.
4. Wire the trained model in behind the same `Code2SeqBaseline.caption(rec)` interface.

Phase 10 does not do step 1-4; it documents the roadmap and keeps the placeholder callable.

---

## 5. Evaluation methodology

- Train on `splits.json::train`. Score on `splits.json::test` (leak-safety guaranteed by [DATASET.md](DATASET.md)).
- Metrics: precision, recall, F1 (micro and macro) per head. Report both micro (dominated by common labels like `Functionality`) and macro (weights every label equally, exposes tail-class weakness).
- Every report must carry `BANNER_WEAK` while training labels are heuristic. Gate G1 clears it for records overridden by human labels.

Phase 21 (final experiments matrix) is where these baselines get their canonical numbers on the blessed 10,721-PRCS corpus and get compared against the graph model.

---

## 6. What Phase 10 explicitly did NOT do

- Did not run the baselines on the blessed corpus to produce a numbers table. That is Phase 21 territory. Running now, before G1 clears the weak banner, would enshrine unverified numbers in `docs/RESULTS.md`.
- Did not train a real Code2Seq. See §4 for the reason.
- Did not add feature engineering beyond the code snippet and API strings. The whole point of the graph vs code ablation is to see if graph structure improves over a fair text-only baseline; feature-heavy tuning here would confound that.
- Did not add a per-baseline hyperparameter search. `max_features=5000` and `LogisticRegression(solver='liblinear', max_iter=200)` are defensible defaults; tuning is a Phase 12/21 concern.
