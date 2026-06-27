"""Custom SQLAlchemy column types for model definitions."""

import enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

E = TypeVar("E", bound=enum.Enum)


def enum_column(enum_class: type[E], name: str) -> SAEnum:
    """
    Create a VARCHAR-backed enum column compatible with PostgreSQL.

    Uses native_enum=False for simpler Alembic migrations and portable storage.
    """
    return SAEnum(
        enum_class,
        name=name,
        native_enum=False,
        values_callable=lambda members: [member.value for member in members],
    )
