"""Unit tests for StratigraphicAnalyzer class."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

# استيراد مباشر بعد التثبيت
from stratica.core.analyzer import StratigraphicAnalyzer
from stratica.core.tci_index import TCIResults


class TestStratigraphicAnalyzer:
    """Test suite for StratigraphicAnalyzer."""
    
    def setup_method(self):
        """Setup before each test."""
        self.analyzer = StratigraphicAnalyzer()
    
    def test_initialization(self):
        """Test initialization."""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'parameters')
        assert len(self.analyzer.parameters) == 9
    
    def test_compute_tci(self):
        """Test TCI computation with mock data."""
        data = {'test': 'data'}
        results = self.analyzer.compute_tci(data)
        
        assert isinstance(results, TCIResults)
        assert hasattr(results, 'tci_composite')
        assert hasattr(results, 'classification')
        assert hasattr(results, 'parameters')
        
    def test_load_core_nonexistent(self):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.analyzer.load_core("nonexistent.csv")
