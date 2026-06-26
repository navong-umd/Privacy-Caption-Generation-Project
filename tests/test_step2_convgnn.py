"""Unit + integration tests for Step 2 ConvGNN (skips cleanly if torch/PyG absent)."""
from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("torch_geometric")

from step2_convgnn.data import FEAT_DIM, NUM_RELATIONS, load_splits, record_to_data
from step2_convgnn.model import ConvGNNClassifier
from step2_convgnn.train import train

_CFG = {"model": {"type_embed_dim": 8, "hidden_dim": 16, "num_layers": 2,
                  "dropout": 0.2, "readout": "attention", "conv": "rgcn"}}


def _record():
    return {
        "prcs_id": "prcs_x",
        "labels": {"practice": ["Collecting", "Sharing"], "purpose": ["Advertisement"],
                   "label_source": "weak"},
        "subgraph": {
            "nodes": [
                {"id": "s0", "label": "Statement", "is_source": True, "category": "LOCATION_INFORMATION"},
                {"id": "s1", "label": "Statement", "is_sink": True, "sink_type": "network"},
                {"id": "src::s0", "label": "Source"},
            ],
            "edges": [{"start": "s0", "end": "s1", "type": "TAINT_FLOW"},
                      {"start": "s0", "end": "src::s0", "type": "PRIVACY_RELATION"}],
        },
    }


def test_record_to_data_shapes():
    d = record_to_data(_record())
    assert d.x.shape == (3, FEAT_DIM)
    assert d.edge_index.shape[0] == 2 and d.edge_type.max() < NUM_RELATIONS
    assert d.y_practice.shape == (1, 4) and d.y_purpose.shape == (1, 4)
    # multi-hot is correct
    assert d.y_practice.sum().item() == 2 and d.y_purpose.sum().item() == 1


def test_model_forward_batch():
    from torch_geometric.loader import DataLoader
    loader = DataLoader([record_to_data(_record()), record_to_data(_record())], batch_size=2)
    model = ConvGNNClassifier(_CFG)
    batch = next(iter(loader))
    lp, lu = model(batch)
    assert lp.shape == (2, 4) and lu.shape == (2, 4)


def test_training_runs_end_to_end(dataset_dir, tmp_path):
    res = train("configs/convgnn.yaml", str(dataset_dir), str(tmp_path / "cg"), epochs=5)
    assert res["is_weak"] is True                      # synthetic/weak -> BOOTSTRAP
    assert (tmp_path / "cg" / "best.pt").exists()
    assert (tmp_path / "cg" / "metrics.csv").exists()
    assert (tmp_path / "cg" / "train_log.csv").exists()
    m = res["test"]
    for k in ("practice_macro_f1", "purpose_macro_f1"):
        assert 0.0 <= m[k] <= 1.0
