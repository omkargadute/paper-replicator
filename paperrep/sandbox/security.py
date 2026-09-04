"""Security sanitization and path traversal prevention for sandbox orchestration."""

from pathlib import Path
from typing import List


class SecurityError(Exception):
    """Raised when an operation violates sandbox security policies."""
    pass


def sanitize_mount_path(host_path: str, allowed_base_dir: str) -> Path:
    """Ensures that a volume mount path is strictly inside an allowed directory.
    
    Prevents directory traversal attacks (e.g. attempting to mount /etc or C:\\Windows).
    """
    base = Path(allowed_base_dir).resolve()
    target = Path(host_path).resolve()
    
    try:
        target.relative_to(base)
    except ValueError:
        raise SecurityError(
            f"Security Violation: Target path '{target}' escapes allowed base directory '{base}'"
        )
    
    return target


def validate_command_safety(command: str) -> None:
    """Validates that command does not contain destructive host commands or fork bombs."""
    forbidden_tokens = [
        ":(){ :|:& };:", # bash fork bomb
        "rm -rf /",
        "mkfs",
        "dd if=/dev/zero",
        "> /dev/sda",
    ]
    
    for token in forbidden_tokens:
        if token in command:
            raise SecurityError(f"Security Violation: Disallowed command token detected: '{token}'")
