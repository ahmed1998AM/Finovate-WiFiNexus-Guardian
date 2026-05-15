# WiFiNexus Guardian v1.0.0 - Theme Manager
# Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
# © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

"""
Theme Manager for WiFiNexus Guardian
Provides centralized theme loading and management
"""

import os
from pathlib import Path


class ThemeManager:
    """Manages application themes and stylesheets"""
    
    THEMES = {
        'cyber_neon': {
            'name': 'Cyber Neon',
            'file': 'cyber_neon.qss',
            'description': 'Professional cyberpunk theme with neon accents',
            'mode': 'dark'
        },
        'dark': {
            'name': 'Dark Professional',
            'file': 'dark.qss',
            'description': 'Material Design dark theme',
            'mode': 'dark'
        },
        'light': {
            'name': 'Light Professional',
            'file': 'light.qss',
            'description': 'Clean light theme for daytime use',
            'mode': 'light'
        }
    }
    
    def __init__(self):
        self.themes_dir = Path(__file__).parent
        self.current_theme = 'cyber_neon'
    
    def get_available_themes(self):
        """Return list of available themes"""
        return list(self.THEMES.keys())
    
    def get_theme_info(self, theme_name):
        """Get detailed information about a theme"""
        return self.THEMES.get(theme_name, {})
    
    def load_stylesheet(self, theme_name=None):
        """Load stylesheet content for specified theme"""
        if theme_name is None:
            theme_name = self.current_theme
        
        if theme_name not in self.THEMES:
            raise ValueError(f"Theme '{theme_name}' not found")
        
        theme_file = self.themes_dir / self.THEMES[theme_name]['file']
        
        if not theme_file.exists():
            raise FileNotFoundError(f"Theme file '{theme_file}' not found")
        
        with open(theme_file, 'r', encoding='utf-8') as f:
            return f.read()
    
    def set_theme(self, theme_name):
        """Set current theme"""
        if theme_name not in self.THEMES:
            raise ValueError(f"Theme '{theme_name}' not found")
        self.current_theme = theme_name
    
    def apply_theme(self, app, theme_name=None):
        """Apply theme to Qt application"""
        if theme_name:
            self.set_theme(theme_name)
        
        stylesheet = self.load_stylesheet()
        app.setStyleSheet(stylesheet)
        return True


# Export singleton instance
theme_manager = ThemeManager()
