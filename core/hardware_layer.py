"""
Hardware Abstraction Layer - Cross-platform hardware interface
"""

import platform
import psutil
from typing import Dict, List, Optional


class HardwareLayer:
    """Abstracts hardware access across different platforms"""
    
    def __init__(self):
        self.system_info = {}
        self.network_interfaces = {}
        self._detect_system()
        
    def _detect_system(self):
        """Detect system information"""
        self.system_info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
        
    def get_network_interfaces(self) -> Dict:
        """Get all network interfaces with their details"""
        interfaces = {}
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for iface_name, addrs in net_if_addrs.items():
                stats = net_if_stats.get(iface_name)
                interfaces[iface_name] = {
                    "name": iface_name,
                    "addresses": [str(addr.address) for addr in addrs if addr.family == 2],  # IPv4
                    "is_up": stats.isup if stats else False,
                    "speed": stats.speed if stats else 0,
                    "duplex": str(stats.duplex) if stats else "unknown"
                }
        except Exception as e:
            print(f"Error getting network interfaces: {e}")
            
        self.network_interfaces = interfaces
        return interfaces
    
    def get_wifi_adapters(self) -> List[Dict]:
        """Filter and return only WiFi adapters"""
        wifi_adapters = []
        interfaces = self.get_network_interfaces()
        
        # Common WiFi adapter name patterns
        wifi_patterns = ['wireless', 'wifi', 'wlan', 'wi-fi', '802.11']
        
        for name, info in interfaces.items():
            is_wifi = any(pattern in name.lower() for pattern in wifi_patterns)
            if is_wifi or info.get('is_up'):
                wifi_adapters.append({
                    "name": name,
                    "addresses": info.get('addresses', []),
                    "status": "active" if info.get('is_up') else "inactive",
                    "speed_mbps": info.get('speed', 0)
                })
                
        return wifi_adapters
    
    def get_cpu_info(self) -> Dict:
        """Get CPU information"""
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "total_cores": psutil.cpu_count(logical=True),
            "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
        }
    
    def get_memory_info(self) -> Dict:
        """Get memory information"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": round(mem.total / (1024 ** 3), 2),
            "available_gb": round(mem.available / (1024 ** 3), 2),
            "percent_used": mem.percent
        }
    
    def get_disk_info(self) -> Dict:
        """Get disk information"""
        disk = psutil.disk_usage('/')
        return {
            "total_gb": round(disk.total / (1024 ** 3), 2),
            "used_gb": round(disk.used / (1024 ** 3), 2),
            "free_gb": round(disk.free / (1024 ** 3), 2),
            "percent_used": disk.percent
        }
    
    def get_full_system_info(self) -> Dict:
        """Get complete system information"""
        return {
            "system": self.system_info,
            "cpu": self.get_cpu_info(),
            "memory": self.get_memory_info(),
            "disk": self.get_disk_info(),
            "network_interfaces": self.get_network_interfaces(),
            "wifi_adapters": self.get_wifi_adapters()
        }
