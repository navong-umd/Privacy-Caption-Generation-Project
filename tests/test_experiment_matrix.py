"""The canonical experiment matrix: ten arms, fixed ids, and no invented numbers."""
from __future__ import annotations

import json

import pytest

from pplib.experiment_matrix import (
    BASELINE_ARMS,
    CAPTION_ARMS,
    CLASSIFICATION_ARMS,
    EXP_ID,
    FINAL_ARMS,
    SEEDS,
    ArmSpec,
    arm_spec,
    enumerate_arms,
    plan_runs,
)


EXPECTED_ARMS = ("apg", "apg_code", "ppg", "ppg_code", "rule", "tfidf",
                 "cap_code", "cap_code_api", "cap_code_taint", "cap_code_taint_pred")


def test_final_arms_match_the_canonical_table_in_order():
    assert FINAL_ARMS == EXPECTED_ARMS


def test_exp_ids_are_fixed():
    assert EXP_ID == {arm: f"EXP{i:03d}" for i, arm in enumerate(EXPECTED_ARMS, start=1)}
    assert EXP_ID["ppg_code"] == "EXP004"
    assert EXP_ID["cap_code_taint_pred"] == "EXP010"


def test_task_groups():
    assert CLASSIFICATION_ARMS == ("apg", "apg_code", "ppg", "ppg_code")
    assert BASELINE_ARMS == ("rule", "tfidf")
    assert CAPTION_ARMS == ("cap_code", "cap_code_api", "cap_code_taint", "cap_code_taint_pred")


def test_enumerate_arms_returns_one_spec_per_arm_in_order():
    specs = enumerate_arms()
    assert [s.arm for s in specs] == list(EXPECTED_ARMS)
    assert all(isinstance(s, ArmSpec) for s in specs)
    assert [s.exp_id for s in specs] == [f"EXP{i:03d}" for i in range(1, 11)]


def test_caption_arms_carry_condition_and_no_flags():
    conditions = {arm: arm_spec(arm).condition for arm in CAPTION_ARMS}
    assert conditions == {"cap_code": "A", "cap_code_api": "B", "cap_code_taint": "C",
                          "cap_code_taint_pred": "G"}
    for arm in CAPTION_ARMS:
        assert arm_spec(arm).task == "captions"
        assert arm_spec(arm).flags == {}


def test_baseline_arms_have_no_flags_condition_or_seeds():
    for arm in BASELINE_ARMS:
        s = arm_spec(arm)
        assert s.task == "baseline"
        assert s.flags == {} and s.condition is None and s.seeds == ()


def test_classification_arms_are_a_2x2_over_the_two_flags():
    flags = {arm: arm_spec(arm).flags for arm in CLASSIFICATION_ARMS}
    for f in flags.values():
        assert set(f) == {"privacy_features", "token_features"}
    tuples = {(f["privacy_features"], f["token_features"]) for f in flags.values()}
    assert tuples == {(False, False), (False, True), (True, False), (True, True)}
    assert flags["apg"] == {"privacy_features": False, "token_features": False}
    assert flags["ppg_code"] == {"privacy_features": True, "token_features": True}


def test_classification_arms_run_five_seeds():
    assert len(SEEDS) == 5
    for arm in CLASSIFICATION_ARMS:
        assert arm_spec(arm).seeds == SEEDS


def test_unknown_arm_raises():
    with pytest.raises(ValueError, match="unknown arm"):
        arm_spec("ppg_knowledge")


def test_arm_spec_to_dict_json_ready():
    for s in enumerate_arms():
        json.dumps(s.to_dict())


def test_plan_runs_yields_one_stub_per_arm_with_fixed_ids_and_empty_metrics():
    stubs = plan_runs(dataset_digest="d" * 40, config_digest="c" * 40, code_version="b@sha")
    assert [s.exp_id for s in stubs] == [EXP_ID[a] for a in EXPECTED_ARMS]
    for s in stubs:
        assert s.metrics == {}
        assert s.artifacts == []
        assert "final_matrix::" in s.name


def test_plan_runs_default_provider_is_mock():
    for s in plan_runs(dataset_digest="x", config_digest="y", code_version="z"):
        assert "provider=mock" in s.notes
