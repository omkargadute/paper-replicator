"""Unit tests for diagnostic rules and forensic investigation."""

from paperrep.diagnosis.diagnostic_tree import DiagnosticTree
from paperrep.diagnosis.investigator import ForensicInvestigator
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry


def test_diagnostic_tree_detects_seed_variance():
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Achieves 91.4% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=91.4,
        dataset_name="CIFAR-10",
        model_name="ResNet",
        citation=CitationCoordinate(page_number=1),
    )
    run = ExecutionRun(
        run_id="RUN_1",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )

    tree = DiagnosticTree()
    # 91.4 vs 90.2 -> delta 1.2
    hypotheses = tree.evaluate_rules(claim, run, reproduced_value=90.2, absolute_delta=1.2)
    assert any(h.category == "seed_variance" for h in hypotheses)


def test_diagnostic_tree_detects_scale_mismatch():
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Achieves 90.0% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=90.0,
        dataset_name="CIFAR-10",
        model_name="ResNet",
        citation=CitationCoordinate(page_number=1),
    )
    run = ExecutionRun(
        run_id="RUN_1",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )

    tree = DiagnosticTree()
    # 90.0 vs 0.90 -> ratio 0.01
    hypotheses = tree.evaluate_rules(claim, run, reproduced_value=0.90, absolute_delta=89.1)
    assert any(h.category == "scale_mismatch" for h in hypotheses)


def test_forensic_investigator():
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Achieves 90.0% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=90.0,
        dataset_name="CIFAR-10",
        model_name="ResNet",
        citation=CitationCoordinate(page_number=1),
    )
    run = ExecutionRun(
        run_id="RUN_1",
        experiment_id="EXP_1",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        telemetry=ResourceTelemetry(wall_clock_time_sec=10.0),
    )

    investigator = ForensicInvestigator()
    report = investigator.diagnose(claim, run, reproduced_value=84.0, absolute_delta=6.0)
    assert report.claim_id == "CLM_001"
    assert len(report.ranked_hypotheses) > 0
    assert "Primary probable cause" in report.diagnostic_summary
