"""Claim specification schemas for verifiable scientific assertions."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from paperrep.schemas.paper import CitationCoordinate


class ClaimType(str, Enum):
    """Categorization of claims extracted from papers."""
    VERIFIABLE_NUMERIC = "verifiable_numeric"  # Explicit number on a benchmark
    COMPARATIVE_ADVANTAGE = "comparative_advantage"  # "Method X beats Baseline Y by Z%"
    ABLATION_EFFECT = "ablation_effect"  # "Removing module A reduces metric by B"
    QUALITATIVE = "qualitative"  # Architectural observation (non-numeric)
    THEORETICAL = "theoretical"  # Mathematical proof/theorem (not empirically testable)


class ClaimSpec(BaseModel):
    """Formal specification of an experimentally verifiable empirical claim."""
    claim_id: str = Field(..., description="Unique claim identifier, e.g. 'CLM_001'")
    statement: str = Field(..., description="Exact claim text quoted or synthesized from paper")
    claim_type: ClaimType = Field(ClaimType.VERIFIABLE_NUMERIC, description="Type of scientific claim")
    
    # Target Metric Details
    metric_name: str = Field(..., description="Name of metric, e.g. 'Accuracy', 'BLEU', 'F1'")
    published_value: float = Field(..., description="Reported numerical value in paper")
    published_uncertainty: Optional[float] = Field(None, description="Reported error/std if stated (e.g. ±0.3)")
    is_percentage: bool = Field(True, description="Whether metric is a percentage (0-100) or decimal (0-1)")
    
    # Target Conditions
    dataset_name: str = Field(..., description="Target dataset name (e.g. 'CIFAR-10', 'SST-2')")
    dataset_split: str = Field("test", description="Data split (e.g. 'test', 'validation')")
    model_name: str = Field(..., description="Model architecture or method variant evaluated")
    
    # Provenance
    citation: CitationCoordinate = Field(..., description="Exact coordinate inside the paper")
    reproducibility_feasibility_score: float = Field(
        1.0, ge=0.0, le=1.0, 
        description="Feasibility score (0.0 = impossible without proprietary cluster, 1.0 = highly feasible)"
    )


class ClaimRegistry(BaseModel):
    """Collection of claims extracted from a single research paper."""
    paper_hash: str = Field(..., description="SHA-256 hash of paper")
    claims: List[ClaimSpec] = Field(default_factory=list, description="List of extracted claims")
