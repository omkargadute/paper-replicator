"""Unit tests for Pydantic v2 schemas and serialization."""

from uuid import uuid4
import pytest
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry
from paperrep.schemas.experiment import DatasetSpec, ExperimentPlan, HardwareProfile
from paperrep.schemas.paper import PaperDocument, PaperMetadata, PaperSection, PaperTable
from paperrep.schemas.verdict import EvaluationVerdict, VerdictStatus


def test_paper_document_serialization():
    doc = PaperDocument(
        file_path="sample.pdf",
        file_hash_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        metadata=PaperMetadata(
            title="Attention Is All You Need",
            authors=["Ashish Vaswani", "Noam Shazeer"],
            year=2017,
        ),
        sections=[PaperSection(title="1 Introduction", level=1, content="The dominant sequence...")],
        tables=[PaperTable(table_id="table_1", caption="Results", page_number=5)],
    )
    data = doc.model_dump()
    restored = PaperDocument.model_validate(data)
    assert restored.metadata.title == "Attention Is All You Need"
    assert len(restored.sections) == 1
    assert restored.file_hash_sha256 == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_claim_spec_validation():
    claim = ClaimSpec(
        claim_id="CLM_001",
        statement="Our model achieves 91.4% accuracy on CIFAR-10",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name="Accuracy",
        published_value=91.4,
        published_uncertainty=0.2,
        dataset_name="CIFAR-10",
        model_name="ResNet-18",
        citation=CitationCoordinate(page_number=6, table_identifier="Table 2"),
    )
    assert claim.claim_id == "CLM_001"
    assert claim.published_value == 91.4
    assert claim.is_percentage is True


def test_experiment_plan_defaults():
    plan = ExperimentPlan(
        experiment_id="EXP_001",
        target_claim_id="CLM_001",
        dataset=DatasetSpec(
            name="CIFAR-10",
            source_type="torchvision",
            source_uri="torchvision.datasets.CIFAR10",
            split="test",
        ),
        entry_point_command="python evaluate.py",
    )
    assert plan.seeds == [42]
    assert plan.hardware.gpu_required is False
    assert plan.hardware.timeout_seconds == 1800
