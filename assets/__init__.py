"""
WiFiNexus Guardian - Assets Module
Contains icons, images, and UI resources
"""

import os
from pathlib import Path

ASSETS_DIR = Path(__file__).parent

# Icon paths
ICON_PATHS = {
    'app_icon': ASSETS_DIR / 'icon.png',
    'wifi_icon': ASSETS_DIR / 'wifi.svg',
    'security_icon': ASSETS_DIR / 'security.svg',
    'scan_icon': ASSETS_DIR / 'scan.svg',
    'attack_icon': ASSETS_DIR / 'attack.svg',
    'defense_icon': ASSETS_DIR / 'defense.svg',
    'ai_icon': ASSETS_DIR / 'ai.svg',
    'report_icon': ASSETS_DIR / 'report.svg',
    'settings_icon': ASSETS_DIR / 'settings.svg',
    'warning_icon': ASSETS_DIR / 'warning.svg',
    'success_icon': ASSETS_DIR / 'success.svg',
    'error_icon': ASSETS_DIR / 'error.svg'
}

# Theme resources
THEME_PATHS = {
    'cyber_neon': ASSETS_DIR / 'themes' / 'cyber_neon.qss',
    'dark': ASSETS_DIR / 'themes' / 'dark.qss',
    'light': ASSETS_DIR / 'themes' / 'light.qss'
}

def get_asset_path(name: str) -> Path:
    """Get path to asset by name"""
    return ICON_PATHS.get(name, ASSETS_DIR / name)

def get_theme_path(theme_name: str) -> Path:
    """Get path to theme stylesheet"""
    return THEME_PATHS.get(theme_name, THEME_PATHS['dark'])

def list_assets() -> dict:
    """List all available assets"""
    return {
        'icons': ICON_PATHS,
        'themes': THEME_PATHS
    }
