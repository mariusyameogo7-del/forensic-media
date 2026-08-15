import enum


class AccountType(str, enum.Enum):
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    INSTITUTIONAL = "institutional"


class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ConclusionLevel(str, enum.Enum):
    NO_MAJOR_ALERT = "no_major_alert"
    REVIEW_RECOMMENDED = "review_recommended"
    IMPORTANT_ATTENTION = "important_attention"


class ProvenanceStatus(str, enum.Enum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    INCONSISTENT = "inconsistent"


class IntegrityStatus(str, enum.Enum):
    CLEAR = "clear"
    REVIEW = "review"
    MAJOR_ANOMALY = "major_anomaly"


class AIStatus(str, enum.Enum):
    INDETERMINATE = "indeterminate"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    DECLARED = "declared"


class ContextStatus(str, enum.Enum):
    COHERENT = "coherent"
    REVIEW = "review"
    POTENTIAL_DECONTEXTUALIZATION = "potential_decontextualization"


class EngineRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    NOT_APPLICABLE = "not_applicable"


class EngineCode(str, enum.Enum):
    C2PA = "c2pa"
    METADATA = "metadata"
    HASHES = "hashes"
    AI = "ai"
    WEB_CONTEXT = "web_context"
    FACT_CHECK = "fact_check"
    SYNTHESIS = "synthesis"


class StoredObjectType(str, enum.Enum):
    ORIGINAL = "original"
    PREVIEW = "preview"
    THUMBNAIL = "thumbnail"
    REPORT_PDF = "report_pdf"
    WORKING_COPY = "working_copy"


class EvidenceType(str, enum.Enum):
    TECHNICAL_PROOF = "technical_proof"
    DECLARED_INFO = "declared_info"
    EXTERNAL_MATCH = "external_match"
    ESTIMATION = "estimation"


class EvidenceSeverity(str, enum.Enum):
    INFO = "info"
    POSITIVE = "positive"
    WARNING = "warning"
    CRITICAL = "critical"


class WebMatchType(str, enum.Enum):
    EXACT = "exact"
    PARTIAL = "partial"
    SIMILAR = "similar"
    VISUALLY_SIMILAR = "visually_similar"
