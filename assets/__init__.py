# WiFiNexus Guardian v1.0.0 - Translations
# Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
# © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

"""
Translation Manager for WiFiNexus Guardian
Supports multiple languages with professional translations
"""


class TranslationManager:
    """Manages application translations"""
    
    TRANSLATIONS = {
        'en': {
            'name': 'English',
            'strings': {
                'app_title': 'WiFiNexus Guardian',
                'version': 'Version',
                'scan_networks': 'Scan Networks',
                'security_audit': 'Security Audit',
                'attack_tools': 'Attack Tools',
                'defense_monitor': 'Defense Monitor',
                'reports': 'Reports',
                'settings': 'Settings',
                'start': 'Start',
                'stop': 'Stop',
                'export': 'Export',
                'import': 'Import',
                'save': 'Save',
                'cancel': 'Cancel',
                'ok': 'OK',
                'yes': 'Yes',
                'no': 'No',
                'loading': 'Loading...',
                'processing': 'Processing...',
                'completed': 'Completed',
                'error': 'Error',
                'warning': 'Warning',
                'success': 'Success',
                'network_name': 'Network Name',
                'signal_strength': 'Signal Strength',
                'security_type': 'Security Type',
                'channel': 'Channel',
                'mac_address': 'MAC Address',
                'connected_devices': 'Connected Devices',
                'vulnerable_networks': 'Vulnerable Networks',
                'secure_networks': 'Secure Networks',
                'open_networks': 'Open Networks',
                'total_networks': 'Total Networks',
                'scan_duration': 'Scan Duration',
                'interface': 'Interface',
                'mode': 'Mode',
                'band': 'Band',
                'all_bands': 'All Bands',
                '2_4ghz': '2.4 GHz',
                '5ghz': '5 GHz',
                '6ghz': '6 GHz',
                'managed': 'Managed',
                'monitor': 'Monitor',
                'promiscuous': 'Promiscuous',
                'capture_handshake': 'Capture Handshake',
                'pmkid_attack': 'PMKID Attack',
                'deauth_attack': 'Deauthentication Attack',
                'evil_twin': 'Evil Twin',
                'wps_attack': 'WPS Attack',
                'beacon_flood': 'Beacon Flood',
                'target': 'Target',
                'clients': 'Clients',
                'packets': 'Packets',
                'handshake_captured': 'Handshake Captured!',
                'attack_successful': 'Attack Successful',
                'attack_failed': 'Attack Failed',
                'no_target_selected': 'No target selected',
                'scanning': 'Scanning...',
                'found_networks': 'Found {count} networks',
                'device_info': 'Device Information',
                'system_status': 'System Status',
                'cpu_usage': 'CPU Usage',
                'memory_usage': 'Memory Usage',
                'disk_usage': 'Disk Usage',
                'network_traffic': 'Network Traffic',
                'upload': 'Upload',
                'download': 'Download',
                'theme': 'Theme',
                'language': 'Language',
                'dark_mode': 'Dark Mode',
                'light_mode': 'Light Mode',
                'auto': 'Auto',
                'about': 'About',
                'help': 'Help',
                'documentation': 'Documentation',
                'check_updates': 'Check for Updates',
                'developer': 'Developer',
                'license': 'License',
                'copyright': 'Copyright',
                'all_rights_reserved': 'All Rights Reserved',
            }
        },
        'ar': {
            'name': 'العربية',
            'strings': {
                'app_title': 'واي فاي نكسوس غارديان',
                'version': 'الإصدار',
                'scan_networks': 'مسح الشبكات',
                'security_audit': 'مراجعة أمنية',
                'attack_tools': 'أدوات الهجوم',
                'defense_monitor': 'مراقب الدفاع',
                'reports': 'التقارير',
                'settings': 'الإعدادات',
                'start': 'بدء',
                'stop': 'إيقاف',
                'export': 'تصدير',
                'import': 'استيراد',
                'save': 'حفظ',
                'cancel': 'إلغاء',
                'ok': 'موافق',
                'yes': 'نعم',
                'no': 'لا',
                'loading': 'جاري التحميل...',
                'processing': 'جاري المعالجة...',
                'completed': 'اكتمل',
                'error': 'خطأ',
                'warning': 'تحذير',
                'success': 'نجاح',
                'network_name': 'اسم الشبكة',
                'signal_strength': 'قوة الإشارة',
                'security_type': 'نوع الأمان',
                'channel': 'القناة',
                'mac_address': 'عنوان MAC',
                'connected_devices': 'الأجهزة المتصلة',
                'vulnerable_networks': 'الشبكات الضعيفة',
                'secure_networks': 'الشبكات الآمنة',
                'open_networks': 'الشبكات المفتوحة',
                'total_networks': 'إجمالي الشبكات',
                'scan_duration': 'مدة المسح',
                'interface': 'الواجهة',
                'mode': 'الوضع',
                'band': 'النطاق',
                'all_bands': 'جميع النطاقات',
                '2_4ghz': '2.4 جيجا هرتز',
                '5ghz': '5 جيجا هرتز',
                '6ghz': '6 جيجا هرتز',
                'managed': 'مُدار',
                'monitor': 'مراقب',
                'promiscuous': 'عشوائي',
                'capture_handshake': 'التقاط المصافحة',
                'pmkid_attack': 'هجوم PMKID',
                'deauth_attack': 'هجوم إلغاء الارتباط',
                'evil_twin': 'التوأم الخبيث',
                'wps_attack': 'هجوم WPS',
                'beacon_flood': 'فيضان المنارات',
                'target': 'الهدف',
                'clients': 'العملاء',
                'packets': 'الحزم',
                'handshake_captured': 'تم التقاط المصافحة!',
                'attack_successful': 'نجح الهجوم',
                'attack_failed': 'فشل الهجوم',
                'no_target_selected': 'لم يتم تحديد هدف',
                'scanning': 'جاري المسح...',
                'found_networks': 'تم العثور على {count} شبكة',
                'device_info': 'معلومات الجهاز',
                'system_status': 'حالة النظام',
                'cpu_usage': 'استخدام المعالج',
                'memory_usage': 'استخدام الذاكرة',
                'disk_usage': 'استخدام القرص',
                'network_traffic': 'حركة الشبكة',
                'upload': 'رفع',
                'download': 'تنزيل',
                'theme': 'السمة',
                'language': 'اللغة',
                'dark_mode': 'الوضع الداكن',
                'light_mode': 'الوضع الفاتح',
                'auto': 'تلقائي',
                'about': 'حول',
                'help': 'مساعدة',
                'documentation': 'التوثيق',
                'check_updates': 'التحقق من التحديثات',
                'developer': 'المطور',
                'license': 'الترخيص',
                'copyright': 'حقوق النشر',
                'all_rights_reserved': 'جميع الحقوق محفوظة',
            }
        },
        'fr': {
            'name': 'Français',
            'strings': {
                'app_title': 'WiFiNexus Guardian',
                'version': 'Version',
                'scan_networks': 'Scanner les réseaux',
                'security_audit': 'Audit de sécurité',
                'attack_tools': 'Outils d\'attaque',
                'defense_monitor': 'Moniteur de défense',
                'reports': 'Rapports',
                'settings': 'Paramètres',
                'start': 'Démarrer',
                'stop': 'Arrêter',
                'export': 'Exporter',
                'import': 'Importer',
                'save': 'Enregistrer',
                'cancel': 'Annuler',
                'ok': 'OK',
                'yes': 'Oui',
                'no': 'Non',
                'loading': 'Chargement...',
                'processing': 'Traitement...',
                'completed': 'Terminé',
                'error': 'Erreur',
                'warning': 'Avertissement',
                'success': 'Succès',
                'network_name': 'Nom du réseau',
                'signal_strength': 'Force du signal',
                'security_type': 'Type de sécurité',
                'channel': 'Canal',
                'mac_address': 'Adresse MAC',
                'connected_devices': 'Appareils connectés',
                'vulnerable_networks': 'Réseaux vulnérables',
                'secure_networks': 'Réseaux sécurisés',
                'open_networks': 'Réseaux ouverts',
                'total_networks': 'Total des réseaux',
                'scan_duration': 'Durée du scan',
                'interface': 'Interface',
                'mode': 'Mode',
                'band': 'Bande',
                'all_bands': 'Toutes les bandes',
                '2_4ghz': '2,4 GHz',
                '5ghz': '5 GHz',
                '6ghz': '6 GHz',
                'managed': 'Géré',
                'monitor': 'Moniteur',
                'promiscuous': 'Promiscuité',
                'capture_handshake': 'Capturer la poignée de main',
                'pmkid_attack': 'Attaque PMKID',
                'deauth_attack': 'Attaque de déauthentification',
                'evil_twin': 'Faux jumeau',
                'wps_attack': 'Attaque WPS',
                'beacon_flood': 'Inondation de balises',
                'target': 'Cible',
                'clients': 'Clients',
                'packets': 'Paquets',
                'handshake_captured': 'Poignée de main capturée!',
                'attack_successful': 'Attaque réussie',
                'attack_failed': 'Attaque échouée',
                'no_target_selected': 'Aucune cible sélectionnée',
                'scanning': 'Numérisation...',
                'found_networks': '{count} réseaux trouvés',
                'device_info': 'Informations sur l\'appareil',
                'system_status': 'État du système',
                'cpu_usage': 'Utilisation CPU',
                'memory_usage': 'Utilisation mémoire',
                'disk_usage': 'Utilisation disque',
                'network_traffic': 'Trafic réseau',
                'upload': 'Téléchargement',
                'download': 'Téléchargement',
                'theme': 'Thème',
                'language': 'Langue',
                'dark_mode': 'Mode sombre',
                'light_mode': 'Mode clair',
                'auto': 'Automatique',
                'about': 'À propos',
                'help': 'Aide',
                'documentation': 'Documentation',
                'check_updates': 'Vérifier les mises à jour',
                'developer': 'Développeur',
                'license': 'Licence',
                'copyright': 'Droits d\'auteur',
                'all_rights_reserved': 'Tous droits réservés',
            }
        }
    }
    
    def __init__(self):
        self.current_language = 'en'
    
    def get_available_languages(self):
        """Return list of available languages"""
        return list(self.TRANSLATIONS.keys())
    
    def get_language_name(self, lang_code):
        """Get native name of language"""
        return self.TRANSLATIONS.get(lang_code, {}).get('name', lang_code)
    
    def set_language(self, lang_code):
        """Set current language"""
        if lang_code not in self.TRANSLATIONS:
            raise ValueError(f"Language '{lang_code}' not supported")
        self.current_language = lang_code
    
    def get(self, key, default=None):
        """Get translation for key"""
        lang_data = self.TRANSLATIONS.get(self.current_language, {})
        strings = lang_data.get('strings', {})
        return strings.get(key, default or key)
    
    def _(self, key):
        """Shorthand for get()"""
        return self.get(key)
    
    def format(self, key, **kwargs):
        """Get translation and format with arguments"""
        text = self.get(key)
        try:
            return text.format(**kwargs)
        except (KeyError, AttributeError):
            return text


# Export singleton instance
translator = TranslationManager()

# Shorthand function
def _(key):
    """Global translation function"""
    return translator.get(key)
