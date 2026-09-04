"""PaperReplicator Command-Line Interface (CLI)."""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from paperrep.comparator.numeric_comparator import NumericComparator
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
    table.add_row("Strict Tolerance (±)", f"{verdict.strict_tolerance_applied}")
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
