"""
WiFiNexus Guardian - Central Configuration File
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

Centralized configuration for all modules and components.
"""

import os
from pathlib import Path
from datetime import datetime

# =============================================================================
# VERSION INFORMATION
# =============================================================================
VERSION = {
    'major': 1,
    'minor': 0,
    'patch': 0,
    'status': 'stable',
    'codename': 'Professional Security Edition',
    'string': '1.0.0',
    'build_date': '2025-05-15',
    'build_number': 100
}

# =============================================================================
# APPLICATION INFORMATION
# =============================================================================
APP_NAME = "WiFiNexus Guardian"
APP_ORGANIZATION = "Finovate - AHMED EG"
APP_AUTHOR = "Ahmed Mostafa Ibrahim"
APP_EMAIL = "gogom8870@gmail.com"
APP_PHONE = "01225155329"
APP_COPYRIGHT = "© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved"
APP_LICENSE = "Community Edition (Personal/Educational Use)"

# =============================================================================
# PATHS AND DIRECTORIES
# =============================================================================
BASE_DIR = Path(__file__).parent.absolute()

DIRECTORIES = {
    'captures': BASE_DIR / 'captures',
    'logs': BASE_DIR / 'logs',
    'reports': BASE_DIR / 'reports',
    'reports_output': BASE_DIR / 'reports_output',
    'wordlists': BASE_DIR / 'wordlists',
    'database': BASE_DIR / 'database',
    'themes': BASE_DIR / 'themes',
    'plugins': BASE_DIR / 'plugins',
    'updates': BASE_DIR / 'updates',
    'assets': BASE_DIR / 'assets',
    'simulation': BASE_DIR / 'simulation'
}

# Ensure directories exist
for dir_path in DIRECTORIES.values():
    dir_path.mkdir(exist_ok=True)

# Database path
DATABASE_PATH = DIRECTORIES['database'] / 'wifinexus.db'

# =============================================================================
# PLATFORM DETECTION
# =============================================================================
import platform
CURRENT_PLATFORM = platform.system()
CURRENT_PLATFORM_VERSION = platform.version()
CURRENT_MACHINE = platform.machine()

PLATFORMS = {
    'LINUX': 'Linux',
    'WINDOWS': 'Windows',
    'MACOS': 'Darwin'
}

IS_LINUX = CURRENT_PLATFORM == PLATFORMS['LINUX']
IS_WINDOWS = CURRENT_PLATFORM == PLATFORMS['WINDOWS']
IS_MACOS = CURRENT_PLATFORM == PLATFORMS['MACOS']

# =============================================================================
# SECURITY SETTINGS
# =============================================================================
SECURITY = {
    'safety_mode_default': True,
    'legal_warning_required': True,
    'audit_logging_enabled': True,
    'stealth_mode_available': True,
    'encryption_enabled': False,
    'max_login_attempts': 3,
    'session_timeout_minutes': 30
}

# Legal warning text
LEGAL_WARNING = """
⚠️  LEGAL WARNING - IMPORTANT ⚠️

This software is designed for authorized security testing and educational purposes ONLY.

✅ ALLOWED USES:
- Testing networks you own
- Testing networks with explicit written permission
- Educational and research purposes
- Monitoring your personal network

❌ PROHIBITED USES:
- Unauthorized network access
- Credential theft
- Illegal packet interception
- Network attacks without permission
- Any malicious or illegal activity

By using this software, you acknowledge that:
1. You are responsible for compliance with all applicable laws
2. Unauthorized access to computer systems is illegal
3. The developers are not liable for misuse of this software

Continue only if you understand and accept these terms.
"""

# =============================================================================
# NETWORK SETTINGS
# =============================================================================
NETWORK = {
    'default_interface': None,  # Auto-detect
    'monitor_mode_timeout': 30,
    'handshake_capture_timeout': 120,
    'deauth_packets_count': 10,
    'scan_interval_seconds': 5,
    'max_retries': 3,
    'retry_delay_seconds': 2
}

# WiFi bands
WIFI_BANDS = {
    '2.4GHZ': {'channels': list(range(1, 14)), 'frequency': 2412},
    '5GHZ': {'channels': [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 149, 153, 157, 161, 165], 'frequency': 5180},
    '6GHZ': {'channels': [1, 5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 65, 69, 73, 77, 81, 85, 89, 93, 97, 101, 105, 109, 113, 117, 121, 125, 129, 133, 137, 141, 145, 149, 153, 157, 161, 165, 169, 173, 177, 181, 185, 189, 193, 197, 201, 205, 209, 213, 217, 221, 225, 229, 233], 'frequency': 5955}
}

# =============================================================================
# AI ENGINE SETTINGS
# =============================================================================
AI = {
    'default_provider': 'local',
    'supported_providers': ['local', 'ollama', 'openai', 'gemini', 'claude', 'deepseek'],
    'models': {
        'ollama': 'llama2',
        'openai': 'gpt-3.5-turbo',
        'gemini': 'gemini-pro',
        'claude': 'claude-3-haiku',
        'deepseek': 'deepseek-chat'
    },
    'api_keys': {
        'openai': os.getenv('OPENAI_API_KEY', ''),
        'gemini': os.getenv('GEMINI_API_KEY', ''),
        'claude': os.getenv('CLAUDE_API_KEY', ''),
        'deepseek': os.getenv('DEEPSEEK_API_KEY', '')
    },
    'timeout_seconds': 30,
    'max_tokens': 1024,
    'temperature': 0.7
}

# =============================================================================
# LOGGING SETTINGS
# =============================================================================
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'file': DIRECTORIES['logs'] / 'wifinexus.log',
    'max_size_mb': 10,
    'backup_count': 5,
    'console_output': True
}

# =============================================================================
# DATABASE SETTINGS
# =============================================================================
DATABASE = {
    'type': 'sqlite',
    'path': DATABASE_PATH,
    'auto_create_tables': True,
    'connection_timeout': 30,
    'pool_size': 5
}

# Tables schema
DATABASE_TABLES = [
    'wifi_scans',
    'speed_tests',
    'handshake_captures',
    'devices',
    'events',
    'settings',
    'security_alerts',
    'forensic_reports'
]

# =============================================================================
# EXTERNAL TOOLS
# =============================================================================
EXTERNAL_TOOLS = {
    'Linux': {
        'required': ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'aircrack-ng'],
        'recommended': ['tshark', 'tcpdump', 'hashcat', 'hcxdumptool', 'hcxcapngtool'],
        'optional': ['wireshark', 'kismet', 'reaver', 'bully']
    },
    'Windows': {
        'required': ['netsh', 'npcap'],
        'recommended': ['tshark', 'Wireshark', 'hashcat'],
        'optional': ['acrylic wifi', 'inSSIDer']
    },
    'macOS': {
        'required': ['airport'],
        'recommended': ['tshark', 'tcpdump', 'hashcat'],
        'optional': ['KisMAC', 'WiFi Explorer']
    }
}

# Package managers per platform
PACKAGE_MANAGERS = {
    'Linux': ['apt', 'yum', 'dnf', 'pacman', 'zypper'],
    'Windows': ['chocolatey', 'winget', 'manual'],
    'macOS': ['brew', 'manual']
}

# =============================================================================
# GUI SETTINGS
# =============================================================================
GUI = {
    'theme': 'cyber_neon',
    'language': 'en',  # 'en' or 'ar'
    'rtl_support': True,
    'min_width': 1200,
    'min_height': 800,
    'default_font': 'Segoe UI',
    'font_size': 10,
    'enable_animations': True,
    'refresh_rate_ms': 1000
}

# Theme colors
THEMES = {
    'cyber_neon': {
        'primary': '#00D9FF',
        'secondary': '#00FF88',
        'accent': '#FF00FF',
        'background': '#0A0A0A',
        'surface': '#1A1A1A',
        'text': '#FFFFFF',
        'warning': '#FFAA00',
        'danger': '#FF4444',
        'success': '#00FF88'
    },
    'dark': {
        'primary': '#2196F3',
        'secondary': '#03DAC6',
        'accent': '#BB86FC',
        'background': '#121212',
        'surface': '#1E1E1E',
        'text': '#FFFFFF',
        'warning': '#FFC107',
        'danger': '#CF6679',
        'success': '#4CAF50'
    },
    'light': {
        'primary': '#1976D2',
        'secondary': '#424242',
        'accent': '#F57C00',
        'background': '#FAFAFA',
        'surface': '#FFFFFF',
        'text': '#212121',
        'warning': '#FFA000',
        'danger': '#D32F2F',
        'success': '#388E3C'
    }
}

# =============================================================================
# AUTOMATION SETTINGS
# =============================================================================
AUTOMATION = {
    'enabled': True,
    'max_concurrent_tasks': 3,
    'task_timeout_minutes': 60,
    'retry_failed_tasks': True,
    'max_retries': 2,
    'notification_enabled': True,
    'log_all_actions': True
}

# Predefined automation scenarios
AUTOMATION_SCENARIOS = [
    'full_security_audit',
    'quick_network_scan',
    'handshake_capture_only',
    'evil_twin_phishing',
    'continuous_monitoring'
]

# =============================================================================
# FORENSIC SETTINGS
# =============================================================================
FORENSIC = {
    'preserve_evidence': True,
    'calculate_hashes': True,
    'hash_algorithms': ['md5', 'sha1', 'sha256'],
    'chain_of_custody': True,
    'timestamp_accuracy': 'microsecond',
    'export_formats': ['json', 'csv', 'pdf', 'html']
}

# =============================================================================
# REPORT SETTINGS
# =============================================================================
REPORT = {
    'default_format': 'html',
    'include_timestamp': True,
    'include_statistics': True,
    'include_recommendations': True,
    'auto_generate': False,
    'output_directory': DIRECTORIES['reports_output'],
    'templates_directory': DIRECTORIES['reports'] / 'templates'
}

# =============================================================================
# WORDLIST SETTINGS
# =============================================================================
WORDLIST = {
    'default_path': DIRECTORIES['wordlists'] / 'common_passwords.txt',
    'max_size_mb': 100,
    'encoding': 'utf-8',
    'generate_from_ssid': True,
    'include_dates': True,
    'include_patterns': True,
    'leet_speak_mutations': True
}

# Common password patterns
PASSWORD_PATTERNS = [
    '{ssid}{year}',
    '{ssid}123',
    '{ssid}!',
    'admin{year}',
    'password{year}',
    'welcome123',
    '{phone}123',
    '{name}{year}'
]

# =============================================================================
# PERFORMANCE SETTINGS
# =============================================================================
PERFORMANCE = {
    'max_threads': 4,
    'max_processes': 2,
    'memory_limit_mb': 512,
    'cpu_usage_limit_percent': 80,
    'network_buffer_size': 4096,
    'cache_enabled': True,
    'cache_ttl_seconds': 300
}

# =============================================================================
# UPDATE SETTINGS
# =============================================================================
UPDATE = {
    'check_on_startup': True,
    'auto_download': False,
    'auto_install': False,
    'update_server': 'https://api.github.com/repos/ahmed1998AM/WiFiNexus-Guardian',
    'check_interval_days': 7
}

# =============================================================================
# PLUGIN SETTINGS
# =============================================================================
PLUGIN = {
    'enabled': True,
    'directory': DIRECTORIES['plugins'],
    'auto_load': True,
    'verify_signatures': False,
    'allowed_extensions': ['.py', '.json']
}

# =============================================================================
# SIMULATION SETTINGS
# =============================================================================
SIMULATION = {
    'enabled': True,
    'default_networks_count': 5,
    'signal_fluctuation_range': 5,
    'client_activity_probability': 0.7,
    'handshake_success_rate': 0.8
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_version_string():
    """Return full version string"""
    return f"{VERSION['string']} ({VERSION['codename']})"

def get_app_info():
    """Return application information dictionary"""
    return {
        'name': APP_NAME,
        'version': get_version_string(),
        'author': APP_AUTHOR,
        'organization': APP_ORGANIZATION,
        'email': APP_EMAIL,
        'copyright': APP_COPYRIGHT
    }

def is_production():
    """Check if running in production mode"""
    return VERSION['status'] == 'stable'

def get_platform_tools():
    """Get required tools for current platform"""
    return EXTERNAL_TOOLS.get(CURRENT_PLATFORM, EXTERNAL_TOOLS['Linux'])

def initialize_config():
    """Initialize configuration and create necessary directories"""
    for dir_path in DIRECTORIES.values():
        dir_path.mkdir(exist_ok=True)
    return True

# Initialize on import
initialize_config()
