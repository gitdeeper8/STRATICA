"""Simple test to verify setup."""

import pytest
import sys
import stratica

def test_import_stratica():
    """Test importing STRATICA modules."""
    assert stratica.__version__ == "1.0.0"
    assert stratica.__author__ == "Samir Baladi"

def test_import_core():
    """Test importing core modules."""
    from stratica.core import StratigraphicAnalyzer, TCIIndex
    assert StratigraphicAnalyzer is not None
    assert TCIIndex is not None

def test_import_parameters():
    """Test importing parameters."""
    from stratica.parameters import LithologicalDepositionRate
    assert LithologicalDepositionRate is not None
