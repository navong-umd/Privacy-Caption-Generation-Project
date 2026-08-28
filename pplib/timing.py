"""
Purpose: Small timing / memory instrumentation for pipeline stages (Phase 20).
Input:   stage name plus an optional record dict.
Output:  StageTiming rows carrying wall clock, peak memory, and any extra metrics
         the caller wants to attach.

The plan puts performance analysis after correctness. This module is the harness:
every stage of pipeline.run_pipeline can wrap its call in `stage_timer` and the
resulting rows land in one JSON file for Phase 21 / Phase 22 to summarize. No
optimization here, only measurement.
"""
from __future__ import annotations

import json
import time
import tracemalloc
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class StageTiming:
    """One timed pipeline stage.

    stage:            short name (e.g. 'ppg_build', 'prcs_extract', 'convgnn_train').
    wall_seconds:     total wall clock elapsed inside the timer.
    peak_kb:          peak Python-visible memory (via tracemalloc).
    extra:            arbitrary metrics the caller attaches (e.g. n_nodes, n_paths).
    error:            populated when the timed block raised; wall_seconds captures partial time.
    """

    stage: str
    wall_seconds: float
    peak_kb: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@contextmanager
def stage_timer(stage: str, rows: List[StageTiming],
                measure_memory: bool = True) -> Iterator[Dict[str, Any]]:
    """Time a pipeline stage. Append a StageTiming row on exit whether or not the body raised.

    Yields a mutable dict that the caller can populate with extra metrics; it lands in
    `row.extra`. On an exception the row still lands and the exception is re-raised.
    """
    extra: Dict[str, Any] = {}
    started_ok = False
    error = ""
    peak_kb: Optional[int] = None
    if measure_memory:
        try:
            tracemalloc.start()
            started_ok = True
        except RuntimeError:
            started_ok = False
    start = time.perf_counter()
    try:
        yield extra
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        raise
    finally:
        elapsed = time.perf_counter() - start
        if started_ok:
            try:
                _, peak = tracemalloc.get_traced_memory()
                peak_kb = int(peak / 1024)
            finally:
                tracemalloc.stop()
        rows.append(StageTiming(
            stage=stage,
            wall_seconds=round(elapsed, 6),
            peak_kb=peak_kb,
            extra=dict(extra),
            error=error,
        ))


def write_timing_report(rows: List[StageTiming], path: str | Path) -> Path:
    """Write timings to JSON. Sorted keys for byte-stable diffs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = [r.to_dict() for r in rows]
    p.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return p


def summarize(rows: List[StageTiming]) -> Dict[str, Any]:
    """Aggregate across all rows: total wall clock, per-stage total + count."""
    total = sum(r.wall_seconds for r in rows)
    by_stage: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        b = by_stage.setdefault(r.stage, {"count": 0, "wall_seconds": 0.0,
                                          "peak_kb_max": 0, "errors": 0})
        b["count"] += 1
        b["wall_seconds"] += r.wall_seconds
        if r.peak_kb is not None:
            b["peak_kb_max"] = max(b["peak_kb_max"], r.peak_kb)
        if r.error:
            b["errors"] += 1
    return {"total_wall_seconds": round(total, 6),
            "by_stage": by_stage,
            "n_rows": len(rows)}
