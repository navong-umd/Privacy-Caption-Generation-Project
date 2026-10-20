"""Label provenance: LLM-assigned labels are never treated as ground truth anywhere downstream,
and the test split can be pinned to an annotated id list."""
from __future__ import annotations

import json

import pytest

from pplib.io_utils import load_json
from pplib.schema import BANNER_LLM, BANNER_WEAK, is_gold, label_banner
from step2_dataset.build_dataset import build_dataset


def _entry(source: str) -> dict:
    return {"practice": ["Collecting"], "purpose": ["Functionality"], "label_source": source,
            "annotator": "ali" if source == "human" else "some-model", "confidence": 1.0,
            "notes": "", "schema_version": "1.0.0"}


def _test_ids(dataset_dir) -> list:
    return json.loads((dataset_dir / "splits.json").read_text())["test"]


@pytest.fixture(scope="module")
def llm_dataset(dataset_dir, tmp_path_factory):
    """The fixture dataset with every test label replaced by an LLM-assigned one."""
    root = tmp_path_factory.mktemp("llm")
    labels = root / "labels.json"
    labels.write_text(json.dumps({pid: _entry("llm") for pid in _test_ids(dataset_dir)}))
    summary = build_dataset(str(dataset_dir.parent / "prcs"), str(root / "dataset"), human_labels=str(labels))
    return root / "dataset", summary


def test_only_human_labels_are_gold():
    assert is_gold("human") and not is_gold("llm") and not is_gold("weak")
    assert label_banner("human") == "" and label_banner("llm") == BANNER_LLM
    assert label_banner("weak") == BANNER_WEAK


def test_dataset_summary_counts_llm_separately(llm_dataset, dataset_dir):
    _, summary = llm_dataset
    assert summary["llm"] == len(_test_ids(dataset_dir)) and summary["human"] == 0
    assert summary["test_all_human"] is False


def test_codr_export_marks_llm_labels_unverified(llm_dataset, dataset_dir):
    ds, _ = llm_dataset
    rec = load_json(ds / "codr_export" / f"{_test_ids(dataset_dir)[0]}.json")
    assert rec["label_status"] == "unverified" and rec["note"] == BANNER_LLM


@pytest.fixture(scope="module")
def mixed_dataset(dataset_dir, tmp_path_factory):
    """Test split with one human label and the rest LLM-assigned (the normal state mid-annotation)."""
    root = tmp_path_factory.mktemp("mixed")
    ids = _test_ids(dataset_dir)
    labels = root / "labels.json"
    labels.write_text(json.dumps({pid: _entry("human" if i == 0 else "llm") for i, pid in enumerate(ids)}))
    summary = build_dataset(str(dataset_dir.parent / "prcs"), str(root / "dataset"), human_labels=str(labels))
    return root / "dataset", summary


def test_mixed_test_split_is_not_all_human(mixed_dataset):
    _, summary = mixed_dataset
    assert summary["human"] == 1 and summary["test_all_human"] is False


def test_mixed_test_split_keeps_banners(mixed_dataset, dataset_dir, tmp_path):
    pytest.importorskip("torch_geometric")
    from step2_convgnn.train import train
    from step3_caption.generate import generate_captions
    from step3_policy.assemble import assemble
    ds, _ = mixed_dataset
    assert train("configs/convgnn.yaml", str(ds), str(tmp_path / "cg"), epochs=1)["is_weak"] is True
    generate_captions(str(ds), str(tmp_path / "cap"), "configs/llm.yaml")
    summary = assemble(str(ds), str(tmp_path / "cap"), str(tmp_path / "pol"))
    test_app = next(r["app_package"] for r in map(json.loads, (ds / "adppg.jsonl").read_text().splitlines())
                    if r["prcs_id"] in set(_test_ids(dataset_dir)))
    assert summary["apps"][test_app]["weak"] is True


def test_malformed_human_entry_is_rejected(dataset_dir, tmp_path):
    entry = {**_entry("human")}
    del entry["annotator"]
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({_test_ids(dataset_dir)[0]: entry}))
    with pytest.raises(ValueError, match="annotator"):
        build_dataset(str(dataset_dir.parent / "prcs"), str(tmp_path / "ds"), human_labels=str(labels))


def test_entry_without_label_source_is_rejected(dataset_dir, tmp_path):
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({_test_ids(dataset_dir)[0]: {"practice": ["Collecting"], "purpose": []}}))
    with pytest.raises(ValueError, match="retag-llm"):
        build_dataset(str(dataset_dir.parent / "prcs"), str(tmp_path / "ds"), human_labels=str(labels))


def test_test_split_pins_to_given_ids(dataset_dir, tmp_path):
    splits = json.loads((dataset_dir / "splits.json").read_text())
    pinned = splits["test"][:3]
    labels = tmp_path / "labels.json"
    labels.write_text(json.dumps({pid: _entry("human") for pid in pinned}))
    s = build_dataset(str(dataset_dir.parent / "prcs"), str(tmp_path / "ds"),
                      human_labels=str(labels), test_ids=pinned)
    out = json.loads((tmp_path / "ds" / "splits.json").read_text())
    assert sorted(out["test"]) == sorted(pinned) and s["test_all_human"] is True
    # the unpinned flows of the held-out app are dropped, not leaked into train/val
    dropped = set(splits["test"]) - set(pinned)
    assert not dropped & (set(out["train"]) | set(out["val"]))


def test_unknown_pinned_id_is_an_error(dataset_dir, tmp_path):
    with pytest.raises(ValueError, match="not in the PRCS set"):
        build_dataset(str(dataset_dir.parent / "prcs"), str(tmp_path / "ds"), test_ids=["prcs_missing"])


def test_training_and_eval_banner_on_llm_test_labels(llm_dataset, tmp_path):
    pytest.importorskip("torch_geometric")
    from step2_convgnn.train import train
    from step4_eval.evaluate import evaluate_classification
    ds, _ = llm_dataset
    res = train("configs/convgnn.yaml", str(ds), str(tmp_path / "cg"), epochs=2)
    assert res["is_weak"] is True
    assert evaluate_classification(str(ds), str(tmp_path / "cg" / "best.pt"))["is_weak"] is True


def test_captions_policy_and_nutrition_banner_llm_labels(llm_dataset, dataset_dir, tmp_path):
    from step3_caption.generate import generate_captions
    from step3_policy.assemble import assemble
    from step4_app.nutrition import build_nutrition
    ds, _ = llm_dataset
    test_ids = set(_test_ids(dataset_dir))
    caps = generate_captions(str(ds), str(tmp_path / "cap"), "configs/llm.yaml")
    assert {c["weak_banner"] for c in caps if c["prcs_id"] in test_ids} == {BANNER_LLM}

    summary = assemble(str(ds), str(tmp_path / "cap"), str(tmp_path / "pol"))
    test_app = next(json.loads(l)["app_package"] for l in (ds / "adppg.jsonl").read_text().splitlines()
                    if json.loads(l)["prcs_id"] in test_ids)
    assert summary["apps"][test_app]["weak"] is True
    notice = (tmp_path / "pol" / test_app.replace("/", "_") / "notice.md").read_text(encoding="utf-8")
    assert BANNER_LLM in notice

    index = build_nutrition(str(ds), str(tmp_path / "cap"), str(tmp_path / "nut"))
    assert index["apps"][test_app]["weak"] is True
    label = load_json(tmp_path / "nut" / test_app.replace("/", "_") / "nutrition.json")
    assert label["banner"]


def test_webapi_banner_flags_llm_labels(monkeypatch):
    from webapi import loader, services
    monkeypatch.setattr(loader, "labels", lambda: {"p1": {"label_source": "llm"}, "p2": {"label_source": "weak"}})
    monkeypatch.setattr(loader, "eval_report", lambda: {})
    monkeypatch.setattr(loader, "caption_eval", lambda: {})
    kinds = [b["kind"] for b in services.build_banners()]
    assert kinds == ["llm"]
