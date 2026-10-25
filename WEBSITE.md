# Research Website

A read-only research site over the committed pipeline artifacts: a FastAPI backend
(`webapi/`) that serves the blessed 7-app / 10,721-PRCS corpus run, and a React +
TypeScript + Vite frontend (`frontend/`).

Every figure the site shows is read from a real artifact under `data/corpus_run/`.
Weak-label and LLM-judge results are labeled as such; nothing is fabricated.

## Prerequisites

- Python 3.14 with the pipeline deps installed, plus the web deps:
  `pip install -r requirements-web.txt`
- Node.js 20+ and npm.

## 1. Backend (FastAPI)

```
# from the repo root
pip install -r requirements-web.txt
python -m webapi.build_index          # one-time: caches the PRCS index (a few minutes)
uvicorn webapi.main:app --port 8000   # add --reload for development
```

- API root redirects to Swagger UI: http://localhost:8000/docs
- OpenAPI schema: http://localhost:8000/openapi.json
- Serves a different run by pointing `RESEARCH_DATA_DIR` at another output dir
  (e.g. `data/run` for the synthetic fixture).

The index cache is written to `data/corpus_run/_webapi_cache/prcs_index.json`. It is
regenerable at any time with `python -m webapi.build_index`.

## 2. Frontend (React + Vite)

```
cd frontend
npm install
cp .env.example .env      # optional; leave VITE_API_BASE_URL empty to use the dev proxy
npm run dev               # http://localhost:5173
```

In development the Vite dev server proxies `/api`, `/docs`, and `/openapi.json` to
`http://localhost:8000`, so no CORS setup is needed. For a production build:

```
npm run build             # tsc + vite build -> frontend/dist
npm run preview           # serve the built site locally
```

For a production deployment where the API lives on another origin, set
`VITE_API_BASE_URL=https://your-api-host` before `npm run build`.

## Endpoints (all GET, read-only)

| Path | Purpose |
|------|---------|
| `/api/overview` | Corpus counts, splits, headline metrics, pipeline stages, banners |
| `/api/apps`, `/api/apps/{package}` | Per-app privacy elements + policy obligations |
| `/api/prcs`, `/api/prcs/{id}` | Privacy slices (filter + paginate), full detail |
| `/api/captions` | Generated captions (real LLM or template), filter + paginate |
| `/api/results/classification` | RGCN metrics (weak-label banner) |
| `/api/results/captions` | LLM-as-judge caption evaluation |
| `/api/results/compliance` | GDPR/CCPA completeness per app |
| `/api/results/experiments` | Experiment-log status (honest "none logged yet") |
| `/api/docs`, `/api/docs/{slug}` | The `research/*.md` documentation set |

## Notes

- The backend never writes to the pipeline outputs.
- Some committed artifacts contain double-encoded characters; the API repairs the
  common cases on read so the site renders clean text.
- Human evaluation and the ten-arm experiment matrix are reserved; the site shows
  their status honestly rather than placeholder numbers.
