"""
Network Interface Manager Pro - Professional Network Adapter Management
Detects internal/external adapters, supports monitor mode, adapter selection
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import subprocess
import re
import json
import platform
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path


class NetworkInterface:
    """Represents a single network interface"""
    
    def __init__(self, name: str, mac: str = None, vendor: str = None):
        self.name = name
        self.mac = mac or "00:00:00:00:00:00"
        self.vendor = vendor or "Unknown"
        self.type = "unknown"  # wireless, ethernet, virtual
        self.state = "unknown"  # up, down, dormant
        self.ip_address = None
        self.netmask = None
        self.gateway = None
        self.driver = None
        self.driver_version = None
        self.is_external = False
        self.is_usb = False
        self.monitor_mode_capable = False
        self.monitor_mode_enabled = False
        self.supported_modes = []
        self.frequency = None
        self.channel = None
        self.signal_strength = None
        self.tx_power = None
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'mac': self.mac,
            'vendor': self.vendor,
            'type': self.type,
            'state': self.state,
            'ip_address': self.ip_address,
            'netmask': self.netmask,
            'gateway': self.gateway,
            'driver': self.driver,
            'driver_version': self.driver_version,
            'is_external': self.is_external,
            'is_usb': self.is_usb,
            'monitor_mode_capable': self.monitor_mode_capable,
            'monitor_mode_enabled': self.monitor_mode_enabled,
            'supported_modes': self.supported_modes,
            'frequency': self.frequency,
            'channel': self.channel,
            'signal_strength': self.signal_strength,
            'tx_power': self.tx_power
        }
    
    def __str__(self) -> str:
        status = "🟢" if self.state == "up" else "🔴"
        ext = "🔌 EXT" if self.is_external else "💻 INT"
        usb = "📶 USB" if self.is_usb else ""
        mon = "👁️ MON" if self.monitor_mode_enabled else ""
        return f"{status} {self.name} ({self.mac}) [{self.type}] {ext} {usb} {mon}"


class NetworkInterfaceManager:
    """
    Professional Network Interface Manager
    - Detects all network adapters (internal/external)
    - Identifies USB vs PCIe adapters
    - Checks monitor mode capability
    - Supports adapter selection for operations
    - Cross-platform support (Windows, Linux, macOS)
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.interfaces: List[NetworkInterface] = []
        self.wireless_interfaces: List[NetworkInterface] = []
        self.external_interfaces: List[NetworkInterface] = []
        self.usb_interfaces: List[NetworkInterface] = []
        self.monitor_capable_interfaces: List[NetworkInterface] = []
        
        # Vendor database
        self.vendor_db = self._load_vendor_db()
        
        # Scan results
        self.last_scan_time = None
        self.total_detected = 0
        
    def _load_vendor_db(self) -> Dict:
        """Load MAC vendor database"""
        vendors = {
            '00:0C:29': 'VMware',
            '00:1A:2B': 'TP-Link',
            '00:1E:C2': 'Belkin',
            '00:22:6B': 'Dell',
            '00:25:9C': 'Apple',
            '00:26:B8': 'Samsung',
            '00:50:56': 'VMware',
            '08:62:66': 'Intel',
            '0C:D2:92': 'Cisco',
            '10:FE:ED': 'TP-Link',
            '14:CC:20': 'TP-Link',
            '18:E8:29': 'Huawei',
            '1C:AF:F7': 'D-Link',
            '2C:54:CF': 'Cisco',
            '3C:5A:B4': 'Google',
            '48:51:B7': 'Huawei',
            '50:C7:BF': 'Samsung',
            '5C:AA:FD': 'Google',
            '64:BC:0C': 'Motorola',
            '68:A8:6D': 'Apple',
            '70:B3:D5': 'Apple',
            '78:CA:39': 'Nokia',
            '80:3F:10': 'Wistron',
            '84:D6:D0': 'Amazon',
            '88:66:A5': 'Apple',
            '90:9F:33': 'Polidea',
            '98:FC:11': 'Cisco',
            'A0:99:9B': 'Apple',
            'A4:C3:F0': 'Netgear',
            'AC:1F:6B': 'Google',
            'B8:27:EB': 'Raspberry Pi',
            'BC:5F:F4': 'ASUSTek',
            'C4:49:A3': 'Mellanox',
            'C8:3A:35': 'Tenda',
            'CC:46:D6': 'Cisco',
            'D0:50:99': 'Espressif',
            'EC:1A:59': 'Belkin',
            'F0:9F:C2': 'Google',
            'F4:0F:24': 'Cisco',
            'F8:1A:67': 'TP-Link',
            'FC:65:DE': 'Intel',
            '00:1B:44': 'Realtek',
            '00:1D:7E': 'Realtek',
            '00:23:CD': 'Realtek',
            '00:27:19': 'Realtek',
            '00:4A:77': 'Realtek',
            '00:E0:4C': 'Realtek',
            '08:10:74': 'Realtek',
            '10:C3:7B': 'ASUS',
            '20:0C:C8': 'TP-Link',
            '24:4B:81': 'HP',
            '34:17:EB': 'Intel',
            '40:A6:B9': 'Passive Systems',
            '54:04:A6': 'ASUS',
            '60:F8:1D': 'Roku',
            '74:DA:38': 'TP-Link',
            '8C:DC:D4': 'Le Shi',
            '9C:B6:54': 'Hewlett Packard',
            'A8:6A:BB': 'RIM',
            'B4:75:0E': 'Pantech',
            'C0:EE:FB': 'OnePlus',
            'D8:FC:93': 'Intel',
            'E0:AC:CB': 'Hewlett Packard',
            'F4:8E:38': 'Honor'
        }
        return vendors
    
    def scan_all_interfaces(self) -> List[NetworkInterface]:
        """
        Scan and detect all network interfaces
        
        Returns:
            List of detected NetworkInterface objects
        """
        print(f"\n🔍 Scanning network interfaces on {self.platform}...")
        
        self.interfaces = []
        self.wireless_interfaces = []
        self.external_interfaces = []
        self.usb_interfaces = []
        self.monitor_capable_interfaces = []
        
        if self.platform == "Linux":
            self._scan_linux()
        elif self.platform == "Windows":
            self._scan_windows()
        elif self.platform == "Darwin":
            self._scan_macos()
        else:
            print(f"⚠️ Unsupported platform: {self.platform}")
            self._simulate_scan()
        
        self.last_scan_time = datetime.now()
        self.total_detected = len(self.interfaces)
        
        print(f"✓ Detected {self.total_detected} interface(s)")
        print(f"  • Wireless: {len(self.wireless_interfaces)}")
        print(f"  • External: {len(self.external_interfaces)}")
        print(f"  • USB: {len(self.usb_interfaces)}")
        print(f"  • Monitor Mode Capable: {len(self.monitor_capable_interfaces)}")
        
        return self.interfaces
    
    def _scan_linux(self):
        """Scan interfaces on Linux"""
        try:
            # Get interface list using ip command
            result = subprocess.run(
                ["ip", "-o", "link", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if not line.strip():
                        continue
                    
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        iface_num = parts[0].strip()
                        iface_info = parts[1].split('@')[0].strip()
                        iface_name = iface_info.split(':')[0].strip()
                        
                        # Create interface object
                        interface = NetworkInterface(iface_name)
                        
                        # Check state
                        if 'UP' in line:
                            interface.state = 'up'
                        elif 'DOWN' in line:
                            interface.state = 'down'
                        else:
                            interface.state = 'dormant'
                        
                        # Get MAC address
                        mac_match = re.search(r'link/ether ([0-9a-fA-F:]+)', line)
                        if mac_match:
                            interface.mac = mac_match.group(1).upper()
                            interface.vendor = self._get_vendor(interface.mac)
                        
                        # Determine type
                        if 'wlan' in iface_name or 'wlx' in iface_name:
                            interface.type = 'wireless'
                            self.wireless_interfaces.append(interface)
                            
                            # Check if external (USB)
                            if self._is_usb_interface_linux(iface_name):
                                interface.is_external = True
                                interface.is_usb = True
                                self.external_interfaces.append(interface)
                                self.usb_interfaces.append(interface)
                            
                            # Check monitor mode capability
                            if self._check_monitor_mode_linux(iface_name):
                                interface.monitor_mode_capable = True
                                self.monitor_capable_interfaces.append(interface)
                        elif 'eth' in iface_name or 'en' in iface_name:
                            interface.type = 'ethernet'
                        elif 'lo' in iface_name:
                            interface.type = 'loopback'
                        elif 'docker' in iface_name or 'br-' in iface_name:
                            interface.type = 'virtual'
                        else:
                            interface.type = 'other'
                        
                        # Get additional info
                        self._get_interface_details_linux(interface)
                        
                        self.interfaces.append(interface)
            
            # Also check iwconfig for wireless details
            self._scan_wireless_details_linux()
            
        except Exception as e:
            print(f"Linux scan error: {e}")
            self._simulate_scan()
    
    def _is_usb_interface_linux(self, iface_name: str) -> bool:
        """Check if interface is USB on Linux"""
        try:
            # Check sysfs for USB path
            usb_path = Path(f"/sys/class/net/{iface_name}/device/usb")
            if usb_path.exists():
                return True
            
            # Alternative: check uevent
            uevent_path = Path(f"/sys/class/net/{iface_name}/device/uevent")
            if uevent_path.exists():
                with open(uevent_path, 'r') as f:
                    content = f.read()
                    if 'usb' in content.lower():
                        return True
            
            # Check interface name pattern (wlx + MAC is USB)
            if iface_name.startswith('wlx'):
                return True
                
            return False
            
        except:
            return False
    
    def _check_monitor_mode_linux(self, iface_name: str) -> bool:
        """Check if interface supports monitor mode on Linux"""
        try:
            # Try iw command
            result = subprocess.run(
                ["iw", iface_name, "info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                output = result.stdout
                if 'Supported interface modes' in output:
                    if 'monitor' in output.lower():
                        return True
            
            # Alternative: check phy
            result = subprocess.run(
                ["iw", "list"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and 'monitor' in result.stdout.lower():
                return True
            
            return False
            
        except:
            return False
    
    def _get_interface_details_linux(self, interface: NetworkInterface):
        """Get detailed interface information on Linux"""
        try:
            # Get IP address
            result = subprocess.run(
                ["ip", "-o", "-4", "addr", "show", interface.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)/(\d+)', result.stdout)
                if match:
                    interface.ip_address = match.group(1)
                    interface.netmask = match.group(2)
            
            # Get driver info
            result = subprocess.run(
                ["ethtool", "-i", interface.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                driver_match = re.search(r'driver:\s*(\S+)', result.stdout)
                version_match = re.search(r'version:\s*(\S+)', result.stdout)
                
                if driver_match:
                    interface.driver = driver_match.group(1)
                if version_match:
                    interface.driver_version = version_match.group(1)
            
            # Get wireless details if applicable
            if interface.type == 'wireless':
                result = subprocess.run(
                    ["iwconfig", interface.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Extract frequency
                    freq_match = re.search(r'Frequency:(\d+\.?\d*)', result.stdout)
                    if freq_match:
                        interface.frequency = float(freq_match.group(1))
                    
                    # Extract signal strength
                    signal_match = re.search(r'Signal level=(-?\d+)', result.stdout)
                    if signal_match:
                        interface.signal_strength = int(signal_match.group(1))
                    
                    # Extract tx power
                    tx_match = re.search(r'Tx-Power=(\d+)', result.stdout)
                    if tx_match:
                        interface.tx_power = int(tx_match.group(1))
                        
        except Exception as e:
            pass
    
    def _scan_wireless_details_linux(self):
        """Scan additional wireless details"""
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse wireless interfaces
                current_iface = None
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line:
                        iface_name = line.split()[0]
                        for iface in self.wireless_interfaces:
                            if iface.name == iface_name:
                                current_iface = iface
                                break
                    
                    if current_iface:
                        if 'ESSID' in line:
                            essid_match = re.search(r'ESSID:"([^"]*)"', line)
                            if essid_match:
                                current_iface.ssid = essid_match.group(1)
                                
        except:
            pass
    
    def _scan_windows(self):
        """Scan interfaces on Windows"""
        try:
            # Get adapter info using PowerShell
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-NetAdapter | Select-Object Name, Status, MacAddress, DriverVersion, InterfaceDescription, NdisVersion | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=15,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                adapters = json.loads(result.stdout)
                
                for adapter in adapters:
                    name = adapter.get('Name', 'Unknown')
                    mac = adapter.get('MacAddress', '00:00:00:00:00:00')
                    description = adapter.get('InterfaceDescription', '')
                    driver_version = adapter.get('DriverVersion', '')
                    status = adapter.get('Status', 'Unknown')
                    
                    interface = NetworkInterface(name, mac)
                    interface.vendor = self._get_vendor(mac)
                    interface.driver_version = driver_version
                    interface.state = 'up' if status == 'Up' else 'down'
                    
                    # Determine type
                    desc_lower = description.lower()
                    if 'wireless' in desc_lower or 'wifi' in desc_lower or '802.11' in desc_lower:
                        interface.type = 'wireless'
                        self.wireless_interfaces.append(interface)
                        
                        # Check if USB
                        if 'usb' in desc_lower:
                            interface.is_external = True
                            interface.is_usb = True
                            self.external_interfaces.append(interface)
                            self.usb_interfaces.append(interface)
                    elif 'ethernet' in desc_lower or 'gbe' in desc_lower:
                        interface.type = 'ethernet'
                    elif 'bluetooth' in desc_lower:
                        interface.type = 'bluetooth'
                    elif 'loopback' in desc_lower:
                        interface.type = 'loopback'
                    elif 'hyper-v' in desc_lower or 'virtual' in desc_lower:
                        interface.type = 'virtual'
                    else:
                        interface.type = 'other'
                    
                    # Get IP configuration
                    self._get_ip_config_windows(interface)
                    
                    self.interfaces.append(interface)
            
            # Additional wireless info
            self._scan_wireless_windows()
            
        except Exception as e:
            print(f"Windows scan error: {e}")
            self._simulate_scan()
    
    def _get_ip_config_windows(self, interface: NetworkInterface):
        """Get IP configuration on Windows"""
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-NetIPConfiguration -InterfaceAlias '{interface.name}' | Select-Object IPv4Address | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                config = json.loads(result.stdout)
                if config and 'IPv4Address' in config:
                    ip_info = config['IPv4Address']
                    if isinstance(ip_info, dict) and 'IPAddress' in ip_info:
                        interface.ip_address = ip_info['IPAddress']
                        
        except:
            pass
    
    def _scan_wireless_windows(self):
        """Scan wireless network details on Windows"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            if result.returncode == 0:
                # Parse signal strength, channel, etc.
                for interface in self.wireless_interfaces:
                    # Find interface section
                    if interface.name in result.stdout:
                        # Extract signal strength
                        signal_match = re.search(r'Signal\s*:\s*(\d+)%', result.stdout)
                        if signal_match:
                            signal_percent = int(signal_match.group(1))
                            interface.signal_strength = signal_percent * -1 + 100
                        
                        # Extract radio type
                        radio_match = re.search(r'Radio type\s*:\s*(\S+)', result.stdout)
                        if radio_match:
                            radio_type = radio_match.group(1)
                            if '802.11ac' in radio_type or '802.11ax' in radio_type:
                                interface.supported_modes = ['802.11a', '802.11b', '802.11g', '802.11n', '802.11ac', '802.11ax']
                            elif '802.11n' in radio_type:
                                interface.supported_modes = ['802.11a', '802.11b', '802.11g', '802.11n']
                                
        except:
            pass
    
    def _scan_macos(self):
        """Scan interfaces on macOS"""
        try:
            # Use networksetup
            result = subprocess.run(
                ["networksetup", "-listallhardwareports"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                current_interface = None
                
                for line in lines:
                    if 'Hardware Port:' in line:
                        port_name = line.split(':')[1].strip()
                        current_interface = NetworkInterface(port_name)
                        self.interfaces.append(current_interface)
                        
                        if 'Wi-Fi' in port_name or 'AirPort' in port_name:
                            current_interface.type = 'wireless'
                            self.wireless_interfaces.append(current_interface)
                        elif 'Ethernet' in port_name:
                            current_interface.type = 'ethernet'
                        elif 'Bluetooth' in port_name:
                            current_interface.type = 'bluetooth'
                        else:
                            current_interface.type = 'other'
                    
                    elif 'Device:' in line and current_interface:
                        current_interface.device = line.split(':')[1].strip()
                    
                    elif 'Ethernet Address:' in line and current_interface:
                        mac = line.split(':')[1].strip().upper()
                        current_interface.mac = mac
                        current_interface.vendor = self._get_vendor(mac)
                
                # Get additional info for wireless
                if self.wireless_interfaces:
                    self._scan_wireless_macos()
                    
        except Exception as e:
            print(f"macOS scan error: {e}")
            self._simulate_scan()
    
    def _scan_wireless_macos(self):
        """Scan wireless details on macOS"""
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for interface in self.wireless_interfaces:
                    # Extract signal strength (RSSI)
                    rssi_match = re.search(r'agrCtlRSSI:\s*(-?\d+)', result.stdout)
                    if rssi_match:
                        interface.signal_strength = int(rssi_match.group(1))
                    
                    # Extract noise
                    noise_match = re.search(r'agrCtlNoise:\s*(-?\d+)', result.stdout)
                    if noise_match:
                        interface.noise_level = int(noise_match.group(1))
                    
                    # Extract channel
                    channel_match = re.search(r'channel:\s*(\d+)', result.stdout)
                    if channel_match:
                        interface.channel = int(channel_match.group(1))
                        
        except:
            pass
    
    def _simulate_scan(self):
        """Simulate scan for testing/demo"""
        sample_interfaces = [
            ("wlan0", "00:1A:2B:3C:4D:5E", "wireless", False, False),
            ("wlan1", "00:1B:44:5F:6A:7B", "wireless", True, True),
            ("eth0", "00:22:6B:8C:9D:AE", "ethernet", False, False),
            ("lo", "00:00:00:00:00:00", "loopback", False, False)
        ]
        
        for name, mac, iface_type, is_external, is_usb in sample_interfaces:
            interface = NetworkInterface(name, mac)
            interface.type = iface_type
            interface.is_external = is_external
            interface.is_usb = is_usb
            interface.state = 'up'
            interface.vendor = self._get_vendor(mac)
            
            if iface_type == 'wireless':
                self.wireless_interfaces.append(interface)
                interface.monitor_mode_capable = True
                self.monitor_capable_interfaces.append(interface)
                
                if is_external:
                    self.external_interfaces.append(interface)
                if is_usb:
                    self.usb_interfaces.append(interface)
            
            self.interfaces.append(interface)
    
    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC address"""
        if not mac or mac == "00:00:00:00:00:00":
            return "Unknown"
        
        mac_prefix = mac.upper().replace(':', '')[:6]
        mac_prefix_formatted = ':'.join([mac_prefix[i:i+2] for i in range(0, 6, 2)])
        
        return self.vendor_db.get(mac_prefix_formatted, "Unknown")
    
    def select_interface(self, index: int = 0, interface_type: str = 'wireless') -> Optional[NetworkInterface]:
        """
        Select an interface for operations
        
        Args:
            index: Index of interface in filtered list
            interface_type: Type filter ('wireless', 'external', 'usb', 'monitor')
            
        Returns:
            Selected NetworkInterface or None
        """
        if interface_type == 'wireless':
            candidates = self.wireless_interfaces
        elif interface_type == 'external':
            candidates = self.external_interfaces
        elif interface_type == 'usb':
            candidates = self.usb_interfaces
        elif interface_type == 'monitor':
            candidates = self.monitor_capable_interfaces
        else:
            candidates = self.interfaces
        
        if not candidates:
            return None
        
        if 0 <= index < len(candidates):
            return candidates[index]
        return None
    
    def get_preferred_interface(self) -> Optional[NetworkInterface]:
        """
        Get preferred interface for operations
        Priority: External USB > Internal Wireless > Any Wireless
        
        Returns:
            Preferred NetworkInterface or None
        """
        # Prefer external USB adapters (better for monitoring)
        if self.usb_interfaces:
            return self.usb_interfaces[0]
        
        # Then external adapters
        if self.external_interfaces:
            return self.external_interfaces[0]
        
        # Then any wireless
        if self.wireless_interfaces:
            return self.wireless_interfaces[0]
        
        return None
    
    def enable_monitor_mode(self, interface: NetworkInterface) -> bool:
        """Enable monitor mode on interface"""
        if not interface.monitor_mode_capable:
            print(f"❌ {interface.name} does not support monitor mode")
            return False
        
        if self.platform == "Linux":
            try:
                # Kill interfering processes
                subprocess.run(["sudo", "killall", "NetworkManager"], capture_output=True, timeout=5)
                
                # Enable monitor mode
                result = subprocess.run(
                    ["sudo", "airmon-ng", "start", interface.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    interface.monitor_mode_enabled = True
                    print(f"✓ Monitor mode enabled on {interface.name}")
                    return True
                    
            except Exception as e:
                print(f"Error enabling monitor mode: {e}")
                return False
        
        print(f"Monitor mode only fully supported on Linux")
        return False
    
    def disable_monitor_mode(self, interface: NetworkInterface) -> bool:
        """Disable monitor mode on interface"""
        if not interface.monitor_mode_enabled:
            return False
        
        if self.platform == "Linux":
            try:
                result = subprocess.run(
                    ["sudo", "airmon-ng", "stop", interface.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    interface.monitor_mode_enabled = False
                    print(f"✓ Monitor mode disabled on {interface.name}")
                    return True
                    
            except Exception as e:
                print(f"Error disabling monitor mode: {e}")
                return False
        
        return False
    
    def export_interfaces(self, format: str = 'json', filename: str = None) -> str:
        """Export interface information to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interfaces_{timestamp}.{format}"
        
        data = {
            'scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'platform': self.platform,
            'total_interfaces': len(self.interfaces),
            'wireless_count': len(self.wireless_interfaces),
            'external_count': len(self.external_interfaces),
            'usb_count': len(self.usb_interfaces),
            'monitor_capable_count': len(self.monitor_capable_interfaces),
            'interfaces': [iface.to_dict() for iface in self.interfaces]
        }
        
        if format.lower() == 'json':
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        elif format.lower() == 'csv':
            with open(filename, 'w') as f:
                f.write("Name,MAC,Vendor,Type,State,IP,External,USB,Monitor_Capable,Monitor_Enabled\n")
                for iface in self.interfaces:
                    f.write(f"{iface.name},{iface.mac},{iface.vendor},{iface.type},{iface.state},"
                           f"{iface.ip_address or ''},{iface.is_external},{iface.is_usb},"
                           f"{iface.monitor_mode_capable},{iface.monitor_mode_enabled}\n")
        
        print(f"✓ Exported interface data to {filename}")
        return filename
    
    def display_all_interfaces(self):
        """Display all interfaces in formatted output"""
        print("\n" + "="*70)
        print("📡 NETWORK INTERFACE MANAGER - DETECTED ADAPTERS")
        print("="*70)
        
        if not self.interfaces:
            print("No interfaces detected. Run scan_all_interfaces() first.")
            return
        
        for i, iface in enumerate(self.interfaces):
            print(f"\n[{i}] {str(iface)}")
            print(f"    Driver: {iface.driver or 'N/A'}")
            print(f"    Driver Ver: {iface.driver_version or 'N/A'}")
            print(f"    IP: {iface.ip_address or 'N/A'}")
            
            if iface.type == 'wireless':
                print(f"    Frequency: {iface.frequency or 'N/A'} GHz")
                print(f"    Channel: {iface.channel or 'N/A'}")
                print(f"    Signal: {iface.signal_strength or 'N/A'} dBm")
                print(f"    TX Power: {iface.tx_power or 'N/A'} dBm")
                print(f"    Supported Modes: {', '.join(iface.supported_modes) or 'N/A'}")
                print(f"    Monitor Mode: {'✓ Capable' if iface.monitor_mode_capable else '✗ Not Supported'}")
                if iface.monitor_mode_capable:
                    print(f"    Monitor Enabled: {'✓ YES' if iface.monitor_mode_enabled else '✗ NO'}")
        
        print("\n" + "="*70)
        
        # Recommendations
        if self.usb_interfaces:
            print("\n💡 RECOMMENDATION: Use external USB adapter for best monitoring results")
            print(f"   Recommended: {self.usb_interfaces[0].name} ({self.usb_interfaces[0].mac})")
        elif self.wireless_interfaces:
            print(f"\n💡 Using internal wireless adapter: {self.wireless_interfaces[0].name}")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    print("="*70)
    print("WiFiNexus Guardian - Network Interface Manager Pro")
    print("="*70)
    
    manager = NetworkInterfaceManager()
    
    # Scan all interfaces
    manager.scan_all_interfaces()
    
    # Display results
    manager.display_all_interfaces()
    
    # Get preferred interface
    preferred = manager.get_preferred_interface()
    if preferred:
        print(f"\n🎯 PREFERRED INTERFACE: {preferred.name}")
        print(f"   Type: {preferred.type}")
        print(f"   External: {'Yes' if preferred.is_external else 'No'}")
        print(f"   USB: {'Yes' if preferred.is_usb else 'No'}")
        print(f"   Monitor Mode: {'Capable' if preferred.monitor_mode_capable else 'Not Supported'}")
    
    # Export data
    manager.export_interfaces(format='json')
    
    print("\n✓ Interface management ready")
    print("="*70)
