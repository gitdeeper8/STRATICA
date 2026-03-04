"""MAG - Magnetic Susceptibility parameter."""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase


class MagneticSusceptibility(ParameterBase):
    """
    MAG: Magnetic Susceptibility (11% weight).
    """
    
    def __init__(self, weight: float = 0.11, config: Optional[Dict] = None):
        super().__init__(name="MAG", weight=weight, config=config)
    
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw MAG quality score."""
        sus = np.array(data.get("susceptibility", []))
        
        if len(sus) < 5:
            return 0.0
        
        # Simple quality score
        if np.std(sus) > 0:
            quality = np.std(sus) / (np.mean(np.abs(sus)) + 1e-10)
            return float(np.clip(quality / 2, 0, 1))
        
        return 0.0
    
    def _signal_quality(self, sus: np.ndarray) -> float:
        if len(sus) < 5:
            return 0.0
        
        signal_var = np.var(sus)
        if len(sus) > 1:
            noise_var = np.var(np.diff(sus)) / 2
        else:
            noise_var = signal_var
        
        snr = signal_var / (noise_var + 1e-10)
        return float(np.clip(snr / 10, 0, 1))
    
    def normalize(self, value: float) -> float:
        return np.clip(value, 0, 1)
