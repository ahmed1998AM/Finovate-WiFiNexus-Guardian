"""
Unit Tests for Handshake Capturer Module
اختبارات وحدة التقاط Handshake
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestHandshakeCapturer(unittest.TestCase):
    """اختبارات فئة HandshakeCapturer"""

    def setUp(self):
        """إعداد البيئة قبل كل اختبار"""
        from network.handshake_capturer import HandshakeCapturer
        self.capturer = HandshakeCapturer()

    def test_initialization(self):
        """اختبار التهيئة الصحيحة"""
        self.assertIsNotNone(self.capturer.interface)
        self.assertEqual(self.capturer.capture_timeout, 120)
        self.assertFalse(self.capturer.is_capturing)

    def test_deauth_attack_validation(self):
        """اختبار التحقق من هجوم Deauth"""
        # اختبار عناوين MAC صالحة
        valid_bssid = 'AA:BB:CC:DD:EE:FF'
        valid_client = '11:22:33:44:55:66'
        
        # يجب أن تمر العناوين الصالحة
        try:
            self.capturer._validate_mac_address(valid_bssid)
            self.capturer._validate_mac_address(valid_client)
        except ValueError:
            self.fail("_validate_mac_address() raised ValueError unexpectedly")

    def test_invalid_bssid_format(self):
        """اختبار تنسيق BSSID غير صالح"""
        with self.assertRaises(ValueError):
            self.capturer._validate_mac_address('INVALID')

    def test_handshake_detection(self):
        """اختبار كشف الـ Handshake"""
        # محاكاة ملف pcap يحتوي على handshake
        with patch('os.path.exists', return_value=True):
            with patch.object(self.capturer, '_verify_handshake', return_value=True):
                result = self.capturer.verify_handshake('/fake/path/capture.pcap')
                self.assertTrue(result)

    def test_capture_directory_creation(self):
        """اختبار إنشاء مجلد الالتقاط"""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            self.capturer.capture_dir = tmpdir
            # يجب ألا يثير استثناء
            path = self.capturer._get_capture_path('TestNetwork')
            self.assertIn('TestNetwork', path)

    def test_process_cleanup_on_stop(self):
        """اختبار تنظيف العمليات عند الإيقاف"""
        mock_process = Mock()
        mock_process.poll.return_value = None  # العملية تعمل
        
        self.capturer.active_processes.append(mock_process)
        self.capturer.stop()
        
        # يجب استدعاء terminate للعملية
        mock_process.terminate.assert_called_once()

    def tearDown(self):
        """تنظيف بعد كل اختبار"""
        if hasattr(self.capturer, 'stop'):
            self.capturer.stop()


class TestDeauthEngine(unittest.TestCase):
    """اختبارات محرك هجوم Deauth"""

    def test_deauth_packet_construction(self):
        """اختبار بناء حزمة Deauth"""
        from network.handshake_capturer import DeauthEngine
        
        engine = DeauthEngine()
        bssid = 'AA:BB:CC:DD:EE:FF'
        client = '11:22:33:44:55:66'
        
        # يجب أن تُبنى الحزمة بدون أخطاء
        packet = engine.build_deauth_frame(bssid, client)
        self.assertIsNotNone(packet)

    def test_broadcast_deauth(self):
        """اختبار حزمة Deauth للإذاعة العامة"""
        from network.handshake_capturer import DeauthEngine
        
        engine = DeauthEngine()
        bssid = 'AA:BB:CC:DD:EE:FF'
        
        # حزمة broadcast
        packet = engine.build_deauth_frame(bssid, 'FF:FF:FF:FF:FF:FF')
        self.assertIsNotNone(packet)


if __name__ == '__main__':
    unittest.main()
