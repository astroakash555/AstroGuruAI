"""Client management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user, get_db, get_usage_service, require_usage, user_owner_id
from backend.app.billing.usage import UsageService
from backend.app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
    conflict_error,
    forbidden_error,
    not_found_error,
)
from backend.app.models.enums import UsageMetric
from backend.app.models.user import User
from backend.app.schemas.client import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate
from backend.app.services.client_service import ClientService

router = APIRouter(prefix="/clients", tags=["clients"])


def get_client_service(session: AsyncSession = Depends(get_db)) -> ClientService:
    """Provide a request-scoped client service."""
    return ClientService(session)


@router.post(
    "",
    response_model=ClientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create client",
)
async def create_client(
    payload: ClientCreate,
    current_user: User = Depends(require_usage(UsageMetric.CLIENTS)),
    service: ClientService = Depends(get_client_service),
    usage_service: UsageService = Depends(get_usage_service),
) -> ClientResponse:
    """Create a new client with validated birth details."""
    try:
        response = await service.create_client(payload, owner_id=current_user.id)
        await usage_service.consume(current_user.id, UsageMetric.CLIENTS)
        return response
    except ConflictError as exc:
        raise conflict_error(exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.message,
        ) from exc


@router.get(
    "",
    response_model=ClientListResponse,
    summary="List clients",
)
async def list_clients(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    include_inactive: bool = Query(default=False),
    search: str | None = Query(default=None, max_length=255),
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientListResponse:
    """List clients with pagination and optional name search."""
    return await service.list_clients(
        owner_id=user_owner_id(current_user),
        page=page,
        page_size=page_size,
        include_inactive=include_inactive,
        search=search,
    )


@router.get(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Get client",
)
async def get_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """Retrieve a single client by UUID."""
    try:
        return await service.get_client(client_id, owner_id=user_owner_id(current_user))
    except NotFoundError:
        raise not_found_error("Client", str(client_id)) from None
    except ForbiddenError as exc:
        raise forbidden_error(exc.message) from exc


@router.patch(
    "/{client_id}",
    response_model=ClientResponse,
    summary="Update client",
)
async def update_client(
    client_id: uuid.UUID,
    payload: ClientUpdate,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> ClientResponse:
    """Partially update client and primary birth profile fields."""
    if not payload.model_dump(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="At least one field must be provided for update.",
        )

    try:
        return await service.update_client(
            client_id,
            payload,
            owner_id=user_owner_id(current_user),
        )
    except NotFoundError:
        raise not_found_error("Client", str(client_id)) from None
    except ConflictError as exc:
        raise conflict_error(exc.message) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.message,
        ) from exc
    except ForbiddenError as exc:
        raise forbidden_error(exc.message) from exc


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete client",
)
async def delete_client(
    client_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ClientService = Depends(get_client_service),
) -> None:
    """Soft-delete a client (sets is_active=false)."""
    try:
        await service.delete_client(client_id, owner_id=user_owner_id(current_user))
    except NotFoundError:
        raise not_found_error("Client", str(client_id)) from None
    except ForbiddenError as exc:
        raise forbidden_error(exc.message) from exc
