# Human gates — index & status

These are the steps that **cannot be automated** (they need your credentials, human judgement,
IRB approval, or API credits). Everything *around* each gate is built, tested, and waiting.

> Note on numbering: the build's `HANDOFF_G*.md` files were numbered in the order they were
> reached, which differs from the research-plan's gate order. This table reconciles both.

| Plan gate | What it is | Handoff file | Status |
|---|---|---|---|
| **Real APK corpus** | a corpus of real APKs (AndroZoo / F-Droid) | [HANDOFF_G4.md](HANDOFF_G4.md) | ✅ **done** — 8 APKs → 10,721 PRCS from 7 live apps |
| **Human annotation** | real Practice/Purpose ground truth (Codr / sheets) | [HANDOFF_G1.md](HANDOFF_G1.md) | 🔄 **in progress** — LLM-assisted labels staged (95.1% two-pass agreement); **you** verify the 13-row shortlist + a sample |
| **Real metrics** | non-bootstrap classification numbers | [HANDOFF_G2.md](HANDOFF_G2.md) | 🔄 **preliminary** — practice macro-F1 0.584 / purpose 0.258 on a 100-flow TikTok test (labels LLM-derived, await human check) |
| **User study** | developer + user study (blind A/B vs Code2Seq) | [HANDOFF_G3.md](HANDOFF_G3.md) | ⬜ **todo** — needs IRB approval + ≥12 developers |

## Also blocked (external, not a gate file)
- **Real-LLM captions** — the Anthropic provider is wired and verified (auth + request format OK),
  but the account returned HTTP 400 *"credit balance too low"*. **Add credits**, then:
  ```
  python -m step3_caption.generate --dataset data/corpus_run/dataset \
      --out data/corpus_run/captions_llm --provider anthropic --per-app 3
  ```
  (`--per-app`/`--limit` bound the API cost; the pipeline default stays on the offline mock.)
- **Live Neo4j display** — the Cypher library + runner work offline (`--show`); rendering the
  graph live needs a running Neo4j (`pip install neo4j`, then `build_ppg --neo4j`). See [../../DISPLAY.md](../../DISPLAY.md).

## The single most valuable next human action
Verify the LLM labels: open `data/_review_shortlist.md`, check those 13 rows + ~20 random sheet
rows. That converts the **preliminary** G2 numbers into audited ones and lets us report human–LLM
agreement (Cohen's κ) for the paper.
