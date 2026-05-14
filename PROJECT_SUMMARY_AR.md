# WiFiNexus Guardian - مشروع متكامل لتحليل الشبكات اللاسلكية

## نظرة عامة

WiFiNexus Guardian هو منصة احترافية متكاملة لتحليل الشبكات اللاسلكية والأمن السيبراني، تم تطويرها بواسطة Ahmed Mostafa Ibrahim (Finovate – AHMED EG).

## المميزات الرئيسية المكتملة

### 1. 📡 Advanced Network Scanner Pro (`network/advanced_scanner.py`)
- مسح متعدد النطاقات (2.4GHz, 5GHz, 6GHz)
- كشف الشبكات المخفية
- تحليل تداخل القنوات
- تحديد البائعين من خلال MAC Address
- تصدير النتائج (JSON/CSV)
- توصيات بأفضل قناة

### 2. 🔌 Network Interface Manager Pro (`network/interface_manager.py`)
- كشف جميع محولات الشبكة (داخلية/خارجية)
- التمييز بين محولات USB و PCIe
- التحقق من دعم وضع المراقبة (Monitor Mode)
- اختيار المحول المفضل للعمليات
- دعم كامل لـ Windows, Linux, macOS
- معلومات تفصيلية عن السائقين والإصدارات

### 3. 📡 Handshake Capturer (`network/handshake_capturer.py`)
- دعم 3 أوضاع: Monitor, Hybrid, Normal
- التقاط Handshake للشبكات WPA/WPA2/WPA3
- كشف حزم EAPOL المتقدم
- تحويل تلقائي لصيغة HCCAPX
- استهداف شبكات محددة
- إرسال Deauthentication packets (Linux فقط)
- كشف العملاء المتصلين

### 4. 🔑 Handshake Cracker (`network/handshake_cracker.py`)
- كسر باستخدام Wordlist (aircrack-ng + hashcat)
- كسر بالذكاء الاصطناعي مع توليد كلمات مرور ذكية
- أنماط متقدمة: substitutions, router defaults, keyboard walks
- دعم كلمات مرور افتراضية للراوترات
- تسجيل النتائج الناجحة

### 5. 🔒 Security & Safety Module (`core/security_manager.py`)
- **Safety Mode**: يمنع العمليات الخطرة افتراضياً
- **Legal Warning**: تحذير قانوني إلزامي
- **Stealth Mode**: يقلل من بصمة الكشف
- **Audit Logging**: تسجيل جميع الأحداث الأمنية
- **Windows Defender Exclusion**: إضافة استثناءات
- **Security Reports**: تقارير أمنية شاملة
- **Environment Validation**: التحقق من بيئة التشغيل

### 6. 💻 Command Line Interface (`cli.py`)
واجهة سطر أوامر كاملة مع الأوامر التالية:
```bash
# مسح الشبكات
python cli.py scan --band all --duration 15 --verbose

# إدارة المحولات
python cli.py interfaces --display --preferred

# التقاط Handshake
python cli.py capture --target AA:BB:CC:DD:EE:FF --channel 6

# كسر Handshake
python cli.py crack --capture handshake.pcap --ai

# الأمان
python cli.py security --status --report --validate

# مراقبة الأجهزة
python cli.py monitor --duration 30
```

### 7. 🖥️ GUI Interface (`gui/main_window.py`)
- واجهة رسومية حديثة بستايل Cyber Neon
- لوحة تحكم رئيسية (Dashboard)
- ماسح شبكات WiFi
- مراقب الأجهزة
- محلل الحزم
- اختبار السرعة
- مركز الذكاء الاصطناعي
- نظام السجلات

## الهيكل العام للمشروع

```
/workspace/
├── main.py                 # نقطة الدخول الرئيسية للتطبيق
├── cli.py                  # واجهة سطر الأوامر
├── requirements.txt        # المكتبات المطلوبة
├── README.md              # التوثيق
├── README_AR.md           # التوثيق بالعربية
│
├── core/
│   ├── initializer.py      # تهيئة المكونات الأساسية
│   ├── hardware_layer.py   # طبقة العتاد
│   └── security_manager.py # مدير الأمان والحماية ⭐
│
├── network/
│   ├── advanced_scanner.py    # الماسح المتقدم ⭐
│   ├── interface_manager.py   # مدير المحولات ⭐
│   ├── handshake_capturer.py  # ملتقط Handshake
│   ├── handshake_cracker.py   # كاسر Handshake
│   ├── wifi_scanner.py        # ماسح WiFi أساسي
│   ├── device_monitor.py      # مراقب الأجهزة
│   └── speed_test.py          # اختبار السرعة
│
├── gui/
│   └── main_window.py      # الواجهة الرسومية
│
├── drivers/
│   ├── driver_manager.py   # مدير التعريفات
│   └── npcap_checker.py    # فحص Npcap
│
├── ai/
│   └── ai_engine.py        # محرك الذكاء الاصطناعي
│
├── packet_analyzer/
│   └── packet_analyzer.py  # محلل الحزم
│
├── database/
│   └── db_manager.py       # إدارة قاعدة البيانات
│
├── adapters/
│   └── adapter_manager.py  # إدارة المحولات
│
├── plugins/
│   └── plugin_manager.py   # نظام الإضافات
│
├── reports/                # التقارير
├── logs/                   # السجلات
├── captures/               # ملفات الالتقاط
├── wordlists/              # قوائم الكلمات
└── themes/                 # السمات
```

## التحسينات الأمنية المطبقة

### لمنع الكشف كبرنامج ضار:

1. **Safety Mode افتراضي**: يمنع الهجمات النشطة
2. **تحذيرات قانونية واضحة**: في كل عملية
3. **وضع Passive Capture**: التقاط سلبي بدون إرسال
4. **Audit Logging**: تسجيل جميع العمليات
5. **Windows Defender Integration**: إضافة استثناءات رسمية
6. **Stealth Mode**: تقليل البصمة الرقمية
7. **Authorization Checks**: التحقق من الصلاحيات

### أفضل الممارسات:

```python
# مثال على استخدام Safety Mode
from core.security_manager import get_security_manager

sec_mgr = get_security_manager()
sec_mgr.show_legal_warning()  # عرض التحذير القانوني
sec_mgr.enable_safety_mode()  # تفعيل وضع الأمان

# التحقق من العملية المسموحة
if sec_mgr.check_operation_allowed('deauth_attack'):
    # العملية محظورة في Safety Mode
    pass
```

## متطلبات التشغيل

### Linux (Kali/Parrot recommended):
```bash
sudo apt install aircrack-ng wireshark tshark tcpdump net-tools
pip install -r requirements.txt
```

### Windows:
```bash
# تثبيت Npcap أولاً من https://npcap.com
pip install -r requirements.txt
```

### macOS:
```bash
brew install aircrack-ng wireshark
pip install -r requirements.txt
```

## المكتبات المطلوبة (requirements.txt)

```
PySide6>=6.5.0
scapy>=2.5.0
requests>=2.31.0
numpy>=1.24.0
pandas>=2.0.0
psutil>=5.9.0
pycryptodome>=3.18.0
```

## أمثلة على الاستخدام

### 1. مسح شامل للشبكات:
```bash
python cli.py scan --band all --duration 15 --export json -o networks.json
```

### 2. اختيار أفضل محول:
```bash
python cli.py interfaces --display --preferred --export json
```

### 3. التقاط Handshake مستهدف:
```bash
python cli.py capture -t AA:BB:CC:DD:EE:FF -c 6 --timeout 120
```

### 4. كسر بالذكاء الاصطناعي:
```bash
python cli.py crack -i capture.pcap --ai
```

### 5. تقرير أمني كامل:
```bash
python cli.py security --status --report --validate --recommendations
```

## التطوير المستقبلي

### مخطط له:
- [ ] دعم WPA3 SAE
- [ ] تحليل طيفي متقدم
- [ ] كشف أنظمة WIDS/WIPS
- [ ] هجمات PMKID
- [ ] دعم Bluetooth Low Energy
- [ ] تكامل مع Cloud APIs
- [ ] نظام إضافات قابل للتوسع
- [ ] واجهة ويب Remote

## الترخيص والتحذيرات

⚠️ **تحذير قانوني مهم**:
هذا البرنامج مخصص للاستخدام المصرح به فقط في:
- اختبار الاختراق المصرح به
- تدقيق الأمان الشبكي
- الأغراض التعليمية
- البحث الأمني

استخدامه للوصول غير المصرح به للشبكات غير قانوني وقد يعرضك للمساءلة القانونية.

## المطور

**Ahmed Mostafa Ibrahim**  
Finovate – AHMED EG  
© 2025 جميع الحقوق محفوظة

## الإصدار

الإصدار الحالي: **1.0.0**  
تاريخ التحديث: **2025**

---

## ملخص التحسينات المكتملة

✅ Advanced Network Scanner Pro - مسح متقدم متعدد النطاقات  
✅ Network Interface Manager Pro - إدارة محولات احترافية  
✅ Security & Safety Module - نظام أمان وحماية متكامل  
✅ Command Line Interface - واجهة سطر أوامر شاملة  
✅ Handshake Capturer Enhanced - التقاط محسن مع 3 أوضاع  
✅ Handshake Cracker with AI - كسر بالذكاء الاصطناعي  
✅ Legal Compliance System - نظام الامتثال القانوني  
✅ Anti-Detection Measures - إجراءات مضادة للكشف  
✅ Windows Defender Integration - تكامل مع دفاعات ويندوز  
✅ Audit Logging System - نظام تسجيل تدقيق  

**عدد الملفات Python**: 35+ ملف  
**إجمالي الأسطر**: 8000+ سطر برمجي  
**اللغات المدعومة**: الإنجليزية والعربية  
**المنصات**: Windows, Linux, macOS
