"""Cryptographic SHA-256 hashing utilities for strict scientific provenance."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Union


def hash_bytes(data: bytes) -> str:
    """Computes SHA-256 hexadecimal digest for raw bytes."""
    return hashlib.sha256(data).hexdigest()


def hash_string(text: str) -> str:
    """Computes SHA-256 hexadecimal digest for a UTF-8 string."""
    return hash_bytes(text.encode("utf-8"))


def hash_dict(data: Dict[str, Any]) -> str:
    """Computes deterministic SHA-256 digest for a dictionary by sorting keys."""
    normalized_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hash_string(normalized_json)


def hash_file(file_path: Union[str, Path], chunk_size_bytes: int = 65536) -> str:
    """Computes SHA-256 hexadecimal digest for a file on disk."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found for cryptographic hashing: {file_path}")
    
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size_bytes):
            sha256.update(chunk)
    return sha256.hexdigest()
