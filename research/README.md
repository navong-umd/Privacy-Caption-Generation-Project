# Research Documentation Index

Every research-facing document produced during the Phase 0 through Phase 22 waterfall lives in this directory. Read them in the order below for the smoothest tour.

Numbers are not in this index. Numbers live only in `manifest.json` files under `experiments/EXP???/` after real runs. `RESULTS.md` renders them once they exist.

## Read in this order

1. [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md) — the questions the project is trying to answer.
2. [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) — top-level architecture, one page.
3. [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) — every subsystem, canonical vs legacy, what to touch first (Phase 0).
4. [ENVIRONMENT.md](ENVIRONMENT.md) — reproducible interpreter + deps + CI.
5. [STATIC_ANALYSIS_PIPELINE.md](STATIC_ANALYSIS_PIPELINE.md) — APK to APG.
6. [APG_SCHEMA.md](APG_SCHEMA.md) — the App Property Graph contract.
7. [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) — Android privacy knowledge base.
8. [PPG_SCHEMA.md](PPG_SCHEMA.md) — the Privacy Property Graph overlay.
9. [PRIVACY_TRAVERSAL.md](PRIVACY_TRAVERSAL.md) — source-to-sink taint analysis.
10. [PRCS_SCHEMA.md](PRCS_SCHEMA.md) — per-flow Privacy-Relevant Code Slice.
11. [PACT_SCHEMA.md](PACT_SCHEMA.md) — Practice + Purpose labels.
12. [DATASET.md](DATASET.md) — ADPPG dataset assembly and leak-safe splits.
    - [ANNOTATION_CODEBOOK.md](ANNOTATION_CODEBOOK.md) — how the two annotators label the PAcT test set.
13. [BASELINES.md](BASELINES.md) — rule and TF-IDF baselines.
14. [GNN_CLASSIFICATION.md](GNN_CLASSIFICATION.md) — RGCN classifier.
15. [FUSION_ABLATION.md](FUSION_ABLATION.md) — code / graph / knowledge arm matrix.
16. [CAPTION_GENERATION.md](CAPTION_GENERATION.md) — evidence-grounded LLM caption generation.
17. [LLM_EXPERIMENTS.md](LLM_EXPERIMENTS.md) — LLM condition harness A through F.
18. [CAPTION_EVAL.md](CAPTION_EVAL.md) — automated caption evaluation.
19. [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md) — error taxonomy and record schema.
20. [END_TO_END.md](END_TO_END.md) — the one canonical run command.
21. [RESEARCH_APP.md](RESEARCH_APP.md) — Nutrition Facts app and human study kit.
22. [EXPERIMENT_LOG.md](EXPERIMENT_LOG.md) — reproducible run manifests.
23. [PERFORMANCE.md](PERFORMANCE.md) — timing and memory measurement.
24. [FINAL_EXPERIMENTS.md](FINAL_EXPERIMENTS.md) — the eight-arm final matrix.
25. [RESULTS.md](RESULTS.md) — numbers, once the runs happen.
26. [LIMITATIONS.md](LIMITATIONS.md) — what remains unresolved.

## Rules that carried through every phase

- **Never invent numbers.** Metrics only ever come from `experiments/EXP???/manifest.json`.
- **Every claim carries provenance.** Sources, sinks, labels, taint edges, and captions all trace back to a specific catalog row or analysis rule.
- **The UI is not the research.** `step4_app` and `step4_userstudy` render and evaluate the research, they do not produce it.
- **Human evaluation is the last gate.** No human numbers ship until the very end.

## Where to look next after reading

- Repo root [README.md](../README.md) for the code-level entry points.
- [legacy/notes/](../legacy/notes/) for older narrative reports (`PROJECT.md`, `FINDINGS.md`, `FINAL_REPORT.md`) that predate this documentation set.
- `experiments/index.jsonl` for the run log (empty until real runs happen).
