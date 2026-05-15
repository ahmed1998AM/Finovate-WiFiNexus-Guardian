#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Professional Report Generator
مولد التقارير الاحترافي بصيغة PDF

المؤلف: فريق WiFiNexus Guardian
الترخيص: MIT (للاستخدام التعليمي والقانوني فقط)
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import base64

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
    
    # تعريف الأنواع للاستخدام اللاحق
    TableType = Table
    TableStyleType = TableStyle
    ParagraphType = Paragraph
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. Install with: pip install reportlab")
    
    # تعريف أنواع وهمية لتجنب الأخطاء
    class TableType:
        pass
    class TableStyleType:
        pass
    class ParagraphType:
        pass

class Colors:
    """ألوان للـ terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class ProfessionalReportGenerator:
    """مولد تقارير احترافي"""
    
    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not REPORTLAB_AVAILABLE:
            print(f"{Colors.YELLOW}ReportLab not available. Using basic text reports.{Colors.RESET}")
            
        self.styles = None
        if REPORTLAB_AVAILABLE:
            self.styles = getSampleStyleSheet()
            self._setup_custom_styles()
            
    def _setup_custom_styles(self):
        """إعداد الأنماط المخصصة"""
        # عنوان رئيسي
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a2e'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # عنوان فرعي
        self.styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#16213e'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # عنوان فرعي 3
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#0f3460'),
            spaceAfter=10,
            spaceBefore=10
        ))
        
        # نص عادي
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # تحذير
        self.styles.add(ParagraphStyle(
            name='WarningStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            spaceBefore=6,
            spaceAfter=6
        ))
        
        # نجاح
        self.styles.add(ParagraphStyle(
            name='SuccessStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.green,
            spaceBefore=6,
            spaceAfter=6
        ))
        
    def generate_security_assessment_report(
        self,
        scan_data: Dict[str, Any],
        attack_results: Optional[Dict[str, Any]] = None,
        wids_alerts: Optional[List[Dict]] = None,
        output_filename: Optional[str] = None
    ) -> str:
        """توليد تقرير تقييم أمني شامل"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = output_filename or f"Security_Assessment_{timestamp}.pdf"
        output_path = self.output_dir / filename
        
        if REPORTLAB_AVAILABLE:
            return self._generate_pdf_report(
                scan_data, attack_results, wids_alerts, output_path
            )
        else:
            return self._generate_text_report(
                scan_data, attack_results, wids_alerts, output_path.with_suffix('.txt')
            )
            
    def _generate_pdf_report(
        self,
        scan_data: Dict,
        attack_results: Optional[Dict],
        wids_alerts: Optional[List],
        output_path: Path
    ) -> str:
        """توليد تقرير PDF"""
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # العنوان الرئيسي
        title = Paragraph(
            "WiFiNexus Guardian - Security Assessment Report",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # معلومات التقرير
        report_info = self._create_report_info_table(scan_data)
        story.append(report_info)
        story.append(Spacer(1, 0.3*inch))
        
        # ملخص تنفيذي
        executive_summary = self._create_executive_summary(scan_data, attack_results)
        story.append(executive_summary)
        story.append(Spacer(1, 0.3*inch))
        
        # نتائج الفحص
        if 'networks' in scan_data:
            scan_results = self._create_scan_results_table(scan_data['networks'])
            story.append(Paragraph("Network Scan Results", self.styles['CustomHeading2']))
            story.append(scan_results)
            story.append(Spacer(1, 0.3*inch))
            
        # نتائج الهجمات
        if attack_results:
            attack_section = self._create_attack_results_section(attack_results)
            story.extend(attack_section)
            story.append(Spacer(1, 0.3*inch))
            
        # تنبيهات WIDS
        if wids_alerts and len(wids_alerts) > 0:
            wids_section = self._create_wids_alerts_section(wids_alerts)
            story.extend(wids_section)
            
        # التوصيات الأمنية
        recommendations = self._create_recommendations(scan_data, attack_results)
        story.append(Paragraph("Security Recommendations", self.styles['CustomHeading2']))
        story.extend(recommendations)
        
        # التذييل
        story.append(PageBreak())
        disclaimer = self._create_disclaimer()
        story.append(disclaimer)
        
        # بناء PDF
        doc.build(story)
        
        print(f"{Colors.GREEN}✓ PDF report generated: {output_path}{Colors.RESET}")
        return str(output_path)
        
    def _create_report_info_table(self, scan_data: Dict) -> 'TableType':
        """إنشاء جدول معلومات التقرير"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        data = [
            ['Report Information', ''],
            ['Generated:', timestamp],
            ['Tool:', 'WiFiNexus Guardian v1.0'],
            ['Assessment Type:', 'Wireless Security Audit'],
            ['Total Networks Scanned:', str(scan_data.get('total_networks', 0))],
            ['Vulnerable Networks:', str(scan_data.get('vulnerable_count', 0))],
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a1a2e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        return table
        
    def _create_executive_summary(self, scan_data: Dict, attack_results: Optional[Dict]) -> Paragraph:
        """إنشاء ملخص تنفيذي"""
        
        total_networks = scan_data.get('total_networks', 0)
        vulnerable = scan_data.get('vulnerable_count', 0)
        encrypted = scan_data.get('encrypted_count', 0)
        open_networks = scan_data.get('open_count', 0)
        
        # حساب درجة الأمان
        if total_networks > 0:
            security_score = ((encrypted + (vulnerable * 0.5)) / total_networks) * 100
        else:
            security_score = 0
            
        summary_text = f"""
        <b>Executive Summary</b><br/><br/>
        This report presents the findings of a comprehensive wireless security assessment 
        conducted using WiFiNexus Guardian. The scan analyzed {total_networks} wireless networks 
        in the target environment.<br/><br/>
        
        <b>Key Findings:</b><br/>
        • Total Networks Detected: {total_networks}<br/>
        • Encrypted Networks (WPA/WPA2/WPA3): {encrypted}<br/>
        • Open/Unencrypted Networks: {open_networks}<br/>
        • Vulnerable Networks (WEP/WPS): {vulnerable}<br/><br/>
        
        <b>Overall Security Score: {security_score:.1f}/100</b><br/><br/>
        """
        
        if attack_results and attack_results.get('success', False):
            summary_text += """
            <b style="color:red;">Critical:</b> Successful penetration testing was conducted, 
            demonstrating that at least one network is susceptible to attacks. Immediate 
            remediation is strongly recommended.<br/><br/>
            """
            
        return Paragraph(summary_text, self.styles['CustomBody'])
        
    def _create_scan_results_table(self, networks: List[Dict]) -> 'TableType':
        """إنشاء جدول نتائج الفحص"""
        
        # رأس الجدول
        data = [['SSID', 'BSSID', 'Signal', 'Encryption', 'Channel', 'Security Status']]
        
        # إضافة الشبكات (أول 20 فقط لتجنب التقرير الطويل جداً)
        for net in networks[:20]:
            ssid = net.get('ssid', 'Hidden')[:20]
            bssid = net.get('bssid', 'N/A')
            signal = net.get('signal', 0)
            encryption = net.get('encryption', 'Unknown')
            channel = net.get('channel', 'N/A')
            
            # تحديد حالة الأمان
            if 'WEP' in encryption.upper():
                status = '🔴 Critical'
            elif 'WPS' in encryption.upper():
                status = '🟠 High Risk'
            elif encryption == 'Open':
                status = '🟠 No Encryption'
            elif 'WPA3' in encryption.upper():
                status = '🟢 Excellent'
            elif 'WPA2' in encryption.upper():
                status = '🟢 Good'
            else:
                status = '🟡 Unknown'
                
            data.append([ssid, bssid, f"{signal} dBm", encryption, str(channel), status])
            
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 0.8*inch, 1*inch, 0.7*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f8f8')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        return table
        
    def _create_attack_results_section(self, attack_results: Dict) -> list:
        """إنشاء قسم نتائج الهجمات"""
        
        story = []
        
        story.append(Paragraph("Penetration Testing Results", self.styles['CustomHeading2']))
        story.append(Spacer(1, 0.2*inch))
        
        # جدول نتائج الهجوم
        data = [
            ['Attack Type', 'Target', 'Status', 'Time Taken', 'Notes']
        ]
        
        attacks = attack_results.get('attacks', [])
        for attack in attacks:
            attack_type = attack.get('type', 'Unknown')
            target = attack.get('target', 'N/A')
            status = '✅ Success' if attack.get('success') else '❌ Failed'
            time_taken = attack.get('duration', 'N/A')
            notes = attack.get('notes', '')[:30]
            
            data.append([attack_type, target, status, time_taken, notes])
            
        table = Table(data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 1*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#16213e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # إذا تم كسر كلمة المرور
        if attack_results.get('cracked_password'):
            warning_style = ParagraphStyle(
                'CrackWarning',
                parent=self.styles['WarningStyle'],
                fontSize=11,
                alignment=TA_CENTER
            )
            
            warning = Paragraph(
                f"<b>⚠️ PASSWORD CRACKED:</b> {attack_results.get('cracked_password')}",
                warning_style
            )
            story.append(warning)
            story.append(Spacer(1, 0.2*inch))
            
        return story
        
    def _create_wids_alerts_section(self, alerts: List[Dict]) -> list:
        """إنشاء قسم تنبيهات WIDS"""
        
        story = []
        
        story.append(Paragraph("Wireless Intrusion Detection Alerts", self.styles['CustomHeading2']))
        story.append(Spacer(1, 0.2*inch))
        
        data = [['Timestamp', 'Alert Type', 'Severity', 'Source MAC', 'Description']]
        
        for alert in alerts[:30]:  # أول 30 تنبيه فقط
            timestamp = alert.get('timestamp', 'N/A')[:19]
            alert_type = alert.get('type', 'Unknown')
            severity = alert.get('severity', 'Medium')
            source = alert.get('source_mac', 'N/A')
            desc = alert.get('description', '')[:25]
            
            # لون حسب الخطورة
            if severity.upper() == 'CRITICAL':
                severity_str = '🔴 Critical'
            elif severity.upper() == 'HIGH':
                severity_str = '🟠 High'
            elif severity.upper() == 'MEDIUM':
                severity_str = '🟡 Medium'
            else:
                severity_str = '🟢 Low'
                
            data.append([timestamp, alert_type, severity_str, source, desc])
            
        table = Table(data, colWidths=[1.3*inch, 1.2*inch, 1*inch, 1.2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 7)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
        
    def _create_recommendations(self, scan_data: Dict, attack_results: Optional[Dict]) -> list:
        """إنشاء قائمة التوصيات الأمنية"""
        
        story = []
        
        recommendations = [
            "• Upgrade all networks to WPA3 encryption where supported",
            "• Disable WPS on all access points immediately",
            "• Implement strong password policies (minimum 12 characters, complexity)",
            "• Enable MAC address filtering as an additional layer",
            "• Regularly update firmware on all wireless equipment",
            "• Implement network segmentation for guest networks",
            "• Deploy Wireless IDS/IPS for continuous monitoring",
            "• Conduct regular security audits and penetration testing"
        ]
        
        if attack_results and attack_results.get('success'):
            recommendations.insert(0, "🔴 URGENT: Change compromised passwords immediately")
            recommendations.insert(1, "🔴 URGENT: Review and enhance authentication mechanisms")
            
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['CustomBody']))
            story.append(Spacer(1, 0.1*inch))
            
        return story
        
    def _create_disclaimer(self) -> Paragraph:
        """إنشاء إخلاء المسؤولية القانونية"""
        
        disclaimer_text = """
        <b>LEGAL DISCLAIMER</b><br/><br/>
        This report was generated by WiFiNexus Guardian for authorized security assessment purposes only. 
        The information contained herein is confidential and intended solely for the use of authorized personnel.<br/><br/>
        
        <b>Important Notice:</b><br/>
        • Unauthorized access to computer networks is illegal in most jurisdictions<br/>
        • This tool must only be used on networks you own or have explicit written permission to test<br/>
        • The authors assume no liability for misuse of this software<br/>
        • All findings should be remediated promptly to ensure network security<br/><br/>
        
        © 2024 WiFiNexus Guardian - For Educational and Authorized Security Testing Only
        """
        
        return Paragraph(disclaimer_text, self.styles['CustomBody'])
        
    def _generate_text_report(
        self,
        scan_data: Dict,
        attack_results: Optional[Dict],
        wids_alerts: Optional[List],
        output_path: Path
    ) -> str:
        """توليد تقرير نصي بديل"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("WiFiNexus Guardian - Security Assessment Report\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Networks: {scan_data.get('total_networks', 0)}\n")
            f.write(f"Vulnerable: {scan_data.get('vulnerable_count', 0)}\n\n")
            
            f.write("-" * 80 + "\n")
            f.write("NETWORK SCAN RESULTS\n")
            f.write("-" * 80 + "\n")
            
            for net in scan_data.get('networks', [])[:20]:
                f.write(f"SSID: {net.get('ssid', 'Hidden')}\n")
                f.write(f"BSSID: {net.get('bssid', 'N/A')}\n")
                f.write(f"Signal: {net.get('signal', 0)} dBm\n")
                f.write(f"Encryption: {net.get('encryption', 'Unknown')}\n")
                f.write(f"Channel: {net.get('channel', 'N/A')}\n")
                f.write("\n")
                
            if attack_results:
                f.write("-" * 80 + "\n")
                f.write("ATTACK RESULTS\n")
                f.write("-" * 80 + "\n")
                
                for attack in attack_results.get('attacks', []):
                    status = "SUCCESS" if attack.get('success') else "FAILED"
                    f.write(f"Attack: {attack.get('type')}\n")
                    f.write(f"Target: {attack.get('target')}\n")
                    f.write(f"Status: {status}\n")
                    f.write(f"Duration: {attack.get('duration')}\n\n")
                    
                if attack_results.get('cracked_password'):
                    f.write(f"!!! PASSWORD CRACKED: {attack_results.get('cracked_password')} !!!\n\n")
                    
            f.write("-" * 80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            f.write("• Upgrade to WPA3 encryption\n")
            f.write("• Disable WPS\n")
            f.write("• Use strong passwords\n")
            f.write("• Regular security audits\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("LEGAL DISCLAIMER: For authorized testing only\n")
            f.write("=" * 80 + "\n")
            
        print(f"{Colors.GREEN}✓ Text report generated: {output_path}{Colors.RESET}")
        return str(output_path)


if __name__ == "__main__":
    # مثال على الاستخدام
    generator = ProfessionalReportGenerator()
    
    # بيانات تجريبية
    sample_scan = {
        'total_networks': 15,
        'vulnerable_count': 3,
        'encrypted_count': 10,
        'open_count': 2,
        'networks': [
            {'ssid': 'HomeWiFi', 'bssid': 'AA:BB:CC:DD:EE:FF', 'signal': -45, 'encryption': 'WPA2', 'channel': 6},
            {'ssid': 'Office_Network', 'bssid': '11:22:33:44:55:66', 'signal': -60, 'encryption': 'WPA3', 'channel': 11},
            {'ssid': 'Guest_WiFi', 'bssid': '77:88:99:AA:BB:CC', 'signal': -75, 'encryption': 'WEP', 'channel': 1}
        ]
    }
    
    sample_attacks = {
        'success': True,
        'cracked_password': 'TestPassword123',
        'attacks': [
            {'type': 'PMKID Attack', 'target': 'AA:BB:CC:DD:EE:FF', 'success': True, 'duration': '45s', 'notes': 'Successful'},
            {'type': 'Handshake Capture', 'target': '11:22:33:44:55:66', 'success': False, 'duration': '120s', 'notes': 'No clients'}
        ]
    }
    
    report_path = generator.generate_security_assessment_report(sample_scan, sample_attacks)
    print(f"Report saved to: {report_path}")
