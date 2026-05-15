"""
Profile Manager Module
======================
إدارة ملفات التعريف (Profiles) للتكوينات المسبقة
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path


class ProfileManager:
    """
    مدير ملفات التعريف
    
    يسمح بتحميل وحفظ وتطبيق ملفات التعريف المسبقة
    """
    
    DEFAULT_PROFILES_DIR = Path(__file__).parent.parent / 'profiles'
    
    def __init__(self, profiles_dir: Optional[str] = None):
        """
        تهيئة مدير الملفات
        
        Args:
            profiles_dir: مسار مجلد ملفات التعريف
        """
        self.profiles_dir = Path(profiles_dir) if profiles_dir else self.DEFAULT_PROFILES_DIR
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_profiles = {}
    
    def list_profiles(self) -> List[str]:
        """
        سرد جميع ملفات التعريف المتاحة
        
        Returns:
            list: أسماء ملفات التعريف
        """
        profiles = []
        for file in self.profiles_dir.glob('*.json'):
            profiles.append(file.stem)
        return profiles
    
    def load_profile(self, profile_name: str) -> Optional[Dict]:
        """
        تحميل ملف تعريف بالاسم
        
        Args:
            profile_name: اسم ملف التعريف
            
        Returns:
            dict: إعدادات ملف التعريف أو None
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        if not profile_path.exists():
            return None
        
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            self.loaded_profiles[profile_name] = profile_data
            return profile_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"خطأ في تحميل ملف التعريف: {e}")
            return None
    
    def save_profile(self, profile_name: str, profile_data: Dict) -> bool:
        """
        حفظ ملف تعريف جديد
        
        Args:
            profile_name: اسم ملف التعريف
            profile_data: بيانات ملف التعريف
            
        Returns:
            bool: نجاح الحفظ
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        try:
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            
            self.loaded_profiles[profile_name] = profile_data
            return True
        except IOError as e:
            print(f"خطأ في حفظ ملف التعريف: {e}")
            return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        حذف ملف تعريف
        
        Args:
            profile_name: اسم ملف التعريف
            
        Returns:
            bool: نجاح الحذف
        """
        profile_path = self.profiles_dir / f"{profile_name}.json"
        
        if not profile_path.exists():
            return False
        
        try:
            profile_path.unlink()
            if profile_name in self.loaded_profiles:
                del self.loaded_profiles[profile_name]
            return True
        except IOError as e:
            print(f"خطأ في حذف ملف التعريف: {e}")
            return False
    
    def get_profile_info(self, profile_name: str) -> Optional[Dict]:
        """
        الحصول على معلومات موجزة عن ملف التعريف
        
        Args:
            profile_name: اسم ملف التعريف
            
        Returns:
            dict: معلومات الملف
        """
        profile = self.load_profile(profile_name)
        if not profile:
            return None
        
        return {
            'name': profile.get('profile_name', profile_name),
            'description': profile.get('description', ''),
            'version': profile.get('version', '1.0.0'),
            'settings_count': len(profile.get('settings', {}))
        }
    
    def validate_profile(self, profile_data: Dict) -> tuple[bool, List[str]]:
        """
        التحقق من صحة ملف التعريف
        
        Args:
            profile_data: بيانات ملف التعريف
            
        Returns:
            tuple: (صحيح/خطأ, قائمة الأخطاء)
        """
        errors = []
        
        # التحقق من الحقول المطلوبة
        required_fields = ['profile_name', 'description']
        for field in required_fields:
            if field not in profile_data:
                errors.append(f"حقل مطلوب مفقود: {field}")
        
        # التحقق من قسم الإعدادات
        if 'settings' not in profile_data:
            errors.append("قسم الإعدادات مفقود")
        else:
            settings = profile_data['settings']
            
            # التحقق من الأقسام الفرعية
            expected_sections = ['scan', 'attack', 'security']
            for section in expected_sections:
                if section not in settings:
                    errors.append(f"قسم الإعدادات '{section}' مفقود")
        
        # التحقق من الحدود
        if 'limits' in profile_data:
            limits = profile_data['limits']
            if 'max_targets' in limits and limits['max_targets'] < 1:
                errors.append("الحد الأقصى للأهداف يجب أن يكون >= 1")
        
        return len(errors) == 0, errors
    
    def create_custom_profile(self, name: str, base_profile: Optional[str] = None,
                             custom_settings: Optional[Dict] = None) -> bool:
        """
        إنشاء ملف تعريف مخصص
        
        Args:
            name: اسم الملف الجديد
            base_profile: ملف أساس للاقتباس منه (اختياري)
            custom_settings: إعدادات مخصصة (اختياري)
            
        Returns:
            bool: نجاح الإنشاء
        """
        # البدء بملف أساسي أو فارغ
        if base_profile:
            profile_data = self.load_profile(base_profile)
            if not profile_data:
                print(f"ملف الأساس '{base_profile}' غير موجود")
                return False
        else:
            profile_data = {
                'profile_name': name,
                'description': 'ملف تعريف مخصص',
                'version': '2.0.0',
                'settings': {},
                'limits': {},
                'exclusions': {}
            }
        
        # تطبيق الإعدادات المخصصة
        if custom_settings:
            for key, value in custom_settings.items():
                profile_data[key] = value
        
        # التحقق من الصحة
        is_valid, errors = self.validate_profile(profile_data)
        if not is_valid:
            print(f"ملف التعريف غير صالح: {errors}")
            return False
        
        # الحفظ
        return self.save_profile(name, profile_data)
    
    def export_profile(self, profile_name: str, output_path: str) -> bool:
        """
        تصدير ملف تعريف إلى مسار خارجي
        
        Args:
            profile_name: اسم الملف
            output_path: المسار الخارجي
            
        Returns:
            bool: نجاح التصدير
        """
        profile_data = self.load_profile(profile_name)
        if not profile_data:
            return False
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def import_profile(self, input_path: str, new_name: Optional[str] = None) -> bool:
        """
        استيراد ملف تعريف من مسار خارجي
        
        Args:
            input_path: مسار الملف
            new_name: اسم جديد للملف (اختياري)
            
        Returns:
            bool: نجاح الاستيراد
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            # استخدام الاسم الجديد أو الاسم من الملف
            profile_name = new_name or profile_data.get('profile_name')
            if not profile_name:
                print("لم يتم العثور على اسم لملف التعريف")
                return False
            
            return self.save_profile(profile_name, profile_data)
        except (IOError, json.JSONDecodeError) as e:
            print(f"خطأ في استيراد ملف التعريف: {e}")
            return False
    
    def apply_profile(self, profile_name: str, target_object) -> bool:
        """
        تطبيق ملف تعريف على كائن
        
        Args:
            profile_name: اسم الملف
            target_object: الكائن المستهدف
            
        Returns:
            bool: نجاح التطبيق
        """
        profile_data = self.load_profile(profile_name)
        if not profile_data:
            return False
        
        # تطبيق الإعدادات
        settings = profile_data.get('settings', {})
        
        for category, values in settings.items():
            if hasattr(target_object, f'set_{category}'):
                getattr(target_object, f'set_{category}')(values)
        
        return True


# دوال مساعدة
def get_default_profiles() -> List[str]:
    """الحصول على قائمة ملفات التعريف الافتراضية"""
    manager = ProfileManager()
    return manager.list_profiles()


def load_quick_profile(name: str) -> Optional[Dict]:
    """تحميل سريع لملف تعريف"""
    manager = ProfileManager()
    return manager.load_profile(name)


if __name__ == '__main__':
    # مثال على الاستخدام
    print("WiFiNexus Guardian - Profile Manager")
    print("=" * 40)
    
    manager = ProfileManager()
    
    # سرد الملفات المتاحة
    profiles = manager.list_profiles()
    print(f"\nملفات التعريف المتاحة ({len(profiles)}):")
    for profile in profiles:
        info = manager.get_profile_info(profile)
        if info:
            print(f"  - {info['name']}: {info['description']}")
    
    # تحميل ملف تعريف
    print("\n--- تحميل ملف Stealth Mode ---")
    stealth = manager.load_profile('stealth_mode')
    if stealth:
        print(f"✓ تم التحميل: {stealth['profile_name']}")
        print(f"  الإصدار: {stealth['version']}")
