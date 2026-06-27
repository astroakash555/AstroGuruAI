"""SQLAlchemy model metadata tests."""

from backend.app.db.base import Base
from backend.app.models import (
    BirthDetail,
    Client,
    DashaReport,
    GeneratedPDF,
    KPReport,
    KundaliChart,
    LalKitabReport,
    Remedy,
    TransitReport,
    UserQuery,
)


def test_all_models_registered():
    """All domain models are registered on Base.metadata."""
    expected_tables = {
        "clients",
        "birth_details",
        "kundali_charts",
        "dasha_reports",
        "transit_reports",
        "lal_kitab_reports",
        "kp_reports",
        "remedies",
        "generated_pdfs",
        "user_queries",
    }
    assert expected_tables.issubset(Base.metadata.tables.keys())


def test_model_public_exports():
    """Public model registry exports all entities."""
    models = [
        Client,
        BirthDetail,
        KundaliChart,
        DashaReport,
        TransitReport,
        LalKitabReport,
        KPReport,
        Remedy,
        GeneratedPDF,
        UserQuery,
    ]
    assert len(models) == 10
    for model in models:
        assert hasattr(model, "id")
        assert hasattr(model, "created_at")
        assert hasattr(model, "updated_at")
