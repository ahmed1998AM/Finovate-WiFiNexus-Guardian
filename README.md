# WiFiNexus Guardian v1.0.0 - README
# Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
# © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

# 🛡️ WiFiNexus Guardian v1.0.0
## Professional Wireless Intelligence Platform

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-orange.svg)
![License](https://img.shields.io/badge/license-MIT-red.svg)

**أداة احترافية لاختبار اختراق الشبكات اللاسلكية ومراقبتها**

*Professional Tool for Wireless Network Penetration Testing and Monitoring*

</div>

---

## 📋 المحتويات / Table of Contents

1. [نظرة عامة / Overview](#-نظرة-عامة--overview)
2. [الميزات الرئيسية / Key Features](#-الميزات-الرئيسية--key-features)
3. [المتطلبات / Requirements](#-المتطلبات--requirements)
4. [التثبيت / Installation](#-التثبيت--installation)
5. [الاستخدام / Usage](#-الاستخدام--usage)
6. [السمات / Themes](#-السمات--themes)
7. [اللغات / Languages](#-اللغات--languages)
8. [البنية / Project Structure](#-البنية--project-structure)
9. [الأمان والقانونية / Security & Legal](#-الأمان-والقانونية--security--legal)
10. [المطور / Developer](#-المطور--developer)

---

## 🌟 نظرة عامة / Overview

WiFiNexus Guardian هو منصة أمنية لاسلكية متكاملة تجمع بين أدوات اختبار الاختراق المتقدمة وأنظمة المراقبة الدفاعية في واجهة واحدة سهلة الاستخدام.

**WiFiNexus Guardian** is a comprehensive wireless security platform that combines advanced penetration testing tools with defensive monitoring systems in a single, easy-to-use interface.

### الواجهات المتاحة / Available Interfaces:
- 🖥️ **GUI** - واجهة رسومية كاملة مع سمات متعددة
- 💻 **CLI** - واجهة سطر أوامر احترافية
- 📱 **TUI** - واجهة نصية تفاعلية

---

## ✨ الميزات الرئيسية / Key Features

### 🔍 المسح والاستكشاف / Scanning & Discovery
- ✅ مسح شبكات WiFi متعدد النطاقات (2.4GHz, 5GHz, 6GHz)
- ✅ كشف الشبكات المخفية
- ✅ تحليل قوة الإشارة
- ✅ تحديد أنواع التشفير الأمنية

### ⚔️ أدوات الهجوم / Attack Tools
- ✅ هجوم PMKID (Hashcat Mode 16800)
- ✅ التقاط Handshake WPA/WPA2
- ✅ هجوم Deauthentication
- ✅ Evil Twin Engine
- ✅ Beacon Flood

### 🛡️ الدفاع والمراقبة / Defense & Monitoring
- ✅ نظام كشف التسلل اللاسلكي (WIDS)
- ✅ وضع التخفي (Stealth Mode)
- ✅ مراقبة الحزم في الوقت الفعلي
- ✅ كشف هجمات Beacon Flooding

### 📊 التقارير / Reports
- ✅ تقارير PDF احترافية
- ✅ تقارير HTML تفاعلية
- ✅ تصدير JSON/TXT
- ✅ تكامل مع WiGLE.net

### 🎨 السمات / Themes
- ✅ **Cyber Neon** - سمة سيبربانك نيون احترافية
- ✅ **Dark Professional** - سمة داكنة Material Design
- ✅ **Light Professional** - سمة فاتحة نظيفة

### 🌐 اللغات / Languages
- ✅ الإنجليزية (English)
- ✅ العربية (Arabic)
- ✅ الفرنسية (Français)

### 🐳 Docker والحاويات / Docker & Containers
- ✅ Dockerfile كامل
- ✅ docker-compose.yml
- ✅ دعم CI/CD Pipeline

### 🧪 الاختبارات / Testing
- ✅ 24+ اختبار آلي
- ✅ pytest integration
- ✅ Coverage reporting

---

## 📦 المتطلبات / Requirements

### الحد الأدنى / Minimum
- Python 3.8+
- Linux/Windows/macOS
- واجهة شبكة لاسلكية تدعم Monitor Mode

### الموصى به / Recommended
- Python 3.10+
- Kali Linux أو Parrot OS
- بطاقة Alfa AWUS036NHA أو مشابه

### الاعتماديات / Dependencies
```bash
pip install -r requirements.txt
```

#### requirements.txt يتضمن:
```
PySide6>=6.5.0        # GUI
rich>=13.0.0          # TUI & CLI styling
textual>=0.40.0       # TUI framework
scapy>=2.5.0          # Packet manipulation
pywifi>=1.1.1         # WiFi control
reportlab>=4.0.0      # PDF reports
python-docx>=0.8.11   # DOCX reports
pytest>=7.4.0         # Testing
pytest-cov>=4.1.0     # Coverage
requests>=2.31.0      # API calls
```

---

## 🚀 التثبيت / Installation

### الطريقة 1: التثبيت اليدوي / Manual Installation

```bash
# استنساخ المستودع
git clone https://github.com/yourusername/wifinexus-guardian.git
cd wifinexus-guardian

# تثبيت الاعتماديات
pip install -r requirements.txt

# تثبيت الأدوات الخارجية (اختياري)
sudo ./scripts/install_external_tools.sh
```

### الطريقة 2: Docker

```bash
# بناء الصورة
docker build -t wifinexus-guardian:1.0.0 .

# تشغيل الحاوية
docker run --rm -it \
  --network host \
  --cap-add NET_ADMIN \
  -v $(pwd)/captures:/app/captures \
  wifinexus-guardian:1.0.0
```

### الطريقة 3: Docker Compose

```bash
docker-compose up -d
```

---

## 💻 الاستخدام / Usage

### واجهة الأوامر / CLI

```bash
# عرض المساعدة
python cli.py --help

# مسح الشبكات
python cli.py scan --band all --verbose

# عرض الواجهات
python cli.py interfaces

# هجوم PMKID
python cli.py pmkid --interface wlan0 --target AA:BB:CC:DD:EE:FF

# التقاط Handshake
python cli.py handshake --interface wlan0 --capture

# تشغيل الوضع الآمن
python cli.py security --stealth enable

# تصدير تقرير
python cli.py report --format pdf --output report.pdf
```

### الواجهة الرسومية / GUI

```bash
# تشغيل الواجهة الرسومية
python gui/main_window.py

# أو عبر CLI
python cli.py gui --theme cyber_neon --lang ar
```

### الواجهة النصية / TUI

```bash
# تشغيل الواجهة النصية
python gui/tui_interface.py
```

---

## 🎨 السمات / Themes

يتوفر 3 سمات احترافية:

| السمة | الوصف | الوضع |
|-------|-------|-------|
| Cyber Neon | سيبربانك نيون | داكن |
| Dark Professional | Material Design | داكن |
| Light Professional | نظيف وعصري | فاتح |

### تغيير السمة:

```python
from themes import ThemeManager

manager = ThemeManager()
manager.set_theme('dark')  # أو 'cyber_neon' أو 'light'
```

أو من CLI:
```bash
python cli.py --theme dark
```

---

## 🌐 اللغات / Languages

يدعم التطبيق 3 لغات:

| الكود | اللغة | الاسم الأصلي |
|-------|------|-------------|
| en | English | English |
| ar | Arabic | العربية |
| fr | French | Français |

### تغيير اللغة:

```python
from assets import translator

translator.set_language('ar')
print(translator.get('app_title'))  # واي فاي نكسوس غارديان
```

أو من CLI:
```bash
python cli.py --lang ar
```

---

## 📁 البنية / Project Structure

```
wifinexus-guardian/
├── ai/                     # محرك الذكاء الاصطناعي
├── attacks/                # أدوات الهجوم
├── automation/             # الأتمتة
├── assets/                 # الترجمات والأصول
├── captures/               # ملفات الالتقاط
├── core/                   # النواة الأساسية
├── database/               # قاعدة البيانات
├── defense/                # أدوات الدفاع
├── docs/                   # التوثيق
├── drivers/                # التعريفات
├── forensics/              # التحليل الجنائي
├── gui/                    # الواجهات الرسومية
├── integrations/           # التكاملات الخارجية
├── logs/                   # السجلات
├── network/                # أدوات الشبكة
├── packet_analyzer/        # محلل الحزم
├── plugins/                # الإضافات
├── profiles/               # ملفات التعريف
├── reports/                # مولدات التقارير
├── tests/                  # الاختبارات
├── themes/                 # السمات
├── tools/                  # الأدوات المساعدة
├── updates/                # نظام التحديثات
├── wordlists/              # قوائم الكلمات
├── cli.py                  # واجهة الأوامر
├── main.py                 # نقطة الدخول
├── config.py               # الإعدادات
├── Dockerfile              # تعريف Docker
├── docker-compose.yml      # تكوين Docker Compose
└── requirements.txt        # الاعتماديات
```

---

## ⚖️ الأمان والقانونية / Security & Legal

### ⚠️ تحذير هام / Important Warning

هذه الأداة مخصصة فقط للاستخدام القانوني في:
- اختبار الاختراق المصرح به
- مراجعة الأنظمة التي تمتلكها
- الأغراض التعليمية والبحثية

**لا تستخدم هذه الأداة على شبكات لا تملك إذنًا صريحًا لاختبارها.**

### الترخيص / License
MIT License - راجع ملف LICENSE للتفاصيل.

### إخلاء المسؤولية / Disclaimer
المطور غير مسؤول عن أي سوء استخدام لهذه الأداة.

---

## 👨‍💻 المطور / Developer

<div align="center">

**Ahmed Mostafa Ibrahim**  
*Finovate – AHMED EG*

© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

</div>

### التواصل / Contact
- GitHub: @ahmed-eg
- Email: ahmed@finovate.eg

---

## 📝 الإصدار / Version

**الإصدار الحالي:** 1.0.0  
**تاريخ الإصدار:** 2025-05-15  
**حالة الإصدار:** Stable

---

<div align="center">

### ⭐ إذا أعجبك المشروع، يرجى تقييمه بنجمة! ⭐

**WiFiNexus Guardian v1.0.0**  
*Professional Wireless Intelligence Platform*

</div>
