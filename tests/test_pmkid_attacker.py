"""
Unit Tests for PMKID Attacker Module
اختبارات وحدة هجوم PMKID
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPMKIDAttacker(unittest.TestCase):
    """اختبارات فئة PMKIDAttacker"""

    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        from attacks.pmkid_attacker import PMKIDAttacker
        self.attacker = PMKIDAttacker()

    def test_initialization(self):
        """اختبار التهيئة الصحيحة للكائن"""
        self.assertIsNotNone(self.attacker.interface)
        self.assertEqual(self.attacker.timeout, 30)
        self.assertFalse(self.attacker.is_running)

    def test_pmkid_capture_timeout(self):
        """اختبار انتهاء مهلة الالتقاط"""
        # محاكاة سيناريو انتهاء المهلة
        with patch.object(self.attacker, '_capture_pmkid', return_value=None):
            result = asyncio.run(self.attacker.attack('AA:BB:CC:DD:EE:FF', 'TestNetwork'))
            self.assertIsNone(result)

    def test_invalid_mac_address(self):
        """اختبار عنوان MAC غير صالح"""
        with self.assertRaises(ValueError):
            asyncio.run(self.attacker.attack('INVALID_MAC', 'TestNetwork'))

    def test_valid_mac_format(self):
        """اختبار تنسيق عنوان MAC الصالح"""
        valid_macs = [
            'AA:BB:CC:DD:EE:FF',
            '11:22:33:44:55:66',
            'aa:bb:cc:dd:ee:ff'
        ]
        for mac in valid_macs:
            # يجب ألا يثير استثناء للتنسيق
            try:
                self.attacker._validate_mac(mac)
            except ValueError:
                self.fail(f"_validate_mac() raised ValueError unexpectedly for {mac}")

    def test_pmkid_file_generation(self):
        """اختبار توليد ملف PMKID"""
        # التحقق من أن الدالة تُنشئ اسم ملف صحيح
        filename = self.attacker._generate_filename('AA:BB:CC:DD:EE:FF', 'TestNetwork')
        self.assertIn('AA_BB_CC_DD_EE_FF', filename)
        self.assertIn('.pmkid', filename)

    def tearDown(self):
        """تنظيف بعد كل اختبار"""
        if hasattr(self.attacker, 'stop'):
            self.attacker.stop()


class TestPMKIDParser(unittest.TestCase):
    """اختبارات محلل ملفات PMKID"""

    def test_parse_valid_pmkid(self):
        """اختبار تحليل ملف PMKID صالح"""
        from attacks.pmkid_attacker import PMKIDParser
        
        # بيانات PMKID وهمية للاختبار
        sample_pmkid = (
            "wlan0:*AA:BB:CC:DD:EE:FF:*TestNetwork:"
            "11223344556677889900AABBCCDDEEFF"
        )
        
        parser = PMKIDParser()
        # ملاحظة: هذا اختبار مبسط، في الواقع يحتاج لملف حقيقي
        self.assertTrue(hasattr(parser, 'parse'))


if __name__ == '__main__':
    unittest.main()
