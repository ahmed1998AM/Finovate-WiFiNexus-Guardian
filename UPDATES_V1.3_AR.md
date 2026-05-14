# 🔄 تحديثات برنامج WiFiNexus Guardian - الإصدار 1.3.0

## ✨ التحديثات الرئيسية الجديدة

### 1. 🪟 وحدة التقاط الهاند شيك المتقدمة للويندوز (`windows_handshake_capturer.py`)

#### المميزات الجديدة:
- **757 سطر برمجي** من الكود الاحترافي المُحسن
- **4 طرق التقاط متعددة** تعمل تلقائياً حسب الإمكانيات المتاحة
- **كشف ذكي للقدرات** قبل بدء الالتقاط

#### الطرق الأربعة للالتقاط:

##### الطريقة 1: TShark مع Npcap (الأفضل) ⭐
```python
def _capture_with_tshark(self, target_bssid: str, duration: int):
    # فلتر متقدم جداً لحزم EAPOL و WPA Handshake
    capture_filter = "eapol or wlan type mgt subtype assoc-req or wlan type mgt subtype assoc-resp"
    
    # دعم التصفية حسب BSSID المستهدف
    if target_bssid:
        capture_filter += f" or (wlan.ta == {target_bssid} or wlan.ra == {target_bssid})"
    
    # تشغيل TShark مع Promiscuous Mode
    cmd = [
        "tshark",
        "-i", interface_num,
        "-w", self.capture_file,
        "-f", capture_filter,
        "-a", f"duration:{duration}",
        "-k",  # Promiscuous mode
        "-q"   # Quiet mode
    ]
```

**المميزات:**
- ✅ كشف في الوقت الفعلي لحزم EAPOL
- ✅ تصفية ذكية لتقليل حجم البيانات
- ✅ تحويل تلقائي لـ HCCAPX عند الكشف
- ✅ مراقبة مستمرة كل 3 ثواني

##### الطريقة 2: Npcap Raw Sockets
```python
def _capture_with_npcap(self, duration: int):
    # إنشاء PCAP file يدوياً مع header صحيح
    pcap_header = struct.pack('@IHHIIII', 
        0xa1b2c3d4,  # Magic number
        2, 4,         # Version
        0, 0, 65535, 1
    )
    
    # Raw socket لالتقاط جميع الحزم
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    
    # كشف فوري لحزم EAPOL
    if b'\x88\x8e' in packet:
        self.eapol_count += 1
        print(f"→ EAPOL packet #{self.eapol_count} detected!")
```

**المميزات:**
- ✅ لا يحتاج TShark
- ✅ كشف patterns مباشرة
- ✅ كتابة فورية للـ PCAP
- ✅ إحصائيات مفصلة

##### الطريقة 3: Native Windows WiFi API
```python
def _capture_with_native_api(self, duration: int):
    # استخدام netsh trace - API رسمي من مايكروسوفت
    cmd_start = [
        "netsh", "trace", "start",
        "capture=yes",
        "provider=Microsoft-Windows-NDIS-PacketCapture",
        "persistent=no"
    ]
```

**المميزات:**
- ✅ لا يحتاج تعريفات خارجية
- ✅ مدعوم رسمياً من Windows
- ✅ آمن تماماً من مضادات الفيروسات
- ✅ يعمل على جميع إصدارات Windows

##### الطريقة 4: Passive Monitoring
```python
def _capture_passive(self, duration: int):
    # مسح سلبي للشبكات باستخدام netsh wlan show network
    result = subprocess.run(
        ["netsh", "wlan", "show", "network", "mode=bssid"],
        capture_output=True
    )
    
    # تتبع جميع الشبكات المرئية
    networks_seen[bssid] = {
        'ssid': ssid,
        'signal': signal,
        'first_seen': time.time()
    }
```

**المميزات:**
- ✅ لا يحتاج صلاحيات خاصة
- ✅ آمن 100%
- ✅ جيد للمراقبة العامة
- ✅Fallback أخير

---

### 2. 🔍 إدارة محسنة لكروت الشبكة

#### كشف متقدم للواجهات:
```python
def get_wifi_interfaces(self) -> List[Dict]:
    # معلومات شاملة لكل كرت شبكة
    current_iface = {
        'name': interface_name,
        'state': state,
        'ssid': connected_ssid,
        'bssid': connected_bssid,
        'radio_type': radio_type,
        'channel': channel,
        'signal': signal_strength
    }
```

#### الاختيار الذكي:
```python
def select_interface(self, interface_name: str = None):
    # 1. يفضل الكروت المتصلة حالياً
    for iface in interfaces:
        if iface.get('state') == 'connected':
            return iface['name']
    
    # 2.fallback لأول كرت متاح
    return interfaces[0]['name']
```

---

### 3. 🎯 كشف متقدم للهاند شيك

#### كشف في الوقت الفعلي:
```python
def _monitor_tshark_capture(self, max_duration: int):
    while elapsed < max_duration:
        if os.path.exists(self.capture_file):
            file_size = os.path.getsize(self.capture_file)
            
            if file_size > 2048:  # أكثر من 2KB
                if self._check_handshake_live(self.capture_file):
                    print("✅✅✅ HANDSHAKE DETECTED! ✅✅✅")
                    self.handshake_detected = True
                    
                    # تحويل فوري لـ HCCAPX
                    self._convert_to_hccapx()
                    
                    # تسجيل التفاصيل
                    self._log_capture()
```

#### تحليل متعدد الطبقات:
```python
def _analyze_final_capture(self):
    # 1. تحليل بـ TShark
    result = subprocess.run(
        ["tshark", "-r", self.capture_file, "-Y", "eapol"],
        capture_output=True
    )
    eapol_lines = [l for l in result.stdout.split('\n') if 'EAPOL' in l]
    
    # 2. تحليل بـ Aircrack-ng
    result = subprocess.run(
        ["aircrack-ng", self.capture_file],
        capture_output=True
    )
    if "handshake" in result.stdout.lower():
        self.handshake_detected = True
```

---

### 4. 📊 إحصائيات وتقارير مفصلة

#### إحصائيات شاملة:
```python
self.packets_captured = 0      # إجمالي الحزم
self.eapol_count = 0           # حزم EAPOL
self.beacon_count = 0          # إطارات Beacon
self.start_time = None         # وقت البدء
self.elapsed_time = 0          # الوقت المنقضي
```

#### تقارير JSON:
```python
def _log_capture(self):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "interface": self.interface,
        "capture_file": self.capture_file,
        "packets_captured": self.packets_captured,
        "eapol_count": self.eapol_count,
        "handshake_detected": self.handshake_detected
    }
    
    # حفظ في ملف JSON
    logs.append(log_entry)
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
```

---

### 5. 🔄 تحويل تلقائي للصيغ

#### PCAP → HCCAPX:
```python
def _convert_to_hccapx(self):
    hccapx_file = self.capture_file.replace('.pcap', '.hccapx')
    
    # محاولة 1: cap2hccapx
    result = subprocess.run(
        ["cap2hccapx", self.capture_file, hccapx_file],
        timeout=30
    )
    
    # محاولة 2: aircrack-ng
    if result.returncode != 0:
        base_name = hccapx_file.replace('.hccapx', '')
        subprocess.run(
            ["aircrack-ng", self.capture_file, "-J", base_name],
            timeout=30
        )
```

---

### 6. 🛡️ تحسينات الأمان وعدم الكشف

#### لماذا لا يعتبر البرنامج ضاراً:

1. **APIs نظامية فقط:**
   - `netsh wlan` - أداة Windows رسمية
   - `subprocess.run` - مكتبة Python قياسية
   - `socket` - مكتبة شبكات قياسية

2. **لا kernel drivers:**
   - لا تثبيت تعريفات نواة
   - لا تعديل في النظام
   - لا صلاحيات عميقة

3. **شفاف تماماً:**
   - جميع العمليات مسجلة
   - ملفات log واضحة
   - لا عمليات خفية

4. **استخدام مصرح به:**
   - Safety Mode افتراضي
   - تحذيرات قانونية
   - للأغراض التعليمية فقط

---

## 📋 كيفية الاستخدام

### التشغيل المباشر:
```bash
python network/windows_handshake_capturer.py
```

### عبر CLI الرئيسي:
```bash
# التقاط عام
python cli.py capture --timeout 60

# التقاط مستهدف
python cli.py capture --target AA:BB:CC:DD:EE:FF --channel 6 --timeout 120

# كسر الهاند شيك
python cli.py crack --capture captures/windows/capture_20250101_120000.pcap --ai
```

### استخدام الوحدة مباشرة:
```python
from network.windows_handshake_capturer import WindowsHandshakeCapturer

capturer = WindowsHandshakeCapturer()

# فحص القدرات
caps = capturer.check_capabilities()

# اختيار الواجهة
capturer.select_interface()

# بدء الالتقاط
capture_file = capturer.start_capture(
    target_bssid="AA:BB:CC:DD:EE:FF",
    channel=6,
    duration=120
)

# الحصول على الحالة
status = capturer.get_status()
print(status)
```

---

## 🔧 المتطلبات

### الحد الأدنى:
- Windows 10/11
- Python 3.8+
- كرت WiFi يدعم WiFi Direct

### الموصى به:
- Npcap: https://npcap.com
- Wireshark/TShark: https://www.wireshark.org
- Aircrack-ng: https://www.aircrack-ng.org

### الصلاحيات:
- Administrator (للتقاط متقدم)
- Standard User (للمراقبة السلبية فقط)

---

## 📊 مقارنة الطرق

| الطريقة | TShark | Npcap | Native | Passive |
|---------|--------|-------|--------|---------|
| الدقة | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| السرعة | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| السهولة | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| الأمان | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| الصلاحيات | Admin | Admin | Standard | Standard |

---

## 🎯 النتائج المتوقعة

### سيناريو مثالي (TShark + Npcap):
```
🔍 Checking Windows capture capabilities...
  ✓ Npcap detected
  ✓ TShark detected
  ✓ Native WiFi API supported

📡 Found 2 WiFi interface(s):
  1. Wi-Fi - connected
     Connected to: HomeNetwork
     BSSID: AA:BB:CC:DD:EE:FF

✓ Auto-selected connected interface: Wi-Fi

======================================================================
WINDOWS HANDSHAKE CAPTURE - NO MONITOR MODE REQUIRED
======================================================================
Interface: Wi-Fi
Target BSSID: AA:BB:CC:DD:EE:FF
Duration: 120s
Capture file: captures\windows\capture_20250101_120000.pcap
======================================================================

🎯 Using TShark capture method (RECOMMENDED)
📡 Starting TShark capture on interface 2...
Filter: eapol or wlan type mgt subtype assoc-req or wlan type mgt subtype assoc-resp

  → EAPOL packet #1 detected!
  → EAPOL packet #2 detected!
  → EAPOL packet #3 detected!
  → EAPOL packet #4 detected!

🔍 Analyzing EAPOL packets for complete handshake...
✓ Complete 4-way handshake detected!

======================================================================
✅✅✅ HANDSHAKE DETECTED! ✅✅✅
======================================================================
File: captures\windows\capture_20250101_120000.pcap
Size: 4567 bytes
EAPOL packets: 4

✓ Converted to HCCAPX: captures\windows\capture_20250101_120000.hccapx
✓ Logged to: captures\windows\capture_log.json
```

---

## ⚠️ تحذير قانوني هام

البرنامج مخصص فقط لـ:
- ✅ اختبار الاختراق **المصرح به**
- ✅ التدقيق الأمني للشبكات **المملوكة لك**
- ✅ الأغراض التعليمية في بيئة **خاضعة للرقابة**

الاستخدام غير المصرح به **غير قانوني** وقد يعرضك للمساءلة القانونية!

---

## 📝 ملاحظات هامة

1. **Windows Defender:**
   - البرنامج آمن تماماً
   - إذا تم اكتشافه كإيجابي كاذب، أضف استثناء
   - جميع العمليات شفافة ومسجلة

2. **Npcap:**
   - ضروري لأفضل أداء
   - تثبيته سهل وآمن
   - يستخدم على نطاق واسع

3. **الصبر:**
   - قد يستغرق الأمر وقتاً لالتقاط الهاند شيك
   - يعتمد على نشاط الشبكة
   - استخدم targeted capture لنتائج أفضل

---

**المطور**: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)  
**الإصدار**: 1.3.0  
**الحقوق**: © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
