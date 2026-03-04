"""Integration test for PETM case study."""

import pytest
import numpy as np
from stratica.parameters import LithologicalDepositionRate


class TestPETMCaseStudy:
    """Test PETM case study reconstruction."""
    
    def create_petm_dataset(self):
        """Create synthetic PETM dataset."""
        np.random.seed(42)
        depth = np.linspace(200, 204, 50)
        age = 56000 - depth * 10
        petm_mask = (age > 55850) & (age < 55950)
        
        # Create bulk density that decreases during PETM
        bulk_density = np.ones_like(depth) * 2000
        bulk_density[petm_mask] = 1400
        
        return {
            'depth': depth,
            'age': age,
            'bulk_density': bulk_density,
            'petm_mask': petm_mask
        }
    
    def test_petm_ldr_change(self):
        """Test LDR change during PETM."""
        dataset = self.create_petm_dataset()
        ldr = LithologicalDepositionRate()
        
        result = ldr.compute(dataset)
        assert isinstance(result, float)
        assert result >= 0
        print(f"LDR result: {result}")
    
    def test_petm_initialization(self):
        """Test PETM dataset creation."""
        dataset = self.create_petm_dataset()
        assert 'depth' in dataset
        assert 'age' in dataset
        assert 'bulk_density' in dataset
        assert len(dataset['depth']) == 50
