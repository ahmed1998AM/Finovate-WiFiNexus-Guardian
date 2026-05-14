# 🔄 تحديثات برنامج WiFiNexus Guardian - الإصدار 1.2.0

## ✨ التحديثات الرئيسية

### 1. 🪟 التقاط الهاند شيك على الويندوز بدون Monitor Mode

#### المميزات الجديدة:
- **4 طرق التقاط متعددة** تعمل تلقائياً حسب الإمكانيات المتاحة:
  1. **TShark + Npcap** (الأفضل)
  2. **Native Windows WiFi API** عبر netsh trace
  3. **Passive Capture** باستخدام Raw Sockets
  4. **Basic Fallback** باستخدام PowerShell

#### التفاصيل التقنية:

##### الطريقة 1: TShark مع Npcap
```python
def _start_capture_windows_tshark(self, duration: int) -> str:
    # فلتر متقدم لحزم EAPOL و WPA Handshake
    capture_filter = "eapol or wlan type mgt or port 80 or port 443"
    
    # تشغيل TShark مع promiscuous mode
    cmd = [
        "tshark",
        "-i", interface_num,
        "-w", self.capture_file,
        "-f", capture_filter,
        "-a", f"duration:{duration}",
        "-k"  # Promiscuous mode
    ]
```

##### الطريقة 2: Native Windows API
```python
def _start_capture_windows_native(self, duration: int) -> str:
    # استخدام netsh trace لالتقاط حزم WiFi
    cmd_start = [
        "netsh", "trace", "start",
        "capture=yes",
        "provider=Microsoft-Windows-NDIS-PacketCapture",
        "persistent=no"
    ]
```

##### الطريقة 3: Passive Capture (Raw Sockets)
```python
def _run_passive_capture(self, duration: int):
    # إنشاء PCAP file يدوياً
    pcap_header = struct.pack('@IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
    
    # Raw socket لالتقاط الحزم
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    
    # كشف حزم EAPOL في الوقت الفعلي
    if b'\x88\x8e' in packet:
        self.eapol_packets += 1
```

##### الطريقة 4: Fallback Basic
```python
def _start_capture_windows_basic(self, duration: int) -> str:
    # PowerShell script لمراقبة الشبكة
    ps_script = """
    $nets = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
    foreach ($net in $nets) {
        # جمع معلومات الشبكة
    }
    """
```

### 2. 🔍 كشف متقدم لكروت الشبكة

#### دعم الكروت الداخلية والخارجية:
```python
def get_all_windows_interfaces(self) -> List[Dict]:
    # كشف كروت WiFi اللاسلكية
    wlan_result = subprocess.run(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True
    )
    
    # كشف كروت Ethernet
    eth_result = subprocess.run(
        ["netsh", "interface", "show", "interface"],
        capture_output=True
    )
    
    # تمييز الكروت USB عن PCIe
    for iface in interfaces:
        if 'USB' in iface_name:
            iface['bus_type'] = 'USB'
        elif 'PCI' in iface_name or 'PCIe' in iface_name:
            iface['bus_type'] = 'PCIe'
        else:
            iface['bus_type'] = 'Internal'
```

#### الاختيار بين كروت الشبكة المتعددة:
```python
def select_interface(self, interface_name: str = None) -> bool:
    # اختيار تلقائي للكارت المتصل
    for iface in interfaces:
        if iface.get('type') == 'wireless' and iface.get('state') == 'connected':
            self.interface = iface['name']
            return True
    
    # اختيار الكارت الأول المتاح
    return self.select_preferred_interface()
```

### 3. 🎯 تحسينات وضع المراقبة والتقاط

#### أوضاع الالتقاط الثلاثة:
1. **Monitor Mode** (Linux فقط)
2. **Hybrid Mode** (جميع الأنظمة)
3. **Normal/Passive Mode** (بدون متطلبات خاصة)

```python
def __init__(self):
    # وضع السلبي افتراضياً
    self.passive_mode = True
    self.active_deauth = False
    
    # أنماط كشف متقدمة
    self.eapol_pattern = re.compile(r'\x88\x8e')  # EAPOL EtherType
    self.wpa_key_pattern = re.compile(r'WPA|\x30\x14\x01\x00\x00\x0f\xac\x02')
```

#### كشف ذكي للهاند شيك:
```python
def _check_handshake_in_file(self, filepath: str) -> bool:
    # طريقة 1: TShark لكشف حزم EAPOL
    result = subprocess.run(
        ["tshark", "-r", filepath, "-Y", "eapol"],
        capture_output=True
    )
    eapol_count = len(result.stdout.strip().split('\n'))
    
    # 4-way handshake يحتاج 4 حزم EAPOL على الأقل
    if eapol_count >= 4:
        return True
    
    # طريقة 2: Aircrack-ng للتحقق
    result = subprocess.run(["aircrack-ng", filepath])
    if "handshake" in result.stdout.lower():
        return True
```

### 4. 🛡️ تحسينات الأمان وعدم الكشف كبرنامج ضار

#### Safety Mode افتراضي:
```python
def __init__(self):
    self.safety_mode = True  # مفعل افتراضياً
    self.legal_warning_shown = False
    self.stealth_mode = False
```

#### تسجيل جميع العمليات (Audit Logging):
```python
def _log_handshake_capture(self):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "target_bssid": self.target_bssid,
        "capture_file": self.capture_file,
        "platform": self.platform,
        "interface": self.interface,
        "method": "passive" if self.passive_mode else "active"
    }
    
    # حفظ في ملف السجلات
    with open(log_file, 'a') as f:
        f.write(f"{log_entry['timestamp']} | BSSID: {log_entry['target_bssid']} | Method: {log_entry['method']}\n")
```

#### تحذيرات قانونية واضحة:
```python
def show_legal_warning(self):
    warning = """
    ⚠️ تحذير قانوني هام
    
    هذا البرنامج مخصص فقط لـ:
    - اختبار الاختراق المصرح به
    - التدقيق الأمني للشبكات المملوكة لك
    - الأغراض التعليمية في بيئة خاضعة للرقابة
    
    الاستخدام غير المصرح به غير قانوني وقد يعرضك للمساءلة القانونية.
    """
    print(warning)
```

### 5. 📊 إحصائيات متقدمة للتقاط

```python
def __init__(self):
    # إحصائيات مفصلة
    self.packets_captured = 0
    self.eapol_packets = 0
    self.beacon_frames = 0
    self.probe_requests = 0
    self.data_frames = 0
    self.capture_start_time = None
```

#### تقرير تفصيلي بعد الالتقاط:
```python
def get_capture_report(self) -> Dict:
    return {
        "total_packets": self.packets_captured,
        "eapol_packets": self.eapol_packets,
        "beacon_frames": self.beacon_frames,
        "probe_requests": self.probe_requests,
        "handshake_detected": self.handshake_detected,
        "capture_duration": time.time() - self.capture_start_time,
        "packets_per_second": self.packets_captured / (time.time() - self.capture_start_time)
    }
```

### 6. 🔄 تحويل تلقائي لصيغ متعددة

```python
def _convert_to_hccapx(self):
    """تحويل PCAP إلى HCCAPX لـ Hashcat"""
    hccapx_file = self.capture_file.replace('.pcap', '.hccapx')
    
    # محاولة التحويل بـ cap2hccapx
    subprocess.run(["cap2hccapx", self.capture_file, hccapx_file])
    
    # أو استخدام aircrack-ng
    subprocess.run(["aircrack-ng", self.capture_file, "-J", hccapx_file.replace('.hccapx', '')])

def _convert_etl_to_pcap(self):
    """تحويل ETL (Windows) إلى PCAP"""
    etl_file = self.capture_file.replace('.pcap', '.etl')
    if os.path.exists(etl_file):
        # استخدام Microsoft Message Analyzer أو tshark
        subprocess.run(["tshark", "-r", etl_file, "-w", self.capture_file])
```

## 📋 أمثلة الاستخدام

### على Windows:
```bash
# التقاط تلقائي بأفضل طريقة متاحة
python cli.py capture --target AA:BB:CC:DD:EE:FF --channel 6

# تحديد كارت شبكة معين
python cli.py capture --interface "Wi-Fi" --target AA:BB:CC:DD:EE:FF

# وضع سلبي فقط (بدون أي عمليات نشطة)
python cli.py capture --passive --duration 60
```

### على Linux:
```bash
# وضع المراقبة الكامل
python cli.py capture --monitor --target AA:BB:CC:DD:EE:FF

# وضع هجين
python cli.py capture --hybrid --deauth
```

## 🔧 المتطلبات الجديدة

### Windows:
- **Npcap** (موصى به) - https://npcap.com
- **Wireshark/TShark** (اختياري)
- **.NET Framework 4.5+**
- **صلاحيات Administrator** لـ Raw Sockets

### Linux:
- **Aircrack-ng suite**
- **TShark/Wireshark** (اختياري)
- **tcpdump**

## 🎯 الفوائد الأمنية

1. **عدم الكشف كبرنامج ضار**:
   - لا حاجة لـ Monitor Mode على Windows
   - استخدام APIs نظامية فقط
   - Safety Mode افتراضي

2. **التقاط موثوق**:
   - 4 طرق احتياطية
   - كشف ذكي لحزم EAPOL
   - تحويل تلقائي للصيغ

3. **دعم واسع**:
   - جميع كروت الشبكة (USB/PCIe/Internal)
   - Windows 10/11, Linux, macOS
   - عمل بدون تعقيدات التعريفات

## 📝 ملاحظات هامة

⚠️ **تحذير قانوني**: 
- استخدم البرنامج فقط على الشبكات المملوكة لك
- الحصول على إذن كتابي قبل اختبار شبكات الآخرين
- الالتزام بالقوانين المحلية والدولية

💡 **نصائح للأداء الأفضل**:
- على Windows: ثبت Npcap للحصول على أفضل أداء
- استخدم كروت WiFi الخارجية لدعم أفضل
- تأكد من وجود عميل متصل بالشبكة المستهدفة

---

**المطور**: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)  
**الإصدار**: 1.2.0  
**الحقوق**: © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
