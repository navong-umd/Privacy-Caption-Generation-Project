"""G1 tooling: annotation sheet round-trip and human-label override in build_dataset."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from pplib.io_utils import load_json
from step2_dataset.build_dataset import build_dataset
from step2_dataset.ingest_annotations import ingest_sheet
from step2_dataset.make_annotation_sheet import SHEET_COLUMNS, make_sheet


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
    human = ingest_sheet(str(sheet), str(human_path))
    assert target in human
    assert set(human[target]["practice"]) == {"Collecting", "Sharing"}
    assert human[target]["purpose"] == ["Analytics"]

    # build_dataset overrides the weak label for that PRCS with label_source=human
    prcs_dir = dataset_dir.parent / "prcs"   # dataset_dir fixture built prcs alongside
    out2 = tmp_path / "ds2"
    build_dataset(str(prcs_dir), str(out2), human_labels=str(human_path))
    recs = {json.loads(l)["prcs_id"]: json.loads(l)
            for l in (out2 / "adppg.jsonl").read_text().splitlines()}
    assert recs[target]["labels"]["label_source"] == "human"
    assert recs[target]["labels"]["weak_banner"] == ""
