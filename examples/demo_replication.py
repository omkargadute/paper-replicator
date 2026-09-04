"""Interactive demonstration script for PaperReplicator."""

from pathlib import Path
import fitz
from paperrep.pipeline import ReplicationPipeline


def create_demo_paper(pdf_path: Path) -> Path:
    """Generates a sample research paper PDF with empirical claims and code links."""
    doc = fitz.open()
    page = doc.new_page()

    paper_content = """DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter
Victor Sanh, Lysandre Debut, Julien Chaumond, Thomas Wolf

Abstract
As Large Language Models become larger, deploying them in real-time applications becomes increasingly difficult. We introduce DistilBERT, a student model trained using knowledge distillation.

1 Introduction
Our method retains 97% of BERT's performance while being 40% smaller and 60% faster.
Specifically, DistilBERT achieves 91.3% accuracy on the SST-2 sentiment classification benchmark.
Official code and checkpoints are available at https://github.com/huggingface/transformers for complete reproducibility.

2 Benchmark Results
We evaluate DistilBERT on standard GLUE tasks.
Table 1: Evaluation Metrics on GLUE Test Set
Model       | SST-2 Acc | QNLI Acc
BERT-Base   | 93.5%     | 90.5%
DistilBERT  | 91.3%     | 89.2%

3 Conclusion
Distillation allows substantial latency reduction while maintaining empirical parity.
"""
    page.insert_text((50, 72), paper_content)
    doc.save(str(pdf_path))
    doc.close()
    return pdf_path


def main():
    demo_dir = Path("./examples_out").resolve()
    demo_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = demo_dir / "distilbert_paper.pdf"

    print(f"[1] Generating sample research paper: {pdf_path.name}")
    create_demo_paper(pdf_path)

    print("\n[2] Initializing PaperReplicator Engine...")
    pipeline = ReplicationPipeline(
        strict_tolerance=0.5,
        loose_tolerance=2.0,
        timeout_seconds=60,
    )

    print("\n[3] Executing End-to-End Replication...")
    report = pipeline.run(
        paper_path=pdf_path,
        output_dir=demo_dir / "report",
        progress_callback=lambda msg: print(f"  {msg}"),
    )

    print("\n========================================================")
    print(f"Target Claim:    {report.evaluated_claim.statement}")
    print(f"Published Value: {report.verdict.published_value}")
    print(f"Reproduced:      {report.verdict.reproduced_value}")
    print(f"Verdict:         {report.verdict.verdict_status.value}")
    print(f"Audit Markdown:  {demo_dir / 'report' / 'reproducibility_report.md'}")
    print(f"Audit HTML:      {demo_dir / 'report' / 'reproducibility_report.html'}")
    print("========================================================")


if __name__ == "__main__":
    main()
