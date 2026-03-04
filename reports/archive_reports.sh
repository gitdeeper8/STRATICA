#!/bin/bash
# STRATICA Reports Archiving System

REPORTS_DIR="/storage/emulated/0/Download/STRATICA/reports"
ARCHIVE_DIR="$REPORTS_DIR/archive"
DATE=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)

# ألوان للتنبيه
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}📦 STRATICA Reports Archiving System${NC}"
echo "========================================"

# إنشاء مجلدات الأرشفة
mkdir -p "$ARCHIVE_DIR/$YEAR/$MONTH"/{daily,weekly,monthly,alerts}

# أرشفة التقارير اليومية
echo -e "\n${YELLOW}📅 Archiving daily reports...${NC}"
if [ -d "$REPORTS_DIR/daily" ]; then
    cp "$REPORTS_DIR/daily"/*.txt "$ARCHIVE_DIR/$YEAR/$MONTH/daily/" 2>/dev/null
    cp "$REPORTS_DIR/daily"/*.md "$ARCHIVE_DIR/$YEAR/$MONTH/daily/" 2>/dev/null
    echo "   ✅ $(ls $REPORTS_DIR/daily/*.txt 2>/dev/null | wc -l) txt files"
    echo "   ✅ $(ls $REPORTS_DIR/daily/*.md 2>/dev/null | wc -l) md files"
fi

# أرشفة التقارير الأسبوعية
echo -e "\n${YELLOW}📅 Archiving weekly reports...${NC}"
if [ -d "$REPORTS_DIR/weekly" ]; then
    cp "$REPORTS_DIR/weekly"/*.md "$ARCHIVE_DIR/$YEAR/$MONTH/weekly/" 2>/dev/null
    echo "   ✅ $(ls $REPORTS_DIR/weekly/*.md 2>/dev/null | wc -l) md files"
fi

# أرشفة التقارير الشهرية
echo -e "\n${YELLOW}📅 Archiving monthly reports...${NC}"
if [ -d "$REPORTS_DIR/monthly" ]; then
    cp "$REPORTS_DIR/monthly"/*.md "$ARCHIVE_DIR/$YEAR/$MONTH/monthly/" 2>/dev/null
    echo "   ✅ $(ls $REPORTS_DIR/monthly/*.md 2>/dev/null | wc -l) md files"
fi

# أرشفة التنبيهات
echo -e "\n${YELLOW}⚠️ Archiving alerts...${NC}"
if [ -d "$REPORTS_DIR/alerts" ]; then
    cp "$REPORTS_DIR/alerts"/*.txt "$ARCHIVE_DIR/$YEAR/$MONTH/alerts/" 2>/dev/null
    cp "$REPORTS_DIR/alerts"/*.json "$ARCHIVE_DIR/$YEAR/$MONTH/alerts/" 2>/dev/null
    echo "   ✅ $(ls $REPORTS_DIR/alerts/*.txt 2>/dev/null | wc -l) txt files"
    echo "   ✅ $(ls $REPORTS_DIR/alerts/*.json 2>/dev/null | wc -l) json files"
fi

echo -e "\n${GREEN}✅ Archiving complete!${NC}"
echo "📁 Archive location: $ARCHIVE_DIR/$YEAR/$MONTH/"
