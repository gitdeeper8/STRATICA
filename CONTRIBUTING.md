# 🪨 CONTRIBUTING TO STRATICA

First off, thank you for considering contributing to STRATICA! We welcome contributions from geologists, paleoclimatologists, stratigraphers, geochemists, data scientists, software engineers, and anyone passionate about understanding Earth's deep-time climate history.

---

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

## Types of Contributions

### 🪨 Scientific Contributions
- New stratigraphic datasets (PANGAEA, IODP, NOAA Paleoclimate)
- Stable isotope measurements (δ¹⁸O, δ¹³C, Δ47)
- Microfossil assemblage data (foraminifera, nannofossils, palynomorphs)
- Magnetic susceptibility and magnetostratigraphy records
- Geochemical proxy data (trace elements, TOC, XRF)
- Cyclostratigraphy and orbital tuning solutions
- Radiometric age dates (U-Pb, Ar-Ar, ¹⁴C)

### 💻 Code Contributions
- TCI calculation engine improvements
- TL-PINN (Transformer-LSTM Physics-Informed Neural Network) enhancements
- Parameter module development
- Back-casting algorithms
- Dashboard and visualization tools
- API extensions

### 📊 Data Contributions
- IODP drill core datasets
- Ice core records (Antarctic, Greenland)
- Sedimentary basin stratigraphy
- Paleobotanical and palynological data
- Geomagnetic polarity time scale integration
- Modern analog calibration datasets

### 📝 Documentation Contributions
- Tutorials and examples
- API documentation
- Parameter explanations
- Case study write-ups
- Translation of documentation

---

## Getting Started

### Prerequisites
- **Python 3.8–3.11**
- **Git**
- **Basic knowledge of stratigraphy or paleoclimatology**

### Setup Development Environment

```bash
# Fork the repository, then clone
git clone https://gitlab.com/YOUR_USERNAME/STRATICA.git
cd STRATICA

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
pre-commit install
```

Verify Setup

```bash
# Run basic validation
python scripts/validate_environment.py

# Run tests
pytest tests/unit/ -v

# Check parameter correlations
python scripts/check_tci.py --expected 96.2
```

---

Development Workflow

1. Create an issue describing your proposed changes
2. Fork and branch:
   ```bash
   git checkout -b feature/your-feature-name
   git checkout -b fix/issue-description
   git checkout -b basin/new-basin-name
   ```
3. Make changes following our standards
4. Write/update tests
5. Run tests locally
6. Commit with clear messages
7. Push to your fork
8. Open a Merge Request

---

Coding Standards

Python

· Format: Black (line length 88)
· Imports: isort with black profile
· Type Hints: Required for all public functions
· Docstrings: Google style

Example Parameter Module

```python
"""LDR - Lithological Deposition Rate parameter."""

from typing import Optional
import numpy as np

from stratica.core import ParameterBase


class LithologicalDepositionRate(ParameterBase):
    """LDR: Lithological Deposition Rate.
    
    Measures sediment accumulation rate as a function of basin subsidence,
    sediment supply, and compaction history.
    
    Attributes:
        rho_b: Bulk density [kg/m³]
        m_dot: Mass flux [kg/m²/yr]
        phi: Porosity evolution with depth
    """
    
    def compute(self) -> float:
        """Compute normalized LDR score."""
        # Implementation using Athy compaction law:
        # phi(z) = phi_0 * exp(-c * z)
        pass
```

---

Testing Guidelines

Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── parameters/
│   │   ├── test_ldr.py
│   │   ├── test_iso.py
│   │   └── test_cec.py
├── integration/             # Integration tests
├── basins/                  # Basin-specific validation
└── fixtures/                # Test data
```

Running Tests

```bash
# All tests
pytest

# Parameter tests
pytest tests/unit/parameters/ -v

# With coverage
pytest --cov=stratica --cov-report=html
```

---

Data Contributions

New Basin Data

When adding data for a new sedimentary basin, include:

1. Basin metadata (location, tectonic setting, age range)
2. Stratigraphic column description
3. Stable isotope data (δ¹⁸O, δ¹³C) with depth/age
4. Microfossil assemblage counts
5. Magnetic susceptibility measurements
6. Geochemical proxy data (XRF, trace elements)
7. Age control points (biostratigraphy, magnetostratigraphy, radiometric)

Data Format Requirements

Parameter Format Min Samples
LDR .csv with depth, density, age 20 measurements
ISO .csv with δ¹⁸O, δ¹³C, depth 50 measurements
MFA .csv with species counts 30 samples
MAG .csv with susceptibility, depth 100 measurements
GCH .csv with element concentrations 30 samples
CEC .csv with depth/age series 200 data points

---

Sample Handling Ethics

Any contribution involving physical samples must:

1. Obtain permits - Document from relevant authorities for sample collection
2. Respect sample integrity - Follow IODP and PANGAEA handling protocols
3. Minimize destruction - Use non-destructive methods where possible
4. Proper storage - Ensure long-term preservation of samples
5. Data sharing - Deposit data in public repositories (PANGAEA, NOAA)

Contact: ethics@stratica.org

---

Adding New Parameters

If you propose a new parameter for TCI:

1. Literature review - Demonstrate scientific basis in peer-reviewed research
2. Physical independence - Show minimal correlation with existing parameters (<0.3)
3. Measurement protocol - Define clear methodology
4. Validation data - Provide dataset showing predictive power
5. Weight proposal - Suggest initial weight (<5% typically for new parameters)

---

Reporting Issues

Bug Reports

Include:

· Clear title and description
· Steps to reproduce
· Expected vs actual behavior
· Environment details
· Logs or screenshots

Feature Requests

Include:

· Use case description
· Expected behavior
· Scientific justification
· References to similar work

---

Contact

Purpose Contact
General inquiries gitdeeper@gmail.com
Code of Conduct conduct@stratica.org
Sample ethics ethics@stratica.org
Data contributions data@stratica.org

Repository: https://gitlab.com/gitdeeper8/STRATICA
Dashboard: https://stratica.netlify.app
DOI: 10.5281/zenodo.18851076

---

🪨 The Earth's stratigraphic column is a 4.5-billion-year journal written in rock. STRATICA decodes.

Last Updated: March 2026
