"""Client management business logic."""

from __future__ import annotations

import math
import uuid
from datetime import date, datetime, time
from decimal import Decimal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from backend.app.models.birth_detail import BirthDetail
from backend.app.models.client import Client
from backend.app.models.enums import RelationshipType
from backend.app.schemas.client import ClientCreate, ClientListResponse, ClientResponse, ClientUpdate


class ClientService:
    """Service layer for client CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_client(self, payload: ClientCreate, *, owner_id: uuid.UUID) -> ClientResponse:
        """Create a client with a primary birth profile."""
        birth_datetime = self._combine_birth_datetime(
            payload.date_of_birth,
            payload.birth_time,
            payload.timezone,
        )

        client = Client(
            owner_id=owner_id,
            full_name=payload.name,
            gender=payload.gender,
            email=str(payload.email) if payload.email else None,
            phone=payload.phone,
            preferred_language=payload.preferred_language,
            timezone=payload.timezone,
            notes=payload.notes,
            is_active=True,
        )
        birth_detail = BirthDetail(
            client=client,
            person_name=payload.name,
            relationship_to_client=RelationshipType.SELF,
            birth_datetime=birth_datetime,
            birth_place_name=payload.birth_place,
            latitude=payload.latitude if payload.latitude is not None else Decimal("0"),
            longitude=payload.longitude if payload.longitude is not None else Decimal("0"),
            timezone=payload.timezone,
            is_primary=True,
        )

        self._session.add(client)
        self._session.add(birth_detail)

        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError(self._integrity_message(exc)) from exc

        await self._session.refresh(client, attribute_names=["birth_details"])
        return self._to_response(client)

    async def get_client(self, client_id: uuid.UUID, *, owner_id: uuid.UUID | None) -> ClientResponse:
        """Fetch a single client by ID."""
        client = await self._get_client_or_raise(client_id, owner_id=owner_id)
        return self._to_response(client)

    async def list_clients(
        self,
        *,
        owner_id: uuid.UUID | None,
        page: int = 1,
        page_size: int = 20,
        include_inactive: bool = False,
        search: str | None = None,
    ) -> ClientListResponse:
        """Return a paginated list of clients."""
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        filters = []
        if owner_id is not None:
            filters.append(Client.owner_id == owner_id)
        if not include_inactive:
            filters.append(Client.is_active.is_(True))
        if search:
            filters.append(Client.full_name.ilike(f"%{search.strip()}%"))

        count_stmt = select(func.count()).select_from(Client)
        if filters:
            count_stmt = count_stmt.where(*filters)
        total = int((await self._session.execute(count_stmt)).scalar_one())

        stmt = (
            select(Client)
            .options(selectinload(Client.birth_details))
            .order_by(Client.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        if filters:
            stmt = stmt.where(*filters)

        result = await self._session.execute(stmt)
        clients = result.scalars().unique().all()

        pages = math.ceil(total / page_size) if total else 0
        return ClientListResponse(
            items=[self._to_response(client) for client in clients],
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def update_client(
        self,
        client_id: uuid.UUID,
        payload: ClientUpdate,
        *,
        owner_id: uuid.UUID | None,
    ) -> ClientResponse:
        """Update client fields and primary birth profile."""
        client = await self._get_client_or_raise(client_id, owner_id=owner_id)
        update_data = payload.model_dump(exclude_unset=True)

        if "name" in update_data:
            client.full_name = update_data["name"]
        if "gender" in update_data:
            client.gender = update_data["gender"]
        if "email" in update_data:
            client.email = str(update_data["email"]) if update_data["email"] else None
        if "phone" in update_data:
            client.phone = update_data["phone"]
        if "preferred_language" in update_data:
            client.preferred_language = update_data["preferred_language"]
        if "timezone" in update_data:
            client.timezone = update_data["timezone"]
        if "notes" in update_data:
            client.notes = update_data["notes"]
        if "is_active" in update_data:
            client.is_active = update_data["is_active"]

        birth_fields = {
            "date_of_birth",
            "birth_time",
            "birth_place",
            "timezone",
            "latitude",
            "longitude",
        }
        if birth_fields.intersection(update_data):
            birth_detail = self._get_primary_birth_detail(client)
            if birth_detail is None:
                raise NotFoundError("Primary birth profile not found for client.")

            timezone_name = update_data.get("timezone", birth_detail.timezone)
            date_of_birth = update_data.get(
                "date_of_birth",
                birth_detail.birth_datetime.astimezone(ZoneInfo(birth_detail.timezone)).date(),
            )
            birth_time = update_data.get(
                "birth_time",
                birth_detail.birth_datetime.astimezone(ZoneInfo(birth_detail.timezone)).time(),
            )

            birth_detail.birth_datetime = self._combine_birth_datetime(
                date_of_birth,
                birth_time,
                timezone_name,
            )
            if "birth_place" in update_data:
                birth_detail.birth_place_name = update_data["birth_place"]
            if "timezone" in update_data:
                birth_detail.timezone = update_data["timezone"]
            if "latitude" in update_data and update_data["latitude"] is not None:
                birth_detail.latitude = update_data["latitude"]
            if "longitude" in update_data and update_data["longitude"] is not None:
                birth_detail.longitude = update_data["longitude"]
            if "name" in update_data:
                birth_detail.person_name = update_data["name"]

        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise ConflictError(self._integrity_message(exc)) from exc

        await self._session.refresh(client, attribute_names=["birth_details"])
        return self._to_response(client)

    async def delete_client(self, client_id: uuid.UUID, *, owner_id: uuid.UUID | None) -> None:
        """Soft-delete a client by marking them inactive."""
        client = await self._get_client_or_raise(client_id, owner_id=owner_id)
        client.is_active = False
        await self._session.commit()

    async def ensure_client_access(self, client_id: uuid.UUID, *, owner_id: uuid.UUID | None) -> Client:
        """Verify the caller can access a client record."""
        return await self._get_client_or_raise(client_id, owner_id=owner_id)

    async def _get_client_or_raise(
        self,
        client_id: uuid.UUID,
        *,
        owner_id: uuid.UUID | None,
    ) -> Client:
        stmt = (
            select(Client)
            .options(selectinload(Client.birth_details))
            .where(Client.id == client_id)
        )
        if owner_id is not None:
            stmt = stmt.where(Client.owner_id == owner_id)
        result = await self._session.execute(stmt)
        client = result.scalar_one_or_none()
        if client is None:
            if owner_id is not None:
                existing = await self._session.execute(select(Client.id).where(Client.id == client_id))
                if existing.scalar_one_or_none() is not None:
                    raise ForbiddenError("You do not have permission to access this client.")
            raise NotFoundError(f"Client with id '{client_id}' was not found.")
        return client

    @staticmethod
    def _get_primary_birth_detail(client: Client) -> BirthDetail | None:
        for birth_detail in client.birth_details:
            if birth_detail.is_primary:
                return birth_detail
        return client.birth_details[0] if client.birth_details else None

    @staticmethod
    def _combine_birth_datetime(
        date_of_birth: date,
        birth_time: time,
        timezone_name: str,
    ) -> datetime:
        try:
            tz = ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise ConflictError(f"Invalid timezone: '{timezone_name}'.") from exc

        localized = datetime.combine(date_of_birth, birth_time, tzinfo=tz)
        return localized

    @staticmethod
    def _integrity_message(exc: IntegrityError) -> str:
        message = str(exc.orig).lower() if exc.orig else str(exc).lower()
        if "email" in message:
            return "A client with this email already exists."
        if "phone" in message:
            return "A client with this phone number already exists."
        if "uq_birth_details_client_person_datetime" in message:
            return "A birth profile with the same name and datetime already exists."
        return "A database constraint was violated."

    @classmethod
    def _to_response(cls, client: Client) -> ClientResponse:
        birth_detail = cls._get_primary_birth_detail(client)
        birth_response = None
        if birth_detail is not None:
            localized = birth_detail.birth_datetime.astimezone(ZoneInfo(birth_detail.timezone))
            birth_response = {
                "id": birth_detail.id,
                "date_of_birth": localized.date(),
                "birth_time": localized.time(),
                "birth_place": birth_detail.birth_place_name,
                "birth_datetime": birth_detail.birth_datetime,
                "timezone": birth_detail.timezone,
                "latitude": birth_detail.latitude,
                "longitude": birth_detail.longitude,
                "is_primary": birth_detail.is_primary,
            }

        return ClientResponse(
            id=client.id,
            name=client.full_name,
            gender=client.gender,
            email=client.email,
            phone=client.phone,
            preferred_language=client.preferred_language,
            timezone=client.timezone,
            notes=client.notes,
            is_active=client.is_active,
            birth_detail=birth_response,
            created_at=client.created_at,
            updated_at=client.updated_at,
        )
