"""
Purpose: Phase 14 LLM experiment harness. Builds one of six evidence conditions from a
         PRCS and records the metadata needed to compare captions across conditions.
Input:   a PRCS record and a condition name in {'A', 'B', 'C', 'D', 'E', 'F'}.
Output:  an evidence dict tailored to the condition, plus a ConditionResult record after a
         run that captures model, prompt, output, latency, token usage, and errors.

The six conditions mirror the plan verbatim:
    A - Code only
    B - Code + API
    C - Code + taint path
    D - Code + PPG (structural / relational context)
    E - Code + PPG + PAcT
    F - Full evidence package (everything the KB + PPG + PAcT know)

Provider abstraction is unchanged: any object with a `generate(prompt, evidence) -> str`
method works. Downstream comparison is driven by which condition wins on
BLEU / ROUGE / BERTScore / LLM-as-judge in Phase 15 and by the human ratings in Phase 15
human eval.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


CONDITIONS = ("A", "B", "C", "D", "E", "F")
CONDITION_LABELS: Dict[str, str] = {
    "A": "code_only",
    "B": "code_plus_api",
    "C": "code_plus_taint_path",
    "D": "code_plus_ppg",
    "E": "code_plus_ppg_plus_pact",
    "F": "full_evidence",
}


@dataclass
class ConditionResult:
    """One caption + provenance for one (PRCS, condition) pair."""

    prcs_id: str
    condition: str
    condition_label: str
    provider: str
    model: str
    prompt: str
    evidence: Dict[str, Any]
    caption: str
    latency_seconds: float
    prompt_chars: int
    caption_chars: int
    error: str = ""
    temperature: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_evidence(rec: Dict[str, Any], condition: str) -> Dict[str, Any]:
    """Project a full PRCS record onto the evidence subset that condition allows.

    condition must be one of CONDITIONS. Raises ValueError otherwise.
    Any consumer of the return value must NOT read fields outside the returned dict,
    or the ablation is meaningless.
    """
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}, expected one of {CONDITIONS}")

    ev: Dict[str, Any] = {
        "prcs_id": rec.get("prcs_id", ""),
        "code_snippet": rec.get("code_snippet", ""),
    }

    if condition == "A":                       # code only
        return ev

    if condition in ("B", "C", "D", "E", "F"):  # add API endpoints
        ev["source_api"] = rec.get("source_api", "")
        ev["sink_api"] = rec.get("sink_api", "")

    if condition in ("C", "F"):                # add taint path
        ev["taint_path"] = list(rec.get("taint_path", []))
        ev["taint_rules"] = list(rec.get("taint_rules", []))
        ev["hop_count"] = rec.get("hop_count", 0)

    if condition in ("D", "E", "F"):           # add PPG structural context
        sub = rec.get("subgraph", {})
        ev["subgraph_nodes"] = len(sub.get("nodes", []))
        ev["subgraph_edges"] = len(sub.get("edges", []))
        # Preserve node labels + edge types as compact strings, no full graph.
        ev["node_labels"] = sorted({n.get("label", "") for n in sub.get("nodes", []) if n.get("label")})
        ev["edge_types"] = sorted({e.get("type", "") for e in sub.get("edges", []) if e.get("type")})
        ev["involved_methods"] = list(rec.get("involved_methods", []))

    if condition in ("E", "F"):                # add PAcT labels + KB fields
        ev["pi_category"] = rec.get("pi_category", "")
        ev["pi_type"] = rec.get("pi_type", "")
        ev["permission"] = rec.get("permission", "")
        ev["sink_type"] = rec.get("sink_type", "")
        ev["privacy_threat"] = rec.get("privacy_threat", "")
        labels = rec.get("labels", {})
        ev["practice"] = list(labels.get("practice", []))
        ev["purpose"] = list(labels.get("purpose", []))

    if condition == "F":                        # everything else worth knowing
        ev["app_package"] = rec.get("app_package", "")
        ev["apk_filename"] = rec.get("apk_filename", "")
        ev["class_name"] = rec.get("class_name", "")
        ev["method_name"] = rec.get("method_name", "")

    return ev


def build_prompt(condition: str, evidence: Dict[str, Any]) -> str:
    """Compose the prompt shown to the LLM for one condition.

    Kept simple and stable so cross-condition comparisons are fair. Real ICL shots live
    in configs/llm.yaml and are appended by callers when desired.
    """
    header = (
        "You write short, accurate, user-facing Android privacy captions "
        "(4 to 5 short lines). Ground every claim in the evidence below; do not invent "
        "data types, purposes, recipients, storage, or sharing behaviors.\n\n"
    )
    label = CONDITION_LABELS.get(condition, condition)
    lines = [f"Condition {condition} ({label}). Evidence:"]
    for k, v in evidence.items():
        if k == "prcs_id":
            continue
        lines.append(f"  {k}: {v}")
    lines.append("\nCaption:")
    return header + "\n".join(lines)


def run_condition(rec: Dict[str, Any], condition: str, provider,
                  temperature: Optional[float] = None) -> ConditionResult:
    """Call `provider.generate(prompt, evidence)` and return a ConditionResult.

    Never raises: a provider error becomes a ConditionResult with `error` populated
    (so a bad row does not sink a whole sweep across many PRCS or many conditions).
    """
    evidence = build_evidence(rec, condition)
    prompt = build_prompt(condition, evidence)
    started = time.perf_counter()
    caption = ""
    error = ""
    try:
        caption = provider.generate(prompt, evidence)
    except Exception as e:                       # capture, do not raise
        error = f"{type(e).__name__}: {e}"
    elapsed = time.perf_counter() - started

    return ConditionResult(
        prcs_id=rec.get("prcs_id", ""),
        condition=condition,
        condition_label=CONDITION_LABELS.get(condition, condition),
        provider=getattr(provider, "name", provider.__class__.__name__),
        model=getattr(provider, "model", ""),
        prompt=prompt,
        evidence=evidence,
        caption=caption,
        latency_seconds=round(elapsed, 4),
        prompt_chars=len(prompt),
        caption_chars=len(caption),
        temperature=temperature,
        error=error,
    )


def run_all_conditions(rec: Dict[str, Any], provider,
                       conditions: Optional[List[str]] = None,
                       temperature: Optional[float] = None) -> List[ConditionResult]:
    """Sweep one PRCS across the requested conditions (default: all six)."""
    return [run_condition(rec, c, provider, temperature=temperature)
            for c in (conditions or list(CONDITIONS))]
