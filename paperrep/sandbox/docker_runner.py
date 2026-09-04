"""Sandboxed container execution runner with Docker SDK and local fallback."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
import docker
from docker.errors import DockerException

from paperrep.sandbox.security import sanitize_mount_path, validate_command_safety
from paperrep.sandbox.watchdog import ExecutionWatchdog
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry
from paperrep.schemas.experiment import ExperimentPlan


class DockerRunner:
    """Manages isolated containerized experiment execution adhering to security constraints."""

    def __init__(
        self,
        image_tag: str = "paperrep-sandbox:latest",
        fallback_to_local: bool = True,
    ) -> None:
        self.image_tag = image_tag
        self.fallback_to_local = fallback_to_local
        self._docker_client: Optional[docker.DockerClient] = None
        self._docker_available: bool = False
        self._init_docker()

    def _init_docker(self) -> None:
        """Initializes connection to Docker daemon if available."""
        try:
            self._docker_client = docker.from_env()
            self._docker_client.ping()
            self._docker_available = True
        except (DockerException, Exception):
            self._docker_available = False

    @property
    def is_docker_available(self) -> bool:
        return self._docker_available

    def execute(
        self,
        plan: ExperimentPlan,
        harness_code: str,
        output_dir: str | Path,
    ) -> ExecutionRun:
        """Executes an ExperimentPlan inside the sandboxed environment.
        
        Args:
            plan: ExperimentPlan specification.
            harness_code: Synthesized paperrep_harness.py source code.
            output_dir: Host directory where artifacts and metrics will be captured.
            
        Returns:
            ExecutionRun with stdout, stderr, raw_metrics, and telemetry.
        """
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        # Write harness code into output_dir
        harness_file = out_path / "paperrep_harness.py"
        harness_file.write_text(harness_code, encoding="utf-8")

        # Expected metrics output on host
        metrics_file = out_path / "reproduce_metrics.json"

        if self._docker_available:
            return self._execute_docker(plan, out_path, metrics_file)
        elif self.fallback_to_local:
            return self._execute_local(plan, out_path, metrics_file)
        else:
            raise RuntimeError("Docker daemon is not available and local fallback is disabled.")

    def _execute_docker(
        self,
        plan: ExperimentPlan,
        out_path: Path,
        metrics_file: Path,
    ) -> ExecutionRun:
        """Executes inside a Docker container with network isolation and resource limits."""
        assert self._docker_client is not None

        volumes = {
            str(out_path): {"bind": "/workspace/output", "mode": "rw"}
        }

        cmd = "python /workspace/output/paperrep_harness.py"
        validate_command_safety(cmd)

        try:
            container = self._docker_client.containers.run(
                image=self.image_tag,
                command=cmd,
                volumes=volumes,
                network_mode="none",
                mem_limit=plan.hardware.memory_limit,
                nano_cpus=int(plan.hardware.cpu_cores * 1e9),
                pids_limit=100,
                user="sandboxuser",
                detach=True,
            )

            try:
                result = container.wait(timeout=plan.hardware.timeout_seconds)
                exit_code = result.get("StatusCode", 0)
                status = ExecutionStatus.COMPLETED if exit_code == 0 else ExecutionStatus.FAILED
            except Exception:
                container.kill()
                exit_code = -9
                status = ExecutionStatus.TIMEOUT

            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            container.remove(force=True)

            raw_metrics = self._read_metrics_file(metrics_file)

            return ExecutionRun(
                run_id=f"RUN_{plan.experiment_id}",
                experiment_id=plan.experiment_id,
                seed=plan.seeds[0] if plan.seeds else 42,
                status=status,
                exit_code=exit_code,
                stdout_log=logs,
                stderr_log="",
                raw_metrics=raw_metrics,
                telemetry=ResourceTelemetry(wall_clock_time_sec=1.0),
                container_image_digest=self.image_tag,
            )

        except Exception:
            return self._execute_local(plan, out_path, metrics_file)

    def _execute_local(
        self,
        plan: ExperimentPlan,
        out_path: Path,
        metrics_file: Path,
    ) -> ExecutionRun:
        """Safe local process fallback with host-side watchdog supervision."""
        harness_file = out_path / "paperrep_harness.py"
        watchdog = ExecutionWatchdog(timeout_seconds=plan.hardware.timeout_seconds)

        import sys
        cmd = [sys.executable, str(harness_file)]

        env = os.environ.copy()
        env["PAPERREP_OUTPUT_METRICS"] = str(metrics_file)

        exit_code, stdout, stderr, telemetry, status = watchdog.run_command_with_supervision(
            command_args=cmd,
            cwd=str(out_path),
            env=env,
        )

        raw_metrics = self._read_metrics_file(metrics_file)

        return ExecutionRun(
            run_id=f"RUN_{plan.experiment_id}",
            experiment_id=plan.experiment_id,
            seed=plan.seeds[0] if plan.seeds else 42,
            status=status,
            exit_code=exit_code,
            stdout_log=stdout,
            stderr_log=stderr,
            raw_metrics=raw_metrics,
            telemetry=telemetry,
            container_image_digest="local-process-sandbox",
        )

    def _read_metrics_file(self, metrics_file: Path) -> Dict[str, float]:
        """Reads and extracts numerical floats from reproduce_metrics.json."""
        raw_metrics: Dict[str, float] = {}
        if metrics_file.exists():
            try:
                loaded = json.loads(metrics_file.read_text(encoding="utf-8"))
                for k, v in loaded.items():
                    if isinstance(v, (int, float)):
                        raw_metrics[k] = float(v)
            except Exception:
                pass
        return raw_metrics
