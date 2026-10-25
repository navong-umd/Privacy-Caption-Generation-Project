# Research Questions

Central question:

> Does an Android privacy-aware graph representation improve privacy behavior understanding and caption generation over existing code / sequence-only approaches?

Broken down:

## Q1. Does a Privacy Property Graph help classify Practice + Purpose?

- Formal: on the same ADPPG test split, does an RGCN over the full PPG (`ppg_code_knowledge` arm) beat the code-only baseline (`code`) on macro-F1 across both heads?
- Instruments: [BASELINES.md](BASELINES.md), [GNN_CLASSIFICATION.md](GNN_CLASSIFICATION.md), [FUSION_ABLATION.md](FUSION_ABLATION.md), [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md).
- Answered by: arm-vs-arm deltas in [RESULTS.md](RESULTS.md) once the runs land.

## Q2. Which piece of the graph carries the signal?

- Formal: does structure alone (`apg`) beat text? Does the KB overlay (`ppg` vs `apg`) add on top? Does the token channel (`ppg_code` vs `apg`) add on top? Does combining them (`ppg_code_knowledge`) add over the union?
- Instrument: the ten-arm matrix in [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md).

## Q3. Which evidence representation produces the strongest privacy caption?

- Formal: across LLM conditions A (code only), B (code + API), C (code + taint path), D (code + PPG), E (code + PPG + PAcT), F (full), which condition maximizes grounding pass rate, minimizes hallucinated-vendor rate, and (with references or an LLM judge) maximizes BLEU / ROUGE / judge score?
- Instrument: [LLM_EXPERIMENTS.md](LLM_EXPERIMENTS.md) + [CAPTION_EVAL.md](CAPTION_EVAL.md).

## Q4. Are the captions evidence-grounded?

- Formal: what fraction of generated captions pass `check_grounding(caption, evidence)` on the test split? Which axis fails more often (PI mention vs sink mention vs forbidden-vendor)?
- Instrument: [CAPTION_GENERATION.md](CAPTION_GENERATION.md) + [CAPTION_EVAL.md](CAPTION_EVAL.md).

## Q5. Can a taint flow be defended after the fact?

- Formal: for every `TAINT_FLOW` edge in the PPG, can a reviewer read the `taint_rule` tag and derive the reason (ddg, icfg, call_arg, call_ret)?
- Instrument: [PRIVACY_TRAVERSAL.md](PRIVACY_TRAVERSAL.md) + `tests/test_ppg_provenance.py`.

## Q6. Is the pipeline reproducible?

- Formal: on a clean Python 3.14 environment following [ENVIRONMENT.md](ENVIRONMENT.md), does `pytest tests/` pass, and does `python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run` produce every artifact listed in [END_TO_END.md](END_TO_END.md)?
- Instrument: `tests/test_pipeline_e2e.py`, `tests/test_pipeline_artifacts.py`.

## Q7. Does the system generalize beyond the synthetic fixtures?

- Formal: on the real 10,721-PRCS AndroZoo corpus, do the same trends hold as on the fixtures?
- Instrument: `pipeline.run_corpus`, real APK inputs, full re-run of the matrix.

## Q8. Does human judgment agree with the automated metrics?

- **Reserved for the final gate.** Instrument: [RESEARCH_APP.md](RESEARCH_APP.md) study packet, blind A/B PPG vs Code2Seq baseline. Wilcoxon / McNemar / Krippendorff alpha not yet implemented; that is part of executing the gate.

## Non-goals

- Formalizing a soundness proof for the taint analysis. The plan explicitly asks for heuristic reach; soundness is a separate research direction.
- Beating state of the art on generic code captioning. The captions are about privacy behavior, not general code summarization.
- Building a production classifier. The RGCN + labels are research prototypes; deployment would need Gate G1 human labels at scale and calibrated per-label thresholds.
