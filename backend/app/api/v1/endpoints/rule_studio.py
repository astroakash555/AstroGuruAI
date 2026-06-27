"""Expert Rule Authoring Studio API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.app.core.config import Settings, get_settings
from backend.app.schemas.rule_studio import (
    ConflictListResponse,
    RuleDetailResponse,
    RuleListResponse,
    RuleMutationResponse,
    SandboxTestResponse,
    StudioReportResponse,
)
from backend.app.services.rule_studio_service import RuleStudioService
from rule_studio.serializers.schemas import RuleCreateSchema, RuleUpdateSchema, SandboxTestRequestSchema, WorkflowActionSchema

router = APIRouter(prefix="/rule-studio", tags=["rule-studio"])


def get_rule_studio_service(settings: Settings = Depends(get_settings)) -> RuleStudioService:
    return RuleStudioService(data_root=settings.rule_studio_data_path)


@router.get("/manifest", summary="Rule studio manifest")
def get_manifest(service: RuleStudioService = Depends(get_rule_studio_service)) -> dict:
    return service.manifest()


@router.get("/report", response_model=StudioReportResponse, summary="Studio summary report")
def get_studio_report(service: RuleStudioService = Depends(get_rule_studio_service)) -> dict:
    return service.studio_report()


@router.get("/rules", response_model=RuleListResponse, summary="List expert rules")
def list_rules(
    system: str | None = Query(default=None),
    status: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return service.list_rules(system=system, status=status, is_active=is_active)


@router.get("/rules/{rule_id}", response_model=RuleDetailResponse, summary="Get expert rule")
def get_rule(rule_id: str, service: RuleStudioService = Depends(get_rule_studio_service)) -> dict:
    try:
        return service.get_rule(rule_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post(
    "/rules",
    response_model=RuleMutationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create expert rule",
)
def create_rule(
    payload: RuleCreateSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    result = service.create_rule(payload.model_dump(mode="json"))
    if not result.get("created"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=result)
    return result


@router.patch("/rules/{rule_id}", response_model=RuleMutationResponse, summary="Update expert rule")
def update_rule(
    rule_id: str,
    payload: RuleUpdateSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    result = service.update_rule(rule_id, payload.model_dump(mode="json", exclude_none=True))
    if not result.get("updated"):
        status_code = status.HTTP_404_NOT_FOUND if "not found" in str(result.get("error", "")).lower() else status.HTTP_422_UNPROCESSABLE_CONTENT
        raise HTTPException(status_code=status_code, detail=result)
    return result


@router.post("/rules/{rule_id}/submit", response_model=RuleMutationResponse, summary="Submit rule for review")
def submit_rule(
    rule_id: str,
    payload: WorkflowActionSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return _workflow_response(service.submit_for_review(rule_id, actor=payload.actor, notes=payload.notes))


@router.post("/rules/{rule_id}/approve", response_model=RuleMutationResponse, summary="Approve rule")
def approve_rule(
    rule_id: str,
    payload: WorkflowActionSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return _workflow_response(service.approve(rule_id, actor=payload.actor, notes=payload.notes))


@router.post("/rules/{rule_id}/reject", response_model=RuleMutationResponse, summary="Reject rule")
def reject_rule(
    rule_id: str,
    payload: WorkflowActionSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return _workflow_response(service.reject(rule_id, actor=payload.actor, notes=payload.notes))


@router.post("/rules/{rule_id}/activate", response_model=RuleMutationResponse, summary="Activate rule")
def activate_rule(
    rule_id: str,
    payload: WorkflowActionSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return _workflow_response(service.activate(rule_id, actor=payload.actor, notes=payload.notes))


@router.post("/rules/{rule_id}/deactivate", response_model=RuleMutationResponse, summary="Deactivate rule")
def deactivate_rule(
    rule_id: str,
    payload: WorkflowActionSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    return _workflow_response(service.deactivate(rule_id, actor=payload.actor, notes=payload.notes))


@router.get("/conflicts", response_model=ConflictListResponse, summary="Detect rule conflicts")
def list_conflicts(service: RuleStudioService = Depends(get_rule_studio_service)) -> dict:
    return service.detect_conflicts()


@router.post("/rules/{rule_id}/sandbox", response_model=SandboxTestResponse, summary="Test rule in sandbox")
def sandbox_test(
    rule_id: str,
    payload: SandboxTestRequestSchema,
    service: RuleStudioService = Depends(get_rule_studio_service),
) -> dict:
    try:
        return service.sandbox_test(rule_id, payload.sample_context)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


def _workflow_response(result: dict) -> dict:
    if not result.get("success"):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=result)
    return result
