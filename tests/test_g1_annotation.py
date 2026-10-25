"""G1 tooling: annotation sheets and kit, ingest provenance, and label override in build_dataset."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from pplib.io_utils import load_json
from pplib.pact_schema import validate_label
from step2_dataset.build_dataset import build_dataset
from step2_dataset.ingest_annotations import ingest_sheet, retag_llm
from step2_dataset.make_annotation_sheet import KIT_COLUMNS, SHEET_COLUMNS, make_kit, make_sheet


def test_sheet_has_expected_columns(dataset_dir, tmp_path):
    sheet = tmp_path / "ann.csv"
    n = make_sheet(str(dataset_dir), str(sheet))
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    assert n == len(rows) and rows
    assert list(rows[0].keys()) == SHEET_COLUMNS
    # blank by default (no anchoring)
    assert all(r["P_Sharing"] == "" for r in rows)


def test_prefill_uses_weak_guess(dataset_dir, tmp_path):
    sheet = tmp_path / "ann_pf.csv"
    make_sheet(str(dataset_dir), str(sheet), prefill=True)
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    # at least one row pre-filled where the weak practice contained a label
    assert any(r["P_Collecting"] == "1" for r in rows)


def test_sample_is_stratified_and_capped(dataset_dir, tmp_path):
    full = tmp_path / "full.csv"
    total = make_sheet(str(dataset_dir), str(full))           # all rows
    target = max(4, total // 2)

    sub = tmp_path / "sub.csv"
    n = make_sheet(str(dataset_dir), str(sub), sample=target, seed=0)
    rows = list(csv.DictReader(sub.open(encoding="utf-8")))
    assert n == len(rows) <= target                            # capped at the budget
    assert len({r["prcs_id"] for r in rows}) == len(rows)      # unique PRCS
    # spread across apps, not all drawn from one (fixture has 8 apps)
    assert len({r["app_package"] for r in rows}) >= 2
    # sample >= total returns everything (no-op)
    assert make_sheet(str(dataset_dir), str(tmp_path / "all.csv"), sample=total + 99) == total

    # reproducible for a fixed seed
    sub2 = tmp_path / "sub2.csv"
    make_sheet(str(dataset_dir), str(sub2), sample=target, seed=0)
    assert sub.read_text(encoding="utf-8") == sub2.read_text(encoding="utf-8")


def test_ingest_and_override(dataset_dir, tmp_path):
    sheet = tmp_path / "ann.csv"
    make_sheet(str(dataset_dir), str(sheet))
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    # human marks the FIRST prcs as Collecting+Sharing / Analytics (distinct from weak)
    target = rows[0]["prcs_id"]
    for r in rows:
        if r["prcs_id"] == target:
            r["P_Collecting"], r["P_Sharing"], r["U_Analytics"] = "1", "1", "x"
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SHEET_COLUMNS)
        w.writeheader(); w.writerows(rows)

    human_path = tmp_path / "human_labels.json"
    human = ingest_sheet(str(sheet), str(human_path), annotator="ali")
    assert target in human
    assert set(human[target]["practice"]) == {"Collecting", "Sharing"}
    assert human[target]["purpose"] == ["Analytics"]
    assert human[target]["annotator"] == "ali" and human[target]["label_source"] == "human"

    # build_dataset overrides the weak label for that PRCS with label_source=human
    prcs_dir = dataset_dir.parent / "prcs"   # dataset_dir fixture built prcs alongside
    out2 = tmp_path / "ds2"
    build_dataset(str(prcs_dir), str(out2), human_labels=str(human_path))
    recs = {json.loads(l)["prcs_id"]: json.loads(l)
            for l in (out2 / "adppg.jsonl").read_text().splitlines()}
    assert recs[target]["labels"]["label_source"] == "human"
    assert recs[target]["labels"]["weak_banner"] == ""


def _mark_first_row(sheet, columns, **extra):
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    rows[0].update({"P_Collecting": "1", "U_Functionality": "1", **extra})
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader(); w.writerows(rows)
    return rows[0]["prcs_id"]


def test_ingest_requires_an_annotator(dataset_dir, tmp_path):
    sheet = tmp_path / "ann.csv"
    make_sheet(str(dataset_dir), str(sheet))
    _mark_first_row(sheet, SHEET_COLUMNS)
    with pytest.raises(ValueError, match="no annotator"):
        ingest_sheet(str(sheet), str(tmp_path / "out.json"))


def test_kit_sheets_are_disjoint_and_hide_weak_labels(dataset_dir, tmp_path):
    m = make_kit(str(dataset_dir), str(tmp_path / "kit"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    s = m["sheets"]
    assert s["overlap_ali.csv"] == s["overlap_labmate.csv"]
    overlap, solo_a, solo_b = set(s["overlap_ali.csv"]), set(s["solo_ali.csv"]), set(s["solo_labmate.csv"])
    calib = set(m["calibration_ids"])
    assert not (overlap & solo_a or overlap & solo_b or solo_a & solo_b)
    assert set(m["test_ids"]) == overlap | solo_a | solo_b and not calib & set(m["test_ids"])
    splits = json.loads((dataset_dir / "splits.json").read_text())
    assert calib <= set(splits["val"]) and set(m["test_ids"]) <= set(splits["test"])
    rows = list(csv.DictReader((tmp_path / "kit" / "solo_labmate.csv").open(encoding="utf-8")))
    assert list(rows[0].keys()) == KIT_COLUMNS and not any(c.startswith("weak_") for c in KIT_COLUMNS)
    assert {r["annotator"] for r in rows} == {"labmate"}
    # reproducible for a fixed seed
    m2 = make_kit(str(dataset_dir), str(tmp_path / "kit2"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    assert m2["test_ids"] == m["test_ids"]


def test_kit_round_trip_confidence_and_merge(dataset_dir, tmp_path):
    make_kit(str(dataset_dir), str(tmp_path / "kit"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    sheet = tmp_path / "kit" / "solo_ali.csv"
    pid = _mark_first_row(sheet, KIT_COLUMNS, confidence="2", notes="sdk sink")
    out = tmp_path / "labels.json"
    labels = ingest_sheet(str(sheet), str(out))
    assert labels[pid]["annotator"] == "ali" and labels[pid]["confidence"] == 0.67
    validate_label(labels[pid])

    other = tmp_path / "kit" / "solo_labmate.csv"
    pid2 = _mark_first_row(other, KIT_COLUMNS)
    ingest_sheet(str(other), str(out), merge=True)
    merged = load_json(out)
    assert {pid, pid2} <= set(merged) and merged[pid2]["confidence"] == 1.0


def test_merge_replaces_entries_with_the_same_prcs_id(dataset_dir, tmp_path):
    make_kit(str(dataset_dir), str(tmp_path / "kit"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    sheet = tmp_path / "kit" / "overlap_ali.csv"
    pid = _mark_first_row(sheet, KIT_COLUMNS)
    out = tmp_path / "labels.json"
    ingest_sheet(str(sheet), str(out))
    adjudicated = tmp_path / "adjudicate.csv"
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    for r in rows:
        r.update({"P_Collecting": "", "U_Functionality": "", "annotator": ""})
    rows[0].update({"P_Sharing": "1", "U_Analytics": "1"})
    with adjudicated.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KIT_COLUMNS)
        w.writeheader(); w.writerows(rows)
    ingest_sheet(str(adjudicated), str(out), annotator="adjudicated", merge=True)
    entry = load_json(out)[pid]
    assert entry["practice"] == ["Sharing"] and entry["purpose"] == ["Analytics"]
    assert entry["annotator"] == "adjudicated"


def test_kit_larger_than_the_test_split_is_an_error(dataset_dir, tmp_path):
    with pytest.raises(ValueError, match="the kit needs"):
        make_kit(str(dataset_dir), str(tmp_path / "kit"), n_calibration=2, n_overlap=100, n_solo=150)


def test_bad_confidence_is_rejected(dataset_dir, tmp_path):
    make_kit(str(dataset_dir), str(tmp_path / "kit"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    sheet = tmp_path / "kit" / "solo_ali.csv"
    _mark_first_row(sheet, KIT_COLUMNS, confidence="5")
    with pytest.raises(ValueError, match="confidence"):
        ingest_sheet(str(sheet), str(tmp_path / "out.json"))


def test_retag_llm_marks_only_untagged_entries(tmp_path):
    p = tmp_path / "human_labels.json"
    p.write_text(json.dumps({
        "prcs_old": {"practice": ["Collecting"], "purpose": ["Functionality"]},
        "prcs_new": {"practice": ["Sharing"], "purpose": ["Analytics"], "label_source": "human",
                     "annotator": "ali", "confidence": 1.0, "notes": "", "schema_version": "1.0.0"},
    }))
    assert retag_llm(str(p)) == 1
    out = load_json(p)
    assert out["prcs_old"]["label_source"] == "llm" and out["prcs_new"]["label_source"] == "human"
    validate_label(out["prcs_old"])


def test_not_personal_rows_ingest_without_labels(dataset_dir, tmp_path):
    make_kit(str(dataset_dir), str(tmp_path / "kit"), seed=0, n_calibration=2, n_overlap=2, n_solo=2)
    sheet = tmp_path / "kit" / "solo_ali.csv"
    rows = list(csv.DictReader(sheet.open(encoding="utf-8")))
    rows[0]["not_personal"] = "1"
    rows[1].update({"not_personal": "1", "P_Sharing": "1"})
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KIT_COLUMNS)
        w.writeheader(); w.writerows(rows[:1])
    entry = ingest_sheet(str(sheet), str(tmp_path / "l.json"))[rows[0]["prcs_id"]]
    assert entry["not_personal"] is True and entry["practice"] == entry["purpose"] == []
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KIT_COLUMNS)
        w.writeheader(); w.writerows(rows[1:2])
    with pytest.raises(ValueError, match="not_personal"):
        ingest_sheet(str(sheet), str(tmp_path / "l2.json"))
