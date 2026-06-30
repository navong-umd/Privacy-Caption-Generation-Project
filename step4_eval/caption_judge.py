"""
Purpose: LLM-as-judge caption evaluation — score caption faithfulness + readability against the
         PRCS evidence, and a blind pairwise PPG-LLM-vs-Code2Seq-baseline comparison.
Input:   --dataset (adppg.jsonl evidence) + --captions (captions.json) + --provider.
Output:  data/caption_eval/caption_eval.json + .md (per-caption scores + aggregates).

This is the AUTOMATED stand-in for human caption references (which we don't have): an LLM judges
each caption's accuracy to the analyzed behaviour and its readability, and picks the better of the
PPG-informed LLM caption vs the Code2Seq baseline (blind, order-balanced). Results carry an
"LLM-JUDGED (not human ratings)" banner. The default mock judge is deterministic + offline so tests
need no key; a real judge runs with --provider openai|anthropic.

Run: python -m step4_eval.caption_judge --dataset data/corpus_run/dataset \
        --captions data/corpus_run/captions_llm --out data/corpus_run/caption_eval --provider openai
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from pplib.io_utils import dump_json, ensure_dir, get_logger, load_yaml

log = get_logger("caption_judge")
REPO_ROOT = Path(__file__).resolve().parent.parent
BANNER_JUDGE = "LLM-JUDGED — automated caption evaluation (not human ratings)"

_PI_TERMS = {
    "LOCATION_INFORMATION": "location", "UNIQUE_IDENTIFIER": "identifier",
    "PHONE_INFORMATION": "phone", "ACCOUNT_INFORMATION": "account",
    "CONTACT_INFORMATION": "contact", "CALENDAR_INFORMATION": "calendar",
    "SMS_MMS": "message", "BROWSER_INFORMATION": "brows",
    "NETWORK_INFORMATION": "network", "DATABASE_INFORMATION": "data",
    "AUDIO_INPUT_OUTPUT": "audio", "SYNCHRONIZATION_DATA": "sync",
}


def _facts(rec: Dict) -> Dict:
    labels = rec.get("labels", {})
    return {
        "pi": rec.get("pi_category", "") or rec.get("pi_type", ""),
        "pi_term": _PI_TERMS.get(rec.get("pi_category", "") or rec.get("pi_type", ""), ""),
        "practice": labels.get("practice", []), "purpose": labels.get("purpose", []),
        "sink_type": rec.get("sink_type", ""),
    }


# ---------- offline deterministic (mock) judge ----------
def _heuristic_score(caption: str, f: Dict) -> Dict:
    c = (caption or "").lower()
    hits = 0
    total = 0
    if f["pi_term"]:
        total += 1; hits += 1 if f["pi_term"] in c else 0
    practice_words = {"Collecting": ["collect", "access", "read"], "Processing": ["process", "use"],
                      "Sharing": ["shar", "send", "transmit", "network"]}
    for p in f["practice"]:
        total += 1
        if any(w in c for w in practice_words.get(p, [p.lower()])):
            hits += 1
    purpose_words = {"Advertisement": ["advertis", "ad "], "Analytics": ["analyt", "measur", "track"],
                     "Functionality": ["function", "feature", "perform"]}
    for p in f["purpose"]:
        total += 1
        if any(w in c for w in purpose_words.get(p, [p.lower()])):
            hits += 1
    accuracy = 5 if total == 0 else round(1 + 4 * hits / total)
    # readability: rewards multiple sentences + reasonable length, penalises raw identifiers
    sents = [s for s in re.split(r"[.!?]", caption or "") if s.strip()]
    words = len((caption or "").split())
    readability = 1 + min(4, (1 if len(sents) >= 2 else 0) + (1 if 8 <= words <= 60 else 0)
                          + (2 if "->" not in (caption or "") and not re.search(r"\b[a-z]\(", caption or "") else 0))
    return {"accuracy": int(accuracy), "readability": int(readability),
            "faithful": bool(accuracy >= 3)}


def _heuristic_pairwise(llm: str, base: str, f: Dict) -> str:
    la = _heuristic_score(llm, f); ba = _heuristic_score(base, f)
    ls = la["accuracy"] + la["readability"]; bs = ba["accuracy"] + ba["readability"]
    return "baseline" if bs > ls else "llm"   # ties -> the PPG-informed LLM caption


# ---------- real LLM judge ----------
def _extract_json(text: str) -> Optional[Dict]:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _llm_score(provider, caption: str, f: Dict) -> Dict:  # pragma: no cover (needs key)
    prompt = (
        "You judge an app privacy caption against the analyzed behaviour. Reply ONLY JSON: "
        '{"accuracy":1-5,"readability":1-5,"faithful":true|false}. '
        "accuracy = how well the caption matches the facts; readability = how clear it is to a user.\n"
        f"facts: personal_data={f['pi']} practice={f['practice']} purpose={f['purpose']} sink={f['sink_type']}\n"
        f"caption: {caption}")
    d = _extract_json(provider.generate(prompt, {})) or {}
    return {"accuracy": int(d.get("accuracy", 3)), "readability": int(d.get("readability", 3)),
            "faithful": bool(d.get("faithful", False))}


def _llm_pairwise(provider, a: str, b: str, f: Dict) -> str:  # pragma: no cover (needs key)
    prompt = (
        "Two privacy captions describe the same app behaviour. Which is more accurate AND readable "
        'for an end user? Reply ONLY JSON: {"winner":"A"|"B"}.\n'
        f"facts: personal_data={f['pi']} practice={f['practice']} purpose={f['purpose']} sink={f['sink_type']}\n"
        f"Caption A: {a}\nCaption B: {b}")
    d = _extract_json(provider.generate(prompt, {})) or {}
    return "A" if str(d.get("winner", "A")).upper().startswith("A") else "B"


def judge_captions(dataset_dir: str, captions_dir: str, out_dir: str,
                   provider_name: str = "mock", llm_config: Optional[str] = None) -> Dict:
    """Score every caption + run the blind pairwise comparison. Returns the aggregate report."""
    records = {json.loads(l)["prcs_id"]: json.loads(l) for l in
               (Path(dataset_dir) / "adppg.jsonl").read_text(encoding="utf-8").splitlines()}
    caps = json.loads((Path(captions_dir) / "captions.json").read_text(encoding="utf-8"))

    use_llm = provider_name and provider_name != "mock"
    provider = None
    if use_llm:
        from pplib.io_utils import load_dotenv
        from step3_caption.llm_interface import get_provider
        load_dotenv()
        cfg = load_yaml(llm_config or REPO_ROOT / "configs" / "llm.yaml")
        provider = get_provider({**cfg, "provider": provider_name})

    per: List[Dict] = []
    llm_wins = base_wins = 0
    sums = {"llm_acc": 0, "llm_read": 0, "base_acc": 0, "base_read": 0}
    for i, c in enumerate(caps):
        rec = records.get(c["prcs_id"], {})
        f = _facts(rec)
        if use_llm:
            ls = _llm_score(provider, c["caption"], f)
            bs = _llm_score(provider, c.get("baseline_caption", ""), f)
            # order-balanced blind A/B to cancel position bias
            a, b = (c["caption"], c["baseline_caption"]) if i % 2 == 0 else (c["baseline_caption"], c["caption"])
            win = _llm_pairwise(provider, a, b, f)
            winner = ("llm" if win == "A" else "baseline") if i % 2 == 0 else ("baseline" if win == "A" else "llm")
        else:
            ls = _heuristic_score(c["caption"], f)
            bs = _heuristic_score(c.get("baseline_caption", ""), f)
            winner = _heuristic_pairwise(c["caption"], c.get("baseline_caption", ""), f)
        llm_wins += winner == "llm"; base_wins += winner == "baseline"
        sums["llm_acc"] += ls["accuracy"]; sums["llm_read"] += ls["readability"]
        sums["base_acc"] += bs["accuracy"]; sums["base_read"] += bs["readability"]
        per.append({"prcs_id": c["prcs_id"], "llm": ls, "baseline": bs, "winner": winner})

    n = max(1, len(caps))
    report = {
        "banner": BANNER_JUDGE, "judge": provider_name, "n_captions": len(caps),
        "llm_mean": {"accuracy": round(sums["llm_acc"] / n, 2), "readability": round(sums["llm_read"] / n, 2)},
        "baseline_mean": {"accuracy": round(sums["base_acc"] / n, 2), "readability": round(sums["base_read"] / n, 2)},
        "pairwise": {"llm_wins": llm_wins, "baseline_wins": base_wins,
                     "llm_win_rate": round(llm_wins / n, 3)},
        "per_caption": per,
    }
    out = ensure_dir(out_dir)
    dump_json(report, out / "caption_eval.json")
    (out / "caption_eval.md").write_text(_render_md(report), encoding="utf-8")
    log.info("Judged %d captions (judge=%s): LLM win-rate %.0f%%",
             len(caps), provider_name, 100 * report["pairwise"]["llm_win_rate"])
    return report


def _render_md(r: Dict) -> str:
    return (f"# Caption evaluation (LLM-judged)\n\n> **{r['banner']}** · judge=`{r['judge']}` · "
            f"n={r['n_captions']}\n\n"
            f"| Caption source | Accuracy (1-5) | Readability (1-5) |\n|---|--:|--:|\n"
            f"| **PPG-informed LLM** | {r['llm_mean']['accuracy']} | {r['llm_mean']['readability']} |\n"
            f"| Code2Seq baseline | {r['baseline_mean']['accuracy']} | {r['baseline_mean']['readability']} |\n\n"
            f"**Pairwise (blind A/B):** PPG-LLM preferred in **{r['pairwise']['llm_wins']}/"
            f"{r['n_captions']}** ({100 * r['pairwise']['llm_win_rate']:.0f}%) vs "
            f"{r['pairwise']['baseline_wins']} for the baseline.\n")


def main() -> None:
    ap = argparse.ArgumentParser(description="LLM-as-judge caption evaluation (Step 4).")
    ap.add_argument("--dataset", default="data/dataset")
    ap.add_argument("--captions", default="data/captions")
    ap.add_argument("--out", default="data/caption_eval")
    ap.add_argument("--provider", default="mock", help="mock | openai | anthropic | ...")
    ap.add_argument("--config", default="configs/llm.yaml")
    args = ap.parse_args()
    r = judge_captions(args.dataset, args.captions, args.out, args.provider, args.config)
    print("\n=== Caption evaluation (LLM-judged) ===")
    print(f"  [{r['banner']}]  judge={r['judge']}  n={r['n_captions']}")
    print(f"  PPG-LLM   accuracy={r['llm_mean']['accuracy']}  readability={r['llm_mean']['readability']}")
    print(f"  baseline  accuracy={r['baseline_mean']['accuracy']}  readability={r['baseline_mean']['readability']}")
    print(f"  pairwise: PPG-LLM preferred {r['pairwise']['llm_wins']}/{r['n_captions']} "
          f"({100 * r['pairwise']['llm_win_rate']:.0f}%)")


if __name__ == "__main__":
    main()
