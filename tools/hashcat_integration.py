#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - وحدة اختبار التكامل مع Hashcat
واجهة برمجية للتعامل مع Hashcat لكسر كلمات المرور
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class HashcatIntegration:
    """تكامل مع أداة Hashcat لكسر كلمات المرور"""
    
    # أنواع الهجوم الشائعة لـ WiFi
    ATTACK_MODES = {
        "dictionary": 0,      # هجوم القاموس
        "combinator": 1,      # هجوم الدمج
        "bruteforce": 3,      # هجوم القوة الغاشمة
        "hybrid_wordlist": 6, # هجوم هجين
        "hybrid_bruteforce": 7 # هجوم هجين عكسي
    }
    
    # أنواع الهاش المعروفة
    HASH_TYPES = {
        "WPA_PMKID": 16800,    # PMKID hash
        "WPA_HANDSHAKE": 2500, # WPA/WPA2 handshake
        "WPS_PIN": 22000       # WPS PIN
    }
    
    def __init__(self, hashcat_path: str = "hashcat"):
        """
        تهيئة التكامل مع Hashcat
        
        Args:
            hashcat_path: مسار تنفيذي لـ hashcat
        """
        self.hashcat_path = hashcat_path
        self.hashcat_available = self._check_hashcat()
        self.output_dir = Path("hashcat_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_hashcat(self) -> bool:
        """التحقق من توفر Hashcat"""
        try:
            result = subprocess.run(
                [self.hashcat_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def get_hashcat_info(self) -> Dict:
        """الحصول على معلومات Hashcat"""
        if not self.hashcat_available:
            return {"available": False}
        
        try:
            result = subprocess.run(
                [self.hashcat_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            version_line = result.stdout.split('\n')[0] if result.stdout else "Unknown"
            
            # الحصول على قائمة الأجهزة
            devices_result = subprocess.run(
                [self.hashcat_path, "-I"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "available": True,
                "version": version_line,
                "devices": devices_result.stdout[:2000] if devices_result.stdout else "N/A"
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def convert_handshake_to_hashcat(self, handshake_file: str, 
                                     output_file: Optional[str] = None) -> str:
        """
        تحويل ملف Handshake إلى صيغة Hashcat
        
        Args:
            handshake_file: مسار ملف الـ handshake (cap أو pcap)
            output_file: مسار الملف الناتج (اختياري)
        
        Returns:
            مسار الملف المحول
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.output_dir / f"hash_{timestamp}.hccapx")
        
        # استخدام hcxpcaptool لتحويل الملف
        try:
            # محاولة استخدام hcxpcapngtool
            result = subprocess.run([
                "hcxpcapngtool",
                "-o", output_file,
                handshake_file
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return output_file
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # طريقة بديلة: استخدام hashcat مباشرة مع cap file
        # بعض إصدارات hashcat تدعم cap مباشرة
        return handshake_file
    
    def run_attack(self, hash_file: str, wordlist: str, 
                   attack_mode: str = "dictionary",
                   hash_type: str = "WPA_PMKID",
                   rules_file: Optional[str] = None,
                   gpu_temp_limit: int = 90,
                   workload_profile: int = 2) -> Dict:
        """
        تشغيل هجوم Hashcat
        
        Args:
            hash_file: ملف الهاش
            wordlist: ملف قائمة الكلمات
            attack_mode: نمط الهجوم (dictionary, bruteforce, etc.)
            hash_type: نوع الهاش
            rules_file: ملف القواعد (للهجمات الهجينة)
            gpu_temp_limit: حد حرارة GPU
            workload_profile: ملف عبء العمل (1-4)
        
        Returns:
            نتائج الهجوم
        """
        if not self.hashcat_available:
            return {"success": False, "error": "Hashcat غير متوفر"}
        
        mode_num = self.ATTACK_MODES.get(attack_mode, 0)
        hash_num = self.HASH_TYPES.get(hash_type, 16800)
        
        # بناء الأمر
        cmd = [
            self.hashcat_path,
            "-m", str(hash_num),
            "-a", str(mode_num),
            hash_file,
            wordlist,
            "--gpu-temp-abort", str(gpu_temp_limit),
            "--workload-profile", str(workload_profile),
            "--potfile-path", str(self.output_dir / "hashcat.pot"),
            "-o", str(self.output_dir / "cracked.txt")
        ]
        
        # إضافة القواعد إذا وجدت
        if rules_file and attack_mode in ["hybrid_wordlist", "hybrid_bruteforce"]:
            cmd.extend(["-r", rules_file])
        
        start_time = datetime.now()
        
        try:
            print(f"🚀 بدء هجوم {attack_mode}...")
            print(f"   الملف: {hash_file}")
            print(f"   القائمة: {wordlist}")
            print(f"   النوع: {hash_type} ({hash_num})")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=None  # لا يوجد مهلة زمنية للهجمات الطويلة
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # تحليل النتائج
            cracked_file = self.output_dir / "cracked.txt"
            cracked_passwords = []
            
            if cracked_file.exists():
                with open(cracked_file, 'r') as f:
                    for line in f:
                        if ':' in line:
                            parts = line.strip().split(':')
                            if len(parts) >= 2:
                                cracked_passwords.append({
                                    "hash": parts[0],
                                    "password": parts[1]
                                })
            
            success = len(cracked_passwords) > 0
            
            return {
                "success": success,
                "attack_mode": attack_mode,
                "hash_type": hash_type,
                "duration_seconds": duration,
                "cracked_count": len(cracked_passwords),
                "cracked_passwords": cracked_passwords,
                "stdout": result.stdout[-1000:] if result.stdout else "",
                "stderr": result.stderr[-1000:] if result.stderr else ""
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "انتهت مهلة الهجوم"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_dictionary_attack(self, hash_file: str, wordlist: str,
                             rules_file: Optional[str] = None) -> Dict:
        """تشغيل هجوم قاموسي"""
        return self.run_attack(
            hash_file=hash_file,
            wordlist=wordlist,
            attack_mode="dictionary",
            rules_file=rules_file
        )
    
    def run_bruteforce_attack(self, hash_file: str, charset: str,
                             min_length: int = 8, max_length: int = 12) -> Dict:
        """
        تشغيل هجوم القوة الغاشمة
        
        Args:
            hash_file: ملف الهاش
            charset: مجموعة الأحرف (?l=?d=...)
            min_length: الحد الأدنى للطول
            max_length: الحد الأقصى للطول
        """
        if not self.hashcat_available:
            return {"success": False, "error": "Hashcat غير متوفر"}
        
        # إنشاء ملف هاك وهمي للقوة الغاشمة
        mask_file = self.output_dir / "mask.hcmask"
        
        # بناء الماسك
        masks = []
        for length in range(min_length, max_length + 1):
            mask = charset * length
            masks.append(mask)
        
        with open(mask_file, 'w') as f:
            f.write('\n'.join(masks))
        
        # تشغيل الهجوم
        cmd = [
            self.hashcat_path,
            "-m", str(self.HASH_TYPES["WPA_PMKID"]),
            "-a", "3",
            hash_file,
            str(mask_file),
            "-o", str(self.output_dir / "cracked.txt")
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            return {
                "success": result.returncode == 0,
                "attack_type": "bruteforce",
                "charset": charset,
                "length_range": f"{min_length}-{max_length}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def show_statistics(self, potfile_path: Optional[str] = None) -> Dict:
        """عرض إحصائيات كلمات المرور المكسورة"""
        if potfile_path is None:
            potfile_path = self.output_dir / "hashcat.pot"
        
        if not Path(potfile_path).exists():
            return {"total_cracked": 0, "passwords": []}
        
        passwords = []
        with open(potfile_path, 'r') as f:
            for line in f:
                if ':' in line:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        passwords.append(parts[-1])
        
        return {
            "total_cracked": len(passwords),
            "passwords": passwords[:100]  # أول 100 كلمة مرور
        }
    
    def generate_custom_wordlist(self, target_info: Dict, 
                                 output_file: str) -> str:
        """
        توليد قائمة كلمات مخصصة بناءً على معلومات الهدف
        
        Args:
            target_info: معلومات عن الهدف (اسم الشركة، السنة، إلخ)
            output_file: ملف الإخراج
        
        Returns:
            مسار ملف قائمة الكلمات
        """
        words = set()
        
        # إضافة الكلمات الأساسية
        if 'company' in target_info:
            company = target_info['company']
            words.add(company.lower())
            words.add(company.upper())
            words.add(company.capitalize())
            
            # إضافات شائعة
            for suffix in ['123', '2024', '2023', 'wifi', 'guest', 'admin']:
                words.add(f"{company}{suffix}")
                words.add(f"{company}_{suffix}")
        
        if 'ssid' in target_info:
            ssid = target_info['ssid']
            words.add(ssid)
            words.add(ssid.lower())
            words.add(ssid.replace(' ', ''))
        
        if 'location' in target_info:
            location = target_info['location']
            words.add(location)
            words.add(location.lower())
        
        # كتابة القائمة
        with open(output_file, 'w', encoding='utf-8') as f:
            for word in sorted(words):
                f.write(f"{word}\n")
        
        return output_file


def main():
    """اختبار تكامل Hashcat"""
    print("=" * 60)
    print("🔐 اختبار تكامل Hashcat")
    print("=" * 60)
    
    hashcat = HashcatIntegration()
    
    # التحقق من Hashcat
    info = hashcat.get_hashcat_info()
    print(f"\nحالة Hashcat: {'متوفر ✓' if info.get('available') else 'غير متوفر ✗'}")
    
    if info.get('available'):
        print(f"الإصدار: {info.get('version', 'Unknown')}")
        print("\nالأجهزة المتاحة:")
        print(info.get('devices', 'N/A')[:500])
    
    # عرض أنماط الهجوم
    print("\n" + "=" * 60)
    print("أنماط الهجوم المتاحة:")
    for name, code in HashcatIntegration.ATTACK_MODES.items():
        print(f"  • {name}: {code}")
    
    print("\nأنواع الهاش:")
    for name, code in HashcatIntegration.HASH_TYPES.items():
        print(f"  • {name}: {code}")
    
    # مثال على توليد قائمة كلمات مخصصة
    print("\n" + "=" * 60)
    print("توليد قائمة كلمات مخصصة:")
    
    target_info = {
        "company": "TechCorp",
        "ssid": "TechCorp_Guest",
        "location": "Riyadh"
    }
    
    custom_wordlist = "custom_wordlist.txt"
    output_path = hashcat.generate_custom_wordlist(target_info, custom_wordlist)
    print(f"✅ تم إنشاء قائمة الكلمات: {output_path}")
    
    # عرض المحتوى
    with open(custom_wordlist, 'r') as f:
        words = f.read().strip().split('\n')
        print(f"عدد الكلمات: {len(words)}")
        print("عينة من الكلمات:")
        for word in words[:10]:
            print(f"  - {word}")
    
    print("\n" + "=" * 60)
    print("⚠️  ملاحظة: الهجمات الفعلية تتطلب ملفات handshake حقيقية")
    print("مثال الاستخدام:")
    print("""
    from reports.hashcat_integration import HashcatIntegration
    
    hashcat = HashcatIntegration()
    
    result = hashcat.run_dictionary_attack(
        hash_file="target.hccapx",
        wordlist="rockyou.txt"
    )
    
    if result['success']:
        print(f"تم كسر كلمة المرور: {result['cracked_passwords']}")
    """)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
