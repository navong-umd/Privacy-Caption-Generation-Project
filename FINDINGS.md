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
12. **Hard-coded foreign paths** (`C:\Users\2015n\...`) throughout Stage 1–3 scripts → they will not
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
