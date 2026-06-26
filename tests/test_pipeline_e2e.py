"""End-to-end smoke test: synthetic APG -> ... -> policy + eval via one driver call."""
from __future__ import annotations

from pathlib import Path

from pipeline.run_pipeline import run_pipeline


def test_pipeline_runs_end_to_end(synth_apg_dir, tmp_path):
    out = tmp_path / "run"
    s = run_pipeline(str(out), apg_dir=str(synth_apg_dir), train_model=True, epochs=3)

    # every stage produced something
    assert s["ppg"]["taint_paths"] > 0
    assert s["prcs"] > 0
    assert s["dataset"]["records"] > 0
    assert s["captions"] > 0
    assert s["policy_apps"] > 0
    assert s["userstudy_tasks"] > 0
    assert s["eval"]["bootstrap"] is True            # synthetic/weak -> banner

    # key artifacts exist on disk (cross-stage I/O contracts all satisfied)
    for rel in ["ppg/PPG_nodes.csv", "ppg/ppg.pkl", "prcs/prcs_index.csv",
                "dataset/adppg.jsonl", "dataset/splits.json", "captions/captions.json",
                "policy/policy.json", "eval/eval_report.json", "userstudy/study_tasks.json"]:
        assert (out / rel).exists(), f"missing {rel}"
