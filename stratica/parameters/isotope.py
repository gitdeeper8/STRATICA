"""ISO - Stable Isotope Fractionation parameter."""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase


class IsotopeFractionation(ParameterBase):
    """
    ISO: Stable Isotope Fractionation (15% weight).
    """
    
    def __init__(self, weight: float = 0.15, config: Optional[Dict] = None):
        super().__init__(name="ISO", weight=weight, config=config)
        self.proxy_types = self.config.get("proxy_types", ["delta18O", "delta13C"])
    
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw ISO quality score."""
        scores = []
        
        if "delta18O" in data and len(data["delta18O"]) > 0:
            d18O = np.array(data["delta18O"])
            scores.append(self._score_d18O(d18O))
        
        if "delta13C" in data and len(data["delta13C"]) > 0:
            d13C = np.array(data["delta13C"])
            scores.append(self._score_d13C(d13C))
        
        if not scores:
            return 0.0
        
        return float(np.mean(scores))
    
    def _score_d18O(self, d18O: np.ndarray) -> float:
        if len(d18O) < 5:
            return 0.0
        
        in_range = np.sum((d18O > -5) & (d18O < 5)) / len(d18O)
        
        if len(d18O) > 5:
            diff = np.abs(np.diff(d18O))
            smoothness = 1.0 / (1.0 + np.mean(diff))
        else:
            smoothness = 0.5
        
        return float(np.clip(0.5 * in_range + 0.5 * smoothness, 0, 1))
    
    def _score_d13C(self, d13C: np.ndarray) -> float:
        if len(d13C) < 5:
            return 0.0
        
        in_range = np.sum((d13C > -5) & (d13C < 5)) / len(d13C)
        
        if len(d13C) > 5:
            diff = np.abs(np.diff(d13C))
            smoothness = 1.0 / (1.0 + np.mean(diff))
        else:
            smoothness = 0.5
        
        return float(np.clip(0.5 * in_range + 0.5 * smoothness, 0, 1))
    
    def normalize(self, value: float) -> float:
        return np.clip(value, 0, 1)
