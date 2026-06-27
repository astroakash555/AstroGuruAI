"""Case Learning Engine API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.case_learning import (
    CaseListResponse,
    CaseRecordResponse,
    LearningReportResponse,
)
from backend.app.services.case_learning_service import CaseLearningService
from case_learning.serializers.schemas import (
    ConsultationCaseCreateSchema,
    ConsultationFromReportSchema,
    FollowUpCreateSchema,
)

router = APIRouter(prefix="/case-learning", tags=["case-learning"])


def get_case_learning_service(settings: Settings = Depends(get_settings)) -> CaseLearningService:
    return CaseLearningService(data_root=settings.case_learning_data_path)


@router.get("/manifest", summary="Case learning manifest")
def get_manifest(service: CaseLearningService = Depends(get_case_learning_service)) -> dict:
    return service.manifest()


@router.get("/report", response_model=LearningReportResponse, summary="Generate learning report")
def get_learning_report(
    category: str | None = Query(default=None),
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    return service.learning_report(category=category)


@router.get("/metrics", summary="Learning metrics")
def get_metrics(
    category: str | None = Query(default=None),
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    return service.metrics(category=category)


@router.get("/suggestions", summary="Rule improvement suggestions")
def get_suggestions(
    category: str | None = Query(default=None),
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    return service.suggestions(category=category)


@router.get("/feedback-loops", summary="Feedback loops")
def get_feedback_loops(
    category: str | None = Query(default=None),
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    return service.feedback_loops(category=category)


@router.get("/cases", response_model=CaseListResponse, summary="List consultation cases")
def list_cases(
    category: str | None = Query(default=None),
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    return service.list_cases(category=category)


@router.get("/cases/{case_id}", summary="Get consultation case")
def get_case(case_id: str, service: CaseLearningService = Depends(get_case_learning_service)) -> dict:
    try:
        return service.get_case(case_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/cases",
    response_model=CaseRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record consultation case",
)
def record_case(
    payload: ConsultationCaseCreateSchema,
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    result = service.record_consultation(payload.model_dump(mode="json"))
    if not result.get("recorded"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=result)
    return result


@router.post(
    "/cases/from-report",
    response_model=CaseRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record case from unified report",
)
def record_from_report(
    payload: ConsultationFromReportSchema,
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    result = service.record_from_report(payload.model_dump(mode="json"))
    if not result.get("recorded"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=result)
    return result


@router.post(
    "/cases/{case_id}/follow-up",
    response_model=CaseRecordResponse,
    summary="Add follow-up result",
)
def add_follow_up(
    case_id: str,
    payload: FollowUpCreateSchema,
    service: CaseLearningService = Depends(get_case_learning_service),
) -> dict:
    result = service.add_follow_up(case_id, payload.model_dump(mode="json"))
    if not result.get("updated"):
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(result.get("error", "")).lower() else status.HTTP_422_UNPROCESSABLE_CONTENT
        raise HTTPException(status_code=status_code, detail=result)
    return result
