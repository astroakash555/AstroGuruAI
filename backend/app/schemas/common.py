"""Shared Pydantic schemas."""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseSchema):
    """Health check response payload."""

    status: str
    app_name: str
    environment: str
