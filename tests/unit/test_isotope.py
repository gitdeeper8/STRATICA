"""Unit tests for IsotopeFractionation parameter."""

import pytest
import numpy as np
from stratica.parameters import IsotopeFractionation


class TestIsotopeFractionation:
    """Test suite for IsotopeFractionation."""
    
    def test_initialization(self):
        """Test initialization."""
        param = IsotopeFractionation()
        assert param is not None
        assert param.name is not None
    
    def test_compute(self):
        """Test compute method."""
        param = IsotopeFractionation()
        data = {'depth': [0, 1, 2], 'age': [0, 10, 20]}
        result = param.compute(data)
        assert isinstance(result, float)
        assert 0 <= result <= 1
    
    def test_normalize(self):
        """Test normalize method."""
        param = IsotopeFractionation()
        assert param.normalize(0.5) == 0.5
        assert param.normalize(1.2) == 1.0
        assert param.normalize(-0.1) == 0.0
