"""
WiFiNexus Guardian - Updates Module
نظام التحديثات لـ WiFiNexus Guardian
"""

from .updater import AutoUpdater, UpdateChecker, UpdateDownloader, UpdateInstaller

__all__ = ['AutoUpdater', 'UpdateChecker', 'UpdateDownloader', 'UpdateInstaller']

def get_updater():
    """Get initialized auto-updater instance"""
    return AutoUpdater()
