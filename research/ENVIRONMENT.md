# Reproducible Research Environment

_Phase 1 deliverable. Companion to [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) §"Smallest Defensible First Milestone". Source: probe workflow `wf_125796bc-397` (imports audit, tests-collection guards, data inventory)._

Goal: `git clone` → one command → **79 green tests** on any machine, using only the deps pinned here.

---

## 1. Interpreter

**CPython 3.14.0** exactly. All wheels below were verified against this interpreter in `requirements-stage4.txt` (kept alongside the new pins for historical continuity — do not delete).

Newer 3.x point releases are untested; earlier 3.x releases are known to lack wheels for at least `torch==2.12.1`.

---

## 2. Dependencies

Runtime pins live in three places, all consistent:

| File | Purpose | Reader |
|------|---------|--------|
| `pyproject.toml` | Project metadata + `[project.dependencies]` + `[project.optional-dependencies]` groups (`dev`, `apk`, `llm`, `neo4j`, `all`). Canonical modern manifest. | `pip install .`, `pip install ".[dev,apk,llm,neo4j]"`, uv/pdm/hatch, IDEs. |
| `requirements.txt` | Same 7 core runtime pins in classic pip-freeze form. | `pip install -r requirements.txt` and CI. |
| `requirements-dev.txt` + `-apk.txt` + `-llm.txt` + `-neo4j.txt` | Opt-in extras that mirror the four optional-dependency groups in `pyproject.toml`. | `pip install -r requirements-<extra>.txt`. |
| `requirements-stage4.txt` | Historical single-file pin from before Phase 1. Retained for backward reference; matches the new files exactly. | — |

### Core runtime (needed for the file-only pipeline + all 79 tests)

Pinned in `requirements.txt` and `pyproject.toml`:

- `pandas==2.3.3`
- `numpy==2.3.5`
- `networkx==3.6.1`
- `PyYAML==6.0.3`
- `scikit-learn==1.9.0`
- `torch==2.12.1`
- `torch-geometric==2.8.0`

### Test runner (needed for CI and local `pytest`)

- `pytest==8.4.2`
- `pytest-cov==7.0.0`

### Opt-in extras (used only when the corresponding feature is enabled)

| Extra | Wheels | Reached by |
|-------|--------|-----------|
| `apk` | `androguard==4.1.4` | `python -m adapters.run_apg_csv --apk ...` — lazy import guard in `adapters/run_apg_csv.py:75`. |
| `llm` | `anthropic>=0.40,<1`, `openai>=1.50,<2` | `python -m step3_caption.generate --provider anthropic|openai` — lazy imports in `step3_caption/llm_interface.py:90,98`. |
| `neo4j` | `neo4j==6.2.0` | `python -m stage4_ppg.build_ppg --neo4j` and `python -m stage4_ppg.cypher_runner` — lazy imports in `stage4_ppg/neo4j_loader.py:24`, `cypher_runner.py:86`. |

`loguru` and `certifi` are additional transitive optional deps used solely to silence androguard log spam / verify AndroZoo TLS. Both are try/except-guarded and degrade cleanly; not pinned here.

Full audit in [CODEBASE_ARCHITECTURE.md](CODEBASE_ARCHITECTURE.md) (Phase 0).

---

## 3. Setup — three supported paths

### 3a. Fastest (Docker; fully hermetic)

```
docker build -t privacy-caption .
docker run --rm privacy-caption           # runs `pytest tests/ -q`
```

The `Dockerfile` layers `python:3.14-slim` + system `libgomp1` + `pip install -r requirements-dev.txt` + project source (respects `.dockerignore`).

### 3b. Local venv (modern; single command)

```
python3.14 -m venv .venv
source .venv/bin/activate                 # (Windows: .venv\Scripts\activate)
pip install -e ".[dev]"                   # add ",apk,llm,neo4j" for extras
pytest tests/ -q
```

### 3c. Local venv (classic; requirements files)

```
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/ -q
```

Any of these paths must produce **79 passed** on a clean clone. If it does not, treat that as a Phase 1 regression, not a local-config issue.

---

## 4. Configuration & conventions

### 4a. Environment variables

`.env` is gitignored; copy from `.env.example` and fill in:

- `ANDRO_ZOO_KEY` — required only for `adapters/fetch_androzoo.py`.
- `ANTHROPIC_API_KEY` — required only for `--provider anthropic`.
- `OPENAI_API_KEY` — required only for `--provider openai` (or openai-compatible base URLs).

Nothing in the default `pytest` path needs any of these.

### 4b. Config files (canonical, under `configs/`)

| File | Owner | Notes |
|------|-------|-------|
| `configs/ppg.yaml` | PPG builder | Phase 1 fix: `paths.apg_dir` now points at `data/fixtures/synthetic_apg` so the CLI works on a fresh clone. Adds a `neo4j:` section documenting the connection defaults (currently unread — see the note in the file). |
| `configs/sinks.yaml` | PPG sink catalog | Rule catalog; consumed by `stage4_ppg/catalogs.py::SinkCatalog`. |
| `configs/convgnn.yaml` | RGCN trainer | Consumed by `step2_convgnn/train.py`. |
| `configs/llm.yaml` | Caption provider | Default `provider: mock` — no network, no keys. |
| `configs/weak_labels.yaml` | Bootstrap labels | Consumed by `step2_dataset/weak_labeler.py`. |
| `configs/sdk_catalog.yaml` | Android SDK catalog | Consumed by `stage4_ppg/catalogs.py`. |
| `configs/gdpr_ccpa_map.yaml` | Policy mapping | Consumed by `step3_policy/assemble.py`. |
| `configs/queries.cypher` | Neo4j viewer | Rendered by `stage4_ppg/cypher_runner.py`. |
| `configs/neo4j.grass` | Neo4j display styling | Consumed by the Neo4j Browser. |

### 4c. Input / output conventions

Every module in the pipeline reads and writes through `pplib/io_utils.py` (YAML/JSON/logging) and honours the column contract in `pplib/schema.py`. Do not fork these.

Directory conventions for `data/` are inventoried in [`data/README.md`](../data/README.md) — 23 subdirectories, only `data/fixtures/` committed.

---

## 5. Logging

All modules use `pplib/io_utils.get_logger(name)` — a thin `logging.getLogger` wrapper that:

- Defaults to `INFO`.
- Emits to stderr with `%(asctime)s %(levelname)s %(name)s: %(message)s`.
- Respects the standard `LOG_LEVEL` environment variable (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

Set `LOG_LEVEL=DEBUG` for verbose PPG-builder or trainer output.

The one exception is `androguard`, which uses `loguru` and emits one line per method disassembled — `adapters/run_apg_csv.py` silences it explicitly to avoid gigabyte log files on real APKs.

---

## 6. Determinism

- **Test suite:** deterministic. No test uses randomness without seeding. `data/fixtures/*` are byte-frozen.
- **Training:** `step2_convgnn/train.py` seeds Python `random`, `numpy`, and `torch` (single default seed) but does not currently pin BLAS thread counts or torch CUDA algorithms — small numeric drift possible across machines. Model architecture, hyperparameters, and data splits are fully reproducible; loss curves may differ in the 4th decimal.
- **Data splits:** APK-grouped and deterministic — see `step2_dataset/build_dataset.py`.
- **PPG:** fully deterministic given an APG and `configs/ppg.yaml`.
- **Captions (mock provider):** deterministic template render.
- **Captions (real LLM provider):** *not* deterministic — record `temperature`, `model`, `prompt`, and full response in `data/captions/captions.json` for provenance (Phase 14 will formalize this).

---

## 7. CI

`.github/workflows/ci.yml` runs on every `push` and `pull_request`:

1. Checkout.
2. `actions/setup-python@v5` with `python-version: '3.14'`.
3. Cache pip downloads keyed on `requirements*.txt` + `pyproject.toml` hashes.
4. `pip install -r requirements-dev.txt`.
5. `pip freeze` (for reproducibility auditing in the build log).
6. `pytest tests/ -q`.

Any test failure = red build. There is no `--allow-fail` matrix.

---

## 8. Test-collection guards

`tests/test_ablation.py` imports `step2_convgnn.data` and `step2_convgnn.ablation` at module scope — both pull `torch` / `torch_geometric` at import time. A Phase 1 `pytest.importorskip("torch") / ...("torch_geometric")` guard at the top of the file means the module skips cleanly when either wheel is absent (e.g. a leaner CI profile that drops torch).

`tests/test_step2_convgnn.py` and `tests/test_step4_eval.py` already guard themselves internally.

---

## 9. Reproducing the numbers in the docs

- legacy/notes/FINAL_REPORT.md and legacy/notes/RESULTS.md report **79 tests green** and metrics from `data/corpus_run/` (10,721 PRCS across 7 real apps). All of that is regenerable with the golden-path commands in `data/README.md`.
- The README banner still says "69 green" from an earlier Phase; the correct count is 79 (verified by Phase 1 probe). Docs sweep for that mismatch is a Phase 22 finalization task; the CI build log is the authoritative source.

---

## 10. What Phase 1 explicitly did NOT do

Per the CODEBASE_ARCHITECTURE.md scope statement, none of the following are touched by this milestone:

- Any model change.
- Any new labels (G1 shortlist stays open).
- Any refactor of the module layout in `research/CODEBASE_ARCHITECTURE.md` §6.
- Any `archive/` move of the legacy `PriGenLocal/`, `legacy/document_analysis/`, or `legacy/static_analysis/` trees.
- Any wiring of the new `configs/ppg.yaml::neo4j` section into `stage4_ppg/neo4j_loader.py` (since done: uri/user come from env or this section, the password only from `NEO4J_PASSWORD`).

Those all come in later phases and depend on Phase 1 being green first.
