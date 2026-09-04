"""Experiment specification contracts between the reasoning and execution layers."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class DatasetSpec(BaseModel):
    """Specification of required dataset and ingestion method."""
    name: str = Field(..., description="Dataset name")
    source_type: str = Field(..., description="'huggingface', 'url', 'torchvision', 'local'")
    source_uri: str = Field(..., description="Download URI or Hugging Face dataset identifier")
    split: str = Field("test", description="Target split")
    expected_sample_count: Optional[int] = Field(None, description="Expected number of samples in split")
    checksum_sha256: Optional[str] = Field(None, description="Expected SHA-256 checksum of data archive")


class HardwareProfile(BaseModel):
    """Execution hardware requirements and sandbox constraints."""
    gpu_required: bool = Field(False, description="Whether execution requires GPU")
    min_vram_gb: float = Field(0.0, description="Minimum GPU VRAM required")
    cpu_cores: int = Field(4, description="Number of CPU cores allocated")
    memory_limit: str = Field("8g", description="Memory limit string for container (e.g. '8g')")
    timeout_seconds: int = Field(1800, description="Hard timeout in seconds (default 30 mins)")


class ExperimentPlan(BaseModel):
    """Immutable contract governing an experiment execution."""
    experiment_id: str = Field(..., description="Unique experiment ID, e.g. 'EXP_001'")
    target_claim_id: str = Field(..., description="Target claim ID being verified")
    
    # Asset Specifications
    repo_url: Optional[str] = Field(None, description="Git repository URL if discovered")
    repo_commit: Optional[str] = Field(None, description="Pinned commit SHA")
    dataset: DatasetSpec = Field(..., description="Resolved dataset specification")
    
    # Execution Specifications
    entry_point_command: str = Field(..., description="Command to run inside sandbox, e.g. 'python eval.py'")
    hyperparameters: Dict[str, Any] = Field(default_factory=dict, description="Injected hyperparameters")
    seeds: List[int] = Field(default_factory=lambda: [42], description="Deterministic seeds to evaluate")
    hardware: HardwareProfile = Field(default_factory=HardwareProfile, description="Sandbox hardware limits")
    
    # Output Contract
    expected_metrics_output_path: str = Field(
        "/workspace/output/reproduce_metrics.json",
        description="Path where the harness must write final metrics"
    )
