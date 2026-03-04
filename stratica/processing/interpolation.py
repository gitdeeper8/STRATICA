"""Interpolation utilities for stratigraphic data."""

import numpy as np
from typing import Optional, Tuple, List, Dict, Callable, Union


class GapFiller:
    """Fill gaps in stratigraphic time series."""
    
    def __init__(self, method: str = 'linear', max_gap_size: Optional[float] = None):
        self.method = method
        self.max_gap_size = max_gap_size
    
    def fill_gaps(self, x: np.ndarray, y: np.ndarray, x_new: Optional[np.ndarray] = None) -> np.ndarray:
        """Fill gaps using numpy interpolation."""
        if x_new is None:
            x_new = x
        
        valid = ~np.isnan(y)
        if valid.sum() < 2:
            return np.full_like(x_new, np.nan)
        
        # Simple linear interpolation with numpy
        return np.interp(x_new, x[valid], y[valid], left=np.nan, right=np.nan)
    
    def fill_stratigraphic_column(self, depth: np.ndarray, properties: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Fill gaps in multiple properties."""
        filled = {}
        for name, values in properties.items():
            filled[name] = self.fill_gaps(depth, values, depth)
        return filled


class DepthAgeConverter:
    """Convert between depth and age domains."""
    
    def __init__(self, method: str = 'linear'):
        self.method = method
    
    def depth_to_age(self, depth: np.ndarray, age: np.ndarray, depth_new: np.ndarray) -> np.ndarray:
        """Convert depth to age using linear interpolation."""
        valid = ~(np.isnan(depth) | np.isnan(age))
        if valid.sum() < 2:
            return np.full_like(depth_new, np.nan)
        
        return np.interp(depth_new, depth[valid], age[valid], left=np.nan, right=np.nan)
    
    def age_to_depth(self, depth: np.ndarray, age: np.ndarray, age_new: np.ndarray) -> np.ndarray:
        """Convert age to depth using linear interpolation."""
        valid = ~(np.isnan(age) | np.isnan(depth))
        if valid.sum() < 2:
            return np.full_like(age_new, np.nan)
        
        return np.interp(age_new, age[valid], depth[valid], left=np.nan, right=np.nan)


def interpolate_depth(depth: np.ndarray, values: np.ndarray, resolution: float) -> Tuple[np.ndarray, np.ndarray]:
    """Interpolate values to uniform depth resolution."""
    depth_min = np.min(depth)
    depth_max = np.max(depth)
    depth_uniform = np.arange(depth_min, depth_max, resolution)
    
    valid = ~np.isnan(values)
    if valid.sum() < 2:
        return depth_uniform, np.full_like(depth_uniform, np.nan)
    
    values_uniform = np.interp(depth_uniform, depth[valid], values[valid], left=np.nan, right=np.nan)
    
    return depth_uniform, values_uniform


def smooth_stratigraphic(depth: np.ndarray, values: np.ndarray, window_length: int = 5) -> np.ndarray:
    """Simple moving average smoothing without scipy."""
    if len(values) < window_length:
        return values
    
    values_smooth = values.copy()
    valid = ~np.isnan(values)
    
    if valid.sum() < window_length:
        return values
    
    # Simple moving average
    kernel = np.ones(window_length) / window_length
    
    # Apply only to valid segments
    values_filled = values.copy()
    values_filled[~valid] = np.interp(depth[~valid], depth[valid], values[valid])
    
    # Convolve
    values_smooth = np.convolve(values_filled, kernel, mode='same')
    
    # Restore original valid points
    values_smooth[valid] = values[valid]
    
    return values_smooth
