"""Tests for Step 4 user-study instrument (build packet + ingest synthetic ratings)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from step3_caption.generate import generate_captions
from step4_userstudy.build_study import build_study
from step4_userstudy.ingest_ratings import ingest


def _build(dataset_dir: Path, tmp_path: Path):
    cap = tmp_path / "cap"
    generate_captions(str(dataset_dir), str(cap))
    out = tmp_path / "us"
    build_study(str(dataset_dir), str(cap), str(out), max_items=10)
    return out


def test_build_study_outputs(dataset_dir, tmp_path):
    out = _build(dataset_dir, tmp_path)
    assert (out / "study_tasks.json").exists()
    assert (out / "study_packet.md").exists()
    tmpl = out / "ratings_template.csv"
    assert tmpl.exists()
    rows = list(csv.DictReader(tmpl.open(encoding="utf-8")))
    # two options (A/B) per task, blank rating cells, conditions recorded for unblinding
    assert rows and all(r["accuracy_1_5"] == "" for r in rows)
    assert {r["condition"] for r in rows} <= {"ppg", "baseline"}


def test_ingest_synthetic_ratings(dataset_dir, tmp_path):
    out = _build(dataset_dir, tmp_path)
    # SYNTHETIC completed sheet (clearly fabricated FOR THE TEST ONLY, never a real result):
    # ppg rated higher than baseline so we can assert the aggregation direction.
    tmpl = list(csv.DictReader((out / "ratings_template.csv").open(encoding="utf-8")))
    completed = out / "ratings_completed.csv"
    with completed.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["participant_id", "prcs_id", "option", "condition",
                    "accuracy_1_5", "clarity_1_5", "completeness_1_5", "would_include_yn", "comments"])
        for r in tmpl:
            score = 5 if r["condition"] == "ppg" else 2
            inc = "yes" if r["condition"] == "ppg" else "no"
            w.writerow(["p1", r["prcs_id"], r["option"], r["condition"],
                        score, score, score, inc, ""])
    res = ingest(str(completed), str(out))
    assert res["conditions"]["ppg"]["accuracy_1_5"] == 5.0
    assert res["conditions"]["baseline"]["accuracy_1_5"] == 2.0
    assert res["conditions"]["ppg"]["would_include_rate"] == 1.0
    assert (out / "study_metrics.json").exists()
