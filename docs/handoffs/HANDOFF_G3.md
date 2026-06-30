# HANDOFF G3 — Developer User Study (human subjects)

**Why this is a gate:** the study measures whether developers find the generated captions
accurate/useful and whether PPG+ConvGNN beats the Code2Seq baseline. It requires **human
participants** and **IRB/ethics approval** — it cannot be automated. Everything *around* it is built.

## What is already built (no action needed)
- `step4_userstudy/protocol.md` — research questions, blind A/B design, measures, analysis plan.
- `step4_userstudy/consent_template.md` — consent form template (fill institution + IRB #).
- `step4_userstudy/build_study.py` — generates the instrument:
  ```
  python -m step4_userstudy.build_study --dataset data/dataset --captions data/captions --out data/userstudy
  ```
  → `study_packet.md` (tasks, conditions hidden), `study_tasks.json`, `ratings_template.csv` (blank).
- `step4_userstudy/ingest_ratings.py` — turns returned sheets into metrics:
  ```
  python -m step4_userstudy.ingest_ratings --ratings data/userstudy/ratings_completed.csv --out data/userstudy
  ```
  → `study_metrics.json` (per-condition Likert means, would-include rate, inter-rater agreement).

## What you do
1. Get **IRB/ethics approval**; fill the consent template.
2. Recruit ≥ 12 Android developers (see protocol for power rationale).
3. Generate the packet (command above); distribute `study_packet.md` + `consent_template.md`.
4. Collect each participant's completed `ratings_template.csv` (set `participant_id`).
5. Put the completed CSV(s) in `data/userstudy/` and run `ingest_ratings.py` over that folder.

## What I need from you
- Confirmation of IRB approval and the recruited sample size.
- The completed rating CSV(s). I will then run the analysis (Wilcoxon ppg vs baseline, McNemar on
  would-include, agreement) and write up RQ1–RQ3.

## Definition of done for this gate
`data/userstudy/study_metrics.json` exists from **real** participant ratings, with ≥ the planned
sample, and per-condition comparisons are reportable for the paper.
