# Phase 1 reproducible environment: the file-only pipeline (79 tests + synthetic fixtures).
# Optional extras (real APK / LLM / Neo4j) are opt-in via `pip install -r requirements-<extra>.txt`
# inside the container — keep the default image lean.

FROM python:3.14-slim

WORKDIR /workspace

# System deps: libgomp1 for pytorch, git for provenance in commits/logs.
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgomp1 \
      git \
    && rm -rf /var/lib/apt/lists/*

# Install deps first so the layer is cached across source edits.
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Project source (respects .dockerignore).
COPY . .

# Default entry: run the test suite. Override for any pipeline command:
#   docker run --rm privacy-caption python -m pipeline.run_pipeline --apg data/fixtures/synthetic_apg --out /tmp/run
CMD ["pytest", "tests/", "-q"]
