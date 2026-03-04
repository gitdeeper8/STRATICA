# 📊 STRATICA Reports Directory

## Directory Structure

```

reports/
├── daily/          # Daily reports (.txt, .md)
├── weekly/         # Weekly summaries (.md)
├── monthly/        # Monthly reports (.md)
├── alerts/         # Active alerts (.json, .txt)
├── archive/        # Archived old reports
└── figures/        # Generated figures

```

## Report Types

### Daily Reports (`daily/`)
- Format: `report_YYYY-MM-DD.txt` and `report_YYYY-MM-DD.md`
- Content: TCI scores, parameter averages, active alerts
- Generated: Every day at 00:00 UTC

### Weekly Reports (`weekly/`)
- Format: `week_W_YYYY.md`
- Content: Weekly summary, trends, statistics
- Generated: Every Sunday

### Monthly Reports (`monthly/`)
- Format: `month_YYYY.md`
- Content: Monthly analysis, significant events
- Generated: First day of each month

### Alerts (`alerts/`)
- Format: `alerts_YYYY-MM-DD.json` and `alerts_YYYY-MM-DD.txt`
- Content: Active alerts with severity levels
- Updated: Realtime

## Usage

Generate all reports:
```bash
python3 report_generator/generate_reports.py
```

Or using the shell script:

```bash
./generate_reports.sh
```

Alert Severity Levels

· 🔴 HIGH: Immediate attention required
· 🟡 MEDIUM: Monitor closely
· 🟢 LOW: Informational

Contact

For questions about reports: gitdeeper@gmail.com
