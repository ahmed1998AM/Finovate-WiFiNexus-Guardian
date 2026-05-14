"""
Driver Manager - Manages network adapter drivers across platforms
"""

import platform
import subprocess
from typing import Dict, List, Optional


class DriverManager:
    """Manages detection and validation of network drivers"""
    
    def __init__(self):
        self.platform = platform.system()
        self.drivers_status = {}
        
    def check_all_drivers(self) -> Dict:
        """Check status of all network drivers"""
        if self.platform == "Windows":
            return self._check_windows_drivers()
        elif self.platform == "Linux":
            return self._check_linux_drivers()
        elif self.platform == "Darwin":
            return self._check_macos_drivers()
        else:
            return {"error": f"Unsupported platform: {self.platform}"}
    
    def _check_windows_drivers(self) -> Dict:
        """Check Windows network drivers"""
        drivers_info = {
            "platform": "Windows",
            "adapters": [],
            "monitor_mode_support": False
        }
        
        try:
            # Use PowerShell to get network adapter info
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-NetAdapter | Select-Object Name, Status, DriverVersion, InterfaceDescription | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                adapters = json.loads(result.stdout)
                for adapter in adapters:
                    drivers_info["adapters"].append({
                        "name": adapter.get("Name", "Unknown"),
                        "status": adapter.get("Status", "Unknown"),
                        "driver_version": adapter.get("DriverVersion", "Unknown"),
                        "description": adapter.get("InterfaceDescription", "Unknown")
                    })
                    
                    # Check for monitor mode capability
                    if "wireless" in adapter.get("InterfaceDescription", "").lower():
                        drivers_info["monitor_mode_support"] = True
                        
        except Exception as e:
            drivers_info["error"] = str(e)
            
        self.drivers_status = drivers_info
        return drivers_info
    
    def _check_linux_drivers(self) -> Dict:
        """Check Linux network drivers"""
        drivers_info = {
            "platform": "Linux",
            "adapters": [],
            "monitor_mode_support": False
        }
        
        try:
            # Get wireless info using iwconfig
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse iwconfig output
                lines = result.stdout.split('\n')
                current_adapter = None
                
                for line in lines:
                    if 'IEEE 802.11' in line:
                        current_adapter = line.split()[0]
                        drivers_info["adapters"].append({
                            "name": current_adapter,
                            "status": "detected",
                            "type": "wireless"
                        })
                        drivers_info["monitor_mode_support"] = True
                        
        except Exception as e:
            drivers_info["error"] = str(e)
            
        self.drivers_status = drivers_info
        return drivers_info
    
    def _check_macos_drivers(self) -> Dict:
        """Check macOS network drivers"""
        drivers_info = {
            "platform": "macOS",
            "adapters": [],
            "monitor_mode_support": False
        }
        
        try:
            # Use networksetup to get WiFi info
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if 'Wi-Fi' in line:
                        # Get the device name from next line
                        if i + 1 < len(lines) and 'Device:' in lines[i + 1]:
                            device = lines[i + 1].split(':')[1].strip()
                            drivers_info["adapters"].append({
                                "name": device,
                                "status": "detected",
                                "type": "wireless"
                            })
                            
        except Exception as e:
            drivers_info["error"] = str(e)
            
        self.drivers_status = drivers_info
        return drivers_info
    
    def get_driver_recommendations(self) -> List[str]:
        """Get recommendations for driver updates or installations"""
        recommendations = []
        
        if not self.drivers_status:
            self.check_all_drivers()
        
        if self.platform == "Windows":
            if not any("Npcap" in str(adapter) for adapter in self.drivers_status.get("adapters", [])):
                recommendations.append("Install Npcap for advanced packet capture features")
                
        return recommendations
    
    def is_monitor_mode_supported(self) -> bool:
        """Check if monitor mode is supported"""
        if not self.drivers_status:
            self.check_all_drivers()
        return self.drivers_status.get("monitor_mode_support", False)
