"""Domain enumerations for astrology platform models."""

import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


class ChartSystem(str, enum.Enum):
    VEDIC = "vedic"
    WESTERN = "western"


class Ayanamsa(str, enum.Enum):
    LAHIRI = "lahiri"
    RAMAN = "raman"
    KP = "kp"
    KRISHNAMURTI = "krishnamurti"
    YUKTESHWAR = "yukteshwar"


class HouseSystem(str, enum.Enum):
    PLACIDUS = "placidus"
    WHOLE_SIGN = "whole_sign"
    EQUAL = "equal"
    SRIPATHI = "sripathi"
    KP = "kp"


class DashaSystem(str, enum.Enum):
    VIMSHOTTARI = "vimshottari"
    YOGINI = "yogini"
    ASHTOTTARI = "ashtottari"
    CHAR = "char"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class RemedyType(str, enum.Enum):
    MANTRA = "mantra"
    GEMSTONE = "gemstone"
    RITUAL = "ritual"
    CHARITY = "charity"
    FASTING = "fasting"
    YANTRA = "yantra"
    COLOR_THERAPY = "color_therapy"
    LIFESTYLE = "lifestyle"
    OTHER = "other"


class RemedyStatus(str, enum.Enum):
    PRESCRIBED = "prescribed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISCONTINUED = "discontinued"


class RemedySourceType(str, enum.Enum):
    DASHA = "dasha"
    TRANSIT = "transit"
    LAL_KITAB = "lal_kitab"
    KP = "kp"
    KUNDALI = "kundali"
    AI = "ai"
    MANUAL = "manual"


class PDFReportType(str, enum.Enum):
    KUNDALI = "kundali"
    DASHA = "dasha"
    TRANSIT = "transit"
    LAL_KITAB = "lal_kitab"
    KP = "kp"
    REMEDY = "remedy"
    COMBINED = "combined"
    CUSTOM = "custom"


class PDFStorageBackend(str, enum.Enum):
    LOCAL = "local"
    S3 = "s3"
    GCS = "gcs"


class PDFGenerationStatus(str, enum.Enum):
    QUEUED = "queued"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class QueryType(str, enum.Enum):
    GENERAL = "general"
    KUNDALI = "kundali"
    DASHA = "dasha"
    TRANSIT = "transit"
    LAL_KITAB = "lal_kitab"
    KP = "kp"
    REMEDY = "remedy"
    COMPATIBILITY = "compatibility"


class QueryStatus(str, enum.Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    ANSWERED = "answered"
    FAILED = "failed"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class AuthTokenType(str, enum.Enum):
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"


class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"


class OrderStatus(str, enum.Enum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUNDED = "refunded"


class UsageMetric(str, enum.Enum):
    REPORTS = "reports"
    CHAT_MESSAGES = "chat_messages"
    CLIENTS = "clients"


class RelationshipType(str, enum.Enum):
    SELF = "self"
    SPOUSE = "spouse"
    CHILD = "child"
    PARENT = "parent"
    SIBLING = "sibling"
    FRIEND = "friend"
    OTHER = "other"
