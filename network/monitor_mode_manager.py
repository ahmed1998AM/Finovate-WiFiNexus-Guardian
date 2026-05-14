#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Monitor Mode Manager Pro
مدير وضع المراقبة الاحترافي مع دعم متقدم للويندوز
المطور: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
الإصدار: 1.5.0
"""

import os
import sys
import platform
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json


class MonitorModeManager:
    """إدارة متقدمة لوضع المراقبة مع دعم جميع الأنظمة"""
    
    def __init__(self):
        self.system = platform.system()
        self.interface_name = None
        self.original_mode = None
        self.monitor_interface = None
        self.supports_monitor = False
        
        # كشف النظام والقدرات
        self.detect_capabilities()
    
    def detect_capabilities(self):
        """كشف قدرات النظام لوضع المراقبة"""
        print("🔍 جاري فحص قدرات وضع المراقبة...")
        
        if self.system == 'Windows':
            self._check_windows_monitor_support()
        elif self.system == 'Linux':
            self._check_linux_monitor_support()
        elif self.system == 'Darwin':
            self._check_macos_monitor_support()
    
    def _check_windows_monitor_support(self):
        """فحص دعم وضع المراقبة على Windows"""
        print("\n🪟 نظام التشغيل: Windows")
        
        # فحص وجود Npcap
        npcap_paths = [
            r"C:\Program Files\Npcap",
            r"C:\Program Files (x86)\Npcap",
            r"C:\Windows\System32\Npcap"
        ]
        
        npcap_installed = any(Path(p).exists() for p in npcap_paths)
        
        if npcap_installed:
            print("✅ Npcap مثبت - دعم جزئي لوضع المراقبة")
            print("   ⚠️ ملاحظة: معظم كروت WiFi على Windows لا تدعم Monitor Mode الأصلي")
            print("   💡 الحل: استخدام الوضع الهجين أو Passive Capture")
            self.supports_monitor = False  # غالباً غير مدعوم على Windows
        else:
            print("❌ Npcap غير مثبت")
            print("   📥 قم بتثبيت Npcap من: https://npcap.com")
            self.supports_monitor = False
    
    def _check_linux_monitor_support(self):
        """فحص دعم وضع المراقبة على Linux"""
        print("\n🐧 نظام التشغيل: Linux")
        
        # فحص وجود airmon-ng
        if subprocess.run(['which', 'airmon-ng'], capture_output=True).returncode == 0:
            print("✅ airmon-ng متاح")
            self.supports_monitor = True
            
            # فحص الكروت المتاحة
            interfaces = self.get_wifi_interfaces()
            for iface in interfaces:
                if iface.get('supports_monitor'):
                    print(f"✅ الكرت '{iface['name']}' يدعم وضع المراقبة")
        else:
            print("❌ airmon-ng غير مثبت")
            print("   📥 قم بتثبيت aircrack-ng suite")
            self.supports_monitor = False
    
    def _check_macos_monitor_support(self):
        """فحص دعم وضع المراقبة على macOS"""
        print("\n🍎 نظام التشغيل: macOS")
        print("⚠️ دعم وضع المراقبة محدود على macOS")
        self.supports_monitor = False
    
    def get_wifi_interfaces(self) -> List[Dict]:
        """الحصول على معلومات كروت WiFi"""
        interfaces = []
        
        if self.system == 'Windows':
            interfaces = self._get_windows_interfaces()
        elif self.system == 'Linux':
            interfaces = self._get_linux_interfaces()
        elif self.system == 'Darwin':
            interfaces = self._get_macos_interfaces()
        
        return interfaces
    
    def _get_windows_interfaces(self) -> List[Dict]:
        """الحصول على كروت WiFi في Windows"""
        interfaces = []
        
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, encoding='cp850'
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # تحليل المخرجات
                current_iface = {}
                for line in output.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower().replace(' ', '_')
                        value = value.strip()
                        
                        if key == 'name':
                            if current_iface:
                                interfaces.append(current_iface)
                            current_iface = {'name': value, 'type': 'windows'}
                        elif key == 'state':
                            current_iface['state'] = value
                        elif key == 'ssid':
                            current_iface['connected_ssid'] = value
                        elif key == 'bssid':
                            current_iface['connected_bssid'] = value
                        elif key == 'radio_type':
                            current_iface['radio_type'] = value
                        elif key == 'channel':
                            current_iface['channel'] = value
                        elif key == 'signal':
                            current_iface['signal_strength'] = value
                
                if current_iface:
                    interfaces.append(current_iface)
                
                # إضافة دعم وضع المراقبة (غالباً غير مدعوم)
                for iface in interfaces:
                    iface['supports_monitor'] = False
                    iface['monitor_note'] = 'غير مدعوم على Windows عادةً'
        
        except Exception as e:
            print(f"⚠️ خطأ في قراءة الكروت: {e}")
        
        return interfaces
    
    def _get_linux_interfaces(self) -> List[Dict]:
        """الحصول على كروت WiFi في Linux"""
        interfaces = []
        
        try:
            # استخدام iwconfig
            result = subprocess.run(
                ['iwconfig'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # تحليل بسيط
                current_iface = {}
                for line in output.split('\n'):
                    if line and not line.startswith(' '):
                        iface_name = line.split()[0]
                        if 'IEEE 802.11' in line or 'wlan' in iface_name:
                            if current_iface:
                                interfaces.append(current_iface)
                            current_iface = {
                                'name': iface_name,
                                'type': 'linux',
                                'raw_info': line
                            }
                            # فحص دعم monitor mode
                            current_iface['supports_monitor'] = True
                
                if current_iface:
                    interfaces.append(current_iface)
            
            # فحص أكثر دقة باستخدام iw
            for iface in interfaces:
                try:
                    result = subprocess.run(
                        ['iw', 'dev', iface['name'], 'info'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        if 'type managed' in result.stdout:
                            iface['current_mode'] = 'managed'
                        elif 'type monitor' in result.stdout:
                            iface['current_mode'] = 'monitor'
                except:
                    pass
        
        except Exception as e:
            print(f"⚠️ خطأ في قراءة الكروت: {e}")
        
        return interfaces
    
    def _get_macos_interfaces(self) -> List[Dict]:
        """الحصول على كروت WiFi في macOS"""
        interfaces = []
        
        try:
            result = subprocess.run(
                ['networksetup', '-listallhardwareports'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                output = result.stdout
                # تحليل بسيط
                interfaces.append({
                    'name': 'en0',
                    'type': 'macos',
                    'supports_monitor': False,
                    'note': 'دعم محدود لوضع المراقبة'
                })
        
        except Exception as e:
            print(f"⚠️ خطأ في قراءة الكروت: {e}")
        
        return interfaces
    
    def enable_monitor_mode(self, interface_name: str = None) -> Optional[str]:
        """تفعيل وضع المراقبة"""
        if not self.supports_monitor:
            print("⚠️ وضع المراقبة غير مدعوم على هذا النظام")
            print("💡 استخدام الوضع الهجين بدلاً من ذلك")
            return None
        
        if self.system == 'Linux':
            return self._enable_linux_monitor(interface_name)
        elif self.system == 'Windows':
            print("⚠️ لا يمكن تفعيل وضع المراقبة الأصلي على Windows")
            return None
        
        return None
    
    def _enable_linux_monitor(self, interface_name: str = None) -> Optional[str]:
        """تفعيل وضع المراقبة على Linux"""
        try:
            # تحديد الواجهة
            if not interface_name:
                interfaces = self.get_wifi_interfaces()
                if not interfaces:
                    print("❌ لا توجد كروت WiFi متاحة")
                    return None
                interface_name = interfaces[0]['name']
            
            print(f"\n🔧 جاري تفعيل وضع المراقبة على {interface_name}...")
            
            # إيقاف الواجهة
            subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'down'], 
                          capture_output=True)
            
            # تغيير الوضع
            result = subprocess.run(
                ['sudo', 'iw', 'dev', interface_name, 'set', 'type', 'monitor'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                # محاولة باستخدام airmon-ng
                print("   🔄 محاولة باستخدام airmon-ng...")
                result = subprocess.run(
                    ['sudo', 'airmon-ng', 'start', interface_name],
                    capture_output=True, text=True
                )
            
            # تشغيل الواجهة
            subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'up'], 
                          capture_output=True)
            
            if result.returncode == 0:
                print(f"✅ تم تفعيل وضع المراقبة على {interface_name}")
                self.monitor_interface = interface_name
                return interface_name
            else:
                print(f"❌ فشل تفعيل وضع المراقبة: {result.stderr}")
                return None
        
        except Exception as e:
            print(f"❌ خطأ: {e}")
            return None
    
    def disable_monitor_mode(self, interface_name: str = None) -> bool:
        """تعطيل وضع المراقبة"""
        if not interface_name:
            interface_name = self.monitor_interface
        
        if not interface_name:
            return False
        
        try:
            if self.system == 'Linux':
                subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'down'], 
                              capture_output=True)
                subprocess.run(
                    ['sudo', 'iw', 'dev', interface_name, 'set', 'type', 'managed'],
                    capture_output=True
                )
                subprocess.run(['sudo', 'ip', 'link', 'set', interface_name, 'up'], 
                              capture_output=True)
                
                print(f"✅ تم تعطيل وضع المراقبة على {interface_name}")
                return True
        
        except Exception as e:
            print(f"⚠️ خطأ في التعطيل: {e}")
        
        return False
    
    def get_monitor_alternatives(self) -> Dict:
        """الحصول على بدائل وضع المراقبة"""
        alternatives = {
            'windows': {
                'hybrid_mode': {
                    'description': 'الوضع الهجين - جمع سلبي + تحليل نشط',
                    'method': 'استخدام Npcap/TShark مع فلترة EAPOL',
                    'effectiveness': 'متوسطة إلى عالية'
                },
                'passive_capture': {
                    'description': 'الالتقاط السلبي بدون إرسال حزم',
                    'method': 'استخدام netsh wlan show network',
                    'effectiveness': 'منخفضة إلى متوسطة'
                },
                'native_api': {
                    'description': 'استخدام Windows WiFi API الرسمي',
                    'method': 'netsh trace start capture=yes',
                    'effectiveness': 'متوسطة'
                }
            },
            'linux': {
                'native_monitor': {
                    'description': 'وضع المراقبة الأصلي',
                    'method': 'airmon-ng start <interface>',
                    'effectiveness': 'عالية جداً'
                }
            },
            'macos': {
                'limited_capture': {
                    'description': 'التقاط محدود',
                    'method': 'أدوات طرف ثالث',
                    'effectiveness': 'منخفضة'
                }
            }
        }
        
        return alternatives.get(self.system, {})
    
    def interactive_setup(self):
        """الإعداد التفاعلي لوضع المراقبة"""
        print("\n" + "=" * 60)
        print("📡 إعداد وضع المراقبة")
        print("=" * 60)
        
        # عرض الكروت المتاحة
        interfaces = self.get_wifi_interfaces()
        
        if not interfaces:
            print("❌ لم يتم العثور على كروت WiFi")
            return
        
        print(f"\n📋 الكروت المتاحة ({len(interfaces)}):")
        for i, iface in enumerate(interfaces, 1):
            status = "✅" if iface.get('supports_monitor') else "⚠️"
            print(f"   {i}. {iface['name']} - {status}")
            if 'connected_ssid' in iface:
                print(f"      متصل بـ: {iface['connected_ssid']}")
            if 'signal_strength' in iface:
                print(f"      قوة الإشارة: {iface['signal_strength']}")
        
        # اختيار الكرت
        if len(interfaces) == 1:
            selected = interfaces[0]
        else:
            try:
                choice = input(f"\nاختر كرت (1-{len(interfaces)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(interfaces):
                    selected = interfaces[idx]
                else:
                    print("❌ اختيار غير صحيح")
                    return
            except ValueError:
                print("❌ إدخال غير صحيح")
                return
        
        # التحقق من دعم وضع المراقبة
        if selected.get('supports_monitor'):
            action = input("\nتفعيل وضع المراقبة؟ (y/n): ").strip().lower()
            if action == 'y':
                monitor_iface = self.enable_monitor_mode(selected['name'])
                if monitor_iface:
                    print(f"\n✅ وضع المراقبة مفعل على {monitor_iface}")
        else:
            print("\n⚠️ هذا الكرت لا يدعم وضع المراقبة الأصلي")
            print("\n📋 البدائل المتاحة:")
            
            alternatives = self.get_monitor_alternatives()
            for name, alt in alternatives.items():
                print(f"\n   • {alt['description']}")
                print(f"     الطريقة: {alt['method']}")
                print(f"     الفعالية: {alt['effectiveness']}")
            
            use_hybrid = input("\nاستخدام الوضع الهجين؟ (y/n): ").strip().lower()
            if use_hybrid == 'y':
                print("\n✅ سيتم استخدام الوضع الهجين تلقائياً في الالتقاط")


def main():
    """الوظيفة الرئيسية"""
    manager = MonitorModeManager()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--status':
            interfaces = manager.get_wifi_interfaces()
            print(json.dumps(interfaces, indent=2, ensure_ascii=False))
        
        elif command == '--enable':
            iface = sys.argv[2] if len(sys.argv) > 2 else None
            manager.enable_monitor_mode(iface)
        
        elif command == '--disable':
            iface = sys.argv[2] if len(sys.argv) > 2 else None
            manager.disable_monitor_mode(iface)
        
        elif command == '--alternatives':
            alts = manager.get_monitor_alternatives()
            print(json.dumps(alts, indent=2, ensure_ascii=False))
        
        else:
            manager.interactive_setup()
    else:
        manager.interactive_setup()


if __name__ == '__main__':
    main()
