"""Core deterministic state-machine orchestration pipeline for PaperReplicator."""

import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from uuid import uuid4

from paperrep.comparator.numeric_comparator import NumericComparator
from paperrep.diagnosis.investigator import ForensicInvestigator
from paperrep.extractors.claim_extractor import ClaimExtractor
from paperrep.extractors.spec_generator import SpecGenerator
from paperrep.parser.pdf_loader import PDFLoader
from paperrep.provenance.hasher import hash_string
from paperrep.reports.generator import ReportGenerator
from paperrep.resolver.repo_finder import RepoFinder
from paperrep.sandbox.docker_runner import DockerRunner
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.report import ArtifactProvenance, ReproducibilityReport
from paperrep.schemas.verdict import VerdictStatus
from paperrep.synthesis.harness_builder import HarnessBuilder


class ReplicationPipeline:
    """Orchestrates end-to-end paper verification across the typed state-machine stages."""

    def __init__(
        self,
        strict_tolerance: float = 0.5,
        loose_tolerance: float = 2.0,
        timeout_seconds: int = 1800,
        gpu_required: bool = False,
    ) -> None:
        self.strict_tolerance = strict_tolerance
        self.loose_tolerance = loose_tolerance
        self.timeout_seconds = timeout_seconds
        self.gpu_required = gpu_required

        # Component Initialization
        self.pdf_loader = PDFLoader()
        self.claim_extractor = ClaimExtractor()
        self.repo_finder = RepoFinder()
        self.spec_generator = SpecGenerator()
        self.harness_builder = HarnessBuilder()
        self.docker_runner = DockerRunner(fallback_to_local=True)
        self.comparator = NumericComparator(
            default_strict_tolerance=strict_tolerance,
            default_loose_tolerance=loose_tolerance,
        )
        self.investigator = ForensicInvestigator()
        self.report_generator = ReportGenerator()

    def run(
        self,
        paper_path: str | Path,
        claim_id: Optional[str] = None,
        output_dir: str | Path = "./reproduction_report",
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> ReproducibilityReport:
        """Executes the full 10-stage scientific replication pipeline.
        
        Args:
            paper_path: Path to scientific PDF.
            claim_id: Specific claim ID to evaluate (e.g. 'CLM_001'). If None, automatically selects primary claim.
            output_dir: Directory where execution artifacts and reports are saved.
            progress_callback: Optional status logging callback.
            
        Returns:
            Fully compiled and auditable ReproducibilityReport.
        """
        def log(msg: str):
            if progress_callback:
                progress_callback(msg)

        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Document Ingestion & Structure Parsing
        log(f"[1/8] Ingesting and parsing PDF: {Path(paper_path).name}")
        paper_doc = self.pdf_loader.load(paper_path)
        log(f"      Title: {paper_doc.metadata.title}")
        log(f"      Extracted {len(paper_doc.sections)} sections, {len(paper_doc.tables)} tables, {len(paper_doc.extracted_urls)} URLs")

        # Stage 2: Repository & Asset Discovery
        log("[2/8] Resolving code repository and asset links...")
        repo_url = self.repo_finder.find_repository(paper_doc)
        if repo_url:
            log(f"      Resolved Repository: {repo_url}")
        else:
            log("      No public GitHub link detected; operating in reference benchmark mode.")

        # Stage 3: Semantic Claim Extraction
        log("[3/8] Extracting verifiable empirical claims...")
        claim_registry = self.claim_extractor.extract_claims(paper_doc, use_llm=True)
        log(f"      Identified {len(claim_registry.claims)} empirical claims.")

        # Stage 4: Target Claim Selection
        if claim_id:
            target_claim = next((c for c in claim_registry.claims if c.claim_id == claim_id), None)
            if not target_claim:
                raise ValueError(f"Claim ID '{claim_id}' not found in extracted claims.")
        else:
            target_claim = claim_registry.claims[0]

        log(f"[4/8] Selected Replication Target: [{target_claim.claim_id}] {target_claim.metric_name} = {target_claim.published_value}")
        log(f"      Citation: Page {target_claim.citation.page_number}")

        # Stage 5: Experiment Plan Generation
        log("[5/8] Synthesizing experiment contract specification...")
        experiment_plan = self.spec_generator.generate_plan(
            claim=target_claim,
            paper=paper_doc,
            repo_url=repo_url,
            gpu_required=self.gpu_required,
            timeout_seconds=self.timeout_seconds,
        )

        # Stage 6: Execution Harness Synthesis
        log("[6/8] Synthesizing execution harness script (paperrep_harness.py)...")
        harness_code = self.harness_builder.build_harness_script(experiment_plan, target_claim)
        harness_hash = hash_string(harness_code)

        # Stage 7: Sandboxed Execution
        log(f"[7/8] Executing verification harness inside sandbox (Timeout: {self.timeout_seconds}s)...")
        sandbox_run_dir = out_dir / "sandbox_run"
        execution_run = self.docker_runner.execute(
            plan=experiment_plan,
            harness_code=harness_code,
            output_dir=sandbox_run_dir,
        )
        log(f"      Sandbox completed with exit code {execution_run.exit_code} ({execution_run.telemetry.wall_clock_time_sec}s)")

        # Stage 8: Numerical Comparison & Tolerance Gates
        log("[8/8] Evaluating reproduced findings against published claims...")
        verdict = self.comparator.evaluate(
            claim=target_claim,
            execution_run=execution_run,
            strict_tolerance=self.strict_tolerance,
            loose_tolerance=self.loose_tolerance,
        )

        # Stage 9: Discrepancy Diagnosis (if status is DISCREPANT)
        if verdict.verdict_status == VerdictStatus.DISCREPANT:
            log("      Discrepancy detected; initiating forensic investigation...")
            assert verdict.reproduced_value is not None
            assert verdict.absolute_delta is not None
            diagnosis = self.investigator.diagnose(
                claim=target_claim,
                run=execution_run,
                reproduced_value=verdict.reproduced_value,
                absolute_delta=verdict.absolute_delta,
            )
            verdict.diagnosis = diagnosis
            log(f"      Primary Diagnostic Cause: {diagnosis.diagnostic_summary}")
        else:
            log(f"      Verdict: {verdict.verdict_status.value}")

        # Stage 10: Compile Report & Provenance Artifacts
        provenance = ArtifactProvenance(
            pdf_sha256=paper_doc.file_hash_sha256,
            git_repo_url=repo_url,
            dataset_source_uri=experiment_plan.dataset.source_uri,
            docker_image_digest=execution_run.container_image_digest,
            harness_script_sha256=harness_hash,
        )

        exec_summary = (
            f"PaperReplicator evaluated claim '{target_claim.statement}' from '{paper_doc.metadata.title}'. "
            f"Published: {verdict.published_value}, Reproduced: {verdict.reproduced_value}. "
            f"Resulting verdict: {verdict.verdict_status.value}."
        )

        report = ReproducibilityReport(
            report_id=f"REP_{uuid4().hex[:8].upper()}",
            generated_at=datetime.utcnow(),
            paper_metadata=paper_doc.metadata,
            evaluated_claim=target_claim,
            execution_run=execution_run,
            verdict=verdict,
            provenance=provenance,
            executive_summary=exec_summary,
        )

        # Save Markdown and HTML reports
        md_file, html_file = self.report_generator.save_reports(report, out_dir)
        log("[OK] Replication Complete!")
        log(f"    Report (Markdown): {md_file}")
        log(f"    Report (HTML):     {html_file}")

        return report
