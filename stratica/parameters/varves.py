"""VSI - Varve Sedimentary Integrity parameter."""

import numpy as np
from typing import Dict, Any, Optional, List, Tuple

from stratica.parameters.base import ParameterBase


class VarveSedimentaryIntegrity(ParameterBase):
    """
    VSI: Varve Sedimentary Integrity (8% weight).
    """
    
    def __init__(self, weight: float = 0.08, config: Optional[Dict] = None):
        super().__init__(name="VSI", weight=weight, config=config)
        self.min_varve_thickness = self.config.get("min_varve_thickness", 0.2)
        self.max_disruption_factor = self.config.get("max_disruption_factor", 3.0)
    
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw VSI score."""
        thicknesses = np.array(data.get("varve_thicknesses", []))
        
        if len(thicknesses) == 0:
            return 0.0
        
        N_total = len(thicknesses)
        N_disrupted = self._count_disrupted(thicknesses)
        
        if N_total > 0:
            vsi_raw = 1 - (N_disrupted / N_total)
        else:
            vsi_raw = 0.0
        
        return float(np.clip(vsi_raw, 0, 1))
    
    def _count_disrupted(self, thicknesses: np.ndarray) -> int:
        """Count disrupted varves based on thickness anomalies."""
        if len(thicknesses) < 5:
            return 0
        
        median = np.median(thicknesses)
        mad = np.median(np.abs(thicknesses - median))
        
        if mad > 0:
            # Flag varves with thickness > 3 * MAD from median
            threshold = median + 3 * mad
            n_disrupted = np.sum(thicknesses > threshold)
        else:
            n_disrupted = 0
        
        return int(n_disrupted)
    
    def count_varve_years(self, thicknesses: np.ndarray) -> int:
        return len(thicknesses)
    
    def annual_resolution_achieved(self, thicknesses: np.ndarray) -> bool:
        if len(thicknesses) == 0:
            return False
        return bool(np.any(thicknesses <= self.min_varve_thickness))
    
    def normalize(self, value: float) -> float:
        return np.clip(value, 0, 1)
