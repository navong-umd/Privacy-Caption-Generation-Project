"""
Purpose: Aggregate every automated caption-quality signal into one per-caption report
         and one corpus-level summary (Phase 15).
Input:   captions list (from step3_caption.generate), ADPPG records (for evidence and
         optional references), and optional LLM-judge output rows.
Output:  {"per_caption": [...], "summary": {...}} with BLEU / ROUGE-L / grounding pass /
         LLM-judge score, plus the honest 'no references' fallback when applicable.

Human eval is deferred to the final gate (per user rule). This aggregator is automated only.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from step3_caption.generate import _evidence
from step3_caption.grounding import check_grounding
from step4_eval.text_metrics import rouge_l, sentence_bleu

NO_REFS_MESSAGE = "no references on disk, BLEU / ROUGE-L not computed"


def _score_bleu_rouge(caption: str, refs: List[str]) -> Dict[str, Optional[float]]:
    if not refs:
        return {"bleu4": None, "rouge_l": None}
    return {
        "bleu4": float(sentence_bleu(caption or "", refs, max_n=4)),
        "rouge_l": float(rouge_l(caption or "", refs)),
    }


def aggregate(
    captions: Sequence[Dict[str, Any]],
    records: Sequence[Dict[str, Any]],
    references: Optional[Dict[str, Any]] = None,
    judge_rows: Optional[Sequence[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Combine text metrics, grounding, and any LLM-judge output into one report.

    `captions`     entries with `prcs_id` + `caption` (as produced by step3_caption.generate).
    `records`      ADPPG records; used to reconstruct evidence via _evidence(rec).
    `references`   optional {prcs_id -> reference caption or list of them}.
    `judge_rows`   optional list of dicts with `prcs_id` + `score` (0..1) + `verdict` fields.
    """
    id_to_rec = {r["prcs_id"]: r for r in records}
    id_to_refs: Dict[str, List[str]] = {}
    for pid, val in (references or {}).items():
        if isinstance(val, list):
            id_to_refs[pid] = [str(v) for v in val]
        else:
            id_to_refs[pid] = [str(val)]
    id_to_judge: Dict[str, Dict[str, Any]] = {
        row["prcs_id"]: row for row in (judge_rows or []) if "prcs_id" in row
    }

    per_caption: List[Dict[str, Any]] = []
    scored = {"bleu4": 0.0, "rouge_l": 0.0, "count_with_refs": 0}
    grounding = {"passed": 0, "total": 0}
    judge = {"sum": 0.0, "count": 0}

    for c in captions:
        pid = c.get("prcs_id", "")
        text = c.get("caption", "")
        rec = id_to_rec.get(pid)
        refs = id_to_refs.get(pid, [])

        # 1. Text metrics against references (if any).
        text_metrics = _score_bleu_rouge(text, refs)
        if text_metrics["bleu4"] is not None:
            scored["bleu4"] += text_metrics["bleu4"]
            scored["rouge_l"] += text_metrics["rouge_l"]
            scored["count_with_refs"] += 1

        # 2. Grounding (Phase 13) against reconstructed evidence.
        if rec is not None:
            report = check_grounding(text, _evidence(rec), prcs_id=pid)
            grounding_row = report.to_dict()
            grounding["total"] += 1
            if report.passes:
                grounding["passed"] += 1
        else:
            grounding_row = None

        # 3. LLM judge score (if present).
        judge_row = id_to_judge.get(pid)
        if judge_row and isinstance(judge_row.get("score"), (int, float)):
            judge["sum"] += float(judge_row["score"])
            judge["count"] += 1

        per_caption.append({
            "prcs_id": pid,
            "caption": text,
            "label_source": c.get("label_source", ""),
            "text_metrics": text_metrics,
            "grounding": grounding_row,
            "judge": judge_row,
        })

    n_refs = scored["count_with_refs"]
    text_summary: Dict[str, Any]
    if n_refs > 0:
        text_summary = {
            "bleu4_mean": scored["bleu4"] / n_refs,
            "rouge_l_mean": scored["rouge_l"] / n_refs,
            "n_scored": n_refs,
        }
    else:
        text_summary = {"status": NO_REFS_MESSAGE, "n_scored": 0}

    grounding_summary = {
        "passed": grounding["passed"],
        "total": grounding["total"],
        "pass_rate": (grounding["passed"] / grounding["total"]) if grounding["total"] else 0.0,
    }
    judge_summary: Dict[str, Any]
    if judge["count"]:
        judge_summary = {"mean": judge["sum"] / judge["count"], "n": judge["count"]}
    else:
        judge_summary = {"status": "no judge rows"}

    return {
        "per_caption": per_caption,
        "summary": {
            "n_captions": len(captions),
            "text_metrics": text_summary,
            "grounding": grounding_summary,
            "judge": judge_summary,
            "human_eval_deferred": True,
        },
    }
