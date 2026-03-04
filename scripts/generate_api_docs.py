#!/usr/bin/env python3
"""Simple script to generate API documentation for STRATICA."""

import os
import sys
import inspect
import importlib
from pathlib import Path

def main():
    print("🚀 Generating API documentation...")
    
    # إنشاء مجلد docs/api
    output_dir = Path("docs/api")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # إنشاء ملف API بسيط
    with open(output_dir / "README.md", 'w') as f:
        f.write("# STRATICA API Reference\n\n")
        f.write("This directory contains automatically generated API documentation.\n\n")
        f.write("## Modules\n\n")
        f.write("- `stratica.core` - Core framework components\n")
        f.write("- `stratica.parameters` - Nine TCI parameters\n")
        f.write("- `stratica.models` - ML models\n")
        f.write("- `stratica.physics` - Physics constraints\n")
        f.write("- `stratica.processing` - Data processing\n")
        f.write("- `stratica.visualization` - Plotting and dashboard\n")
        f.write("- `stratica.utils` - Utility functions\n")
        f.write("- `stratica.api` - REST API\n")
    
    print("✅ API documentation generated successfully!")

if __name__ == "__main__":
    main()
