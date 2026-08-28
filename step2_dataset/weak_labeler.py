"""
Purpose: Assign WEAK heuristic Practice+Purpose labels to a PRCS (BOOTSTRAP only).
Input:   a PRCS record (dict) + weak-label rules + SDK catalog.
Output:  {practice:[...], purpose:[...], label_source:"weak", weak_banner, rationale}.

!!! WEAK — NOT GROUND TRUTH. These exist solely to make the ConvGNN runnable before
human Codr annotation (Gate G1). Every consumer must surface the banner.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from pplib.io_utils import load_yaml
from pplib.pact_schema import PACT_SCHEMA_VERSION
from pplib.schema import BANNER_WEAK, PRACTICE_LABELS, PURPOSE_LABELS

REPO_ROOT = Path(__file__).resolve().parent.parent


class WeakLabeler:
    """Heuristic multi-label labeler keyed on sink type + third-party SDK packages."""

    def __init__(self, rules_path: Path | None = None, sdk_path: Path | None = None):
        self.rules = load_yaml(rules_path or REPO_ROOT / "configs" / "weak_labels.yaml")
        sdk = load_yaml(sdk_path or REPO_ROOT / "configs" / "sdk_catalog.yaml")
        self.ad_pkgs: List[str] = sdk.get("advertisement", [])
        self.an_pkgs: List[str] = sdk.get("analytics", [])

    def _classes(self, prcs: dict) -> List[str]:
        """All class names referenced by the PRCS (involved methods + subgraph Class nodes)."""
        classes = {m.split("->", 1)[0] for m in prcs.get("involved_methods", [])}
        for n in prcs.get("subgraph", {}).get("nodes", []):
            if n.get("label") == "Class":
                classes.add(n["id"])
        return sorted(classes)

    def label(self, prcs: dict) -> dict:
        sink_type = prcs.get("sink_type", "")
        practice = set(self.rules.get("practice_source_default", []))
        practice.update(self.rules.get("practice_by_sink", {}).get(sink_type, []))
        if not practice:
            practice.update(self.rules.get("practice_fallback", ["Other"]))

        classes = self._classes(prcs)
        purpose = set()
        rationale = [f"sink_type={sink_type or 'none'}"]
        if any(c.startswith(p) for c in classes for p in self.ad_pkgs):
            purpose.update(self.rules.get("purpose_advertisement", []))
            rationale.append("ad-SDK class present")
        if any(c.startswith(p) for c in classes for p in self.an_pkgs):
            purpose.update(self.rules.get("purpose_analytics", []))
            rationale.append("analytics-SDK class present")
        if not purpose:
            purpose.update(self.rules.get("purpose_default", ["Functionality"]))
            rationale.append("no 3rd-party SDK -> Functionality")

        return {
            "practice": [l for l in PRACTICE_LABELS if l in practice],
            "purpose": [l for l in PURPOSE_LABELS if l in purpose],
            "label_source": "weak",
            "weak_banner": BANNER_WEAK,
            "rationale": "; ".join(rationale),
            "schema_version": PACT_SCHEMA_VERSION,
        }
