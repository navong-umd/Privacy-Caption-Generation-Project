# Evidence-Grounded Caption Generation

_Phase 13 deliverable. Builds on [PRCS_SCHEMA.md](PRCS_SCHEMA.md), [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md), and [PACT_SCHEMA.md](PACT_SCHEMA.md). Implementation in [`step3_caption/generate.py`](../step3_caption/generate.py); grounding verifier at [`step3_caption/grounding.py`](../step3_caption/grounding.py); tests in [`tests/test_caption_grounding.py`](../tests/test_caption_grounding.py)._

A privacy caption exists to tell a human what an APK does with their data. The plan's absolute rule: the caption must not introduce data types, purposes, recipients, storage, or sharing behaviors that are not in the evidence.

Phase 13 pins the evidence dict, the prompt, and the grounding contract, and adds a post-hoc verifier that flags hallucination.

---

## 1. Evidence dict (`step3_caption/generate.py::_evidence`)

Every caption request is derived from one PRCS. The structured representation is:

```json
{
  "category":       "LOCATION_INFORMATION",
  "pi_type":        "user's coarse location",
  "practice":       ["Collecting", "Sharing"],
  "purpose":        ["Functionality"],
  "sink_type":      "network",
  "sink_api":       "java.net.URL->openConnection",
  "source_api":     "android.location.LocationManager->getLastKnownLocation",
  "privacy_threat": "Data Disclosure;Detecting",
  "app_package":    "com.example.locate"
}
```

Every field originates in a KB-backed classification on the PPG (Phase 4, 5) and is copied through the PRCS record (Phase 7). Nothing here is fabricated at the caption stage.

---

## 2. Prompt template

The ICL prompt (`build_prompt`) lists a handful of `(evidence -> caption)` shots from `configs/llm.yaml::icl_examples`, then asks the model to caption the current evidence. The prompt does not tell the model to hallucinate a recipient, storage location, or purpose; those must come from evidence fields.

Providers:

- `MockProvider` (default): deterministic template render straight from the evidence dict. Grounded by construction.
- `RealProvider(anthropic|openai)`: real LLM call. Can hallucinate.

Any real-provider run must be followed by the grounding verifier below before its output is trusted.

---

## 3. Grounding contract (`step3_caption/grounding.py::check_grounding`)

Given `(caption, evidence)` the verifier returns a `GroundingReport(mentions_pi, mentions_sink, contains_forbidden_recipient, passes, notes)`.

A caption **passes** when all of:

1. It mentions the PI category or one of its natural-language aliases (e.g. `LOCATION_INFORMATION -> "location", "gps", "whereabouts"`), OR the natural-language `pi_type` string directly.
2. It mentions the sink type or one of its aliases (e.g. `network -> "network", "server", "upload", "send", "http", "internet"`), OR the sink method name (last token after `->`).
3. It does not name a concrete third-party vendor that is not in the evidence's app package, source API, or sink API. The list is intentionally short and conservative (`admob`, `adsense`, `doubleclick`); expanding it is a config change, not a code change.

Each axis is reported separately so downstream consumers can weight them or surface which axis failed.

The verifier is not perfect: it can pass a caption that names the right data type but ascribes it to a wrong purpose (the purpose axis is not yet checked because the purpose vocabulary is small and often implicit). Phase 16 error analysis is where those cases get tracked.

---

## 4. Batch mode (`grounding.batch_check`)

Runs the verifier across a list of captions and returns a summary:

```json
{
  "n":                            120,
  "passed":                       104,
  "pass_rate":                    0.867,
  "mentions_pi":                  118,
  "mentions_sink":                111,
  "contains_forbidden_recipient": 3,
  "reports":                      [ { ... GroundingReport ... }, ... ]
}
```

The `reports` list preserves per-PRCS detail so error analysis can slice by failure axis.

---

## 5. Where the grounding check is wired

**Not yet wired into the pipeline drivers.** `pipeline/run_pipeline.py` and `pipeline/run_corpus.py` still emit captions without a post-hoc check. Wiring it is a small follow-up task (behind a `--verify-grounding` flag on the driver, with the summary written next to `captions.json`).

The recon flagged both this and the LLM-judge as wiring gaps in Phase 0. Phase 13 lands the verifier; Phase 15 (caption evaluation) is the natural place to wire it into the automated eval report.

---

## 6. Invariants tested

- Grounded caption ("reads location and sends over the network") passes for LOCATION + network evidence.
- Missing PI mention -> `passes = False`, note explains which axis failed.
- Missing sink mention -> `passes = False`, note explains which axis failed.
- Natural-language `pi_type` synonym alone counts as PI mention.
- Sink API method name (last token) counts as sink mention.
- Caption naming a vendor not in evidence -> `contains_forbidden_recipient = True`.
- Same vendor appearing in evidence -> allowed.
- Empty caption fails cleanly (no crash, no false pass).
- Batch mode returns the expected summary shape and pass rate.

---

## 7. What Phase 13 explicitly did NOT do

- Did not wire `check_grounding` into `pipeline/run_pipeline.py`. Belongs to Phase 15 alongside the caption-evaluation harness.
- Did not add a purpose-axis check. The purpose vocabulary is currently four buckets (`Functionality`, `Advertisement`, `Analytics`, `Other`); a mention test would either be trivial (the word appears verbatim) or over-specific (asks the LLM for a specific phrasing). Save for after G3 human ratings tell us which purpose confusions matter.
- Did not expand the forbidden-vendor list beyond three seed entries. Widening is a config change (`configs/grounding.yaml` when needed) rather than a Python change.
- Did not add semantic (LLM-based) grounding. The BLEU / ROUGE / BERTScore / LLM-as-judge axis is Phase 15's job; this Phase 13 verifier is deterministic and dependency-light so it can run in CI on every caption.
