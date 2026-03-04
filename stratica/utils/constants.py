"""Physical constants and thresholds for STRATICA."""

import numpy as np

# ============================================================================
# TCI THRESHOLDS (from paper Section 2.1 and Appendix A)
# ============================================================================
TCI_THRESHOLDS = {
    "optimal": 0.88,
    "good": 0.72,
    "moderate": 0.55,
    "marginal": 0.38,
    "dysfunctional": 0.00
}
TCI_FUNCTIONAL_THRESHOLD = 0.62

# ============================================================================
# PARAMETER WEIGHTS (from paper Table in Section 2.2)
# ============================================================================
PARAMETER_WEIGHTS = {
    "LDR": 0.20,
    "ISO": 0.15,
    "MFA": 0.12,
    "MAG": 0.11,
    "GCH": 0.10,
    "PYS": 0.09,
    "VSI": 0.08,
    "TDM": 0.08,
    "CEC": 0.07,
}

# ============================================================================
# PHYSICAL CONSTANTS (from paper Section 3)
# ============================================================================

# Athy compaction law: phi(z) = phi_0 * exp(-c * z)
ATHY_COMPACTION = {
    "phi_0": 0.5,          # Surface porosity (typical for siliciclastics)
    "c": 5e-4,             # Compaction coefficient [m⁻¹]
}

# Paleotemperature equation coefficients
PALEOTEMPERATURE_EQUATION = {
    "a0": 16.9,
    "a1": -4.38,
    "a2": 0.10,
    "valid_range": [0, 30],
}

# Milankovitch orbital frequencies [kyr⁻¹]
MILANKOVITCH_FREQUENCIES = {
    "eccentricity_long": 1/405,
    "eccentricity_short": 1/100,
    "obliquity": 1/41,
    "precession": 1/21,
}

# Thermal diffusivity parameters
THERMAL_DIFFUSIVITY = {
    "kappa_sediment": 1e-6,
    "kappa_rock": 2e-6,
    "radiogenic_avg": 1e-6,
    "heat_capacity": 2.5e6,
}

# Geochemical anomaly thresholds
GEOchemical_ANOMALY = {
    "background_window": 500,
    "iridium_threshold": 5.0,
    "molybdenum_threshold": 3.0,
    "uranium_threshold": 3.0,
    "mercury_threshold": 3.0,
}

# ============================================================================
# VALIDATION METRICS (from paper Section 6.2)
# ============================================================================
VALIDATION_TARGETS = {
    "tci_accuracy": 96.2,
    "isotope_rmsd": 0.0018,
    "orbital_precision": 1200,
    "magnetostratigraphy_error": 3.4,
    "microfossil_accuracy": 93.4,
    "extinction_detection": 92.1,
}
