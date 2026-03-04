"""Integration tests for STRATICA full pipeline."""

import pytest
import numpy as np

from stratica.core import StratigraphicAnalyzer
from stratica.parameters import LithologicalDepositionRate


class TestFullPipeline:
    """Integration tests for complete STRATICA pipeline."""
    
    def create_test_dataset(self):
        """Create synthetic test dataset."""
        np.random.seed(42)
        depth = np.linspace(0, 100, 50)
        
        return {
            'depth': depth,
            'age': depth * 10,
            'd18O': 2.0 + 0.5 * np.sin(2 * np.pi * depth / 20),
            'bulk_density': 2000 * np.ones_like(depth)
        }
    
    def test_individual_parameters(self):
        """Test individual parameter computations."""
        dataset = self.create_test_dataset()
        
        ldr = LithologicalDepositionRate()
        result = ldr.compute(dataset)
        assert isinstance(result, float)
        assert result >= 0
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = StratigraphicAnalyzer()
        assert analyzer is not None
        assert len(analyzer.parameters) == 9
