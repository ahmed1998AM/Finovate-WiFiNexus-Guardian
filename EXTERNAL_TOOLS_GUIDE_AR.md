# 🔧 External Tools Manager - دليل التثبيت والإعداد

## نظرة عامة

تم إضافة نظام متكامل لإدارة الأدوات الخارجية لبرنامج WiFiNexus Guardian. هذا النظام يمكن المستخدم من:

1. **كشف الأدوات المثبتة** تلقائياً
2. **تثبيت الأدوات المفقودة** بتوجيهات واضحة
3. **إعداد مسارات مخصصة** للأدوات
4. **تصدير تقارير** عن حالة الأدوات

---

## 📋 الأدوات المدعومة

### أدوات الالتقاط والتحليل:
| الأداة | الوصف | المنصات | الحالة |
|--------|-------|---------|--------|
| **Aircrack-ng** | Suite كامل لالتقاط وكسر الشبكات | Win/Linux/Mac | ✅ مطلوب |
| **Npcap** | مكتبة التقاط الحزم للويندوز | Windows فقط | ✅ مطلوب |
| **Wireshark** | محلل بروتوكولات شبكية متقدم | جميع المنصات | ⭐ موصى به |
| **TShark** | نسخة سطر الأوامر من Wireshark | جميع المنصات | ⭐ موصى به |
| **HCXDumptool** | أداة التقاط PMKID/Handshake متقدمة | Linux فقط | ⭐ موصى به |
| **HCXTools** | أدوات تحويل صيغ الهاش | Linux فقط | ⭐ موصى به |

### أدوات الكسر:
| الأداة | الوصف | المنصات | الحالة |
|--------|-------|---------|--------|
| **Hashcat** | أسرع أداة كسر باستخدام GPU | جميع المنصات | ✅ مطلوب |
| **John the Ripper** | كسر كلمات المرور الكلاسيكي | جميع المنصات | ⭐ موصى به |

### أدوات هجوم WPS:
| الأداة | الوصف | المنصات | الحالة |
|--------|-------|---------|--------|
| **Reaver** | هجوم WPS التقليدي | Linux/Mac | اختياري |
| **Bully** | هجوم WPS البديل | Linux فقط | اختياري |

---

## 🚀 الاستخدام عبر CLI

### 1. فحص الأدوات المثبتة:
```bash
python cli.py tools --scan
```

**المخرجات:**
```
🔍 Scanning for installed tools...
============================================================
✅ aircrack-ng     - 1.7                  [wireless]
❌ hashcat         - Not Installed        [cracking]
✅ npcap           - Latest               [capture]
...
============================================================

📊 Summary: 3/10 tools installed
⚠️  Missing tools: hashcat, wireshark, tshark, john, ...
```

### 2. تثبيت أداة محددة:
```bash
python cli.py tools --install aircrack-ng
```

**المخرجات (على Linux):**
```
📦 Installing aircrack-ng...
============================================================
Description: WiFi packet capture and cracking suite
Category: wireless
============================================================

🐧 Linux Installation Method:
  Using apt: aircrack-ng

Run this command:
  sudo apt update && sudo apt install -y aircrack-ng
```

**المخرجات (على Windows):**
```
📦 Installing aircrack-ng...
============================================================
Description: WiFi packet capture and cracking suite
Category: wireless
============================================================

🪟 Windows Installation Method:
  Trying Chocolatey package manager...
  ⚠️  Chocolatey not found
  
  Downloading from: https://www.aircrack-ng.org/files/aircrack-ng-1.7-win.zip

📋 Manual Installation Steps:
  1. Visit: https://www.aircrack-ng.org/installation.html
  2. Download the installer
  3. Run the installer as Administrator
  4. Add installation directory to PATH
```

### 3. تثبيت جميع الأدوات الموصى بها:
```bash
python cli.py tools --install-recommended
```

### 4. إعداد مسار مخصص لأداة:
```bash
python cli.py tools --configure --tool hashcat --path "C:\Program Files\hashcat\hashcat.exe"
```

### 5. تصدير تقرير شامل:
```bash
python cli.py tools --report --output my_tools_report.json
```

### 6. الوضع التفاعلي (القائمة الكاملة):
```bash
python cli.py tools --interactive
```

**القائمة التفاعلية:**
```
======================================================================
  EXTERNAL TOOLS MANAGER - Interactive Menu
======================================================================

Options:
  1. Scan for installed tools
  2. Install a specific tool
  3. Install all recommended tools
  4. Configure custom tool path
  5. Export tools report
  6. Show tool details
  7. Return to main menu

Enter choice (1-7):
```

---

## 💡 التكامل مع باقي البرنامج

### مع Handshake Capturer:
عند بدء الالتقاط، يتحقق البرنامج تلقائياً من الأدوات المطلوبة:

```python
from network.handshake_capturer import HandshakeCapturer

capturer = HandshakeCapturer()
reqs = capturer.check_requirements()

for tool, installed in reqs.items():
    status = "✓" if installed else "✗"
    print(f"  {status} {tool}")
```

**إذا كانت أداة مفقودة:**
```
✗ aircrack-ng
💡 Install with: python cli.py tools --install aircrack-ng
```

### مع Handshake Cracker:
```python
from network.handshake_cracker import HandshakeCracker

cracker = HandshakeCracker()

# التحقق من Hashcat
if not cracker.hashcat_available:
    print("⚠️ Hashcat not found!")
    print("Install with: python cli.py tools --install hashcat")
```

---

## 🔧 التثبيت اليدوي للأدوات

### Windows:

#### 1. Npcap (مطلوب):
```powershell
# تحميل من: https://npcap.com
# تثبيت كمسؤول مع خيار "WinPcap API-compatible Mode"
```

#### 2. Aircrack-ng:
```powershell
# طريقة 1: Chocolatey
choco install aircrack-ng -y

# طريقة 2: يدوي
# 1. حمل من: https://www.aircrack-ng.org/installation.html
# 2. استخرج الملف
# 3. أضف المسار إلى PATH
```

#### 3. Hashcat:
```powershell
# طريقة 1: Chocolatey
choco install hashcat -y

# طريقة 2: يدوي
# 1. حمل من: https://hashcat.net/hashcat/
# 2. استخرج الملف
# 3. شغل: hashcat.exe -I للاختبار
```

#### 4. Wireshark/TShark:
```powershell
# طريقة 1: Chocolatey
choco install wireshark -y

# طريقة 2: يدوي
# 1. حمل من: https://www.wireshark.org/download.html
# 2. ثبت مع خيار "Add to PATH"
```

### Linux:

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y aircrack-ng hashcat wireshark tshark hcxdumptool hcxtools john reaver bully
```

#### Fedora/RHEL:
```bash
sudo dnf install -y aircrack-ng hashcat wireshark john-the-ripper reaver
```

#### Arch Linux:
```bash
sudo pacman -S --noconfirm aircrack-ng hashcat wireshark-qt john reaver bully
```

### macOS:

```bash
# تثبيت Homebrew أولاً إن لم يكن موجوداً
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# تثبيت الأدوات
brew install aircrack-ng hashcat wireshark john-jumbo reaver
```

---

## 📊 تقارير الحالة

### مثال على تقرير JSON:
```json
{
  "timestamp": "2025-01-15T10:30:45.123456",
  "platform": "Windows",
  "architecture": "AMD64",
  "tools": {
    "aircrack-ng": {
      "installed": true,
      "version": "1.7",
      "path": "C:\\Program Files\\Aircrack-ng",
      "executable": "C:\\Program Files\\Aircrack-ng\\aircrack-ng.exe"
    },
    "hashcat": {
      "installed": false,
      "version": "N/A",
      "path": null,
      "executable": null
    }
  },
  "recommendations": ["hashcat", "wireshark", "tshark"]
}
```

---

## ⚙️ تكوين المسارات المخصصة

يتم حفظ المسارات المخصصة في ملف `external_tools/tool_paths.json`:

```json
{
  "hashcat": "C:\\Program Files\\hashcat\\hashcat.exe",
  "aircrack-ng": "/usr/local/bin/aircrack-ng",
  "tshark": "/Applications/Wireshark.app/Contents/MacOS/tshark"
}
```

---

## 🛡️ ملاحظات الأمان

1. **تحميل من مصادر رسمية فقط:**
   - جميع روابط التحميل في قاعدة البيانات تشير للمواقع الرسمية
   - لا يتم تحميل أي ملفات تلقائياً بدون موافقة المستخدم

2. **صلاحيات المسؤول:**
   - بعض الأدوات تتطلب صلاحيات Administrator/root
   - البرنامج يعرض تعليمات واضحة للتثبيت اليدوي

3. **التوافق مع مضادات الفيروسات:**
   - الأدوات المذكورة قانونية ومعترف بها
   - قد تظهر تحذيرات من بعض مضادات الفيروسات (False Positive)
   - يمكن إضافة استثناءات إذا لزم الأمر

---

## 🎯 أفضل الممارسات

### للويندوز:
1. ثبت **Npcap** أولاً (مطلوب للالتقاط)
2. استخدم **Chocolatey** لتسهيل التثبيت
3. أضف جميع الأدوات إلى PATH النظام

### للينكس:
1. استخدم مدير الحزم الرسمي للتوزيع
2. ثبت مجموعة `hcxdumptool + hcxtools` للالتقاط المتقدم
3. تأكد من دعم Monitor Mode لكرت الشبكة

### للماك:
1. ثبت **Homebrew** أولاً
2. استخدمه لتثبيت جميع الأدوات
3. قد تحتاج لصلاحيات خاصة لبعض العمليات

---

## 📞 الدعم

للمزيد من المعلومات:
- 📖 README_AR.md - دليل المستخدم الكامل
- 📄 PROJECT_SUMMARY_AR.md - ملخص المشروع
- 💻 `python cli.py --help` - مساعدة سريعة

---

**المطور**: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)  
**الإصدار**: 1.4.0  
**الحقوق**: © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
