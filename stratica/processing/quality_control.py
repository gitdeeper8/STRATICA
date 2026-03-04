"""Quality control utilities for stratigraphic data.

Handles:
- Data validation
- Quality flagging
- Uncertainty estimation
- Benchmarking against reference datasets
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List, Union
from dataclasses import dataclass
import warnings


@dataclass
class QualityFlags:
    """Quality flags for stratigraphic data."""
    FLAG_GOOD = 0
    FLAG_SUSPECT = 1
    FLAG_POOR = 2
    FLAG_MISSING = 3
    FLAG_OUTLIER = 4
    
    descriptions = {
        0: "Good quality data",
        1: "Suspect data - use with caution",
        2: "Poor quality data - not recommended",
        3: "Missing data",
        4: "Statistical outlier"
    }


class QualityController:
    """Quality control for stratigraphic data."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize quality controller.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.flags = QualityFlags()
        
        # Default thresholds
        self.outlier_threshold = self.config.get('outlier_threshold', 3.0)
        self.min_data_points = self.config.get('min_data_points', 10)
        self.max_gap_percent = self.config.get('max_gap_percent', 20)
    
    def check_data_quality(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive quality check on DataFrame.
        
        Returns:
            Dictionary with quality metrics and flags
        """
        results = {
            'overall_quality': 'GOOD',
            'issues': [],
            'warnings': [],
            'column_quality': {},
            'flags': pd.DataFrame(index=df.index)
        }
        
        # Check required columns
        if required_columns:
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                results['issues'].append(f"Missing required columns: {missing}")
                results['overall_quality'] = 'POOR'
        
        # Check each column
        for col in df.columns:
            col_quality = self._check_column_quality(df[col])
            results['column_quality'][col] = col_quality
            results['flags'][col] = col_quality['flags']
            
            if col_quality['quality'] == 'POOR':
                results['overall_quality'] = 'POOR'
                results['issues'].append(f"Column {col}: {col_quality['message']}")
            elif col_quality['quality'] == 'SUSPECT':
                if results['overall_quality'] == 'GOOD':
                    results['overall_quality'] = 'SUSPECT'
                results['warnings'].append(f"Column {col}: {col_quality['message']}")
        
        # Overall statistics
        results['n_rows'] = len(df)
        results['n_columns'] = len(df.columns)
        results['total_missing'] = df.isna().sum().sum()
        results['missing_percent'] = 100 * results['total_missing'] / (len(df) * len(df.columns))
        
        if results['missing_percent'] > self.max_gap_percent:
            results['warnings'].append(f"High missing data: {results['missing_percent']:.1f}%")
        
        return results
    
    def _check_column_quality(self, series: pd.Series) -> Dict[str, Any]:
        """Check quality of a single column."""
        result = {
            'quality': 'GOOD',
            'flags': np.zeros(len(series), dtype=int),
            'message': '',
            'stats': {}
        }
        
        # Check for missing data
        missing = series.isna()
        n_missing = missing.sum()
        missing_pct = 100 * n_missing / len(series)
        
        result['stats']['n_missing'] = n_missing
        result['stats']['missing_percent'] = missing_pct
        result['flags'][missing] = self.flags.FLAG_MISSING
        
        if missing_pct > self.max_gap_percent:
            result['quality'] = 'POOR'
            result['message'] = f"High missing data: {missing_pct:.1f}%"
            return result
        
        # Check for outliers (if numeric)
        if np.issubdtype(series.dtype, np.number):
            valid = series[~missing]
            
            if len(valid) >= self.min_data_points:
                # Z-score method
                z_scores = np.abs((valid - valid.mean()) / valid.std())
                outliers = z_scores > self.outlier_threshold
                
                outlier_indices = valid.index[outliers]
                result['flags'][outlier_indices] = self.flags.FLAG_OUTLIER
                result['stats']['n_outliers'] = len(outlier_indices)
                
                if len(outlier_indices) > 0.1 * len(valid):
                    result['quality'] = 'SUSPECT'
                    result['message'] = f"High outlier count: {len(outlier_indices)}"
        
        return result
    
    def flag_outliers(
        self,
        values: np.ndarray,
        method: str = 'zscore',
        **kwargs
    ) -> np.ndarray:
        """
        Flag outlier points.
        
        Args:
            values: Input array
            method: 'zscore', 'iqr', 'mad'
            **kwargs: Method-specific parameters
        
        Returns:
            Boolean array (True = outlier)
        """
        values = np.asarray(values)
        valid = ~np.isnan(values)
        
        if valid.sum() < self.min_data_points:
            return np.zeros_like(values, dtype=bool)
        
        valid_values = values[valid]
        
        if method == 'zscore':
            threshold = kwargs.get('threshold', self.outlier_threshold)
            z_scores = np.abs((valid_values - np.mean(valid_values)) / np.std(valid_values))
            outlier_valid = z_scores > threshold
        
        elif method == 'iqr':
            threshold = kwargs.get('threshold', 1.5)
            q75, q25 = np.percentile(valid_values, [75, 25])
            iqr = q75 - q25
            lower = q25 - threshold * iqr
            upper = q75 + threshold * iqr
            outlier_valid = (valid_values < lower) | (valid_values > upper)
        
        elif method == 'mad':
            threshold = kwargs.get('threshold', 3.0)
            median = np.median(valid_values)
            mad = np.median(np.abs(valid_values - median))
            modified_z = 0.6745 * (valid_values - median) / (mad + 1e-10)
            outlier_valid = np.abs(modified_z) > threshold
        
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        # Map back to original array
        outliers = np.zeros_like(values, dtype=bool)
        outliers[valid] = outlier_valid
        
        return outliers
    
    def estimate_uncertainty(
        self,
        values: np.ndarray,
        method: str = 'moving_std',
        **kwargs
    ) -> np.ndarray:
        """
        Estimate measurement uncertainty.
        
        Args:
            values: Input array
            method: 'moving_std', 'replicate_error', 'theoretical'
            **kwargs: Method-specific parameters
        
        Returns:
            Uncertainty estimates (standard deviation)
        """
        values = np.asarray(values)
        uncertainty = np.full_like(values, np.nan)
        
        if method == 'moving_std':
            window = kwargs.get('window', min(11, len(values) // 10))
            if window % 2 == 0:
                window += 1
            
            if len(values) >= window:
                from scipy import signal
                
                # Rolling standard deviation
                valid = ~np.isnan(values)
                if valid.sum() >= window:
                    # Interpolate missing for calculation
                    from .interpolation import GapFiller
                    filler = GapFiller(method='linear')
                    values_filled = filler.fill_gaps(np.arange(len(values)), values)
                    
                    # Calculate moving std
                    weights = np.ones(window) / window
                    mean = signal.convolve(values_filled, weights, mode='same')
                    sq_mean = signal.convolve(values_filled**2, weights, mode='same')
                    moving_std = np.sqrt(np.maximum(0, sq_mean - mean**2))
                    
                    uncertainty = moving_std
        
        elif method == 'replicate_error':
            # If multiple measurements available
            if 'replicates' in kwargs:
                replicates = kwargs['replicates']
                uncertainty = np.std(replicates, axis=0)
        
        return uncertainty
    
    def validate_against_reference(
        self,
        values: np.ndarray,
        reference: np.ndarray,
        tolerance: float = 0.1
    ) -> Dict[str, float]:
        """
        Validate data against reference dataset.
        
        Args:
            values: Data to validate
            reference: Reference data
            tolerance: Relative tolerance for comparison
        
        Returns:
            Validation metrics
        """
        # Ensure same length
        min_len = min(len(values), len(reference))
        values = values[:min_len]
        reference = reference[:min_len]
        
        # Remove NaN
        valid = ~(np.isnan(values) | np.isnan(reference))
        if valid.sum() < 2:
            return {
                'rmse': np.nan,
                'mae': np.nan,
                'r2': np.nan,
                'within_tolerance': 0.0
            }
        
        values_valid = values[valid]
        ref_valid = reference[valid]
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((values_valid - ref_valid)**2))
        mae = np.mean(np.abs(values_valid - ref_valid))
        
        # R²
        ss_res = np.sum((values_valid - ref_valid)**2)
        ss_tot = np.sum((ref_valid - np.mean(ref_valid))**2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
        
        # Within tolerance
        rel_error = np.abs(values_valid - ref_valid) / (np.abs(ref_valid) + 1e-10)
        within_tol = np.mean(rel_error < tolerance)
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2': r2,
            'within_tolerance': within_tol
        }
    
    def generate_quality_report(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate HTML quality report.
        
        Args:
            df: Input DataFrame
            output_file: Path to save report
        
        Returns:
            HTML report as string
        """
        # Run quality check
        qc_results = self.check_data_quality(df)
        
        # Build HTML
        html = []
        html.append("<html><head><title>STRATICA Quality Report</title>")
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; margin: 20px; }")
        html.append(".good { color: green; }")
        html.append(".suspect { color: orange; }")
        html.append(".poor { color: red; }")
        html.append("table { border-collapse: collapse; width: 100%; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #f2f2f2; }")
        html.append("</style>")
        html.append("</head><body>")
        
        html.append("<h1>STRATICA Quality Control Report</h1>")
        
        # Overall quality
        quality_class = qc_results['overall_quality'].lower()
        html.append(f"<h2>Overall Quality: <span class='{quality_class}'>{qc_results['overall_quality']}</span></h2>")
        
        # Issues and warnings
        if qc_results['issues']:
            html.append("<h3>Issues:</h3><ul>")
            for issue in qc_results['issues']:
                html.append(f"<li class='poor'>{issue}</li>")
            html.append("</ul>")
        
        if qc_results['warnings']:
            html.append("<h3>Warnings:</h3><ul>")
            for warning in qc_results['warnings']:
                html.append(f"<li class='suspect'>{warning}</li>")
            html.append("</ul>")
        
        # Summary statistics
        html.append("<h3>Summary Statistics:</h3>")
        html.append("<table>")
        html.append("<tr><th>Metric</th><th>Value</th></tr>")
        html.append(f"<tr><td>Rows</td><td>{qc_results['n_rows']}</td></tr>")
        html.append(f"<tr><td>Columns</td><td>{qc_results['n_columns']}</td></tr>")
        html.append(f"<tr><td>Missing Data</td><td>{qc_results['total_missing']} ({qc_results['missing_percent']:.1f}%)</td></tr>")
        html.append("</table>")
        
        # Column quality
        html.append("<h3>Column Quality:</h3>")
        html.append("<table>")
        html.append("<tr><th>Column</th><th>Quality</th><th>Message</th><th>Missing</th><th>Outliers</th></tr>")
        
        for col, quality in qc_results['column_quality'].items():
            stats = quality.get('stats', {})
            html.append(f"<tr>")
            html.append(f"<td>{col}</td>")
            html.append(f"<td class='{quality['quality'].lower()}'>{quality['quality']}</td>")
            html.append(f"<td>{quality.get('message', '')}</td>")
            html.append(f"<td>{stats.get('missing_percent', 0):.1f}%</td>")
            html.append(f"<td>{stats.get('n_outliers', 0)}</td>")
            html.append(f"</tr>")
        
        html.append("</table>")
        html.append("</body></html>")
        
        report = "\n".join(html)
        
        # Save if requested
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
        
        return report


def qc_check(
    df: pd.DataFrame,
    **kwargs
) -> Dict[str, Any]:
    """Convenience function for quality control."""
    qc = QualityController(kwargs)
    return qc.check_data_quality(df)
