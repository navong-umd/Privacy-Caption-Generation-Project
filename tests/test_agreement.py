"""Inter-annotator agreement (Cohen's kappa) and the LLM labeler used for human-vs-LLM agreement."""
from __future__ import annotations

import csv
import json

import pytest

from pplib.io_utils import load_json
from step2_dataset.agreement import agreement, pairwise


def _lab(practice, purpose):
    return {"practice": practice, "purpose": purpose}


A = {"p1": _lab(["Collecting"], ["Functionality"]),
     "p2": _lab(["Collecting", "Sharing"], ["Analytics"]),
     "p3": _lab(["Processing"], ["Functionality"]),
     "p4": _lab(["Collecting", "Sharing"], ["Functionality"])}


def test_identical_labels_give_kappa_one_on_defined_labels():
    res = pairwise(A, A)
    assert res["n_items"] == 4 and res["exact_match"] == 1.0
    defined = {k: v for k, v in res["labels"].items() if not v["undefined"]}
    assert defined and all(v["kappa"] == 1.0 for v in defined.values())
    assert res["macro_kappa"]["practice"] == 1.0


def test_constant_label_is_undefined_and_left_out_of_the_macro():
    res = pairwise(A, A)
    adv = res["labels"]["purpose_Advertisement"]               # never marked by either rater
    assert adv["undefined"] is True and adv["kappa"] is None and adv["prevalence"] == 0.0
    assert res["defined_labels"]["purpose"] == 2               # Functionality + Analytics


def test_hand_computed_kappa():
    # practice_Sharing: A = [0,1,0,1], B = [0,1,1,1] -> po=0.75, pe=0.5*0.25+0.5*0.75=0.5, kappa=0.5
    b = {**A, "p3": _lab(["Processing", "Sharing"], ["Functionality"])}
    assert pairwise(A, b)["labels"]["practice_Sharing"]["kappa"] == pytest.approx(0.5)


def test_report_and_disagreement_sheet(tmp_path):
    a_path, b_path = tmp_path / "a.json", tmp_path / "b.json"
    a_path.write_text(json.dumps(A))
    b_path.write_text(json.dumps({**A, "p2": _lab(["Collecting"], ["Analytics"])}))
    sheet = tmp_path / "overlap.csv"
    with sheet.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["prcs_id", "app_package", "annotator"])
        w.writeheader()
        w.writerows({"prcs_id": p, "app_package": "com.x", "annotator": "ali"} for p in A)
    out = tmp_path / "AGREEMENT.json"
    report = agreement(str(a_path), str(b_path), str(out), sheet_csv=str(sheet),
                       disagreements_csv=str(tmp_path / "adj.csv"))
    assert load_json(out)["pairs"]["a_vs_b"]["n_items"] == 4 and out.with_suffix(".md").exists()
    rows = list(csv.DictReader((tmp_path / "adj.csv").open(encoding="utf-8")))
    assert [r["prcs_id"] for r in rows] == ["p2"] and report["disagreements"]["n_items"] == 1
    assert rows[0]["annotator"] == "" and rows[0]["a_practice"] == "Collecting|Sharing"


def test_report_includes_human_vs_llm_pairs(tmp_path):
    llm = {**A, "p1": _lab(["Sharing"], ["Advertisement"])}
    b = {**A, "p4": _lab(["Collecting"], ["Functionality"])}
    for name, data in (("a", A), ("b", b), ("llm", llm)):
        (tmp_path / f"{name}.json").write_text(json.dumps(data))
    report = agreement(str(tmp_path / "a.json"), str(tmp_path / "b.json"), str(tmp_path / "out.json"),
                       llm_json=str(tmp_path / "llm.json"))
    assert report["pairs"]["a_vs_llm"] == pairwise(A, llm)
    assert report["pairs"]["b_vs_llm"] == pairwise(b, llm) != pairwise(A, llm)


class _JsonModel:
    """Fake paid model that answers with a PAcT label and reports token usage."""
    model = "fake-model"

    def __init__(self, fail_on=()):
        self.calls, self.fail_on = 0, set(fail_on)

    def generate(self, prompt, evidence):
        from step3_caption.budget import FRAMING_TOKENS
        from step3_caption.llm_interface import GenerationResult
        self.calls += 1
        assert "weak" not in prompt.lower()                    # weak labels never reach the model
        if self.calls in self.fail_on:
            raise RuntimeError("rate limited")
        return GenerationResult('{"practice": ["Collecting"], "purpose": ["Analytics"], "confidence": 2}',
                                len(prompt.encode("utf-8")) + FRAMING_TOKENS, 40)


def _sheet(dataset_dir, tmp_path, n):
    ids = [json.loads(l)["prcs_id"] for l in (dataset_dir / "adppg.jsonl").read_text().splitlines()][:n]
    sheet = tmp_path / "sheet.csv"
    sheet.write_text("prcs_id\n" + "\n".join(ids) + "\n", encoding="utf-8")
    return ids, sheet


def test_llm_labeler_writes_llm_entries(dataset_dir, tmp_path):
    from step2_dataset.llm_label import label_sheet
    from step3_caption.budget import Budget
    ids, sheet = _sheet(dataset_dir, tmp_path, 3)
    s = label_sheet(str(dataset_dir), str(sheet), str(tmp_path / "llm.json"), _JsonModel(),
                    Budget(limit_usd=100, price_in_per_mtok=1, price_out_per_mtok=1, max_tokens=50))
    labels = load_json(tmp_path / "llm.json")
    assert s["labeled"] == 3 and set(labels) == set(ids)
    assert {e["label_source"] for e in labels.values()} == {"llm"}
    assert labels[ids[0]]["annotator"] == "fake-model" and labels[ids[0]]["confidence"] == 0.67


def test_llm_labeler_stops_at_budget_and_keeps_partial_labels(dataset_dir, tmp_path):
    from step2_dataset.llm_label import build_prompt, label_sheet
    from step3_caption.budget import Budget
    ids, _ = _sheet(dataset_dir, tmp_path, 1)
    sheet = tmp_path / "same_flow.csv"                         # one flow 4x: every call costs the same
    sheet.write_text("prcs_id\n" + f"{ids[0]}\n" * 4, encoding="utf-8")
    budget = Budget(limit_usd=1.0, price_in_per_mtok=1000, price_out_per_mtok=1000, max_tokens=50)
    record = next(json.loads(l) for l in (dataset_dir / "adppg.jsonl").read_text().splitlines()
                  if json.loads(l)["prcs_id"] == ids[0])
    budget.limit_usd = budget.upper_bound_usd(build_prompt(record)) * 1.5   # room for exactly one call
    model = _JsonModel()
    s = label_sheet(str(dataset_dir), str(sheet), str(tmp_path / "llm.json"), model, budget)
    assert model.calls == 1 and s["labeled"] == 1 and s["budget"]["stopped_by_budget"] is True
    assert load_json(tmp_path / "llm.summary.json")["budget"]["spent_usd"] <= budget.limit_usd


def test_llm_labeler_records_failed_calls_and_keeps_going(dataset_dir, tmp_path):
    from step2_dataset.llm_label import label_sheet
    from step3_caption.budget import Budget
    ids, sheet = _sheet(dataset_dir, tmp_path, 3)
    s = label_sheet(str(dataset_dir), str(sheet), str(tmp_path / "llm.json"), _JsonModel(fail_on={2}),
                    Budget(limit_usd=100, price_in_per_mtok=1, price_out_per_mtok=1, max_tokens=50))
    assert s["labeled"] == 2 and list(s["errors"]) == [ids[1]]
    assert set(load_json(tmp_path / "llm.json")) == {ids[0], ids[2]}


def test_llm_labeler_refuses_the_offline_mock(dataset_dir, tmp_path, monkeypatch):
    import sys
    from step2_dataset import llm_label
    _, sheet = _sheet(dataset_dir, tmp_path, 1)
    monkeypatch.setattr(sys, "argv", ["llm_label", "--dataset", str(dataset_dir), "--sheet", str(sheet),
                                      "--out", str(tmp_path / "o.json"), "--provider", "mock", "--budget-usd", "1"])
    with pytest.raises(SystemExit, match="real model"):
        llm_label.main()
