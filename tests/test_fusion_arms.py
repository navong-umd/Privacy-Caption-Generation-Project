"""RGCN arms derive from the canonical matrix and produce the expected featurization."""
from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytest.importorskip("torch_geometric")

import torch

from pplib.experiment_matrix import CLASSIFICATION_ARMS, EXP_ID, FINAL_ARMS, arm_spec
from step2_convgnn.arms import FUSION_ARMS, arm_to_flags, record_to_data_for_arm
from step2_convgnn.data import FEAT_DIM, TOKEN_HOOK_DIM

TOKEN_BASE = FEAT_DIM - TOKEN_HOOK_DIM


def _stub_record() -> dict:
    return {
        "prcs_id": "prcs_arm_test",
        "subgraph": {
            "nodes": [
                {"id": "s0", "label": "Source",    "is_source": "1",
                 "permission": "ACCESS_FINE_LOCATION", "category": "LOCATION_INFORMATION",
                 "sink_type": "", "code": "invoke getLastKnownLocation",
                 "callee": "android.location.LocationManager->getLastKnownLocation"},
                {"id": "s1", "label": "Sink", "is_sink": "1",
                 "sink_type": "logging", "sink_label": "Log",
                 "code": "invoke Log.i",
                 "callee": "android.util.Log->i", "category": ""},
            ],
            "edges": [{"start": "s0", "end": "s1", "type": "TAINT_FLOW"}],
        },
        "labels": {"practice": ["Collecting"], "purpose": ["Functionality"],
                   "label_source": "weak"},
    }


def test_fusion_arms_are_the_matrix_classification_arms():
    assert FUSION_ARMS == CLASSIFICATION_ARMS == ("apg", "apg_code", "ppg", "ppg_code")
    assert len(FINAL_ARMS) == 10
    assert [EXP_ID[a] for a in FUSION_ARMS] == ["EXP001", "EXP002", "EXP003", "EXP004"]


def test_arm_flags_match_the_matrix_and_are_distinct():
    for arm in FUSION_ARMS:
        f = arm_spec(arm).flags
        assert arm_to_flags(arm) == (f["privacy_features"], f["token_features"])
    assert arm_to_flags("apg") == (False, False)
    assert arm_to_flags("apg_code") == (False, True)
    assert arm_to_flags("ppg") == (True, False)
    assert arm_to_flags("ppg_code") == (True, True)
    assert len({arm_to_flags(a) for a in FUSION_ARMS}) == 4


@pytest.mark.parametrize("arm", ["rule", "tfidf"])
def test_baseline_arms_are_not_rgcn_configurations(arm):
    with pytest.raises(ValueError, match="baselines"):
        arm_to_flags(arm)


@pytest.mark.parametrize("arm", ["bogus_arm", "cap_code", "ppg_knowledge"])
def test_unknown_arm_rejected(arm):
    with pytest.raises(ValueError, match="unknown arm"):
        arm_to_flags(arm)


def _blocks(arm):
    x = record_to_data_for_arm(_stub_record(), arm).x
    privacy = any(bool(torch.any(row[:TOKEN_BASE] != 0)) for row in x)
    tokens = any(bool(torch.any(row[TOKEN_BASE:] != 0)) for row in x)
    return privacy, tokens


@pytest.mark.parametrize("arm", ["apg", "apg_code", "ppg", "ppg_code"])
def test_each_arm_populates_exactly_its_feature_blocks(arm):
    assert _blocks(arm) == arm_to_flags(arm)


def test_arms_produce_distinct_feature_matrices():
    xs = [record_to_data_for_arm(_stub_record(), a).x for a in FUSION_ARMS]
    for i in range(len(xs)):
        for j in range(i + 1, len(xs)):
            assert not torch.equal(xs[i], xs[j])


def test_edge_and_type_encoding_invariant_across_arms():
    """Only x changes across arms; edges and node types stay the same."""
    a = record_to_data_for_arm(_stub_record(), "apg")
    b = record_to_data_for_arm(_stub_record(), "ppg_code")
    assert torch.equal(a.edge_index, b.edge_index)
    assert torch.equal(a.edge_type, b.edge_type)
    assert torch.equal(a.node_type, b.node_type)
