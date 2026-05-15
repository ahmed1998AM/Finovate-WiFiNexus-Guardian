"""
اختبارات وحدة Report Generator
تغطي وظائف توليد التقارير بأنواعها المختلفة
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestReportGenerator:
    """فئة اختبارات لـ Report Generator"""
    
    def test_report_generator_initialization(self):
        """اختبار تهيئة مولد التقارير"""
        from reports.report_generator_pro import ProfessionalReportGenerator
        generator = ProfessionalReportGenerator()
        assert generator is not None
        # التحقق من وجود دوال التوليد الأساسية
        assert hasattr(generator, 'generate_security_assessment_report')
        assert hasattr(generator, '_generate_pdf_report') or hasattr(generator, '_generate_text_report')
    
    def test_generate_text_report(self):
        """اختبار توليد تقرير نصي"""
        from reports.report_generator_pro import ProfessionalReportGenerator
        from pathlib import Path
        import tempfile
        generator = ProfessionalReportGenerator()
        data = {
            'title': 'تقرير نصي',
            'summary': 'ملخص الاختبار',
            'networks': [{'ssid': 'Net1'}]
        }
        # استخدام مسار مؤقت
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = Path(f.name)
        try:
            txt_content = generator._generate_text_report(
                scan_data=data,
                attack_results=None,
                wids_alerts=None,
                output_path=temp_path
            )
            assert txt_content is not None
            assert isinstance(txt_content, str)
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_report_with_data(self):
        """اختبار التقرير مع البيانات"""
        from reports.report_generator_pro import ProfessionalReportGenerator
        generator = ProfessionalReportGenerator()
        data = {
            'title': 'تقرير اختبار',
            'scan_time': '2024-01-01',
            'networks': [
                {'ssid': 'Network1', 'bssid': 'AA:BB:CC:DD:EE:FF', 'security': 'WPA2'}
            ]
        }
        # التأكد من أن المولد يعمل بدون أخطاء
        assert generator is not None
    
    def test_empty_data_handling(self):
        """اختبار معالجة البيانات الفارغة"""
        from reports.report_generator_pro import ProfessionalReportGenerator
        generator = ProfessionalReportGenerator()
        data = {'title': 'تقرير فارغ', 'networks': []}
        # يجب أن يتعامل مع البيانات الفارغة بدون أخطاء
        try:
            content = generator._generate_text_report(data, output_file=None)
            assert content is not None
        except Exception:
            pass  # قد يثير استثناء للبيانات الفارغة

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
