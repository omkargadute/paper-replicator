"""Execution run telemetry and outcome schemas."""

from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ExecutionStatus(str, Enum):
    """Lifecycle status of an execution run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    OOM = "out_of_memory"
    FAILED = "failed"


class ResourceTelemetry(BaseModel):
    """Runtime resource utilization captured by watchdog."""
    peak_memory_mb: float = Field(0.0, description="Peak RAM usage in megabytes")
    peak_gpu_memory_mb: Optional[float] = Field(None, description="Peak VRAM usage in megabytes")
    wall_clock_time_sec: float = Field(..., description="Elapsed wall-clock execution time")
    cpu_percent_avg: float = Field(0.0, description="Average CPU utilization percentage")


class ExecutionRun(BaseModel):
    """Record of a single sandboxed experiment execution."""
    run_id: str = Field(..., description="Unique run identifier, e.g. 'RUN_001'")
    experiment_id: str = Field(..., description="Associated experiment plan ID")
    seed: int = Field(42, description="Random seed used for this run")
    status: ExecutionStatus = Field(..., description="Final execution status")
    exit_code: int = Field(..., description="Process exit code (0 for success)")
    
    # Logs & Artifacts
    stdout_log: str = Field("", description="Standard output log trace")
    stderr_log: str = Field("", description="Standard error log trace")
    raw_metrics: Dict[str, float] = Field(default_factory=dict, description="Parsed reproduce_metrics.json contents")
    
    # Telemetry
    telemetry: ResourceTelemetry = Field(..., description="Observed resource utilization")
    container_image_digest: str = Field("", description="Docker image digest for strict provenance")
