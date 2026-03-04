"""LDR - Lithological Deposition Rate parameter."""

import numpy as np
from typing import Dict, Any, Optional

from stratica.parameters.base import ParameterBase


class LithologicalDepositionRate(ParameterBase):
    """
    LDR: Lithological Deposition Rate (20% weight).
    """
    
    def __init__(self, weight: float = 0.20, config: Optional[Dict] = None):
        super().__init__(name="LDR", weight=weight, config=config)
        self.phi_0 = self.config.get("phi_0", 0.5)
        self.c = self.config.get("c", 5e-4)
        self.rho_g = self.config.get("grain_density", 2650)
    
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw LDR value."""
        depth = np.array(data.get("depth", []))
        bulk_density = np.array(data.get("bulk_density", []))
        age = np.array(data.get("age", []))
        
        if len(depth) < 2:
            return 0.0
        
        # If we have both age and bulk density
        if len(age) == len(depth) and len(age) >= 2 and len(bulk_density) == len(depth) and len(bulk_density) >= 2:
            # Sort by depth
            sort_idx = np.argsort(depth)
            depth_sorted = depth[sort_idx]
            bulk_density_sorted = bulk_density[sort_idx]
            age_sorted = age[sort_idx]
            
            # Calculate sedimentation rate
            dz = np.diff(depth_sorted)
            dt = np.diff(age_sorted) * 1000  # ka to years
            if np.all(dt > 0):
                rates = dz / dt  # m/yr
                mean_rate = np.mean(rates) * 1000  # m/kyr
                return float(mean_rate)
        
        return 0.0
    
    def normalize(self, value: float) -> float:
        """Normalize raw LDR to [0,1]."""
        # Get tectonic setting from config or use default
        setting = self.config.get("tectonic_setting", "passive_margin")
        
        max_rates = {
            "passive_margin": 0.5,
            "active_margin": 2.0,
            "intracratonic": 0.2,
            "foreland_basin": 1.0,
            "rift_basin": 1.5,
            "deep_sea": 0.1,
        }
        max_rate = max_rates.get(setting, 0.5)
        
        return np.clip(value / max_rate, 0, 1)
    
    def athy_porosity(self, depth: float) -> float:
        """Calculate porosity at depth using Athy's law."""
        return self.phi_0 * np.exp(-self.c * depth)
