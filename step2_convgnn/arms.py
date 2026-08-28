"""
Purpose: Fusion-ablation arms mapped to concrete featurization flags (Phase 12).
Input:   an ADPPG record.
Output:  a PyG Data for the given arm, or the (privacy_features, token_features) flags
         that arm corresponds to.

The plan's Phase 12 asks for four comparison arms:
    code                       code-only baseline; ignores the graph entirely
    graph                      graph structure only, no privacy overlay, no code tokens
    code_graph                 graph structure + code tokens (hashing trick over statement text)
    code_graph_knowledge       graph structure + code tokens + privacy overlay from the KB

All four map onto the two knobs already exposed by step2_convgnn.data.record_to_data:
privacy_features (the knowledge-base signal) and token_features (the code signal).
The 'code' arm is not RGCN-based; it goes through the TfIdfBaseline in step3_caption.baselines.
"""
from __future__ import annotations

from typing import Dict, Tuple

from step2_convgnn.data import record_to_data

# Canonical arm names. Every consumer must use these strings so aggregated metrics tables line up.
ARM_CODE = "code"
ARM_GRAPH = "graph"
ARM_CODE_GRAPH = "code_graph"
ARM_CODE_GRAPH_KNOWLEDGE = "code_graph_knowledge"
FUSION_ARMS = (ARM_CODE, ARM_GRAPH, ARM_CODE_GRAPH, ARM_CODE_GRAPH_KNOWLEDGE)

# Which record_to_data flags correspond to each RGCN arm. The 'code' arm is handled elsewhere.
_ARM_FLAGS: Dict[str, Tuple[bool, bool]] = {
    ARM_GRAPH:                 (False, False),   # privacy_features, token_features
    ARM_CODE_GRAPH:            (False, True),
    ARM_CODE_GRAPH_KNOWLEDGE:  (True,  True),
}


def arm_to_flags(arm: str) -> Tuple[bool, bool]:
    """Return (privacy_features, token_features) for one of the RGCN arms.

    Raises ValueError for the 'code' arm (which is not an RGCN configuration) or an unknown arm.
    """
    if arm == ARM_CODE:
        raise ValueError(
            "arm 'code' is text-only and does not use record_to_data; "
            "use step3_caption.baselines.TfIdfBaseline instead"
        )
    if arm not in _ARM_FLAGS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {FUSION_ARMS}")
    return _ARM_FLAGS[arm]


def record_to_data_for_arm(rec: dict, arm: str):
    """Convert an ADPPG record to a PyG Data configured for the given RGCN arm."""
    privacy, tokens = arm_to_flags(arm)
    return record_to_data(rec, privacy_features=privacy, token_features=tokens)
