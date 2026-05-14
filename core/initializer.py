"""
Core Initializer - Initializes all core components of WiFiNexus Guardian
"""

import os
import sys
import logging
from pathlib import Path

class CoreInitializer:
    """Handles initialization of all core system components"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.initialized_modules = []
        
    def initialize_all(self):
        """Initialize all core components in sequence"""
        print("Initializing WiFiNexus Guardian...")
        
        # Step 1: Setup logging
        self._setup_logging()
        
        # Step 2: Initialize hardware layer
        self._initialize_hardware_layer()
        
        # Step 3: Check drivers
        self._check_drivers()
        
        # Step 4: Load adapters
        self._load_adapters()
        
        # Step 5: Verify Npcap (Windows)
        self._verify_npcap()
        
        # Step 6: Initialize AI engine
        self._initialize_ai_engine()
        
        # Step 7: Initialize database
        self._initialize_database()
        
        # Step 8: Load plugins
        self._load_plugins()
        
        print("Initialization complete!")
        return True
    
    def _setup_logging(self):
        """Setup application logging"""
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "app.log"),
                logging.StreamHandler()
            ]
        )
        self.initialized_modules.append("logging")
        print("✓ Logging initialized")
    
    def _initialize_hardware_layer(self):
        """Initialize hardware abstraction layer"""
        from core.hardware_layer import HardwareLayer
        self.hardware_layer = HardwareLayer()
        self.initialized_modules.append("hardware_layer")
        print("✓ Hardware layer initialized")
    
    def _check_drivers(self):
        """Check and validate network drivers"""
        from drivers.driver_manager import DriverManager
        self.driver_manager = DriverManager()
        self.driver_manager.check_all_drivers()
        self.initialized_modules.append("drivers")
        print("✓ Drivers checked")
    
    def _load_adapters(self):
        """Load available network adapters"""
        from adapters.adapter_manager import AdapterManager
        self.adapter_manager = AdapterManager()
        self.adapter_manager.discover_adapters()
        self.initialized_modules.append("adapters")
        print("✓ Adapters loaded")
    
    def _verify_npcap(self):
        """Verify Npcap installation (Windows)"""
        import platform
        if platform.system() == "Windows":
            from drivers.npcap_checker import NpcapChecker
            npcap_checker = NpcapChecker()
            if not npcap_checker.is_installed():
                print("⚠ Npcap not detected - Some features may be limited")
            else:
                print("✓ Npcap verified")
        else:
            print("ℹ Npcap check skipped (non-Windows)")
        self.initialized_modules.append("npcap_check")
    
    def _initialize_ai_engine(self):
        """Initialize AI engine for network intelligence"""
        from ai.ai_engine import AIEngine
        self.ai_engine = AIEngine()
        self.initialized_modules.append("ai_engine")
        print("✓ AI engine initialized")
    
    def _initialize_database(self):
        """Initialize local database"""
        from database.db_manager import DatabaseManager
        self.db_manager = DatabaseManager()
        self.db_manager.initialize()
        self.initialized_modules.append("database")
        print("✓ Database initialized")
    
    def _load_plugins(self):
        """Load plugin system"""
        from plugins.plugin_manager import PluginManager
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugins()
        self.initialized_modules.append("plugins")
        print("✓ Plugins loaded")
    
    def get_status(self):
        """Get initialization status"""
        return {
            "initialized": len(self.initialized_modules),
            "modules": self.initialized_modules
        }
