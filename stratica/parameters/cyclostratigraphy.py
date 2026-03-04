"""CEC - Cyclostratigraphic Energy Cycle parameter."""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase


class CyclostratigraphicEnergyCycle(ParameterBase):
    """
    CEC: Cyclostratigraphic Energy Cycle (7% weight).
    """
    
    def __init__(self, weight: float = 0.07, config: Optional[Dict] = None):
        super().__init__(name="CEC", weight=weight, config=config)
        self.frequencies = [1/100, 1/41, 1/21]
    
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw CEC score."""
        proxy = np.array(data.get("proxy", []))
        
        if len(proxy) < 10:
            return 0.0
        
        return self._simple_spectral(proxy)
    
    def _simple_spectral(self, x: np.ndarray) -> float:
        """Simple spectral analysis."""
        x_detrend = x - np.mean(x)
        
        # Simple FFT
        fft = np.fft.rfft(x_detrend)
        power = np.abs(fft)**2
        
        if len(power) > 0 and np.max(power) > 0:
            power_norm = power / np.max(power)
            return float(np.mean(power_norm[:min(10, len(power_norm))]))
        
        return 0.3
    
    def _is_evenly_spaced(self, x: np.ndarray) -> bool:
        if len(x) < 3:
            return True
        dx = np.diff(x)
        return bool(np.std(dx) / (np.mean(dx) + 1e-10) < 0.01)
    
    def normalize(self, value: float) -> float:
        return np.clip(value, 0, 1)
