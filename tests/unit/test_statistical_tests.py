"""Unit tests for statistical aggregation and z-scores."""

import pytest
from paperrep.comparator.statistical_tests import StatisticalEvaluator


def test_aggregate_seeds_basic():
    values = [90.0, 91.0, 92.0]
    stats = StatisticalEvaluator.aggregate_seeds(values)
    assert stats["mean"] == 91.0
    assert stats["std"] == 1.0
    assert stats["min"] == 90.0
    assert stats["max"] == 92.0
    assert stats["n"] == 3


def test_aggregate_seeds_empty():
    stats = StatisticalEvaluator.aggregate_seeds([])
    assert stats["n"] == 0
    assert stats["mean"] == 0.0


def test_compute_z_score():
    z = StatisticalEvaluator.compute_z_score(observed_mean=91.4, published_value=90.0, observed_std=0.7)
    assert z == 2.0
