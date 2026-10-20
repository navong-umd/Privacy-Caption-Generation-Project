"""Aggregation logic between the raw loaders and the API models.

Keeps routers thin. Every number here comes from a real artifact; when an
artifact is absent the corresponding field is None / empty, never invented.
"""
from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Optional

from webapi import loader
from webapi.config import DATA_ROOT
from webapi.loader import PRACTICE_LABELS, PURPOSE_LABELS

# The eight canonical pipeline stages, straight from the research docs. Not fabricated.
PIPELINE_STAGES: List[Dict[str, str]] = [
    {"key": "apk", "title": "APK Analysis", "tool": "androguard",
     "description": "Disassemble the Android APK's Dalvik bytecode and record provenance (sha256, tool versions).",
     "inputs": "app.apk", "outputs": "APG CSVs + APG_META.json"},
    {"key": "apg", "title": "App Property Graph", "tool": "pplib/apg_model",
     "description": "Four interlocking views of the program: AST, call graph (MCG), control flow (ICFG), and data dependence (DDG).",
     "inputs": "Dalvik bytecode", "outputs": "{AST,MCG,ICFG,DDG}_{nodes,edges}.csv"},
    {"key": "kb", "title": "Knowledge Base", "tool": "pplib/knowledge",
     "description": "Classify each API call as a personal-information source or a data sink, with a provenance tier and Android permission.",
     "inputs": "API callee strings", "outputs": "source / sink / permission tags"},
    {"key": "ppg", "title": "Privacy Property Graph", "tool": "stage4_ppg/build_ppg",
     "description": "Overlay privacy semantics on the APG: Source / Sink / DataItem nodes, taint flows, and LINDDUN threat tags.",
     "inputs": "APG + knowledge base", "outputs": "PPG nodes/edges + taint paths"},
    {"key": "prcs", "title": "Privacy-Relevant Code Slice", "tool": "step2_prcs/extract_prcs",
     "description": "Slice one subgraph per source-to-sink flow: the methods it touches, the privacy overlay, and a bounded neighborhood.",
     "inputs": "PPG", "outputs": "one PRCS record per flow"},
    {"key": "pact", "title": "PAcT Labels", "tool": "step2_dataset",
     "description": "Attach multi-label Practice (Collecting / Processing / Sharing / Other) and Purpose (Functionality / Advertisement / Analytics / Other).",
     "inputs": "PRCS", "outputs": "ADPPG dataset + leak-safe splits"},
    {"key": "model", "title": "Graph Classifier", "tool": "step2_convgnn (RGCN)",
     "description": "A relation-aware graph neural network with two multi-label heads for Practice and Purpose.",
     "inputs": "ADPPG subgraphs", "outputs": "predicted PAcT labels"},
    {"key": "caption", "title": "Caption Generation", "tool": "step3_caption",
     "description": "Turn the structured evidence into a short, evidence-grounded privacy caption, then a GDPR/CCPA policy.",
     "inputs": "PRCS + labels", "outputs": "captions + policy documents"},
]


def _f(metrics: Dict[str, str], key: str) -> Optional[float]:
    v = metrics.get(key)
    if v is None:
        return None
    try:
        return float(v)
    except ValueError:
        return None


def build_banners() -> List[Dict[str, str]]:
    banners: List[Dict[str, str]] = []
    er = loader.eval_report()
    if er.get("bootstrap") or (er.get("classification", {}) or {}).get("is_weak"):
        banners.append({
            "kind": "bootstrap",
            "text": "Classification metrics are computed on test labels that are not human-annotated (heuristic or LLM-assigned). Directional only until human annotation (Gate G1).",
        })
    sources = Counter(v["label_source"] for v in loader.labels().values())
    if sources["llm"]:
        banners.append({
            "kind": "llm",
            "text": f"{sources['llm']} labels were assigned by an LLM, not a human annotator. They are not ground truth.",
        })
    ce = loader.caption_eval()
    if ce:
        banners.append({
            "kind": "judge",
            "text": "Caption quality is scored by an LLM judge, not human ratings. Human evaluation is the reserved final gate.",
        })
    return banners


def build_overview() -> Dict[str, Any]:
    idx = loader.prcs_index()
    er = loader.eval_report()
    cls = er.get("classification", {}) or {}
    ce = loader.caption_eval()
    splits_counts = Counter(r.get("split", "") for r in idx if r.get("split"))

    judge = None
    if ce.get("llm_mean"):
        judge = {
            "llm_accuracy": ce["llm_mean"].get("accuracy"),
            "llm_readability": ce["llm_mean"].get("readability"),
            "llm_win_rate": (ce.get("pairwise", {}) or {}).get("llm_win_rate"),
        }

    return {
        "title": "Privacy Caption Generation",
        "summary": (
            "Given an Android APK, we build a privacy-aware graph of the program, trace how personal "
            "data flows from sources to sinks, classify the privacy practice and purpose, and generate "
            "evidence-grounded privacy captions and GDPR/CCPA policy notices."
        ),
        "data_root": str(DATA_ROOT.name),
        "n_apps": len(loader.app_packages()),
        "n_prcs": len(idx),
        "n_captions_llm": len(loader.captions_llm()),
        "n_captions_mock": len(loader.captions_mock()),
        "splits": dict(splits_counts),
        "practice_macro_f1": cls.get("practice_macro_f1"),
        "purpose_macro_f1": cls.get("purpose_macro_f1"),
        "n_test": cls.get("n_test"),
        "caption_judge": judge,
        "banners": build_banners(),
        "pipeline": PIPELINE_STAGES,
    }


def _app_prcs_counts(pkg: str) -> int:
    return sum(1 for r in loader.prcs_index() if r.get("app_package") == pkg)


def app_summary(pkg: str) -> Optional[Dict[str, Any]]:
    pol = loader.policy().get("apps", {}).get(pkg)
    comp = ((loader.eval_report().get("compliance", {}) or {}).get("per_app", {}) or {}).get(pkg, {})
    if pol is None and _app_prcs_counts(pkg) == 0:
        return None
    sections = (pol or {}).get("sections", {})
    reqs = (pol or {}).get("requirements", {})
    return {
        "package": pkg,
        "display_name": loader.display_name(pkg),
        "n_prcs": _app_prcs_counts(pkg),
        "collected": sections.get("collected", []),
        "purposes": sections.get("purposes", []),
        "shared_with": sections.get("shared_with", []),
        "gdpr_reqs": len(reqs.get("gdpr", [])),
        "ccpa_reqs": len(reqs.get("ccpa", [])),
        "completeness": comp.get("completeness"),
    }


def app_detail(pkg: str) -> Optional[Dict[str, Any]]:
    summ = app_summary(pkg)
    if summ is None:
        return None
    rows = [r for r in loader.prcs_index() if r.get("app_package") == pkg]
    pi_counts = Counter(r.get("pi_category", "") for r in rows if r.get("pi_category"))
    sink_counts = Counter(r.get("sink_type", "") for r in rows if r.get("sink_type"))
    pol = loader.policy().get("apps", {}).get(pkg, {})
    reqs = pol.get("requirements", {})

    llm = loader.captions_llm()
    samples: List[Dict[str, Any]] = []
    for r in rows:
        entry = llm.get(r["prcs_id"])
        if entry:
            samples.append(_caption_row(entry))
        if len(samples) >= 5:
            break

    summ.update({
        "top_pi_categories": [{"name": k, "count": v} for k, v in pi_counts.most_common(8)],
        "top_sink_types": [{"name": k, "count": v} for k, v in sink_counts.most_common(8)],
        "gdpr": reqs.get("gdpr", []),
        "ccpa": reqs.get("ccpa", []),
        "sample_captions": samples,
    })
    return summ


def _caption_row(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "prcs_id": entry.get("prcs_id", ""),
        "app_package": entry.get("app_package", ""),
        "caption": entry.get("caption", ""),
        "provider": entry.get("provider", ""),
        "label_source": entry.get("label_source", ""),
        "baseline_caption": entry.get("baseline_caption"),
    }


def filter_prcs(
    app: Optional[str], pi_category: Optional[str], sink_type: Optional[str],
    practice: Optional[str], purpose: Optional[str], label_source: Optional[str],
    split: Optional[str], q: Optional[str], page: int, page_size: int,
) -> Dict[str, Any]:
    rows = loader.prcs_index()
    ql = q.lower().strip() if q else None

    def keep(r: Dict[str, Any]) -> bool:
        if app and r.get("app_package") != app:
            return False
        if pi_category and r.get("pi_category") != pi_category:
            return False
        if sink_type and r.get("sink_type") != sink_type:
            return False
        if practice and practice not in r.get("practice", []):
            return False
        if purpose and purpose not in r.get("purpose", []):
            return False
        if label_source and r.get("label_source") != label_source:
            return False
        if split and r.get("split") != split:
            return False
        if ql:
            hay = " ".join([
                r.get("prcs_id", ""), r.get("source_api", ""), r.get("sink_api", ""),
                r.get("class_name", ""), r.get("method_name", ""),
            ]).lower()
            if ql not in hay:
                return False
        return True

    filtered = [r for r in rows if keep(r)]
    total = len(filtered)
    start = (page - 1) * page_size
    items = filtered[start:start + page_size]
    return {
        "total": total, "page": page, "page_size": page_size,
        "has_more": start + page_size < total, "items": items,
    }


def prcs_detail(prcs_id: str) -> Optional[Dict[str, Any]]:
    rec = loader.prcs_detail(prcs_id)
    if rec is None:
        return None
    meta = loader.prcs_index_by_id().get(prcs_id, {})
    sub = rec.get("subgraph", {})
    edges = []
    for e in sub.get("edges", []):
        edges.append({
            "start": e.get("start", ""), "end": e.get("end", ""),
            "type": e.get("type", ""), "taint_rule": e.get("taint_rule"),
        })
    llm = loader.captions_llm().get(prcs_id, {})
    mock = loader.captions_mock().get(prcs_id, {})
    return {
        "prcs_id": rec.get("prcs_id", prcs_id),
        "app_package": rec.get("app_package", ""),
        "apk_filename": rec.get("apk_filename"),
        "class_name": rec.get("class_name", ""),
        "method_name": rec.get("method_name", ""),
        "method_signature": rec.get("method_signature"),
        "source_api": rec.get("source_api", ""),
        "sink_api": rec.get("sink_api", ""),
        "sink_type": rec.get("sink_type", ""),
        "sink_label": rec.get("sink_label"),
        "pi_type": rec.get("pi_type", ""),
        "pi_category": rec.get("pi_category", ""),
        "permission": rec.get("permission", ""),
        "privacy_threat": rec.get("privacy_threat", ""),
        "hop_count": rec.get("hop_count", 0),
        "involved_methods": rec.get("involved_methods", []),
        "code_snippet": rec.get("code_snippet", ""),
        "subgraph": {"nodes": sub.get("nodes", []), "edges": edges},
        "taint_path": rec.get("taint_path"),
        "taint_rules": rec.get("taint_rules"),
        "label_source": meta.get("label_source", ""),
        "practice": meta.get("practice", []),
        "purpose": meta.get("purpose", []),
        "split": meta.get("split", ""),
        "llm_caption": llm.get("caption"),
        "mock_caption": mock.get("caption"),
        "baseline_caption": (llm or mock).get("baseline_caption"),
    }


def filter_captions(
    app: Optional[str], provider: str, q: Optional[str], page: int, page_size: int,
) -> Dict[str, Any]:
    source = loader.captions_llm() if provider == "llm" else loader.captions_mock()
    ql = q.lower().strip() if q else None
    rows = list(source.values())

    def keep(e: Dict[str, Any]) -> bool:
        if app and e.get("app_package") != app:
            return False
        if ql and ql not in (e.get("caption", "") + " " + e.get("prcs_id", "")).lower():
            return False
        return True

    filtered = [e for e in rows if keep(e)]
    total = len(filtered)
    start = (page - 1) * page_size
    items = [_caption_row(e) for e in filtered[start:start + page_size]]
    return {
        "total": total, "page": page, "page_size": page_size,
        "has_more": start + page_size < total, "items": items,
    }


def classification_results() -> Dict[str, Any]:
    m = loader.model_metrics()
    banner_text = m.get("BANNER", "")
    banner = {"kind": "bootstrap" if banner_text else "none", "text": banner_text}

    def labels_for(head: str, label_list: List[str]) -> List[Dict[str, Any]]:
        out = []
        for lbl in label_list:
            out.append({
                "label": lbl,
                "precision": _f(m, f"{head}_{lbl}_P"),
                "recall": _f(m, f"{head}_{lbl}_R"),
                "f1": _f(m, f"{head}_{lbl}_F1"),
            })
        return out

    return {
        "banner": banner,
        "n_test": (loader.eval_report().get("classification", {}) or {}).get("n_test"),
        "practice_macro_f1": _f(m, "practice_macro_f1"),
        "practice_micro_f1": _f(m, "practice_micro_f1"),
        "purpose_macro_f1": _f(m, "purpose_macro_f1"),
        "purpose_micro_f1": _f(m, "purpose_micro_f1"),
        "practice_labels": labels_for("practice", PRACTICE_LABELS),
        "purpose_labels": labels_for("purpose", PURPOSE_LABELS),
    }


def caption_results() -> Dict[str, Any]:
    ce = loader.caption_eval()
    banner = {"kind": "judge" if ce else "none", "text": ce.get("banner", "")}
    return {
        "banner": banner,
        "judge": ce.get("judge"),
        "n_captions": ce.get("n_captions", 0),
        "llm_mean": ce.get("llm_mean"),
        "baseline_mean": ce.get("baseline_mean"),
        "pairwise": ce.get("pairwise"),
    }


def compliance_results() -> Dict[str, Any]:
    comp = loader.eval_report().get("compliance", {}) or {}
    per = comp.get("per_app", {}) or {}
    apps = []
    for pkg, info in per.items():
        apps.append({
            "package": pkg,
            "display_name": loader.display_name(pkg),
            "facts": info.get("facts", 0),
            "surfaced": info.get("surfaced", 0),
            "completeness": info.get("completeness", 0.0),
            "gdpr_reqs": info.get("gdpr_reqs", 0),
            "ccpa_reqs": info.get("ccpa_reqs", 0),
        })
    apps.sort(key=lambda a: -a["facts"])
    return {"overall_completeness": comp.get("overall_completeness"), "per_app": apps}


def experiments_status() -> Dict[str, Any]:
    from webapi.config import REPO_ROOT
    idx = REPO_ROOT / "experiments" / "index.jsonl"
    if idx.exists():
        n = sum(1 for line in idx.read_text(encoding="utf-8").splitlines() if line.strip())
        return {"available": n > 0, "logged_runs": n,
                "note": "Experiment runs logged to experiments/index.jsonl."}
    return {
        "available": False, "logged_runs": 0,
        "note": "No experiment runs are logged yet. The final eight-arm matrix and human evaluation are reserved for a budget-approved run; numbers appear here only from real manifests.",
    }
