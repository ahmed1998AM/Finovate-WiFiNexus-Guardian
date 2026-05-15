"""
نظام تنبيهات سطح المكتب
يدعم Linux و macOS و Windows
"""
import os
import sys
import subprocess
from typing import Optional

class NotificationSystem:
    """نظام إرسال تنبيهات سطح المكتب"""
    
    def __init__(self):
        """تهيئة نظام التنبيهات"""
        self.platform = sys.platform
        self.enabled = True
    
    def send(self, title: str, message: str, urgency: str = 'normal') -> bool:
        """
        إرسال تنبيه سطح المكتب
        
        Args:
            title: عنوان التنبيه
            message: نص الرسالة
            urgency: مستوى الأهمية (low, normal, critical)
        
        Returns:
            bool: True إذا تم الإرسال بنجاح
        """
        if not self.enabled:
            return False
        
        try:
            if self.platform == 'linux':
                return self._send_linux(title, message, urgency)
            elif self.platform == 'darwin':
                return self._send_macos(title, message)
            elif self.platform == 'win32':
                return self._send_windows(title, message)
            else:
                return self._send_fallback(title, message)
        except Exception as e:
            print(f"فشل إرسال التنبيه: {e}")
            return False
    
    def _send_linux(self, title: str, message: str, urgency: str) -> bool:
        """إرسال تنبيه على Linux باستخدام notify-send"""
        try:
            cmd = [
                'notify-send',
                '-u', urgency,
                '-t', '5000',  # 5 ثواني
                title,
                message
            ]
            subprocess.run(cmd, check=False, timeout=2)
            return True
        except FileNotFoundError:
            # notify-send غير متوفر، محاولة استخدام بديل
            return self._send_fallback(title, message)
        except Exception:
            return False
    
    def _send_macos(self, title: str, message: str) -> bool:
        """إرسال تنبيه على macOS باستخدام osascript"""
        try:
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(
                ['osascript', '-e', script],
                check=False,
                timeout=2
            )
            return True
        except Exception:
            return False
    
    def _send_windows(self, title: str, message: str) -> bool:
        """إرسال تنبيه على Windows"""
        try:
            # محاولة استخدام plyer إذا كان متوفراً
            try:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=5
                )
                return True
            except ImportError:
                # fallback لـ PowerShell
                script = f'''
                [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
                $balloon = New-Object System.Windows.Forms.NotifyIcon
                $balloon.Icon = [System.Drawing.SystemIcons]::Information
                $balloon.Visible = $true
                $balloon.ShowBalloonTip(5000, "{title}", "{message}", [System.Windows.Forms.ToolTipIcon]::None)
                '''
                subprocess.run(
                    ['powershell', '-Command', script],
                    check=False,
                    timeout=2
                )
                return True
        except Exception:
            return False
    
    def _send_fallback(self, title: str, message: str) -> bool:
        """طريقة احتياطية - طباعة التنبيه في الطرفية"""
        print(f"\n🔔 [{title}] {message}\n")
        return True
    
    def enable(self):
        """تفعيل نظام التنبيهات"""
        self.enabled = True
    
    def disable(self):
        """تعطيل نظام التنبيهات"""
        self.enabled = False
    
    def test_notification(self) -> bool:
        """إرسال تنبيه اختباري"""
        return self.send(
            "WiFiNexus Guardian - اختبار",
            "نظام التنبيهات يعمل بنجاح!",
            urgency="normal"
        )


# مثال للاستخدام
if __name__ == '__main__':
    notifier = NotificationSystem()
    success = notifier.test_notification()
    print(f"تم إرسال التنبيه: {success}")
