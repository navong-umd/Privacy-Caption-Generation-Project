"""
Purpose: Final experiments matrix (Phase 21). Pins the exact 8 arms the plan asks for
         and assembles a list of ExperimentRun stubs without executing any paid work.
Input:   dataset_dir, seed, provider (default 'mock' so no paid LLM is called).
Output:  list of ExperimentRun stubs ready to be filled with metrics and saved.

The plan's final matrix compares these 8 arms (verbatim):
    1. code
    2. code_api
    3. code_taint
    4. apg
    5. ppg
    6. ppg_code
    7. ppg_knowledge
    8. ppg_code_knowledge

Arms 1 to 3 exercise the LLM caption harness (Phase 14 conditions A / B / C).
Arms 4 to 8 exercise the RGCN classifier (Phase 12 fusion arms + APG-only).

This module DOES NOT run anything. It defines what to run, produces the plan,
and refuses to invent numbers. Actually running the matrix belongs to a real
compute job with a budget approval.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pplib.experiment import ExperimentRun


FINAL_ARMS: tuple[str, ...] = (
    "code",
    "code_api",
    "code_taint",
    "apg",
    "ppg",
    "ppg_code",
    "ppg_knowledge",
    "ppg_code_knowledge",
)

# Which task the arm is scored on: LLM caption conditions vs RGCN classification.
_ARM_TASK: Dict[str, str] = {
    "code":               "captions",
    "code_api":           "captions",
    "code_taint":         "captions",
    "apg":                "classification",
    "ppg":                "classification",
    "ppg_code":           "classification",
    "ppg_knowledge":      "classification",
    "ppg_code_knowledge": "classification",
}

# Maps caption arms onto Phase 14 conditions.
_CAPTION_CONDITION: Dict[str, str] = {
    "code":       "A",
    "code_api":   "B",
    "code_taint": "C",
}

# Maps classification arms onto (privacy_features, token_features) for step2_convgnn.data.
# apg              structural + type embedding only
# ppg              plus PPG privacy overlay (knowledge from KB)
# ppg_code         plus statement tokens
# ppg_knowledge    same as ppg here (kept for plan verbatim)
# ppg_code_knowledge full featurization
_CLASSIFICATION_FLAGS: Dict[str, Dict[str, bool]] = {
    "apg":                {"privacy_features": False, "token_features": False},
    "ppg":                {"privacy_features": True,  "token_features": False},
    "ppg_code":           {"privacy_features": False, "token_features": True},
    "ppg_knowledge":      {"privacy_features": True,  "token_features": False},
    "ppg_code_knowledge": {"privacy_features": True,  "token_features": True},
}


@dataclass
class ArmSpec:
    """Everything Phase 21 needs to know about one arm to run it later."""

    arm: str
    task: str                             # 'captions' or 'classification'
    provider: str = "mock"
    condition: Optional[str] = None       # for captions: 'A' / 'B' / 'C'
    flags: Dict[str, bool] = field(default_factory=dict)   # for classification
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {"arm": self.arm, "task": self.task, "provider": self.provider,
             "notes": self.notes}
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
        return ArmSpec(
            arm=arm, task=task, provider=provider,
            condition=_CAPTION_CONDITION[arm],
            notes=(
                "LLM caption task. Provider stays 'mock' unless a budget-approved run "
                "overrides it explicitly."
            ),
        )
    return ArmSpec(
        arm=arm, task=task, provider=provider,
        flags=dict(_CLASSIFICATION_FLAGS[arm]),
        notes=(
            "RGCN classification. Featurization flags map onto step2_convgnn.data / arms.py."
        ),
    )


def enumerate_arms(provider: str = "mock") -> List[ArmSpec]:
    """Return one ArmSpec per arm in the canonical order."""
    return [arm_spec(a, provider=provider) for a in FINAL_ARMS]


def plan_runs(
    dataset_digest: str,
    config_digest: str,
    code_version: str,
    seed: int = 13,
    provider: str = "mock",
    start_from: int = 1,
) -> List[ExperimentRun]:
    """Assemble one ExperimentRun stub per arm. No metrics, no artifacts, no execution.

    The stubs are ready to be filled by the concrete runner (`run_captions_arm` or
    `train_classification_arm` when they exist) and then saved via
    `pplib.experiment.save_experiment`.
    """
    runs: List[ExperimentRun] = []
    for i, spec in enumerate(enumerate_arms(provider=provider), start=start_from):
        exp_id = f"EXP{i:03d}"
        runs.append(ExperimentRun(
            exp_id=exp_id,
            name=f"final_matrix::{spec.arm}",
            code_version=code_version,
            config_digest=config_digest,
            dataset_digest=dataset_digest,
            seed=seed,
            model_version="",                # filled by the runner
            metrics={},                      # NEVER pre-populated
            artifacts=[],
            notes=(
                f"Phase 21 final matrix, arm={spec.arm}, task={spec.task}, "
                f"provider={spec.provider}. Plan-only stub; metrics stay empty until "
                "the concrete run happens with a real compute budget."
            ),
        ))
    return runs
