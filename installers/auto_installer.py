#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Automatic Installer
تثبيت تلقائي لجميع المتطلبات والأدوات الخارجية

المؤلف: فريق WiFiNexus Guardian
الترخيص: MIT (للاستخدام التعليمي والقانوني فقط)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict, Optional
import time

class Colors:
    """ألوان لل终端"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class AutoInstaller:
    """مثبت تلقائي ذكي"""
    
    def __init__(self):
        self.system = platform.system()
        self.arch = platform.machine()
        self.is_root = os.geteuid() == 0 if self.system != "Windows" else False
        
        # قوائم الأدوات حسب النظام
        self.linux_tools = {
            'essential': [
                'python3', 'python3-pip', 'git', 'curl', 'wget',
                'aircrack-ng', 'hashcat', 'hcxdumptool', 'hcxtools',
                'wireshark', 'tshark', 'reaver', 'bully', 'cowpatty',
                'macchanger', 'iw', 'wireless-tools', 'net-tools'
            ],
            'optional': [
                'john', 'hydra', 'nmap', 'tcpdump', 'sslstrip'
            ]
        }
        
        self.windows_tools = {
            'essential': [
                'Npcap', 'Wireshark', 'AirCrack-NG-Windows',
                'Hashcat', 'WinPcap'
            ],
            'optional': [
                'Netcat', 'PuTTY', 'Nmap'
            ]
        }
        
        self.python_packages = [
            'scapy', 'cryptography', 'requests', 'colorama',
            'asyncio', 'aiohttp', 'psutil', 'netifaces',
            'pyric', 'pandas', 'matplotlib', 'seaborn',
            'reportlab', 'jinja2', 'pyyaml', 'click',
            'rich', 'questionary', 'tabulate'
        ]
        
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("=" * 60)
        print("   WiFiNexus Guardian - Automatic Installer")
        print("   المثبت التلقائي الشامل")
        print("=" * 60)
        print(f"{Colors.RESET}")
        
    def log(self, message: str, level: str = "INFO"):
        """تسجيل الرسائل"""
        timestamp = time.strftime("%H:%M:%S")
        if level == "SUCCESS":
            color = Colors.GREEN
        elif level == "ERROR":
            color = Colors.RED
        elif level == "WARNING":
            color = Colors.YELLOW
        else:
            color = Colors.WHITE
            
        print(f"{color}[{timestamp}] [{level}] {message}{Colors.RESET}")
        
    def check_root(self) -> bool:
        """التحقق من صلاحيات الجذر"""
        if self.system == "Windows":
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        return self.is_root
        
    def run_command(self, command: List[str], capture: bool = False) -> tuple:
        """تشغيل أمر نظامي"""
        try:
            if capture:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(command, timeout=300)
                return result.returncode == 0, "", ""
        except subprocess.TimeoutExpired:
            self.log(f"Timeout: {' '.join(command)}", "ERROR")
            return False, "", "Timeout"
        except Exception as e:
            self.log(f"Error running command: {e}", "ERROR")
            return False, "", str(e)
            
    def detect_package_manager(self) -> Optional[str]:
        """كشف مدير الحزم في لينكس"""
        managers = [
            ('apt', ['apt', '--version']),
            ('yum', ['yum', '--version']),
            ('dnf', ['dnf', '--version']),
            ('pacman', ['pacman', '--version']),
            ('zypper', ['zypper', '--version'])
        ]
        
        for name, cmd in managers:
            success, _, _ = self.run_command(cmd, capture=True)
            if success:
                return name
                
        return None
        
    def install_linux_packages(self, packages: List[str], manager: str) -> bool:
        """تثبيت حزم لينكس"""
        install_commands = {
            'apt': ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y'],
            'yum': ['sudo', 'yum', 'install', '-y'],
            'dnf': ['sudo', 'dnf', 'install', '-y'],
            'pacman': ['sudo', 'pacman', '-Sy', '--noconfirm'],
            'zypper': ['sudo', 'zypper', 'install', '-y']
        }
        
        if manager not in install_commands:
            self.log(f"Unsupported package manager: {manager}", "ERROR")
            return False
            
        base_cmd = install_commands[manager]
        
        # تثبيت الحزم مجموعة مجموعة
        batch_size = 5
        for i in range(0, len(packages), batch_size):
            batch = packages[i:i+batch_size]
            cmd = base_cmd + batch
            
            # معالجة خاصة لـ apt مع &&
            if manager == 'apt' and i == 0:
                # تحديث ثم تثبيت
                update_cmd = ['sudo', 'apt', 'update']
                self.log("Updating package lists...", "INFO")
                self.run_command(update_cmd)
                
            self.log(f"Installing: {', '.join(batch)}", "INFO")
            success, _, _ = self.run_command(cmd)
            
            if not success:
                self.log(f"Failed to install batch: {batch}", "WARNING")
                
        return True
        
    def install_windows_tools(self, tools: List[str]) -> bool:
        """تثبيت أدوات ويندوز"""
        self.log("Windows installation requires manual steps", "WARNING")
        self.log("Please download and install the following tools manually:", "INFO")
        
        for tool in tools:
            print(f"  - {tool}")
            
        self.log("Visit official websites for downloads", "INFO")
        return True
        
    def install_python_packages(self) -> bool:
        """تثبيت حزم بايثون"""
        self.log("Installing Python packages...", "INFO")
        
        # ترقية pip أولاً
        self.run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        
        # تثبيت الحزم
        failed = []
        for package in self.python_packages:
            self.log(f"Installing {package}...", "INFO")
            success, stdout, stderr = self.run_command(
                [sys.executable, '-m', 'pip', 'install', package],
                capture=True
            )
            
            if not success:
                self.log(f"Failed to install {package}", "WARNING")
                failed.append(package)
            else:
                self.log(f"✓ {package} installed", "SUCCESS")
                
        if failed:
            self.log(f"Failed packages: {', '.join(failed)}", "WARNING")
            
        return len(failed) == 0
        
    def verify_installation(self) -> Dict[str, bool]:
        """التحقق من التثبيت"""
        results = {}
        
        # التحقق من أدوات النظام
        system_tools = ['aircrack-ng', 'hashcat', 'tshark', 'python3'] if self.system != "Windows" else ['python.exe']
        
        for tool in system_tools:
            cmd = ['which', tool] if self.system != "Windows" else ['where', tool]
            success, _, _ = self.run_command(cmd, capture=True)
            results[tool] = success
            
        # التحقق من حزم بايثون
        python_packages = ['scapy', 'cryptography', 'requests']
        for package in python_packages:
            try:
                __import__(package)
                results[f'py_{package}'] = True
            except ImportError:
                results[f'py_{package}'] = False
                
        return results
        
    def create_wrapper_scripts(self):
        """إنشاء سكريبتات التشغيل"""
        self.log("Creating wrapper scripts...", "INFO")
        
        # سكريبت التشغيل الرئيسي
        main_script = """#!/bin/bash
# WiFiNexus Guardian Launcher
cd "$(dirname "$0")"
python3 main.py "$@"
"""
        
        with open('run.sh', 'w') as f:
            f.write(main_script)
        os.chmod('run.sh', 0o755)
        
        # سكريبت التحديث
        update_script = """#!/bin/bash
git pull origin main
python3 -m pip install -r requirements.txt
"""
        
        with open('update.sh', 'w') as f:
            f.write(update_script)
        os.chmod('update.sh', 0o755)
        
        self.log("✓ Wrapper scripts created", "SUCCESS")
        
    def generate_requirements(self):
        """توليد ملف requirements.txt"""
        self.log("Generating requirements.txt...", "INFO")
        
        with open('requirements.txt', 'w') as f:
            for package in self.python_packages:
                f.write(f"{package}\n")
                
        self.log("✓ requirements.txt generated", "SUCCESS")
        
    def run(self):
        """تشغيل عملية التثبيت الكاملة"""
        self.log("Starting installation process...", "INFO")
        self.log(f"System: {self.system} ({self.arch})", "INFO")
        self.log(f"Root/Admin: {'Yes' if self.check_root() else 'No'}", "INFO")
        
        # الخطوة 1: التحقق من الصلاحيات
        if not self.check_root() and self.system != "Windows":
            self.log("Running without root privileges. Some features may fail.", "WARNING")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                self.log("Installation cancelled", "ERROR")
                return
                
        # الخطوة 2: تثبيت أدوات النظام
        if self.system == "Linux":
            manager = self.detect_package_manager()
            if manager:
                self.log(f"Detected package manager: {manager}", "SUCCESS")
                self.install_linux_packages(
                    self.linux_tools['essential'] + self.linux_tools['optional'],
                    manager
                )
            else:
                self.log("Could not detect package manager", "ERROR")
                
        elif self.system == "Windows":
            self.install_windows_tools(
                self.windows_tools['essential'] + self.windows_tools['optional']
            )
            
        elif self.system == "Darwin":  # macOS
            self.log("macOS detected. Install Homebrew tools manually:", "INFO")
            self.log("brew install aircrack-ng hashcat wireshark", "INFO")
            
        # الخطوة 3: تثبيت حزم بايثون
        self.install_python_packages()
        
        # الخطوة 4: إنشاء الملفات المساعدة
        self.generate_requirements()
        self.create_wrapper_scripts()
        
        # الخطوة 5: التحقق النهائي
        self.log("Verifying installation...", "INFO")
        results = self.verify_installation()
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}Installation Summary:{Colors.RESET}")
        print(f"  Successful: {success_count}/{total_count}")
        
        for item, status in results.items():
            icon = "✓" if status else "✗"
            color = Colors.GREEN if status else Colors.RED
            print(f"  {color}{icon} {item}{Colors.RESET}")
            
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        if success_count == total_count:
            self.log("🎉 Installation completed successfully!", "SUCCESS")
            self.log("Run './run.sh' to start WiFiNexus Guardian", "INFO")
        else:
            self.log("⚠️  Some components failed to install", "WARNING")
            self.log("Check the logs above and install manually if needed", "INFO")

if __name__ == "__main__":
    installer = AutoInstaller()
    installer.run()
