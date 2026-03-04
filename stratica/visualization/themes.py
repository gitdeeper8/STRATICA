"""Plot themes and styling for STRATICA."""

import matplotlib.pyplot as plt
from typing import Dict, Any, Optional

# STRATICA default theme
STRATICA_THEME = {
    'figure.facecolor': 'white',
    'axes.facecolor': '#f8f9fa',
    'axes.edgecolor': '#2c3e50',
    'axes.labelcolor': '#2c3e50',
    'axes.titlecolor': '#2c3e50',
    'xtick.color': '#2c3e50',
    'ytick.color': '#2c3e50',
    'grid.color': '#dee2e6',
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'legend.frameon': True,
    'legend.fancybox': True,
    'legend.shadow': False,
    'figure.dpi': 100,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight'
}

# Publication theme for journals
PUBLICATION_THEME = {
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.labelcolor': 'black',
    'axes.titlecolor': 'black',
    'xtick.color': 'black',
    'ytick.color': 'black',
    'grid.color': '#cccccc',
    'grid.linestyle': ':',
    'grid.alpha': 0.5,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'axes.labelsize': 10,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 8,
    'legend.frameon': False,
    'figure.dpi': 300,
    'savefig.dpi': 600,
    'savefig.bbox': 'tight',
    'savefig.format': 'pdf'
}

# Dark theme for presentations
DARK_THEME = {
    'figure.facecolor': '#2d2d2d',
    'axes.facecolor': '#3d3d3d',
    'axes.edgecolor': '#cccccc',
    'axes.labelcolor': '#ffffff',
    'axes.titlecolor': '#ffffff',
    'xtick.color': '#cccccc',
    'ytick.color': '#cccccc',
    'grid.color': '#555555',
    'grid.linestyle': '--',
    'grid.alpha': 0.5,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'legend.frameon': True,
    'legend.facecolor': '#3d3d3d',
    'legend.edgecolor': '#cccccc',
    'figure.dpi': 100,
    'savefig.dpi': 300
}


def set_theme(theme: str = 'stratica', **kwargs):
    """
    Set matplotlib theme for STRATICA plots.
    
    Args:
        theme: 'stratica', 'publication', 'dark', or custom dict
        **kwargs: Additional theme parameters to override
    """
    if theme == 'stratica':
        theme_dict = STRATICA_THEME.copy()
    elif theme == 'publication':
        theme_dict = PUBLICATION_THEME.copy()
    elif theme == 'dark':
        theme_dict = DARK_THEME.copy()
    elif isinstance(theme, dict):
        theme_dict = theme.copy()
    else:
        raise ValueError(f"Unknown theme: {theme}")
    
    # Override with kwargs
    theme_dict.update(kwargs)
    
    # Apply to matplotlib
    plt.rcParams.update(theme_dict)


def get_color_palette(name: str = 'stratica') -> Dict[str, str]:
    """
    Get color palette for STRATICA parameters.
    
    Args:
        name: Palette name ('stratica', 'viridis', 'plasma')
    
    Returns:
        Dictionary mapping parameter names to colors
    """
    if name == 'stratica':
        return {
            'LDR': '#A23B72',
            'ISO': '#F18F01',
            'MFA': '#C73E1D',
            'MAG': '#6A4E7D',
            'GCH': '#3B8F5E',
            'PYS': '#B6465F',
            'VSI': '#579C8A',
            'TDM': '#E59500',
            'CEC': '#9A7D56',
            'TCI': '#2E86AB'
        }
    elif name == 'viridis':
        import matplotlib.cm as cm
        import matplotlib.colors as mcolors
        
        cmap = cm.viridis
        params = ['LDR', 'ISO', 'MFA', 'MAG', 'GCH', 'PYS', 'VSI', 'TDM', 'CEC', 'TCI']
        colors = [mcolors.rgb2hex(cmap(i / (len(params) - 1))) for i in range(len(params))]
        
        return dict(zip(params, colors))
    else:
        # Default
        return {
            'LDR': '#1f77b4',
            'ISO': '#ff7f0e',
            'MFA': '#2ca02c',
            'MAG': '#d62728',
            'GCH': '#9467bd',
            'PYS': '#8c564b',
            'VSI': '#e377c2',
            'TDM': '#7f7f7f',
            'CEC': '#bcbd22',
            'TCI': '#17becf'
        }


def save_figure(fig, filename: str, **kwargs):
    """
    Save figure with optimal settings.
    
    Args:
        fig: matplotlib Figure
        filename: Output filename (extension determines format)
        **kwargs: Additional savefig arguments
    """
    # Determine format from extension
    if filename.endswith('.pdf'):
        kwargs.setdefault('format', 'pdf')
    elif filename.endswith('.png'):
        kwargs.setdefault('format', 'png')
        kwargs.setdefault('dpi', 300)
    elif filename.endswith('.svg'):
        kwargs.setdefault('format', 'svg')
    elif filename.endswith('.eps'):
        kwargs.setdefault('format', 'eps')
    
    # Default settings
    kwargs.setdefault('bbox_inches', 'tight')
    kwargs.setdefault('pad_inches', 0.05)
    
    fig.savefig(filename, **kwargs)
