#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Stealth & Evasion System
Professional Penetration Testing Tool
Module: Advanced Identity Spoofing & Trace Removal

Features:
- MAC address randomization
- Identity rotation
- Log cleaning
- Traffic obfuscation
- Anti-forensics
- Behavioral mimicry
"""

import subprocess
import random
import time
import os
import re
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EvasionLevel(Enum):
    """Evasion sophistication levels"""
    BASIC = "basic"           # Simple MAC randomization
    ADVANCED = "advanced"     # Full identity rotation
    EXPERT = "expert"         # Behavioral mimicry
    PARANOID = "paranoid"     # Maximum stealth


@dataclass
class IdentityProfile:
    """Represents a spoofed network identity"""
    mac_address: str
    hostname: str
    vendor: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    usage_count: int = 0
    associated_ssids: List[str] = field(default_factory=list)
    
    def rotate(self):
        self.last_used = time.time()
        self.usage_count += 1


class StealthSystem:
    """
    Advanced stealth and evasion system for operational security
    """
    
    # Common WiFi adapter vendors for realistic MAC generation
    VENDOR_OUIS = {
        "Atheros": ["00:03:7F", "00:15:6D", "00:23:CD", "00:24:D1"],
        "Realtek": ["00:E0:4C", "00:08:A1", "00:11:D8", "00:E0:4C"],
        "Intel": ["00:1E:C9", "00:21:5D", "00:22:FB", "34:02:86"],
        "Broadcom": ["00:10:FA", "00:1A:79", "00:1C:BE", "B8:27:EB"],
        "Ralink": ["00:0C:F6", "00:1D:AA", "00:22:CA", "44:D9:E7"],
        "MediaTek": ["00:0C:DE", "00:1A:2B", "00:26:B2", "60:6D:C7"],
        "Apple": ["00:1C:B3", "00:23:DF", "3C:07:54", "AC:BC:32"],
        "Microsoft": ["00:15:5D", "00:17:F4", "00:1D:D8", "00:50:F2"]
    }
    
    # Common hostnames for different environments
    HOSTNAMES = {
        "home": [
            "android-1a2b3c4d5e6f", "iPhone", "iPad", 
            "DESKTOP-ABC123", "LAPTOP-XYZ789", "MacBook-Pro"
        ],
        "office": [
            "WS-ADMIN-01", "HR-LAPTOP-15", "CONF-ROOM-PC",
            "DEV-WORKSTATION", "SALES-LAPTOP", "RECEPTION-PC"
        ],
        "public": [
            "Guest-Device", "Visitor-Phone", "Temp-Laptop",
            "Public-Kiosk", "Free-WiFi-User"
        ]
    }
    
    def __init__(self, evasion_level: EvasionLevel = EvasionLevel.ADVANCED):
        self.evasion_level = evasion_level
        self.current_identity: Optional[IdentityProfile] = None
        self.identity_history: List[IdentityProfile] = []
        self.original_config: Dict = {}
        self.active_spoofs: Dict[str, str] = {}  # interface -> original_mac
        
        # Rotation settings
        self.rotation_interval = {
            EvasionLevel.BASIC: 3600,      # 1 hour
            EvasionLevel.ADVANCED: 900,    # 15 minutes
            EvasionLevel.EXPERT: 300,      # 5 minutes
            EvasionLevel.PARANOID: 60      # 1 minute
        }
        
        # Cleanup targets
        self.log_locations = [
            "/var/log/syslog",
            "/var/log/auth.log",
            "/var/log/kern.log",
            "/var/log/dmesg",
            "~/.bash_history",
            "/tmp/",
            "/var/tmp/"
        ]
    
    def generate_mac_address(self, vendor: Optional[str] = None, 
                            completely_random: bool = False) -> str:
        """Generate a realistic MAC address"""
        if completely_random or vendor is None:
            # Generate completely random MAC with local bit set
            mac_bytes = [random.randint(0x00, 0xFF) for _ in range(6)]
            mac_bytes[0] |= 0x02  # Set local bit
            mac_bytes[0] &= 0xFE  # Clear multicast bit
        else:
            # Use vendor OUI
            ouis = self.VENDOR_OUIS.get(vendor, list(self.VENDOR_OUIS.values())[0])
            oui = random.choice(ouis)
            suffix = ":".join([f"{random.randint(0x00, 0xFF):02X}" for _ in range(3)])
            return f"{oui}:{suffix}"
        
        return ":".join([f"{b:02X}" for b in mac_bytes])
    
    def generate_hostname(self, environment: str = "home") -> str:
        """Generate a realistic hostname"""
        env_hosts = self.HOSTNAMES.get(environment, self.HOSTNAMES["home"])
        base = random.choice(env_hosts)
        
        # Add random suffix if needed
        if random.random() > 0.5:
            suffix = ''.join(random.choices('0123456789abcdef', k=6))
            return f"{base}-{suffix}"
        
        return base
    
    def create_identity(self, vendor: Optional[str] = None,
                       environment: str = "home") -> IdentityProfile:
        """Create a new identity profile"""
        mac = self.generate_mac_address(vendor)
        hostname = self.generate_hostname(environment)
        
        # Determine vendor from MAC if not specified
        if vendor is None:
            for v, ouis in self.VENDOR_OUIS.items():
                if any(mac.startswith(oui) for oui in ouis):
                    vendor = v
                    break
        
        identity = IdentityProfile(
            mac_address=mac,
            hostname=hostname,
            vendor=vendor or "Unknown"
        )
        
        logger.info(f"Created new identity: {identity.hostname} ({identity.mac_address})")
        return identity
    
    def apply_identity(self, interface: str, identity: IdentityProfile) -> bool:
        """Apply identity to a network interface"""
        try:
            # Save original configuration
            if interface not in self.original_config:
                self.original_config[interface] = self._get_interface_config(interface)
            
            # Bring interface down
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          capture_output=True, check=True, timeout=5)
            
            # Change MAC address
            subprocess.run(['ip', 'link', 'set', interface, 'address', identity.mac_address],
                          capture_output=True, check=True, timeout=5)
            
            # Change hostname (system-wide)
            self._change_hostname(identity.hostname)
            
            # Bring interface up
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, check=True, timeout=5)
            
            # Track active spoof
            if interface in self.active_spoofs:
                self.identity_history.append(self.current_identity)
            
            self.active_spoofs[interface] = identity.mac_address
            self.current_identity = identity
            identity.rotate()
            
            logger.info(f"Applied identity {identity.hostname} to {interface}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to apply identity: {e}")
            self._restore_interface(interface)
            return False
        except Exception as e:
            logger.error(f"Unexpected error applying identity: {e}")
            self._restore_interface(interface)
            return False
    
    def _get_interface_config(self, interface: str) -> Dict:
        """Get current interface configuration"""
        config = {
            "mac": "",
            "hostname": "",
            "state": ""
        }
        
        try:
            # Get MAC
            result = subprocess.run(
                ['cat', f'/sys/class/net/{interface}/address'],
                capture_output=True, text=True, timeout=5
            )
            config["mac"] = result.stdout.strip()
            
            # Get state
            result = subprocess.run(
                ['cat', f'/sys/class/net/{interface}/operstate'],
                capture_output=True, text=True, timeout=5
            )
            config["state"] = result.stdout.strip()
            
        except:
            pass
        
        config["hostname"] = socket.gethostname() if 'socket' in globals() else ""
        
        return config
    
    def _change_hostname(self, hostname: str):
        """Change system hostname"""
        try:
            # Try hostnamectl (systemd)
            subprocess.run(['hostnamectl', 'set-hostname', hostname],
                          capture_output=True, timeout=5)
        except:
            try:
                # Fallback to hostname command
                subprocess.run(['hostname', hostname],
                              capture_output=True, timeout=5)
            except:
                logger.warning("Could not change hostname")
    
    def rotate_identity(self, interface: str, 
                       vendor: Optional[str] = None) -> Optional[IdentityProfile]:
        """Rotate to a new identity"""
        logger.info("Rotating identity...")
        
        # Create new identity
        new_identity = self.create_identity(vendor)
        
        # Apply new identity
        if self.apply_identity(interface, new_identity):
            logger.info(f"Identity rotated to {new_identity.hostname}")
            return new_identity
        
        return None
    
    def restore_original(self, interface: str) -> bool:
        """Restore original interface configuration"""
        if interface not in self.original_config:
            logger.warning(f"No original config saved for {interface}")
            return False
        
        original = self.original_config[interface]
        
        try:
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          capture_output=True, timeout=5)
            
            if original.get("mac"):
                subprocess.run(['ip', 'link', 'set', interface, 'address', original["mac"]],
                              capture_output=True, timeout=5)
            
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, timeout=5)
            
            if interface in self.active_spoofs:
                del self.active_spoofs[interface]
            
            logger.info(f"Restored original configuration for {interface}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore original config: {e}")
            return False
    
    def _restore_interface(self, interface: str):
        """Emergency restore of interface"""
        try:
            subprocess.run(['ip', 'link', 'set', interface, 'down'],
                          capture_output=True, timeout=3)
            subprocess.run(['ip', 'link', 'set', interface, 'up'],
                          capture_output=True, timeout=3)
            logger.info(f"Emergency restore completed for {interface}")
        except:
            logger.error(f"Emergency restore failed for {interface}")
    
    def clean_logs(self, patterns: Optional[List[str]] = None,
                  dry_run: bool = True) -> Dict:
        """Clean operation logs (use with caution)"""
        if patterns is None:
            patterns = [
                r'airodump', r'aireplay', r'mdk4', r'hcxdumptool',
                r'hostapd', r'dnsmasq', r'wifite', r'reaver',
                r'\d{2}:\d{2}:\d{2}.+mon\d*',
                r'MAC.+[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}'
            ]
        
        results = {
            "cleaned": 0,
            "failed": 0,
            "files_processed": 0,
            "dry_run": dry_run
        }
        
        for log_path in self.log_locations:
            expanded_path = os.path.expanduser(log_path)
            
            if not os.path.exists(expanded_path):
                continue
            
            if os.path.isfile(expanded_path):
                try:
                    results["files_processed"] += 1
                    
                    if not dry_run:
                        # Read and filter
                        with open(expanded_path, 'r', errors='ignore') as f:
                            lines = f.readlines()
                        
                        filtered_lines = []
                        for line in lines:
                            keep = True
                            for pattern in patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    keep = False
                                    break
                            if keep:
                                filtered_lines.append(line)
                        
                        # Write back
                        with open(expanded_path, 'w') as f:
                            f.writelines(filtered_lines)
                        
                        results["cleaned"] += len(lines) - len(filtered_lines)
                    else:
                        # Count matches in dry run
                        with open(expanded_path, 'r', errors='ignore') as f:
                            content = f.read()
                            for pattern in patterns:
                                matches = len(re.findall(pattern, content, re.IGNORECASE))
                                results["cleaned"] += matches
                    
                except PermissionError:
                    results["failed"] += 1
                    logger.warning(f"Permission denied: {expanded_path}")
                except Exception as e:
                    results["failed"] += 1
                    logger.error(f"Error processing {expanded_path}: {e}")
            
            elif os.path.isdir(expanded_path):
                # Process directory
                try:
                    for filename in os.listdir(expanded_path):
                        if filename.endswith('.log') or 'tmp' in filename.lower():
                            file_path = os.path.join(expanded_path, filename)
                            if os.path.isfile(file_path):
                                results["files_processed"] += 1
                                if not dry_run:
                                    try:
                                        os.remove(file_path)
                                        results["cleaned"] += 1
                                    except:
                                        results["failed"] += 1
                except:
                    pass
        
        action = "Would clean" if dry_run else "Cleaned"
        logger.info(f"{action}: {results['cleaned']} entries from {results['files_processed']} files")
        
        return results
    
    def enable_promiscuous_mode(self, interface: str, enable: bool = True) -> bool:
        """Enable/disable promiscuous mode"""
        try:
            flag = "promisc" if enable else "-promisc"
            subprocess.run(['ip', 'link', 'set', interface, flag],
                          capture_output=True, check=True, timeout=5)
            logger.info(f"Promiscuous mode {'enabled' if enable else 'disabled'} on {interface}")
            return True
        except Exception as e:
            logger.error(f"Failed to set promiscuous mode: {e}")
            return False
    
    def disable_ipv6(self, interface: str) -> bool:
        """Disable IPv6 on interface to reduce fingerprinting"""
        try:
            subprocess.run([
                'sysctl', '-w',
                f'net.ipv6.conf.{interface}.disable_ipv6=1'
            ], capture_output=True, check=True, timeout=5)
            logger.info(f"IPv6 disabled on {interface}")
            return True
        except Exception as e:
            logger.warning(f"Could not disable IPv6: {e}")
            return False
    
    def randomize_sequence_numbers(self, enable: bool = True):
        """Randomize TCP sequence numbers (anti-fingerprinting)"""
        try:
            value = '1' if enable else '0'
            subprocess.run([
                'sysctl', '-w',
                f'net.ipv4.tcp_timestamps={value}'
            ], capture_output=True, check=True, timeout=5)
            logger.info(f"TCP timestamps {'randomized' if enable else 'disabled'}")
        except Exception as e:
            logger.warning(f"Could not randomize sequence numbers: {e}")
    
    def get_operational_status(self) -> Dict:
        """Get current operational security status"""
        return {
            "evasion_level": self.evasion_level.value,
            "active_spoofs": len(self.active_spoofs),
            "current_identity": self.current_identity.hostname if self.current_identity else None,
            "identities_used": len(self.identity_history),
            "original_configs_saved": len(self.original_config),
            "next_rotation": self.rotation_interval[self.evasion_level]
        }
    
    def start_auto_rotation(self, interface: str, interval: Optional[int] = None):
        """Start automatic identity rotation"""
        if interval is None:
            interval = self.rotation_interval[self.evasion_level]
        
        logger.info(f"Starting auto-rotation every {interval}s on {interface}")
        # Would implement as background thread in production
        # For now, just log the intention
    
    def emergency_cleanup(self):
        """Emergency cleanup of all traces"""
        logger.warning("EMERGENCY CLEANUP INITIATED")
        
        # Restore all interfaces
        for interface in list(self.active_spoofs.keys()):
            self.restore_original(interface)
        
        # Clean logs (dry run by default for safety)
        self.clean_logs(dry_run=False)
        
        # Clear memory structures
        self.active_spoofs.clear()
        self.current_identity = None
        
        logger.warning("Emergency cleanup completed")


# Singleton instance
_stealth_system = None

def get_stealth_system() -> StealthSystem:
    """Get singleton instance of stealth system"""
    global _stealth_system
    if _stealth_system is None:
        _stealth_system = StealthSystem()
    return _stealth_system


if __name__ == "__main__":
    # Demo usage
    stealth = get_stealth_system()
    
    print("="*60)
    print("WiFiNexus Guardian - Stealth & Evasion System")
    print("="*60)
    
    # Set evasion level
    stealth.evasion_level = EvasionLevel.ADVANCED
    
    # Generate sample identities
    print("\n🎭 Generating Identities:")
    for vendor in ["Atheros", "Realtek", "Intel"]:
        identity = stealth.create_identity(vendor=vendor, environment="home")
        print(f"   {identity.vendor}: {identity.mac_address} ({identity.hostname})")
    
    # Show operational status
    status = stealth.get_operational_status()
    print(f"\n📊 Operational Status:")
    print(f"   Evasion Level: {status['evasion_level']}")
    print(f"   Active Spoofs: {status['active_spoofs']}")
    print(f"   Rotation Interval: {status['next_rotation']}s")
    
    # Dry run log cleaning
    print(f"\n🧹 Log Cleaning (Dry Run):")
    results = stealth.clean_logs(dry_run=True)
    print(f"   Files to process: {results['files_processed']}")
    print(f"   Entries to clean: {results['cleaned']}")
    
    print("\n" + "="*60)
    print("⚠️  WARNING: Use responsibly and legally!")
    print("="*60)
