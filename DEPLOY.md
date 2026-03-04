# 🪨 STRATICA DEPLOYMENT GUIDE

This guide covers deployment options for the STRATICA framework, including the live dashboard, API services, documentation, and data repositories.

---

## Quick Deployments

### Netlify (Dashboard)

The STRATICA interactive dashboard is pre-configured for Netlify deployment.

#### Automatic Deployment

1. Connect your Git repository to Netlify
2. Use these settings:
   - Build command: `cd dashboard && npm run build` (if using Node) or leave empty
   - Publish directory: `dashboard/dist` or `dashboard`
   - Environment variables: none required

3. Or use the `netlify.toml` configuration:

```toml
[build]
  publish = "dashboard"

[build.environment]
  PYTHON_VERSION = "3.11"

[[redirects]]
  from = "/api/*"
  to = "https://stratica.netlify.app/api/:splat"
  status = 200
  force = true

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
```

Manual Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dashboard
```

Live dashboard: https://stratica.netlify.app
API endpoint: https://stratica.netlify.app/api

---

ReadTheDocs (Documentation)

Deploy technical documentation to ReadTheDocs.

Configuration

1. Connect your Git repository to readthedocs.org
2. Use the .readthedocs.yaml configuration in this repository
3. Build documentation automatically on push

Documentation: https://stratica.readthedocs.io

---

PyPI (Python Package)

Deploy the core STRATICA package to PyPI.

Preparation

```bash
# Install build tools
pip install build twine

# Update version in setup.py/pyproject.toml
# Version: 1.0.0

# Create distribution files
python -m build
```

Upload to PyPI

```bash
# Upload to production PyPI
twine upload dist/*

# Install
pip install stratica
```

PyPI package: https://pypi.org/project/stratica

---

Docker Deployment

Build Image

```dockerfile
# Dockerfile
FROM python:3.10-slim

LABEL maintainer="gitdeeper@gmail.com"
LABEL version="1.0.0"
LABEL description="STRATICA - Stratigraphic Pattern Recognition Framework"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STRATICA_HOME=/opt/stratica \
    STRATICA_CONFIG=/etc/stratica/config.yaml

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 -s /bin/bash stratica && \
    mkdir -p /opt/stratica && \
    mkdir -p /etc/stratica && \
    mkdir -p /data/sedimentary && \
    mkdir -p /data/isotope && \
    mkdir -p /data/results && \
    chown -R stratica:stratica /opt/stratica /etc/stratica /data

USER stratica
WORKDIR /opt/stratica

COPY --chown=stratica:stratica requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=stratica:stratica . .

RUN pip install --user -e .

EXPOSE 8000 8501

CMD ["stratica", "serve", "--all"]
```

Build and Run

```bash
# Build image
docker build -t stratica:1.0.0 .

# Run container
docker run -d \
  --name stratica-prod \
  -p 8000:8000 \
  -p 8501:8501 \
  -v /host/data:/data \
  -v /host/config:/etc/stratica \
  -e STRATICA_CONFIG=/etc/stratica/config.yaml \
  --restart unless-stopped \
  stratica:1.0.0
```

---

Configuration

Production Configuration

```yaml
# config/stratica.prod.yaml
# STRATICA Production Configuration

version: 1.0
environment: production

server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 120

database:
  host: postgres
  port: 5432
  name: stratica
  user: stratica_user
  password: ${DB_PASSWORD}
  pool_size: 20

monitoring:
  metrics_enabled: true
  metrics_port: 9090
  tci_update_interval: 60  # seconds

security:
  jwt_secret: ${JWT_SECRET}
  jwt_expiry_hours: 24
  rate_limit: 100/minute
  cors_origins:
    - https://stratica.netlify.app
    - https://stratica.readthedocs.io

api:
  public_url: https://stratica.netlify.app/api
  docs_url: https://stratica.readthedocs.io/api

external_apis:
  pangaea:
    url: https://ws.pangaea.de
    api_key: ${PANGAEA_API_KEY}
    endpoints:
      search: /search
      download: /download
  noaa_paleo:
    url: https://www.ncei.noaa.gov/access/paleo
    api_key: ${NOAA_PALEOCLIMATE_KEY}
    endpoints:
      search: /search
      data: /data
  iodp:
    url: https://web.iodp.tamu.edu
    token: ${IODP_ACCESS_TOKEN}
    endpoints:
      core: /core
      data: /data

data:
  upload_dir: /data/uploads
  max_file_size: 2GB
  allowed_formats:
    - .csv
    - .xlsx
    - .las
    - .npy
    - .h5
    - .json
```

---

Backup & Recovery

Automated Backup Script

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
pg_dump -h postgres -U stratica_user stratica | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Stratigraphic data backup
tar -czf $BACKUP_DIR/sedimentary_data_$DATE.tar.gz /data/sedimentary

# Isotope data backup
tar -czf $BACKUP_DIR/isotope_data_$DATE.tar.gz /data/isotope

# Configuration backup
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /etc/stratica

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Cron Setup

```bash
# Daily backup at 2 AM
0 2 * * * /usr/local/bin/backup.sh
```

---

Monitoring

Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'stratica'
    static_configs:
      - targets: ['api:8000', 'dashboard:8501']
    metrics_path: /metrics
    scrape_interval: 15s
```

Grafana Dashboard

Import the STRATICA dashboard template to visualize:

· TCI scores across 47 basins
· δ¹⁸O and δ¹³C time series
· Milankovitch cycle detection
· Geomagnetic reversal patterns
· Geochemical anomaly maps
· Extinction precursor alerts
· System health metrics

---

Quick Reference

```bash
# Netlify Dashboard
https://stratica.netlify.app
https://stratica.netlify.app/api

# PyPI Package
pip install stratica

# Docker
docker pull gitlab.com/gitdeeper8/stratica:latest

# Documentation
https://stratica.readthedocs.io

# Source Code
https://gitlab.com/gitdeeper8/STRATICA
https://github.com/gitdeeper8/STRATICA

# Data Repositories
https://pangaea.de
https://www.ncei.noaa.gov/products/paleoclimatology
https://iodp.org
```

---

Support

For deployment assistance:

· Dashboard: https://stratica.netlify.app
· Documentation: https://stratica.readthedocs.io
· Issues: https://gitlab.com/gitdeeper8/STRATICA/-/issues
· Email: deploy@stratica.org
· Principal Investigator: gitdeeper@gmail.com

---

🪨 The Earth's stratigraphic column is a 4.5-billion-year journal written in rock. STRATICA decodes.

DOI: 10.5281/zenodo.18851076
