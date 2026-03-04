"""Configuration management utilities."""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Union

# محاولة استيراد yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ConfigManager:
    """Manage configuration for STRATICA."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        Initialize config manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = {}
        if config_path:
            self.load(config_path)
    
    def load(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
        
        Returns:
            Loaded configuration dictionary
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        ext = config_path.suffix.lower()
        
        if ext in ['.yaml', '.yml']:
            if YAML_AVAILABLE:
                with open(config_path, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            else:
                raise ImportError("PyYAML is required to load YAML configs")
        
        elif ext == '.json':
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        
        else:
            raise ValueError(f"Unsupported config format: {ext}")
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration with dictionary."""
        self.config.update(updates)
    
    def save(self, filepath: Union[str, Path]):
        """Save configuration to file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        ext = filepath.suffix.lower()
        
        if ext in ['.yaml', '.yml']:
            if YAML_AVAILABLE:
                with open(filepath, 'w') as f:
                    yaml.dump(self.config, f)
            else:
                raise ImportError("PyYAML is required to save YAML configs")
        
        elif ext == '.json':
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
        
        else:
            raise ValueError(f"Unsupported output format: {ext}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self.config.copy()


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    
    Args:
        base: Base configuration
        override: Override configuration
    
    Returns:
        Merged configuration
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
    
    return result
