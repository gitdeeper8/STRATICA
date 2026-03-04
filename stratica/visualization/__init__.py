"""Visualization and plotting utilities."""

from .plots import (
    plot_tci_profile,
    plot_parameter_breakdown,
    plot_stratigraphic_column,
    plot_isotope_curve
)
from .dashboard import DashboardGenerator, generate_dashboard
from .themes import set_theme, STRATICA_THEME

__all__ = [
    'plot_tci_profile',
    'plot_parameter_breakdown',
    'plot_stratigraphic_column',
    'plot_isotope_curve',
    'DashboardGenerator',
    'generate_dashboard',
    'set_theme',
    'STRATICA_THEME'
]
