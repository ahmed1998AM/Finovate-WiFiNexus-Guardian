"""
Npcap Checker - Verifies Npcap installation on Windows
"""

import platform
import os
from pathlib import Path


class NpcapChecker:
    """Checks for Npcap installation and status"""
    
    def __init__(self):
        self.platform = platform.system()
        self.npcap_path = None
        self.is_installed_flag = False
        
    def is_installed(self) -> bool:
        """Check if Npcap is installed"""
        if self.platform != "Windows":
            return False
            
        # Common Npcap installation paths
        npcap_paths = [
            r"C:\Program Files\Npcap",
            r"C:\Program Files (x86)\Npcap",
            r"C:\Windows\System32\Npcap"
        ]
        
        for path in npcap_paths:
            if os.path.exists(path):
                self.npcap_path = path
                self.is_installed_flag = True
                return True
                
        # Check registry for Npcap
        try:
            import winreg
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\Npcap"
                )
                winreg.CloseKey(key)
                self.is_installed_flag = True
                return True
            except WindowsError:
                pass
        except ImportError:
            pass
            
        return False
    
    def get_version(self) -> str:
        """Get Npcap version if installed"""
        if not self.is_installed():
            return "Not installed"
            
        if self.npcap_path:
            version_file = Path(self.npcap_path) / "version.txt"
            if version_file.exists():
                try:
                    return version_file.read_text().strip()
                except:
                    pass
                    
        return "Unknown version"
    
    def get_capabilities(self) -> dict:
        """Get Npcap capabilities"""
        capabilities = {
            "installed": self.is_installed(),
            "version": self.get_version(),
            "loopback_support": False,
            "raw_802.11_support": False,
            "monitor_mode_support": False
        }
        
        if capabilities["installed"]:
            # Assume basic capabilities if installed
            capabilities["loopback_support"] = True
            capabilities["raw_802.11_support"] = True
            capabilities["monitor_mode_support"] = True
            
        return capabilities
    
    def check_npcap_service(self) -> bool:
        """Check if Npcap service is running"""
        if self.platform != "Windows":
            return False
            
        try:
            import subprocess
            result = subprocess.run(
                ["sc", "query", "npcap"],
                capture_output=True,
                text=True
            )
            return "RUNNING" in result.stdout
        except:
            return False
    
    def get_installation_guide(self) -> str:
        """Get installation guide for Npcap"""
        return """
Npcap Installation Guide:
=========================

1. Download Npcap from: https://npcap.com/
2. Run the installer as Administrator
3. During installation, enable these options:
   - Install Npcap in WinPcap API-compatible Mode
   - Support raw 802.11 traffic (and monitor mode)
4. Complete installation and restart if prompted
5. Verify installation by checking Device Manager

Note: Npcap is required for advanced packet capture features on Windows.
"""
