"""
Purpose: The canonical experiment matrix: ten arms, each with a fixed experiment id, so a rerun
         updates the same manifest. Every other arm list (step2_convgnn/arms.py) derives from it.
Input:   an arm name.
Output:  ArmSpec (task, flags or caption condition, replication) and ExperimentRun stubs.

    EXP001 apg                  classification  privacy_features=False token_features=False  5 seeds
    EXP002 apg_code             classification  False True                                   5 seeds
    EXP003 ppg                  classification  True  False                                  5 seeds
    EXP004 ppg_code             classification  True  True (full model)                      5 seeds
    EXP005 rule                 baseline        step3_caption.baselines.RuleBaseline         1 run
    EXP006 tfidf                baseline        step3_caption.baselines.TfIdfBaseline        1 run
    EXP007 cap_code             captions        condition A, code only                       rating sample
    EXP008 cap_code_api         captions        condition B, code + source/sink APIs         rating sample
    EXP009 cap_code_taint       captions        condition C, code + taint path               rating sample
    EXP010 cap_code_taint_pred  captions        condition G, C + labels predicted by ppg_code seed 0

The classification arms are a 2x2 over the two featurizer flags. pplib.run_matrix executes the
matrix; this module only defines it and never fills in metrics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from pplib.experiment import ExperimentRun


FINAL_ARMS: Tuple[str, ...] = (
    "apg",
    "apg_code",
    "ppg",
    "ppg_code",
    "rule",
    "tfidf",
    "cap_code",
    "cap_code_api",
    "cap_code_taint",
    "cap_code_taint_pred",
)

EXP_ID: Dict[str, str] = {arm: f"EXP{i:03d}" for i, arm in enumerate(FINAL_ARMS, start=1)}

_ARM_TASK: Dict[str, str] = {
    "apg":                 "classification",
    "apg_code":            "classification",
    "ppg":                 "classification",
    "ppg_code":            "classification",
    "rule":                "baseline",
    "tfidf":               "baseline",
    "cap_code":            "captions",
    "cap_code_api":        "captions",
    "cap_code_taint":      "captions",
    "cap_code_taint_pred": "captions",
}

# Caption arms onto step3_caption.experiments conditions. G takes predicted, never gold, labels.
_CAPTION_CONDITION: Dict[str, str] = {
    "cap_code":            "A",
    "cap_code_api":        "B",
    "cap_code_taint":      "C",
    "cap_code_taint_pred": "G",
}

# Classification arms onto step2_convgnn.data.record_to_data flags.
_CLASSIFICATION_FLAGS: Dict[str, Dict[str, bool]] = {
    "apg":      {"privacy_features": False, "token_features": False},
    "apg_code": {"privacy_features": False, "token_features": True},
    "ppg":      {"privacy_features": True,  "token_features": False},
    "ppg_code": {"privacy_features": True,  "token_features": True},
}

CLASSIFICATION_ARMS = tuple(a for a in FINAL_ARMS if _ARM_TASK[a] == "classification")
BASELINE_ARMS = tuple(a for a in FINAL_ARMS if _ARM_TASK[a] == "baseline")
CAPTION_ARMS = tuple(a for a in FINAL_ARMS if _ARM_TASK[a] == "captions")

SEEDS: Tuple[int, ...] = (0, 1, 2, 3, 4)
REFERENCE_ARM = "ppg_code"           # paired bootstrap baseline and condition G label source
REFERENCE_SEED = SEEDS[0]
THRESHOLD = 0.5
BOOTSTRAP_DRAWS = 2000
RATING_SAMPLE_SIZE = 60


@dataclass
class ArmSpec:
    """Everything the runner needs to know about one arm."""

    arm: str
    exp_id: str
    task: str                             # 'classification', 'baseline' or 'captions'
    provider: str = "mock"
    condition: Optional[str] = None       # captions only
    flags: Dict[str, bool] = field(default_factory=dict)   # classification only
    seeds: Tuple[int, ...] = ()
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {"arm": self.arm, "exp_id": self.exp_id, "task": self.task,
             "provider": self.provider, "seeds": list(self.seeds), "notes": self.notes}
        if self.condition is not None:
            d["condition"] = self.condition
        if self.flags:
            d["flags"] = dict(self.flags)
        return d


def arm_spec(arm: str, provider: str = "mock") -> ArmSpec:
    """Return the ArmSpec for one arm. Raises ValueError on an unknown arm."""
    if arm not in FINAL_ARMS:
        raise ValueError(f"unknown arm {arm!r}; expected one of {FINAL_ARMS}")
    task = _ARM_TASK[arm]
    if task == "captions":
        return ArmSpec(arm=arm, exp_id=EXP_ID[arm], task=task, provider=provider,
                       condition=_CAPTION_CONDITION[arm],
                       notes="LLM captions on the rating sample; provider stays 'mock' unless a "
                             "budgeted run overrides it.")
    if task == "baseline":
        return ArmSpec(arm=arm, exp_id=EXP_ID[arm], task=task, provider=provider,
                       notes=f"Deterministic {arm} baseline from step3_caption.baselines.")
    return ArmSpec(arm=arm, exp_id=EXP_ID[arm], task=task, provider=provider,
                   flags=dict(_CLASSIFICATION_FLAGS[arm]), seeds=SEEDS,
                   notes="RGCN classification; flags map onto step2_convgnn.data.record_to_data.")


def enumerate_arms(provider: str = "mock") -> List[ArmSpec]:
    """Return one ArmSpec per arm in the canonical order."""
    return [arm_spec(a, provider=provider) for a in FINAL_ARMS]


def plan_runs(
    dataset_digest: str,
    config_digest: str,
    code_version: str,
    seed: int = REFERENCE_SEED,
    provider: str = "mock",
) -> List[ExperimentRun]:
    """One ExperimentRun stub per arm with its fixed id. No metrics, no artifacts, no execution."""
    return [ExperimentRun(
        exp_id=spec.exp_id,
        name=f"final_matrix::{spec.arm}",
        code_version=code_version,
        config_digest=config_digest,
        dataset_digest=dataset_digest,
        seed=seed,
        model_version="",
        metrics={},
        artifacts=[],
        notes=f"arm={spec.arm}, task={spec.task}, provider={spec.provider}. Plan-only stub.",
    ) for spec in enumerate_arms(provider=provider)]
