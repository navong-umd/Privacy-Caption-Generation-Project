"""Phase 19: experiment manifest schema + save / load / index."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from pplib.experiment import (
    EXPERIMENT_SCHEMA_VERSION,
    ExperimentRun,
    INDEX_FILENAME,
    MANIFEST_FILENAME,
    current_code_version,
    digest_configs,
    digest_dataset,
    list_experiments,
    load_experiment,
    save_experiment,
    validate_experiment,
)


def _run(exp_id="EXP001", name="rgcn full ppg baseline") -> ExperimentRun:
    return ExperimentRun(
        exp_id=exp_id,
        name=name,
        code_version="Ali-F/Branch@abc1234",
        config_digest="0" * 40,
        dataset_digest="1" * 40,
        seed=13,
        metrics={"practice_macro_f1": 0.71, "purpose_macro_f1": 0.62},
        artifacts=["convgnn/best.pt", "convgnn/metrics.csv"],
        model_version="rgcn v0.4",
        notes="baseline full ppg on synthetic fixture",
    )


def test_schema_version_pinned():
    assert EXPERIMENT_SCHEMA_VERSION == "1.0.0"


def test_validate_accepts_valid_record():
    validate_experiment(_run().to_dict())


def test_validate_rejects_missing_field():
    d = _run().to_dict()
    d.pop("metrics")
    with pytest.raises(ValueError, match="metrics"):
        validate_experiment(d)


def test_validate_rejects_bad_exp_id():
    d = _run(exp_id="foo").to_dict()
    with pytest.raises(ValueError, match="exp_id"):
        validate_experiment(d)


def test_validate_rejects_non_dict_metrics():
    d = _run().to_dict()
    d["metrics"] = ["not a dict"]
    with pytest.raises(ValueError, match="metrics"):
        validate_experiment(d)


def test_save_writes_manifest_and_appends_index(tmp_path):
    root = tmp_path / "experiments"
    manifest = save_experiment(_run("EXP001"), root)
    assert manifest.name == MANIFEST_FILENAME
    assert (root / "EXP001" / MANIFEST_FILENAME).exists()
    assert (root / INDEX_FILENAME).exists()

    entries = list_experiments(root)
    assert len(entries) == 1
    assert entries[0]["exp_id"] == "EXP001"


def test_save_is_idempotent_for_same_exp_id(tmp_path):
    root = tmp_path / "experiments"
    save_experiment(_run("EXP001", name="v1"), root)
    save_experiment(_run("EXP001", name="v2"), root)
    entries = list_experiments(root)
    assert len(entries) == 1
    assert entries[0]["name"] == "v2"


def test_two_experiments_indexed_side_by_side(tmp_path):
    root = tmp_path / "experiments"
    save_experiment(_run("EXP001"), root)
    save_experiment(_run("EXP002"), root)
    entries = list_experiments(root)
    ids = {e["exp_id"] for e in entries}
    assert ids == {"EXP001", "EXP002"}


def test_load_experiment_returns_the_manifest(tmp_path):
    root = tmp_path / "experiments"
    save_experiment(_run("EXP001"), root)
    loaded = load_experiment(root, "EXP001")
    assert loaded["exp_id"] == "EXP001"
    assert loaded["metrics"]["practice_macro_f1"] == 0.71


def test_load_missing_experiment_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_experiment(tmp_path, "EXP999")


def test_digest_configs_is_stable(tmp_path):
    a = tmp_path / "a.yaml"
    a.write_text("foo: 1\n", encoding="utf-8")
    b = tmp_path / "b.yaml"
    b.write_text("bar: 2\n", encoding="utf-8")
    d1 = digest_configs([a, b])
    d2 = digest_configs([b, a])   # order should not matter, we sort
    assert d1 == d2
    a.write_text("foo: 2\n", encoding="utf-8")
    assert digest_configs([a, b]) != d1


def test_digest_dataset_stable_across_reads(tmp_path):
    (tmp_path / "adppg.jsonl").write_text('{"prcs_id": "x"}\n', encoding="utf-8")
    (tmp_path / "splits.json").write_text('{"train": ["x"]}', encoding="utf-8")
    d1 = digest_dataset(tmp_path)
    d2 = digest_dataset(tmp_path)
    assert d1 == d2
    assert len(d1) == 40


def test_current_code_version_returns_string_or_unknown():
    v = current_code_version()
    assert isinstance(v, str)
    assert v == "unknown" or "@" in v


def test_manifest_json_is_sorted_and_deterministic(tmp_path):
    root = tmp_path / "experiments"
    save_experiment(_run("EXP001"), root)
    text_a = (root / "EXP001" / MANIFEST_FILENAME).read_text(encoding="utf-8")
    save_experiment(_run("EXP001"), root)
    text_b = (root / "EXP001" / MANIFEST_FILENAME).read_text(encoding="utf-8")
    assert text_a == text_b   # byte-stable across saves of the same run
