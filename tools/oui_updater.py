"""
أداة تحديث قاعدة بيانات OUI تلقائياً
تقوم بتنزيل أحدث قائمة مصنعي الأجهزة من IEEE
"""
import os
import sys
import requests
import gzip
import shutil
from datetime import datetime
from typing import bool

class OUIUpdater:
    """محدث قاعدة بيانات OUI (Organizationally Unique Identifier)"""
    
    def __init__(self, data_dir: str = None):
        """
        تهيئة محدث OUI
        
        Args:
            data_dir: مجلد حفظ البيانات (افتراضي: data/)
        """
        if data_dir is None:
            data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data'
            )
        self.data_dir = data_dir
        self.oui_file = os.path.join(data_dir, 'oui.txt')
        self.manufacturer_db = {}
        
        # ضمان وجود مجلد البيانات
        os.makedirs(data_dir, exist_ok=True)
    
    def download_oui_database(self) -> bool:
        """
        تنزيل قاعدة بيانات OUI من IEEE
        
        Returns:
            bool: True إذا تم التنزيل بنجاح
        """
        ieee_url = "https://standards-oui.ieee.org/oui/oui.txt.gz"
        
        print(f"📥 جاري تنزيل قاعدة بيانات OUI من IEEE...")
        
        try:
            response = requests.get(ieee_url, timeout=30)
            response.raise_for_status()
            
            # حفظ الملف المضغوط مؤقتاً
            gz_path = self.oui_file + '.gz'
            with open(gz_path, 'wb') as f:
                f.write(response.content)
            
            # فك الضغط
            with gzip.open(gz_path, 'rb') as f_in:
                with open(self.oui_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # حذف الملف المضغوط
            os.remove(gz_path)
            
            print(f"✅ تم تنزيل قاعدة البيانات بنجاح")
            print(f"📁 الحفظ في: {self.oui_file}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ فشل التنزيل: {e}")
            return False
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")
            return False
    
    def parse_oui_file(self) -> dict:
        """
        تحليل ملف OUI واستخراج معلومات المصنعين
        
        Returns:
            dict: قاموس يربط MAC prefixes بأسماء المصنعين
        """
        if not os.path.exists(self.oui_file):
            print("⚠️ ملف OUI غير موجود، جاري التنزيل...")
            if not self.download_oui_database():
                return {}
        
        manufacturers = {}
        
        print("🔍 جاري تحليل ملف OUI...")
        
        try:
            with open(self.oui_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    # تنسيق IEEE: XX-XX-XX (base 16)  Manufacturer Name
                    if '(base 16)' in line:
                        parts = line.split('(base 16)')
                        if len(parts) >= 2:
                            mac_prefix = parts[0].strip().upper()
                            manufacturer = parts[1].strip()
                            
                            # تنظيف البادئة (إزالة الشرطات والنقط)
                            mac_clean = mac_prefix.replace('-', ':')
                            manufacturers[mac_clean] = manufacturer
            
            self.manufacturer_db = manufacturers
            print(f"✅ تم تحليل {len(manufacturers)} مدخلة مصنع")
            
            return manufacturers
            
        except Exception as e:
            print(f"❌ فشل التحليل: {e}")
            return {}
    
    def lookup_manufacturer(self, mac_address: str) -> str:
        """
        البحث عن مصنع جهاز بناءً على عنوان MAC
        
        Args:
            mac_address: عنوان MAC (XX:XX:XX:YY:YY:YY)
        
        Returns:
            str: اسم المصنع أو "Unknown"
        """
        if not self.manufacturer_db:
            self.parse_oui_file()
        
        # استخراج أول 3 بايتات (OUI)
        mac_clean = mac_address.upper().replace('-', ':')
        oui = ':'.join(mac_clean.split(':')[:3])
        
        return self.manufacturer_db.get(oui, "Unknown Manufacturer")
    
    def get_last_update_time(self) -> str:
        """
        الحصول على وقت آخر تحديث للملف
        
        Returns:
            str: تاريخ آخر تحديث
        """
        if not os.path.exists(self.oui_file):
            return "غير متوفر"
        
        mtime = os.path.getmtime(self.oui_file)
        return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    def is_update_needed(self, days: int = 30) -> bool:
        """
        التحقق مما إذا كان التحديث مطلوباً
        
        Args:
            days: عدد الأيام قبل اعتبار الملف قديماً
        
        Returns:
            bool: True إذا كان التحديث مطلوباً
        """
        if not os.path.exists(self.oui_file):
            return True
        
        mtime = os.path.getmtime(self.oui_file)
        age_days = (datetime.now().timestamp() - mtime) / (24 * 3600)
        
        return age_days > days
    
    def update_if_needed(self, auto: bool = False) -> bool:
        """
        التحديث التلقائي إذا لزم الأمر
        
        Args:
            auto: إذا True، يحدث فقط إذا كان الملف قديماً
        
        Returns:
            bool: True إذا تم التحديث
        """
        if auto and not self.is_update_needed():
            last_update = self.get_last_update_time()
            print(f"✅ قاعدة البيانات حديثة (آخر تحديث: {last_update})")
            return False
        
        success = self.download_oui_database()
        if success:
            self.parse_oui_file()
        
        return success


def main():
    """الوظيفة الرئيسية للأداة"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='أداة تحديث قاعدة بيانات OUI'
    )
    parser.add_argument(
        '--update', '-u',
        action='store_true',
        help='فرض التحديث حتى لو كان الملف حديثاً'
    )
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='التحديث التلقائي فقط إذا لزم الأمر'
    )
    parser.add_argument(
        '--lookup', '-l',
        type=str,
        help='البحث عن مصنع لعنوان MAC معين'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='عرض حالة قاعدة البيانات'
    )
    
    args = parser.parse_args()
    
    updater = OUIUpdater()
    
    if args.lookup:
        manufacturer = updater.lookup_manufacturer(args.lookup)
        print(f"MAC: {args.lookup}")
        print(f"المصنع: {manufacturer}")
        return
    
    if args.status:
        last_update = updater.get_last_update_time()
        needs_update = updater.is_update_needed()
        print(f"آخر تحديث: {last_update}")
        print(f"تحديث مطلوب: {'نعم' if needs_update else 'لا'}")
        if os.path.exists(updater.oui_file):
            size = os.path.getsize(updater.oui_file)
            print(f"حجم الملف: {size:,} بايت")
        return
    
    if args.update or args.auto:
        success = updater.update_if_needed(auto=not args.update)
        if success:
            print("\n✅ اكتمل التحديث بنجاح!")
        else:
            print("\n⚠️ لم يتم التحديث")
        return
    
    # السلوك الافتراضي: عرض المساعدة
    parser.print_help()


if __name__ == '__main__':
    main()
