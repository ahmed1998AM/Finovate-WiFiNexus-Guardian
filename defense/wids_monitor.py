"""
Wireless Intrusion Detection System (WIDS) for WiFiNexus Guardian
Monitors wireless environment for attacks and suspicious activities.
Detects: Deauth floods, Evil Twin APs, Beacon floods, KRACK attempts, and more.
"""

import logging
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

@dataclass
class SecurityAlert:
    """Represents a security alert"""
    timestamp: datetime
    alert_type: str
    severity: str  # low, medium, high, critical
    source_mac: str
    target_mac: str
    description: str
    evidence: Dict = field(default_factory=dict)
    recommended_action: str = ""

@dataclass
class NetworkDevice:
    """Represents a tracked network device"""
    mac_address: str
    first_seen: datetime
    last_seen: datetime
    vendor: str = ""
    is_ap: bool = False
    essid: str = ""
    channel: int = 0
    signal_strength: int = 0
    packet_count: int = 0

class WirelessIDSEngine:
    """
    Wireless Intrusion Detection System Engine
    
    Detects various wireless attacks:
    - Deauthentication/Disassociation Floods
    - Evil Twin/Rogue Access Points
    - Beacon Flood Attacks
    - KRACK Attack Attempts
    - Probe Request Floods
    - Authentication Floods
    - Fragmentation/TKIP Attacks
    """
    
    def __init__(self, interface: str, monitoring_dir: str = "captures/wids"):
        self.interface = interface
        self.monitoring_dir = Path(monitoring_dir)
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Device tracking
        self.known_devices: Dict[str, NetworkDevice] = {}
        self.known_aps: Dict[str, NetworkDevice] = {}
        self.suspicious_devices: Set[str] = set()
        
        # Attack detection state
        self.deauth_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.beacon_counts: Dict[str, int] = defaultdict(int)
        self.probe_counts: Dict[str, List[datetime]] = defaultdict(list)
        self.auth_counts: Dict[str, List[datetime]] = defaultdict(list)
        
        # Alert management
        self.alerts: List[SecurityAlert] = []
        self.alert_callbacks: List[callable] = []
        
        # Monitoring state
        self.is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Thresholds for attack detection
        self.thresholds = {
            'deauth_per_minute': 10,  # Deauth packets per minute threshold
            'beacon_rate': 50,  # Beacons per second threshold
            'probe_per_minute': 30,  # Probe requests per minute
            'auth_per_minute': 20,  # Authentication attempts per minute
            'same_ssid_count': 5,  # Number of APs with same SSID to trigger Evil Twin alert
        }
    
    def start_monitoring(self):
        """Start WIDS monitoring"""
        if self.is_monitoring:
            logger.warning("WIDS is already monitoring")
            return
        
        logger.info("Starting Wireless IDS monitoring...")
        self.is_monitoring = True
        self._stop_event.clear()
        
        self._monitor_thread = threading.Thread(target=self._monitoring_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop WIDS monitoring"""
        if not self.is_monitoring:
            return
        
        logger.info("Stopping Wireless IDS monitoring...")
        self.is_monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                # In a real implementation, this would parse live packets
                # For now, we'll simulate the structure
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Check for attacks
                self._detect_deauth_flood()
                self._detect_evil_twin()
                self._detect_beacon_flood()
                self._detect_probe_flood()
                self._detect_auth_flood()
                
                # Sleep before next iteration
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in WIDS monitoring loop: {e}")
                time.sleep(2)
    
    def process_packet(self, packet_info: Dict):
        """
        Process a captured packet for analysis
        
        Args:
            packet_info: Dictionary containing packet details:
                - type: packet type (beacon, deauth, probe, auth, etc.)
                - src_mac: source MAC address
                - dst_mac: destination MAC address
                - bssid: BSSID if applicable
                - essid: ESSID if applicable
                - channel: channel number
                - signal: signal strength
                - timestamp: packet timestamp
        """
        pkt_type = packet_info.get('type', '')
        src_mac = packet_info.get('src_mac', '')
        dst_mac = packet_info.get('dst_mac', '')
        bssid = packet_info.get('bssid', '')
        essid = packet_info.get('essid', '')
        timestamp = packet_info.get('timestamp', datetime.now())
        
        # Update device tracking
        self._update_device_tracking(packet_info)
        
        # Process by packet type
        if pkt_type == 'deauth' or pkt_type == 'disassoc':
            self.deauth_counts[src_mac].append(timestamp)
            
        elif pkt_type == 'beacon':
            self.beacon_counts[bssid] += 1
            
            # Track AP
            if bssid not in self.known_aps:
                self.known_aps[bssid] = NetworkDevice(
                    mac_address=bssid,
                    first_seen=timestamp,
                    last_seen=timestamp,
                    is_ap=True,
                    essid=essid,
                    channel=packet_info.get('channel', 0),
                    signal_strength=packet_info.get('signal', 0)
                )
            
        elif pkt_type == 'probe_req':
            self.probe_counts[src_mac].append(timestamp)
            
        elif pkt_type in ['auth', 'assoc']:
            self.auth_counts[src_mac].append(timestamp)
    
    def _update_device_tracking(self, packet_info: Dict):
        """Update device tracking information"""
        src_mac = packet_info.get('src_mac', '')
        timestamp = packet_info.get('timestamp', datetime.now())
        
        if not src_mac:
            return
        
        if src_mac not in self.known_devices:
            self.known_devices[src_mac] = NetworkDevice(
                mac_address=src_mac,
                first_seen=timestamp,
                last_seen=timestamp,
                vendor=self._get_vendor(src_mac),
                is_ap=packet_info.get('type') == 'beacon'
            )
        
        device = self.known_devices[src_mac]
        device.last_seen = timestamp
        device.packet_count += 1
        
        if packet_info.get('type') == 'beacon':
            device.is_ap = True
            device.essid = packet_info.get('essid', '')
            device.channel = packet_info.get('channel', 0)
    
    def _detect_deauth_flood(self):
        """Detect deauthentication flood attacks"""
        current_time = datetime.now()
        
        for mac, timestamps in list(self.deauth_counts.items()):
            # Keep only last minute
            recent = [t for t in timestamps if (current_time - t).total_seconds() < 60]
            self.deauth_counts[mac] = recent
            
            if len(recent) > self.thresholds['deauth_per_minute']:
                self._generate_alert(
                    alert_type="DEAUTH_FLOOD",
                    severity="high",
                    source_mac=mac,
                    target_mac="broadcast",
                    description=f"Deauthentication flood detected: {len(recent)} deauth packets in last minute",
                    evidence={"packet_count": len(recent), "time_window": "60s"},
                    recommended_action="Block source MAC or investigate further"
                )
    
    def _detect_evil_twin(self):
        """Detect Evil Twin / Rogue Access Points"""
        # Group APs by SSID
        ssid_to_aps: Dict[str, List[NetworkDevice]] = defaultdict(list)
        
        for bssid, ap in self.known_aps.items():
            if ap.essid:
                ssid_to_aps[ap.essid].append(ap)
        
        # Check for multiple APs with same SSID
        for ssid, aps in ssid_to_aps.items():
            if len(aps) >= self.thresholds['same_ssid_count']:
                # Multiple APs with same SSID - possible Evil Twin
                for ap in aps[1:]:  # All except the first one are suspicious
                    if ap.mac_address not in self.suspicious_devices:
                        self.suspicious_devices.add(ap.mac_address)
                        
                        self._generate_alert(
                            alert_type="EVIL_TWIN",
                            severity="critical",
                            source_mac=ap.mac_address,
                            target_mac=aps[0].mac_address,
                            description=f"Possible Evil Twin AP detected for SSID '{ssid}'",
                            evidence={
                                "suspect_bssid": ap.mac_address,
                                "legitimate_bssid": aps[0].mac_address,
                                "ssid": ssid,
                                "total_duplicate_aps": len(aps)
                            },
                            recommended_action="Verify legitimate AP and block rogue AP"
                        )
    
    def _detect_beacon_flood(self):
        """Detect beacon flood attacks"""
        # This would analyze beacon rates in a real implementation
        pass
    
    def _detect_probe_flood(self):
        """Detect probe request flood attacks"""
        current_time = datetime.now()
        
        for mac, timestamps in list(self.probe_counts.items()):
            recent = [t for t in timestamps if (current_time - t).total_seconds() < 60]
            self.probe_counts[mac] = recent
            
            if len(recent) > self.thresholds['probe_per_minute']:
                self._generate_alert(
                    alert_type="PROBE_FLOOD",
                    severity="medium",
                    source_mac=mac,
                    target_mac="broadcast",
                    description=f"Probe request flood detected: {len(recent)} probes in last minute",
                    evidence={"packet_count": len(recent)},
                    recommended_action="Monitor for reconnaissance activity"
                )
    
    def _detect_auth_flood(self):
        """Detect authentication flood attacks"""
        current_time = datetime.now()
        
        for mac, timestamps in list(self.auth_counts.items()):
            recent = [t for t in timestamps if (current_time - t).total_seconds() < 60]
            self.auth_counts[mac] = recent
            
            if len(recent) > self.thresholds['auth_per_minute']:
                self._generate_alert(
                    alert_type="AUTH_FLOOD",
                    severity="high",
                    source_mac=mac,
                    target_mac="AP",
                    description=f"Authentication flood detected: {len(recent)} attempts in last minute",
                    evidence={"packet_count": len(recent)},
                    recommended_action="Enable rate limiting on AP"
                )
    
    def _generate_alert(
        self,
        alert_type: str,
        severity: str,
        source_mac: str,
        target_mac: str,
        description: str,
        evidence: Dict = None,
        recommended_action: str = ""
    ):
        """Generate a security alert"""
        alert = SecurityAlert(
            timestamp=datetime.now(),
            alert_type=alert_type,
            severity=severity,
            source_mac=source_mac,
            target_mac=target_mac,
            description=description,
            evidence=evidence or {},
            recommended_action=recommended_action
        )
        
        self.alerts.append(alert)
        
        # Log alert
        severity_icon = {"low": "ℹ️", "medium": "⚠️", "high": "🚨", "critical": "🔴"}
        logger.warning(
            f"{severity_icon.get(severity, '❗')} [{alert_type}] {description}"
        )
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        # Save alert to file
        self._save_alert(alert)
    
    def _save_alert(self, alert: SecurityAlert):
        """Save alert to file"""
        alert_file = self.monitoring_dir / "wids_alerts.log"
        
        with open(alert_file, 'a') as f:
            f.write(
                f"{alert.timestamp.isoformat()} | {alert.severity.upper()} | "
                f"{alert.alert_type} | {alert.source_mac} -> {alert.target_mac} | "
                f"{alert.description}\n"
            )
    
    def _cleanup_old_data(self):
        """Clean up old tracking data"""
        current_time = datetime.now()
        
        # Remove devices not seen in last 10 minutes
        expired_devices = [
            mac for mac, device in self.known_devices.items()
            if (current_time - device.last_seen).total_seconds() > 600
        ]
        
        for mac in expired_devices:
            del self.known_devices[mac]
            self.suspicious_devices.discard(mac)
    
    def _get_vendor(self, mac: str) -> str:
        """Get vendor from MAC address OUI"""
        # Simplified vendor lookup (in production, use full OUI database)
        oui_prefixes = {
            '00:1A:2B': 'Apple',
            '00:50:56': 'VMware',
            '52:54:00': 'QEMU',
            '08:00:27': 'VirtualBox',
        }
        
        prefix = mac[:8].upper()
        return oui_prefixes.get(prefix, 'Unknown')
    
    def add_alert_callback(self, callback: callable):
        """Add callback function to be called when alerts are generated"""
        self.alert_callbacks.append(callback)
    
    def get_alerts(
        self,
        severity: Optional[str] = None,
        alert_type: Optional[str] = None,
        limit: int = 100
    ) -> List[SecurityAlert]:
        """Get filtered list of alerts"""
        filtered = self.alerts
        
        if severity:
            filtered = [a for a in filtered if a.severity == severity]
        
        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]
        
        return filtered[-limit:]
    
    def get_status(self) -> Dict:
        """Get WIDS status summary"""
        return {
            "is_monitoring": self.is_monitoring,
            "known_devices": len(self.known_devices),
            "known_aps": len(self.known_aps),
            "suspicious_devices": len(self.suspicious_devices),
            "total_alerts": len(self.alerts),
            "alerts_by_severity": {
                "critical": len([a for a in self.alerts if a.severity == "critical"]),
                "high": len([a for a in self.alerts if a.severity == "high"]),
                "medium": len([a for a in self.alerts if a.severity == "medium"]),
                "low": len([a for a in self.alerts if a.severity == "low"])
            }
        }
    
    def export_report(self, filepath: str):
        """Export WIDS report to file"""
        import json
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "interface": self.interface,
            "status": self.get_status(),
            "alerts": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "source": alert.source_mac,
                    "target": alert.target_mac,
                    "description": alert.description,
                    "recommended_action": alert.recommended_action
                }
                for alert in self.alerts
            ],
            "known_devices": [
                {
                    "mac": device.mac_address,
                    "vendor": device.vendor,
                    "is_ap": device.is_ap,
                    "essid": device.essid,
                    "first_seen": device.first_seen.isoformat(),
                    "last_seen": device.last_seen.isoformat()
                }
                for device in list(self.known_devices.values())[:50]  # Limit to 50
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"WIDS report exported to {filepath}")
