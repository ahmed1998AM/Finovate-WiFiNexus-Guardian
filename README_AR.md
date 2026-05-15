# 🚀 WiFiNexus Guardian - الإصدار الاحترافي v1.0.0

## نظام اختبار الاختراق اللاسلكي المتقدم

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

**أداة احترافية لاختبار اختراق شبكات WiFi مع ذكاء اصطناعي متقدم**

</div>

---

## 🔍 نظرة عامة

WiFiNexus Guardian هو نظام متكامل لاختبار اختراق الشبكات اللاسلكية، مصمم للمحترفين والباحثين الأمنيين. يجمع بين أدوات الاختراق التقليدية وتقنيات الذكاء الاصطناعي المتقدمة لتنفيذ هجمات ذكية ومتكيفة.

### ✨ المكونات الجديدة في v1.0.0

| المكون | الوصف | الحالة |
|--------|-------|--------|
| **Dynamic Hardware Manager** | كشف واختبار العتاد تلقائيًا | ✅ مكتمل |
| **Tactical Attack Engine** | قرارات هجومية ذكية | ✅ مكتمل |
| **Stealth & Evasion System** | تغيير الهوية وإزالة الآثار | ✅ مكتمل |
| **Attack Scenarios** | 5 سيناريوهات هجوم آلية | ✅ مكتمل |
| **AI Agents** | 4 وكلاء ذكاء اصطناعي | ✅ مكتمل |

---

## 🎯 الميزات الرئيسية

### الوحدات الأساسية

1. **إدارة العتاد الديناميكية**
   - كشف تلقائي للواجهات اللاسلكية
   - اختبار دعم Monitor Mode و Packet Injection
   - تقييم أداء الواجهات
   - استعادة تلقائية عند الأخطاء

2. **المحرك التكتيكي للهجوم**
   - 4 مستويات تخفي (Aggressive, Balanced, Silent, Ghost)
   - 4 مستويات مخاطرة (Low, Medium, High, Critical)
   - تخطيط سلاسل هجوم مترابطة
   - تقييم ثغرات ذكي

3. **نظام التخفي والتحايل**
   - تغيير عنوان MAC بمصنّعين واقعيين
   - تغيير اسم الجهاز
   - تنظيف السجلات
   - إزالة آثار التشغيل

4. **سيناريوهات الهجوم الآلية**
   - Quiet Capture: التقاط هادئ للمصافحة
   - Aggressive Crack: هجوم سريع متعدد المتجهات
   - WPS Focus: هجوم مركز على WPS
   - Evil Twin Ops: محطة وهمية خبيثة
   - Recon Only: استطلاع فقط بدون هجوم

5. **وكلاء الذكاء الاصطناعي**
   - NetworkHealthAgent: تحليل صحة الشبكة
   - SecurityAdvisorAgent: توصيات أمنية
   - PasswordGeneratorAgent: توليد كلمات مرور
   - ThreatDetectionAgent: كشف التهديدات

---

## 💻 متطلبات النظام

### الحد الأدنى
- **OS**: Linux (مفضل)، Windows 10+، macOS 11+
- **CPU**: Dual-core 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 500 MB
- **Python**: 3.8+

### الموصى به
- **OS**: Kali Linux / Parrot OS
- **CPU**: Quad-core 3.0 GHz+
- **RAM**: 8 GB+
- **WiFi Adapter**: Atheros AR9271 أو Ralink RT3070

### الأدوات المطلوبة
```bash
aircrack-ng, hashcat, hcxdumptool, reaver, wireshark
```

---

## 📦 التثبيت

```bash
# استنساخ المستودع
git clone https://github.com/yourusername/wifinexus-guardian.git
cd wifinexus-guardian

# تثبيت المتطلبات
pip install -r requirements.txt

# تثبيت الأدوات (Linux)
sudo apt install -y aircrack-ng hashcat wireshark hcxdumptool reaver

# التحقق
python main.py --check
```

---

## 🚀 الاستخدام

### واجهة سطر الأوامر

```bash
# الواجهة الرسومية
python main.py --gui

# مسح العتاد
python main.py --hardware-scan

# سيناريو هادئ
python main.py --scenario quiet_capture

# تحليل الذكاء الاصطناعي
python main.py --ai-analyze

# وضع التخفي
python main.py --stealth expert
```

### استخدام المكتبة

```python
# إدارة العتاد
from core.hardware_manager import get_hardware_manager
hw = get_hardware_manager()
interfaces = hw.detect_all_interfaces()
best = hw.get_best_interface("attack")

# المحرك التكتيكي
from tactical.attack_engine import get_tactical_engine, StealthMode
engine = get_tactical_engine()
engine.set_stealth_mode(StealthMode.SILENT)
target = engine.add_target("AA:BB:CC:DD:EE:FF", "WiFi", 6, -50, "WPA2")

# التخفي
from stealth.evasion import get_stealth_system, EvasionLevel
stealth = get_stealth_system()
stealth.evasion_level = EvasionLevel.EXPERT
identity = stealth.create_identity(vendor="Atheros")

# السيناريوهات
from scenarios.attack_chains import get_scenarios_manager, ScenarioType
scenarios = get_scenarios_manager()
result = scenarios.execute_scenario(ScenarioType.QUIET_CAPTURE)
```

---

## ⚔️ سيناريوهات الهجوم

| السيناريو | الخطوات | المدة | النجاح | الكشف |
|-----------|---------|-------|--------|-------|
| Quiet Capture | 7 | ~6 دقيقة | 75% | منخفض |
| Aggressive Crack | 9 | ~15 دقيقة | 85% | عالي |
| WPS Focus | 5 | ~10 دقائق | 60% | متوسط |
| Evil Twin Ops | 8 | ~30 دقيقة | 50% | عالي جداً |
| Recon Only | 5 | ~8 دقائق | 95% | منخفض جداً |

---

## 🛡️ مستويات التخفي

| المستوى | الوصف | فاصل التغيير |
|---------|-------|--------------|
| Basic | تغيير MAC بسيط | كل ساعة |
| Advanced | هوية كاملة | كل 15 دقيقة |
| Expert | محاكاة سلوكية | كل 5 دقائق |
| Paranoid | أقصى تخفي | كل دقيقة |

---

## ⚠️ إخلاء المسؤولية

هذه الأداة للأغراض التعليمية والبحث الأمني المصرح به فقط.

- ✅ استخدم فقط على شبكاتك الخاصة أو بإذن كتابي
- ✅ التزم بالقوانين المحلية
- ❌ لا تستخدم للوصول غير المصرح به

**المطورون غير مسؤولين عن سوء الاستخدام.**

---

## 📄 الترخيص

مرخص تحت [MIT License](LICENSE).

---

<div align="center">

**WiFiNexus Guardian v1.0.0** - صنع بـ ❤️ للأمن السيبراني

</div>
