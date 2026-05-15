#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - نظام التنبيهات الفورية
نظام متقدم لإرسال التنبيهات والإشعارات
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import List, Dict, Optional, Callable
from pathlib import Path


class NotificationManager:
    """مدير الإشعارات المكتبية"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.notification_history: List[Dict] = []
        
    def send_desktop_notification(self, title: str, message: str, urgency: str = "normal") -> bool:
        """إرسال إشعار مكتبي"""
        if not self.enabled:
            return False
        
        try:
            # محاولة استخدام notify-send على Linux
            import subprocess
            
            urgency_map = {
                "low": "low",
                "normal": "normal",
                "critical": "critical"
            }
            
            subprocess.run([
                "notify-send",
                "-u", urgency_map.get(urgency, "normal"),
                "-t", "5000",
                title,
                message
            ], check=False, capture_output=True)
            
            return True
        except Exception:
            # fallback: طباعة التنبيه
            print(f"🔔 [{title}] {message}")
            return True
    
    def log_notification(self, title: str, message: str, alert_type: str) -> None:
        """تسجيل الإشعار في السجل"""
        self.notification_history.append({
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "message": message,
            "type": alert_type
        })


class AlertRule:
    """قاعدة تنبيه مخصصة"""
    
    def __init__(self, name: str, condition: Callable, action: Callable, enabled: bool = True):
        self.name = name
        self.condition = condition
        self.action = action
        self.enabled = enabled
        self.triggered_count = 0
        self.last_triggered: Optional[datetime] = None
    
    def check(self, data: Dict) -> bool:
        """التحقق من شرط التنبيه"""
        if not self.enabled:
            return False
        
        try:
            if self.condition(data):
                self.triggered_count += 1
                self.last_triggered = datetime.now()
                self.action(data)
                return True
        except Exception:
            pass
        
        return False


class AdvancedAlertSystem:
    """نظام التنبيهات المتقدم"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "alert_config.json"
        self.alerts_enabled = True
        self.rules: List[AlertRule] = []
        self.notification_manager = NotificationManager()
        self.alert_history: List[Dict] = []
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # تحميل التكوين إذا وجد
        self.load_config()
        
        # إضافة قواعد افتراضية
        self._add_default_rules()
    
    def _add_default_rules(self) -> None:
        """إضافة قواعد التنبيه الافتراضية"""
        
        # قاعدة: اكتشاف شبكة مستهدفة
        def target_condition(data: Dict) -> bool:
            return data.get('is_target', False)
        
        def target_action(data: Dict) -> None:
            self.notify_target_detected(
                data.get('ssid', 'Unknown'),
                data.get('reason', 'تم التحديد كهدف')
            )
        
        self.add_rule(AlertRule("Target Detection", target_condition, target_action))
        
        # قاعدة: التقاط Handshake
        def handshake_condition(data: Dict) -> bool:
            return data.get('handshake_captured', False)
        
        def handshake_action(data: Dict) -> None:
            self.notify_handshake_captured(
                data.get('ssid', 'Unknown'),
                data.get('bssid', 'N/A')
            )
        
        self.add_rule(AlertRule("Handshake Captured", handshake_condition, handshake_action))
        
        # قاعدة: إشارة قوية جداً
        def strong_signal_condition(data: Dict) -> bool:
            signal = data.get('signal', -100)
            return signal >= -50
        
        def strong_signal_action(data: Dict) -> None:
            self.send_alert(
                f"إشارة قوية جداً: {data.get('ssid')} ({data.get('signal')}dBm)",
                "info"
            )
        
        self.add_rule(AlertRule("Strong Signal", strong_signal_condition, strong_signal_action))
        
        # قاعدة: عملاء متعددين
        def many_clients_condition(data: Dict) -> bool:
            return data.get('clients', 0) >= 10
        
        def many_clients_action(data: Dict) -> None:
            self.send_alert(
                f"شبكة بها {data.get('clients')} عميل: {data.get('ssid')}",
                "warning"
            )
        
        self.add_rule(AlertRule("Many Clients", many_clients_condition, many_clients_action))
    
    def add_rule(self, rule: AlertRule) -> None:
        """إضافة قاعدة تنبيه جديدة"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """إزالة قاعدة تنبيه"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                return True
        return False
    
    def enable_rule(self, rule_name: str) -> bool:
        """تفعيل قاعدة تنبيه"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = True
                return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """تعطيل قاعدة تنبيه"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = False
                return True
        return False
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """تسجيل دالة استدعاء لحدث معين"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def trigger_callbacks(self, event_type: str, data: Dict) -> None:
        """تشغيل دوال الاستدعاء لحدث معين"""
        callbacks = self.callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"❌ خطأ في callback {event_type}: {e}")
    
    def process_event(self, event_data: Dict) -> None:
        """معالجة حدث وفحص قواعد التنبيه"""
        if not self.alerts_enabled:
            return
        
        # فحص جميع القواعد
        for rule in self.rules:
            rule.check(event_data)
        
        # تشغيل دوال الاستدعاء
        event_type = event_data.get('event_type', 'general')
        self.trigger_callbacks(event_type, event_data)
    
    def send_alert(self, message: str, alert_type: str = "info", 
                   title: Optional[str] = None, urgency: str = "normal") -> None:
        """إرسال تنبيه عام"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if title is None:
            title_map = {
                "info": "معلومات",
                "success": "نجاح",
                "warning": "تحذير",
                "error": "خطأ",
                "critical": "حرج"
            }
            title = title_map.get(alert_type, "تنبيه")
        
        # تسجيل التنبيه
        alert_record = {
            "timestamp": timestamp,
            "title": title,
            "message": message,
            "type": alert_type,
            "urgency": urgency
        }
        self.alert_history.append(alert_record)
        
        # إرسال إشعار مكتبي
        self.notification_manager.send_desktop_notification(title, message, urgency)
        
        # تسجيل في السجل
        self.notification_manager.log_notification(title, message, alert_type)
        
        # طباعة التنبيه
        self._print_alert(alert_record)
    
    def _print_alert(self, alert: Dict) -> None:
        """طباعة التنبيه بتنسيق ملون"""
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        colors = {
            "info": "\033[94m",      # أزرق
            "success": "\033[92m",   # أخضر
            "warning": "\033[93m",   # أصفر
            "error": "\033[91m",     # أحمر
            "critical": "\033[95m"   # بنفسجي
        }
        
        reset = "\033[0m"
        icon = icons.get(alert['type'], "📢")
        color = colors.get(alert['type'], "")
        
        print(f"{color}{icon} [{alert['title']}] {alert['message']} {reset}")
        print(f"   └─ {alert['timestamp']}")
    
    def notify_handshake_captured(self, ssid: str, bssid: str) -> None:
        """تنبيه عند التقاط Handshake"""
        self.send_alert(
            f"تم التقاط Handshake للشبكة {ssid} ({bssid})",
            "success",
            "تم التقاط Handshake!",
            "normal"
        )
        self.trigger_callbacks("handshake_captured", {"ssid": ssid, "bssid": bssid})
    
    def notify_target_detected(self, ssid: str, reason: str) -> None:
        """تنبيه عند اكتشاف شبكة مستهدفة"""
        self.send_alert(
            f"اكتشاف الهدف: {ssid} - {reason}",
            "warning",
            "تم اكتشاف هدف",
            "normal"
        )
        self.trigger_callbacks("target_detected", {"ssid": ssid, "reason": reason})
    
    def notify_attack_complete(self, attack_type: str, success: bool, 
                               target_ssid: Optional[str] = None) -> None:
        """تنبيه عند اكتمال الهجوم"""
        alert_type = "success" if success else "error"
        title = "هجوم ناجح" if success else "فشل الهجوم"
        
        message = f"اكتمل هجوم {attack_type}"
        if target_ssid:
            message += f" على {target_ssid}"
        message += f" - {'✓ ناجح' if success else '✗ فشل'}"
        
        self.send_alert(message, alert_type, title, "critical" if not success else "normal")
        self.trigger_callbacks("attack_complete", {
            "attack_type": attack_type,
            "success": success,
            "target": target_ssid
        })
    
    def notify_scan_complete(self, networks_found: int, duration: float) -> None:
        """تنبيه عند اكتمال المسح"""
        message = f"اكتمل المسح: عُثر على {networks_found} شبكة في {duration:.1f} ثانية"
        self.send_alert(message, "info", "اكتمل المسح", "low")
        self.trigger_callbacks("scan_complete", {
            "networks_found": networks_found,
            "duration": duration
        })
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """الحصول على سجل التنبيهات"""
        return self.alert_history[-limit:]
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات التنبيهات"""
        stats = {
            "total_alerts": len(self.alert_history),
            "by_type": {},
            "rules": {
                "total": len(self.rules),
                "enabled": sum(1 for r in self.rules if r.enabled),
                "details": []
            }
        }
        
        # الإحصائيات حسب النوع
        for alert in self.alert_history:
            alert_type = alert['type']
            stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
        
        # تفاصيل القواعد
        for rule in self.rules:
            stats["rules"]["details"].append({
                "name": rule.name,
                "enabled": rule.enabled,
                "triggered_count": rule.triggered_count,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None
            })
        
        return stats
    
    def save_config(self) -> None:
        """حفظ التكوين"""
        config = {
            "alerts_enabled": self.alerts_enabled,
            "rules": [
                {
                    "name": rule.name,
                    "enabled": rule.enabled
                }
                for rule in self.rules
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def load_config(self) -> None:
        """تحميل التكوين"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.alerts_enabled = config.get('alerts_enabled', True)
            
            # تحديث حالة القواعد
            saved_rules = config.get('rules', [])
            for saved_rule in saved_rules:
                for rule in self.rules:
                    if rule.name == saved_rule['name']:
                        rule.enabled = saved_rule.get('enabled', True)
        except Exception as e:
            print(f"⚠️  خطأ في تحميل التكوين: {e}")
    
    def export_history(self, filename: Optional[str] = None) -> str:
        """تصدير سجل التنبيهات إلى ملف"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alert_history_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.alert_history, f, indent=2, ensure_ascii=False)
        
        return filename


def main():
    """اختبار نظام التنبيهات"""
    print("=" * 60)
    print("🔔 اختبار نظام التنبيهات المتقدم")
    print("=" * 60)
    
    # إنشاء النظام
    alerts = AdvancedAlertSystem()
    
    # اختبار التنبيهات المباشرة
    print("\n📝 اختبار التنبيهات المباشرة:\n")
    alerts.send_alert("بدء النظام...", "info")
    alerts.send_alert("تم تحميل الوحدات بنجاح", "success")
    alerts.send_alert("تحذير: شبكة غير آمنة مكتشفة", "warning")
    
    # محاكاة أحداث
    print("\n🎯 محاكاة الأحداث:\n")
    
    events = [
        {"event_type": "network_detected", "ssid": "HomeWiFi", "is_target": True, "reason": "WEP"},
        {"event_type": "network_detected", "ssid": "OfficeNet", "handshake_captured": True, "bssid": "AA:BB:CC:DD:EE:FF"},
        {"event_type": "network_detected", "ssid": "Cafe_WiFi", "signal": -45, "clients": 15},
    ]
    
    for event in events:
        print(f"\nمعالجة حدث: {event.get('ssid', 'N/A')}")
        alerts.process_event(event)
        time.sleep(0.5)
    
    # عرض الإحصائيات
    print("\n📊 إحصائيات التنبيهات:")
    stats = alerts.get_statistics()
    print(f"  إجمالي التنبيهات: {stats['total_alerts']}")
    print(f"  القواعد المفعلة: {stats['rules']['enabled']}/{stats['rules']['total']}")
    
    # تصدير السجل
    history_file = alerts.export_history()
    print(f"\n💾 تم تصدير سجل التنبيهات إلى: {history_file}")
    
    print("\n✅ اكتمل الاختبار بنجاح!")


if __name__ == "__main__":
    main()
