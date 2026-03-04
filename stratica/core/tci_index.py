"""Temporal Climate Integrity Index (TCI) computation.

Based on paper Section 2.1: 
TCI = Σ(i=1 to 9) [w_i * φ_i] where Σ(w_i) = 1; φ_i in [0,1]
"""

from typing import Dict, Any, Optional, List
import numpy as np
from dataclasses import dataclass

from stratica.utils.constants import TCI_THRESHOLDS, TCI_FUNCTIONAL_THRESHOLD


@dataclass
class TCIResults:
    """Results from TCI computation."""
    tci_composite: float
    classification: str
    parameters: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None
    functional: Optional[bool] = None
    confidence: Optional[float] = None
    
    def __post_init__(self):
        """Set functional flag based on threshold."""
        self.functional = self.tci_composite >= TCI_FUNCTIONAL_THRESHOLD


class TCIIndex:
    """Temporal Climate Integrity Index computation engine."""
    
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize TCI index with optional custom weights.
        
        Args:
            weights: Dictionary of parameter weights (must sum to 1.0)
                   If None, uses default weights from paper Section 2.2
        """
        if weights is None:
            from stratica.utils.constants import PARAMETER_WEIGHTS
            self.weights = PARAMETER_WEIGHTS.copy()
        else:
            # Validate weights sum to 1.0
            if abs(sum(weights.values()) - 1.0) > 1e-6:
                raise ValueError(f"Weights must sum to 1.0, got {sum(weights.values())}")
            self.weights = weights
        
        self.thresholds = TCI_THRESHOLDS
        self.functional_threshold = TCI_FUNCTIONAL_THRESHOLD
    
    def compute(self, parameter_scores: Dict[str, float]) -> float:
        """
        Compute composite TCI score from normalized parameter scores.
        
        Args:
            parameter_scores: Dictionary mapping parameter names to normalized scores [0,1]
            
        Returns:
            Composite TCI score in range [0,1]
            
        Raises:
            ValueError: If parameters don't match weights or scores outside [0,1]
        """
        # Validate inputs
        if set(parameter_scores.keys()) != set(self.weights.keys()):
            missing = set(self.weights.keys()) - set(parameter_scores.keys())
            extra = set(parameter_scores.keys()) - set(self.weights.keys())
            raise ValueError(
                f"Parameter mismatch. Missing: {missing}, Extra: {extra}"
            )
        
        for name, score in parameter_scores.items():
            if not 0 <= score <= 1:
                raise ValueError(f"Parameter {name} score {score} outside [0,1]")
        
        # Compute weighted sum
        tci = sum(
            self.weights[name] * score 
            for name, score in parameter_scores.items()
        )
        
        return float(tci)
    
    def classify(self, tci_value: float) -> str:
        """
        Classify TCI value into functional categories.
        
        Args:
            tci_value: Composite TCI score
            
        Returns:
            Classification string: 'optimal', 'good', 'moderate', 'marginal', 'dysfunctional'
        """
        if tci_value > self.thresholds["optimal"]:
            return "optimal"
        elif tci_value > self.thresholds["good"]:
            return "good"
        elif tci_value > self.thresholds["moderate"]:
            return "moderate"
        elif tci_value > self.thresholds["marginal"]:
            return "marginal"
        else:
            return "dysfunctional"
    
    def is_functional(self, tci_value: float) -> bool:
        """Check if TCI meets functional threshold for reliable paleoclimate interpretation."""
        return tci_value >= self.functional_threshold
    
    def confidence_interval(
        self, 
        parameter_scores: Dict[str, float],
        parameter_errors: Optional[Dict[str, float]] = None,
        n_samples: int = 1000
    ) -> Dict[str, float]:
        """
        Estimate confidence interval for TCI via Monte Carlo sampling.
        
        Args:
            parameter_scores: Best estimates for each parameter
            parameter_errors: Uncertainty for each parameter (std dev)
            n_samples: Number of Monte Carlo samples
            
        Returns:
            Dictionary with 'mean', 'std', 'ci_lower', 'ci_upper' (95% CI)
        """
        if parameter_errors is None:
            # Default errors if not provided
            parameter_errors = {name: 0.05 for name in parameter_scores}
        
        # Monte Carlo sampling
        samples = []
        for _ in range(n_samples):
            sample_scores = {}
            for name, score in parameter_scores.items():
                # Sample from truncated normal to stay in [0,1]
                raw = np.random.normal(score, parameter_errors[name])
                sample_scores[name] = np.clip(raw, 0, 1)
            
            tci_sample = self.compute(sample_scores)
            samples.append(tci_sample)
        
        samples = np.array(samples)
        
        return {
            "mean": float(np.mean(samples)),
            "std": float(np.std(samples)),
            "ci_lower": float(np.percentile(samples, 2.5)),
            "ci_upper": float(np.percentile(samples, 97.5)),
        }
    
    def parameter_contributions(self, parameter_scores: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate each parameter's contribution to the final TCI.
        
        Returns:
            Dictionary mapping parameter names to their contribution (weight * score)
        """
        return {
            name: self.weights[name] * score
            for name, score in parameter_scores.items()
        }
    
    def __repr__(self) -> str:
        """String representation."""
        weights_str = ", ".join(f"{k}:{v:.2f}" for k, v in self.weights.items())
        return f"TCIIndex(weights={{{weights_str}}})"
