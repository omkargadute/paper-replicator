"""Deterministic numerical comparator and tolerance classifier."""

from typing import Optional
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.execution import ExecutionRun, ExecutionStatus
from paperrep.schemas.verdict import EvaluationVerdict, VerdictStatus


class NumericComparator:
    """Compares reproduced numerical metrics against published paper claims using strict tolerances."""

    def __init__(
        self,
        default_strict_tolerance: float = 0.5,
        default_loose_tolerance: float = 2.0,
    ) -> None:
        """
        Args:
            default_strict_tolerance: Absolute difference threshold for EXACT_REPLICATION (e.g. 0.5%).
            default_loose_tolerance: Absolute difference threshold for PARTIAL_REPLICATION (e.g. 2.0%).
        """
        self.default_strict_tolerance = default_strict_tolerance
        self.default_loose_tolerance = default_loose_tolerance

    def evaluate(
        self,
        claim: ClaimSpec,
        execution_run: ExecutionRun,
        strict_tolerance: Optional[float] = None,
        loose_tolerance: Optional[float] = None,
    ) -> EvaluationVerdict:
        """Evaluates an execution run against the target claim specification.
        
        Args:
            claim: Target claim specification from paper.
            execution_run: Completed or failed execution run.
            strict_tolerance: Optional override for strict tolerance.
            loose_tolerance: Optional override for loose tolerance.
            
        Returns:
            EvaluationVerdict containing numerical analysis and 5-tier classification.
        """
        strict_tol = strict_tolerance if strict_tolerance is not None else self.default_strict_tolerance
        loose_tol = loose_tolerance if loose_tolerance is not None else self.default_loose_tolerance
        
        # Check if execution failed
        if execution_run.status != ExecutionStatus.COMPLETED or execution_run.exit_code != 0:
            return EvaluationVerdict(
                claim_id=claim.claim_id,
                verdict_status=VerdictStatus.EXECUTION_FAILED,
                metric_name=claim.metric_name,
                published_value=claim.published_value,
                reproduced_value=None,
                absolute_delta=None,
                relative_error_percent=None,
                strict_tolerance_applied=strict_tol,
                loose_tolerance_applied=loose_tol,
                within_tolerance=False,
                diagnosis=None,
            )

        # Check if the target metric exists in output
        target_metric_key = self._find_metric_key(claim.metric_name, execution_run.raw_metrics)
        if target_metric_key is None:
            return EvaluationVerdict(
                claim_id=claim.claim_id,
                verdict_status=VerdictStatus.EXECUTION_FAILED,
                metric_name=claim.metric_name,
                published_value=claim.published_value,
                reproduced_value=None,
                absolute_delta=None,
                relative_error_percent=None,
                strict_tolerance_applied=strict_tol,
                loose_tolerance_applied=loose_tol,
                within_tolerance=False,
                diagnosis=None,
            )

        reproduced_value = execution_run.raw_metrics[target_metric_key]
        
        # Scale handling: If published value is e.g. 91.4 (%) but reproduced is 0.914, normalize
        if claim.is_percentage and 0.0 <= reproduced_value <= 1.0 and claim.published_value > 1.0:
            reproduced_value = reproduced_value * 100.0

        absolute_delta = abs(reproduced_value - claim.published_value)
        relative_error_percent = (
            (absolute_delta / abs(claim.published_value)) * 100.0
            if claim.published_value != 0
            else 0.0
        )

        if absolute_delta <= strict_tol:
            status = VerdictStatus.EXACT_REPLICATION
            within_tol = True
        elif absolute_delta <= loose_tol:
            status = VerdictStatus.PARTIAL_REPLICATION
            within_tol = True
        else:
            status = VerdictStatus.DISCREPANT
            within_tol = False

        return EvaluationVerdict(
            claim_id=claim.claim_id,
            verdict_status=status,
            metric_name=claim.metric_name,
            published_value=claim.published_value,
            reproduced_value=round(reproduced_value, 4),
            absolute_delta=round(absolute_delta, 4),
            relative_error_percent=round(relative_error_percent, 4),
            strict_tolerance_applied=strict_tol,
            loose_tolerance_applied=loose_tol,
            within_tolerance=within_tol,
            diagnosis=None,
        )

    def _find_metric_key(self, metric_name: str, raw_metrics: dict) -> Optional[str]:
        """Case-insensitive fuzzy match for metric name in raw_metrics dictionary."""
        normalized_target = metric_name.strip().lower()
        
        # Direct exact or lowercase match
        for key in raw_metrics:
            if key.strip().lower() == normalized_target:
                return key
                
        # Common aliases (e.g. accuracy -> acc, test_accuracy -> accuracy)
        aliases = {
            "acc": ["accuracy", "top1", "top1_acc", "test_acc", "test_accuracy"],
            "accuracy": ["acc", "top1", "top1_acc", "test_acc", "test_accuracy"],
            "bleu": ["bleu_score", "test_bleu", "bleu-4"],
            "f1": ["f1_score", "macro_f1", "micro_f1", "test_f1"],
        }
        
        possible_aliases = aliases.get(normalized_target, [])
        for key in raw_metrics:
            norm_key = key.strip().lower()
            if norm_key in possible_aliases:
                return key
            for alias in possible_aliases:
                if alias in norm_key:
                    return key

        return None
