"""
WiFiNexus Guardian - Themes Module
مجموعة الثيمات لـ WiFiNexus Guardian
"""

from pathlib import Path

THEMES_DIR = Path(__file__).parent

AVAILABLE_THEMES = {
    'cyber_neon': {
        'name': 'Cyber Neon',
        'description': 'Professional dark theme with neon accents',
        'file': THEMES_DIR / 'cyber_neon.qss',
        'colors': {
            'primary': '#00D9FF',
            'secondary': '#00FF88',
            'accent': '#FF00FF',
            'background': '#0A0A0A',
            'surface': '#1A1A1A'
        }
    },
    'dark': {
        'name': 'Dark Mode',
        'description': 'Classic dark theme',
        'file': THEMES_DIR / 'dark.qss',
        'colors': {
            'primary': '#2196F3',
            'secondary': '#03DAC6',
            'accent': '#BB86FC',
            'background': '#121212',
            'surface': '#1E1E1E'
        }
    },
    'light': {
        'name': 'Light Mode',
        'description': 'Clean light theme',
        'file': THEMES_DIR / 'light.qss',
        'colors': {
            'primary': '#1976D2',
            'secondary': '#424242',
            'accent': '#F57C00',
            'background': '#FAFAFA',
            'surface': '#FFFFFF'
        }
    }
}

def get_theme(theme_name: str) -> dict:
    """Get theme information by name"""
    return AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES['cyber_neon'])

def list_themes() -> list:
    """List all available themes"""
    return [
        {
            'id': key,
            'name': value['name'],
            'description': value['description']
        }
        for key, value in AVAILABLE_THEMES.items()
    ]

def load_stylesheet(theme_name: str) -> str:
    """Load stylesheet content for a theme"""
    theme = get_theme(theme_name)
    stylesheet_path = theme['file']
    
    if stylesheet_path.exists():
        with open(stylesheet_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""
