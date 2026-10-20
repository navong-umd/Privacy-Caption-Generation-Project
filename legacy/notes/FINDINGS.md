# FINDINGS — notable decisions, surprises, and insights (for the paper)

## §0 — "What I Found" audit (≤20 bullets)
1. **Two existing modules**, not one: `Document Analysis Module/` (Stage 3) and
   `Static Code Analysis Module/` (Stages 1–2). `PROJECT_PLAN.md` describes the *older* Jain-2022
   framing; the actual code already implements the APG/Neo4j approach this build extends.
2. **No research-plan PDF is present in the repo** (the prompt referenced one). Source of truth
   used instead: the Stage 1–3 code + README + PROJECT_PLAN.md. (Gap — flagged for the user.)
3. **Stage 2 APG builder** = `androguard_analysis_APG_III_Update1Fixed_14.py`. Uses `AnalyzeAPK`,
   iterates internal methods, builds 4 NetworkX graphs (AST/MCG/ICFG/DDG) and loads CSV + Neo4j.
4. **APG node CSV schema:** `id,label,type,code,callee,app_id`. **Edge CSV:** `start_id,end_id,type,app_id`.
5. **APG labels:** `Method`, `Statement` in CSVs; `Class` + `HAS_METHOD` exist **only in Neo4j**
   (not exported to CSV). The adapter reconstructs them from method ids.
6. **Edge types:** HAS_STATEMENT (AST), CALLS (MCG), ICFG_NEXT (ICFG), DATA_DEPENDS (DDG).
7. **Statement.callee** = `"pkg.Class->method"` for invoke instructions — this is the **join key**
   for matching sources/sinks. `app_id = "package@apk_filename"`.
8. **DDG is built from def/use heuristics** on dalvik move/iput/sput/etc. — already a heuristic,
   so layering heuristic taint on top is consistent.
9. **Stage 3 outputs:** `personal_info_results.csv` (382 rows for the sample APK; 52 with a non-empty
   `Personal Information`, 170 with a real doc description — rest "Documentation not found.").
10. **SuSi catalog:** `formatted_sources.csv` = 17,800 rows (11,553 NO_CATEGORY), `formatted_sinks.csv`
    = 8,040 rows. Columns: `Class Name,Return Type,Method Name,Parameter Types,Category`.
11. **Reachability scripts** already do MCG BFS from entry points to a hard-coded `SENSITIVE_RULES`
    list — a good seed for the sink catalog (externalized to `configs/sinks.yaml`).
12. **Hard-coded foreign paths** (`<user-home>\...`) throughout Stage 1–3 scripts → they will not
    run as-is on this machine, and the APG `output_csv/` folder does **not** exist here. The PPG
    builder is therefore made to read a **configurable** APG dir, decoupled from Neo4j.
13. **Sample APK present** at `Static Code Analysis Module/input/APK/sample.apk` (11.9 MB).
14. **Environment:** CPython **3.14.0**; only pandas/numpy/nltk/PyYAML pre-installed. All required
    deps have verified 3.14 wheels (torch 2.12.1, torch-geometric 2.8.0, androguard 4.1.4, neo4j 6.2.0).
15. **No CSV APG outputs exist yet** on this machine — so end-to-end "today" relies on the SYNTHETIC
    fixture (and an adapter to regenerate APG from the sample APK).
16. **Codr** annotation tool is referenced as done but not in this repo tree — G1 handoff targets it.
17. **PAcT taxonomy** confirmed: Practice {Processing, Collecting, Sharing, Other}, Purpose
    {Functionality, Advertisement, Analytics, Other}; both multi-label.
18. **Assumption:** `app_id` is the grouping key for leakage-free splits; the fixture carries
    per-app `app_id` so grouped splits are testable.
19. **Assumption:** taint follows DDG primarily, with ICFG as a recall fallback and CALLS for
    inter-procedural — matching "enhanced static + heuristic" in the plan.
20. **Gap:** real ground-truth labels (G1), a real APK corpus (G4), and LLM keys (Step 3) are
    human/credential gated — built around with handoffs.

## §A — Stage 4 PPG
- **Key insight (precision):** the SuSi source catalog lists framework-**internal** class names
  (`com.android.internal.telephony.CDMAPhone->getDeviceId`), but decompiled apps call the **public**
  API (`android.telephony.TelephonyManager->getDeviceId`). Exact catalog matching therefore misses
  most real source calls. Fix: a curated **public-API `known_sources` allowlist** (high precision)
  with the SuSi catalog kept as a recall tier and `personal_info_results.csv` for NL pi-type. This
  is a genuine, reusable methods contribution — naive catalog matching under-reports sources.
- **Classification precedence** matters: curated source → explicit catalog sink → SuSi-recall source
  → heuristic sink. Without it, noisy SuSi entries (e.g. `getOutputStream` listed as NETWORK source)
  steal statements that are really sinks, deflating sink/flow counts.
- **Inter-procedural taint needs CALL-RET**, not just CALL-ARG: a getter that holds a source returns
  the tainted value to its call sites. Modeling only argument-flow misses the common
  "helper returns PI, caller ships it" pattern (validated by the synthetic inter-procedural flow).
- **Heuristic unknown-sink detection** (external callee + egress verb in method name) is required by
  the plan to catch sinks outside the catalog; kept configurable in `sinks.yaml`.

## §C — ADPPG dataset
- **Leakage-free splits must group by APK**, not by PRCS — flows from one app share SDK code and
  structure, so a random PRCS split would inflate metrics. With <3 apps the split is degenerate
  (handled: large fixture has 8 apps → real 36/6/6).
- The WEAK labeler is a near-deterministic function of (sink_type, SDK package). That means a GNN
  can essentially *memorize* it — which is exactly why bootstrap metrics are high yet meaningless,
  and why the BOOTSTRAP banner is non-negotiable until G1.

## §D — ConvGNN
- **HeteroData vs. homogeneous+edge_type:** chose homogeneous `Data` with an integer `edge_type`
  and `RGCNConv(num_relations)`. PRCS graphs are small/sparse (≈8–12 nodes, 7 relation types);
  HeteroData would add per-type message-passing plumbing for no accuracy gain at this scale. RGCN
  over typed edges preserves relation-awareness. (Deviation from the literal HeteroData ask, justified.)
- **Feature layout is fixed & documented** (type embedding ⊕ [is_source,is_sink,permission,
  sink-type 1-hot, PI-category 1-hot, 8-dim zero token-hook]) so a future statement-token encoder
  drops into the reserved slot without reshaping the model.
- **pos_weight matters** even on the bootstrap: Practice labels are imbalanced (Sharing≈⅔,
  Other≈0); clamping pos_weight to [0.1,10] keeps BCE stable on tiny batches.
- Bootstrap result (WEAK, not real): practice micro-F1 0.97 / macro-F1 0.71; purpose 0.86 / 0.62.
  High micro-F1 reflects the GNN learning the heuristic, not real privacy semantics.

## §I — Real-APK validation (scale)
- The APG adapter ran on the bundled real APK — it is the **F-Droid client** (`org.fdroid.fdroid`):
  **18,427 classes, 98,724 methods, 1,528,774 statements, 413,897 CALLS, 1,509,885 ICFG, 286,602 DDG**
  (androguard XREF build ≈34 s; total a few minutes). Confirms the Neo4j-free adapter mirrors Stage 2.
- **Real-data robustness bug found + fixed:** decompiled smali `code`/`callee` strings contain NULL
  bytes / control chars, which lxml's GraphML writer rejects (`ValueError: All strings must be XML
  compatible`). Fix: write the pickle first (authoritative, robust), sanitize all attrs for GraphML
  via a codepoint filter, and wrap GraphML in try/except so the pipeline never aborts on it. CSV
  export (pandas) is unaffected. This only surfaces on real APKs, not the synthetic fixture — a good
  argument for always smoke-testing on a real APK.
- **Scale note:** taint is depth-capped (`max_depth`), so per-source BFS stays bounded even on a
  1.5M-statement graph; this is what keeps a real APK tractable without a full points-to analysis.
- **Real PPG result (F-Droid):** 206 PI sources, 11,639 sinks, **632,178 source→sink taint paths**,
  1.66M PPG nodes, 4.32M edges. Example: `ConnectivityMonitorService.getNetworkState → okhttp3
  RealConnection` (network, 8 hops) — a genuine network-egress flow.
- **KEY FINDING — heuristic taint over-generates at scale.** 206 sources × depth-25 BFS with the
  ICFG-fallback + inter-procedural CALL-RET rules yields 632K source→sink pairs (many sharing one
  source, e.g. one `getNetworkState` reaching thousands of okhttp sinks). This is fine on the
  synthetic fixture but explodes on a real app, and 1:1 PRCS extraction (one JSON per path) would be
  impractical. **Mitigations for next iteration (config-ready):** (a) keep `follow_icfg:false` for
  precision on large apps; (b) dedup paths by (source_method, sink_method); (c) rank/keep top-k
  shortest paths per source; (d) require the sink to be data-dependent on the source (DDG-only),
  not merely ICFG-reachable. These are precision knobs, not correctness fixes — the over-approx is
  intentional for recall but must be tightened before mass PRCS extraction (ties into G4 scale-out).
- **Mitigation quantified:** enabling `dedup_by_method` (one path per source/sink method pair) cut
  F-Droid from **632,178 → 235,304 paths (-63%)** with no loss of distinct method-level flows.
  Adding `max_paths_per_source: 25` bounds it to <= 206x25 ~ 5,150, and `follow_icfg:false` trims
  further toward DDG-only data flows — composed, these yield a PRCS count suitable for annotation.

## §Display — what_it_does + Neo4j
- **Every node needs meaning, not just code.** A graph of raw smali is unreadable. Generating a
  deterministic `what_it_does` per node (role-aware template) makes the PPG legible offline and at
  scale; the LLM hook is reserved for salient (source/sink/tainted) nodes so cost stays bounded on
  million-node real PPGs. LLM-derived text is tagged `what_it_does_src=llm:<provider>` — never
  silently mixed with rule-based text.
- **Cypher as the slicing interface.** Taint slicing maps cleanly onto variable-length path patterns
  (`(:Statement{id:$src})-[:TAINT_FLOW*1..25]->(:Statement{id:$sink})`), matching the property-graph
  paper's subgraph-query style. Per-app isolation via `app_id` lets many apps share one instance.

## §Stage8 — Privacy Nutrition Facts
- **Risk must be transparent, not a black box.** The risk indicator is a documented additive rule over
  *statically detected* facts (egress, identifier access, sensitive categories) plus purpose labels;
  it prints its factors and carries the BOOTSTRAP banner whenever a purpose label is weak. It is framed
  as a heuristic indicator, explicitly "not a security audit" — avoids fabricating a security score.
- **Lightest stack = stdlib static HTML.** For an offline-first, test-without-keys repo, a static
  generator beats Flask/JS: one command, zero deps, opens in any browser, data stays as plain JSON.

## §G2 — first preliminary real metric on real apps
- After LLM-assisted labeling of the 100-flow TikTok held-out test split, retraining gave the first
  banner-cleared metric: **practice micro-F1 0.848 / macro-F1 0.584 / subset-acc 0.620; purpose
  micro-F1 0.847 / macro-F1 0.258 / subset-acc 0.830** (train 7591 weak / val 2712 weak / test 100).
- **Purpose macro-F1 is low by construction:** the test split is ~84% Functionality, ~16% Analytics,
  ~0% Advertisement, so macro-F1 (which averages per-class incl. empty classes) is pulled down while
  micro-F1 and subset-accuracy are healthy. A balanced labeled set is needed before macro-F1 is
  meaningful — a concrete argument for the G1 annotation push to cover rare purposes.
- **Integrity caveat (decisive for the paper):** the "human" test labels here are **LLM-annotated,
  not human-verified**. Two independent LLM passes agreed 95.1% (135/142); 13 rows are in the
  human-review shortlist. These numbers are a *preliminary pipeline result*, not ground truth, until a
  human checks the shortlist + a random sample so human-LLM Cohen's kappa can be reported and disclosed.

## §Captions — real LLM captions beat the Code2Seq baseline (LLM-judged)
- Generated real captions with **OpenAI gpt-4o** (the supplied key was OpenAI; `--provider openai`
  routed through the same pluggable interface, zero code change). 350 captions over the 7 real apps.
- **LLM-as-judge** (`step4_eval/caption_judge.py`, automated stand-in for missing human references):
  on a 70-caption sample the PPG-informed LLM captions scored **accuracy 4.59/5, readability 4.56/5**
  vs the Code2Seq baseline's **2.74 / 2.23**, and were preferred **70/70 (100%)** in blind pairwise.
  Banner: LLM-JUDGED (not human ratings) — a strong directional signal for RQ "is the PPG→LLM caption
  better than code2seq", to be confirmed by the G3 human study. Example (Twitter db-info→network):
  LLM "This app accesses your database information... processes and shares this data over the network..."
  vs baseline "getCount value flows to applyAndAckSettings; app appears to share this data."

## §Ablation — the PPG privacy overlay helps classification (real, non-bootstrap)
- Same ConvGNN / same splits+seed, node features WITH vs WITHOUT the privacy overlay (APG-only =
  node-type embedding + graph structure, overlay vector zeroed via `load_splits(privacy_features=False)`).
  On the 100-flow human-labeled TikTok test split (banner cleared): **overall macro-F1 0.421 (full PPG)
  vs 0.396 (APG-only), Δ +0.025**, and the overlay helps on ALL four metrics (practice macro +0.021,
  purpose macro +0.030, practice micro +0.016, purpose micro +0.007). `privacy_overlay_helps=true`.
- This is the empirical core of the novelty claim (PPG > APG-only). Margin is modest but consistent;
  a balanced human-labeled set + the reserved statement-token encoder should widen it. Directional
  until human-verified labels (same caveat as G2), but it is computed on the non-weak test split.

## §Token-encoder — a naive statement-token hook hurts at bootstrap scale (negative result)
- Filled the reserved `TOKEN_HOOK_DIM` slot with a hashing-trick bag-of-tokens over each node's
  code+callee (camelCase/identifier split, L1-normalized). On the 100-flow human-labeled test it
  **lowered** practice macro-F1 (0.584 → 0.415) and purpose (0.259 → 0.228). Reason: an 8-dim hashed
  token vector is collision-heavy and, on ~100 test graphs with weak-supervised training, injects noise
  rather than lexical signal. Kept **`token_features=False` by default** (all recorded results are the
  no-token setting). The hook is implemented + tested so a *learned* code-token embedding can drop into
  the same slot later — but the cheap hashing version is a documented dead end at this scale.

## §Review — adversarial self-review caught 5 real bugs
- A find→verify workflow (16 agents) over the 6 new modules surfaced 10 findings; the verify pass
  confirmed 5 and rejected 5. All 5 were genuine: cache dropped LLM provenance (reported "cache" not
  "llm:<prov>"); tainted relay nodes lost their PI category; nutrition `third_parties` listed on-device
  sinks (Gson/FileIO/Log/SQLite) as ad/analytics recipients (missing egress gate); the judge's JSON
  extraction was greedy and its score coercion could crash on non-int model output. Lesson: unit tests
  passed on all 6 yet three bugs only manifested on real pipeline data / the optional LLM path — a
  reminder to review against the real data model, not just the fixture.
