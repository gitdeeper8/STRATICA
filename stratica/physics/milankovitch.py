"""Milankovitch orbital forcing calculations."""

import numpy as np
from typing import Dict, Tuple, Optional


class MilankovitchForcing:
    """Simplified Milankovitch orbital cycle calculations."""
    
    def __init__(self):
        self.frequencies = {
            "eccentricity_long": 1/405,
            "eccentricity_short": 1/100,
            "obliquity": 1/41,
            "precession": 1/21,
        }
    
    def eccentricity(self, t_kyr: np.ndarray) -> np.ndarray:
        """Simplified eccentricity."""
        t = t_kyr * 1000
        e = 0.03 + 0.03 * np.sin(2 * np.pi * t / 100000)
        return e
    
    def obliquity(self, t_kyr: np.ndarray) -> np.ndarray:
        """Simplified obliquity."""
        t = t_kyr * 1000
        obl = 23.5 + 2.0 * np.sin(2 * np.pi * t / 41000)
        return obl
    
    def precession_index(self, t_kyr: np.ndarray) -> np.ndarray:
        """Simplified precession."""
        t = t_kyr * 1000
        p = np.sin(2 * np.pi * t / 21000)
        return p
    
    def target_curve(self, t_kyr: np.ndarray) -> np.ndarray:
        """Generate combined target curve."""
        e = self.eccentricity(t_kyr)
        e_norm = (e - np.mean(e)) / (np.std(e) + 1e-10)
        return e_norm
    
    def orbital_coherence(self, proxy: np.ndarray, t_proxy: np.ndarray) -> float:
        """Simple correlation with orbital target."""
        if len(proxy) < 10 or len(t_proxy) < 10:
            return 0.0
        
        target = self.target_curve(t_proxy[:len(proxy)])
        
        # Simple correlation coefficient
        proxy_detrend = proxy - np.mean(proxy)
        target_detrend = target - np.mean(target)
        
        corr = np.sum(proxy_detrend * target_detrend)
        corr /= np.sqrt(np.sum(proxy_detrend**2) * np.sum(target_detrend**2) + 1e-10)
        
        return float(np.abs(corr))
