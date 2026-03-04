#!/bin/bash
# تنظيف المجلدات - يحتفظ بآخر 7 تقارير فقط

REPORTS_DIR="/storage/emulated/0/Download/STRATICA/reports"
KEEP_LAST=7

echo "🧹 STRATICA Reports Cleanup"
echo "==========================="

# تنظيف التقارير اليومية
echo -e "\n📅 Cleaning daily reports (keeping last $KEEP_LAST)..."
cd "$REPORTS_DIR/daily" 2>/dev/null && {
    ls -t *.txt 2>/dev/null | tail -n +$((KEEP_LAST+1)) | xargs -r rm
    ls -t *.md 2>/dev/null | tail -n +$((KEEP_LAST+1)) | xargs -r rm
    echo "   ✅ Done"
}

# تنظيف التقارير الأسبوعية
echo -e "\n📅 Cleaning weekly reports (keeping last $KEEP_LAST)..."
cd "$REPORTS_DIR/weekly" 2>/dev/null && {
    ls -t *.md 2>/dev/null | tail -n +$((KEEP_LAST+1)) | xargs -r rm
    echo "   ✅ Done"
}

# تنظيف التنبيهات
echo -e "\n⚠️ Cleaning alerts (keeping last $KEEP_LAST)..."
cd "$REPORTS_DIR/alerts" 2>/dev/null && {
    ls -t *.txt 2>/dev/null | tail -n +$((KEEP_LAST+1)) | xargs -r rm
    ls -t *.json 2>/dev/null | tail -n +$((KEEP_LAST+1)) | xargs -r rm
    echo "   ✅ Done"
}

echo -e "\n✅ Cleanup complete!"
