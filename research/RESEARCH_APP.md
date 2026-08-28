# Research App and User-Study Surface

_Phase 18 deliverable. Companion to [END_TO_END.md](END_TO_END.md), [CAPTION_GENERATION.md](CAPTION_GENERATION.md), and [CAPTION_EVAL.md](CAPTION_EVAL.md). Implementation in [`step4_app/`](../step4_app/) and [`step4_userstudy/`](../step4_userstudy/); smoke tests in [`tests/test_research_app.py`](../tests/test_research_app.py)._

The research-facing surfaces are for demonstration and evaluation, not for research. Nothing in this phase produces a claim by itself: the app renders artifacts already computed upstream, and the study packet is a rating instrument that humans fill in.

**The UI is not the research.** It is where the research is inspected, presented, and gated.

---

## 1. Two surfaces

`step4_app/` and `step4_userstudy/` do different jobs:

| Surface | Purpose | Human role |
|---------|---------|-----------|
| `step4_app/` | Static Privacy Nutrition Facts site rendered from `data/dataset/adppg.jsonl` + `data/captions/captions.json`. One index page listing every app in the corpus, one detail page per app. | Reader: opens the site, inspects one app's privacy elements. |
| `step4_userstudy/` | Blind A/B rating packet comparing the PPG-informed LLM caption against the Code2Seq baseline caption on the same PRCS. Order-balanced across tasks. | Annotator: fills the ratings sheet; the ingester scores the results. |

They share the same PRCS records but different output shapes. Nothing in the app writes a rating; nothing in the study packet generates content beyond the shots the humans are supposed to score.

---

## 2. `step4_app/build_app.py`

Entry: `build_app(dataset_dir, captions_dir, out_dir)`.

Reads:
- `dataset_dir/adppg.jsonl` for the PRCS records.
- Optional `captions_dir/captions.json` for the LLM captions (grouped by PRCS).

Writes:
- `out_dir/index.html`: app picker across every `app_package` in the dataset.
- `out_dir/<package>.html`: one detail page per app with the app's Privacy Elements (PI categories collected, purposes, sinks, threat tags) and its captions.
- `out_dir/_data/` : the per-app JSON payload the page uses (kept next to the HTML so the site is self-contained).

Rendering is stdlib-only (no JS bundler, no framework). Opening `index.html` in a browser is the whole install. Neo4j Cypher for the same graph slice is emitted as text alongside each app so a reviewer with a Neo4j instance can paste-and-inspect.

**Not interactive.** No filtering, sorting, or search yet. The recon flagged that as a follow-up in [CODEBASE_ARCHITECTURE.md §5](CODEBASE_ARCHITECTURE.md#5-missing-research-components).

---

## 3. `step4_userstudy/build_study.py`

Entry: `build_study(dataset_dir, captions_dir, out_dir, seed=13, per_app_cap=6)`.

Reads:
- `dataset_dir/adppg.jsonl` for PRCS metadata (source / sink / method / class).
- `captions_dir/captions.json` for both captions (LLM and Code2Seq baseline).

Writes:
- `out_dir/study_tasks.json`: `{tasks: [...], instrument: ...}`. Each task has `option_1` and `option_2` blocks with `condition` (one is `ppg`, one is `baseline`); order is balanced across tasks with a fixed seed.
- `out_dir/study_packet.md`: human-readable packet explaining the task, tied to `protocol.md` (in the module directory) for the instructions and `consent_template.md` for the consent form.
- `out_dir/ratings_template.csv`: blank rows the annotator fills in. Columns: `participant_id`, `prcs_id`, `option`, `condition`, plus the rating fields the sheet declares.

`per_app_cap` bounds the number of tasks per app so no single app dominates.

Consent + protocol are static templates checked into the module (`step4_userstudy/consent_template.md`, `protocol.md`). The build reproduces them by reference; humans customize them per study.

---

## 4. `step4_userstudy/ingest_ratings.py`

Reads a completed `ratings.csv` (fills of the blank template) and produces:

- Per-condition rating means (`ppg_llm` vs `code2seq_baseline`).
- A pairwise `|delta|` proxy across matched tasks (mean absolute difference per rating axis).

The recon flagged the promised statistical tests (Wilcoxon signed-rank / McNemar / Krippendorff alpha) as not yet implemented. They belong to the final human-eval gate, not to this phase.

---

## 5. Boundary between research and demo

Rule (mirroring the plan verbatim):

> The UI is NOT the research. It is a demonstration and evaluation surface for the research system. Do not allow frontend work to delay core analysis / model development.

Concretely:

- Every field the app renders originates in `adppg.jsonl` (Phase 7 PRCS schema). Nothing is fabricated at render time.
- Every caption compared in the study came from either `step3_caption/generate.py` or `step3_caption/code2seq_baseline.py` under `configs/llm.yaml` and the current model checkpoint. Reruns are reproducible.
- No rating is emitted by any of these modules. Humans fill the sheet; `ingest_ratings.py` reads it.

---

## 6. Invariants tested

- `build_app` on the synthetic fixture produces `index.html` and at least one per-package page, plus the `_data/` payload.
- `build_study` on the same fixture produces `study_tasks.json` with well-formed `option_1` / `option_2` blocks, `study_packet.md`, and a blank `ratings_template.csv` with the expected header row.
- Every study task's two options carry distinct `condition` strings.
- Every task's `prcs_id` is present in the underlying dataset.

---

## 7. What Phase 18 explicitly did NOT do

- Did not add filtering / sorting / search to the app. Belongs to a later frontend pass; the plan explicitly parks frontend investment behind core analysis and model work.
- Did not implement the statistical tests promised in `protocol.md`. Belongs to the final human-eval gate.
- Did not rewire the Nutrition app to consume `caption_eval.json` output. Aggregated eval belongs to Phase 21 numbers; the demo site should not decorate itself with unfinished metrics.
- Did not move `consent_template.md` and `protocol.md` under `configs/`. They stay module-local because they are content, not configuration.
