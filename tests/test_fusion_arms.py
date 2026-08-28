"""Phase 12: every fusion-ablation arm produces the expected featurization."""
from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytest.importorskip("torch_geometric")

import torch

from step2_convgnn.arms import (
    ARM_CODE,
    ARM_CODE_GRAPH,
    ARM_CODE_GRAPH_KNOWLEDGE,
    ARM_GRAPH,
    FUSION_ARMS,
    arm_to_flags,
    record_to_data_for_arm,
)
from step2_convgnn.data import FEAT_DIM, TOKEN_HOOK_DIM


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


def test_canonical_arm_names_match_the_plan():
    assert FUSION_ARMS == ("code", "graph", "code_graph", "code_graph_knowledge")


def test_code_arm_is_not_an_rgcn_configuration():
    with pytest.raises(ValueError, match="TfIdfBaseline"):
        arm_to_flags(ARM_CODE)


def test_unknown_arm_rejected():
    with pytest.raises(ValueError, match="unknown arm"):
        arm_to_flags("bogus_arm")


def test_arm_flags_table():
    assert arm_to_flags(ARM_GRAPH) == (False, False)
    assert arm_to_flags(ARM_CODE_GRAPH) == (False, True)
    assert arm_to_flags(ARM_CODE_GRAPH_KNOWLEDGE) == (True, True)


def test_graph_arm_zeroes_the_privacy_and_token_blocks():
    data = record_to_data_for_arm(_stub_record(), ARM_GRAPH)
    token_base = FEAT_DIM - TOKEN_HOOK_DIM
    for row in data.x:
        # privacy block (indices 0..token_base-1) all zero
        assert torch.all(row[:token_base] == 0)
        # token block all zero
        assert torch.all(row[token_base:] == 0)


def test_code_graph_arm_populates_only_the_token_block():
    data = record_to_data_for_arm(_stub_record(), ARM_CODE_GRAPH)
    token_base = FEAT_DIM - TOKEN_HOOK_DIM
    # privacy block still zero
    for row in data.x:
        assert torch.all(row[:token_base] == 0)
    # some node has a nonzero token block (both stub nodes carry code+callee text)
    assert any(bool(torch.any(row[token_base:] > 0)) for row in data.x)


def test_code_graph_knowledge_arm_populates_both_blocks():
    data = record_to_data_for_arm(_stub_record(), ARM_CODE_GRAPH_KNOWLEDGE)
    token_base = FEAT_DIM - TOKEN_HOOK_DIM
    # privacy block has at least one nonzero row (Source and Sink stubs both light up)
    assert any(bool(torch.any(row[:token_base] > 0)) for row in data.x)
    # token block populated
    assert any(bool(torch.any(row[token_base:] > 0)) for row in data.x)


def test_arms_produce_distinct_feature_matrices():
    """The three RGCN arms must not produce identical x tensors on the same record."""
    a = record_to_data_for_arm(_stub_record(), ARM_GRAPH).x
    b = record_to_data_for_arm(_stub_record(), ARM_CODE_GRAPH).x
    c = record_to_data_for_arm(_stub_record(), ARM_CODE_GRAPH_KNOWLEDGE).x
    assert not torch.equal(a, b)
    assert not torch.equal(a, c)
    assert not torch.equal(b, c)


def test_edge_and_type_encoding_invariant_across_arms():
    """Only x changes across arms; edges and node types stay the same."""
    a = record_to_data_for_arm(_stub_record(), ARM_GRAPH)
    b = record_to_data_for_arm(_stub_record(), ARM_CODE_GRAPH_KNOWLEDGE)
    assert torch.equal(a.edge_index, b.edge_index)
    assert torch.equal(a.edge_type, b.edge_type)
    assert torch.equal(a.node_type, b.node_type)
