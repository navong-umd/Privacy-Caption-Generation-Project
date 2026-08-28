"""API routes. Everything is GET and read-only.

Validation errors return 422 automatically; missing resources return 404 with a
clear message; unexpected failures return a clean 500 without a stack trace.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from webapi import loader, services
from webapi.models import (
    AppDetail, AppSummary, CaptionPage, CaptionResults, ClassificationResults,
    ComplianceResults, DocContent, DocMeta, ExperimentsStatus, Overview,
    PrcsDetail, PrcsPage,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "data_root": str(loader.DATA_ROOT), "n_prcs": len(loader.prcs_index())}


@router.get("/overview", response_model=Overview)
def overview() -> Overview:
    return Overview(**services.build_overview())


@router.get("/apps", response_model=list[AppSummary])
def list_apps() -> list[AppSummary]:
    out = []
    for pkg in loader.app_packages():
        s = services.app_summary(pkg)
        if s:
            out.append(AppSummary(**s))
    out.sort(key=lambda a: -a.n_prcs)
    return out


@router.get("/apps/{package}", response_model=AppDetail)
def app_detail(package: str) -> AppDetail:
    d = services.app_detail(package)
    if d is None:
        raise HTTPException(status_code=404, detail=f"No analysis found for app '{package}'.")
    return AppDetail(**d)


@router.get("/prcs", response_model=PrcsPage)
def list_prcs(
    app: Optional[str] = None,
    pi_category: Optional[str] = None,
    sink_type: Optional[str] = None,
    practice: Optional[str] = None,
    purpose: Optional[str] = None,
    label_source: Optional[str] = None,
    split: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
) -> PrcsPage:
    result = services.filter_prcs(
        app, pi_category, sink_type, practice, purpose, label_source, split, q, page, page_size
    )
    return PrcsPage(**result)


@router.get("/prcs/{prcs_id}", response_model=PrcsDetail)
def prcs_detail(prcs_id: str) -> PrcsDetail:
    d = services.prcs_detail(prcs_id)
    if d is None:
        raise HTTPException(status_code=404, detail=f"PRCS '{prcs_id}' not found.")
    return PrcsDetail(**d)


@router.get("/captions", response_model=CaptionPage)
def list_captions(
    app: Optional[str] = None,
    provider: str = Query("llm", pattern="^(llm|mock)$"),
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
) -> CaptionPage:
    return CaptionPage(**services.filter_captions(app, provider, q, page, page_size))


@router.get("/results/classification", response_model=ClassificationResults)
def results_classification() -> ClassificationResults:
    return ClassificationResults(**services.classification_results())


@router.get("/results/captions", response_model=CaptionResults)
def results_captions() -> CaptionResults:
    return CaptionResults(**services.caption_results())


@router.get("/results/compliance", response_model=ComplianceResults)
def results_compliance() -> ComplianceResults:
    return ComplianceResults(**services.compliance_results())


@router.get("/results/experiments", response_model=ExperimentsStatus)
def results_experiments() -> ExperimentsStatus:
    return ExperimentsStatus(**services.experiments_status())


@router.get("/docs", response_model=list[DocMeta])
def list_docs() -> list[DocMeta]:
    return [DocMeta(**d) for d in loader.research_docs()]


@router.get("/docs/{slug}", response_model=DocContent)
def get_doc(slug: str) -> DocContent:
    d = loader.research_doc(slug)
    if d is None:
        raise HTTPException(status_code=404, detail=f"Doc '{slug}' not found.")
    return DocContent(**d)
