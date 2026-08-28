"""FastAPI read-only research API over the committed pipeline artifacts.

Serves the blessed corpus run (data/corpus_run/) as JSON for the research
website. Read-only: it never writes to the pipeline outputs and never
fabricates data. When an artifact is missing it says so rather than guessing.
"""

__version__ = "0.1.0"
