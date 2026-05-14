"""
Adapter Manager - Discovers and manages network adapters
"""

import psutil
from typing import Dict, List, Optional


class AdapterManager:
    """Manages discovery and configuration of network adapters"""
    
    def __init__(self):
        self.adapters = {}
        self.wifi_adapters = []
        self.active_adapter = None
        
    def discover_adapters(self) -> List[Dict]:
        """Discover all network adapters on the system"""
        self.adapters = {}
        self.wifi_adapters = []
        
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for iface_name, addrs in net_if_addrs.items():
                stats = net_if_stats.get(iface_name)
                
                # Get IPv4 addresses
                ipv4_addresses = []
                mac_address = None
                
                for addr in addrs:
                    if addr.family == 2:  # AF_INET
                        ipv4_addresses.append(addr.address)
                    elif addr.family == 17:  # AF_LINK (MAC address on some systems)
                        mac_address = addr.address
                
                adapter_info = {
                    "name": iface_name,
                    "ipv4_addresses": ipv4_addresses,
                    "mac_address": mac_address,
                    "is_up": stats.isup if stats else False,
                    "speed_mbps": stats.speed if stats else 0,
                    "duplex": str(stats.duplex) if stats else "unknown",
                    "mtu": stats.mtu if stats else 1500,
                    "type": self._detect_adapter_type(iface_name)
                }
                
                self.adapters[iface_name] = adapter_info
                
                # Identify WiFi adapters
                if adapter_info["type"] == "wifi":
                    self.wifi_adapters.append(adapter_info)
                    
        except Exception as e:
            print(f"Error discovering adapters: {e}")
            
        return list(self.adapters.values())
    
    def _detect_adapter_type(self, iface_name: str) -> str:
        """Detect the type of network adapter"""
        name_lower = iface_name.lower()
        
        # WiFi patterns
        wifi_patterns = ['wireless', 'wifi', 'wlan', 'wi-fi', '802.11']
        if any(pattern in name_lower for pattern in wifi_patterns):
            return "wifi"
        
        # Ethernet patterns
        ethernet_patterns = ['ethernet', 'eth', 'local area connection', 'gbe']
        if any(pattern in name_lower for pattern in ethernet_patterns):
            return "ethernet"
        
        # Virtual/Loopback
        if 'loopback' in name_lower or name_lower == 'lo':
            return "loopback"
        
        if 'virtual' in name_lower or 'vmnet' in name_lower or 'vbox' in name_lower:
            return "virtual"
        
        return "other"
    
    def get_wifi_adapters(self) -> List[Dict]:
        """Get list of WiFi adapters"""
        if not self.wifi_adapters:
            self.discover_adapters()
        return self.wifi_adapters
    
    def get_active_wifi_adapter(self) -> Optional[Dict]:
        """Get the currently active WiFi adapter"""
        wifi_adapters = self.get_wifi_adapters()
        for adapter in wifi_adapters:
            if adapter.get("is_up"):
                self.active_adapter = adapter
                return adapter
        return None
    
    def set_active_adapter(self, adapter_name: str) -> bool:
        """Set a specific adapter as active"""
        if adapter_name in self.adapters:
            self.active_adapter = self.adapters[adapter_name]
            return True
        return False
    
    def get_adapter_by_name(self, name: str) -> Optional[Dict]:
        """Get adapter information by name"""
        return self.adapters.get(name)
    
    def get_adapter_statistics(self, adapter_name: str) -> Dict:
        """Get statistics for a specific adapter"""
        try:
            io_counters = psutil.net_io_counters(pernic=True)
            if adapter_name in io_counters:
                stats = io_counters[adapter_name]
                return {
                    "bytes_sent": stats.bytes_sent,
                    "bytes_recv": stats.bytes_recv,
                    "packets_sent": stats.packets_sent,
                    "packets_recv": stats.packets_recv,
                    "errors_in": stats.errin,
                    "errors_out": stats.errout,
                    "drops_in": stats.dropin,
                    "drops_out": stats.dropout
                }
        except Exception as e:
            print(f"Error getting adapter statistics: {e}")
            
        return {}
    
    def refresh(self) -> List[Dict]:
        """Refresh adapter list"""
        return self.discover_adapters()
