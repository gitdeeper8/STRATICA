# 🪨 STRATICA Installation Guide

## Quick Install

```bash
pip install stratica
```

Development Install

```bash
git clone https://gitlab.com/gitdeeper8/STRATICA.git
cd STRATICA
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Docker Install

```bash
docker pull gitlab.com/gitdeeper8/stratica:latest
docker run -p 8000:8000 -p 8501:8501 stratica:latest
```

Requirements

· Python 3.8–3.11
· 8GB RAM minimum (16GB recommended)
· 20GB disk space for datasets

Verify Installation

```bash
stratica doctor
stratica basins list
```

📚 Full documentation: https://stratica.readthedocs.io
