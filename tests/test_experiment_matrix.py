"""Phase 21: final experiments matrix enumerates the plan's 8 arms and refuses to invent numbers."""
from __future__ import annotations

import pytest

from pplib.experiment_matrix import (
    ArmSpec,
    FINAL_ARMS,
    arm_spec,
    enumerate_arms,
    plan_runs,
)


EXPECTED_ARMS = ("code", "code_api", "code_taint", "apg", "ppg",
                 "ppg_code", "ppg_knowledge", "ppg_code_knowledge")


def test_final_arms_match_the_plan_exactly_and_in_order():
    assert FINAL_ARMS == EXPECTED_ARMS


def test_enumerate_arms_returns_one_spec_per_arm_in_order():
    specs = enumerate_arms()
    assert [s.arm for s in specs] == list(EXPECTED_ARMS)
    for s in specs:
        assert isinstance(s, ArmSpec)


def test_caption_arms_carry_condition_and_no_flags():
    for arm in ("code", "code_api", "code_taint"):
        s = arm_spec(arm)
        assert s.task == "captions"
        assert s.condition in ("A", "B", "C")
        assert s.flags == {}


def test_classification_arms_carry_flags_and_no_condition():
    for arm in ("apg", "ppg", "ppg_code", "ppg_knowledge", "ppg_code_knowledge"):
        s = arm_spec(arm)
        assert s.task == "classification"
        assert s.condition is None
        assert set(s.flags) == {"privacy_features", "token_features"}


def test_apg_is_the_baseline_zero_zero_arm():
    s = arm_spec("apg")
    assert s.flags == {"privacy_features": False, "token_features": False}


def test_full_arm_turns_everything_on():
    s = arm_spec("ppg_code_knowledge")
    assert s.flags == {"privacy_features": True, "token_features": True}


def test_unknown_arm_raises():
    with pytest.raises(ValueError, match="unknown arm"):
        arm_spec("bogus")


def test_arm_spec_to_dict_json_ready():
    import json
    for s in enumerate_arms():
        json.dumps(s.to_dict())


def test_plan_runs_yields_one_stub_per_arm_with_empty_metrics():
    stubs = plan_runs(
        dataset_digest="d" * 40,
        config_digest="c" * 40,
        code_version="Ali-F/Branch@testsha",
    )
    assert len(stubs) == len(EXPECTED_ARMS)
    # Each stub carries a stable EXP### id in canonical order.
    for i, s in enumerate(stubs, start=1):
        assert s.exp_id == f"EXP{i:03d}"
        # Numbers must NEVER be pre-populated: this is the plan's honesty rule.
        assert s.metrics == {}
        assert s.artifacts == []
        assert "final_matrix::" in s.name


def test_plan_runs_default_provider_is_mock():
    """Cost safety: nothing in this planner should call a paid provider by default."""
    stubs = plan_runs(dataset_digest="x", config_digest="y", code_version="z")
    for s in stubs:
        # The provider lives on ArmSpec (visible via re-planning), but the ExperimentRun
        # stub carries the notes string which must include 'provider=mock' for caption arms.
        if "captions" in s.notes:
            assert "provider=mock" in s.notes


def test_start_from_shifts_exp_ids():
    stubs = plan_runs(dataset_digest="x", config_digest="y", code_version="z", start_from=42)
    assert stubs[0].exp_id == "EXP042"
    assert stubs[-1].exp_id == f"EXP{42 + len(EXPECTED_ARMS) - 1:03d}"
