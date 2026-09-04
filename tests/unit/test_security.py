"""Unit tests for sandbox security boundaries and path sanitization."""

from pathlib import Path
import pytest
from paperrep.sandbox.security import SecurityError, sanitize_mount_path, validate_command_safety


def test_sanitize_mount_path_valid(tmp_path: Path):
    safe_sub = tmp_path / "workspace" / "runs"
    safe_sub.mkdir(parents=True)
    sanitized = sanitize_mount_path(str(safe_sub), str(tmp_path))
    assert sanitized == safe_sub.resolve()


def test_sanitize_mount_path_traversal_blocked(tmp_path: Path):
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    
    forbidden_dir = tmp_path / "forbidden"
    forbidden_dir.mkdir()

    with pytest.raises(SecurityError, match="escapes allowed base directory"):
        sanitize_mount_path(str(forbidden_dir), str(allowed_dir))


def test_validate_command_safety_fork_bomb():
    with pytest.raises(SecurityError, match="Disallowed command token detected"):
        validate_command_safety(":(){ :|:& };:")


def test_validate_command_safety_valid():
    validate_command_safety("python -m pytest tests/unit")
