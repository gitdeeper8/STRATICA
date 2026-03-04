"""Input/output utilities for STRATICA."""

import json
import numpy as np
from pathlib import Path
from typing import Dict, Any, Union, Optional

# محاولة استيراد yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# محاولة استيراد pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def load_data(filepath: Union[str, Path], **kwargs) -> Dict[str, Any]:
    """
    Load data from file.
    
    Supported formats: .csv, .json, .yaml, .yml, .npy
    
    Args:
        filepath: Path to data file
        **kwargs: Additional arguments passed to reader
    
    Returns:
        Dictionary with loaded data
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    ext = filepath.suffix.lower()
    
    if ext == '.csv':
        if PANDAS_AVAILABLE:
            df = pd.read_csv(filepath, **kwargs)
            return df.to_dict(orient='list')
        else:
            # Simple CSV parsing without pandas
            with open(filepath, 'r') as f:
                lines = f.readlines()
            if not lines:
                return {}
            headers = lines[0].strip().split(',')
            data = {h: [] for h in headers}
            for line in lines[1:]:
                if line.strip():
                    values = line.strip().split(',')
                    for h, v in zip(headers, values):
                        try:
                            data[h].append(float(v))
                        except ValueError:
                            data[h].append(v)
            return data
    
    elif ext == '.json':
        with open(filepath, 'r') as f:
            return json.load(f)
    
    elif ext in ['.yaml', '.yml']:
        if YAML_AVAILABLE:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        else:
            raise ImportError("PyYAML is required to load YAML files")
    
    elif ext == '.npy':
        data = np.load(filepath, **kwargs)
        return {'data': data.tolist()}
    
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def save_results(data: Dict[str, Any], filepath: Union[str, Path], **kwargs):
    """
    Save results to file.
    
    Args:
        data: Data to save
        filepath: Output file path
        **kwargs: Additional arguments passed to writer
    """
    filepath = Path(filepath)
    
    # Create parent directories if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    ext = filepath.suffix.lower()
    
    if ext == '.json':
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, **kwargs)
    
    elif ext in ['.yaml', '.yml']:
        if YAML_AVAILABLE:
            with open(filepath, 'w') as f:
                yaml.dump(data, f, **kwargs)
        else:
            raise ImportError("PyYAML is required to save YAML files")
    
    elif ext == '.csv':
        if PANDAS_AVAILABLE:
            # Convert to DataFrame if possible
            if all(isinstance(v, (list, np.ndarray)) for v in data.values()):
                df = pd.DataFrame(data)
                df.to_csv(filepath, index=False, **kwargs)
            else:
                raise ValueError("Data cannot be converted to CSV")
        else:
            # Simple CSV writing without pandas
            with open(filepath, 'w') as f:
                headers = list(data.keys())
                f.write(','.join(headers) + '\n')
                # Get max length
                max_len = max(len(v) for v in data.values() if isinstance(v, (list, np.ndarray)))
                for i in range(max_len):
                    row = []
                    for h in headers:
                        if i < len(data[h]):
                            row.append(str(data[h][i]))
                        else:
                            row.append('')
                    f.write(','.join(row) + '\n')
    
    elif ext == '.npy':
        if 'data' in data and isinstance(data['data'], (list, np.ndarray)):
            np.save(filepath, np.array(data['data']), **kwargs)
        else:
            raise ValueError("Data cannot be saved as .npy")
    
    else:
        raise ValueError(f"Unsupported output format: {ext}")


def read_config(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Read configuration file."""
    filepath = Path(filepath)
    
    if not filepath.exists():
        return {}
    
    ext = filepath.suffix.lower()
    
    if ext in ['.yaml', '.yml']:
        if YAML_AVAILABLE:
            with open(filepath, 'r') as f:
                return yaml.safe_load(f)
        else:
            raise ImportError("PyYAML is required to load YAML configs")
    elif ext == '.json':
        with open(filepath, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported config format: {ext}")
