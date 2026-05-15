"""
WiGLE.net API Integration Module
=================================
تكامل مع قاعدة بيانات WiGLE العالمية للشبكات اللاسلكية
"""

import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class WiGLEIntegration:
    """
    فئة التكامل مع WiGLE.net API
    
    تسمح برفع نتائج المسح والبحث في قاعدة البيانات العالمية
    """
    
    BASE_URL = "https://api.wigle.net/api/v2"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        تهيئة الاتصال مع WiGLE API
        
        Args:
            api_token: رمز الوصول لـ WiGLE API (يمكن الحصول عليه من wigle.net/account)
        """
        self.api_token = api_token or os.getenv('WIGLE_API_TOKEN')
        self.session = requests.Session()
        
        if self.api_token:
            self.session.headers.update({
                'Authorization': f'Basic {self.api_token}',
                'Accept': 'application/json'
            })
        
        self.last_upload = None
        self.last_search = None
    
    def is_authenticated(self) -> bool:
        """التحقق من صحة المصادقة"""
        if not self.api_token:
            return False
        
        try:
            response = self.session.get(f"{self.BASE_URL}/network/authenticated")
            return response.status_code == 200
        except Exception:
            return False
    
    def search_network(self, ssid: str, latitude: float = None, 
                      longitude: float = None, 
                      results_limit: int = 100) -> Dict:
        """
        البحث عن شبكة في قاعدة بيانات WiGLE
        
        Args:
            ssid: اسم الشبكة للبحث
            latitude: خط العرض (اختياري)
            longitude: خط الطول (اختياري)
            results_limit: عدد النتائج الأقصى
            
        Returns:
            dict: نتائج البحث
        """
        params = {
            'ssid': ssid,
            'resultsPerPage': min(results_limit, 1000),
            'first': 0
        }
        
        if latitude and longitude:
            params['latrange1'] = latitude - 0.01
            params['latrange2'] = latitude + 0.01
            params['longrange1'] = longitude - 0.01
            params['longrange2'] = longitude + 0.01
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/network/search",
                params=params
            )
            response.raise_for_status()
            self.last_search = datetime.now()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}
    
    def upload_discovery(self, bssid: str, ssid: str, 
                        frequency: int, signal_strength: int,
                        latitude: float, longitude: float,
                        encryption: str = 'WPA2',
                        visible: bool = True) -> Dict:
        """
        رفع اكتشاف شبكة جديدة إلى WiGLE
        
        Args:
            bssid: عنوان MAC للنقطة
            ssid: اسم الشبكة
            frequency: التردد (MHz)
            signal_strength: قوة الإشارة (dBm)
            latitude: خط العرض
            longitude: خط الطول
            encryption: نوع التشفير
            visible: هل الشبكة ظاهرة
            
        Returns:
            dict: نتيجة الرفع
        """
        data = {
            'bssid': bssid,
            'ssid': ssid,
            'frequency': frequency,
            'signal': signal_strength,
            'latitude': latitude,
            'longitude': longitude,
            'encryption': encryption,
            'visible': str(visible).lower(),
            'foundtime': int(datetime.now().timestamp() * 1000)
        }
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/network/discovery",
                json=data
            )
            response.raise_for_status()
            self.last_upload = datetime.now()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}
    
    def batch_upload(self, discoveries: List[Dict]) -> Dict:
        """
        رفع متعدد للاكتشافات
        
        Args:
            discoveries: قائمة من الاكتشافات
            
        Returns:
            dict: نتيجة الرفع المتعدد
        """
        data = {'discoveries': discoveries}
        
        try:
            response = self.session.post(
                f"{self.BASE_URL}/file/upload",
                json=data
            )
            response.raise_for_status()
            self.last_upload = datetime.now()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e), 'success': False}
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات الحساب
        
        Returns:
            dict: إحصائيات المستخدم
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/stats/user")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': str(e)}
    
    def export_data(self, format_type: str = 'kml', 
                   start_date: str = None, 
                   end_date: str = None) -> Optional[bytes]:
        """
        تصدير البيانات بصيغة مختلفة
        
        Args:
            format_type: الصيغة (kml, csv, gpx)
            start_date: تاريخ البداية (YYYYMMDD)
            end_date: تاريخ النهاية (YYYYMMDD)
            
        Returns:
            bytes: البيانات المصدرة أو None
        """
        params = {'type': format_type}
        
        if start_date:
            params['start'] = start_date
        if end_date:
            params['end'] = end_date
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/file/export",
                params=params
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException:
            return None
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """التحقق من صحة الإحداثيات"""
        return (-90 <= latitude <= 90) and (-180 <= longitude <= 180)
    
    def format_bssid(self, bssid: str) -> str:
        """تنسيق عنوان BSSID بالصيغة الصحيحة"""
        bssid = bssid.replace(':', '').upper()
        if len(bssid) != 12:
            raise ValueError("BSSID must be 12 hexadecimal characters")
        return ':'.join(bssid[i:i+2] for i in range(0, 12, 2))


# دوال مساعدة للاستخدام السريع
def quick_search(ssid: str, api_token: str = None) -> Dict:
    """بحث سريع عن شبكة"""
    wigle = WiGLEIntegration(api_token)
    return wigle.search_network(ssid)


def quick_upload(bssid: str, ssid: str, lat: float, lon: float, 
                api_token: str = None) -> Dict:
    """رفع سريع لاكتشاف"""
    wigle = WiGLEIntegration(api_token)
    return wigle.upload_discovery(
        bssid=bssid,
        ssid=ssid,
        frequency=2437,
        signal_strength=-65,
        latitude=lat,
        longitude=lon
    )


if __name__ == '__main__':
    # مثال على الاستخدام
    print("WiFiNexus Guardian - WiGLE Integration")
    print("=" * 40)
    
    # التحقق من وجود متغير البيئة
    api_token = os.getenv('WIGLE_API_TOKEN')
    
    if api_token:
        wigle = WiGLEIntegration(api_token)
        
        if wigle.is_authenticated():
            print("✓ تم الاتصال بـ WiGLE بنجاح")
            
            # الحصول على الإحصائيات
            stats = wigle.get_stats()
            if 'success' in stats:
                print(f"الإحصائيات: {json.dumps(stats, indent=2)}")
        else:
            print("✗ فشل الاتصال بـ WiGLE")
    else:
        print("⚠ لم يتم العثور على WIGLE_API_TOKEN")
        print("احصل على رمزك من: https://wigle.net/account")
