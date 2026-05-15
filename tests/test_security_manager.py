"""
Unit Tests for Security Manager Module
اختبارات وحدة إدارة الأمان والحماية
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestSecurityManager(unittest.TestCase):
    """اختبارات فئة SecurityManager"""

    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        from core.security_manager import SecurityManager
        self.security_mgr = SecurityManager()

    def test_initialization(self):
        """اختبار التهيئة الصحيحة"""
        self.assertTrue(self.security_mgr.monitoring_enabled)
        self.assertFalse(self.security_mgr.stealth_mode_active)

    def test_stealth_mode_activation(self):
        """اختبار تفعيل وضع التخفي"""
        self.security_mgr.enable_stealth_mode()
        self.assertTrue(self.security_mgr.stealth_mode_active)

    def test_stealth_mode_deactivation(self):
        """اختبار تعطيل وضع التخفي"""
        self.security_mgr.enable_stealth_mode()
        self.security_mgr.disable_stealth_mode()
        self.assertFalse(self.security_mgr.stealth_mode_active)

    def test_process_monitoring(self):
        """اختبار مراقبة العمليات"""
        # محاكاة عملية وهمية
        mock_process = Mock()
        mock_process.pid = 12345
        mock_process.name.return_value = 'test_process'
        
        self.security_mgr.monitored_processes.append(mock_process)
        
        # يجب أن تحتوي القائمة على العملية
        self.assertIn(mock_process, self.security_mgr.monitored_processes)

    def test_cleanup_all_processes(self):
        """اختبار تنظيف جميع العمليات"""
        mock_process1 = Mock()
        mock_process1.poll.return_value = None
        mock_process2 = Mock()
        mock_process2.poll.return_value = None
        
        self.security_mgr.active_processes = [mock_process1, mock_process2]
        self.security_mgr.cleanup_all()
        
        # يجب استدعاء terminate لكل عملية
        mock_process1.terminate.assert_called_once()
        mock_process2.terminate.assert_called_once()

    def test_mac_randomization(self):
        """اختبار عشوائية عنوان MAC"""
        mac1 = self.security_mgr._generate_random_mac()
        mac2 = self.security_mgr._generate_random_mac()
        
        # يجب أن يكون العنوانين مختلفين
        self.assertNotEqual(mac1, mac2)
        
        # يجب أن يكون التنسيق صحيح (XX:XX:XX:XX:XX:XX)
        import re
        mac_pattern = r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'
        self.assertRegex(mac1, mac_pattern)
        self.assertRegex(mac2, mac_pattern)

    def test_interface_check(self):
        """اختبار التحقق من وجود الواجهة"""
        # في بيئة الاختبار، نتوقع أن الواجهة الوهمية غير موجودة
        result = self.security_mgr.check_interface('nonexistent_interface')
        # الدالة يجب أن ترجع False أو تثير استثناء
        self.assertIsInstance(result, bool)

    def test_log_security_event(self):
        """اختبار تسجيل حدث أمني"""
        event_type = 'TEST_EVENT'
        message = 'Test security event'
        
        # يجب ألا يثير استثناء
        try:
            self.security_mgr.log_security_event(event_type, message)
        except Exception as e:
            self.fail(f"log_security_event() raised {type(e).__name__}: {e}")

    def tearDown(self):
        """تنظيف بعد كل اختبار"""
        if hasattr(self.security_mgr, 'cleanup_all'):
            self.security_mgr.cleanup_all()


class TestStealthMode(unittest.TestCase):
    """اختبارات وضع التخفي المتقدم"""

    def test_beacon_flooding_detection(self):
        """اختبار كشف فيضان Beacon"""
        from core.security_manager import StealthModeDetector
        
        detector = StealthModeDetector()
        # محاكاة عدد كبير من beacon frames
        beacon_count = 1000
        
        # يجب كشف الفيضان
        is_flooding = detector.detect_beacon_flood(beacon_count, threshold=500)
        self.assertTrue(is_flooding)

    def test_normal_beacon_rate(self):
        """اختبار معدل Beacon طبيعي"""
        from core.security_manager import StealthModeDetector
        
        detector = StealthModeDetector()
        beacon_count = 50
        
        # لا يجب كشف فيضان
        is_flooding = detector.detect_beacon_flood(beacon_count, threshold=500)
        self.assertFalse(is_flooding)


if __name__ == '__main__':
    unittest.main()
