"""Unit tests for NumericComparator tolerance classification and metric parsing."""

import pytest
from paperrep.comparator.numeric_comparator import NumericComparator
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry
from paperrep.schemas.verdict import VerdictStatus


@pytest.fixture
def sample_claim():
    return ClaimSpec(
        claim_id="CLM_TEST",
        statement="Method achieves 90.0% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=90.0,
        dataset_name="TestDataset",
        model_name="TestModel",
        citation=CitationCoordinate(page_number=1),
    )


def test_exact_replication_within_strict_tolerance(sample_claim):
    comparator = NumericComparator(default_strict_tolerance=0.5, default_loose_tolerance=2.0)
    run = ExecutionRun(
        run_id="RUN_1",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={"accuracy": 90.3},
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )
    verdict = comparator.evaluate(sample_claim, run)
    assert verdict.verdict_status == VerdictStatus.EXACT_REPLICATION
    assert verdict.within_tolerance is True
    assert verdict.absolute_delta == 0.3


def test_partial_replication_within_loose_tolerance(sample_claim):
    comparator = NumericComparator(default_strict_tolerance=0.5, default_loose_tolerance=2.0)
    run = ExecutionRun(
        run_id="RUN_2",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={"accuracy": 91.2},
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )
    verdict = comparator.evaluate(sample_claim, run)
    assert verdict.verdict_status == VerdictStatus.PARTIAL_REPLICATION
    assert verdict.within_tolerance is True
    assert verdict.absolute_delta == 1.2


def test_discrepancy_exceeding_tolerance(sample_claim):
    comparator = NumericComparator(default_strict_tolerance=0.5, default_loose_tolerance=2.0)
    run = ExecutionRun(
        run_id="RUN_3",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={"accuracy": 85.0},
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )
    verdict = comparator.evaluate(sample_claim, run)
    assert verdict.verdict_status == VerdictStatus.DISCREPANT
    assert verdict.within_tolerance is False
    assert verdict.absolute_delta == 5.0


def test_scale_normalization_decimal_to_percent(sample_claim):
    comparator = NumericComparator(default_strict_tolerance=0.5, default_loose_tolerance=2.0)
    # Model outputs decimal 0.901 instead of 90.1%
    run = ExecutionRun(
        run_id="RUN_4",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={"acc": 0.901},
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )
    verdict = comparator.evaluate(sample_claim, run)
    assert verdict.verdict_status == VerdictStatus.EXACT_REPLICATION
    assert verdict.reproduced_value == 90.1


def test_execution_failure_handling(sample_claim):
    comparator = NumericComparator()
    run = ExecutionRun(
        run_id="RUN_5",
        experiment_id="EXP_1",
        status=ExecutionStatus.FAILED,
        exit_code=1,
        raw_metrics={},
        telemetry=ResourceTelemetry(wall_clock_time_sec=5.0),
    )
    verdict = comparator.evaluate(sample_claim, run)
    assert verdict.verdict_status == VerdictStatus.EXECUTION_FAILED
    assert verdict.within_tolerance is False
    assert verdict.reproduced_value is None
