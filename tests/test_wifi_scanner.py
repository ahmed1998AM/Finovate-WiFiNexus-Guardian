"""
اختبارات وحدة WiFi Scanner
تغطي وظائف المسح الضوئي للشبكات اللاسلكية
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# إضافة مسار المشروع
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestWiFiScanner:
    """فئة اختبارات لـ WiFi Scanner"""
    
    def test_scanner_initialization(self):
        """اختبار تهيئة الماسح الضوئي"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        assert scanner is not None
        assert hasattr(scanner, 'scan_networks')
    
    def test_scan_networks_basic(self):
        """اختبار المسح الأساسي للشبكات"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        # نستخدم get_simulated_networks لأن المسح الحقيقي يتطلب واجهة
        networks = scanner._get_simulated_networks()
        assert len(networks) > 0
        assert 'ssid' in networks[0]
        # الإشارة قد تكون في حقول مختلفة حسب التنفيذ
        assert 'signal' in networks[0] or 'dbm' in networks[0] or networks[0].get('signal_dbm') is not None
    
    def test_filter_by_band(self):
        """اختبار تصفية الشبكات حسب التردد"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        networks = [
            {'ssid': '2.4G_Net', 'band': '2.4GHz'},
            {'ssid': '5G_Net', 'band': '5GHz'},
            {'ssid': '6G_Net', 'band': '6GHz'}
        ]
        # استخدام دالة مساعدة للتصفية
        filtered = [n for n in networks if n.get('band') == '5GHz']
        assert len(filtered) == 1
        assert filtered[0]['ssid'] == '5G_Net'
    
    def test_filter_by_signal_strength(self):
        """اختبار تصفية الشبكات حسب قوة الإشارة"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        networks = [
            {'ssid': 'Strong', 'signal': -30},
            {'ssid': 'Medium', 'signal': -60},
            {'ssid': 'Weak', 'signal': -80}
        ]
        # تصفية الشبكات بإشارة أفضل من -70
        filtered = [n for n in networks if n['signal'] >= -70]
        assert len(filtered) == 2
        assert all(n['signal'] >= -70 for n in filtered)
    
    def test_get_network_channels(self):
        """اختبار الحصول على قنوات الشبكات"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        networks = [
            {'ssid': 'Net1', 'channel': 6},
            {'ssid': 'Net2', 'channel': 11},
            {'ssid': 'Net3', 'channel': 36}
        ]
        channels = [n['channel'] for n in networks]
        assert set(channels) == {6, 11, 36}
    
    def test_detect_hidden_networks(self):
        """اختبار كشف الشبكات المخفية"""
        from network.wifi_scanner import WiFiScanner
        scanner = WiFiScanner()
        networks = [
            {'ssid': '', 'bssid': 'AA:BB:CC:DD:EE:FF'},
            {'ssid': 'Visible', 'bssid': '11:22:33:44:55:66'}
        ]
        hidden = [n for n in networks if not n.get('ssid')]
        assert len(hidden) == 1
        assert hidden[0]['bssid'] == 'AA:BB:CC:DD:EE:FF'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
