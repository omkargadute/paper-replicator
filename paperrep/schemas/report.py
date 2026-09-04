"""Reproducibility report schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from paperrep.schemas.paper import PaperMetadata
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.execution import ExecutionRun
from paperrep.schemas.verdict import EvaluationVerdict


class ArtifactProvenance(BaseModel):
    """Cryptographic audit trail for all assets involved in replication."""
    pdf_sha256: str = Field(...)
    git_repo_url: Optional[str] = Field(None)
    git_commit_sha: Optional[str] = Field(None)
    dataset_source_uri: str = Field(...)
    dataset_checksum_sha256: Optional[str] = Field(None)
    docker_image_digest: str = Field(...)
    harness_script_sha256: str = Field(...)


class ReproducibilityReport(BaseModel):
    """Final auditable reproducibility report document."""
    report_id: str = Field(...)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    paper_metadata: PaperMetadata = Field(...)
    evaluated_claim: ClaimSpec = Field(...)
    execution_run: ExecutionRun = Field(...)
    verdict: EvaluationVerdict = Field(...)
    provenance: ArtifactProvenance = Field(...)
    inferred_parameters: Dict[str, str] = Field(
        default_factory=dict,
        description="Parameters not disclosed in paper that had to be inferred"
    )
    executive_summary: str = Field(...)
