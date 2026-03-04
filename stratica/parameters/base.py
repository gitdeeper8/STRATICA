"""Base class for all TCI parameters."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class ParameterBase(ABC):
    """Abstract base class for TCI parameters."""
    
    def __init__(self, name: str, weight: float, config: Optional[Dict] = None):
        self.name = name
        self.weight = weight
        self.config = config or {}
        self._value = None
        self._normalized_score = None
    
    @abstractmethod
    def compute(self, data: Dict[str, Any]) -> float:
        """Compute raw parameter value from data."""
        pass
    
    def normalize(self, value: float) -> float:
        """Normalize raw value to [0,1] range."""
        # Default implementation - override if needed
        return np.clip(value, 0, 1)
    
    @property
    def value(self) -> Optional[float]:
        return self._value
    
    @property
    def normalized_score(self) -> Optional[float]:
        return self._normalized_score
    
    def __call__(self, data: Dict[str, Any]) -> float:
        self._value = self.compute(data)
        self._normalized_score = self.normalize(self._value)
        return self._normalized_score
