# Developer User Study — Protocol (template)

> Build-around for **Gate G3**. This is the instrument; running it with human subjects is the gate.
> Obtain IRB/ethics approval before recruiting.

## Research questions
- **RQ1 (accuracy):** Do developers judge the generated privacy captions as *accurate* descriptions
  of what the code does with personal data?
- **RQ2 (usefulness):** Would developers *include* the generated caption/policy text in their app's
  privacy notice?
- **RQ3 (contribution):** Do PPG+ConvGNN captions outperform the **Code2Seq baseline** on
  accuracy/clarity/completeness (blind A/B)?

## Design
- Within-subjects, blind A/B. Each PRCS is shown with two candidate captions in random order:
  condition `ppg` (this system) and condition `baseline` (Code2Seq). Participants do not know which.
- Participants: ≥ 12 Android developers (power for a within-subjects Wilcoxon on 3 Likert items).
- Each participant rates a balanced subset (e.g., 15–20 PRCS) to cap session length ≈ 30 min.

## Per-item task
Shown: the code snippet (PRCS) + a candidate caption. Rate 1–5:
- **accuracy** — does the caption correctly describe the data behavior?
- **clarity** — is it understandable to a non-expert user?
- **completeness** — does it cover what is collected, how used, and with whom shared?
- **would_include** (yes/no) — would you put this in your privacy notice?
Free-text comments optional.

## Measures / analysis
- Per-condition means + 95% CI for each Likert item; Wilcoxon signed-rank `ppg` vs `baseline`.
- Inter-rater agreement (Krippendorff's α or mean pairwise |Δ|) per item.
- `would_include` rate per condition (McNemar's test).
- The ingestion script (`ingest_ratings.py`) computes these from returned sheets.

## Materials produced by `build_study.py`
- `study_packet.md` (human-readable tasks), `study_tasks.json` (machine), `ratings_template.csv`.
