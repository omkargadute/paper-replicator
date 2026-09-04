"""Unit tests for PDFLoader using synthetic scientific PDF fixture."""

from pathlib import Path
import fitz
import pytest
from paperrep.parser.pdf_loader import PDFLoader


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    """Creates a minimal synthetic research paper PDF for testing."""
    pdf_path = tmp_path / "sample_paper.pdf"
    doc = fitz.open()
    page = doc.new_page()

    text = """Attention Is All You Need
Ashish Vaswani, Noam Shazeer

Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer.

1 Introduction
Our method achieves 91.4% accuracy on CIFAR-10 benchmark.
Code is available at https://github.com/tensorflow/tensor2tensor for reproducibility.

2 Experiments
We evaluated our model against various baselines.
"""
    page.insert_text((50, 72), text)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def test_pdf_loader_extracts_structure(sample_pdf: Path):
    loader = PDFLoader()
    paper = loader.load(sample_pdf)

    assert paper.file_path == str(sample_pdf.resolve())
    assert len(paper.file_hash_sha256) == 64
    assert "Attention Is All You Need" in paper.metadata.title or "Sample Paper" in paper.metadata.title
    assert len(paper.sections) >= 1
    assert any("https://github.com/tensorflow/tensor2tensor" in url for url in paper.extracted_urls)
