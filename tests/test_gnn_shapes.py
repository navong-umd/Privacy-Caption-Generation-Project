"""Phase 11: RGCN input tensor contract pinned against `record_to_data`.

If any dtype, shape, or value-range invariant changes, the classifier breaks
in weird ways deep in RGCNConv. Assert them at the featurization boundary.
"""
from __future__ import annotations

import pytest

pytest.importorskip("torch")
pytest.importorskip("torch_geometric")

import torch

from pplib.schema import PPG_EDGE_TYPES, PRACTICE_LABELS, PURPOSE_LABELS
from step2_convgnn.data import (
    FEAT_DIM,
    NUM_NODE_TYPES,
    NUM_RELATIONS,
    TOKEN_HOOK_DIM,
    record_to_data,
)


def _stub_record() -> dict:
    return {
        "prcs_id": "prcs_test",
        "subgraph": {
            "nodes": [
                {"id": "s0", "label": "Source",    "is_source": "1",
                 "permission": "ACCESS_FINE_LOCATION", "category": "LOCATION_INFORMATION",
                 "sink_type": "", "callee": "android.location.LocationManager->getLastKnownLocation",
                 "code": ""},
                {"id": "s1", "label": "Statement", "callee": "", "code": "move-result-object v0"},
                {"id": "s2", "label": "Sink",      "is_sink": "1",
                 "sink_type": "logging", "sink_label": "Log", "callee": "android.util.Log->i",
                 "code": ""},
            ],
            "edges": [
                {"start": "s0", "end": "s1", "type": "DATA_DEPENDS"},
                {"start": "s1", "end": "s2", "type": "TAINT_FLOW"},
            ],
        },
        "labels": {"practice": ["Collecting"], "purpose": ["Functionality"],
                   "label_source": "weak"},
    }


@pytest.fixture(scope="module")
def data():
    return record_to_data(_stub_record())


def test_feat_dim_matches_the_schema():
    # 2 boolean source/sink slots + 1 permission slot + 6 sink types + 13 PI categories + TOKEN_HOOK_DIM
    assert FEAT_DIM == 2 + 1 + 6 + 13 + TOKEN_HOOK_DIM
    assert TOKEN_HOOK_DIM == 8


def test_num_relations_matches_ppg_edge_types():
    assert NUM_RELATIONS == len(PPG_EDGE_TYPES)


def test_x_is_float_and_correct_shape(data):
    assert isinstance(data.x, torch.Tensor)
    assert data.x.dtype == torch.float32
    assert data.x.dim() == 2
    assert data.x.size(1) == FEAT_DIM


def test_node_type_is_long_and_in_range(data):
    assert data.node_type.dtype == torch.int64
    assert int(data.node_type.min()) >= 0
    assert int(data.node_type.max()) < NUM_NODE_TYPES


def test_edge_index_and_edge_type_shapes_line_up(data):
    assert data.edge_index.dtype == torch.int64
    assert data.edge_index.size(0) == 2
    assert data.edge_type.dtype == torch.int64
    assert data.edge_index.size(1) == data.edge_type.size(0)


def test_edge_type_values_in_range(data):
    assert int(data.edge_type.min()) >= 0
    assert int(data.edge_type.max()) < NUM_RELATIONS


def test_edge_index_references_valid_nodes(data):
    n = data.x.size(0)
    assert int(data.edge_index.min()) >= 0
    assert int(data.edge_index.max()) < n


def test_labels_are_multi_hot_and_shaped_for_the_two_heads(data):
    assert data.y_practice.dtype == torch.float32
    assert tuple(data.y_practice.shape) == (1, len(PRACTICE_LABELS))
    assert data.y_purpose.dtype == torch.float32
    assert tuple(data.y_purpose.shape) == (1, len(PURPOSE_LABELS))
    for row in (data.y_practice, data.y_purpose):
        for v in row.flatten().tolist():
            assert v in (0.0, 1.0)


def test_apg_only_ablation_zeroes_privacy_features_but_keeps_type():
    from step2_convgnn.data import _node_features
    n = {"label": "Source", "is_source": "1", "permission": "P", "category": "LOCATION_INFORMATION",
         "sink_type": "network", "callee": "", "code": ""}
    t_full, f_full = _node_features(n, privacy_features=True)
    t_apg, f_apg = _node_features(n, privacy_features=False)
    assert t_full == t_apg               # node-type id (APG structure) preserved
    assert any(v != 0 for v in f_full)   # PPG carries privacy signal
    assert f_apg == [0.0] * FEAT_DIM     # APG-only zeroes the overlay vector


def test_token_hook_slots_are_zero_by_default(data):
    for row in data.x:
        block = row[FEAT_DIM - TOKEN_HOOK_DIM:]
        assert torch.all(block == 0), "token hook slots should be empty by default"


def test_forward_pass_shape():
    """End-to-end: ConvGNNClassifier accepts a batch of one graph and returns two heads."""
    from torch_geometric.loader import DataLoader
    from step2_convgnn.model import ConvGNNClassifier

    d = record_to_data(_stub_record())
    batch = next(iter(DataLoader([d], batch_size=1)))
    cfg = {"model": {"type_embed_dim": 8, "hidden_dim": 16, "num_layers": 2,
                     "dropout": 0.0, "readout": "attention"}}
    model = ConvGNNClassifier(cfg).eval()
    with torch.no_grad():
        p_logits, u_logits = model(batch)
    assert tuple(p_logits.shape) == (1, len(PRACTICE_LABELS))
    assert tuple(u_logits.shape) == (1, len(PURPOSE_LABELS))
