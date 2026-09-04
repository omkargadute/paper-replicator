"""Host-side out-of-band execution watchdog timer and process supervisor."""

import subprocess
import threading
import time
from typing import Optional, Tuple
from paperrep.schemas.execution import ExecutionStatus, ResourceTelemetry


class ExecutionWatchdog:
    """Monitors process execution on the host and enforces hard timeouts via SIGKILL.
    
    This lives entirely out-of-band so the sandboxed code cannot bypass or alter timeouts.
    """

    def __init__(self, timeout_seconds: int = 1800) -> None:
        self.timeout_seconds = timeout_seconds
        self._timed_out = False

    def run_command_with_supervision(
        self,
        command_args: list[str],
        cwd: Optional[str] = None,
    ) -> Tuple[int, str, str, ResourceTelemetry, ExecutionStatus]:
        """Executes a command with external watchdog enforcement.
        
        Returns:
            Tuple of (exit_code, stdout_str, stderr_str, telemetry, status)
        """
        start_time = time.time()
        self._timed_out = False

        process = subprocess.Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd,
        )

        def _kill_on_timeout():
            self._timed_out = True
            process.kill()

        timer = threading.Timer(self.timeout_seconds, _kill_on_timeout)
        timer.start()

        try:
            stdout, stderr = process.communicate()
            exit_code = process.returncode
        finally:
            timer.cancel()

        elapsed_time = time.time() - start_time

        telemetry = ResourceTelemetry(
            peak_memory_mb=0.0,
            wall_clock_time_sec=round(elapsed_time, 2),
            cpu_percent_avg=0.0,
        )

        if self._timed_out:
            return -9, stdout, stderr + f"\n[WATCHDOG] Terminated: Exceeded hard timeout of {self.timeout_seconds}s.", telemetry, ExecutionStatus.TIMEOUT

        status = ExecutionStatus.COMPLETED if exit_code == 0 else ExecutionStatus.FAILED
        return exit_code, stdout, stderr, telemetry, status
