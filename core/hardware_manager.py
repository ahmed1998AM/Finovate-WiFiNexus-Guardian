#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Dynamic Hardware Manager
Professional Penetration Testing Tool
Module: Smart Hardware Detection & Management

Features:
- Real-time hardware detection
- Monitor mode support verification
- Injection capability testing
- Automatic driver management
- Fallback mechanisms
- Performance benchmarking
"""

import subprocess
import re
import os
import time
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class InterfaceState(Enum):
    """Interface operational states"""
    UNKNOWN = "unknown"
    DOWN = "down"
    UP = "up"
    MONITOR = "monitor"
    MANAGED = "managed"
    AP = "ap"
    ERROR = "error"


@dataclass
class WiFiInterface:
    """Represents a WiFi interface with capabilities"""
    name: str
    phy: str
    mac: str
    state: InterfaceState
    monitor_supported: bool
    injection_supported: bool
    driver: str
    chipset: str
    frequency: Optional[str] = None
    channel: Optional[int] = None
    ssid: Optional[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['state'] = self.state.value
        return data


class DynamicHardwareManager:
    """
    Advanced hardware management with real-time detection and adaptation
    """
    
    def __init__(self):
        self.interfaces: Dict[str, WiFiInterface] = {}
        self.monitor_interfaces: Dict[str, str] = {}  # name -> original name
        self.benchmark_results: Dict[str, Dict] = {}
        
    def detect_all_interfaces(self) -> List[WiFiInterface]:
        """Detect all wireless interfaces with detailed capabilities"""
        logger.info("Starting hardware detection...")
        interfaces = []
        
        # Get list of physical devices
        try:
            result = subprocess.run(
                ['iw', 'dev'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                interfaces.extend(self._parse_iw_dev(result.stdout))
        except Exception as e:
            logger.warning(f"iw dev failed: {e}")
        
        # Get interface details from ip command
        try:
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self._enrich_with_ip_info(interfaces, result.stdout)
        except Exception as e:
            logger.warning(f"ip link failed: {e}")
        
        # Test capabilities for each interface
        for iface in interfaces:
            self._test_interface_capabilities(iface)
        
        self.interfaces = {iface.name: iface for iface in interfaces}
        logger.info(f"Detected {len(interfaces)} wireless interfaces")
        return interfaces
    
    def _parse_iw_dev(self, output: str) -> List[WiFiInterface]:
        """Parse iw dev output"""
        interfaces = []
        current_iface = None
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith('phy#'):
                if current_iface:
                    interfaces.append(current_iface)
                current_iface = WiFiInterface(
                    name="",
                    phy=line.split()[1],
                    mac="",
                    state=InterfaceState.UNKNOWN,
                    monitor_supported=False,
                    injection_supported=False,
                    driver="",
                    chipset=""
                )
            elif line.startswith('Interface'):
                if current_iface:
                    current_iface.name = line.split()[1]
            elif line.startswith('addr'):
                if current_iface:
                    current_iface.mac = line.split()[1]
        
        if current_iface:
            interfaces.append(current_iface)
        
        return interfaces
    
    def _enrich_with_ip_info(self, interfaces: List[WiFiInterface], output: str):
        """Enrich interface data with ip command info"""
        for iface in interfaces:
            # Find interface in ip output
            pattern = rf'\d+: {re.escape(iface.name)}@.*?state (\w+)'
            match = re.search(pattern, output)
            if match:
                state_str = match.group(1).lower()
                if state_str == 'up':
                    iface.state = InterfaceState.UP
                elif state_str == 'down':
                    iface.state = InterfaceState.DOWN
        
        # Get driver info using ethtool
        for iface in interfaces:
            try:
                result = subprocess.run(
                    ['ethtool', '-i', iface.name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if line.startswith('driver:'):
                            iface.driver = line.split(':', 1)[1].strip()
            except:
                pass
    
    def _test_interface_capabilities(self, iface: WiFiInterface):
        """Test monitor mode and packet injection support"""
        # Test monitor mode support
        try:
            # Check supported interface combinations
            result = subprocess.run(
                ['iw', iface.name, 'info'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                if 'type: monitor' in result.stdout or 'monitor' in result.stdout:
                    iface.state = InterfaceState.MONITOR
                    iface.monitor_supported = True
                elif 'type: managed' in result.stdout:
                    iface.state = InterfaceState.MANAGED
                    iface.monitor_supported = True  # Most cards support it
        except:
            iface.errors.append("Failed to get interface info")
        
        # Test injection capability (simplified test)
        iface.injection_supported = self._test_packet_injection(iface.name)
        
        # Identify chipset from driver
        chipset_map = {
            'ath9k': 'Atheros',
            'ath10k': 'Atheros',
            'rtl88x2bu': 'Realtek',
            'rtl8812au': 'Realtek',
            'mt76': 'MediaTek',
            'iwlwifi': 'Intel',
            'brcmfmac': 'Broadcom'
        }
        for driver, chipset in chipset_map.items():
            if driver in iface.driver.lower():
                iface.chipset = chipset
                break
        
        if not iface.chipset:
            iface.chipset = "Unknown"
            if 'intel' in iface.driver.lower():
                iface.errors.append("Intel cards often have limited injection support")
    
    def _test_packet_injection(self, interface: str) -> bool:
        """Test packet injection capability"""
        # Create a temporary monitor interface for testing
        test_mon = f"{interface}_test"
        try:
            # Try to set monitor mode
            subprocess.run(['ip', 'link', 'set', interface, 'down'], 
                          capture_output=True, timeout=3)
            subprocess.run(['iw', interface, 'set', 'type', 'monitor'],
                          capture_output=True, timeout=3)
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, timeout=3)
            
            # Try to send a test packet (very basic test)
            result = subprocess.run(
                ['aireplay-ng', '--test', interface],
                capture_output=True,
                timeout=10
            )
            
            # Restore managed mode
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          capture_output=True, timeout=3)
            subprocess.run(['iw', interface, 'set', 'type', 'managed'],
                          capture_output=True, timeout=3)
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, timeout=3)
            
            return result.returncode == 0 or 'Injection is working' in result.stdout.decode('utf-8', errors='ignore')
        except:
            # Cleanup on error
            try:
                subprocess.run(['ip', 'link', 'set', interface, 'down'],
                              capture_output=True, timeout=3)
                subprocess.run(['iw', interface, 'set', 'type', 'managed'],
                              capture_output=True, timeout=3)
                subprocess.run(['ip', 'link', 'set', interface, 'up'],
                              capture_output=True, timeout=3)
            except:
                pass
            return False
    
    def enable_monitor_mode(self, interface: str, new_name: Optional[str] = None) -> Optional[str]:
        """Enable monitor mode on an interface"""
        if interface not in self.interfaces:
            logger.error(f"Interface {interface} not found")
            return None
        
        iface = self.interfaces[interface]
        if not iface.monitor_supported:
            logger.error(f"Interface {interface} does not support monitor mode")
            return None
        
        mon_name = new_name or f"{interface}mon"
        
        try:
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          check=True, capture_output=True, timeout=5)
            
            # Set monitor mode
            subprocess.run(['iw', interface, 'set', 'type', 'monitor'],
                          check=True, capture_output=True, timeout=5)
            
            # Rename if needed
            if mon_name != interface:
                subprocess.run(['ip', 'link', 'set', interface, 'name', mon_name],
                              check=True, capture_output=True, timeout=5)
            
            # Bring up
            subprocess.run(['ip', 'link', 'set', mon_name, 'up'],
                          check=True, capture_output=True, timeout=5)
            
            self.monitor_interfaces[mon_name] = interface
            logger.info(f"Monitor mode enabled: {mon_name}")
            return mon_name
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to enable monitor mode: {e}")
            # Attempt recovery
            self._recover_interface(interface)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self._recover_interface(interface)
            return None
    
    def disable_monitor_mode(self, monitor_interface: str) -> bool:
        """Disable monitor mode and restore original interface"""
        if monitor_interface not in self.monitor_interfaces:
            logger.warning(f"Interface {monitor_interface} is not a managed monitor interface")
            return False
        
        original_name = self.monitor_interfaces[monitor_interface]
        
        try:
            subprocess.run(['ip', 'link', 'set', monitor_interface, 'down'],
                          capture_output=True, timeout=5)
            subprocess.run(['iw', monitor_interface, 'set', 'type', 'managed'],
                          capture_output=True, timeout=5)
            
            if monitor_interface != original_name:
                subprocess.run(['ip', 'link', 'set', monitor_interface, 'name', original_name],
                              capture_output=True, timeout=5)
            
            subprocess.run(['ip', 'link', 'set', original_name, 'up'],
                          capture_output=True, timeout=5)
            
            del self.monitor_interfaces[monitor_interface]
            logger.info(f"Monitor mode disabled, restored to {original_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to disable monitor mode: {e}")
            return False
    
    def _recover_interface(self, interface: str):
        """Attempt to recover an interface to managed mode"""
        try:
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          capture_output=True, timeout=3)
            subprocess.run(['iw', interface, 'set', 'type', 'managed'],
                          capture_output=True, timeout=3)
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, timeout=3)
            logger.info(f"Interface {interface} recovered to managed mode")
        except:
            logger.error(f"Failed to recover interface {interface}")
    
    def benchmark_interface(self, interface: str) -> Dict:
        """Benchmark interface performance"""
        if interface not in self.interfaces:
            return {"error": "Interface not found"}
        
        results = {
            "interface": interface,
            "timestamp": time.time(),
            "scan_speed": 0,
            "injection_rate": 0,
            "stability_score": 0
        }
        
        # Benchmark scanning speed
        start = time.time()
        try:
            result = subprocess.run(
                ['iwlist', interface, 'scanning'],
                capture_output=True,
                timeout=15
            )
            scan_time = time.time() - start
            networks = result.stdout.count(b'Cell ')
            results["scan_speed"] = networks / scan_time if scan_time > 0 else 0
        except:
            results["scan_speed"] = 0
        
        # Stability score based on driver and chipset
        iface = self.interfaces[interface]
        stability = 100
        if 'intel' in iface.driver.lower():
            stability -= 30
        if not iface.injection_supported:
            stability -= 40
        if iface.errors:
            stability -= len(iface.errors) * 10
        results["stability_score"] = max(0, stability)
        
        self.benchmark_results[interface] = results
        return results
    
    def get_best_interface(self, purpose: str = "attack") -> Optional[str]:
        """Get the best interface for a specific purpose"""
        if not self.interfaces:
            self.detect_all_interfaces()
        
        best_iface = None
        best_score = -1
        
        for name, iface in self.interfaces.items():
            score = 0
            
            if purpose == "attack":
                if iface.injection_supported:
                    score += 50
                if iface.monitor_supported:
                    score += 30
                if iface.state == InterfaceState.MONITOR:
                    score += 20
            elif purpose == "scanning":
                if iface.state == InterfaceState.UP:
                    score += 30
                if iface.monitor_supported:
                    score += 20
            elif purpose == "stable":
                score = self.benchmark_results.get(name, {}).get("stability_score", 50)
            
            if score > best_score:
                best_score = score
                best_iface = name
        
        return best_iface
    
    def get_status_report(self) -> Dict:
        """Generate comprehensive hardware status report"""
        if not self.interfaces:
            self.detect_all_interfaces()
        
        report = {
            "total_interfaces": len(self.interfaces),
            "monitor_enabled": len(self.monitor_interfaces),
            "interfaces": [iface.to_dict() for iface in self.interfaces.values()],
            "benchmarks": self.benchmark_results,
            "recommendations": []
        }
        
        # Generate recommendations
        for iface in self.interfaces.values():
            if not iface.injection_supported:
                report["recommendations"].append(
                    f"Interface {iface.name} ({iface.chipset}) does not support packet injection. Consider using an external adapter."
                )
            if 'intel' in iface.driver.lower():
                report["recommendations"].append(
                    f"Intel card detected on {iface.name}. May have limitations in monitor mode."
                )
        
        return report


# Singleton instance
_hardware_manager = None

def get_hardware_manager() -> DynamicHardwareManager:
    """Get singleton instance of hardware manager"""
    global _hardware_manager
    if _hardware_manager is None:
        _hardware_manager = DynamicHardwareManager()
    return _hardware_manager


if __name__ == "__main__":
    # Demo usage
    manager = get_hardware_manager()
    
    print("="*60)
    print("WiFiNexus Guardian - Hardware Detection System")
    print("="*60)
    
    interfaces = manager.detect_all_interfaces()
    
    for iface in interfaces:
        print(f"\n📡 Interface: {iface.name}")
        print(f"   PHY: {iface.phy}")
        print(f"   MAC: {iface.mac}")
        print(f"   Driver: {iface.driver}")
        print(f"   Chipset: {iface.chipset}")
        print(f"   State: {iface.state.value}")
        print(f"   Monitor Support: {'✅' if iface.monitor_supported else '❌'}")
        print(f"   Injection Support: {'✅' if iface.injection_supported else '❌'}")
        if iface.errors:
            print(f"   Warnings: {', '.join(iface.errors)}")
    
    print("\n" + "="*60)
    print("Best interface for attack:", manager.get_best_interface("attack"))
    print("="*60)
    
    report = manager.get_status_report()
    print(f"\nStatus Report Generated: {json.dumps(report, indent=2)}")
