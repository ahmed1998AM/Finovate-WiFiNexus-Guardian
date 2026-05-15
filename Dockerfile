"""
WiFiNexus Guardian - Dockerfile
================================
حاوية Docker للتشغيل المعزول والآمن
"""

FROM python:3.10-slim

# معلومات الصيانة
LABEL maintainer="WiFiNexus Security Team"
LABEL version="2.0.0"
LABEL description="Professional WiFi Security Assessment Tool"

# متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# تثبيت الاعتماديات النظامية
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    net-tools \
    wireless-tools \
    iw \
    pciutils \
    usbutils \
    tcpdump \
    tshark \
    aircrack-ng \
    reaver \
    bully \
    hashcat \
    john \
    sqlite3 \
    libpcap-dev \
    libnl-3-dev \
    libnl-genl-3-dev \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# إنشاء مجلد العمل
WORKDIR /app

# نسخ ملفات الاعتماديات أولاً (لتحسين التخزين المؤقت)
COPY requirements.txt .

# تثبيت حزم Python
RUN pip install --no-cache-dir -r requirements.txt

# نسخ كود المصدر
COPY . .

# إنشاء مجلدات البيانات
RUN mkdir -p /app/captures /app/logs /app/reports /app/database

# تعيين الأذونات
RUN chmod +x wifinexus.py
RUN chmod +x run.sh

# المنفذ الافتراضي (للاستخدام المستقبلي مع الواجهة الرسومية)
EXPOSE 8080

# حجم التخزين للحاوية
VOLUME ["/app/captures", "/app/logs", "/app/reports", "/app/database"]

# المستخدم غير الجذر للأمان (اختياري - يتطلب إعدادات إضافية)
# RUN useradd -m -u 1000 wifinexus && chown -R wifinexus:wifinexus /app
# USER wifinexus

# نقطة الدخول
ENTRYPOINT ["python", "wifinexus.py"]

# الأمر الافتراضي
CMD ["--help"]
