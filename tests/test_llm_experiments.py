"""Phase 14: A-G condition builders project the right evidence subset."""
from __future__ import annotations

import pytest

from step3_caption.budget import Budget
from step3_caption.experiments import (
    BUDGET_REFUSED,
    CONDITIONS,
    CONDITION_LABELS,
    ConditionResult,
    build_evidence,
    build_prompt,
    run_all_conditions,
    run_condition,
)


FULL_PRCS = {
    "prcs_id": "prcs_ff01",
    "app_package": "com.example.app",
    "apk_filename": "app.apk",
    "class_name": "com.example.Loc",
    "method_name": "read",
    "method_signature": "com.example.Loc->read",
    "source_api": "android.location.LocationManager->getLastKnownLocation",
    "sink_api": "java.net.URL->openConnection",
    "sink_type": "network",
    "pi_type": "user's coarse location",
    "pi_category": "LOCATION_INFORMATION",
    "permission": "ACCESS_FINE_LOCATION",
    "privacy_threat": "Data Disclosure",
    "hop_count": 2,
    "taint_path": ["a_stmt_0", "a_stmt_1", "a_stmt_2"],
    "taint_rules": ["source", "ddg", "ddg"],
    "code_snippet": "// method\n  move v0\n  invoke URL.openConnection",
    "involved_methods": ["com.example.Loc->read"],
    "subgraph": {
        "nodes": [{"label": "Source"}, {"label": "Statement"}, {"label": "Sink"}],
        "edges": [{"type": "DATA_DEPENDS"}, {"type": "TAINT_FLOW"}],
    },
    "labels": {"practice": ["Collecting", "Sharing"], "purpose": ["Functionality"],
               "label_source": "weak"},
}


class _StubProvider:
    name = "stub"
    model = "stub-1"

    def generate(self, prompt, evidence):
        return f"caption for {evidence.get('prcs_id')} under {evidence.get('sink_api', '?')}"


class _FailingProvider:
    name = "boom"
    model = "boom-1"

    def generate(self, prompt, evidence):
        raise RuntimeError("provider unreachable")


def test_conditions_and_labels_match_the_plan():
    assert CONDITIONS == ("A", "B", "C", "D", "E", "F", "G")
    for c in CONDITIONS:
        assert c in CONDITION_LABELS


def test_condition_A_is_code_only():
    ev = build_evidence(FULL_PRCS, "A")
    assert set(ev) == {"prcs_id", "code_snippet"}


def test_condition_B_adds_apis():
    ev = build_evidence(FULL_PRCS, "B")
    assert "source_api" in ev and "sink_api" in ev
    # But taint path / PPG / PAcT are all absent
    for absent in ("taint_path", "node_labels", "practice", "purpose", "pi_category"):
        assert absent not in ev, f"unexpected field in condition B: {absent}"


def test_condition_C_adds_taint_path_only():
    ev = build_evidence(FULL_PRCS, "C")
    assert ev["taint_path"] == FULL_PRCS["taint_path"]
    assert ev["taint_rules"] == FULL_PRCS["taint_rules"]
    assert ev["hop_count"] == FULL_PRCS["hop_count"]
    for absent in ("node_labels", "practice", "pi_category"):
        assert absent not in ev, f"unexpected in condition C: {absent}"


def test_condition_D_adds_ppg_structure_but_no_pact():
    ev = build_evidence(FULL_PRCS, "D")
    assert "node_labels" in ev and "edge_types" in ev
    assert ev["subgraph_nodes"] == 3
    for absent in ("practice", "pi_category", "taint_path"):
        assert absent not in ev, f"unexpected in condition D: {absent}"


def test_condition_E_adds_pact_and_kb_but_no_taint_path():
    ev = build_evidence(FULL_PRCS, "E")
    assert ev["practice"] == FULL_PRCS["labels"]["practice"]
    assert ev["purpose"] == FULL_PRCS["labels"]["purpose"]
    assert ev["pi_category"] == FULL_PRCS["pi_category"]
    assert "taint_path" not in ev


def test_condition_F_is_the_full_evidence_package():
    ev = build_evidence(FULL_PRCS, "F")
    for key in ("code_snippet", "source_api", "sink_api", "taint_path", "taint_rules",
                "node_labels", "practice", "purpose", "pi_category",
                "app_package", "apk_filename", "class_name", "method_name"):
        assert key in ev, f"condition F missing {key}"


def test_unknown_condition_raises():
    with pytest.raises(ValueError, match="unknown condition"):
        build_evidence(FULL_PRCS, "Z")


def test_prompt_is_stable_across_repeat_calls():
    p1 = build_prompt("F", build_evidence(FULL_PRCS, "F"))
    p2 = build_prompt("F", build_evidence(FULL_PRCS, "F"))
    assert p1 == p2


def test_run_condition_captures_provenance():
    r = run_condition(FULL_PRCS, "F", _StubProvider(), temperature=0.2)
    assert isinstance(r, ConditionResult)
    assert r.condition == "F"
    assert r.condition_label == CONDITION_LABELS["F"]
    assert r.provider == "stub"
    assert r.model == "stub-1"
    assert r.caption.startswith("caption for prcs_ff01")
    assert r.prompt_chars == len(r.prompt)
    assert r.caption_chars == len(r.caption)
    assert r.temperature == 0.2
    assert r.error == ""


def test_run_condition_never_raises_on_provider_error():
    r = run_condition(FULL_PRCS, "A", _FailingProvider())
    assert r.caption == ""
    assert "RuntimeError" in r.error
    # ConditionResult is still produced with all fields populated.
    assert r.condition == "A"


def test_run_all_conditions_skips_G_without_predictions():
    results = run_all_conditions(FULL_PRCS, _StubProvider())
    assert [r.condition for r in results] == ["A", "B", "C", "D", "E", "F"]


def test_run_all_conditions_returns_one_result_per_condition_with_predictions():
    results = run_all_conditions(FULL_PRCS, _StubProvider(), predicted=PREDICTED)
    assert [r.condition for r in results] == list(CONDITIONS)


PREDICTED = {"practice": ["Processing"], "purpose": ["Advertisement", "Analytics"]}


def test_condition_G_uses_predicted_labels_not_gold():
    assert PREDICTED["practice"] != FULL_PRCS["labels"]["practice"]
    ev = build_evidence(FULL_PRCS, "G", predicted=PREDICTED)
    assert ev["practice"] == PREDICTED["practice"]
    assert ev["purpose"] == PREDICTED["purpose"]
    c = build_evidence(FULL_PRCS, "C")
    assert {k: v for k, v in ev.items() if k not in ("practice", "purpose")} == c


def test_condition_G_never_reads_rec_labels():
    class _Exploding(dict):
        def __getitem__(self, k):
            if k == "labels":
                raise AssertionError("condition G read rec['labels']")
            return super().__getitem__(k)

        def get(self, k, default=None):
            if k == "labels":
                raise AssertionError("condition G read rec['labels']")
            return super().get(k, default)

    ev = build_evidence(_Exploding(FULL_PRCS), "G", predicted=PREDICTED)
    assert ev["purpose"] == PREDICTED["purpose"]


def test_condition_G_without_predictions_raises():
    with pytest.raises(ValueError, match="predicted labels"):
        build_evidence(FULL_PRCS, "G")


def test_run_condition_respects_the_budget():
    class _Priced(_StubProvider):
        calls = 0

        def generate(self, prompt, evidence):
            _Priced.calls += 1
            return super().generate(prompt, evidence)

    prompt_len = len(build_prompt("A", build_evidence(FULL_PRCS, "A")).encode("utf-8"))
    one_call = (prompt_len + 64) * 1.0 / 1e6 + 10 * 1.0 / 1e6
    budget = Budget(limit_usd=one_call * 1.5, price_in_per_mtok=1.0, price_out_per_mtok=1.0,
                    max_tokens=10)
    first = run_condition(FULL_PRCS, "A", _Priced(), budget=budget)
    second = run_condition(FULL_PRCS, "A", _Priced(), budget=budget)
    assert first.error == "" and first.caption
    assert second.error == BUDGET_REFUSED and second.caption == ""
    assert _Priced.calls == 1
    assert budget.summary()["stopped_by_budget"] is True


def test_to_dict_is_json_ready():
    import json
    r = run_condition(FULL_PRCS, "F", _StubProvider())
    json.dumps(r.to_dict())
