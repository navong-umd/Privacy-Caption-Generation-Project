"""Phase 20: stage_timer helper timings, memory, error capture, and JSON output."""
from __future__ import annotations

import json
import time

import pytest

from pplib.timing import (
    StageTiming,
    stage_timer,
    summarize,
    write_timing_report,
)


def test_stage_timer_records_wall_clock_and_peak_memory():
    rows = []
    with stage_timer("busy_stage", rows) as extra:
        extra["n_widgets"] = 3
        # Allocate something non-trivial so tracemalloc records a peak.
        buf = "x" * 10_000
        time.sleep(0.01)
    assert len(rows) == 1
    row = rows[0]
    assert isinstance(row, StageTiming)
    assert row.stage == "busy_stage"
    assert row.wall_seconds >= 0.005
    assert row.error == ""
    assert row.extra == {"n_widgets": 3}
    # peak may be None if tracemalloc was already active; either way the field must exist.
    assert row.peak_kb is None or row.peak_kb >= 0


def test_stage_timer_appends_row_on_exception_and_reraises():
    rows = []
    with pytest.raises(ValueError, match="boom"):
        with stage_timer("failing_stage", rows):
            raise ValueError("boom")
    assert len(rows) == 1
    assert rows[0].stage == "failing_stage"
    assert "ValueError" in rows[0].error
    assert rows[0].wall_seconds >= 0.0


def test_stage_timer_extra_dict_is_mutable_yielded_object():
    rows = []
    with stage_timer("meta", rows) as extra:
        extra["a"] = 1
        extra["b"] = "hello"
    assert rows[0].extra == {"a": 1, "b": "hello"}


def test_write_timing_report_produces_stable_json(tmp_path):
    rows = []
    with stage_timer("stage_1", rows) as extra:
        extra["k"] = 1
    with stage_timer("stage_2", rows) as extra:
        extra["k"] = 2
    path = write_timing_report(rows, tmp_path / "timing.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert len(payload) == 2
    for name, row in zip(("stage_1", "stage_2"), payload):
        assert row["stage"] == name
        # keys are sorted for stable diffs
        assert list(row.keys()) == sorted(row.keys())


def test_summarize_aggregates_by_stage_and_counts_errors():
    rows = [
        StageTiming(stage="ppg", wall_seconds=0.3, peak_kb=1000),
        StageTiming(stage="ppg", wall_seconds=0.1, peak_kb=2000, error="X: y"),
        StageTiming(stage="prcs", wall_seconds=0.05, peak_kb=500),
    ]
    s = summarize(rows)
    assert s["n_rows"] == 3
    assert s["by_stage"]["ppg"]["count"] == 2
    assert s["by_stage"]["ppg"]["errors"] == 1
    assert s["by_stage"]["ppg"]["peak_kb_max"] == 2000
    assert abs(s["by_stage"]["ppg"]["wall_seconds"] - 0.4) < 1e-9
    assert s["by_stage"]["prcs"]["count"] == 1
    assert abs(s["total_wall_seconds"] - 0.45) < 1e-9


def test_summarize_empty_returns_zeroes():
    s = summarize([])
    assert s == {"total_wall_seconds": 0.0, "by_stage": {}, "n_rows": 0}
