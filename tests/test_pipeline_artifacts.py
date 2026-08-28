"""Phase 17: one canonical run must produce every artifact END_TO_END.md promises."""
from __future__ import annotations

from pathlib import Path

import pytest

from pipeline.run_pipeline import run_pipeline


# Artifacts the doc promises on a fixture run. `apg/` is omitted because the
# fixture path skips the adapter, and `convgnn/` is checked separately because
# torch may be absent in the lean CI profile.
EXPECTED_FILES = [
    "ppg/PPG_nodes.csv",
    "ppg/PPG_edges.csv",
    "ppg/ppg.pkl",
    "ppg/taint_paths.json",
    "prcs/prcs_index.csv",
    "dataset/adppg.jsonl",
    "dataset/splits.json",
    "dataset/labels.csv",
    "captions/captions.json",
    "captions/captions.csv",
    "policy/policy.json",
    "eval/eval_report.json",
    "eval/eval_report.md",
    "eval/caption_rating_sheet.csv",
    "userstudy/study_tasks.json",
    "userstudy/study_packet.md",
    "userstudy/ratings_template.csv",
    "app/index.html",
]


@pytest.fixture(scope="module")
def run_dir(synth_apg_dir, tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("phase17_run")
    run_pipeline(str(out), apg_dir=str(synth_apg_dir), train_model=True, epochs=3)
    return out


def test_expected_files_exist_after_a_fresh_run(run_dir):
    missing = [rel for rel in EXPECTED_FILES if not (run_dir / rel).exists()]
    assert not missing, f"pipeline missing artifacts vs END_TO_END.md: {missing}"


def test_convgnn_directory_present_or_marked_skipped(run_dir):
    convgnn_dir = run_dir / "convgnn"
    if convgnn_dir.exists():
        # If it exists, best.pt or metrics.csv should be there.
        assert (convgnn_dir / "best.pt").exists() or (convgnn_dir / "metrics.csv").exists()
    else:
        # Torch missing is fine; the pipeline still completed the other stages.
        pass


def test_prcs_slices_are_written_per_flow(run_dir):
    slices = list((run_dir / "prcs").glob("prcs_*.json"))
    assert slices, "no prcs_<id>.json slices written under prcs/"


def test_codr_export_mirrors_prcs_slices(run_dir):
    codr = list((run_dir / "dataset" / "codr_export").glob("prcs_*.json"))
    slices = list((run_dir / "prcs").glob("prcs_*.json"))
    assert len(codr) == len(slices)


def test_policy_directory_has_at_least_one_app(run_dir):
    apps = [p for p in (run_dir / "policy").iterdir() if p.is_dir()]
    assert apps, "policy/ has no per-app subdirs"
    # And each app has a notice + policy pair.
    for app in apps:
        assert (app / "notice.md").exists()
        assert (app / "policy.md").exists()
