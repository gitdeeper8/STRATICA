"""Core plotting functions for STRATICA.

Generates:
- TCI profile plots
- Parameter breakdown charts
- Stratigraphic columns
- Isotope curves
- Time series analysis
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import warnings

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    warnings.warn("Seaborn not available. Using matplotlib only.")


class StratigraphyPlotter:
    """Plotting class for stratigraphic data."""
    
    def __init__(self, style: str = 'default', figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize plotter.
        
        Args:
            style: Plot style ('default', 'seaborn', 'publication')
            figsize: Default figure size
        """
        self.style = style
        self.figsize = figsize
        self.colors = {
            'tci': '#2E86AB',
            'ldr': '#A23B72',
            'iso': '#F18F01',
            'mfa': '#C73E1D',
            'mag': '#6A4E7D',
            'gch': '#3B8F5E',
            'pys': '#B6465F',
            'vsi': '#579C8A',
            'tdm': '#E59500',
            'cec': '#9A7D56'
        }
        
        # Set style
        self._set_style()
    
    def _set_style(self):
        """Set matplotlib style."""
        if self.style == 'seaborn' and SEABORN_AVAILABLE:
            sns.set_style("whitegrid")
            sns.set_context("notebook")
        elif self.style == 'publication':
            plt.style.use('default')
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.labelsize'] = 11
            plt.rcParams['axes.titlesize'] = 12
            plt.rcParams['legend.fontsize'] = 9
            plt.rcParams['figure.dpi'] = 300
            plt.rcParams['savefig.dpi'] = 300
    
    def plot_tci_profile(
        self,
        depth: np.ndarray,
        tci: np.ndarray,
        parameters: Optional[Dict[str, np.ndarray]] = None,
        thresholds: bool = True,
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot TCI profile with depth.
        
        Args:
            depth: Depth array [m]
            tci: TCI values
            parameters: Optional parameter values for subplots
            thresholds: Show TCI thresholds
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        if parameters:
            # Multiple subplots
            n_params = len(parameters)
            fig = plt.figure(figsize=(self.figsize[0], self.figsize[1] * (1 + n_params * 0.3)))
            gs = gridspec.GridSpec(1 + n_params, 1, height_ratios=[3] + [1] * n_params)
            
            # Main TCI plot
            ax0 = plt.subplot(gs[0])
            ax0.plot(tci, depth, 'k-', linewidth=2, color=self.colors['tci'])
            ax0.set_xlabel('TCI')
            ax0.set_ylabel('Depth [m]')
            ax0.invert_yaxis()
            
            # Add thresholds
            if thresholds:
                ax0.axvline(x=0.38, color='red', linestyle='--', alpha=0.5, label='Dysfunctional')
                ax0.axvline(x=0.55, color='orange', linestyle='--', alpha=0.5, label='Marginal')
                ax0.axvline(x=0.72, color='yellow', linestyle='--', alpha=0.5, label='Moderate')
                ax0.axvline(x=0.88, color='green', linestyle='--', alpha=0.5, label='Good')
                ax0.legend(loc='lower right')
            
            # Parameter subplots
            for i, (param_name, param_values) in enumerate(parameters.items()):
                ax = plt.subplot(gs[i + 1], sharey=ax0)
                color = self.colors.get(param_name.lower(), 'gray')
                ax.plot(param_values, depth, linewidth=1.5, color=color)
                ax.set_xlabel(param_name)
                ax.invert_yaxis()
            
            plt.tight_layout()
        
        else:
            # Single plot
            fig, ax = plt.subplots(figsize=self.figsize)
            ax.plot(tci, depth, 'k-', linewidth=2, color=self.colors['tci'])
            ax.set_xlabel('Temporal Climate Integrity Index (TCI)')
            ax.set_ylabel('Depth [m]')
            ax.invert_yaxis()
            ax.set_title('Stratigraphic TCI Profile')
            
            # Add thresholds
            if thresholds:
                ax.axvline(x=0.38, color='red', linestyle='--', alpha=0.5, label='Dysfunctional')
                ax.axvline(x=0.55, color='orange', linestyle='--', alpha=0.5, label='Marginal')
                ax.axvline(x=0.72, color='yellow', linestyle='--', alpha=0.5, label='Moderate')
                ax.axvline(x=0.88, color='green', linestyle='--', alpha=0.5, label='Good')
                ax.legend(loc='lower right')
            
            # Add functional threshold
            ax.axvline(x=0.62, color='blue', linestyle=':', alpha=0.7, label='Functional')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_parameter_breakdown(
        self,
        tci_value: float,
        parameter_scores: Dict[str, float],
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot pie/bar chart of parameter contributions.
        
        Args:
            tci_value: Composite TCI score
            parameter_scores: Dictionary of parameter scores
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        from stratica.utils.constants import PARAMETER_WEIGHTS
        
        # Calculate contributions
        contributions = {}
        for name, score in parameter_scores.items():
            weight = PARAMETER_WEIGHTS.get(name, 0)
            contributions[name] = weight * score
        
        # Sort by contribution
        sorted_items = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
        names = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]
        colors = [self.colors.get(name.lower(), 'gray') for name in names]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(self.figsize[0], self.figsize[1] // 2))
        
        # Bar chart
        bars = ax1.bar(range(len(names)), values, color=colors)
        ax1.set_xticks(range(len(names)))
        ax1.set_xticklabels(names, rotation=45, ha='right')
        ax1.set_ylabel('Contribution to TCI')
        ax1.set_title(f'Parameter Contributions (TCI = {tci_value:.3f})')
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=8)
        
        # Pie chart of weights
        weights = [PARAMETER_WEIGHTS.get(name, 0) for name in names]
        ax2.pie(weights, labels=names, colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Parameter Weights')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_stratigraphic_column(
        self,
        depth: np.ndarray,
        lithology: np.ndarray,
        properties: Optional[Dict[str, np.ndarray]] = None,
        age: Optional[np.ndarray] = None,
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot stratigraphic column with lithology and properties.
        
        Args:
            depth: Depth array
            lithology: Lithology codes or names
            properties: Additional properties to plot
            age: Age array for secondary axis
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        n_props = len(properties) if properties else 0
        
        # Create figure with subplots
        if n_props > 0:
            fig = plt.figure(figsize=(self.figsize[0] * (1 + n_props * 0.3), self.figsize[1]))
            gs = gridspec.GridSpec(1, 1 + n_props, width_ratios=[1] + [0.5] * n_props)
        else:
            fig, ax = plt.subplots(figsize=self.figsize)
            gs = gridspec.GridSpec(1, 1)
        
        # Main lithology column
        ax_lith = plt.subplot(gs[0])
        
        # Plot lithology as colored bars
        unique_lith = np.unique(lithology)
        lith_colors = plt.cm.tab10(np.linspace(0, 1, len(unique_lith)))
        lith_map = dict(zip(unique_lith, lith_colors))
        
        for i, (top, bottom) in enumerate(zip(depth[:-1], depth[1:])):
            lith = lithology[i]
            color = lith_map.get(lith, 'gray')
            ax_lith.barh(y=(top + bottom)/2, width=1, height=bottom-top,
                        left=0, color=color, edgecolor='black', linewidth=0.5)
        
        ax_lith.set_xlim(0, 1)
        ax_lith.set_xticks([])
        ax_lith.set_ylabel('Depth [m]')
        ax_lith.invert_yaxis()
        ax_lith.set_title('Lithology')
        
        # Add age axis if provided
        if age is not None:
            ax_age = ax_lith.twiny()
            ax_age.set_xlim(0, 1)
            ax_age.set_xticks([])
            ax_age.set_xlabel('Age [ka]')
            
            # Add age labels at key depths
            depth_ticks = np.linspace(depth.min(), depth.max(), 5)
            age_ticks = np.interp(depth_ticks, depth, age)
            ax_age.set_yticks(depth_ticks)
            ax_age.set_yticklabels([f'{a:.0f}' for a in age_ticks])
        
        # Property subplots
        if properties:
            for i, (prop_name, prop_values) in enumerate(properties.items()):
                ax_prop = plt.subplot(gs[i + 1], sharey=ax_lith)
                ax_prop.plot(prop_values, depth, 'k-', linewidth=1.5)
                ax_prop.set_xlabel(prop_name)
                ax_prop.invert_yaxis()
                ax_prop.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_isotope_curve(
        self,
        depth: np.ndarray,
        d18O: np.ndarray,
        d13C: Optional[np.ndarray] = None,
        temperature: Optional[np.ndarray] = None,
        age: Optional[np.ndarray] = None,
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot stable isotope curves.
        
        Args:
            depth: Depth array
            d18O: δ¹⁸O values
            d13C: δ¹³C values (optional)
            temperature: Reconstructed temperature (optional)
            age: Age array (optional)
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        # Determine number of subplots
        n_plots = 1
        if d13C is not None:
            n_plots += 1
        if temperature is not None:
            n_plots += 1
        
        fig, axes = plt.subplots(1, n_plots, figsize=(self.figsize[0], self.figsize[1]), sharey=True)
        
        if n_plots == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # δ¹⁸O plot
        ax = axes[plot_idx]
        ax.plot(d18O, depth, 'b-', linewidth=1.5, label='δ¹⁸O')
        ax.set_xlabel('δ¹⁸O (‰ VPDB)')
        ax.set_ylabel('Depth [m]')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3)
        plot_idx += 1
        
        # δ¹³C plot
        if d13C is not None:
            ax = axes[plot_idx]
            ax.plot(d13C, depth, 'g-', linewidth=1.5, label='δ¹³C')
            ax.set_xlabel('δ¹³C (‰ VPDB)')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
            plot_idx += 1
        
        # Temperature plot
        if temperature is not None:
            ax = axes[plot_idx]
            ax.plot(temperature, depth, 'r-', linewidth=1.5, label='Temperature')
            ax.set_xlabel('Temperature (°C)')
            ax.invert_yaxis()
            ax.grid(True, alpha=0.3)
        
        # Add age axis if provided
        if age is not None:
            for ax in axes:
                ax_age = ax.twiny()
                ax_age.set_xlim(ax.get_xlim())
                ax_age.set_xticks([])
            axes[0].set_xlabel('Age [ka]')
        
        plt.suptitle('Stable Isotope Stratigraphy')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_time_series(
        self,
        age: np.ndarray,
        values: Dict[str, np.ndarray],
        normalize: bool = False,
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot time series of multiple variables.
        
        Args:
            age: Age array
            values: Dictionary of time series
            normalize: Whether to normalize each series
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        n_series = len(values)
        
        fig, axes = plt.subplots(n_series, 1, figsize=(self.figsize[0], self.figsize[1] * n_series / 2),
                                 sharex=True)
        
        if n_series == 1:
            axes = [axes]
        
        for i, (name, series) in enumerate(values.items()):
            ax = axes[i]
            
            data = series.copy()
            if normalize and not np.all(np.isnan(data)):
                data = (data - np.nanmean(data)) / np.nanstd(data)
            
            color = self.colors.get(name.lower(), f'C{i}')
            ax.plot(age, data, color=color, linewidth=1.5)
            ax.set_ylabel(name)
            ax.grid(True, alpha=0.3)
            
            if i == n_series - 1:
                ax.set_xlabel('Age [ka]')
        
        plt.suptitle('Stratigraphic Time Series')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_correlation_matrix(
        self,
        data: Dict[str, np.ndarray],
        method: str = 'pearson',
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot correlation matrix of parameters.
        
        Args:
            data: Dictionary of parameter arrays
            method: Correlation method ('pearson', 'spearman')
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        # Create DataFrame
        import pandas as pd
        df = pd.DataFrame(data)
        
        # Calculate correlation
        if method == 'pearson':
            corr = df.corr()
        elif method == 'spearman':
            corr = df.corr(method='spearman')
        else:
            raise ValueError(f"Unknown correlation method: {method}")
        
        # Plot
        fig, ax = plt.subplots(figsize=(self.figsize[0], self.figsize[0]))
        
        if SEABORN_AVAILABLE:
            sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0,
                       square=True, ax=ax, cbar_kws={'label': 'Correlation'})
        else:
            im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha='right')
            ax.set_yticklabels(corr.columns)
            plt.colorbar(im, ax=ax, label='Correlation')
            
            # Add correlation values
            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    text = ax.text(j, i, f'{corr.iloc[i, j]:.2f}',
                                 ha='center', va='center')
        
        ax.set_title(f'{method.capitalize()} Correlation Matrix')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def plot_petm_event(
        self,
        age: np.ndarray,
        d13C: np.ndarray,
        tci: Optional[np.ndarray] = None,
        highlight_interval: Tuple[float, float] = (55.8, 56.0),
        save_path: Optional[str] = None,
        **kwargs
    ) -> plt.Figure:
        """
        Plot PETM event with carbon isotope excursion.
        
        Args:
            age: Age array [Ma]
            d13C: δ¹³C values
            tci: TCI values (optional)
            highlight_interval: PETM interval to highlight
            save_path: Path to save figure
        
        Returns:
            matplotlib Figure
        """
        if tci is not None:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(self.figsize[0], self.figsize[1]),
                                           sharex=True)
        else:
            fig, ax1 = plt.subplots(figsize=self.figsize)
        
        # δ¹³C plot
        ax1.plot(age, d13C, 'g-', linewidth=1.5)
        ax1.axvspan(highlight_interval[0], highlight_interval[1],
                   alpha=0.2, color='red', label='PETM')
        ax1.set_ylabel('δ¹³C (‰ VPDB)')
        ax1.invert_xaxis()
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # TCI plot
        if tci is not None:
            ax2.plot(age, tci, 'b-', linewidth=1.5)
            ax2.axvspan(highlight_interval[0], highlight_interval[1],
                       alpha=0.2, color='red')
            ax2.axhline(y=0.62, color='k', linestyle='--', alpha=0.5, label='Functional')
            ax2.set_ylabel('TCI')
            ax2.set_xlabel('Age (Ma)')
            ax2.invert_xaxis()
            ax2.grid(True, alpha=0.3)
            ax2.legend()
        else:
            ax1.set_xlabel('Age (Ma)')
        
        plt.suptitle('Paleocene-Eocene Thermal Maximum (PETM)')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig


# Convenience functions
def plot_tci_profile(*args, **kwargs):
    """Convenience function for TCI profile plot."""
    plotter = StratigraphyPlotter()
    return plotter.plot_tci_profile(*args, **kwargs)


def plot_parameter_breakdown(*args, **kwargs):
    """Convenience function for parameter breakdown plot."""
    plotter = StratigraphyPlotter()
    return plotter.plot_parameter_breakdown(*args, **kwargs)


def plot_stratigraphic_column(*args, **kwargs):
    """Convenience function for stratigraphic column plot."""
    plotter = StratigraphyPlotter()
    return plotter.plot_stratigraphic_column(*args, **kwargs)


def plot_isotope_curve(*args, **kwargs):
    """Convenience function for isotope curve plot."""
    plotter = StratigraphyPlotter()
    return plotter.plot_isotope_curve(*args, **kwargs)
