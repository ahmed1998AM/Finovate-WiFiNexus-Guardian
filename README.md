# 📡 Finovate WiFiNexus Guardian - دليل الاستخدام بالعربية

## نظرة عامة
**WiFiNexus Guardian** هو منصة احترافية لتحليل ومراقبة وتشخيص شبكات WiFi مع دعم متقدم لنظام Windows، وذكاء اصطناعي مدمج، وتحليلات لاسلكية في الوقت الفعلي.

**الإصدار الحالي**: 1.5.0 (Professional Security Edition)  
**تاريخ التحديث**: 2025-05-15

---

## ⚠️ تحذير قانوني هام

> **هذا البرنامج مخصص للاستخدام القانوني والأمني المصرح به فقط!**

### الاستخدامات المسموحة:
- ✅ اختبار الأمان للشبكات التي تمتلكها
- ✅ مراجعة الشبكات بإذن صريح من المالك
- ✅ الأغراض التعليمية والبحثية
- ✅ مراقبة شبكتك الشخصية

### الاستخدامات المحظورة:
- ❌ الوصول غير المصرح به للشبكات
- ❌ سرقة بيانات الاعتماد
- ❌ الاعتراض غير القانوني للحزم
- ❌ هجمات الشبكات
- ❌ أي نشاط ضار أو غير قانوني

**المسؤولية القانونية تقع على عاتق المستخدم النهائي.**

---

## 🚀 التثبيت السريع

### المتطلبات الأساسية

#### لنظام Linux:
```bash
sudo apt update
sudo apt install -y python3 python3-pip git
sudo apt install -y aircrack-ng tshark tcpdump wireshark
sudo apt install -y net-tools wireless-tools
```

#### لنظام Windows:
1. تثبيت Python 3.12+ من [python.org](https://www.python.org)
2. تثبيت Npcap من [npcap.com](https://nmap.org/npcap/)
3. تثبيت Tshark من [wireshark.org](https://www.wireshark.org)

### تثبيت المشروع

```bash
cd /workspace
pip install -r requirements.txt
```

### ملف المتطلبات (requirements.txt):
```
PySide6>=6.6.0
fastapi>=0.109.0
uvicorn>=0.27.0
scapy>=2.5.0
psutil>=5.9.0
netifaces>=0.11.0
pywifi>=1.1.2
sqlite3
requests>=2.31.0
pandas>=2.1.0
matplotlib>=3.8.0
```

---

## 📁 هيكل المشروع

```
/workspace/
├── main.py                 # نقطة الدخول الرئيسية
├── core/                   # النواة الأساسية
│   ├── initializer.py      # تهيئة النظام
│   └── hardware_layer.py   # طبقة الأجهزة
├── gui/                    # واجهة المستخدم
│   └── main_window.py      # النافذة الرئيسية
├── network/                # وحدات الشبكة
│   ├── wifi_scanner.py     # ماسح WiFi
│   ├── device_monitor.py   # مراقب الأجهزة
│   ├── speed_test.py       # اختبار السرعة
│   └── handshake_capturer.py  # ملتقط المصافحة ⭐
├── packet_analyzer/        # محلل الحزم
│   └── packet_analyzer.py  # التحليل العميق ⭐
├── ai/                     # الذكاء الاصطناعي
│   └── ai_engine.py        # محرك AI
├── database/               # قاعدة البيانات
│   └── db_manager.py       # مدير SQLite
├── captures/               # ملفات الالتقاط
└── logs/                   # السجلات
```

---

## 🔧 الوحدات الرئيسية

### 1️⃣ ماسح WiFi (WiFi Scanner)
مسح الشبكات اللاسلكية القريبة وتحليلها.

```python
from network.wifi_scanner import WiFiScanner

scanner = WiFiScanner()
networks = scanner.scan_networks()

for net in networks:
    print(f"SSID: {net['ssid']}")
    print(f"Signal: {net['signal_dbm']} dBm")
    print(f"Channel: {net['channel']}")
    print(f"Encryption: {net['encryption']}")
```

### 2️⃣ مراقب الأجهزة (Device Monitor)
اكتشاف الأجهزة المتصلة بالشبكة.

```python
from network.device_monitor import DeviceMonitor

monitor = DeviceMonitor()
devices = monitor.discover_devices()

for device in devices:
    print(f"IP: {device['ip']}")
    print(f"MAC: {device['mac']}")
    print(f"Vendor: {device['vendor']}")
```

### 3️⃣ اختبار السرعة (Speed Test)
قياس سرعة التنزيل والرفع وزمن الاستجابة.

```python
from network.speed_test import SpeedTest

test = SpeedTest()
result = test.run_speed_test()

print(f"Download: {result['download_mbps']} Mbps")
print(f"Upload: {result['upload_mbps']} Mbps")
print(f"Ping: {result['ping_ms']} ms")
```

### 4️⃣ ملتقط المصافحة (Handshake Capturer) ⭐
التقاط مصافحة WPA/WPA2 من الشبكات المستهدفة.

```python
from network.handshake_capturer import HandshakeCapturer

capturer = HandshakeCapturer()

# التحقق من المتطلبات
reqs = capturer.check_requirements()
for tool, installed in reqs.items():
    status = "✓" if installed else "✗"
    print(f"{status} {tool}")

# التقاط مصافحة مستهدفة
target_bssid = "AA:BB:CC:DD:EE:FF"  # MAC الشبكة
channel = 6  # قناة الشبكة

handshake_file = capturer.capture_handshake_targeted(
    target_bssid=target_bssid,
    channel=channel,
    timeout=120  # ثانية
)

if handshake_file:
    print(f"✓ تم التقاط المصافحة: {handshake_file}")
else:
    print("لم يتم التقاط المصافحة")
```

#### خطوات الالتقاط:
1. **تفعيل وضع المراقبة** (Monitor Mode)
2. **بدء الالتقاط** على القناة المستهدفة
3. **اكتشاف العملاء** المتصلين
4. **إرسال Deauth** لإجبار إعادة الاتصال (اختياري)
5. **انتظار المصافحة** (4-way handshake)
6. **حفظ الملف** بصيغة PCAP و HCCAPX

#### الملفات المحفوظة:
- `captures/capture_YYYYMMDD_HHMMSS.pcap` - ملف الالتقاط الخام
- `captures/capture_YYYYMMDD_HHMMSS.hccapx` - صيغة Hashcat
- `captures/handshake_log.txt` - سجل الالتقاطات

### 5️⃣ محلل الحزم (Packet Analyzer) ⭐
تحليل عميق للحزم captured في ملفات PCAP.

```python
from packet_analyzer.packet_analyzer import PacketAnalyzer

analyzer = PacketAnalyzer()

# تحليل ملف PCAP
results = analyzer.analyze_pcap("captures/capture_20250101_120000.pcap")

# استخراج معلومات المصافحة
hs_info = analyzer.extract_handshake_info("captures/capture_20250101_120000.pcap")
print(f"Has Handshake: {hs_info['has_handshake']}")
print(f"BSSID: {hs_info['bssid']}")
print(f"ESSID: {hs_info['essid']}")
print(f"EAPOL Count: {hs_info['eapol_count']}")

# الحصول على أكثر الأجهزة تحدثاً
talkers = analyzer.get_top_talkers("captures/capture_20250101_120000.pcap", limit=10)
for t in talkers:
    print(f"{t['ip']}: {t['total']} packets")

# تصدير التحليل
analyzer.export_analysis("analysis_report.json", output_format="json")
```

#### ميزات المحلل:
- ✅ إحصائيات الحزم (TCP, UDP, ICMP)
- ✅ توزيع البروتوكولات
- ✅ اتصالات TCP/UDP
- ✅ استعلامات DNS
- ✅ طلبات HTTP
- ✅ اكتشاف EAPOL (المصافحة)
- ✅ تصدير JSON/CSV/TXT

---

## 🎯 سيناريوهات الاستخدام

### السيناريو 1: مسح شامل للشبكة
```python
from network.wifi_scanner import WiFiScanner
from network.device_monitor import DeviceMonitor

# مسح الشبكات
scanner = WiFiScanner()
networks = scanner.scan_networks()
print(f"الشبكات المكتشفة: {len(networks)}")

# تحليل ازدحام القنوات
congestion = scanner.analyze_channel_congestion()
print(f"أفضل قناة: {congestion['least_congested']}")

# مراقبة الأجهزة
monitor = DeviceMonitor()
devices = monitor.discover_devices()
print(f"الأجهزة المتصلة: {len(devices)}")
```

### السيناريو 2: اختبار أمان الشبكة
```python
from network.handshake_capturer import HandshakeCapturer
from packet_analyzer.packet_analyzer import PacketAnalyzer

# إعداد الملتقط
capturer = HandshakeCapturer()

# التحقق من الأدوات
if not all(capturer.check_requirements().values()):
    print("⚠️ بعض الأدوات المطلوبة غير مثبتة")
    print("ثبّت: aircrack-ng, tshark, tcpdump")

# التقاط المصافحة
handshake = capturer.capture_handshake_targeted(
    target_bssid="AA:BB:CC:DD:EE:FF",
    channel=11,
    timeout=180
)

if handshake:
    # تحليل المصافحة
    analyzer = PacketAnalyzer()
    hs_info = analyzer.extract_handshake_info(handshake)
    
    if hs_info['has_handshake']:
        print("✓ المصافحة صحيحة وجاهزة للاختبار")
        print(f"الملف: {handshake}")
        print(f"HCCAPX: {handshake.replace('.pcap', '.hccapx')}")
```

### السيناريو 3: تحليل حركة المرور
```python
from packet_analyzer.packet_analyzer import PacketAnalyzer

analyzer = PacketAnalyzer()

# تحليل جميع ملفات الالتقاط
from pathlib import Path

capture_dir = Path("captures")
for pcap in capture_dir.glob("*.pcap"):
    print(f"\n{'='*50}")
    print(f"تحليل: {pcap.name}")
    print('='*50)
    
    results = analyzer.analyze_pcap(str(pcap))
    
    if results:
        stats = results.get('statistics', {})
        print(f"إجمالي الحزم: {stats.get('total_packets', 0)}")
        print(f"استعلامات DNS: {results.get('dns_count', 0)}")
        print(f"طلبات HTTP: {results.get('http_count', 0)}")
        
        # تصدير التقرير
        report_file = str(pcap).replace('.pcap', '_report.txt')
        analyzer.export_analysis(report_file, output_format="txt")
```

---

## 🖥️ تشغيل الواجهة الرسومية

```bash
python main.py
```

### مميزات الواجهة:
- 🎨 تصميم Cyber Neon عصري
- 📊 لوحات معلومات حية
- 📈 رسوم بيانية في الوقت الفعلي
- 🔔 إشعارات وتنبيهات
- 🌐 دعم RTL للعربية
- 💾 حفظ التقارير والتصدير

---

## 📊 قواعد البيانات

يستخدم المشروع SQLite لتخزين:
- سجلات المسح
- نتائج اختبار السرعة
- سجلات الالتقاطات
- أحداث النظام
- إعدادات المستخدم

### الجداول:
1. `wifi_scans` - نتائج مسح WiFi
2. `speed_tests` - نتائج اختبار السرعة
3. `handshake_captures` - سجلات المصافحة
4. `devices` - الأجهزة المكتشفة
5. `events` - أحداث النظام
6. `settings` - الإعدادات

---

## 🔐 الأمان والخصوصية

### ميزات الحماية:
- ✅ تشفير السجلات
- ✅ حماية البيانات المحلية
- ✅ عزل الجلسات
- ✅ وحدات قائمة على الأذونات
- ✅ تصدير آمن للتقارير

### أفضل الممارسات:
1. احفظ الملفات في مجلد آمن
2. استخدم كلمات مرور قوية للملفات المشفرة
3. امسح ملفات الالتقاط بعد الاستخدام
4. لا تشارك الملفات مع آخرين

---

## ⚙️ التكوين المتقدم

### تكوين الذكاء الاصطناعي
```python
from ai.ai_engine import AIEngine

ai = AIEngine()
ai.set_provider("ollama")  # أو "openai", "gemini"
ai.configure(model="llama2", api_key="your-key")
```

### تكوين قاعدة البيانات
```python
from database.db_manager import DatabaseManager

db = DatabaseManager(db_path="custom_db.sqlite")
db.initialize()
```

---

## 🛠️ استكشاف الأخطاء

### مشكلة: وضع المراقبة لا يعمل
**الحل:**
```bash
# لينكس
sudo airmon-ng check kill
sudo airmon-ng start wlan0

# تحقق من الواجهة
iwconfig
```

### مشكلة: عدم وجود حزم EAPOL
**الحل:**
- تأكد من وجود عملاء متصلين
- أرسل حزم deauth لإجبار إعادة الاتصال
- انتظر فترة أطول

### مشكلة: tools غير مثبتة
**الحل:**
```bash
# لينكس
sudo apt install aircrack-ng tshark tcpdump wireshark

# ويندوز
# ثبّت Npcap من npcap.com
# ثبّت Wireshark من wireshark.org
```

---

## 📝 الترخيص والنشر

© 2025 أحمدMostafa إبراهيم - جميع الحقوق محفوظة

**الإصدار الحالي**: 1.5.0 (Professional Security Edition)  
**حالة الإصدار**: مستقر ✅

### الترخيص:
- **النسخة المجتمعية**: مجانية للاستخدام الشخصي والتعليمي
- **النسخة التجارية**: تتطلب ترخيصًا للاستخدام التجاري
- **النسخة المؤسسية**: متاحة للشركات والمنظمات

### المطور:
- **الاسم**: Ahmed Mostafa Ibrahim
- **العلامة التجارية**: Finovate – AHMED EG
- **البريد**: gogom8870@gmail.com
- **الهاتف**: 01225155329

---

## 🗺️ خارطة الطريق

### ✅ المرحلة 1-5 (مكتملة 100%):
- [x] الواجهة الأساسية (GUI + CLI)
- [x] مسح WiFi متعدد النطاقات
- [x] تكامل Windows/Linux/macOS
- [x] تحليل الإشارة والطيف
- [x] التقاط المصافحة WPA/WPA2/WPA3
- [x] هجوم PMKID
- [x] محرك Evil Twin
- [x] تحليل الحزم المتقدم
- [x] نظام WIDS للدفاع
- [x] التحليل الجنائي
- [x] الأتمتة الكاملة
- [x] الذكاء الاصطناعي
- [x] توليد التقارير الاحترافية
- [x] تثبيت الأدوات التلقائي

### 🔄 المرحلة 6 (جارية):
- [x] التحسينات الأمنية
- [x] التوثيق الشامل
- [ ] اختبارات آلية كاملة
- [ ] تحسين الأداء

### 🚀 المرحلة 7 (قادمة - v1.6.0):
- [ ] المزامنة السحابية
- [ ] تطبيق الجوال المرافق
- [ ] التعاون في الوقت الفعلي
- [ ] تنبؤات الذكاء الاصطناعي المتقدمة

### 🔮 المرحلة 8 (مستقبلية - v2.0.0):
- [ ] سوق الإضافات
- [ ] نشر المؤسسات
- [ ] المراقبة الموزعة
- [ ] إعادة كتابة Rust للأداء

---

## 📞 الدعم والتواصل

للأسئلة والدعم الفني:
- 📧 البريد: gogom8870@gmail.com
- 📱 الهاتف: 01225155329
- 💻 GitHub: https://github.com/ahmed1998AM
- 👤 Facebook: https://www.facebook.com/profile.php?id=100049475271023

---

## ⭐ شكر وتقدير

شكرًا لاستخدامك **Finovate WiFiNexus Guardian**!

نهدف إلى توفير أدوات احترافية وأخلاقية لأمن الشبكات. نرجو استخدام هذا البرنامج بمسؤولية ووفقًا للقوانين المحلية.

**استخدم بحكمة، واختبر بأمان! 🛡️**
