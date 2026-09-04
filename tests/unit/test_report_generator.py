"""Unit tests for Reproducibility Report rendering in Markdown and HTML."""

from datetime import datetime
from pathlib import Path
from paperrep.reports.generator import ReportGenerator
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry
from paperrep.schemas.paper import PaperMetadata
from paperrep.schemas.report import ArtifactProvenance, ReproducibilityReport
from paperrep.schemas.verdict import EvaluationVerdict, VerdictStatus


def test_report_generation_markdown_and_html(tmp_path: Path):
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Our method achieves 91.4% accuracy",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=91.4,
        dataset_name="CIFAR-10",
        model_name="ResNet-18",
        citation=CitationCoordinate(page_number=5, table_identifier="Table 1"),
    )
    run = ExecutionRun(
        run_id="RUN_001",
        experiment_id="EXP_001",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={"accuracy": 91.2},
        telemetry=ResourceTelemetry(wall_clock_time_sec=42.0),
        container_image_digest="paperrep-sandbox:latest",
    )
    verdict = EvaluationVerdict(
        claim_id="CLM_001",
        verdict_status=VerdictStatus.EXACT_REPLICATION,
        metric_name="Accuracy",
        published_value=91.4,
        reproduced_value=91.2,
        absolute_delta=0.2,
        relative_error_percent=0.22,
        strict_tolerance_applied=0.5,
        loose_tolerance_applied=2.0,
        within_tolerance=True,
    )
    provenance = ArtifactProvenance(
        pdf_sha256="1234567890abcdef",
        dataset_source_uri="torchvision.datasets.CIFAR10",
        docker_image_digest="paperrep-sandbox:latest",
        harness_script_sha256="fedcba0987654321",
    )

    report = ReproducibilityReport(
        report_id="REP_TEST_001",
        generated_at=datetime.utcnow(),
        paper_metadata=PaperMetadata(title="Deep Residual Learning for Image Recognition", authors=["Kaiming He"]),
        evaluated_claim=claim,
        execution_run=run,
        verdict=verdict,
        provenance=provenance,
        executive_summary="Replication verified within strict tolerance.",
    )

    generator = ReportGenerator()
    md_file, html_file = generator.save_reports(report, tmp_path)

    assert md_file.exists()
    assert html_file.exists()

    md_content = md_file.read_text(encoding="utf-8")
    assert "VERDICT: EXACT / CLOSE REPLICATION" in md_content
    assert "Deep Residual Learning" in md_content
    assert "91.40" in md_content

    html_content = html_file.read_text(encoding="utf-8")
    assert "EXACT REPLICATION" in html_content
    assert "Kaiming He" in html_content
