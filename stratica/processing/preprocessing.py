"""Data preprocessing utilities for STRATICA.

Handles:
- Loading raw stratigraphic data
- Cleaning and validation
- Outlier detection
- Missing data handling
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List, Union
from pathlib import Path
import warnings


class DataPreprocessor:
    """Preprocess stratigraphic data for analysis."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize preprocessor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.outlier_threshold = self.config.get('outlier_threshold', 3.0)
        self.max_gap_percent = self.config.get('max_gap_percent', 20)
    
    def load_data(
        self,
        filepath: Union[str, Path],
        filetype: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load data from file.
        
        Supported formats:
        - CSV (.csv)
        - Excel (.xlsx, .xls)
        - LAS (.las) - well log format
        - JSON (.json)
        
        Args:
            filepath: Path to data file
            filetype: Force file type (optional)
        
        Returns:
            DataFrame with loaded data
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Determine file type
        if filetype is None:
            ext = filepath.suffix.lower()
        else:
            ext = f".{filetype.lower()}"
        
        # Load based on extension
        if ext == '.csv':
            df = pd.read_csv(filepath)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(filepath)
        elif ext == '.las':
            df = self._load_las(filepath)
        elif ext == '.json':
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
        
        return df
    
    def _load_las(self, filepath: Path) -> pd.DataFrame:
        """Load LAS well log format."""
        # Simplified LAS reader
        # Full version would use lasio library
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Find ~A section (data)
        data_start = None
        for i, line in enumerate(lines):
            if line.strip().startswith('~A'):
                data_start = i + 1
                break
        
        if data_start is None:
            raise ValueError("No ~A section found in LAS file")
        
        # Parse data
        data_lines = lines[data_start:]
        data = []
        for line in data_lines:
            if line.strip() and not line.strip().startswith('#'):
                values = line.strip().split()
                try:
                    data.append([float(v) for v in values])
                except ValueError:
                    continue
        
        # Find column names from ~C section
        col_names = ['DEPT'] + [f'LOG_{i}' for i in range(1, len(data[0]))]
        
        return pd.DataFrame(data, columns=col_names)
    
    def clean_data(
        self,
        df: pd.DataFrame,
        required_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Clean and validate data.
        
        Steps:
        1. Remove duplicates
        2. Handle missing values
        3. Remove outliers
        4. Validate required columns
        
        Args:
            df: Input DataFrame
            required_columns: List of required column names
        
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Check required columns
        if required_columns:
            missing = [col for col in required_columns if col not in df_clean.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
        
        # Convert to numeric where possible
        for col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Remove outliers (if enough data)
        if len(df_clean) > 10:
            df_clean = self._remove_outliers(df_clean)
        
        # Sort by depth if available
        if 'depth' in df_clean.columns:
            df_clean = df_clean.sort_values('depth')
        elif 'DEPT' in df_clean.columns:
            df_clean = df_clean.sort_values('DEPT')
        
        return df_clean
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if col in ['depth', 'DEPT', 'age']:
                continue  # Don't remove outliers from position columns
            
            # Calculate IQR
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define bounds
            lower = Q1 - self.outlier_threshold * IQR
            upper = Q3 + self.outlier_threshold * IQR
            
            # Mark outliers as NaN
            df_clean.loc[~df_clean[col].between(lower, upper), col] = np.nan
        
        return df_clean
    
    def handle_missing(
        self,
        df: pd.DataFrame,
        method: str = 'interpolate',
        max_gap: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Handle missing values in data.
        
        Args:
            df: Input DataFrame
            method: 'interpolate', 'drop', 'fill_mean', 'fill_median'
            max_gap: Maximum gap size to interpolate (in points)
        
        Returns:
            DataFrame with missing values handled
        """
        df_filled = df.copy()
        
        if max_gap is None:
            max_gap = int(len(df) * self.max_gap_percent / 100)
        
        for col in df_filled.columns:
            if col in ['depth', 'DEPT', 'age']:
                continue
            
            # Count missing
            n_missing = df_filled[col].isna().sum()
            missing_percent = 100 * n_missing / len(df_filled)
            
            if missing_percent > self.max_gap_percent:
                warnings.warn(f"Column {col} has {missing_percent:.1f}% missing values")
            
            if method == 'interpolate':
                # Identify gaps
                mask = df_filled[col].isna()
                gap_starts = np.where(mask & ~mask.shift(1).fillna(False))[0]
                gap_ends = np.where(mask & ~mask.shift(-1).fillna(False))[0]
                
                for start, end in zip(gap_starts, gap_ends):
                    gap_size = end - start + 1
                    if gap_size <= max_gap:
                        # Interpolate small gaps
                        df_filled.loc[start:end, col] = np.nan
                        df_filled[col] = df_filled[col].interpolate(method='linear')
            
            elif method == 'drop':
                df_filled = df_filled.dropna(subset=[col])
            
            elif method == 'fill_mean':
                df_filled[col] = df_filled[col].fillna(df_filled[col].mean())
            
            elif method == 'fill_median':
                df_filled[col] = df_filled[col].fillna(df_filled[col].median())
        
        return df_filled
    
    def detect_outliers(
        self,
        df: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> Dict[str, np.ndarray]:
        """
        Detect outliers in data.
        
        Returns:
            Dictionary mapping column names to outlier masks
        """
        if columns is None:
            columns = [col for col in df.columns if col not in ['depth', 'DEPT', 'age']]
        
        outliers = {}
        
        for col in columns:
            if col not in df.columns:
                continue
            
            # Z-score method
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers[col] = z_scores > self.outlier_threshold
        
        return outliers
    
    def normalize_depth(
        self,
        df: pd.DataFrame,
        depth_col: str = 'depth',
        method: str = 'relative'
    ) -> pd.DataFrame:
        """
        Normalize depth values.
        
        Args:
            df: Input DataFrame
            depth_col: Name of depth column
            method: 'relative' (0-1), 'zscore', or None
        
        Returns:
            DataFrame with normalized depth
        """
        df_norm = df.copy()
        
        if depth_col not in df_norm.columns:
            return df_norm
        
        if method == 'relative':
            depth_min = df_norm[depth_col].min()
            depth_max = df_norm[depth_col].max()
            df_norm['depth_norm'] = (df_norm[depth_col] - depth_min) / (depth_max - depth_min)
        
        elif method == 'zscore':
            depth_mean = df_norm[depth_col].mean()
            depth_std = df_norm[depth_col].std()
            df_norm['depth_norm'] = (df_norm[depth_col] - depth_mean) / depth_std
        
        return df_norm
    
    def resample(
        self,
        df: pd.DataFrame,
        resolution: float,
        depth_col: str = 'depth',
        method: str = 'linear'
    ) -> pd.DataFrame:
        """
        Resample data to uniform depth resolution.
        
        Args:
            df: Input DataFrame
            resolution: Target resolution (e.g., 0.01 for 1 cm)
            depth_col: Name of depth column
            method: Interpolation method
        
        Returns:
            Resampled DataFrame
        """
        if depth_col not in df.columns:
            raise ValueError(f"Depth column '{depth_col}' not found")
        
        # Create uniform depth grid
        depth_min = df[depth_col].min()
        depth_max = df[depth_col].max()
        depth_uniform = np.arange(depth_min, depth_max, resolution)
        
        # Interpolate each column
        df_resampled = pd.DataFrame({'depth': depth_uniform})
        
        for col in df.columns:
            if col == depth_col:
                continue
            
            from scipy import interpolate
            
            # Remove NaN for interpolation
            valid = ~df[col].isna()
            if valid.sum() < 2:
                df_resampled[col] = np.nan
                continue
            
            f = interpolate.interp1d(
                df[depth_col][valid],
                df[col][valid],
                kind=method,
                bounds_error=False,
                fill_value='extrapolate'
            )
            
            df_resampled[col] = f(depth_uniform)
        
        return df_resampled
    
    def extract_petm_interval(
        self,
        df: pd.DataFrame,
        age_col: str = 'age',
        buffer_kyr: float = 100
    ) -> pd.DataFrame:
        """
        Extract PETM interval from data.
        
        PETM occurred at ~55.9 Ma with duration ~200 kyr.
        
        Args:
            df: Input DataFrame with age column
            age_col: Name of age column (in ka or Ma)
            buffer_kyr: Buffer around PETM in kyr
        
        Returns:
            DataFrame with PETM interval
        """
        if age_col not in df.columns:
            raise ValueError(f"Age column '{age_col}' not found")
        
        # Check age units (assume Ma if values are ~55)
        age_values = df[age_col].values
        if np.mean(age_values) > 10:  # Probably Ma
            petm_age = 55.9  # Ma
            buffer = buffer_kyr / 1000  # Convert to Ma
        else:  # Probably ka
            petm_age = 55900  # ka
            buffer = buffer_kyr
        
        # Extract interval
        mask = (df[age_col] >= petm_age - buffer) & (df[age_col] <= petm_age + buffer)
        
        return df[mask].copy()


def clean_data(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    """Convenience function for data cleaning."""
    preprocessor = DataPreprocessor(kwargs)
    return preprocessor.clean_data(df)


def load_stratigraphic_data(filepath: str, **kwargs) -> pd.DataFrame:
    """Convenience function for loading data."""
    preprocessor = DataPreprocessor(kwargs)
    return preprocessor.load_data(filepath)
