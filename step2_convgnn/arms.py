"""
Purpose: RGCN featurization arms, derived from the canonical matrix in pplib/experiment_matrix.py.
Input:   an ADPPG record.
Output:  a PyG Data for the given arm, or the (privacy_features, token_features) flags of that arm.

The four RGCN arms are a 2x2 over the two knobs record_to_data exposes:
    apg        neither the PPG privacy overlay nor statement tokens
    apg_code   statement tokens (hashing trick over statement text) only
    ppg        PPG privacy overlay only
    ppg_code   both (the full model)
The text-only and rule baselines (tfidf, rule) are not RGCN arms; they live in step3_caption.baselines.
"""
from __future__ import annotations

from typing import Dict, Tuple

from pplib.experiment_matrix import BASELINE_ARMS, CLASSIFICATION_ARMS, arm_spec
from step2_convgnn.data import record_to_data

FUSION_ARMS = CLASSIFICATION_ARMS

_ARM_FLAGS: Dict[str, Tuple[bool, bool]] = {
    arm: (arm_spec(arm).flags["privacy_features"], arm_spec(arm).flags["token_features"])
    for arm in FUSION_ARMS
}


def arm_to_flags(arm: str) -> Tuple[bool, bool]:
    """Return (privacy_features, token_features) for one of the RGCN arms.

    Raises ValueError for a baseline arm (not an RGCN configuration) or any other arm.
    """
    if arm in BASELINE_ARMS:
        raise ValueError(f"arm {arm!r} is not an RGCN configuration; "
                         "use step3_caption.baselines (RuleBaseline / TfIdfBaseline) instead")
    if arm not in _ARM_FLAGS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {FUSION_ARMS}")
    return _ARM_FLAGS[arm]


def record_to_data_for_arm(rec: dict, arm: str):
    """Convert an ADPPG record to a PyG Data configured for the given RGCN arm."""
    privacy, tokens = arm_to_flags(arm)
    return record_to_data(rec, privacy_features=privacy, token_features=tokens)
