"""Unit tests for Evidence Provenance Graph generation."""

from paperrep.provenance.graph import ProvenanceGraphBuilder
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry
from paperrep.schemas.experiment import DatasetSpec, ExperimentPlan
from paperrep.schemas.paper import PaperDocument, PaperMetadata
from paperrep.schemas.verdict import EvaluationVerdict, VerdictStatus


def test_provenance_graph_jsonld_and_mermaid():
    paper = PaperDocument(
        file_path="attention.pdf",
        file_hash_sha256="abc123456789",
        metadata=PaperMetadata(title="Attention Is All You Need"),
    )
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Achieves 28.4 BLEU",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="BLEU",
        published_value=28.4,
        dataset_name="WMT-14",
        model_name="Transformer",
        citation=CitationCoordinate(page_number=8),
    )
    plan = ExperimentPlan(
        experiment_id="EXP_001",
        target_claim_id="CLM_001",
        dataset=DatasetSpec(name="WMT-14", source_type="huggingface", source_uri="wmt14"),
        entry_point_command="python eval.py",
    )
    run = ExecutionRun(
        run_id="RUN_001",
        experiment_id="EXP_001",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        telemetry=ResourceTelemetry(wall_clock_time_sec=12.5),
        container_image_digest="paperrep-sandbox:latest",
    )
    verdict = EvaluationVerdict(
        claim_id="CLM_001",
        verdict_status=VerdictStatus.EXACT_REPLICATION,
        metric_name="BLEU",
        published_value=28.4,
        reproduced_value=28.3,
        absolute_delta=0.1,
        relative_error_percent=0.35,
        strict_tolerance_applied=0.5,
        loose_tolerance_applied=2.0,
        within_tolerance=True,
    )

    graph_dict = ProvenanceGraphBuilder.build_graph_dict(paper, claim, plan, run, verdict)
    assert graph_dict["@type"] == "ScientificEvidenceAudit"
    assert graph_dict["paper"]["sha256"] == "abc123456789"
    assert graph_dict["verdict"]["within_tolerance"] is True

    mermaid = ProvenanceGraphBuilder.to_mermaid(paper, claim, run, verdict)
    assert "flowchart TD" in mermaid
    assert "CLM_001" in mermaid
    assert "EXACT_REPLICATION" in mermaid
