"""Forensic discrepancy investigator producing ranked causal hypotheses and diagnostic reports."""

from typing import List, Optional
from paperrep.diagnosis.diagnostic_tree import DiagnosticTree
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.execution import ExecutionRun
from paperrep.schemas.verdict import DiscrepancyHypothesis, DiscrepancyReport


class ForensicInvestigator:
    """Investigates numerical discrepancies and synthesizes evidence-backed diagnostic reports."""

    def __init__(self) -> None:
        self.diagnostic_tree = DiagnosticTree()

    def diagnose(
        self,
        claim: ClaimSpec,
        run: ExecutionRun,
        reproduced_value: float,
        absolute_delta: float,
    ) -> DiscrepancyReport:
        """Analyzes a discrepant replication run and produces a ranked DiscrepancyReport.
        
        Args:
            claim: Target ClaimSpec.
            run: Executed run with telemetry and logs.
            reproduced_value: Observed reproduced float metric.
            absolute_delta: Absolute difference from published value.
            
        Returns:
            DiscrepancyReport with ranked hypotheses and executive diagnostic summary.
        """
        hypotheses = self.diagnostic_tree.evaluate_rules(
            claim=claim,
            run=run,
            reproduced_value=reproduced_value,
            absolute_delta=absolute_delta,
        )

        # Sort hypotheses by descending confidence score
        hypotheses.sort(key=lambda h: h.confidence_score, reverse=True)

        top_hyp = hypotheses[0] if hypotheses else None
        summary = (
            f"Observed {claim.metric_name} of {reproduced_value:.2f} diverges from published "
            f"{claim.published_value:.2f} by {absolute_delta:.2f} percentage points. "
            f"Primary probable cause: {top_hyp.category if top_hyp else 'Unknown anomaly'}."
        )

        return DiscrepancyReport(
            claim_id=claim.claim_id,
            published_value=claim.published_value,
            reproduced_value=reproduced_value,
            delta=absolute_delta,
            ranked_hypotheses=hypotheses,
            diagnostic_summary=summary,
        )
