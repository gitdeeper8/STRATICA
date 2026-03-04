"""Parameter normalization utilities."""

import numpy as np
from typing import Dict, Any, Optional, Callable, Union


class ParameterNormalizer:
    """Normalize raw parameter values to [0,1] range."""
    
    def __init__(self, method: str = 'minmax'):
        self.method = method
        self.normalizers = {
            'minmax': self._minmax_normalize,
            'zscore': self._zscore_normalize,
            'robust': self._robust_normalize,
        }
    
    def normalize(self, values: np.ndarray, method: Optional[str] = None, **kwargs) -> np.ndarray:
        """Normalize values to [0,1]."""
        if method is None:
            method = self.method
        
        if method in self.normalizers:
            normalized = self.normalizers[method](values, **kwargs)
        else:
            raise ValueError(f"Unknown normalization method: {method}")
        
        return np.clip(normalized, 0, 1)
    
    def _minmax_normalize(self, values: np.ndarray, min_val: Optional[float] = None, max_val: Optional[float] = None) -> np.ndarray:
        """Min-max normalization to [0,1]."""
        values = np.asarray(values)
        
        if min_val is None:
            min_val = np.min(values)
        if max_val is None:
            max_val = np.max(values)
        
        if max_val - min_val == 0:
            return np.zeros_like(values)
        
        return (values - min_val) / (max_val - min_val)
    
    def _zscore_normalize(self, values: np.ndarray) -> np.ndarray:
        """Z-score normalization then map to [0,1] using logistic function."""
        values = np.asarray(values)
        
        if len(values) < 2:
            return np.zeros_like(values)
        
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return np.zeros_like(values)
        
        z_scores = (values - mean) / std
        
        # Logistic function maps (-∞, ∞) to (0, 1)
        return 1 / (1 + np.exp(-z_scores))
    
    def _robust_normalize(self, values: np.ndarray) -> np.ndarray:
        """Robust normalization using median and IQR."""
        values = np.asarray(values)
        
        if len(values) < 4:
            return np.zeros_like(values)
        
        median = np.median(values)
        q75, q25 = np.percentile(values, [75, 25])
        iqr = q75 - q25
        
        if iqr == 0:
            return np.zeros_like(values)
        
        robust_scores = (values - median) / iqr
        robust_scores = np.clip(robust_scores, -3, 3)
        return (robust_scores + 3) / 6


class LDRNormalizer(ParameterNormalizer):
    """Specialized normalizer for Lithological Deposition Rate."""
    
    def __init__(self, tectonic_setting: str = 'passive_margin'):
        super().__init__(method='minmax')
        self.max_rates = {
            'passive_margin': 0.5,
            'active_margin': 2.0,
            'intracratonic': 0.2,
            'foreland_basin': 1.0,
            'rift_basin': 1.5,
            'deep_sea': 0.1,
        }
        self.max_rate = self.max_rates.get(tectonic_setting, 0.5)
    
    def normalize(self, values: np.ndarray, **kwargs) -> np.ndarray:
        values = np.asarray(values)
        return np.clip(values / self.max_rate, 0, 1)


class ISONormalizer(ParameterNormalizer):
    """Specialized normalizer for Stable Isotopes."""
    
    def normalize_d18O(self, values: np.ndarray) -> np.ndarray:
        return (np.clip(values, -5, 5) + 5) / 10
    
    def normalize_d13C(self, values: np.ndarray) -> np.ndarray:
        return (np.clip(values, -5, 5) + 5) / 10


class PYSNormalizer(ParameterNormalizer):
    """Specialized normalizer for Palynology."""
    
    def __init__(self, alpha: float = 0.55):
        super().__init__(method='minmax')
        self.alpha = alpha
    
    def normalize_pollen(self, concentration: float, diversity: float, max_concentration: float = 100000) -> float:
        conc_norm = min(1.0, concentration / max_concentration)
        return self.alpha * conc_norm + (1 - self.alpha) * diversity


class VSINormalizer(ParameterNormalizer):
    """Specialized normalizer for Varve Integrity."""
    
    def normalize_varves(self, n_disrupted: int, n_total: int, thickness_factor: float = 1.0) -> float:
        if n_total == 0:
            return 0.0
        return max(0, 1 - (n_disrupted / n_total) * thickness_factor)


def normalize_parameter(values: np.ndarray, param_name: str, method: str = 'auto', **kwargs) -> np.ndarray:
    """Convenience function for parameter normalization."""
    if param_name.upper() == 'LDR':
        normalizer = LDRNormalizer(**kwargs)
    elif param_name.upper() == 'ISO':
        normalizer = ISONormalizer()
    elif param_name.upper() == 'PYS':
        normalizer = PYSNormalizer(**kwargs)
    elif param_name.upper() == 'VSI':
        normalizer = VSINormalizer()
    else:
        normalizer = ParameterNormalizer(method=method)
    
    return normalizer.normalize(values, **kwargs)
