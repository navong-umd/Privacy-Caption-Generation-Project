"""Unit + integration tests for Step 2 ADPPG dataset (weak labels, splits, Codr export)."""
from __future__ import annotations

import json

import pandas as pd

from pplib.io_utils import load_json
from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS
from step2_dataset.weak_labeler import WeakLabeler


def _prcs(sink_type, classes, methods=None):
    return {
        "prcs_id": "prcs_test", "sink_type": sink_type,
        "involved_methods": methods or [f"{classes[0]}->m"],
        "subgraph": {"nodes": [{"id": c, "label": "Class"} for c in classes]},
    }


def test_weak_labeler_network_ad_sdk():
    wl = WeakLabeler()
    out = wl.label(_prcs("network", ["com.google.ads.AdView"]))
    assert "Sharing" in out["practice"] and "Advertisement" in out["purpose"]
    assert out["label_source"] == "weak" and out["weak_banner"] == BANNER_WEAK


def test_weak_labeler_storage_is_collecting_processing():
    wl = WeakLabeler()
    out = wl.label(_prcs("storage", ["com.myapp.Store"]))
    assert set(out["practice"]) >= {"Collecting", "Processing"}
    assert out["purpose"] == ["Functionality"]  # first-party


def test_weak_labeler_analytics_sdk():
    wl = WeakLabeler()
    out = wl.label(_prcs("network", ["com.flurry.sdk.Agent"]))
    assert "Analytics" in out["purpose"]


def test_dataset_build_outputs(dataset_dir):
    # adppg.jsonl + splits + labels.csv + codr_export all written
    records = [json.loads(l) for l in (dataset_dir / "adppg.jsonl").read_text().splitlines()]
    assert records and all("labels" in r for r in records)
    splits = load_json(dataset_dir / "splits.json")
    assert set(splits) == {"train", "val", "test"}
    # 8 apps -> non-empty test split (leakage-free)
    assert splits["test"], "expected a non-empty test split with 8 apps"


def test_dataset_splits_are_leakage_free(dataset_dir):
    records = {json.loads(l)["prcs_id"]: json.loads(l)
               for l in (dataset_dir / "adppg.jsonl").read_text().splitlines()}
    splits = load_json(dataset_dir / "splits.json")
    # no app_package appears in more than one split
    app_of = {pid: r["app_package"] for pid, r in records.items()}
    split_apps = {s: {app_of[pid] for pid in ids} for s, ids in splits.items()}
    assert not (split_apps["train"] & split_apps["test"])
    assert not (split_apps["train"] & split_apps["val"])
    assert not (split_apps["val"] & split_apps["test"])


def test_labels_csv_is_multihot(dataset_dir):
    df = pd.read_csv(dataset_dir / "labels.csv")
    for l in PRACTICE_LABELS:
        assert f"practice_{l}" in df.columns
    for l in PURPOSE_LABELS:
        assert f"purpose_{l}" in df.columns
    assert df.filter(like="practice_").to_numpy().max() == 1


def test_codr_export_shape(dataset_dir):
    files = list((dataset_dir / "codr_export").glob("*.json"))
    assert files
    rec = load_json(files[0])
    assert {"id", "app", "code", "graph", "candidate_labels", "label_status"} <= set(rec)
    assert rec["label_status"] == "unverified"  # weak -> needs human verification
