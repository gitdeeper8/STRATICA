"""Unit tests for LithologicalDepositionRate parameter."""

import pytest
import numpy as np
from stratica.parameters import LithologicalDepositionRate


class TestLithologicalDepositionRate:
    """Test suite for LithologicalDepositionRate."""
    
    def test_initialization(self):
        """Test initialization."""
        param = LithologicalDepositionRate()
        assert param is not None
        assert param.name == "LDR"
    
    def test_compute(self):
        """Test compute method with all required data."""
        param = LithologicalDepositionRate()
        data = {
            'depth': [0, 1, 2],
            'age': [0, 10, 20],
            'bulk_density': [2000, 2100, 2200]
        }
        result = param.compute(data)
        assert isinstance(result, float)
        assert result >= 0
    
    def test_compute_missing_bulk_density(self):
        """Test compute method with missing bulk density."""
        param = LithologicalDepositionRate()
        data = {'depth': [0, 1, 2], 'age': [0, 10, 20]}
        result = param.compute(data)
        assert result == 0.0
    
    def test_normalize(self):
        """Test normalize method."""
        param = LithologicalDepositionRate()
        # Test with tectonic_setting='passive_margin' (max_rate=0.5)
        assert param.normalize(0.25) == 0.5
        assert param.normalize(0.5) == 1.0
        assert param.normalize(1.0) == 1.0
        assert param.normalize(0.0) == 0.0
