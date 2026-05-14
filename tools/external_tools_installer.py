#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - External Tools Auto-Installer
مدير تثبيت الأدوات الخارجية التلقائي
المطور: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
الإصدار: 1.5.0
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ToolsAutoInstaller:
    """نظام التثبيت التلقائي للأدوات الأمنية"""
    
    def __init__(self):
        self.system = platform.system()
        self.arch = platform.machine()
        self.tools_dir = Path(__file__).parent.parent / "tools"
        self.tools_dir.mkdir(exist_ok=True)
        
        # تعريفات الأدوات
        self.tools_definitions = {
            'aircrack-ng': {
                'description': 'Suite أمان الشبكات اللاسلكية',
                'windows': {
                    'installer_url': 'https://www.aircrack-ng.org/files/aircrack-ng-1.7-win.zip',
                    'choco': 'aircrack-ng',
                    'manual': 'تحميل من الموقع الرسمي'
                },
                'linux': {
                    'apt': ['aircrack-ng', 'airmon-ng', 'airodump-ng'],
                    'yum': ['aircrack-ng'],
                    'pacman': ['aircrack-ng']
                },
                'macos': {
                    'brew': 'aircrack-ng'
                },
                'required': True,
                'category': 'capture'
            },
            'hashcat': {
                'description': 'أداة كسر كلمات المرور المتقدمة',
                'windows': {
                    'installer_url': 'https://hashcat.net/hashcat/',
                    'choco': 'hashcat'
                },
                'linux': {
                    'apt': ['hashcat'],
                    'yum': ['hashcat']
                },
                'macos': {
                    'brew': 'hashcat'
                },
                'required': False,
                'category': 'crack'
            },
            'npcap': {
                'description': 'مكتبة التقاط الحزم لـ Windows',
                'windows': {
                    'installer_url': 'https://npcap.com/dist/npcap-1.79.exe',
                    'silent_args': '/S'
                },
                'required': True,
                'category': 'driver',
                'windows_only': True
            },
            'wireshark': {
                'description': 'محلل البروتوكولات الشبكية',
                'windows': {
                    'choco': 'wireshark'
                },
                'linux': {
                    'apt': ['wireshark', 'tshark'],
                    'yum': ['wireshark']
                },
                'macos': {
                    'brew': '--cask wireshark'
                },
                'required': False,
                'category': 'analysis'
            },
            'hcxdumptool': {
                'description': 'أداة الالتقاط المتقدمة',
                'linux': {
                    'apt': ['hcxdumptool'],
                    'source': 'https://github.com/ZerBea/hcxdumptool'
                },
                'required': False,
                'category': 'capture'
            },
            'hcxtools': {
                'description': 'أدوات تحويل صيغ الهاند شيك',
                'linux': {
                    'apt': ['hcxtools'],
                    'source': 'https://github.com/ZerBea/hcxtools'
                },
                'required': False,
                'category': 'conversion'
            }
        }
    
    def detect_package_manager(self) -> str:
        """كشف مدير الحزم المتاح"""
        if self.system == 'Windows':
            # فحص Chocolatey
            if shutil.which('choco'):
                return 'chocolatey'
            return 'manual'
        
        elif self.system == 'Linux':
            if shutil.which('apt-get'):
                return 'apt'
            elif shutil.which('yum'):
                return 'yum'
            elif shutil.which('pacman'):
                return 'pacman'
            elif shutil.which('dnf'):
                return 'dnf'
            return 'source'
        
        elif self.system == 'Darwin':
            if shutil.which('brew'):
                return 'homebrew'
            return 'manual'
        
        return 'unknown'
    
    def check_tool_installed(self, tool_name: str) -> Tuple[bool, Optional[str]]:
        """فحص ما إذا كانت الأداة مثبتة"""
        tool_info = self.tools_definitions.get(tool_name)
        if not tool_info:
            return False, None
        
        # فحص المسارات الشائعة
        possible_names = [tool_name]
        if tool_name == 'aircrack-ng':
            possible_names.extend(['airmon-ng', 'airodump-ng', 'aireplay-ng'])
        
        for name in possible_names:
            path = shutil.which(name)
            if path:
                return True, path
        
        # فحص مسارات مخصصة
        tool_path = self.tools_dir / tool_name
        if tool_path.exists():
            return True, str(tool_path)
        
        return False, None
    
    def install_tool(self, tool_name: str, auto_confirm: bool = False) -> bool:
        """تثبيت أداة محددة"""
        tool_info = self.tools_definitions.get(tool_name)
        if not tool_info:
            print(f"❌ الأداة '{tool_name}' غير معروفة")
            return False
        
        # فحص التوافق مع النظام
        if tool_info.get('windows_only') and self.system != 'Windows':
            print(f"⚠️ الأداة '{tool_name}' متاحة فقط لـ Windows")
            return False
        
        print(f"\n🔧 جاري تثبيت '{tool_name}'...")
        print(f"   الوصف: {tool_info['description']}")
        
        package_manager = self.detect_package_manager()
        
        try:
            if self.system == 'Windows':
                return self._install_windows(tool_name, tool_info, package_manager, auto_confirm)
            elif self.system == 'Linux':
                return self._install_linux(tool_name, tool_info, package_manager, auto_confirm)
            elif self.system == 'Darwin':
                return self._install_macos(tool_name, tool_info, package_manager, auto_confirm)
        except Exception as e:
            print(f"❌ خطأ في التثبيت: {str(e)}")
            return False
        
        return False
    
    def _install_windows(self, tool_name: str, tool_info: Dict, pm: str, auto_confirm: bool) -> bool:
        """التثبيت على Windows"""
        win_info = tool_info.get('windows', {})
        
        if pm == 'chocolatey' and 'choco' in win_info:
            print("   📦 استخدام Chocolatey...")
            cmd = ['choco', 'install', win_info['choco'], '-y']
            if auto_confirm:
                cmd.append('--force')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ تم تثبيت '{tool_name}' بنجاح عبر Chocolatey")
                return True
            else:
                print(f"⚠️ فشل تثبيت Chocolatey: {result.stderr}")
        
        # محاولة التحميل اليدوي
        if 'installer_url' in win_info:
            print(f"   🌐 التحميل من: {win_info['installer_url']}")
            print("   ⚠️ يرجى التثبيت اليدوي من الرابط أعلاه")
            print(f"   💾 حفظ في: {self.tools_dir}")
            return True
        
        print("   ❌ لا توجد طريقة تثبيت تلقائية متاحة")
        return False
    
    def _install_linux(self, tool_name: str, tool_info: Dict, pm: str, auto_confirm: bool) -> bool:
        """التثبيت على Linux"""
        linux_info = tool_info.get('linux', {})
        
        if pm in ['apt', 'yum', 'pacman', 'dnf'] and pm in linux_info:
            packages = linux_info[pm]
            print(f"   📦 استخدام {pm.upper()}...")
            
            if pm == 'apt':
                # تحديث القائمة أولاً
                subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True)
                cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
            elif pm == 'yum':
                cmd = ['sudo', 'yum', 'install', '-y'] + packages
            elif pm == 'pacman':
                cmd = ['sudo', 'pacman', '-S', '--noconfirm'] + packages
            elif pm == 'dnf':
                cmd = ['sudo', 'dnf', 'install', '-y'] + packages
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ تم تثبيت '{tool_name}' بنجاح عبر {pm}")
                return True
            else:
                print(f"⚠️ فشل التثبيت: {result.stderr}")
        
        # التثبيت من المصدر
        if 'source' in linux_info:
            print(f"   🔨 التثبيت من المصدر: {linux_info['source']}")
            print("   يرجى اتباع التعليمات على صفحة GitHub")
            return True
        
        return False
    
    def _install_macos(self, tool_name: str, tool_info: Dict, pm: str, auto_confirm: bool) -> bool:
        """التثبيت على macOS"""
        mac_info = tool_info.get('macos', {})
        
        if pm == 'homebrew' and 'brew' in mac_info:
            print("   📦 استخدام Homebrew...")
            brew_arg = mac_info['brew']
            cmd = ['brew', 'install'] + brew_arg.split()
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ تم تثبيت '{tool_name}' بنجاح عبر Homebrew")
                return True
            else:
                print(f"⚠️ فشل التثبيت: {result.stderr}")
        
        return False
    
    def install_recommended(self, auto_confirm: bool = False) -> Dict[str, bool]:
        """تثبيت جميع الأدوات الموصى بها"""
        results = {}
        
        print("\n🚀 جاري تثبيت الأدوات الموصى بها...")
        print("=" * 60)
        
        for tool_name, tool_info in self.tools_definitions.items():
            if tool_info.get('required', False):
                installed, _ = self.check_tool_installed(tool_name)
                if not installed:
                    success = self.install_tool(tool_name, auto_confirm)
                    results[tool_name] = success
                else:
                    print(f"✅ '{tool_name}' مثبت بالفعل")
                    results[tool_name] = True
        
        return results
    
    def generate_report(self) -> Dict:
        """إنشاء تقرير حالة الأدوات"""
        report = {
            'system': self.system,
            'architecture': self.arch,
            'package_manager': self.detect_package_manager(),
            'tools': {},
            'timestamp': str(Path.home())
        }
        
        for tool_name, tool_info in self.tools_definitions.items():
            installed, path = self.check_tool_installed(tool_name)
            report['tools'][tool_name] = {
                'installed': installed,
                'path': path,
                'description': tool_info['description'],
                'required': tool_info.get('required', False),
                'category': tool_info.get('category', 'other')
            }
        
        return report
    
    def interactive_menu(self):
        """القائمة التفاعلية لإدارة الأدوات"""
        while True:
            print("\n" + "=" * 60)
            print("🛠️  مدير الأدوات الخارجية")
            print("=" * 60)
            print("1. فحص حالة الأدوات")
            print("2. تثبيت أداة محددة")
            print("3. تثبيت الأدوات الموصى بها")
            print("4. عرض التقرير")
            print("5. خروج")
            
            choice = input("\nاختر عملية (1-5): ").strip()
            
            if choice == '1':
                self.show_status()
            elif choice == '2':
                tool = input("اسم الأداة: ").strip()
                self.install_tool(tool)
            elif choice == '3':
                self.install_recommended()
            elif choice == '4':
                report = self.generate_report()
                print("\n📊 تقرير حالة الأدوات:")
                for tool, info in report['tools'].items():
                    status = "✅" if info['installed'] else "❌"
                    print(f"   {status} {tool}: {info['description']}")
            elif choice == '5':
                break
    
    def show_status(self):
        """عرض حالة جميع الأدوات"""
        print("\n📊 حالة الأدوات المثبتة:")
        print("-" * 60)
        
        for tool_name, tool_info in self.tools_definitions.items():
            installed, path = self.check_tool_installed(tool_name)
            status = "✅ مثبت" if installed else "❌ غير مثبت"
            required = "⭐ مطلوب" if tool_info.get('required') else "اختياري"
            
            print(f"\n{tool_name}:")
            print(f"   الحالة: {status}")
            print(f"   النوع: {required}")
            print(f"   الوصف: {tool_info['description']}")
            if path:
                print(f"   المسار: {path}")


def main():
    """الوظيفة الرئيسية"""
    installer = ToolsAutoInstaller()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--scan':
            installer.show_status()
        elif command == '--install':
            if len(sys.argv) > 2:
                installer.install_tool(sys.argv[2])
            else:
                print("الاستخدام: python external_tools_installer.py --install <tool_name>")
        elif command == '--install-recommended':
            installer.install_recommended(auto_confirm=True)
        elif command == '--report':
            report = installer.generate_report()
            import json
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            installer.interactive_menu()
    else:
        installer.interactive_menu()


if __name__ == '__main__':
    main()
