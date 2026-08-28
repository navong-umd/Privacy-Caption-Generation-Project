"""Pydantic response models. These are the API contract the frontend types mirror.

Fields marked Optional are ones the older committed corpus run may not carry
(for example taint_rules / schema_version, added in a later pipeline phase).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


# ---- shared ----

class Banner(BaseModel):
    kind: str            # "bootstrap" | "weak" | "judge" | "none"
    text: str


class PipelineStage(BaseModel):
    key: str
    title: str
    tool: str
    description: str
    inputs: str
    outputs: str


class Overview(BaseModel):
    title: str
    summary: str
    data_root: str
    n_apps: int
    n_prcs: int
    n_captions_llm: int
    n_captions_mock: int
    splits: Dict[str, int]
    practice_macro_f1: Optional[float] = None
    purpose_macro_f1: Optional[float] = None
    n_test: Optional[int] = None
    caption_judge: Optional[Dict[str, float]] = None
    banners: List[Banner]
    pipeline: List[PipelineStage]


# ---- apps ----

class AppSummary(BaseModel):
    package: str
    display_name: str
    n_prcs: int
    collected: List[str]
    purposes: List[str]
    shared_with: List[str]
    gdpr_reqs: int
    ccpa_reqs: int
    completeness: Optional[float] = None


class AppDetail(AppSummary):
    top_pi_categories: List[Dict[str, object]]     # [{name, count}]
    top_sink_types: List[Dict[str, object]]        # [{name, count}]
    gdpr: List[str]
    ccpa: List[str]
    sample_captions: List["CaptionRow"]


# ---- prcs ----

class PrcsListItem(BaseModel):
    prcs_id: str
    app_package: str
    class_name: str
    method_name: str
    source_api: str
    sink_api: str
    sink_type: str
    pi_type: str
    pi_category: str
    permission: str
    privacy_threat: str
    hop_count: int
    n_nodes: int
    n_edges: int
    label_source: str
    practice: List[str]
    purpose: List[str]
    split: str


class GraphNode(BaseModel):
    id: str
    label: Optional[str] = None
    type: Optional[str] = None
    callee: Optional[str] = None
    code: Optional[str] = None


class GraphEdge(BaseModel):
    start: str
    end: str
    type: str
    taint_rule: Optional[str] = None


class Subgraph(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class CaptionRow(BaseModel):
    prcs_id: str
    app_package: str
    caption: str
    provider: str
    label_source: str
    baseline_caption: Optional[str] = None


class PrcsDetail(BaseModel):
    prcs_id: str
    app_package: str
    apk_filename: Optional[str] = None
    class_name: str
    method_name: str
    method_signature: Optional[str] = None
    source_api: str
    sink_api: str
    sink_type: str
    sink_label: Optional[str] = None
    pi_type: str
    pi_category: str
    permission: str
    privacy_threat: str
    hop_count: int
    involved_methods: List[str]
    code_snippet: str
    subgraph: Subgraph
    taint_path: Optional[List[str]] = None
    taint_rules: Optional[List[str]] = None
    label_source: str
    practice: List[str]
    purpose: List[str]
    split: str
    llm_caption: Optional[str] = None
    mock_caption: Optional[str] = None
    baseline_caption: Optional[str] = None


# ---- results ----

class LabelMetric(BaseModel):
    label: str
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1: Optional[float] = None


class ClassificationResults(BaseModel):
    banner: Banner
    n_test: Optional[int] = None
    practice_macro_f1: Optional[float] = None
    practice_micro_f1: Optional[float] = None
    purpose_macro_f1: Optional[float] = None
    purpose_micro_f1: Optional[float] = None
    practice_labels: List[LabelMetric]
    purpose_labels: List[LabelMetric]


class CaptionResults(BaseModel):
    banner: Banner
    judge: Optional[str] = None
    n_captions: int
    llm_mean: Optional[Dict[str, float]] = None
    baseline_mean: Optional[Dict[str, float]] = None
    pairwise: Optional[Dict[str, float]] = None


class ComplianceApp(BaseModel):
    package: str
    display_name: str
    facts: int
    surfaced: int
    completeness: float
    gdpr_reqs: int
    ccpa_reqs: int


class ComplianceResults(BaseModel):
    overall_completeness: Optional[float] = None
    per_app: List[ComplianceApp]


class ExperimentsStatus(BaseModel):
    available: bool
    logged_runs: int
    note: str


# ---- docs ----

class DocMeta(BaseModel):
    slug: str
    title: str
    file: str


class DocContent(BaseModel):
    slug: str
    title: str
    markdown: str


# ---- pagination ----

class Page(BaseModel):
    total: int
    page: int
    page_size: int
    has_more: bool


class PrcsPage(Page):
    items: List[PrcsListItem]


class CaptionPage(Page):
    items: List[CaptionRow]


AppDetail.model_rebuild()
