"""Phase 18: step4_app and step4_userstudy render usable artifacts on the fixture."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from pplib.io_utils import REPO_ROOT
from stage4_ppg.build_ppg import build_ppg
from step2_prcs.extract_prcs import extract_prcs
from step2_dataset.build_dataset import build_dataset
from step3_caption.generate import generate_captions
from step4_app.build_app import build_app
from step4_userstudy.build_study import build_study


@pytest.fixture(scope="module")
def prepped(tmp_path_factory):
    root = tmp_path_factory.mktemp("phase18_bundle")
    build_ppg(
        str(REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"),
        str(REPO_ROOT / "configs" / "ppg.yaml"),
        str(root / "ppg"),
    )
    extract_prcs(str(root / "ppg"), str(root / "prcs"))
    build_dataset(str(root / "prcs"), str(root / "dataset"))
    generate_captions(str(root / "dataset"), str(root / "captions"))
    return root


def test_build_app_writes_index_and_per_app_pages(prepped):
    out = prepped / "app"
    build_app(str(prepped / "dataset"), str(prepped / "captions"), str(out))
    assert (out / "index.html").exists()
    html_pages = [p for p in out.iterdir() if p.suffix == ".html" and p.name != "index.html"]
    assert html_pages, "no per-app html pages"
    # The per-app JSON payload the pages read from.
    assert (out / "_data").exists()
    json_payloads = list((out / "_data").glob("*.json"))
    assert json_payloads, "no per-app JSON payloads under _data/"


def test_build_study_writes_tasks_packet_and_blank_ratings(prepped):
    out = prepped / "userstudy"
    result = build_study(str(prepped / "dataset"), str(prepped / "captions"), str(out))
    assert result["n_tasks"] > 0
    assert (out / "study_tasks.json").exists()
    assert (out / "study_packet.md").exists()
    assert (out / "ratings_template.csv").exists()


def _tasks(prepped):
    payload = json.loads((prepped / "userstudy" / "study_tasks.json").read_text(encoding="utf-8"))
    # study_tasks.json is {tasks: [...], instrument: ...}; extract tasks tolerantly.
    return payload["tasks"] if isinstance(payload, dict) else payload


def test_study_tasks_have_two_options_with_distinct_conditions(prepped):
    tasks = _tasks(prepped)
    assert tasks
    for t in tasks:
        assert "prcs_id" in t
        for k in ("option_1", "option_2"):
            assert k in t
            assert "condition" in t[k]
        c1 = t["option_1"]["condition"]
        c2 = t["option_2"]["condition"]
        assert c1 != c2, f"task {t['prcs_id']} has identical conditions {c1} on both options"


def test_study_task_prcs_ids_are_all_in_the_dataset(prepped):
    tasks = _tasks(prepped)
    ds_ids = {
        json.loads(line)["prcs_id"]
        for line in (prepped / "dataset" / "adppg.jsonl").read_text(encoding="utf-8").splitlines()
    }
    for t in tasks:
        assert t["prcs_id"] in ds_ids, f"study task references unknown prcs {t['prcs_id']}"


def test_ratings_template_has_the_expected_header(prepped):
    with open(prepped / "userstudy" / "ratings_template.csv", encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))
    for col in ("participant_id", "prcs_id", "option", "condition"):
        assert col in header, f"ratings header missing {col}"
