"""
Packet Analyzer Pro - Advanced Packet Analysis Module
Deep packet inspection, protocol analysis, traffic pattern detection
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import subprocess
import re
import json
import platform
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class PacketInfo:
    """Represents a single packet"""
    
    def __init__(self):
        self.timestamp = None
        self.source_mac = None
        self.dest_mac = None
        self.bssid = None
        self.packet_type = None  # Management, Control, Data
        self.subtype = None
        self.frame_control = None
        self.duration = None
        self.sequence_number = None
        self.fragment_number = None
        self.payload_size = 0
        self.signal_strength = None
        self.channel = None
        self.frequency = None
        self.protocol = None  # 802.11a/b/g/n/ac/ax
        self.encrypted = False
        self.encryption_type = None
        self.eapol_key = False
        
    def to_dict(self) -> Dict:
        return {
            'timestamp': str(self.timestamp),
            'source_mac': self.source_mac,
            'dest_mac': self.dest_mac,
            'bssid': self.bssid,
            'packet_type': self.packet_type,
            'subtype': self.subtype,
            'payload_size': self.payload_size,
            'signal_strength': self.signal_strength,
            'channel': self.channel,
            'encrypted': self.encrypted,
            'encryption_type': self.encryption_type,
            'eapol_key': self.eapol_key
        }


class PacketAnalyzerPro:
    """
    Professional Packet Analyzer
    - Deep packet inspection
    - Protocol analysis
    - Traffic pattern detection
    - Anomaly detection
    - Real-time monitoring
    """
    
    def __init__(self, interface: str = None):
        self.platform = platform.system()
        self.interface = interface or self._detect_interface()
        self.capture_file = None
        self.packets: List[PacketInfo] = []
        self.running = False
        
        # Statistics
        self.total_packets = 0
        self.management_packets = 0
        self.control_packets = 0
        self.data_packets = 0
        self.eapol_packets = 0
        self.deauth_packets = 0
        self.beacon_packets = 0
        self.probe_packets = 0
        
        # Pattern detection
        self.mac_addresses = set()
        self.ssids = set()
        self.channels = set()
        self.anomalies = []
        
        # Time tracking
        self.analysis_start_time = None
        self.analysis_end_time = None
        
        # Capture directory
        self.capture_dir = Path("captures")
        self.capture_dir.mkdir(exist_ok=True)
        
    def _detect_interface(self) -> str:
        """Detect available wireless interface"""
        if self.platform == "Linux":
            try:
                result = subprocess.run(
                    ["iwconfig"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                for line in result.stdout.split('\n'):
                    if 'IEEE 802.11' in line:
                        return line.split()[0]
            except:
                pass
            return "wlan0"
        elif self.platform == "Windows":
            return "Wi-Fi"
        elif self.platform == "Darwin":
            return "en0"
        return "wlan0"
    
    def start_live_capture(self, duration: int = 60, filter_bpf: str = None) -> bool:
        """
        Start live packet capture
        
        Args:
            duration: Capture duration in seconds
            filter_bpf: BPF filter string (optional)
            
        Returns:
            True if capture started successfully
        """
        print(f"\n📡 Starting live packet capture on {self.interface}...")
        print(f"Duration: {duration}s")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.capture_file = str(self.capture_dir / f"live_capture_{timestamp}.pcap")
        
        self.running = True
        self.analysis_start_time = datetime.now()
        self.packets = []
        self._reset_statistics()
        
        try:
            # Build tcpdump/tshark command
            if self.platform == "Linux":
                cmd = ["sudo", "tcpdump", "-i", self.interface, "-w", self.capture_file]
            elif self.platform == "Windows":
                cmd = ["tshark", "-i", self.interface, "-w", self.capture_file]
            else:
                cmd = ["sudo", "tcpdump", "-i", self.interface, "-w", self.capture_file]
            
            if filter_bpf:
                cmd.extend(["-f", filter_bpf])
            
            cmd.extend(["-c", "10000"])  # Limit packets
            
            self.capture_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Schedule stop
            import threading
            def stop_after():
                import time
                time.sleep(duration)
                self.stop_live_capture()
            
            threading.Thread(target=stop_after, daemon=True).start()
            
            print(f"✓ Capture started: {self.capture_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error starting capture: {e}")
            return False
    
    def stop_live_capture(self):
        """Stop live capture"""
        self.running = False
        self.analysis_end_time = datetime.now()
        
        if hasattr(self, 'capture_process') and self.capture_process:
            try:
                self.capture_process.terminate()
                self.capture_process.wait(timeout=5)
                print("✓ Capture stopped")
            except:
                try:
                    self.capture_process.kill()
                except:
                    pass
    
    def analyze_pcap(self, pcap_file: str) -> Dict:
        """
        Analyze pcap file
        
        Args:
            pcap_file: Path to pcap file
            
        Returns:
            Analysis results dictionary
        """
        print(f"\n🔍 Analyzing capture file: {pcap_file}")
        
        if not Path(pcap_file).exists():
            print(f"❌ File not found: {pcap_file}")
            return {}
        
        self.capture_file = pcap_file
        self._reset_statistics()
        self.analysis_start_time = datetime.now()
        
        # Use tshark for analysis
        try:
            # Get basic statistics
            self._analyze_with_tshark(pcap_file)
            
            # Detect anomalies
            self._detect_anomalies()
            
            # Generate report
            results = self._generate_analysis_report()
            
            self.analysis_end_time = datetime.now()
            
            return results
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {}
    
    def _reset_statistics(self):
        """Reset all statistics"""
        self.total_packets = 0
        self.management_packets = 0
        self.control_packets = 0
        self.data_packets = 0
        self.eapol_packets = 0
        self.deauth_packets = 0
        self.beacon_packets = 0
        self.probe_packets = 0
        self.mac_addresses = set()
        self.ssids = set()
        self.channels = set()
        self.anomalies = []
    
    def _analyze_with_tshark(self, pcap_file: str):
        """Analyze pcap using tshark"""
        try:
            # Get packet count
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.total_packets = len(result.stdout.strip().split('\n'))
            
            # Get management frames
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.type == 0", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.management_packets = len(result.stdout.strip().split('\n'))
            
            # Get control frames
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.type == 1", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.control_packets = len(result.stdout.strip().split('\n'))
            
            # Get data frames
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.type == 2", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            self.data_packets = len(result.stdout.strip().split('\n'))
            
            # Get EAPOL packets
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "eapol", "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            eapol_lines = [l for l in result.stdout.strip().split('\n') if l]
            self.eapol_packets = len(eapol_lines)
            
            # Get deauthentication packets
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.subtype == 0x0c", "-T", "fields", 
                 "-e", "wlan.sa", "-e", "wlan.da", "-e", "wlan.reason_code"],
                capture_output=True,
                text=True,
                timeout=60
            )
            deauth_lines = [l for l in result.stdout.strip().split('\n') if l]
            self.deauth_packets = len(deauth_lines)
            
            # Get beacon frames
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.subtype == 0x08", "-T", "fields", 
                 "-e", "wlan_mgt.ssid", "-e", "wlan.sa"],
                capture_output=True,
                text=True,
                timeout=60
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        ssid = parts[0].strip()
                        mac = parts[1].strip()
                        if ssid:
                            self.ssids.add(ssid)
                        if mac:
                            self.mac_addresses.add(mac)
                    self.beacon_packets += 1
            
            # Get probe requests
            result = subprocess.run(
                ["tshark", "-r", pcap_file, "-Y", "wlan.fc.subtype == 0x04", "-T", "fields", 
                 "-e", "wlan_mgt.ssid", "-e", "wlan.sa"],
                capture_output=True,
                text=True,
                timeout=60
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    self.probe_packets += 1
                    parts = line.split('\t')
                    if len(parts) >= 1 and parts[0].strip():
                        self.ssids.add(parts[0].strip())
            
            print(f"✓ Analysis complete")
            print(f"  Total Packets: {self.total_packets}")
            print(f"  Management: {self.management_packets}")
            print(f"  Control: {self.control_packets}")
            print(f"  Data: {self.data_packets}")
            print(f"  EAPOL: {self.eapol_packets}")
            print(f"  Deauth: {self.deauth_packets}")
            print(f"  Beacons: {self.beacon_packets}")
            print(f"  Probes: {self.probe_packets}")
            
        except Exception as e:
            print(f"TShark analysis error: {e}")
    
    def _detect_anomalies(self):
        """Detect network anomalies"""
        self.anomalies = []
        
        # High deauth rate
        if self.total_packets > 0:
            deauth_ratio = self.deauth_packets / self.total_packets
            if deauth_ratio > 0.1:  # More than 10% deauth packets
                self.anomalies.append({
                    'type': 'HIGH_DEAUTH_RATE',
                    'severity': 'HIGH',
                    'description': f'High deauthentication rate detected ({deauth_ratio*100:.1f}%)',
                    'recommendation': 'Possible deauth attack in progress'
                })
        
        # Multiple EAPOL without association
        if self.eapol_packets > 20:
            self.anomalies.append({
                'type': 'EXCESSIVE_EAPOL',
                'severity': 'MEDIUM',
                'description': f'Excessive EAPOL packets ({self.eapol_packets})',
                'recommendation': 'Possible handshake capture attempt'
            })
        
        # Many probe requests
        if self.probe_packets > 100:
            self.anomalies.append({
                'type': 'PROBE_FLOOD',
                'severity': 'LOW',
                'description': f'High number of probe requests ({self.probe_packets})',
                'recommendation': 'Possible network discovery or wardriving'
            })
        
        # Hidden SSIDs
        hidden_count = sum(1 for ssid in self.ssids if ssid == '' or ssid.startswith('\\x00'))
        if hidden_count > 3:
            self.anomalies.append({
                'type': 'MULTIPLE_HIDDEN_SSIDS',
                'severity': 'MEDIUM',
                'description': f'{hidden_count} hidden networks detected',
                'recommendation': 'Hidden networks may indicate suspicious activity'
            })
    
    def _generate_analysis_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        duration = 0
        if self.analysis_start_time and self.analysis_end_time:
            duration = (self.analysis_end_time - self.analysis_start_time).total_seconds()
        
        report = {
            'file': self.capture_file,
            'analysis_time': datetime.now().isoformat(),
            'duration_seconds': duration,
            'statistics': {
                'total_packets': self.total_packets,
                'management_packets': self.management_packets,
                'control_packets': self.control_packets,
                'data_packets': self.data_packets,
                'eapol_packets': self.eapol_packets,
                'deauth_packets': self.deauth_packets,
                'beacon_packets': self.beacon_packets,
                'probe_packets': self.probe_packets,
                'unique_macs': len(self.mac_addresses),
                'unique_ssids': len(self.ssids)
            },
            'networks_detected': list(self.ssids)[:20],  # First 20
            'mac_addresses': list(self.mac_addresses)[:20],  # First 20
            'anomalies': self.anomalies,
            'packets_per_second': self.total_packets / max(1, duration)
        }
        
        return report
    
    def export_analysis(self, results: Dict, format: str = 'json', filename: str = None) -> str:
        """Export analysis results"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"packet_analysis_{timestamp}.{format}"
        
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
        elif format == 'csv':
            # Export to CSV
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                for key, value in results.get('statistics', {}).items():
                    writer.writerow([key, value])
        
        print(f"✓ Analysis exported to {filename}")
        return filename
    
    def print_summary(self, results: Dict):
        """Print analysis summary"""
        print("\n" + "="*70)
        print("PACKET ANALYSIS SUMMARY")
        print("="*70)
        
        stats = results.get('statistics', {})
        print(f"\n📊 TRAFFIC STATISTICS:")
        print(f"  Total Packets:      {stats.get('total_packets', 0):,}")
        print(f"  Management Frames:  {stats.get('management_packets', 0):,}")
        print(f"  Control Frames:     {stats.get('control_packets', 0):,}")
        print(f"  Data Frames:        {stats.get('data_packets', 0):,}")
        
        print(f"\n🔐 SECURITY FRAMES:")
        print(f"  EAPOL Packets:      {stats.get('eapol_packets', 0)}")
        print(f"  Deauth Packets:     {stats.get('deauth_packets', 0)}")
        print(f"  Beacon Frames:      {stats.get('beacon_packets', 0)}")
        print(f"  Probe Requests:     {stats.get('probe_packets', 0)}")
        
        print(f"\n📡 NETWORKS & DEVICES:")
        print(f"  Unique SSIDs:       {stats.get('unique_ssids', 0)}")
        print(f"  Unique MACs:        {stats.get('unique_macs', 0)}")
        
        if results.get('anomalies'):
            print(f"\n⚠️ ANOMALIES DETECTED: {len(results['anomalies'])}")
            for anomaly in results['anomalies']:
                severity_icon = "🔴" if anomaly['severity'] == 'HIGH' else "🟡" if anomaly['severity'] == 'MEDIUM' else "🟢"
                print(f"  {severity_icon} [{anomaly['severity']}] {anomaly['type']}")
                print(f"      {anomaly['description']}")
        
        print("\n" + "="*70)


if __name__ == "__main__":
    print("="*70)
    print("WiFiNexus Guardian - Packet Analyzer Pro")
    print("="*70)
    
    analyzer = PacketAnalyzerPro()
    
    print(f"\nInterface: {analyzer.interface}")
    print(f"Platform: {analyzer.platform}")
    
    # Test with existing capture if available
    captures_dir = Path("captures")
    if captures_dir.exists():
        pcap_files = list(captures_dir.glob("*.pcap"))
        if pcap_files:
            print(f"\nFound {len(pcap_files)} capture file(s)")
            results = analyzer.analyze_pcap(str(pcap_files[0]))
            if results:
                analyzer.print_summary(results)
        else:
            print("\nNo capture files found")
    else:
        print("\nNo captures directory")
    
    print("\nReady for packet analysis operations")
