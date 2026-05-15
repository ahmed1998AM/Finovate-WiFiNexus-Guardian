#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - نظام توليد تقارير DOCX
توليد تقارير احترافية بصيغة Microsoft Word
"""

import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.style import WD_STYLE_TYPE
    from docx.oxml.ns import qn
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("⚠️  python-docx not installed. Install with: pip install python-docx")


class DOCXReportGenerator:
    """مولد تقارير DOCX الاحترافية"""
    
    def __init__(self, output_dir: str = "reports_output"):
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx library is required")
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.document: Optional[Document] = None
    
    def create_document(self, title: str, subtitle: str = "") -> Document:
        """إنشاء مستند Word جديد"""
        self.document = Document()
        
        # إضافة العنوان الرئيسي
        title_para = self.document.add_heading(title, 0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # إضافة العنوان الفرعي
        if subtitle:
            subtitle_para = self.document.add_heading(subtitle, 1)
            subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # إضافة معلومات التقرير
        self._add_report_metadata()
        
        return self.document
    
    def _add_report_metadata(self) -> None:
        """إضافة بيانات وصفية للتقرير"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        meta_table = self.document.add_table(rows=3, cols=2)
        meta_table.style = 'Table Grid'
        
        # البيانات الوصفية
        metadata = [
            ("تاريخ التقرير:", timestamp),
            ("الإصدار:", "v2.0.0"),
            ("الأداة:", "WiFiNexus Guardian")
        ]
        
        for idx, (label, value) in enumerate(metadata):
            meta_table.rows[idx].cells[0].text = label
            meta_table.rows[idx].cells[1].text = value
            
            # تنسيق الخلية الأولى
            meta_table.rows[idx].cells[0].paragraphs[0].runs[0].bold = True
    
    def add_section(self, title: str, content: str = "") -> None:
        """إضافة قسم جديد"""
        if not self.document:
            raise ValueError("No document created. Call create_document() first.")
        
        self.document.add_heading(title, level=2)
        
        if content:
            self.document.add_paragraph(content)
    
    def add_network_table(self, networks: List[Dict], title: str = "الشبكات المكتشفة") -> None:
        """إضافة جدول الشبكات"""
        if not self.document:
            raise ValueError("No document created")
        
        self.document.add_heading(title, level=3)
        
        if not networks:
            self.document.add_paragraph("لا توجد شبكات لعرضها.")
            return
        
        # إنشاء الجدول
        table = self.document.add_table(rows=1, cols=7)
        table.style = 'Table Grid'
        
        # إضافة العناوين
        headers = ["#", "BSSID", "SSID", "القناة", "الإشارة", "التشفير", "العملاء"]
        header_cells = table.rows[0].cells
        for idx, header in enumerate(headers):
            header_cells[idx].text = header
            header_cells[idx].paragraphs[0].runs[0].bold = True
        
        # إضافة البيانات
        for idx, network in enumerate(networks[:50], 1):  # حد أقصى 50 شبكة
            row = table.add_row().cells
            row[0].text = str(idx)
            row[1].text = network.get('bssid', 'N/A')
            row[2].text = network.get('ssid', 'Hidden')
            row[3].text = str(network.get('channel', 0))
            row[4].text = f"{network.get('signal', 0)} dBm"
            row[5].text = network.get('encryption', 'Unknown')
            row[6].text = str(network.get('clients', 0))
    
    def add_attack_results(self, attack_type: str, results: Dict) -> None:
        """إضافة نتائج الهجوم"""
        if not self.document:
            raise ValueError("No document created")
        
        self.document.add_heading(f"نتائج الهجوم: {attack_type}", level=3)
        
        # جدول النتائج
        result_table = self.document.add_table(rows=1, cols=2)
        result_table.style = 'Table Grid'
        
        # العناوين
        result_table.rows[0].cells[0].text = "المعيار"
        result_table.rows[0].cells[1].text = "القيمة"
        result_table.rows[0].cells[0].paragraphs[0].runs[0].bold = True
        result_table.rows[0].cells[1].paragraphs[0].runs[0].bold = True
        
        # إضافة النتائج
        for key, value in results.items():
            row = result_table.add_row().cells
            row[0].text = key.replace('_', ' ').title()
            row[1].text = str(value)
    
    def add_handshake_info(self, handshake_data: Dict) -> None:
        """إضافة معلومات Handshake"""
        if not self.document:
            raise ValueError("No document created")
        
        self.document.add_heading("معلومات Handshake", level=3)
        
        info = [
            ("الشبكة (SSID):", handshake_data.get('ssid', 'Unknown')),
            ("BSSID:", handshake_data.get('bssid', 'N/A')),
            ("مسار الملف:", handshake_data.get('file_path', 'N/A')),
            ("تاريخ الالتقاط:", handshake_data.get('capture_time', 'N/A')),
            ("الحالة:", "✓ تم التحقق" if handshake_data.get('verified', False) else "✗ لم يتم التحقق")
        ]
        
        info_table = self.document.add_table(rows=len(info), cols=2)
        info_table.style = 'Table Grid'
        
        for idx, (label, value) in enumerate(info):
            info_table.rows[idx].cells[0].text = label
            info_table.rows[idx].cells[1].text = value
            info_table.rows[idx].cells[0].paragraphs[0].runs[0].bold = True
    
    def add_recommendations(self, recommendations: List[str]) -> None:
        """إضافة التوصيات الأمنية"""
        if not self.document:
            raise ValueError("No document created")
        
        self.document.add_heading("التوصيات الأمنية", level=3)
        
        for idx, rec in enumerate(recommendations, 1):
            para = self.document.add_paragraph(style='List Number')
            para.add_run(rec)
    
    def add_executive_summary(self, summary: str) -> None:
        """إضافة الملخص التنفيذي"""
        if not self.document:
            raise ValueError("No document created")
        
        self.document.add_heading("الملخص التنفيذي", level=2)
        
        # صندوق ملون للملخص
        summary_para = self.document.add_paragraph(summary)
        summary_para.paragraph_format.space_before = Pt(12)
        summary_para.paragraph_format.space_after = Pt(12)
    
    def save_report(self, filename: Optional[str] = None) -> str:
        """حفظ التقرير"""
        if not self.document:
            raise ValueError("No document to save")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"WiFiNexus_Report_{timestamp}.docx"
        
        output_path = self.output_dir / filename
        self.document.save(str(output_path))
        
        return str(output_path)
    
    def generate_full_report(self, scan_data: Dict, attack_results: List[Dict], 
                            recommendations: List[str]) -> str:
        """توليد تقرير كامل"""
        # إنشاء المستند
        self.create_document(
            "تقرير اختبار اختراق WiFi",
            "WiFiNexus Guardian Security Assessment"
        )
        
        # الملخص التنفيذي
        total_networks = len(scan_data.get('networks', []))
        handshakes = sum(1 for n in scan_data.get('networks', []) if n.get('handshake'))
        
        summary = f"""تم إجراء مسح أمني للشبكات اللاسلكية في المنطقة المستهدفة. 
عُثر على {total_networks} شبكة لاسلكية، وتم التقاط {handshakes} handshake بنجاح.
يحتوي هذا التقرير على تفاصيل الشبكات المكتشفة ونتائج الهجمات والتوصيات الأمنية."""
        
        self.add_executive_summary(summary)
        
        # قسم الشبكات
        self.add_network_table(scan_data.get('networks', []))
        
        # قسم نتائج الهجمات
        if attack_results:
            self.add_section("نتائج الهجمات")
            for result in attack_results:
                self.add_attack_results(
                    result.get('type', 'Unknown'),
                    result.get('details', {})
                )
        
        # التوصيات
        self.add_recommendations(recommendations)
        
        # حفظ التقرير
        return self.save_report()


def main():
    """اختبار مولد تقارير DOCX"""
    if not DOCX_AVAILABLE:
        print("❌ مكتبة python-docx غير مثبتة")
        print("قم بالتثبيت: pip install python-docx")
        return 1
    
    print("=" * 60)
    print("📄 اختبار مولد تقارير DOCX")
    print("=" * 60)
    
    try:
        generator = DOCXReportGenerator()
        
        # بيانات تجريبية
        scan_data = {
            "networks": [
                {"bssid": "AA:BB:CC:DD:EE:01", "ssid": "HomeWiFi", "channel": 6, 
                 "signal": -45, "encryption": "WPA2", "clients": 3, "handshake": True},
                {"bssid": "AA:BB:CC:DD:EE:02", "ssid": "Office_Network", "channel": 11,
                 "signal": -62, "encryption": "WPA3", "clients": 12, "handshake": False},
                {"bssid": "AA:BB:CC:DD:EE:03", "ssid": "Guest_WiFi", "channel": 1,
                 "signal": -78, "encryption": "WEP", "clients": 5, "handshake": True},
            ]
        }
        
        attack_results = [
            {
                "type": "PMKID Attack",
                "details": {
                    "target": "HomeWiFi",
                    "status": "Success",
                    "time_elapsed": "45 seconds",
                    "packets_captured": 1250
                }
            },
            {
                "type": "Deauth Attack",
                "details": {
                    "target": "Guest_WiFi",
                    "status": "Success",
                    "deauth_frames": 500,
                    "clients_disconnected": 5
                }
            }
        ]
        
        recommendations = [
            "ترقية جميع الشبكات من WEP إلى WPA3",
            "تفعيل تصفية MAC addresses للشبكات الحساسة",
            "تقليل قوة الإشارة للشبكات الداخلية",
            "تفعيل نظام كشف التسلل اللاسلكي (WIDS)",
            "إجراء فحوصات أمنية دورية كل شهر"
        ]
        
        # توليد التقرير
        print("\n📝 جاري توليد التقرير...")
        report_path = generator.generate_full_report(scan_data, attack_results, recommendations)
        
        print(f"\n✅ تم إنشاء التقرير بنجاح!")
        print(f"📁 المسار: {report_path}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
