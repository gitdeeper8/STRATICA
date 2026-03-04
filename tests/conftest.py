"""Pytest configuration and fixtures for STRATICA tests."""

import pytest
import numpy as np
from pathlib import Path


@pytest.fixture
def sample_depth():
    """Sample depth array."""
    return np.linspace(0, 100, 50)


@pytest.fixture
def sample_age():
    """Sample age array (ka)."""
    return np.linspace(0, 1000, 50)


@pytest.fixture
def sample_d18O():
    """Sample δ¹⁸O data."""
    np.random.seed(42)
    depth = np.linspace(0, 100, 50)
    # Create realistic δ¹⁸O pattern
    trend = -0.02 * depth  # Decreasing with depth
    cycles = 0.5 * np.sin(2 * np.pi * depth / 20)
    noise = np.random.normal(0, 0.1, len(depth))
    return trend + cycles + noise


@pytest.fixture
def sample_d13C():
    """Sample δ¹³C data."""
    np.random.seed(43)
    depth = np.linspace(0, 100, 50)
    trend = 0.01 * depth
    cycles = 0.3 * np.cos(2 * np.pi * depth / 15)
    noise = np.random.normal(0, 0.05, len(depth))
    return trend + cycles + noise


@pytest.fixture
def sample_susceptibility():
    """Sample magnetic susceptibility data."""
    np.random.seed(44)
    depth = np.linspace(0, 100, 50)
    # Create reversal pattern
    base = 1e-3 * np.ones_like(depth)
    reversals = np.zeros_like(depth)
    reversals[10:20] = 2e-3
    reversals[30:40] = -1e-3
    noise = np.random.normal(0, 1e-4, len(depth))
    return base + reversals + noise


@pytest.fixture
def sample_porosity():
    """Sample porosity data following Athy's law."""
    depth = np.linspace(0, 100, 50)
    phi_0 = 0.5
    c = 5e-4
    porosity = phi_0 * np.exp(-c * depth)
    noise = np.random.normal(0, 0.02, len(depth))
    return porosity + noise


@pytest.fixture
def sample_pollen_counts():
    """Sample pollen count data."""
    return {
        'Quercus': 150,
        'Pinus': 200,
        'Betula': 80,
        'Artemisia': 30,
        'Chenopodiaceae': 20,
        'Polypodiaceae': 45,
        'Cyperaceae': 35
    }


@pytest.fixture
def sample_species_counts():
    """Sample microfossil species counts."""
    return {
        'Globigerinoides_ruber': 45,
        'Globigerinoides_sacculifer': 30,
        'Neogloboquadrina_pachyderma': 15,
        'Neogloboquadrina_dutertrei': 25,
        'Globorotalia_truncatulinoides': 10,
        'Globorotalia_menardii': 20,
        'Globigerina_bulloides': 35,
        'Orbulina_universa': 12
    }


@pytest.fixture
def sample_varve_thickness():
    """Sample varve thickness data (mm)."""
    np.random.seed(45)
    n_years = 100
    # Create annual cycle
    thickness = 1.0 + 0.5 * np.sin(2 * np.pi * np.arange(n_years) / 10)
    noise = np.random.gamma(2, 0.1, n_years)
    return thickness + noise


@pytest.fixture
def sample_tci_parameters():
    """Sample TCI parameter scores."""
    return {
        'LDR': 0.75,
        'ISO': 0.82,
        'MFA': 0.68,
        'MAG': 0.71,
        'GCH': 0.64,
        'PYS': 0.77,
        'VSI': 0.59,
        'TDM': 0.63,
        'CEC': 0.81
    }


@pytest.fixture
def sample_basin_data():
    """Sample basin data for testing."""
    return [
        {
            'name': 'Shatsky Rise',
            'location': 'North Pacific',
            'lat': 36.7,
            'lon': 158.5,
            'depth_m': 2387,
            'tci': 0.78
        },
        {
            'name': 'Walvis Ridge',
            'location': 'South Atlantic',
            'lat': -28.5,
            'lon': 2.3,
            'depth_m': 3000,
            'tci': 0.81
        },
        {
            'name': 'Demerara Rise',
            'location': 'Equatorial Atlantic',
            'lat': 9.0,
            'lon': -54.0,
            'depth_m': 3200,
            'tci': 0.74
        }
    ]


@pytest.fixture
def sample_petm_data():
    """Sample PETM data for testing."""
    age = np.linspace(55.5, 56.5, 200)  # Ma
    # Create CIE
    d13C = 2.0 * np.ones_like(age)
    cie_mask = (age > 55.85) & (age < 55.95)
    d13C[cie_mask] = np.linspace(2.0, -1.5, np.sum(cie_mask))
    d13C[cie_mask] = d13C[cie_mask] - 3.5
    
    return {
        'age': age.tolist(),
        'd13C': d13C.tolist(),
        'site': 'ODP 1209B',
        'location': 'Shatsky Rise'
    }


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def sample_csv_file(temp_data_dir):
    """Create sample CSV file."""
    import pandas as pd
    
    df = pd.DataFrame({
        'depth': np.linspace(0, 100, 50),
        'd18O': np.random.normal(0, 0.5, 50),
        'd13C': np.random.normal(1, 0.3, 50),
        'susceptibility': np.random.uniform(1e-4, 1e-3, 50)
    })
    
    filepath = temp_data_dir / "sample.csv"
    df.to_csv(filepath, index=False)
    return filepath


@pytest.fixture
def mock_analyzer():
    """Mock StratigraphicAnalyzer for testing."""
    from unittest.mock import Mock
    
    analyzer = Mock()
    analyzer.compute_tci.return_value = Mock(
        tci_composite=0.78,
        classification='good',
        parameters={'LDR': 0.75, 'ISO': 0.82}
    )
    return analyzer
