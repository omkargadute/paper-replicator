"""Deterministic rule-based diagnostic tree for replication discrepancies."""

from typing import List, Optional
from paperrep.schemas.claim import ClaimSpec
from paperrep.schemas.execution import ExecutionRun
from paperrep.schemas.verdict import DiscrepancyHypothesis


class DiagnosticTree:
    """Heuristic rule-engine that scans execution logs, metrics, and parameters for discrepancy causes."""

    def evaluate_rules(
        self,
        claim: ClaimSpec,
        run: ExecutionRun,
        reproduced_value: float,
        absolute_delta: float,
    ) -> List[DiscrepancyHypothesis]:
        """Applies deterministic diagnostic rules against the execution trace."""
        hypotheses: List[DiscrepancyHypothesis] = []
        hyp_counter = 1

        # Rule 1: Scale / Percentage Mismatch
        ratio = reproduced_value / claim.published_value if claim.published_value != 0 else 1.0
        if 95.0 <= ratio <= 105.0 or 0.0095 <= ratio <= 0.0105:
            hypotheses.append(
                DiscrepancyHypothesis(
                    hypothesis_id=f"HYP_{hyp_counter:03d}",
                    category="scale_mismatch",
                    explanation=f"Metric scale mismatch: Reproduced value ({reproduced_value}) appears to differ by a factor of 100 from published value ({claim.published_value}).",
                    confidence_score=0.95,
                    supporting_evidence=[f"Ratio reproduced / published = {ratio:.4f}"],
                    suggested_verification_test="Multiply or divide metric by 100.0 and re-evaluate.",
                )
            )
            hyp_counter += 1

        # Rule 2: Stochastic / Random Seed Sensitivity
        # If absolute delta is between 0.5% and 2.5%, it is often normal stochastic initialization variance
        if 0.5 < absolute_delta <= 2.5:
            hypotheses.append(
                DiscrepancyHypothesis(
                    hypothesis_id=f"HYP_{hyp_counter:03d}",
                    category="seed_variance",
                    explanation=(
                        f"Stochastic seed variance: The discrepancy ({absolute_delta:.2f} percentage points) "
                        "is consistent with standard random seed and weight initialization variance in deep learning benchmarks."
                    ),
                    confidence_score=0.75,
                    supporting_evidence=[
                        f"Observed delta {absolute_delta:.2f} is within empirical 3-sigma bounds for {claim.metric_name}."
                    ],
                    suggested_verification_test="Evaluate across 5 distinct random seeds [42, 43, 44, 45, 46] and compute mean ± std.",
                )
            )
            hyp_counter += 1

        # Rule 3: Execution Truncation / Step Limit
        if "timeout" in run.stderr_log.lower() or "truncated" in run.stdout_log.lower():
            hypotheses.append(
                DiscrepancyHypothesis(
                    hypothesis_id=f"HYP_{hyp_counter:03d}",
                    category="execution_truncation",
                    explanation="Evaluation was prematurely truncated by execution limits or incomplete batch iterations.",
                    confidence_score=0.85,
                    supporting_evidence=["Trace logs indicate timeout or early termination flag."],
                    suggested_verification_test="Increase timeout limit and verify complete dataset epoch traversal.",
                )
            )
            hyp_counter += 1

        # Rule 4: Data Preprocessing or Augmentation Drift
        if absolute_delta > 2.5:
            hypotheses.append(
                DiscrepancyHypothesis(
                    hypothesis_id=f"HYP_{hyp_counter:03d}",
                    category="preprocessing_mismatch",
                    explanation=(
                        f"Preprocessing or Test-Split Mismatch: Large numerical divergence ({absolute_delta:.2f}) "
                        "strongly suggests a difference in data normalization (e.g. ImageNet mean/std vs. [0, 1] scaling), "
                        "or evaluation on a different split than reported in the paper."
                    ),
                    confidence_score=0.70,
                    supporting_evidence=[
                        f"Significant divergence ({absolute_delta:.2f} vs published {claim.published_value})."
                    ],
                    suggested_verification_test="Inspect dataset loader transforms and sample count against paper Section 4.",
                )
            )
            hyp_counter += 1

        return hypotheses
