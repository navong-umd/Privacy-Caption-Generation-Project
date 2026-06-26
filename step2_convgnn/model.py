"""
Purpose: Relation-aware ConvGNN (RGCN) with graph-level readout and two multi-label heads.
Input:   PyG batched graphs (x, node_type, edge_index, edge_type, batch).
Output:  (practice_logits[B,4], purpose_logits[B,4]).

Architecture: node-type embedding ⊕ structural features → RGCN stack (relation-aware) →
attention/mean readout → shared graph vector → two independent sigmoid heads
(Practice, Purpose). Sigmoid heads make both predictions multi-label.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import RGCNConv, global_mean_pool
from torch_geometric.nn.aggr import AttentionalAggregation

from pplib.schema import PRACTICE_LABELS, PURPOSE_LABELS
from step2_convgnn.data import FEAT_DIM, NUM_NODE_TYPES, NUM_RELATIONS


class ConvGNNClassifier(nn.Module):
    """RGCN encoder + attention readout + Practice/Purpose heads."""

    def __init__(self, cfg: dict):
        super().__init__()
        m = cfg["model"]
        emb = m["type_embed_dim"]
        hid = m["hidden_dim"]
        self.dropout = m["dropout"]
        self.readout = m.get("readout", "attention")

        self.type_emb = nn.Embedding(NUM_NODE_TYPES, emb)
        self.in_proj = nn.Linear(FEAT_DIM + emb, hid)
        self.convs = nn.ModuleList(
            [RGCNConv(hid, hid, num_relations=NUM_RELATIONS) for _ in range(m["num_layers"])])
        if self.readout == "attention":
            self.pool = AttentionalAggregation(gate_nn=nn.Linear(hid, 1))
        self.head_practice = nn.Sequential(
            nn.Linear(hid, hid), nn.ReLU(), nn.Dropout(self.dropout),
            nn.Linear(hid, len(PRACTICE_LABELS)))
        self.head_purpose = nn.Sequential(
            nn.Linear(hid, hid), nn.ReLU(), nn.Dropout(self.dropout),
            nn.Linear(hid, len(PURPOSE_LABELS)))

    def forward(self, data):
        x = torch.cat([data.x, self.type_emb(data.node_type)], dim=-1)
        h = F.relu(self.in_proj(x))
        for conv in self.convs:
            h = F.relu(conv(h, data.edge_index, data.edge_type))
            h = F.dropout(h, p=self.dropout, training=self.training)
        g = self.pool(h, data.batch) if self.readout == "attention" else global_mean_pool(h, data.batch)
        return self.head_practice(g), self.head_purpose(g)
