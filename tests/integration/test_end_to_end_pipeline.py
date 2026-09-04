"""End-to-end integration test verifying complete pipeline execution and report compilation."""

from pathlib import Path
import fitz
import pytest
from paperrep.pipeline import ReplicationPipeline
from paperrep.schemas.verdict import VerdictStatus


@pytest.fixture
def synthetic_paper(tmp_path: Path) -> Path:
    """Creates an end-to-end synthetic paper PDF fixture with verifiable empirical claims."""
    pdf_path = tmp_path / "empirical_paper.pdf"
    doc = fitz.open()
    page = doc.new_page()

    paper_text = """Deep Residual Learning for Visual Verification
Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun

Abstract
Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.

1 Introduction
Our method achieves 91.4% accuracy on CIFAR-10 benchmark.
Code and models are open-sourced at https://github.com/pytorch/vision for reproducibility.

2 Experimental Results
The empirical findings demonstrate consistent gains across standard image recognition benchmarks.
"""
    page.insert_text((50, 72), paper_text)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_full_pipeline_run(synthetic_paper: Path, tmp_path: Path):
    out_dir = tmp_path / "replication_output"
    pipeline = ReplicationPipeline(
        strict_tolerance=0.5,
        loose_tolerance=2.0,
        timeout_seconds=300,
        gpu_required=False,
    )

    log_messages = []
    report = pipeline.run(
        paper_path=synthetic_paper,
        output_dir=out_dir,
        progress_callback=lambda msg: log_messages.append(msg),
    )

    # 1. Verify report structure
    assert report.evaluated_claim.published_value == 91.4
    assert report.verdict.verdict_status in [VerdictStatus.EXACT_REPLICATION, VerdictStatus.PARTIAL_REPLICATION]
    assert report.verdict.within_tolerance is True
    assert report.provenance.pdf_sha256 is not None
    assert len(report.provenance.pdf_sha256) == 64

    # 2. Verify artifact outputs on disk
    md_report = out_dir / "reproducibility_report.md"
    html_report = out_dir / "reproducibility_report.html"
    assert md_report.exists()
    assert html_report.exists()

    md_content = md_report.read_text(encoding="utf-8")
    assert "Scientific Reproducibility Audit Report" in md_content
    assert "91.40" in md_content

    # 3. Verify execution logs were captured
    assert any("[1/8]" in msg for msg in log_messages)
    assert any("[OK] Replication Complete!" in msg for msg in log_messages)
