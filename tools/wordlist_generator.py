#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Wordlist Generator
مولد قوائم كلمات ذكي ومخصص

المؤلف: فريق WiFiNexus Guardian
الترخيص: MIT (للاستخدام التعليمي والقانوني فقط)
"""

import os
import sys
import itertools
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Optional
import json

class Colors:
    """ألوان للـ terminal"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class SmartWordlistGenerator:
    """مولد قوائم كلمات ذكي"""
    
    def __init__(self, output_dir: str = "wordlists"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # القواميس الأساسية
        self.common_words = [
            'wifi', 'wireless', 'network', 'internet', 'connection',
            'home', 'office', 'guest', 'public', 'private',
            'secure', 'safe', 'fast', 'speed', 'fiber',
            'link', 'net', 'web', 'cloud', 'data'
        ]
        
        self.brand_names = [
            'tp-link', 'd-link', 'netgear', 'asus', 'linksys',
            'cisco', 'huawei', 'zte', 'belkin', 'motorola',
            'apple', 'google', 'amazon', 'microsoft'
        ]
        
        self.default_ssids = [
            'admin', 'password', 'default', 'guest', 'user',
            '1234', '12345', '123456', '12345678', '1234567890',
            'qwerty', 'abc123', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'login', 'passw0rd', 'shadow'
        ]
        
        # أنماط الأرقام الشائعة
        self.number_patterns = [
            list(range(0, 100)),  # 0-99
            list(range(100, 1000, 10)),  # 100, 110, 120...
            [1990 + i for i in range(35)],  # سنوات الميلاد 1990-2024
            [2000 + i for i in range(25)],
            list(range(1, 13)),  # أشهر 1-12
            list(range(1, 32)),  # أيام 1-31
            [111, 222, 333, 444, 555, 666, 777, 888, 999],
            [123, 321, 1234, 4321, 12345, 54321]
        ]
        
        # رموز خاصة شائعة
        self.special_chars = ['', '_', '-', '.', '@', '#', '!']
        
        # تحويلات الحروف
        self.letter_substitutions = {
            'a': ['a', 'A', '4', '@'],
            'e': ['e', 'E', '3'],
            'i': ['i', 'I', '1', '!'],
            'o': ['o', 'O', '0'],
            's': ['s', 'S', '5', '$'],
            't': ['t', 'T', '7'],
            'l': ['l', 'L', '1'],
            'b': ['b', 'B', '8'],
            'g': ['g', 'G', '9', '6']
        }
        
    def generate_from_ssid(self, ssid: str, min_length: int = 6, max_length: int = 20) -> Set[str]:
        """توليد كلمات مرور محتملة بناءً على اسم الشبكة"""
        
        passwords = set()
        
        # تنظيف SSID
        clean_ssid = re.sub(r'[^a-zA-Z0-9]', '', ssid).lower()
        
        if not clean_ssid:
            return passwords
            
        # 1. الاسم نفسه
        passwords.add(clean_ssid)
        passwords.add(ssid.lower())
        passwords.add(ssid.upper())
        passwords.add(ssid.capitalize())
        
        # 2. مع أرقام
        for numbers in self.number_patterns[0]:
            passwords.add(f"{clean_ssid}{numbers}")
            passwords.add(f"{numbers}{clean_ssid}")
            
        # 3. مع رموز
        for char in self.special_chars:
            passwords.add(f"{clean_ssid}{char}")
            passwords.add(f"{char}{clean_ssid}")
            passwords.add(f"{clean_ssid}{char}{clean_ssid}")
            
            # مع أرقام ورموز
            for numbers in self.number_patterns[0][:20]:
                passwords.add(f"{clean_ssid}{char}{numbers}")
                passwords.add(f"{numbers}{char}{clean_ssid}")
                
        # 4. تبديل الحروف
        substituted = self._substitute_letters(clean_ssid)
        passwords.update(substituted)
        
        # 5. تكرار الأحرف
        for i in range(len(clean_ssid)):
            for count in [2, 3]:
                modified = clean_ssid[:i] + clean_ssid[i]*count + clean_ssid[i+1:]
                passwords.add(modified)
                
        # تصفية حسب الطول
        filtered = {p for p in passwords if min_length <= len(p) <= max_length}
        
        return filtered
        
    def generate_contextual_wordlist(
        self,
        target_info: Dict[str, str],
        min_length: int = 6,
        max_length: int = 20
    ) -> Set[str]:
        """توليد قائمة كلمات سياقية بناءً على معلومات الهدف"""
        
        passwords = set()
        
        # معلومات متاحة
        ssid = target_info.get('ssid', '')
        brand = target_info.get('brand', '').lower()
        location = target_info.get('location', '').lower()
        owner_name = target_info.get('owner', '').lower()
        
        # 1. من اسم الشبكة
        if ssid:
            passwords.update(self.generate_from_ssid(ssid, min_length, max_length))
            
        # 2. من العلامة التجارية
        if brand:
            passwords.add(brand)
            passwords.add(f"{brand}123")
            passwords.add(f"{brand}1234")
            passwords.add(f"admin{brand}")
            passwords.add(f"{brand}admin")
            passwords.add(f"{brand}wifi")
            passwords.add(f"{brand}password")
            
        # 3. من الموقع
        if location:
            loc_clean = re.sub(r'[^a-z]', '', location)
            passwords.add(loc_clean)
            passwords.add(f"{loc_clean}123")
            passwords.add(f"wifi{loc_clean}")
            passwords.add(f"{loc_clean}wifi")
            
        # 4. من اسم المالك
        if owner_name:
            name_clean = re.sub(r'[^a-z]', '', owner_name)
            passwords.add(name_clean)
            passwords.add(f"{name_clean}123")
            passwords.add(f"{name_clean}1990")
            passwords.add(f"{name_clean}2000")
            
            # توليد اختلافات
            passwords.update(self._substitute_letters(name_clean))
            
        # 5. توليفات
        elements = [x for x in [brand, location, owner_name] if x]
        if len(elements) >= 2:
            for combo in itertools.permutations(elements, 2):
                passwords.add(f"{combo[0]}{combo[1]}")
                passwords.add(f"{combo[0]}{combo[1]}123")
                passwords.add(f"{combo[0]}123{combo[1]}")
                
        # تصفية حسب الطول
        filtered = {p for p in passwords if min_length <= len(p) <= max_length}
        
        return filtered
        
    def generate_default_passwords(self) -> Set[str]:
        """توليد قائمة بكلمات المرور الافتراضية"""
        
        passwords = set()
        
        # كلمات مرور افتراضية شائعة
        defaults = [
            'admin', 'password', 'administrator', 'default', 'guest',
            '1234', '12345', '123456', '12345678', '123456789', '1234567890',
            'password1', 'password123', 'admin123', 'root', 'toor',
            'qwerty', 'abc123', 'letmein', 'welcome', 'monkey',
            'dragon', 'master', 'login', 'passw0rd', 'shadow',
            'sunshine', 'princess', 'football', 'baseball', 'iloveyou',
            'trustno1', 'superman', 'batman', 'starwars', 'hello',
            'charlie', 'donald', 'loveme', 'michael', 'ashley',
            'bailey', 'access', 'mustang', 'metallica', 'shadow',
            'computer', 'internet', 'batman', 'superman', 'hello'
        ]
        
        passwords.update(defaults)
        
        # كلمات مرور افتراضية حسب الشركة المصنعة
        brand_defaults = {
            'tp-link': ['admin', 'tp-link'],
            'd-link': ['admin', 'password', ''],
            'netgear': ['password', 'admin', '1234'],
            'asus': ['admin', 'password', 'asus'],
            'linksys': ['admin', 'password', 'linksys'],
            'cisco': ['cisco', 'admin', 'password'],
            'huawei': ['admin', 'huawei', 'password'],
            'zte': ['admin', 'zte', 'password'],
            'belkin': ['admin', 'password', 'belkin'],
            'motorola': ['motorola', 'password', 'admin']
        }
        
        for brand, pw_list in brand_defaults.items():
            passwords.update(pw_list)
            passwords.add(brand)
            
        # كلمات فارغة (بعض الأجهزة لا تطلب كلمة مرور)
        passwords.add('')
        
        return passwords
        
    def generate_mutations(self, base_words: List[str]) -> Set[str]:
        """توليد طفرات لكلمات أساسية"""
        
        mutations = set()
        
        for word in base_words:
            word_lower = word.lower()
            word_upper = word.upper()
            word_capital = word.capitalize()
            
            mutations.add(word_lower)
            mutations.add(word_upper)
            mutations.add(word_capital)
            
            # تبديل الحروف
            mutations.update(self._substitute_letters(word_lower))
            
            # إضافة أرقام
            for num in range(0, 100):
                mutations.add(f"{word_lower}{num}")
                mutations.add(f"{word_upper}{num}")
                
            # إضافة سنوات
            for year in range(1990, 2025):
                mutations.add(f"{word_lower}{year}")
                mutations.add(f"{word_capital}{year}")
                
            # إضافة رموز
            for char in self.special_chars:
                mutations.add(f"{word_lower}{char}")
                mutations.add(f"{char}{word_lower}")
                mutations.add(f"{word_lower}{char}{word_lower}")
                
            # تكرار
            mutations.add(f"{word_lower}{word_lower}")
            mutations.add(f"{word_lower}{word_upper}")
            
        return mutations
        
    def _substitute_letters(self, word: str) -> Set[str]:
        """تبديل الأحرف بأرقام ورموز مشابهة"""
        
        results = {word}
        
        for i, char in enumerate(word):
            if char in self.letter_substitutions:
                new_variants = set()
                for variant in results:
                    for sub in self.letter_substitutions[char]:
                        new_variant = variant[:i] + sub + variant[i+1:]
                        new_variants.add(new_variant)
                results.update(new_variants)
                
        return results
        
    def generate_hybrid_wordlist(
        self,
        ssid: str,
        brand: Optional[str] = None,
        include_defaults: bool = True,
        min_length: int = 6,
        max_length: int = 20
    ) -> Set[str]:
        """توليد قائمة كلمات هجينة شاملة"""
        
        all_passwords = set()
        
        # 1. من SSID
        ssid_passwords = self.generate_from_ssid(ssid, min_length, max_length)
        all_passwords.update(ssid_passwords)
        
        # 2. سياقية
        target_info = {'ssid': ssid, 'brand': brand or ''}
        contextual = self.generate_contextual_wordlist(target_info, min_length, max_length)
        all_passwords.update(contextual)
        
        # 3. افتراضية
        if include_defaults:
            defaults = self.generate_default_passwords()
            # تصفية الكلمات الافتراضية حسب الطول
            defaults_filtered = {p for p in defaults if min_length <= len(p) <= max_length}
            all_passwords.update(defaults_filtered)
            
        # 4. طفرات
        base_words = [ssid]
        if brand:
            base_words.append(brand)
        mutations = self.generate_mutations(base_words)
        mutations_filtered = {p for p in mutations if min_length <= len(p) <= max_length}
        all_passwords.update(mutations_filtered)
        
        return all_passwords
        
    def save_wordlist(
        self,
        passwords: Set[str],
        filename: str,
        sort_by: str = 'length',
        remove_empty: bool = True
    ) -> str:
        """حفظ قائمة الكلمات في ملف"""
        
        output_path = self.output_dir / filename
        
        # تحويل إلى قائمة
        password_list = list(passwords)
        
        # إزالة الفراغات إذا لزم الأمر
        if remove_empty:
            password_list = [p for p in password_list if p.strip()]
            
        # الترتيب
        if sort_by == 'length':
            password_list.sort(key=len)
        elif sort_by == 'alphabetical':
            password_list.sort()
        elif sort_by == 'complexity':
            # ترتيب حسب التعقيد (أطول وأكثر تنوعاً أولاً)
            password_list.sort(key=lambda x: (-len(x), sum(c.isdigit() for c in x), sum(not c.isalnum() for c in x)))
            
        # الحفظ
        with open(output_path, 'w', encoding='utf-8') as f:
            for password in password_list:
                f.write(f"{password}\n")
                
        print(f"{Colors.GREEN}✓ Wordlist saved: {output_path} ({len(password_list)} passwords){Colors.RESET}")
        
        return str(output_path)
        
    def estimate_crack_time(self, password_count: int, hash_type: str = 'WPA2') -> str:
        """تقدير وقت الكسر"""
        
        # معدلات تقريبية (hashes per second)
        rates = {
            'WPA2': 500,  # GPU متوسط
            'WPA3': 100,
            'MD5': 100000000,
            'SHA256': 50000000
        }
        
        rate = rates.get(hash_type, 500)
        seconds = password_count / rate
        
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            return f"{seconds/60:.1f} minutes"
        elif seconds < 86400:
            return f"{seconds/3600:.1f} hours"
        else:
            return f"{seconds/86400:.1f} days"


if __name__ == "__main__":
    # مثال على الاستخدام
    generator = SmartWordlistGenerator()
    
    print(f"{Colors.CYAN}=== WiFiNexus Guardian - Smart Wordlist Generator ==={Colors.RESET}\n")
    
    # توليد من SSID
    ssid = "HomeWiFi_5G"
    print(f"Generating passwords for SSID: {ssid}")
    
    passwords = generator.generate_hybrid_wordlist(
        ssid=ssid,
        brand="TP-Link",
        include_defaults=True,
        min_length=6,
        max_length=16
    )
    
    print(f"Generated {len(passwords)} potential passwords")
    
    # حفظ القائمة
    filename = f"wordlist_{ssid.replace(' ', '_').replace('/', '_')}.txt"
    output_path = generator.save_wordlist(passwords, filename, sort_by='length')
    
    # تقدير وقت الكسر
    crack_time = generator.estimate_crack_time(len(passwords), 'WPA2')
    print(f"Estimated crack time (GPU): {crack_time}")
    
    # عرض عينة
    print(f"\n{Colors.YELLOW}Sample passwords:{Colors.RESET}")
    sample = list(passwords)[:20]
    for pwd in sample:
        print(f"  - {pwd}")
