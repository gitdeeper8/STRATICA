#!/usr/bin/env python3
"""
Generate API documentation for STRATICA.
This script creates markdown files from docstrings.
"""

import os
import sys
import inspect
import importlib
import subprocess
from pathlib import Path

# إضافة المسار الحالي إلى sys.path
sys.path.insert(0, os.path.abspath('.'))

def ensure_package_installed():
    """التأكد من تثبيت الحزمة في وضع التطوير"""
    try:
        import stratica
        print("✅ Package 'stratica' is already available")
        return True
    except ImportError:
        print("📦 Package 'stratica' not found. Installing in development mode...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], 
                         check=True, capture_output=True)
            print("✅ Package installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install package: {e}")
            return False

def safe_import(module_name):
    """محاولة استيراد الوحدة مع معالجة الأخطاء"""
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"⚠️ Warning: Could not import {module_name}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Warning: Error importing {module_name}: {e}")
        return None

def generate_module_docs(module_name, output_dir):
    """Generate markdown documentation for a module."""
    print(f"📄 Generating docs for {module_name}...")
    
    module = safe_import(module_name)
    if module is None:
        return
    
    try:
        output_path = Path(output_dir) / f"{module_name.replace('.', '/')}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {module_name}\n\n")
            
            # Module docstring
            if module.__doc__:
                f.write(f"{module.__doc__.strip()}\n\n")
            
            # Classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, '__module__') and obj.__module__ == module_name:
                    if name.startswith('_'):
                        continue
                    f.write(f"## {name}\n\n")
                    if obj.__doc__:
                        f.write(f"{obj.__doc__.strip()}\n\n")
                    
                    # Methods
                    for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                        if method_name.startswith('_'):
                            continue
                        f.write(f"### {method_name}\n\n")
                        if method.__doc__:
                            f.write(f"{method.__doc__.strip()}\n\n")
                        
                        # Signature
                        try:
                            sig = inspect.signature(method)
                            f.write(f"```python\n{method_name}{sig}\n```\n\n")
                        except:
                            pass
            
            # Functions
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if hasattr(obj, '__module__') and obj.__module__ == module_name:
                    if name.startswith('_'):
                        continue
                    f.write(f"## {name}\n\n")
                    if obj.__doc__:
                        f.write(f"{obj.__doc__.strip()}\n\n")
                    
                    try:
                        sig = inspect.signature(obj)
                        f.write(f"```python\n{name}{sig}\n```\n\n")
                    except:
                        pass
            
        print(f"✅ Generated {module_name}")
    except Exception as e:
        print(f"❌ Error writing {module_name}: {e}")

def main():
    """Generate all API documentation."""
    print("🚀 Starting API documentation generation...")
    
    # التأكد من تثبيت الحزمة أولاً
    if not ensure_package_installed():
        print("❌ Cannot proceed without stratica package")
        return
    
    output_dir = "docs/api"
    
    # Clean output directory
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
        print(f"🧹 Cleaned {output_dir}")
    
    # Core modules to document
    modules = [
        'stratica',
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
    
    success_count = 0
    fail_count = 0
    
    for module in modules:
        try:
            generate_module_docs(module, output_dir)
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to generate {module}: {e}")
            fail_count += 1
    
    print(f"\n✅ API documentation generated successfully!")
    print(f"   📁 Location: {output_dir}/")
    print(f"   📊 Summary: {success_count} modules succeeded, {fail_count} failed")

if __name__ == "__main__":
    main()
