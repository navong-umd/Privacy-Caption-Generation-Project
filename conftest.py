"""Pytest root config: put the repo root on sys.path and expose shared fixtures."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

SYNTH_APG = REPO_ROOT / "data" / "fixtures" / "synthetic_apg"
SYNTH_APG_LARGE = REPO_ROOT / "data" / "fixtures" / "synthetic_apg_large"
PPG_CONFIG = REPO_ROOT / "configs" / "ppg.yaml"


@pytest.fixture(scope="session")
def synth_apg_dir() -> Path:
    """Path to the committed tiny SYNTHETIC APG fixture."""
    return SYNTH_APG


@pytest.fixture(scope="session")
def ppg_builder(tmp_path_factory):
    """Build the PPG once from the synthetic fixture for cross-stage tests."""
    from stage4_ppg.build_ppg import build_ppg

    out = tmp_path_factory.mktemp("ppg")
    builder = build_ppg(str(SYNTH_APG), str(PPG_CONFIG), str(out))
    return builder, out


@pytest.fixture(scope="session")
def dataset_dir(tmp_path_factory):
    """Run PPG->PRCS->ADPPG on the 8-app fixture for meaningful train/val/test splits."""
    from stage4_ppg.build_ppg import build_ppg
    from step2_prcs.extract_prcs import extract_prcs
    from step2_dataset.build_dataset import build_dataset

    root = tmp_path_factory.mktemp("pipe")
    build_ppg(str(SYNTH_APG_LARGE), str(PPG_CONFIG), str(root / "ppg"))
    extract_prcs(str(root / "ppg"), str(root / "prcs"))
    build_dataset(str(root / "prcs"), str(root / "dataset"))
    return root / "dataset"
