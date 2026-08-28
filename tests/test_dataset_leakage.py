"""Phase 9: no PRCS or app_package leaks across train / val / test splits.

The ADPPG dataset groups records by app_package (configurable) and assigns
whole groups to a single split. This is the leak-safety guarantee the entire
research claim rests on: if test-time apps are also in training, any classifier
score is inflated by memorization.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from pplib.io_utils import REPO_ROOT
from stage4_ppg.build_ppg import build_ppg
from step2_prcs.extract_prcs import extract_prcs
from step2_dataset.build_dataset import build_dataset


@pytest.fixture(scope="module")
def built_dataset(tmp_path_factory):
    root = tmp_path_factory.mktemp("ds_phase9")
    build_ppg(
        str(REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"),
        str(REPO_ROOT / "configs" / "ppg.yaml"),
        str(root / "ppg"),
    )
    extract_prcs(str(root / "ppg"), str(root / "prcs"))
    build_dataset(str(root / "prcs"), str(root / "dataset"))
    return root / "dataset"


def _load_splits(ds_dir: Path) -> dict:
    return json.loads((ds_dir / "splits.json").read_text(encoding="utf-8"))


def _load_records(ds_dir: Path) -> list[dict]:
    return [json.loads(line) for line in (ds_dir / "adppg.jsonl").read_text(encoding="utf-8").splitlines()]


def test_splits_json_has_the_three_expected_keys(built_dataset):
    splits = _load_splits(built_dataset)
    assert set(splits) == {"train", "val", "test"}


def test_prcs_ids_are_disjoint_across_splits(built_dataset):
    splits = _load_splits(built_dataset)
    train, val, test = map(set, (splits["train"], splits["val"], splits["test"]))
    assert not (train & val), f"train/val overlap: {train & val}"
    assert not (train & test), f"train/test overlap: {train & test}"
    assert not (val & test), f"val/test overlap: {val & test}"


def test_every_prcs_id_appears_in_exactly_one_split(built_dataset):
    splits = _load_splits(built_dataset)
    records = _load_records(built_dataset)
    all_ids = {r["prcs_id"] for r in records}
    covered = set(splits["train"]) | set(splits["val"]) | set(splits["test"])
    assert all_ids == covered, f"missing from splits: {all_ids - covered}; extra: {covered - all_ids}"


def test_no_app_package_bridges_two_splits(built_dataset):
    """The whole point of grouped splits: an app is in exactly one bucket."""
    splits = _load_splits(built_dataset)
    records = _load_records(built_dataset)
    id_to_app = {r["prcs_id"]: r["app_package"] for r in records}

    bucket_of: dict[str, str] = {}
    for name in ("train", "val", "test"):
        for pid in splits[name]:
            app = id_to_app.get(pid)
            if app is None:
                continue
            prior = bucket_of.setdefault(app, name)
            assert prior == name, (
                f"app_package {app!r} appears in both {prior!r} and {name!r} (leak)"
            )


def test_splits_are_deterministic_across_two_runs(tmp_path_factory):
    """Same inputs + same seed must produce identical splits.json."""
    root = tmp_path_factory.mktemp("ds_repro")
    build_ppg(
        str(REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"),
        str(REPO_ROOT / "configs" / "ppg.yaml"),
        str(root / "ppg"),
    )
    extract_prcs(str(root / "ppg"), str(root / "prcs"))
    build_dataset(str(root / "prcs"), str(root / "ds_a"))
    build_dataset(str(root / "prcs"), str(root / "ds_b"))
    a = (root / "ds_a" / "splits.json").read_text(encoding="utf-8")
    b = (root / "ds_b" / "splits.json").read_text(encoding="utf-8")
    assert a == b, "splits.json differs across two runs with the same seed"


def test_labels_csv_has_one_row_per_prcs_and_all_label_columns(built_dataset):
    from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
    df = pd.read_csv(built_dataset / "labels.csv", dtype=str, keep_default_na=False)
    n_records = sum(1 for _ in _load_records(built_dataset))
    assert len(df) == n_records
    for l in PRACTICE_LABELS:
        assert f"practice_{l}" in df.columns
    for l in PURPOSE_LABELS:
        assert f"purpose_{l}" in df.columns
