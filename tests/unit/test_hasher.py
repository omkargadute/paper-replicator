"""Unit tests for cryptographic SHA-256 provenance hashing."""

from pathlib import Path
import pytest
from paperrep.provenance.hasher import hash_bytes, hash_dict, hash_file, hash_string


def test_hash_string_deterministic():
    text = "PaperReplicator Scientific Provenance"
    digest1 = hash_string(text)
    digest2 = hash_string(text)
    assert digest1 == digest2
    assert len(digest1) == 64


def test_hash_dict_key_order_independence():
    dict1 = {"model": "ResNet", "seed": 42, "dataset": "CIFAR-10"}
    dict2 = {"dataset": "CIFAR-10", "model": "ResNet", "seed": 42}
    assert hash_dict(dict1) == hash_dict(dict2)


def test_hash_file_content(tmp_path: Path):
    test_file = tmp_path / "test_artifact.txt"
    test_file.write_text("Hello scientific reproducibility!", encoding="utf-8")
    digest = hash_file(test_file)
    assert len(digest) == 64
    assert digest == hash_string("Hello scientific reproducibility!")
