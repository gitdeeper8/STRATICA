#!/usr/bin/env python3
"""
Generate API documentation for STRATICA.
This script creates markdown files from docstrings.
"""

import os
import inspect
import importlib
import pkgutil
from pathlib import Path

def generate_module_docs(module_name, output_dir):
    """Generate markdown documentation for a module."""
    try:
        module = importlib.import_module(module_name)
        output_path = Path(output_dir) / f"{module_name.replace('.', '/')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(f"# {module_name}\n\n")
            
            # Module docstring
            if module.__doc__:
                f.write(f"{module.__doc__}\n\n")
            
            # Classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module_name:
                    f.write(f"## {name}\n\n")
                    if obj.__doc__:
                        f.write(f"{obj.__doc__}\n\n")
                    
                    # Methods
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        if not method_name.startswith('_'):
                            f.write(f"### {method_name}\n\n")
                            if method.__doc__:
                                f.write(f"{method.__doc__}\n\n")
                            
                            # Signature
                            try:
                                sig = inspect.signature(method)
                                f.write(f"```python\n{method_name}{sig}\n```\n\n")
                            except:
                                pass
            
            # Functions
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if obj.__module__ == module_name and not name.startswith('_'):
                    f.write(f"## {name}\n\n")
                    if obj.__doc__:
                        f.write(f"{obj.__doc__}\n\n")
                    
                    try:
                        sig = inspect.signature(obj)
                        f.write(f"```python\n{name}{sig}\n```\n\n")
                    except:
                        pass
            
        print(f"✅ Generated {module_name}")
    except Exception as e:
        print(f"❌ Error generating {module_name}: {e}")

def main():
    """Generate all API documentation."""
    output_dir = "docs/api"
    
    # Clean output directory
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    # Modules to document
    modules = [
        'stratica.core',
        'stratica.core.analyzer',
        'stratica.core.tci_index',
        'stratica.parameters',
        'stratica.parameters.lithological',
        'stratica.parameters.isotope',
        'stratica.parameters.microfossil',
        'stratica.parameters.magnetic',
        'stratica.parameters.geochemistry',
        'stratica.parameters.palynology',
        'stratica.parameters.varves',
        'stratica.parameters.thermal',
        'stratica.parameters.cyclostratigraphy',
        'stratica.models',
        'stratica.models.pinn',
        'stratica.models.transformer_lstm',
        'stratica.models.microfossil_cnn',
        'stratica.models.backcast',
        'stratica.physics',
        'stratica.physics.sediment_transport',
        'stratica.physics.isotope_fractionation',
        'stratica.physics.milankovitch',
        'stratica.physics.compaction',
        'stratica.processing',
        'stratica.processing.preprocessing',
        'stratica.processing.normalization',
        'stratica.processing.interpolation',
        'stratica.processing.quality_control',
        'stratica.visualization',
        'stratica.visualization.plots',
        'stratica.visualization.dashboard',
        'stratica.visualization.themes',
        'stratica.utils',
        'stratica.utils.io',
        'stratica.utils.config',
        'stratica.utils.logging',
        'stratica.utils.constants',
        'stratica.utils.helpers',
    ]
    
    print("🚀 Generating API documentation...")
    for module in modules:
        generate_module_docs(module, output_dir)
    
    print("\n✅ API documentation generated successfully!")
    print(f"📁 Location: {output_dir}/")

if __name__ == "__main__":
    main()
