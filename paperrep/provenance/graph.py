"""Evidence Provenance DAG builder for auditability and verification."""

from typing import Any, Dict
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.execution import ExecutionRun
from paperrep.schemas.experiment import ExperimentPlan
from paperrep.schemas.paper import PaperDocument
from paperrep.schemas.verdict import EvaluationVerdict


class ProvenanceGraphBuilder:
    """Constructs auditable DAG linkages connecting raw PDF to final reproducibility verdict."""

    @staticmethod
    def build_graph_dict(
        paper: PaperDocument,
        claim: ClaimSpec,
        plan: ExperimentPlan,
        run: ExecutionRun,
        verdict: EvaluationVerdict,
    ) -> Dict[str, Any]:
        """Builds a JSON-LD structured provenance chain."""
        return {
            "@context": "https://schema.org",
            "@type": "ScientificEvidenceAudit",
            "paper": {
                "title": paper.metadata.title,
                "sha256": paper.file_hash_sha256,
                "file_path": paper.file_path,
            },
            "target_claim": {
                "claim_id": claim.claim_id,
                "statement": claim.statement,
                "metric": claim.metric_name,
                "published_value": claim.published_value,
                "citation": claim.citation.model_dump(),
            },
            "execution_plan": {
                "experiment_id": plan.experiment_id,
                "repo_url": plan.repo_url,
                "dataset": plan.dataset.model_dump(),
                "entry_point": plan.entry_point_command,
            },
            "execution_run": {
                "run_id": run.run_id,
                "seed": run.seed,
                "status": run.status.value,
                "exit_code": run.exit_code,
                "wall_clock_sec": run.telemetry.wall_clock_time_sec,
                "container_digest": run.container_image_digest,
            },
            "verdict": {
                "status": verdict.verdict_status.value,
                "reproduced_value": verdict.reproduced_value,
                "absolute_delta": verdict.absolute_delta,
                "within_tolerance": verdict.within_tolerance,
            },
        }

    @staticmethod
    def to_mermaid(
        paper: PaperDocument,
        claim: ClaimSpec,
        run: ExecutionRun,
        verdict: EvaluationVerdict,
    ) -> str:
        """Generates a Mermaid graph string for visual audit in Markdown reports."""
        status_color = "green" if verdict.within_tolerance else "red"
        return f"""```mermaid
flowchart TD
    P["Paper: {paper.metadata.title[:30]}...<br/>(SHA: {paper.file_hash_sha256[:8]}...)"] --> C["Claim: {claim.claim_id}<br/>{claim.metric_name} = {claim.published_value}"]
    C --> E["Harness Execution<br/>(Seed: {run.seed}, Status: {run.status.value})"]
    E --> V["Verdict: {verdict.verdict_status.value}<br/>(Observed: {verdict.reproduced_value}, Delta: {verdict.absolute_delta})"]
    style V fill:{'#d4edda' if verdict.within_tolerance else '#f8d7da'},stroke:{'#28a745' if verdict.within_tolerance else '#dc3545'}
```"""
