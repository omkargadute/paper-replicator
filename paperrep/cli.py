"""PaperReplicator Command-Line Interface (CLI)."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from paperrep.comparator.numeric_comparator import NumericComparator
from paperrep.extractors.claim_extractor import ClaimExtractor
from paperrep.parser.pdf_loader import PDFLoader
from paperrep.pipeline import ReplicationPipeline
from paperrep.provenance.hasher import hash_file
from paperrep.schemas.claim import CitationCoordinate, ClaimSpec, ClaimType
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus, ResourceTelemetry

app = typer.Typer(
    name="paperrep",
    help="Autonomous Scientific Paper Replication & Evidence-Driven Verification Engine",
    add_completion=False,
)
console = Console()


@app.command("version")
def version_cmd():
    """Display PaperReplicator version and banner."""
    console.print(
        Panel.fit(
            "[bold cyan]PaperReplicator[/bold cyan] v0.1.0\n"
            "[italic]Autonomous Scientific Paper Replication & Verification Engine[/italic]\n"
            "Built with deterministic sandboxing and cryptographic provenance.",
            border_style="cyan",
        )
    )


@app.command("run")
def run_cmd(
    pdf_path: Path = typer.Argument(..., help="Path to scientific research paper PDF"),
    claim_id: Optional[str] = typer.Option(None, "--claim", "-c", help="Specific claim ID to target (e.g. CLM_001)"),
    output_dir: Path = typer.Option(Path("./reproduction_report"), "--output-dir", "-o", help="Output directory"),
    strict: float = typer.Option(0.5, "--strict", help="Strict tolerance threshold (default 0.5%)"),
    loose: float = typer.Option(2.0, "--loose", help="Loose tolerance threshold (default 2.0%)"),
    timeout: int = typer.Option(1800, "--timeout", help="Watchdog timeout in seconds"),
    gpu: bool = typer.Option(False, "--gpu", help="Require GPU allocation"),
):
    """Execute end-to-end scientific paper replication and compile audit report."""
    if not pdf_path.exists():
        console.print(f"[bold red]Error:[/bold red] PDF file not found: {pdf_path}")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Starting PaperReplicator on:[/bold cyan] {pdf_path.name}")
    
    pipeline = ReplicationPipeline(
        strict_tolerance=strict,
        loose_tolerance=loose,
        timeout_seconds=timeout,
        gpu_required=gpu,
    )

    def print_progress(msg: str):
        console.print(f"[dim]{msg}[/dim]")

    report = pipeline.run(
        paper_path=pdf_path,
        claim_id=claim_id,
        output_dir=output_dir,
        progress_callback=print_progress,
    )

    # Render summary card
    verdict = report.verdict
    color = "green" if verdict.within_tolerance else "red"
    console.print(
        Panel(
            f"[bold]Target Claim:[/bold] {report.evaluated_claim.statement}\n"
            f"[bold]Published Value:[/bold] {verdict.published_value:.2f}\n"
            f"[bold]Reproduced Value:[/bold] {verdict.reproduced_value if verdict.reproduced_value is not None else 'N/A'}\n"
            f"[bold]Verdict:[/bold] [{color}]{verdict.verdict_status.value}[/{color}]\n"
            f"[bold]Reports Generated:[/bold] {output_dir.resolve()}",
            title="[Audit] Replication Audit Complete",
            border_style=color,
        )
    )


@app.command("parse")
def parse_cmd(
    pdf_path: Path = typer.Argument(..., help="Path to research paper PDF"),
):
    """Parse scientific paper PDF and display extracted sections and tables."""
    if not pdf_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {pdf_path}")
        raise typer.Exit(1)

    loader = PDFLoader()
    doc = loader.load(pdf_path)

    console.print(Panel.fit(f"[bold cyan]Paper Document:[/bold cyan] {doc.metadata.title}\nSHA-256: {doc.file_hash_sha256}"))
    console.print(f"Authors: {', '.join(doc.metadata.authors) if doc.metadata.authors else 'Unknown'}")
    console.print(f"Abstract: {doc.metadata.abstract[:200]}..." if doc.metadata.abstract else "No abstract detected")
    console.print(f"Extracted Sections: {len(doc.sections)} | Tables: {len(doc.tables)} | URLs: {len(doc.extracted_urls)}")


@app.command("claims")
def claims_cmd(
    pdf_path: Path = typer.Argument(..., help="Path to research paper PDF"),
):
    """Extract verifiable empirical claims from a research paper."""
    if not pdf_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {pdf_path}")
        raise typer.Exit(1)

    loader = PDFLoader()
    doc = loader.load(pdf_path)
    extractor = ClaimExtractor()
    registry = extractor.extract_claims(doc)

    table = Table(title=f"Extracted Claims ({doc.metadata.title[:40]}...)", border_style="cyan")
    table.add_column("Claim ID", style="bold cyan")
    table.add_column("Metric", style="yellow")
    table.add_column("Published", style="green")
    table.add_column("Dataset", style="white")
    table.add_column("Page", style="dim")

    for c in registry.claims:
        table.add_row(
            c.claim_id,
            c.metric_name,
            f"{c.published_value:.2f}" + ("%" if c.is_percentage else ""),
            c.dataset_name,
            str(c.citation.page_number),
        )

    console.print(table)


@app.command("compare")
def compare_cmd(
    published: float = typer.Argument(..., help="Published numerical metric value in paper (e.g. 91.4)"),
    reproduced: float = typer.Argument(..., help="Observed reproduced metric value (e.g. 91.1)"),
    metric: str = typer.Option("Accuracy", "--metric", "-m", help="Metric name"),
    strict: float = typer.Option(0.5, "--strict", help="Strict tolerance threshold (default 0.5)"),
    loose: float = typer.Option(2.0, "--loose", help="Loose tolerance threshold (default 2.0)"),
):
    """Compare a reproduced metric against a published claim using deterministic tolerance gates."""
    claim = ClaimSpec(
        claim_id="CLM_CLI",
        statement=f"Method achieves {published} {metric}",
        claim_type=ClaimType.VERIFIABLE_NUMERIC,
        metric_name=metric,
        published_value=published,
        dataset_name="TestDataset",
        model_name="TestModel",
        citation=CitationCoordinate(page_number=1),
    )

    run = ExecutionRun(
        run_id="RUN_CLI",
        experiment_id="EXP_CLI",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        raw_metrics={metric.lower(): reproduced},
        telemetry=ResourceTelemetry(wall_clock_time_sec=1.0),
    )

    comparator = NumericComparator(
        default_strict_tolerance=strict,
        default_loose_tolerance=loose,
    )
    verdict = comparator.evaluate(claim, run)

    # Render results table
    table = Table(title="Replication Comparison Result", border_style="cyan")
    table.add_column("Field", style="bold white")
    table.add_column("Value", style="green" if verdict.within_tolerance else "red")

    table.add_row("Metric", verdict.metric_name)
    table.add_row("Published Value", f"{verdict.published_value:.4f}")
    table.add_row("Reproduced Value", f"{verdict.reproduced_value:.4f}")
    table.add_row("Absolute Delta", f"{verdict.absolute_delta:.4f}")
    table.add_row("Relative Error", f"{verdict.relative_error_percent:.2f}%")
    table.add_row("Strict Tolerance (+/-)", f"{verdict.strict_tolerance_applied}")
    table.add_row("Verdict Status", f"[bold]{verdict.verdict_status.value}[/bold]")

    console.print(table)


@app.command("hash")
def hash_cmd(file_path: Path = typer.Argument(..., help="Path to file to compute SHA-256 for")):
    """Compute cryptographic SHA-256 hash of a paper PDF or dataset artifact."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file_path}")
        raise typer.Exit(1)

    digest = hash_file(file_path)
    console.print(f"[bold green]File:[/bold green] {file_path.name}")
    console.print(f"[bold green]SHA-256:[/bold green] [yellow]{digest}[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()
