# PROJECT.md — Privacy Caption / Policy Generation (PPG + ConvGNN)

> Durable single source of truth for the Stage 4 + Step 2–4 build.
> Living document — updated as phases land. See `LEDGER.md` for the chronological log,
> `FINDINGS.md` for notable decisions/insights, `FINAL_REPORT.md` for the wrap-up.

## 1. Overview & Goals
Given an Android **APK**, automatically generate an accurate, **GDPR/CCPA-compliant,
human-readable privacy caption → full privacy notice/policy**. The system combines
static program analysis, taint analysis, a privacy-semantic graph, a graph neural
network classifier, and LLM-based caption/policy generation.

## 2. Novelty (why this replaces code2seq / PriGen)
Prior work (PriGen, code2seq) encodes **AST paths** with a **BiLSTM** to caption code.
We instead build a **Privacy Property Graph (PPG)** — program structure (AST) + call
graph (MCG) + control flow (ICFG) + data dependence (DDG) + **taint flows** + **privacy
semantics** (sources, sinks, PI types, LINDDUN threats) — and encode it with a
**relation-aware ConvGNN (RGCN)**. The graph carries data-flow and privacy context that
linear AST paths lose, enabling **multi-label Practice + Purpose** classification that
feeds caption and policy generation.

## 3. Full Pipeline
```
 STEP 1: STATIC ANALYSIS                          STEP 2: LEARNING
 ┌─────────────────────────────────────┐   ┌──────────────────────────────────┐
 │ Stage 1  APK disassembly (androguard)│   │ PRCS   subgraph per source→sink  │
 │ Stage 2  APG: AST/MCG/ICFG/DDG       │   │ ADPPG  Practice+Purpose labels   │
 │          → CSV + Neo4j  [DONE]       │   │        (WEAK auto / human Codr)  │
 │ Stage 3  API→PI mapping (docs+NLP)   │   │ ConvGNN  RGCN → 2 multi-label    │
 │          → personal_info_results.csv │   │          heads (Practice/Purpose)│
 │ Stage 4  PPG: sources+sinks+taint+   │   └──────────────────────────────────┘
 │          LINDDUN overlay  [THIS WORK]│                  │
 └─────────────────────────────────────┘                  ▼
                  │                          STEP 3: GENERATION
                  ▼                          ┌──────────────────────────────────┐
        APG CSV ──► PPG ──► PRCS ──► ADPPG ──► caption (LLM/ICL + Code2Seq base)│
                                             │ policy/notice assembly (GDPR/CCPA)│
                                             └──────────────────────────────────┘
                                                            │
                                             STEP 4: EVALUATION
                                             ┌──────────────────────────────────┐
                                             │ classification + caption + comply │
                                             │ developer user study (instrument) │
                                             └──────────────────────────────────┘
```

## 4. Stage-by-Stage Spec

### Stage 1–3 (EXISTING — do not modify)
- **Stage 1/2** `Static Code Analysis Module/Sourcecode/.../androguard_analysis_APG_III_Update1Fixed_14.py`
  disassembles an APK with androguard and writes the APG as CSVs (`{AST,MCG,ICFG,DDG}_{nodes,edges}.csv`)
  and into Neo4j. Schema in §5.
- **Stage 3** `Document Analysis Module/` scrapes Android API docs + NLP → `personal_info_results.csv`
  (API → personal-information type). Also `formatted_sources.csv` / `formatted_sinks.csv` (SuSi catalog).

### Stage 4 — Privacy Property Graph (PPG)  ✅ this build
- **Purpose:** overlay privacy semantics on the APG: tag PI **sources**, data **sinks**,
  propagate **taint**, attach **LINDDUN(GO)** threats.
- **In:** APG CSV dir + Stage 3 catalogs. **Out:** `PPG_nodes.csv`, `PPG_edges.csv`,
  `ppg.graphml`, `ppg.pkl`, `taint_paths.json` (+ optional Neo4j).
- **How:** sources matched by signature (curated public-API allowlist → SuSi catalog →
  PI-type enrichment); sinks from an editable YAML catalog + unknown-sink heuristics;
  taint BFS over DDG/ICFG/CALLS (intra + inter-procedural); flows tagged with LINDDUN.
- **Script:** `stage4_ppg/build_ppg.py`
- **Run:** `python -m stage4_ppg.build_ppg --apg data/fixtures/synthetic_apg --config configs/ppg.yaml --out data/ppg`

### Step 2 — PRCS / ADPPG / ConvGNN
- **PRCS** `step2_prcs/extract_prcs.py` — slice a subgraph around each source→sink flow.
- **ADPPG** `step2_dataset/build_dataset.py` — WEAK heuristic labels + Codr export + APK-grouped splits.
- **ConvGNN** `step2_convgnn/train.py` — PRCS subgraph → PyG → RGCN → Practice + Purpose heads.

### Step 3 — Caption + Policy
- **Caption** `step3_caption/generate.py` — pluggable LLM (offline mock default) + Code2Seq baseline.
- **Policy** `step3_policy/assemble.py` — group captions into sections, map to GDPR/CCPA.

### Step 4 — Evaluation + User Study
- **Eval** `step4_eval/evaluate.py` — classification + caption + compliance metrics (banner-gated).
- **User study** `step4_userstudy/` — protocol, consent, rating sheet, ingestion script.

## 5. Data Schemas

### APG (Stage 2 output — verified from the script)
- **Node CSV columns:** `id,label,type,code,callee,app_id`
- **Edge CSV columns:** `start_id,end_id,type,app_id`
- **Node labels:** `Class` (Neo4j only), `Method`, `Statement`.
  - Method `id = "pkg.Class->method"`; Statement `id = "{method_id}_stmt_{i}"`.
  - Statement `callee = "pkg.Class->method"` for invoke instructions (the join key).
- **Edge types:** `HAS_METHOD` (Neo4j only), `HAS_STATEMENT`, `CALLS`, `ICFG_NEXT`, `DATA_DEPENDS`.
- **app_id** = `"package@apk_filename"`.

### PPG (Stage 4 — adds overlay)
- **Node labels:** APG labels + `DataItem`, `Source`, `Sink`, `Store`, `Component`.
- **Statement props added:** `is_source,is_sink,pi_type,permission,sink_type,privacy_threat,tainted,sdk,sdk_purpose`.
- **Edge types:** APG edges + `TAINT_FLOW` (stmt→stmt along a flow) + `PRIVACY_RELATION`
  (Statement→Source/Sink, Source→DataItem, Sink→Store/Component, Source→Sink with threat).
- **PPG_nodes.csv columns:** `id,label,type,code,callee,app_id,is_source,is_sink,pi_type,permission,sink_type,privacy_threat,tainted,sdk,sdk_purpose`
- **PPG_edges.csv columns:** `start_id,end_id,type,app_id,pi_type,privacy_threat`

### PRCS record (Step 2) — `step2_prcs/extract_prcs.py`
JSON per source→sink flow: `{prcs_id, app_package, apk_filename, class_name, method_name,
method_signature, source_api, sink_api, sink_type, pi_type, permission, privacy_threat,
hop_count, code_snippet, subgraph:{nodes,edges}}`.

### ADPPG label schema (Step 2)
Multi-label per PRCS, two heads:
`{prcs_id, labels:{practice:[...], purpose:[...]}, label_source:"weak"|"human", weak_banner}`.

### PyG graph format (Step 2 ConvGNN)
Homogeneous `torch_geometric.data.Data` with typed edges (`edge_type` per relation) for
RGCN. Node feature = type one-hot + privacy features (is_source/is_sink/pi-category/
permission/sink-type) + token-embedding hook. Graph-level `y_practice` (4) and `y_purpose` (4).

## 6. PAcT Taxonomy (both heads multi-label)
**Practice** — what the code does with data:
- `Processing` — uses/transforms PI in-app (e.g., logs, computes on it).
- `Collecting` — obtains/persists PI (e.g., reads a sensor, stores locally).
- `Sharing` — sends PI off-device or to another component/party (network, IPC).
- `Other` — privacy-relevant but none of the above.

**Purpose** — why:
- `Functionality` — core app feature.
- `Advertisement` — ad targeting/serving (third-party ad SDK).
- `Analytics` — usage tracking/measurement (analytics SDK).
- `Other` — purpose unclear/none of the above.

## 7. Repo Map (new code)
```
pplib/                 shared libs (schema, io, APG adapter)
configs/               sinks.yaml, sdk_catalog.yaml, ppg.yaml, convgnn.yaml, gdpr_ccpa_map.yaml, llm.yaml, weak_labels.yaml
stage4_ppg/            PPG build (catalogs, taint, build_ppg, neo4j_loader)
step2_prcs/            PRCS extraction
step2_dataset/         weak labeler + ADPPG dataset + splits + Codr export
step2_convgnn/         PyG data + RGCN model + training
step3_caption/         LLM/ICL caption + Code2Seq baseline
step3_policy/          policy/notice assembly
step4_eval/            evaluation harness
step4_userstudy/       user-study instrument + ingestion
pipeline/              run_pipeline end-to-end driver
data/                  apg/ ppg/ prcs/ dataset/ fixtures/
tests/                 unit + integration + e2e
adapters/              run_apg_csv.py (Neo4j-free APG generation from a real .apk)
```

## 8. Environment & Run Order
- Python **3.14.0** (matches existing). Install: `pip install -r requirements-stage4.txt`.
- Exact order (synthetic fixture; swap `--apg data/apg` for a real APK run):
```
python data/fixtures/make_synthetic_apg.py --apps 8 --out data/fixtures/synthetic_apg_large
python -m stage4_ppg.build_ppg   --apg data/fixtures/synthetic_apg_large --out data/ppg
python -m step2_prcs.extract_prcs --ppg data/ppg --out data/prcs
python -m step2_dataset.build_dataset --prcs data/prcs --out data/dataset
python -m step2_convgnn.train    --config configs/convgnn.yaml --dataset data/dataset
python -m step3_caption.generate --dataset data/dataset --out data/captions
python -m step3_policy.assemble  --captions data/captions --out data/policy
python -m step4_eval.evaluate    --dataset data/dataset --captions data/captions
# or everything at once:
python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg_large --out data/run
```

## 9. Progress Tracker
- ✅ Stage 1 Disassembly (existing)
- ✅ Stage 2 APG (existing)
- ✅ Stage 3 KB / API→PI (existing)
- ✅ Stage 4 PPG (this build)
- ✅ Step 2 PRCS extraction
- ✅ Step 2 ADPPG dataset (WEAK labels; human labels gated G1)
- ✅ Step 2 ConvGNN (trains end-to-end; real metrics gated G1/G2)
- ✅ Step 3 Caption generation (offline mock; real LLM key-gated)
- ✅ Step 3 Policy/notice assembly + GDPR/CCPA mapping
- ✅ Step 4 Evaluation harness (banner-gated; real numbers gated G1/G4)
- ✅ Step 4 User-study instrument (running it is gated G3)
- ✅ One-command pipeline + real-APK adapter
- ⬜ Human gates: G1 annotation · G2 real metrics · G3 user study · G4 APK corpus

## 10. What's Next (ordered)
1. **G1** — real human annotation in Codr → real ADPPG ground truth.
2. Train ConvGNN on real labels → **G2** real classification metrics.
3. Caption generation with a real LLM key; tune prompts.
4. Policy assembly + compliance review.
5. **G4** — Androzoo corpus for scale; retrain.
6. **G3** — developer user study.

## 11. Decisions / Assumptions / Open Questions
- **Stage 2 CSVs omit Class/HAS_METHOD** (Neo4j-only) → reconstructed in the adapter (`pplib/apg_model.py`).
- **SuSi catalog uses framework-internal class names** → added a curated public-API
  `known_sources` allowlist for precision; SuSi kept as recall tier. (See FINDINGS.)
- **Heuristic taint is an over-approximation** (ICFG fallback + inter-procedural CALL-ARG/CALL-RET) — by design.
- **WEAK labels and SYNTHETIC fixtures are bootstrap only** — never ground truth; all banner-labeled.
- Open: real APK corpus (G4), labeled-set size target (G1), LLM provider/key choice.
