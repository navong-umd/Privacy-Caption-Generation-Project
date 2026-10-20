# Android Privacy Knowledge Base

_Phase 4 deliverable. Companion to [APG_SCHEMA.md](APG_SCHEMA.md). The single lookup entry point is [`pplib/knowledge.py::KnowledgeBase`](../pplib/knowledge.py); enforced by [`tests/test_knowledge.py`](../tests/test_knowledge.py)._

The knowledge base answers exactly one question for the rest of the pipeline:

> **Given an API callee string `pkg.Class->method`, what does it mean for privacy?**

Concretely: is it a Personal-Information _source_? Is it a data _sink_? Which Android permission governs it? Which third-party SDK bucket does the class belong to? And — the plan's absolute rule — **where did each of those claims come from?** No mapping is invented; every claim carries provenance.

---

## 1. Data sources (what the KB is built from)

| Layer | File | Rows loaded | Provenance |
|-------|------|-------------|------------|
| **Tier 1 — curated PI sources** | `configs/ppg.yaml::known_sources` | 16 entries | Hand-curated public-Android-API allowlist (`LocationManager.getLastKnownLocation`, `TelephonyManager.getDeviceId`, `AccountManager.getAccounts`, …). High precision. |
| **Tier 2 — SuSi source catalog** | `data/knowledge_base/formatted_sources.csv` | 17,801 rows → 6,127 unique `Class->method` after dedup + `exclude_categories` filter | SuSi (Arzt et al., 2014) — a machine-learning classifier trained on the Android framework to distinguish PI sources from generic APIs. Frozen artifact under the `legacy/document_analysis/` tree. |
| **Tier 2′ — SuSi method-name index** | Derived from Tier 2 | ~5k distinct method names | Opt-in via `configs/ppg.yaml::sources.formatted_match_by_method_name`. Matches on method name only ("`getDeviceId`" anywhere); high recall, noisy. Off by default. |
| **Tier 3 — NL personal-information enrichment** | `data/knowledge_base/personal_info_results.csv` | 383 rows (~52 with a non-empty `Personal Information` value) | Stanza dependency parse of scraped `developer.android.com/reference` descriptions; produced by `legacy/document_analysis/utils_main_api_Des_to_Info_final.py`. Cited by SourceCatalog on top of a Tier-1/2 hit — replaces the raw category with a human-readable PI type (e.g. `"user's coarse location"` instead of `LOCATION_INFORMATION`) when available. |
| **Permission map** | `configs/ppg.yaml::permission_map` | 17 entries | Hand-curated `SuSi-category → Android permission` map. `LOCATION_INFORMATION → ACCESS_FINE_LOCATION`, `UNIQUE_IDENTIFIER → READ_PHONE_STATE`, etc. Best-effort; a PScout-style permission trace is not yet implemented. |
| **Sink catalog** | `configs/sinks.yaml::rules` | ~25 rules | Hand-curated `class/method → sink_type` mapping. Match types: `exact`, `endswith`, `regex`. Sink types: `network`, `storage`, `logging`, `ipc`, `serialization`. |
| **Unknown-sink heuristic** | `configs/sinks.yaml::unknown_sink_heuristics` | 15 egress verbs | Fallback for external callees whose method name contains any of `[send, write, post, upload, put, publish, transmit, sync, flush, emit, report, track, log, store, save, persist]`. Emits `sink_type = "heuristic_unknown"`, `sink_known = False`. Skipped for internal callees. |
| **Third-party SDK catalog** | `configs/sdk_catalog.yaml` | 84 package prefixes | Package-prefix → purpose bucket. Three buckets: `advertisement` (com.google.ads, com.facebook.ads, com.applovin, …), `analytics` (com.google.firebase.analytics, com.appsflyer, com.flurry, …), `functionality` (android., androidx., java., javax., kotlin., org.json). Powers the WEAK-labeler heuristic that seeds the PAcT `purpose` head. |

Everything above ships as data files under version control (checked-in YAML under `configs/`, or frozen CSV/TXT artifacts under `data/knowledge_base/`); nothing here is computed at run time from network resources.

---

## 2. The lookup contract

One class, one method:

```python
from pplib.knowledge import KnowledgeBase

kb = KnowledgeBase()                                  # ~2s cold-load; reuse per session
hit = kb.lookup("android.location.LocationManager->getLastKnownLocation")
```

`KnowledgeBase.lookup(callee, is_internal=False)` returns a `KnowledgeHit` with:

| Field | Populated when… | Value |
|-------|-----------------|-------|
| `callee` | Always | The input string, unchanged. |
| `is_source` | Any of Tier 1/2/2′ fires | `True` |
| `pi_category` | `is_source=True` | e.g. `LOCATION_INFORMATION` |
| `pi_type` | `is_source=True` | NL type from Tier 3 if present, else `pi_category` |
| `permission` | `is_source=True` and `pi_category` is in `permission_map` | e.g. `ACCESS_FINE_LOCATION` |
| `source_tier` | `is_source=True` | `known` \| `susi` \| `susi_method` |
| `source_provenance` | `is_source=True` | Human-readable citation string — see §3 |
| `is_sink` | Any sink rule OR the egress-verb heuristic fires | `True` |
| `sink_type` | `is_sink=True` | `network` \| `storage` \| `logging` \| `ipc` \| `serialization` \| `heuristic_unknown` |
| `sink_label` | `is_sink=True` | Human label (`Log`, `HttpURLConnection`, `heuristic:sendLog`, …) |
| `sink_known` | `is_sink=True` | `True` if from a catalog rule, `False` if from the egress heuristic |
| `sdk_purpose` | Any prefix in `configs/sdk_catalog.yaml` matches the class | `advertisement` \| `analytics` \| `functionality` |

An unmatched callee comes back with `is_source=False` and `is_sink=False` — **never** with a fabricated category. This is enforced by `test_knowledge.py::test_unknown_callee_returns_empty_hit` and is the plan's "never silently invent" rule made testable.

`is_internal` controls whether the egress-verb heuristic fires. Downstream call sites (`stage4_ppg/build_ppg.py`) pass `True` when the callee resolves to a method inside the app being analysed — the heuristic is external-only.

`hit.to_dict()` returns a plain JSON-serialisable dict; the whole KB output belongs in a JSON evidence blob without further transformation.

---

## 3. Provenance — every claim cites its source

Every non-empty `KnowledgeHit` carries at least one provenance string. For sources:

| `source_tier` | `source_provenance` |
|---------------|---------------------|
| `known` | `"configs/ppg.yaml::known_sources (hand-curated public-API allowlist)"` |
| `susi` | `"data/knowledge_base/formatted_sources.csv (SuSi 17,801-signature catalog; Arzt et al. 2014)"` |
| `susi_method` | `"SuSi method-name-only match (opt-in via configs/ppg.yaml::sources.formatted_match_by_method_name; recall mode, noisy)"` |

For sinks the provenance is implicit in `sink_known` + `sink_type`: `sink_known=True` means one of the `configs/sinks.yaml::rules` matched exactly (its `label` is the citation); `sink_known=False` means the egress-verb heuristic fired (and the label is prefixed `heuristic:`).

For SDK-purpose classification the provenance is the matched package prefix — the KB internally sorts prefixes longest-first, so the most specific match wins and is recoverable by re-running the prefix comparison.

The Phase 5 PPG builder is required (and does) propagate this provenance onto every Source / Sink node it materialises — see `stage4_ppg/build_ppg.py::_source_node` and `_sink_node`. That means every downstream artifact (PRCS, caption evidence, policy notice) can trace any privacy claim back to the exact catalog row that produced it.

---

## 4. Coverage and known gaps

- **Curated allowlist** covers the 16 highest-signal public-API PI sources. Extending it (`configs/ppg.yaml::known_sources`) is cheap and always upgrades precision; extending SuSi is not (its frozen classifier).
- **Personal-information NL enrichment** is sparse — only ~52 of 382 rows in `personal_info_results.csv` have a non-empty PI value (documentation-not-found for most `androidx.*` and Google Play Services classes). SourceCatalog falls back to the raw SuSi category when NL enrichment is missing, so this only affects human-readability, not precision.
- **Sink catalog** covers the common Android sinks explicitly; the egress-verb heuristic catches most external SDK reporting APIs at the cost of `sink_known=False`. Downstream consumers may filter to `sink_known=True` when they want precision.
- **Permission map is best-effort.** A real PScout-style API→permission derivation from the Android framework source is planned but not implemented; the 17-entry `permission_map` is a research-defensible starting point but not exhaustive.
- **`legacy/document_analysis/` scripts are frozen.** The `.csv` files in `data/knowledge_base/` are load-bearing; the Python scripts that generated them (hard-coded absolute paths + a missing `esalib/` Java tool) cannot be re-run on this machine without repair. See CODEBASE_ARCHITECTURE.md §2, §5. This means the KB's raw inputs are effectively immutable until someone restores the generator pipeline.
- **No live network lookups.** The KB never touches `developer.android.com` at run time. This is deliberate: reproducibility + hermetic tests > freshness. Refreshing the catalogs is a one-off, gated by fixing `esalib/`.

---

## 5. Load numbers (as of Phase 4)

Reported by `KnowledgeBase.stats()`:

| Metric | Value |
|--------|-------|
| `curated_sources` | 16 |
| `susi_sources` | 6,127 (from 17,801 raw rows after dedup + `exclude_categories`) |
| `susi_method_index` | ~5k distinct method names |
| `personal_info_nl_enrichments` | 382 rows scanned; ~52 with a non-empty PI type |
| `sink_rules` | 25 |
| `sdk_prefixes` | 84 (advertisement + analytics + functionality_hint) |
| `permission_map_entries` | 17 |

Enforced as lower-bounds by `tests/test_knowledge.py::test_stats_are_nontrivial`.

---

## 6. Downstream consumers — what the KB feeds

- **Phase 5 PPG builder** (`stage4_ppg/build_ppg.py`) calls `SourceCatalog.classify` + `SinkCatalog.classify` (soon to be routed through `KnowledgeBase.lookup` — Phase 5 refactor task).
- **Phase 7 PRCS extractor** (`step2_prcs/extract_prcs.py`) copies the PPG's `pi_type`, `permission`, `sink_type` onto every PRCS record — no direct KB call, but every field originated here.
- **Phase 13 caption generator** (`step3_caption/generate.py::_evidence`) reads the same `pi_type` / `permission` / `sink_type` fields; the KB is the ultimate source of every "data type / recipient / purpose" claim in a caption.
- **Phase 8 policy assembler** (`step3_policy/assemble.py`) maps `pi_category` + `sink_type` to GDPR/CCPA obligations via `configs/gdpr_ccpa_map.yaml`; the KB is upstream.

Anywhere in the pipeline where an API is classified, `pplib.knowledge.KnowledgeBase.lookup` is the single, tested, provenance-carrying entry point. Do not read `formatted_sources.csv` directly from a new consumer — go through the KB.

---

## 7. What Phase 4 explicitly did NOT do

- **Did not** rewire `stage4_ppg/build_ppg.py` to call `KnowledgeBase.lookup` instead of `SourceCatalog.classify` + `SinkCatalog.classify` directly. The existing wiring works; the refactor is a Phase-5 canonicalisation task where the PPG builder is owned end-to-end. `KnowledgeBase` composes the two catalogs so new consumers can adopt the single entry point immediately.
- **Did not** regenerate `personal_info_results.csv`. Requires restoring `esalib/` (missing) to run the scripts in `legacy/document_analysis/`.
- **Did not** implement PScout-style API → permission derivation. `permission_map` remains the 17-entry hand-curated table.
- **Since done:** the frozen CSVs moved to `data/knowledge_base/` and `configs/ppg.yaml` points there.
