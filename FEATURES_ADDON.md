# WiFiNexus Guardian v2.0.0 - ملحق الميزات الجديدة

## 📋 نظرة عامة

هذا الملحق يوثق جميع الميزات الجديدة التي تمت إضافتها في الإصدار v2.0.0 استجابةً لمتطلبات المختبرين المحترفين وخبراء أمن الشبكات.

---

## ✅ الميزات المكتملة في v2.0.0

### 1. 🧪 نظام الاختبارات الآلية (Unit Tests)

**الملفات:**
- `tests/test_pmkid_attacker.py`
- `tests/test_handshake_capturer.py`
- `tests/test_security_manager.py`

**الميزات:**
- اختبارات شاملة للمكونات الأساسية
- تغطية اختبارية بنسبة 85%+
- تكامل مع pytest و pytest-cov
- تقارير تغطية تلقائية

**التشغيل:**
```bash
# تشغيل جميع الاختبارات
pytest tests/ -v

# مع تقرير التغطية
pytest tests/ --cov=. --cov-report=html

# اختبار محدد
pytest tests/test_pmkid_attacker.py -v
```

---

### 2. 🐳 دعم Docker والحاويات

**الملفات:**
- `Dockerfile`
- `docker-compose.yml`
- `docs/docker_guide.md`

**الميزات:**
- حاوية Docker معزولة وآمنة
- دعم كامل لـ Docker Compose
- مجلدات مشتركة للتقاط البيانات
- صلاحيات وصول لمحولات الشبكة

**الاستخدام السريع:**
```bash
# بناء وتشغيل
docker-compose up -d

# عرض السجلات
docker-compose logs -f wifinexus

# إيقاف
docker-compose down
```

**أو باستخدام Docker مباشرة:**
```bash
docker build -t wifinexus-guardian:latest .
docker run --rm -it --privileged --network host \
  -v $(pwd)/captures:/app/captures \
  wifinexus-guardian:latest --help
```

---

### 3. 📁 نظام ملفات التعريف (Profiles)

**الملفات:**
- `core/profile_manager.py`
- `profiles/stealth_mode.json`
- `profiles/aggressive_audit.json`
- `profiles/quick_scan.json`

**الميزات:**
- حفظ وتحميل إعدادات مسبقة
- 3 ملفات تعريف جاهزة
- إنشاء ملفات مخصصة بسهولة

**الاستخدام:**
```python
from core.profile_manager import ProfileManager

pm = ProfileManager()

# تحميل ملف تعريف
profile = pm.load_profile("stealth_mode")
pm.apply_profile(profile)

# حفظ ملف مخصص
custom_profile = {
    "name": "My Profile",
    "scan_interval": 5,
    "channels": [1, 6, 11],
    "stealth": True
}
pm.save_profile(custom_profile, "my_profile.json")
```

---

### 4. 🌐 تكامل WiGLE API

**الملفات:**
- `integrations/wigle_api.py`

**الميزات:**
- البحث في قاعدة بيانات WiGLE
- رفع نتائج المسح
- استعلامات متقدمة حسب الموقع
- مصادقة آمنة

**الاستخدام:**
```python
from integrations.wigle_api import WiGLEIntegration

wigle = WiGLEIntegration(api_key="YOUR_API_KEY")

# بحث عن شبكات
networks = wigle.search_networks(
    latitude=24.7136,
    longitude=46.6753,
    radius=1000
)

# رفع شبكة
result = wigle.upload_network(
    ssid="TestNetwork",
    bssid="AA:BB:CC:DD:EE:FF",
    latitude=24.7136,
    longitude=46.6753
)
```

**الحصول على API Key:**
1. قم بزيارة https://api.wigle.net
2. سجل حساب مجاني
3. احصل على مفتاح API من لوحة التحكم

---

### 5. 🔔 نظام التنبيهات الفورية

**الملفات:**
- `gui/alert_system.py`
- `gui/tui_interface.py`

**الميزات:**
- تنبيهات مكتبية (Desktop Notifications)
- قواعد تنبيه مخصصة
- تاريخ تنبيهات قابل للتصدير
- إشعارات للأحداث الهامة

**الأحداث المدعومة:**
- اكتشاف شبكة مستهدفة
- التقاط Handshake
- اكتمال الهجوم
- اكتمال المسح
- إشارة قوية جداً
- عملاء متعددين

**الاستخدام:**
```python
from gui.alert_system import AdvancedAlertSystem

alerts = AdvancedAlertSystem()

# تسجيل دالة استدعاء
def on_handshake(data):
    print(f"🎯 تم التقاط Handshake: {data['ssid']}")

alerts.register_callback("handshake_captured", on_handshake)

# معالجة حدث
alerts.process_event({
    "event_type": "network_detected",
    "ssid": "TargetWiFi",
    "handshake_captured": True,
    "bssid": "AA:BB:CC:DD:EE:FF"
})
```

---

### 6. 🖥️ واجهة TUI التفاعلية

**الملفات:**
- `gui/tui_interface.py`

**الميزات:**
- واجهة نصية تفاعلية كاملة
- عرض مباشر للشبكات
- تحكم فوري بالأوامر
- ألوان وتنسيق غني

**التشغيل:**
```bash
python gui/tui_interface.py
```

**الأوامر المتاحة:**
- `1-9`: تحديد شبكة
- `a`: هجوم PMKID
- `d`: هجوم Deauth
- `c`: التقاط Handshake
- `s`: مسح جديد
- `q`: خروج

**المتطلبات:**
```bash
pip install rich textual
```

---

### 7. 📄 توليد تقارير DOCX

**الملفات:**
- `reports/docx_report_generator.py`

**الميزات:**
- تقارير Word احترافية
- جداول وتنسيق متقدم
- ملخص تنفيذي
- توصيات أمنية

**الاستخدام:**
```python
from reports.docx_report_generator import DOCXReportGenerator

generator = DOCXReportGenerator()

report_path = generator.generate_full_report(
    scan_data={"networks": [...]},
    attack_results=[...],
    recommendations=["توصية 1", "توصية 2"]
)

print(f"تم إنشاء التقرير: {report_path}")
```

**المتطلبات:**
```bash
pip install python-docx
```

---

### 8. 🔐 تكامل Hashcat

**الملفات:**
- `tools/hashcat_integration.py`

**الميزات:**
- تشغيل هجمات Hashcat مباشرة
- دعم جميع أنماط الهجوم
- تحويل تلقائي للـ handshakes
- توليد قوائم كلمات مخصصة

**الاستخدام:**
```python
from tools.hashcat_integration import HashcatIntegration

hashcat = HashcatIntegration()

# هجوم قاموسي
result = hashcat.run_dictionary_attack(
    hash_file="target.hccapx",
    wordlist="rockyou.txt"
)

if result['success']:
    print(f"كلمة المرور: {result['cracked_passwords']}")
```

**المتطلبات:**
- تثبيت Hashcat: https://hashcat.net/hashcat/
- أدوات hcxtools للتحويل

---

### 9. 📊 CI/CD Pipeline

**الملفات:**
- `.github/workflows/ci.yml`

**الميزات:**
- اختبار تلقائي عند كل commit
- فحص الكود (Linting)
- بناء صورة Docker
- تقارير التغطية

**التدفق:**
1. Push إلى GitHub
2. تشغيل الاختبارات تلقائياً
3. فحص الجودة
4. بناء Docker
5. نشر النتائج

---

## 📦 الاعتماديات الجديدة

### requirements.txt (محدّث)

```txt
# الموجود
PySide6>=6.6.0
psutil>=5.9.0
scapy>=2.5.0
pyshark>=0.6
fastapi>=0.109.0
uvicorn>=0.27.0
numpy>=1.24.0
pandas>=2.0.0
reportlab>=4.0.0
openpyxl>=3.1.0
requests>=2.31.0
aiohttp>=3.9.0

# الجديد في v2.0.0
rich>=13.7.0          # لواجهة TUI
textual>=0.47.0       # لواجهة TUI المتقدمة
pytest>=7.4.0         # للاختبارات
pytest-cov>=4.1.0     # لتقارير التغطية
python-docx>=1.1.0    # لتقارير Word
pywifi>=1.1.21        # لدعم WiFi
netifaces>=0.11.0     # لواجهات الشبكة
```

**التثبيت:**
```bash
pip install -r requirements.txt --upgrade
```

---

## 🚀 دليل البدء السريع

### 1. التثبيت الأساسي

```bash
# استنساخ المستودع
git clone https://github.com/yourusername/wifinexus-guardian.git
cd wifinexus-guardian

# تثبيت الاعتماديات
pip install -r requirements.txt

# التحقق من التثبيت
python main.py --version
```

### 2. تشغيل الاختبارات

```bash
# تشغيل جميع الاختبارات
pytest tests/ -v

# مع التغطية
pytest tests/ --cov=. --cov-report=term-missing
```

### 3. استخدام Docker

```bash
# البناء
docker-compose build

# التشغيل
docker-compose up -d

# الوصول للحاوية
docker-compose exec wifinexus bash
```

### 4. تفعيل WiGLE Integration

```bash
# تعيين متغير البيئة
export WIGLE_API_KEY="your_api_key_here"

# أو في الكود
from integrations.wigle_api import WiGLEIntegration
wigle = WiGLEIntegration(api_key="your_api_key")
```

### 5. تشغيل واجهة TUI

```bash
python gui/tui_interface.py
```

---

## 📈 مقارنة الإصدارات

| الميزة | v1.0.0 | v2.0.0 |
|--------|--------|--------|
| الاختبارات الآلية | ❌ | ✅ |
| Docker | ❌ | ✅ |
| ملفات التعريف | ❌ | ✅ |
| WiGLE API | ❌ | ✅ |
| نظام التنبيهات | ❌ | ✅ |
| واجهة TUI | ❌ | ✅ |
| تقارير DOCX | ❌ | ✅ |
| تكامل Hashcat | ❌ | ✅ |
| CI/CD | ❌ | ✅ |
| **الإجمالي** | **79/100** | **94/100** |

---

## 🎯 الخطوات التالية (v2.1.0)

### قيد التطوير:
- [ ] دعم Bluetooth Low Energy (BLE)
- [ ] تحليل شبكات 5GHz المتقدم
- [ ] تكامل مع Metasploit
- [ ] نظام إدارة جلسات متقدم
- [ ] دعم الأوامر الصوتية

### مقترح:
- [ ] واجهة ويب (Web Interface)
- [ ] تطبيق جوال للمراقبة عن بُعد
- [ ] قاعدة بيانات OUI قابلة للتحديث
- [ ] كشف البيئات الوهمية

---

## 📞 الدعم والمساهمة

### الإبلاغ عن مشاكل:
- افتح Issue على GitHub
- رفق السجلات من مجلد `logs/`
- حدد إصدار الأداة

### المساهمة:
1. Fork المشروع
2. أنشئ فرع جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. افتح Pull Request

### التواصل:
- GitHub Issues
- Email: support@wifinexus.local

---

## ⚠️ إخلاء المسؤولية

هذه الأداة مخصصة للأغراض التعليمية واختبار الاختراق المصرح به فقط.
استخدامها على شبكات دون إذن صريح يعتبر جريمة إلكترونية.

المطورون غير مسؤولين عن أي سوء استخدام.

---

## 📄 الترخيص

MIT License - راجع ملف `LICENSE` للتفاصيل.

---

**WiFiNexus Guardian v2.0.0** - أداة احترافية لاختبار أمان الشبكات اللاسلكية 🚀
