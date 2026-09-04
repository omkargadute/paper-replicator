"""Statistical aggregation and significance testing for multi-seed replication runs."""

import math
from typing import Dict, List, Optional, Tuple


class StatisticalEvaluator:
    """Computes sample statistics, confidence intervals, and t-tests across replicated seeds."""

    @staticmethod
    def aggregate_seeds(values: List[float]) -> Dict[str, float]:
        """Calculates mean, standard deviation, and standard error across runs.
        
        Args:
            values: List of metric values from different seed runs.
            
        Returns:
            Dictionary with 'mean', 'std', 'stderr', 'min', 'max'.
        """
        n = len(values)
        if n == 0:
            return {"mean": 0.0, "std": 0.0, "stderr": 0.0, "min": 0.0, "max": 0.0, "n": 0}

        mean = sum(values) / n
        if n > 1:
            variance = sum((x - mean) ** 2 for x in values) / (n - 1)
            std = math.sqrt(variance)
            stderr = std / math.sqrt(n)
        else:
            std = 0.0
            stderr = 0.0

        return {
            "mean": round(mean, 4),
            "std": round(std, 4),
            "stderr": round(stderr, 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
            "n": n,
        }

    @staticmethod
    def compute_z_score(observed_mean: float, published_value: float, observed_std: float) -> Optional[float]:
        """Computes z-score distance from published claim."""
        if observed_std <= 1e-6:
            return None
        return round((observed_mean - published_value) / observed_std, 3)
