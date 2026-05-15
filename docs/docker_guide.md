# WiFiNexus Guardian - دليل التشغيل عبر Docker

## نظرة عامة

يوفر هذا الدليل تعليمات مفصلة لتشغيل WiFiNexus Guardian داخل حاوية Docker معزولة وآمنة.

## المتطلبات المسبقة

- Docker 20.10 أو أحدث
- Docker Compose 2.0 أو أحدث (اختياري)
- محول WiFi يدعم وضع المراقبة
- صلاحيات root/sudo

## التثبيت السريع

### الطريقة 1: استخدام Docker Compose (موصى بها)

```bash
# بناء وتشغيل الحاوية
docker-compose up -d

# عرض السجلات
docker-compose logs -f wifinexus

# إيقاف الخدمة
docker-compose down
```

### الطريقة 2: استخدام Docker مباشرة

```bash
# بناء الصورة
docker build -t wifinexus-guardian:latest .

# تشغيل الحاوية
docker run --rm -it \
  --privileged \
  --network host \
  -v $(pwd)/captures:/app/captures \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/database:/app/database \
  wifinexus-guardian:latest --help
```

## التكوين المتقدم

### متغيرات البيئة

يمكنك تخصيص السلوك عبر متغيرات البيئة:

```yaml
environment:
  - DEBUG=false           # تفعيل وضع التصحيح
  - LOG_LEVEL=INFO        # مستوى السجلات (DEBUG, INFO, WARNING, ERROR)
  - CAPTURE_DIR=/app/captures
  - REPORTS_DIR=/app/reports
  - WIGLE_API_TOKEN=xxx   # رمز WiGLE API (اختياري)
```

### الوصول إلى محول WiFi

للسماح للحاوية بالوصول إلى محول WiFi:

```bash
# تحديد جهاز USB
docker run --rm -it \
  --privileged \
  --device /dev/bus/usb \
  -v /dev:/dev \
  wifinexus-guardian:latest
```

### وضع المراقبة

لتفعيل وضع المراقبة على محول WiFi:

```bash
# خارج الحاوية
sudo iw dev wlan0 set monitor control

# ثم تشغيل الحاوية
docker run --rm -it --network host wifinexus-guardian:latest
```

## أمثلة على الاستخدام

### مسح سريع للشبكات

```bash
docker run --rm --network host wifinexus-guardian:latest scan -i wlan0
```

### التقاط Handshake

```bash
docker run --rm \
  --privileged \
  --network host \
  -v $(pwd)/captures:/app/captures \
  wifinexus-guardian:latest capture -i wlan0 -t AA:BB:CC:DD:EE:FF
```

### هجوم PMKID

```bash
docker run --rm \
  --privileged \
  --network host \
  -v $(pwd)/captures:/app/captures \
  wifinexus-guardian:latest pmkid -i wlan0 -t AA:BB:CC:DD:EE:FF
```

### استخدام ملف تعريف

```bash
docker run --rm \
  --network host \
  -v $(pwd)/profiles:/app/profiles \
  wifinexus-guardian:latest --profile stealth_mode
```

## إدارة البيانات

### حفظ النتائج

جميع الملفات المحفوظة في المجلدات التالية يتم الاحتفاظ بها على المضيف:

- `./captures/` - ملفات الالتقاط (PCAP, PMKID)
- `./logs/` - سجلات النظام
- `./reports/` - التقارير المصدرة
- `./database/` - قاعدة بيانات SQLite

### نسخ احتياطي

```bash
# إنشاء نسخة احتياطية
tar -czf wifinexus-backup.tar.gz captures/ logs/ reports/ database/

# استعادة النسخة
tar -xzf wifinexus-backup.tar.gz
```

## الأمان

### أفضل الممارسات

1. **لا تشغل كـ root إلا عند الضرورة**
   ```yaml
   security_opt:
     - no-new-privileges:true
   ```

2. **حدد الموارد**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 2G
   ```

3. **استخدم شبكات معزولة**
   ```bash
   docker network create wifinexus-net
   ```

### تحذيرات هامة

⚠️ **تحذير**: تشغيل أدوات الاختراق قد يكون غير قانوني في بلدك. استخدم فقط على الشبكات التي تملكها أو لديك إذن خطي لاختبارها.

## استكشاف الأخطاء

### المشكلة: لا يمكن الوصول إلى محول WiFi

```bash
# تحقق من الأجهزة المتاحة
docker run --rm --privileged lsusb

# تحقق من صلاحيات الجهاز
ls -l /dev/bus/usb
```

### المشكلة: فشل وضع المراقبة

```bash
# تحقق من دعم المحول
iw list | grep "Supported interface modes"

# جرب محول آخر أو تحديث التعريفات
```

### المشكلة: نفاد المساحة

```bash
# تنظيف الملفات القديمة
docker system prune -a

# زيادة حجم التخزين
docker run --storage-opt size=10g ...
```

## التكامل مع CI/CD

### GitHub Actions

```yaml
- name: Run WiFiNexus Tests
  run: |
    docker build -t wifinexus-test .
    docker run --rm wifinexus-test pytest tests/
```

### Jenkins

```groovy
stage('Security Scan') {
    steps {
        sh 'docker run --rm wifinexus-guardian scan -i wlan0'
    }
}
```

## التحديث

```bash
# إعادة بناء الصورة
docker-compose build --no-cache

# سحب التحديثات
docker pull wifinexus-guardian:latest
```

## الدعم

للحصول على المساعدة:
- افتح issue على GitHub
- راجع الوثائق في `/docs`
- انضم إلى قناة Discord

---

**WiFiNexus Guardian v2.0.0** - أداة احترافية لتقييم أمان الشبكات اللاسلكية
