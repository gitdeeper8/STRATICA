#!/bin/bash
# عرض آخر التقارير

REPORTS_DIR="/storage/emulated/0/Download/STRATICA/reports"

echo "📊 STRATICA Latest Reports"
echo "=========================="

# آخر تقرير يومي
echo -e "\n📅 Latest Daily Report:"
latest_daily=$(ls -t $REPORTS_DIR/daily/*.txt 2>/dev/null | head -1)
if [ -f "$latest_daily" ]; then
    echo "   File: $(basename "$latest_daily")"
    echo "   Preview:"
    head -15 "$latest_daily"
else
    echo "   No daily reports found"
fi

# آخر تقرير أسبوعي
echo -e "\n📅 Latest Weekly Report:"
latest_weekly=$(ls -t $REPORTS_DIR/weekly/*.md 2>/dev/null | head -1)
if [ -f "$latest_weekly" ]; then
    echo "   File: $(basename "$latest_weekly")"
    head -5 "$latest_weekly"
fi

# آخر التنبيهات
echo -e "\n⚠️ Latest Alerts:"
latest_alerts=$(ls -t $REPORTS_DIR/alerts/*.txt 2>/dev/null | head -1)
if [ -f "$latest_alerts" ]; then
    echo "   File: $(basename "$latest_alerts")"
    tail -10 "$latest_alerts"
fi
