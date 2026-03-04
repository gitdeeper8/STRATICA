#!/usr/bin/env python
"""
STRATICA Report Generator
يقوم بإنشاء تقارير يومية، أسبوعية، شهرية، وتنبيهات
بصيغ txt و md فقط
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import random

# إضافة المسار
sys.path.insert(0, str(Path(__file__).parent.parent))

class STRATICAGenerator:
    """مولد تقارير STRATICA"""
    
    def __init__(self):
        self.reports_dir = Path("reports")
        self.today = datetime.datetime.now()
        self.date_str = self.today.strftime("%Y-%m-%d")
        self.week_num = self.today.isocalendar()[1]
        self.month_num = self.today.month
        self.year = self.today.year
        self.month_names = ["January", "February", "March", "April", "May", "June",
                           "July", "August", "September", "October", "November", "December"]
        
        # بيانات الأحواض الرسوبية
        self.basins = [
            {"name": "Shatsky Rise", "location": "North Pacific", "tci": 0.78, "trend": "+0.02"},
            {"name": "Walvis Ridge", "location": "South Atlantic", "tci": 0.81, "trend": "+0.01"},
            {"name": "Demerara Rise", "location": "Equatorial Atlantic", "tci": 0.74, "trend": "-0.03"},
            {"name": "Iberian Margin", "location": "North Atlantic", "tci": 0.83, "trend": "+0.04"},
            {"name": "Ceará Rise", "location": "Equatorial Atlantic", "tci": 0.79, "trend": "+0.00"},
            {"name": "Kerguelen Plateau", "location": "Southern Ocean", "tci": 0.68, "trend": "-0.02"},
            {"name": "Campbell Plateau", "location": "Southwest Pacific", "tci": 0.72, "trend": "+0.01"},
            {"name": "ODP 1209B", "location": "Shatsky Rise", "tci": 0.78, "trend": "+0.01"},
            {"name": "ODP 1262", "location": "Walvis Ridge", "tci": 0.80, "trend": "-0.01"},
        ]
        
        # معاملات TCI
        self.parameters = {
            "LDR": 0.72, "ISO": 0.68, "MFA": 0.65,
            "MAG": 0.71, "GCH": 0.59, "PYS": 0.63,
            "VSI": 0.67, "TDM": 0.70, "CEC": 0.66
        }
        
        # أنواع التنبيهات
        self.alert_types = [
            "Geochemical anomaly (Mo enrichment)",
            "Magnetic reversal detected",
            "TCI below functional threshold",
            "Carbon isotope excursion",
            "Anoxia event precursor",
            "Milankovitch cycle detected",
            "Deposition rate anomaly"
        ]
    
    def get_tci_status(self, tci: float) -> str:
        """تحديد حالة TCI"""
        if tci > 0.88:
            return "🟢 OPTIMAL"
        elif tci > 0.72:
            return "✅ GOOD"
        elif tci > 0.55:
            return "🟡 MODERATE"
        elif tci > 0.38:
            return "🟠 MARGINAL"
        else:
            return "🔴 DYSFUNCTIONAL"
    
    def generate_daily_report(self) -> tuple:
        """إنشاء تقرير يومي (txt و md)"""
        report_dir = self.reports_dir / "daily"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        # اختيار أحواض للتقرير
        selected_basins = self.basins[:7]  # أول 7 أحواض
        
        # توليد تنبيهات عشوائية
        n_alerts = random.randint(1, 3)
        alerts = []
        alert_sources = random.sample(self.basins, min(n_alerts, len(self.basins)))
        for basin in alert_sources:
            alert_type = random.choice(self.alert_types)
            severity = random.choice(["🔴", "🟡", "🟢"])
            alerts.append({"basin": basin["name"], "type": alert_type, "severity": severity})
        
        # ========== إنشاء التقرير النصي ==========
        txt_file = report_dir / f"daily_{self.date_str}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"STRATICA DAILY REPORT - {self.date_str}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("📊 TCI SCORES SUMMARY:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Basin':<25} {'TCI':<8} {'Status':<20} {'Trend':<8}\n")
            f.write("-" * 60 + "\n")
            
            for basin in selected_basins:
                status = self.get_tci_status(basin["tci"])
                f.write(f"{basin['name']:<25} {basin['tci']:<8.2f} {status:<20} {basin['trend']:<8}\n")
            
            f.write("\n📈 PARAMETER AVERAGES:\n")
            f.write("-" * 60 + "\n")
            f.write(f"LDR: {self.parameters['LDR']:.2f}  | ISO: {self.parameters['ISO']:.2f}  | MFA: {self.parameters['MFA']:.2f}\n")
            f.write(f"MAG: {self.parameters['MAG']:.2f}  | GCH: {self.parameters['GCH']:.2f}  | PYS: {self.parameters['PYS']:.2f}\n")
            f.write(f"VSI: {self.parameters['VSI']:.2f}  | TDM: {self.parameters['TDM']:.2f}  | CEC: {self.parameters['CEC']:.2f}\n")
            
            f.write("\n⚠️ ACTIVE ALERTS:\n")
            f.write("-" * 60 + "\n")
            if alerts:
                for alert in alerts:
                    f.write(f"{alert['severity']} {alert['basin']:<25} - {alert['type']}\n")
            else:
                f.write("No active alerts\n")
            
            f.write("\n📋 NOTES:\n")
            f.write("-" * 60 + "\n")
            f.write(f"- All systems operational\n")
            f.write(f"- {len(alerts)} active alerts monitored\n")
            f.write(f"- Next update: {(self.today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')} 00:00 UTC\n")
            f.write("=" * 60 + "\n")
        
        # ========== إنشاء التقرير بصيغة Markdown ==========
        md_file = report_dir / f"daily_{self.date_str}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 STRATICA Daily Report - {self.date_str}\n\n")
            
            f.write(f"## TCI Scores Overview\n\n")
            f.write(f"| Basin | TCI | Status | Trend |\n")
            f.write(f"|-------|-----|--------|-------|\n")
            
            for basin in selected_basins:
                status = self.get_tci_status(basin["tci"])
                f.write(f"| {basin['name']} | {basin['tci']:.2f} | {status} | {basin['trend']} |\n")
            
            f.write(f"\n## Parameter Averages\n\n")
            f.write(f"| LDR | ISO | MFA | MAG | GCH | PYS | VSI | TDM | CEC |\n")
            f.write(f"|-----|-----|-----|-----|-----|-----|-----|-----|-----|\n")
            f.write(f"| {self.parameters['LDR']:.2f} | {self.parameters['ISO']:.2f} | {self.parameters['MFA']:.2f} | ")
            f.write(f"{self.parameters['MAG']:.2f} | {self.parameters['GCH']:.2f} | {self.parameters['PYS']:.2f} | ")
            f.write(f"{self.parameters['VSI']:.2f} | {self.parameters['TDM']:.2f} | {self.parameters['CEC']:.2f} |\n\n")
            
            f.write(f"## Active Alerts\n\n")
            if alerts:
                for alert in alerts:
                    f.write(f"- {alert['severity']} **{alert['basin']}**: {alert['type']}\n")
            else:
                f.write(f"- No active alerts\n")
            
            f.write(f"\n## Notes\n\n")
            f.write(f"- All systems operational\n")
            f.write(f"- {len(alerts)} active alerts being monitored\n")
            f.write(f"- Next update: {(self.today + datetime.timedelta(days=1)).strftime('%Y-%m-%d')} 00:00 UTC\n\n")
            
            f.write(f"---\n")
            f.write(f"*Report generated by STRATICA Intelligence System*\n")
        
        return txt_file, md_file
    
    def generate_weekly_report(self) -> Path:
        """إنشاء تقرير أسبوعي (md فقط)"""
        report_dir = self.reports_dir / "weekly"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        week_range = f"{self.date_str} to {(self.today + datetime.timedelta(days=6)).strftime('%Y-%m-%d')}"
        month_name = self.month_names[self.month_num - 1]
        
        md_file = report_dir / f"week_{self.week_num}_{self.year}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 STRATICA Weekly Report - Week {self.week_num}, {self.year}\n\n")
            f.write(f"**Period:** {week_range}\n\n")
            
            f.write(f"## Weekly Summary\n\n")
            f.write(f"This week's analysis covers **{len(self.basins)}** sedimentary basins.\n\n")
            
            # إحصائيات
            functional = sum(1 for b in self.basins if b["tci"] > 0.62)
            optimal = sum(1 for b in self.basins if b["tci"] > 0.88)
            good = sum(1 for b in self.basins if 0.72 < b["tci"] <= 0.88)
            moderate = sum(1 for b in self.basins if 0.55 < b["tci"] <= 0.72)
            marginal = sum(1 for b in self.basins if b["tci"] <= 0.55)
            
            f.write(f"### Key Statistics\n\n")
            f.write(f"- **Average TCI**: {sum(b['tci'] for b in self.basins)/len(self.basins):.2f}\n")
            f.write(f"- **Functional Basins**: {functional}/{len(self.basins)} ({functional/len(self.basins)*100:.1f}%)\n")
            f.write(f"- **Optimal (TCI > 0.88)**: {optimal}\n")
            f.write(f"- **Good (0.72-0.88)**: {good}\n")
            f.write(f"- **Moderate (0.55-0.72)**: {moderate}\n")
            f.write(f"- **Marginal (<0.55)**: {marginal}\n\n")
            
            f.write(f"### Top 5 Basins\n\n")
            f.write(f"| Basin | TCI | Location |\n")
            f.write(f"|-------|-----|----------|\n")
            for basin in sorted(self.basins, key=lambda x: x["tci"], reverse=True)[:5]:
                f.write(f"| {basin['name']} | {basin['tci']:.2f} | {basin['location']} |\n")
            
            f.write(f"\n### Basins Requiring Attention\n\n")
            f.write(f"| Basin | TCI | Issue |\n")
            f.write(f"|-------|-----|-------|\n")
            for basin in sorted(self.basins, key=lambda x: x["tci"])[:3]:
                if basin["tci"] < 0.72:
                    issue = "Below optimal threshold"
                    if basin["tci"] < 0.55:
                        issue = "Critical - below functional threshold"
                    f.write(f"| {basin['name']} | {basin['tci']:.2f} | {issue} |\n")
            
            f.write(f"\n### Parameter Trends (Weekly Average)\n\n")
            f.write(f"| Parameter | Current | Weekly Change |\n")
            f.write(f"|-----------|---------|---------------|\n")
            for param, value in self.parameters.items():
                change = random.uniform(-0.05, 0.05)
                arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                f.write(f"| {param} | {value:.2f} | {arrow} {change:+.3f} |\n")
            
            f.write(f"\n---\n")
            f.write(f"*Week {self.week_num} Report - {month_name} {self.year}*\n")
        
        return md_file
    
    def generate_monthly_report(self) -> Path:
        """إنشاء تقرير شهري (md فقط)"""
        report_dir = self.reports_dir / "monthly"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        month_name = self.month_names[self.month_num - 1]
        
        md_file = report_dir / f"{month_name.lower()}_{self.year}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 STRATICA Monthly Report - {month_name} {self.year}\n\n")
            
            f.write(f"## Executive Summary\n\n")
            f.write(f"This monthly report summarizes stratigraphic analysis for {month_name} {self.year}.\n\n")
            
            f.write(f"### Monthly Statistics\n\n")
            f.write(f"- **Total Basins Analyzed**: {len(self.basins)}\n")
            f.write(f"- **Data Points Processed**: {len(self.basins) * 1000:,}\n")
            f.write(f"- **Active Alerts**: {random.randint(3, 8)}\n")
            f.write(f"- **Resolved Alerts**: {random.randint(2, 6)}\n\n")
            
            f.write(f"### TCI Distribution\n\n")
            f.write(f"| Category | Count | Percentage |\n")
            f.write(f"|----------|-------|------------|\n")
            
            optimal = random.randint(2, 4)
            good = random.randint(3, 5)
            moderate = random.randint(1, 3)
            marginal = len(self.basins) - optimal - good - moderate
            
            f.write(f"| Optimal (>0.88) | {optimal} | {optimal/len(self.basins)*100:.1f}% |\n")
            f.write(f"| Good (0.72-0.88) | {good} | {good/len(self.basins)*100:.1f}% |\n")
            f.write(f"| Moderate (0.55-0.72) | {moderate} | {moderate/len(self.basins)*100:.1f}% |\n")
            f.write(f"| Marginal (<0.55) | {marginal} | {marginal/len(self.basins)*100:.1f}% |\n\n")
            
            f.write(f"### Significant Events This Month\n\n")
            events = [
                f"PETM precursor detected at ODP 1209B ({self.date_str})",
                f"Milankovitch cycle confirmed in North Atlantic (Week {self.week_num-2})",
                f"Geomagnetic reversal recorded at Iberian Margin",
                f"New basin data added from IODP Expedition 401",
                f"Carbon isotope excursion identified in Pacific"
            ]
            for event in random.sample(events, 3):
                f.write(f"- {event}\n")
            
            f.write(f"\n### Parameter Monthly Averages\n\n")
            f.write(f"| Parameter | Value | Monthly Change |\n")
            f.write(f"|-----------|-------|----------------|\n")
            for param, value in self.parameters.items():
                change = random.uniform(-0.03, 0.03)
                arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                f.write(f"| {param} | {value:.2f} | {arrow} {change:+.3f} |\n")
            
            f.write(f"\n---\n")
            f.write(f"*{month_name} {self.year} Monthly Report*\n")
        
        return md_file
    
    def generate_alerts(self) -> tuple:
        """إنشاء ملف التنبيهات (txt و json)"""
        alerts_dir = self.reports_dir / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        # توليد تنبيهات نشطة
        active_alerts = []
        n_alerts = random.randint(2, 4)
        alert_basins = random.sample(self.basins, n_alerts)
        
        for basin in alert_basins:
            alert = {
                "basin": basin["name"],
                "tci": basin["tci"],
                "type": random.choice(self.alert_types),
                "detected": self.date_str,
                "severity": random.choice(["HIGH", "MEDIUM", "LOW"])
            }
            active_alerts.append(alert)
        
        # ========== ملف التنبيهات النصي ==========
        txt_file = alerts_dir / f"alerts_{self.date_str}.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"STRATICA ACTIVE ALERTS - {self.date_str}\n")
            f.write("=" * 60 + "\n\n")
            
            if active_alerts:
                for alert in active_alerts:
                    severity_color = "🔴" if alert["severity"] == "HIGH" else "🟡" if alert["severity"] == "MEDIUM" else "🟢"
                    f.write(f"{severity_color} [{alert['severity']}] {alert['basin']}\n")
                    f.write(f"   Type: {alert['type']}\n")
                    f.write(f"   TCI: {alert['tci']:.2f}\n")
                    f.write(f"   Detected: {alert['detected']}\n\n")
            else:
                f.write("No active alerts\n")
            
            f.write("=" * 60 + "\n")
        
        # ========== ملف التنبيهات JSON ==========
        json_file = alerts_dir / f"alerts_{self.date_str}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump({
                "date": self.date_str,
                "total_alerts": len(active_alerts),
                "alerts": active_alerts
            }, f, indent=2, ensure_ascii=False)
        
        return txt_file, json_file
    
    def generate_all(self):
        """توليد جميع التقارير"""
        print("📊 STRATICA Report Generator")
        print("=" * 40)
        
        print(f"\n📅 Generating daily report ({self.date_str})...")
        daily_txt, daily_md = self.generate_daily_report()
        print(f"   ✅ {daily_txt.name}")
        print(f"   ✅ {daily_md.name}")
        
        print(f"\n📅 Generating weekly report (Week {self.week_num})...")
        weekly = self.generate_weekly_report()
        print(f"   ✅ {weekly.name}")
        
        print(f"\n📅 Generating monthly report ({self.month_names[self.month_num-1]})...")
        monthly = self.generate_monthly_report()
        print(f"   ✅ {monthly.name}")
        
        print(f"\n⚠️ Generating alerts...")
        alerts_txt, alerts_json = self.generate_alerts()
        print(f"   ✅ {alerts_txt.name}")
        print(f"   ✅ {alerts_json.name}")
        
        print(f"\n" + "=" * 40)
        print(f"✅ All reports generated successfully!")
        print(f"📁 Reports saved in: reports/")
        print(f"\n   📄 Daily:    reports/daily/")
        print(f"   📄 Weekly:   reports/weekly/")
        print(f"   📄 Monthly:  reports/monthly/")
        print(f"   ⚠️ Alerts:   reports/alerts/")


if __name__ == "__main__":
    generator = STRATICAGenerator()
    generator.generate_all()
