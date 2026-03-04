#!/bin/bash
# STRATICA Report Generator Script

echo "🚀 STRATICA Report Generator"
echo "================================"

cd /storage/emulated/0/Download/STRATICA

# تشغيل مولد التقارير
python3 report_generator/generate_reports.py

# عرض قائمة التقارير
echo ""
echo "📁 Generated Reports:"
ls -la reports/daily/ reports/weekly/ reports/monthly/ reports/alerts/ 2>/dev/null
