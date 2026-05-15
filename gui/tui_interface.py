#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Terminal User Interface (TUI)
واجهة نصية تفاعلية للتحكم الفوري في الأداة
"""

import sys
import os
import time
import threading
from datetime import datetime
from typing import List, Dict, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.align import Align
    from rich.style import Style
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not installed. Install with: pip install rich")


class NetworkScannerTUI:
    """واجهة TUI لمسح الشبكات وعرضها بشكل تفاعلي"""
    
    def __init__(self):
        if not RICH_AVAILABLE:
            raise ImportError("Rich library is required for TUI")
        
        self.console = Console()
        self.running = False
        self.networks: List[Dict] = []
        self.selected_network: Optional[Dict] = None
        self.status_message = "جاهز"
        self.scan_progress = 0
        
    def create_network_table(self) -> Table:
        """إنشاء جدول عرض الشبكات"""
        table = Table(
            title="📡 الشبكات المكتشفة",
            border_style="blue",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("#", style="cyan", width=4)
        table.add_column("BSSID", style="yellow", width=18)
        table.add_column("SSID", style="green", width=25)
        table.add_column("القناة", style="cyan", width=6)
        table.add_column("الإشارة", style="red", width=8)
        table.add_column("التشفير", style="magenta", width=12)
        table.add_column("العملاء", style="blue", width=8)
        table.add_column("✅", style="green", width=4)
        
        for idx, network in enumerate(self.networks[:20], 1):
            has_handshake = "✓" if network.get('handshake', False) else ""
            signal_bars = "▂▄▆█"[:max(1, min(4, (network.get('signal', -100) + 100) // 25))]
            
            table.add_row(
                str(idx),
                network.get('bssid', 'N/A'),
                network.get('ssid', 'Hidden')[:24],
                str(network.get('channel', 0)),
                f"{signal_bars} {network.get('signal', 0)}dBm",
                network.get('encryption', 'Unknown'),
                str(network.get('clients', 0)),
                has_handshake
            )
        
        return table
    
    def create_status_panel(self) -> Panel:
        """إنشاء لوحة الحالة"""
        status_text = Text()
        status_text.append("الحالة: ", style="bold cyan")
        status_text.append(f"{self.status_message}\n", style="green")
        status_text.append("الشبكات: ", style="bold cyan")
        status_text.append(f"{len(self.networks)}\n", style="yellow")
        status_text.append("التقدم: ", style="bold cyan")
        status_text.append(f"{self.scan_progress}%\n", style="magenta")
        status_text.append("الوقت: ", style="bold cyan")
        status_text.append(datetime.now().strftime("%H:%M:%S"), style="white")
        
        return Panel(status_text, title="📊 حالة النظام", border_style="blue")
    
    def create_help_panel(self) -> Panel:
        """إنشاء لوحة المساعدة"""
        help_text = """[bold cyan]الأوامر:[/bold cyan]
  [green]1-9[/green]     تحديد شبكة
  [green]a[/green]       هجوم PMKID
  [green]d[/green]       هجوم Deauth
  [green]c[/green]       التقاط Handshake
  [green]s[/green]       مسح جديد
  [green]q[/green]       خروج
  
[bold yellow]اختر أمراً للمتابعة...[/bold yellow]"""
        
        return Panel(help_text, title="❓ مساعدة", border_style="yellow")
    
    def create_layout(self) -> Layout:
        """إنشاء التخطيط العام"""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=12)
        )
        
        layout["body"].split_row(
            Layout(name="main", ratio=2),
            Layout(name="side", ratio=1)
        )
        
        layout["main"].update(self.create_network_table())
        layout["side"].split(
            Layout(name="status"),
            Layout(name="help")
        )
        layout["side"]["status"].update(self.create_status_panel())
        layout["side"]["help"].update(self.create_help_panel())
        
        # Header
        header_text = Text()
        header_text.append(" WiFiNexus Guardian ", style="bold white on blue")
        header_text.append(" v1.0.0 ", style="black on yellow")
        header_text.append(" - واجهة TUI التفاعلية", style="white")
        layout["header"].update(Panel(header_text, style="bold"))
        
        return layout
    
    def update_display(self, layout: Layout) -> None:
        """تحديث العرض"""
        layout["main"].update(self.create_network_table())
        layout["side"]["status"].update(self.create_status_panel())
    
    def simulate_scan(self) -> None:
        """محاكاة مسح الشبكات (للعرض فقط)"""
        import random
        
        sample_networks = [
            {"bssid": "AA:BB:CC:DD:EE:01", "ssid": "HomeWiFi", "channel": 6, "signal": -45, "encryption": "WPA2", "clients": 3},
            {"bssid": "AA:BB:CC:DD:EE:02", "ssid": "Office_Network", "channel": 11, "signal": -62, "encryption": "WPA3", "clients": 12},
            {"bssid": "AA:BB:CC:DD:EE:03", "ssid": "Guest_WiFi", "channel": 1, "signal": -78, "encryption": "WPA2", "clients": 5},
            {"bssid": "AA:BB:CC:DD:EE:04", "ssid": "IoT_Devices", "channel": 6, "signal": -55, "encryption": "WPA2", "clients": 8},
            {"bssid": "AA:BB:CC:DD:EE:05", "ssid": "Hidden Net", "channel": 36, "signal": -70, "encryption": "WPA3", "clients": 2},
        ]
        
        for i, net in enumerate(sample_networks):
            if not self.running:
                break
            self.networks.append(net)
            self.scan_progress = min(100, (i + 1) * 20)
            self.status_message = f"جاري المسح... القناة {net['channel']}"
            time.sleep(0.5)
        
        self.status_message = "اكتمل المسح"
    
    def run(self) -> None:
        """تشغيل الواجهة التفاعلية"""
        self.console.print("[bold green]🚀 بدء واجهة TUI التفاعلية...[/bold green]\n")
        
        self.running = True
        
        # بدء خيط المسح المحاكي
        scan_thread = threading.Thread(target=self.simulate_scan, daemon=True)
        scan_thread.start()
        
        layout = self.create_layout()
        
        try:
            with Live(layout, console=self.console, refresh_per_second=4, screen=True) as live:
                while self.running:
                    self.update_display(layout)
                    time.sleep(0.25)
                    
                    # التحقق من إدخال المستخدم (في النسخة الحقيقية)
                    if len(self.networks) >= 5 and self.scan_progress == 100:
                        time.sleep(2)
                        self.running = False
                        
        except KeyboardInterrupt:
            self.running = False
        
        self.console.print("\n[bold yellow]👋 الخروج من واجهة TUI...[/bold yellow]")


class AlertSystem:
    """نظام التنبيهات الفورية"""
    
    def __init__(self):
        self.console = Console()
        self.alerts_enabled = True
        self.alert_history: List[Dict] = []
        
    def send_alert(self, message: str, alert_type: str = "info") -> None:
        """إرسال تنبيه فوري"""
        if not self.alerts_enabled:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        alert_colors = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "critical": "bold red on white"
        }
        
        alert_icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }
        
        color = alert_colors.get(alert_type, "white")
        icon = alert_icons.get(alert_type, "📢")
        
        alert_text = Text()
        alert_text.append(f"{icon} ", style=color)
        alert_text.append(f"[{alert_type.upper()}] ", style=f"bold {color}")
        alert_text.append(f"{message}", style="white")
        alert_text.append(f" ({timestamp})", style="dim")
        
        self.console.print(Panel(alert_text, border_style=color))
        
        # حفظ في السجل
        self.alert_history.append({
            "timestamp": timestamp,
            "type": alert_type,
            "message": message
        })
    
    def notify_handshake_captured(self, ssid: str, bssid: str) -> None:
        """تنبيه عند التقاط Handshake"""
        self.send_alert(
            f"تم التقاط Handshake للشبكة {ssid} ({bssid})",
            "success"
        )
    
    def notify_target_detected(self, ssid: str, reason: str) -> None:
        """تنبيه عند اكتشاف شبكة مستهدفة"""
        self.send_alert(
            f"اكتشاف الهدف: {ssid} - {reason}",
            "warning"
        )
    
    def notify_attack_complete(self, attack_type: str, success: bool) -> None:
        """تنبيه عند اكتمال الهجوم"""
        alert_type = "success" if success else "error"
        message = f"اكتمل هجوم {attack_type} - {'ناجح' if success else 'فشل'}"
        self.send_alert(message, alert_type)
    
    def get_alert_history(self) -> List[Dict]:
        """الحصول على سجل التنبيهات"""
        return self.alert_history


def main():
    """الدالة الرئيسية لواجهة TUI"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]WiFiNexus Guardian v1.0.0[/bold blue]\n"
        "[cyan]واجهة TUI التفاعلية[/cyan]",
        border_style="blue"
    ))
    
    # اختبار نظام التنبيهات
    alerts = AlertSystem()
    alerts.send_alert("بدء النظام...", "info")
    alerts.send_alert("تم تحميل الوحدات بنجاح", "success")
    
    # تشغيل واجهة TUI
    try:
        tu = NetworkScannerTUI()
        tu.run()
    except ImportError as e:
        console.print(f"[bold red]خطأ: {e}[/bold red]")
        console.print("[yellow]قم بتثبيت Rich: pip install rich[/yellow]")
        return 1
    except Exception as e:
        console.print(f"[bold red]خطأ غير متوقع: {e}[/bold red]")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
