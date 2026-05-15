#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Process Cleanup & Safety System
نظام تنظيف العمليات والحماية التلقائية
يضمن إغلاق جميع العمليات الخلفية عند انتهاء البرنامج أو انقطاعه
المطور: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
الإصدار: 1.1.0 Pro
"""

import subprocess
import signal
import sys
import os
import atexit
from typing import List, Optional

class ProcessCleanupManager:
    """
    مدير عمليات التنظيف والسلامة
    يراقب العمليات الفرعية ويضمن إغلاقها بشكل نظيف
    """
    
    def __init__(self):
        self.active_processes: List[subprocess.Popen] = []
        self.monitor_mode_interfaces: List[str] = []
        self.is_cleaning = False
        
        # تسجيل دالة التنظيف عند خروج البرنامج
        atexit.register(self.cleanup_all)
        
        # التعامل مع إشارات النظام (SIGINT, SIGTERM)
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("[+] تم تهيئة نظام تنظيف العمليات والحماية.")

    def register_process(self, process: subprocess.Popen):
        """تسجيل عملية فرعية لمراقبتها"""
        self.active_processes.append(process)
        # print(f"[*] تم تسجيل العملية PID: {process.pid}")

    def unregister_process(self, process: subprocess.Popen):
        """إلغاء تسجيل عملية انتهت"""
        if process in self.active_processes:
            self.active_processes.remove(process)

    def enable_monitor_mode(self, interface: str):
        """تسجيل واجهة تم تفعيل وضع المراقبة عليها لاستعادتها لاحقاً"""
        if interface not in self.monitor_mode_interfaces:
            self.monitor_mode_interfaces.append(interface)
            # print(f"[*] تم تسجيل الواجهة {interface} كوضعة مراقبة.")

    def disable_monitor_mode(self, interface: str):
        """محاولة إعادة الواجهة لوضع الإدارة العادي"""
        try:
            # محاولة استخدام airmon-ng
            subprocess.run(['airmon-ng', 'stop', interface], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            # أو استخدام iw
            subprocess.run(['iw', 'dev', interface, 'set', 'type', 'managed'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
            
            if interface in self.monitor_mode_interfaces:
                self.monitor_mode_interfaces.remove(interface)
            print(f"[+] تم إعادة الواجهة {interface} لوضع الإدارة.")
        except Exception as e:
            print(f"[-] فشل إعادة الواجهة {interface}: {e}")

    def kill_process(self, process: subprocess.Popen, force: bool = False):
        """إيقاف عملية معينة بشكل آمن"""
        if process.poll() is None: # العملية لا تزال تعمل
            try:
                if force:
                    process.kill()
                else:
                    process.terminate()
                
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                    
                print(f"[+] تم إيقاف العملية PID: {process.pid}")
                self.unregister_process(process)
            except Exception as e:
                print(f"[-] خطأ أثناء إيقاف العملية {process.pid}: {e}")

    def cleanup_all(self):
        """تنظيف شامل لجميع العمليات والواجهات"""
        if self.is_cleaning:
            return
        self.is_cleaning = True
        
        print("\n[!] بدء عملية التنظيف الشامل...")
        
        # 1. إيقاف جميع العمليات الفرعية
        for proc in self.active_processes[:]: # نسخة من القائمة لتجنب التعديل أثناء التكرار
            self.kill_process(proc, force=True)
        
        # 2. إعادة واجهات المراقبة لوضعها الطبيعي
        for iface in self.monitor_mode_interfaces[:]:
            self.disable_monitor_mode(iface)
        
        # 3. قتل أي عمليات عالقة معروفة بأسمائها
        dangerous_procs = ['aireplay-ng', 'airodump-ng', 'mdk4', 'hcxdumptool', 'tshark']
        for proc_name in dangerous_procs:
            try:
                # استخدام pkill أو killall
                subprocess.run(['pkill', '-9', proc_name], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['killall', '-9', proc_name], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass # قد لا تكون الأداة موجودة
        
        print("[+] اكتمل التنظيف الشامل. يمكن الخروج بأمان.")
        self.is_cleaning = False

    def signal_handler(self, signum, frame):
        """معالجة إشارات المقاطعة (Ctrl+C)"""
        sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
        print(f"\n[!] تم استلام إشارة {sig_name}. بدء الإغلاق الآمن...")
        self.cleanup_all()
        sys.exit(0)

# مثال للاستخدام
if __name__ == "__main__":
    print("=== اختبار نظام التنظيف ===")
    cleaner = ProcessCleanupManager()
    
    # محاكاة تشغيل عملية
    try:
        print("[*] تشغيل عملية وهمية (sleep)...")
        proc = subprocess.Popen(['sleep', '10'])
        cleaner.register_process(proc)
        
        print("[*] انتظار 2 ثانية ثم مقاطعة...")
        import time
        time.sleep(2)
        
        # محاكاة Ctrl+C برمجياً ليس ضرورياً هنا، سنستدعي التنظيف يدوياً
        cleaner.cleanup_all()
        
    except KeyboardInterrupt:
        print("\nتمت المقاطعة.")
        cleaner.cleanup_all()
