"""PaperReplicator data contracts and schemas."""

from paperrep.schemas.paper import (
    PaperDocument,
    PaperMetadata,
    PaperSection,
    PaperTable,
    CitationCoordinate,
)
from paperrep.schemas.claim import (
    ClaimSpec,
    ClaimType,
    ClaimRegistry,
)
from paperrep.schemas.experiment import (
    ExperimentPlan,
    DatasetSpec,
    HardwareProfile,
)
from paperrep.schemas.execution import (
    ExecutionRun,
    ExecutionStatus,
    ResourceTelemetry,
)
from paperrep.schemas.verdict import (
    VerdictStatus,
    EvaluationVerdict,
    DiscrepancyHypothesis,
    DiscrepancyReport,
)
from paperrep.schemas.report import (
    ReproducibilityReport,
    ArtifactProvenance,
)

__all__ = [
    "PaperDocument",
    "PaperMetadata",
    "PaperSection",
    "PaperTable",
    "CitationCoordinate",
    "ClaimSpec",
    "ClaimType",
    "ClaimRegistry",
    "ExperimentPlan",
    "DatasetSpec",
    "HardwareProfile",
    "ExecutionRun",
    "ExecutionStatus",
    "ResourceTelemetry",
    "VerdictStatus",
    "EvaluationVerdict",
    "DiscrepancyHypothesis",
    "DiscrepancyReport",
    "ReproducibilityReport",
    "ArtifactProvenance",
]
