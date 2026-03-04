"""Unit tests for TCIIndex class."""

import pytest
import numpy as np

from stratica.core.tci_index import TCIIndex, TCIResults
from stratica.utils.constants import PARAMETER_WEIGHTS, TCI_THRESHOLDS


class TestTCIIndex:
    """Test suite for TCIIndex."""
    
    def setup_method(self):
        """Setup before each test."""
        self.tci = TCIIndex()
        self.sample_params = {
            'LDR': 0.8,
            'ISO': 0.7,
            'MFA': 0.6,
            'MAG': 0.5,
            'GCH': 0.4,
            'PYS': 0.3,
            'VSI': 0.2,
            'TDM': 0.1,
            'CEC': 0.0
        }
    
    def test_initialization(self):
        """Test initialization."""
        assert self.tci is not None
        assert len(self.tci.weights) == 9
    
    def test_compute(self):
        """Test TCI computation."""
        result = self.tci.compute(self.sample_params)
        assert 0 <= result <= 1
        
    def test_classify(self):
        """Test classification."""
        assert self.tci.classify(0.9) in ['optimal', 'good']
        assert self.tci.classify(0.5) in ['moderate', 'marginal']
