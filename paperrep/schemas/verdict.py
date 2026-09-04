"""Verdict schemas and discrepancy diagnostic models."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class VerdictStatus(str, Enum):
    """Rigorous 5-tier classification of replication outcome."""
    EXACT_REPLICATION = "EXACT_REPLICATION"            # Delta <= strict tolerance
    PARTIAL_REPLICATION = "PARTIAL_REPLICATION"        # Delta <= loose tolerance OR trend matches
    DISCREPANT = "DISCREPANT"                          # Clean run, but metric divergence > tolerance
    EXECUTION_FAILED = "EXECUTION_FAILED"              # Crashed, timed out, or OOM
    UNVERIFIABLE = "UNVERIFIABLE"                      # Missing assets, private dataset, or paywalled code


class DiscrepancyHypothesis(BaseModel):
    """An evidence-backed hypothesis explaining a numerical mismatch."""
    hypothesis_id: str = Field(..., description="Hypothesis identifier, e.g. 'HYP_001'")
    category: str = Field(
        ..., 
        description="Category: 'dataset_split_drift', 'preprocessing_mismatch', 'seed_variance', 'hyperparameter_shift', 'hardware_precision'"
    )
    explanation: str = Field(..., description="Detailed causal rationale")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in this hypothesis")
    supporting_evidence: List[str] = Field(default_factory=list, description="Concrete evidence points (log lines, diffs)")
    suggested_verification_test: Optional[str] = Field(None, description="Suggested test to confirm/refute hypothesis")


class DiscrepancyReport(BaseModel):
    """Complete diagnostic investigation of an experimental discrepancy."""
    claim_id: str = Field(...)
    published_value: float = Field(...)
    reproduced_value: float = Field(...)
    delta: float = Field(...)
    ranked_hypotheses: List[DiscrepancyHypothesis] = Field(default_factory=list)
    diagnostic_summary: str = Field(..., description="Executive diagnostic summary")


class EvaluationVerdict(BaseModel):
    """Complete evaluation verdict comparing reproduced results to published claims."""
    claim_id: str = Field(..., description="Target claim ID")
    verdict_status: VerdictStatus = Field(..., description="5-tier replication status")
    
    # Numerical Comparison
    metric_name: str = Field(...)
    published_value: float = Field(...)
    reproduced_value: Optional[float] = Field(None)
    absolute_delta: Optional[float] = Field(None)
    relative_error_percent: Optional[float] = Field(None)
    
    # Tolerance Bounds Applied
    strict_tolerance_applied: float = Field(...)
    loose_tolerance_applied: float = Field(...)
    within_tolerance: bool = Field(...)
    
    # Discrepancy Diagnosis (if status is DISCREPANT)
    diagnosis: Optional[DiscrepancyReport] = Field(None)
