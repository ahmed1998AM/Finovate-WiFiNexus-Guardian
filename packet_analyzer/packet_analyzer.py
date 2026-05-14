"""
Packet Analyzer Module - Deep packet inspection and protocol analysis
Legal Use Only: Authorized network analysis and security auditing
"""

import subprocess
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class PacketAnalyzer:
    """
    Professional Packet Analyzer for deep network inspection
    Supports PCAP analysis, protocol detection, and traffic statistics
    """
    
    def __init__(self, interface: str = None):
        self.platform = "Linux"  # Default for container
        self.interface = interface or "eth0"
        self.capture_file = None
        self.analysis_results = {}
        self.packets = []
        self.stats = {
            "total_packets": 0,
            "tcp_packets": 0,
            "udp_packets": 0,
            "icmp_packets": 0,
            "dns_queries": 0,
            "http_requests": 0,
            "https_connections": 0
        }
        self.protocols = defaultdict(int)
        self.connections = set()
        self.dns_cache = {}
        
    def start_live_capture(self, interface: str = None, count: int = 100,
                          filter_expr: str = None) -> bool:
        """
        Start live packet capture
        
        Args:
            interface: Network interface to capture from
            count: Number of packets to capture
            filter_expr: BPF filter expression (e.g., "port 80", "host 192.168.1.1")
        """
        self.interface = interface or self.interface
        
        try:
            cmd = ["tcpdump", "-i", self.interface, "-c", str(count)]
            
            if filter_expr:
                cmd.extend(filter_expr.split())
            
            cmd.extend(["-w", "/tmp/live_capture.pcap"])
            
            print(f"Starting live capture on {self.interface}...")
            print(f"Filter: {filter_expr or 'none'}")
            print(f"Packets: {count}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.capture_file = "/tmp/live_capture.pcap"
                print(f"✓ Capture saved to {self.capture_file}")
                return True
            else:
                print(f"Capture failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Live capture error: {e}")
            return False
    
    def analyze_pcap(self, filepath: str) -> Dict:
        """
        Analyze a PCAP file for protocols, connections, and statistics
        
        Args:
            filepath: Path to PCAP file
        
        Returns:
            Analysis results dictionary
        """
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return {}
        
        print(f"\nAnalyzing: {filepath}")
        print("="*60)
        
        self.analysis_results = {
            "file": filepath,
            "size": os.path.getsize(filepath),
            "timestamp": datetime.now().isoformat(),
            "packets": [],
            "protocols": {},
            "connections": [],
            "dns_queries": [],
            "http_requests": [],
            "statistics": {}
        }
        
        # Reset stats
        self.stats = {k: 0 for k in self.stats}
        self.protocols = defaultdict(int)
        self.connections = set()
        
        # Use tshark for detailed analysis
        try:
            # Get packet count
            result = subprocess.run(
                ["tshark", "-r", filepath, "-T", "fields", "-e", "frame.number"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                packet_count = len(result.stdout.strip().split('\n'))
                self.stats["total_packets"] = packet_count
                print(f"Total Packets: {packet_count}")
            
            # Protocol distribution
            result = subprocess.run(
                ["tshark", "-r", filepath, "-q", "-z", "io,phs"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._parse_protocol_stats(result.stdout)
            
            # TCP connections
            result = subprocess.run(
                ["tshark", "-r", filepath, "-T", "fields", 
                 "-e", "ip.src", "-e", "ip.dst", "-e", "tcp.srcport", "-e", "tcp.dstport",
                 "-Y", "tcp"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._parse_connections(result.stdout)
            
            # DNS queries
            result = subprocess.run(
                ["tshark", "-r", filepath, "-T", "fields",
                 "-e", "dns.qry.name", "-e", "ip.dst",
                 "-Y", "dns.flags.response == 0"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._parse_dns(result.stdout)
            
            # HTTP requests
            result = subprocess.run(
                ["tshark", "-r", filepath, "-T", "fields",
                 "-e", "http.request.method", "-e", "http.host", "-e", "http.request.uri",
                 "-Y", "http.request"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._parse_http(result.stdout)
            
            # Build statistics
            self.analysis_results["statistics"] = dict(self.stats)
            self.analysis_results["protocols"] = dict(self.protocols)
            self.analysis_results["unique_connections"] = len(self.connections)
            self.analysis_results["dns_count"] = len(self.analysis_results["dns_queries"])
            self.analysis_results["http_count"] = len(self.analysis_results["http_requests"])
            
            self._print_analysis_summary()
            
            return self.analysis_results
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {}
    
    def _parse_protocol_stats(self, output: str):
        """Parse protocol hierarchy statistics"""
        lines = output.split('\n')
        for line in lines:
            if '=' in line or '_packets' in line:
                parts = line.split()
                for part in parts:
                    if '_' in part and part.endswith('packets'):
                        proto = part.replace('_packets', '')
                        try:
                            count = int(parts[parts.index(part) + 1].replace('(', '').replace(')', ''))
                            self.protocols[proto] = count
                        except:
                            pass
    
    def _parse_connections(self, output: str):
        """Parse TCP/UDP connections"""
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 4:
                    src_ip, dst_ip, src_port, dst_port = parts[:4]
                    if src_ip and dst_ip:
                        conn = f"{src_ip}:{src_port} -> {dst_ip}:{dst_port}"
                        self.connections.add(conn)
                        
                        # Count by protocol
                        if src_port == "80" or dst_port == "80":
                            self.stats["http_requests"] += 1
                        elif src_port == "443" or dst_port == "443":
                            self.stats["https_connections"] += 1
                        elif src_port == "53" or dst_port == "53":
                            self.stats["dns_queries"] += 1
                        
                        self.stats["tcp_packets"] += 1
    
    def _parse_dns(self, output: str):
        """Parse DNS queries"""
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 1 and parts[0]:
                    query = parts[0]
                    server = parts[1] if len(parts) > 1 else ""
                    
                    if query and query not in [q['query'] for q in self.analysis_results["dns_queries"]]:
                        self.analysis_results["dns_queries"].append({
                            "query": query,
                            "server": server,
                            "timestamp": datetime.now().isoformat()
                        })
                        self.dns_cache[query] = server
    
    def _parse_http(self, output: str):
        """Parse HTTP requests"""
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip():
                parts = line.split('\t')
                if len(parts) >= 3:
                    method = parts[0]
                    host = parts[1]
                    uri = parts[2]
                    
                    if method and host:
                        self.analysis_results["http_requests"].append({
                            "method": method,
                            "host": host,
                            "uri": uri,
                            "url": f"http://{host}{uri}",
                            "timestamp": datetime.now().isoformat()
                        })
    
    def extract_handshake_info(self, filepath: str) -> Dict:
        """
        Extract WPA handshake information from PCAP
        
        Args:
            filepath: Path to PCAP file
        
        Returns:
            Handshake information dictionary
        """
        if not os.path.exists(filepath):
            return {}
        
        print(f"\nExtracting handshake info from: {filepath}")
        
        handshake_info = {
            "has_handshake": False,
            "bssid": None,
            "essid": None,
            "client_mac": None,
            "eapol_count": 0,
            "handshake_valid": False
        }
        
        try:
            # Count EAPOL packets
            result = subprocess.run(
                ["tshark", "-r", filepath, "-Y", "eapol", "-T", "fields", "-e", "wlan.sa"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                eapol_macs = result.stdout.strip().split('\n')
                handshake_info["eapol_count"] = len(eapol_macs)
                
                if len(eapol_macs) >= 4:
                    handshake_info["has_handshake"] = True
                    
                    # Get BSSID (AP MAC)
                    handshake_info["bssid"] = eapol_macs[0] if eapol_macs else None
                    
                    # Get client MAC
                    if len(eapol_macs) > 1:
                        handshake_info["client_mac"] = eapol_macs[1]
            
            # Try aircrack-ng for more details
            result = subprocess.run(
                ["aircrack-ng", filepath],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Extract ESSID
                essid_match = re.search(r'ESSID:\s*"?([^"\n]+)"?', output)
                if essid_match:
                    handshake_info["essid"] = essid_match.group(1)
                
                # Check if handshake is valid
                if "KEY FOUND" in output or "handshake" in output.lower():
                    handshake_info["handshake_valid"] = True
            
            print(f"Handshake Info:")
            print(f"  Has Handshake: {handshake_info['has_handshake']}")
            print(f"  BSSID: {handshake_info['bssid']}")
            print(f"  ESSID: {handshake_info['essid']}")
            print(f"  Client: {handshake_info['client_mac']}")
            print(f"  EAPOL Count: {handshake_info['eapol_count']}")
            print(f"  Valid: {handshake_info['handshake_valid']}")
            
            return handshake_info
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return handshake_info
    
    def get_top_talkers(self, filepath: str, limit: int = 10) -> List[Dict]:
        """
        Get top talking hosts by packet count
        
        Args:
            filepath: Path to PCAP file
            limit: Maximum number of hosts to return
        
        Returns:
            List of top talkers with statistics
        """
        if not os.path.exists(filepath):
            return []
        
        ip_counts = defaultdict(lambda: {"sent": 0, "received": 0})
        
        try:
            result = subprocess.run(
                ["tshark", "-r", filepath, "-T", "fields", "-e", "ip.src", "-e", "ip.dst"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        src, dst = parts[0], parts[1]
                        if src:
                            ip_counts[src]["sent"] += 1
                        if dst:
                            ip_counts[dst]["received"] += 1
                
                # Sort by total packets
                sorted_ips = sorted(
                    ip_counts.items(),
                    key=lambda x: x[1]["sent"] + x[1]["received"],
                    reverse=True
                )[:limit]
                
                return [
                    {
                        "ip": ip,
                        "sent": stats["sent"],
                        "received": stats["received"],
                        "total": stats["sent"] + stats["received"]
                    }
                    for ip, stats in sorted_ips
                ]
                
        except Exception as e:
            print(f"Top talkers error: {e}")
        
        return []
    
    def export_analysis(self, filepath: str, output_format: str = "json") -> str:
        """
        Export analysis results to file
        
        Args:
            filepath: Output file path
            output_format: Format (json, csv, txt)
        
        Returns:
            Output file path or None
        """
        import json
        import csv
        
        if not self.analysis_results:
            print("No analysis results to export")
            return None
        
        try:
            if output_format == "json":
                with open(filepath, 'w') as f:
                    json.dump(self.analysis_results, f, indent=2, default=str)
            
            elif output_format == "csv":
                # Export DNS queries
                if self.analysis_results.get("dns_queries"):
                    dns_file = filepath.replace('.csv', '_dns.csv')
                    with open(dns_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=["query", "server", "timestamp"])
                        writer.writeheader()
                        writer.writerows(self.analysis_results["dns_queries"])
                
                # Export HTTP requests
                if self.analysis_results.get("http_requests"):
                    http_file = filepath.replace('.csv', '_http.csv')
                    with open(http_file, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=["method", "host", "uri", "url", "timestamp"])
                        writer.writeheader()
                        writer.writerows(self.analysis_results["http_requests"])
            
            elif output_format == "txt":
                with open(filepath, 'w') as f:
                    f.write("="*60 + "\n")
                    f.write("PACKET ANALYSIS REPORT\n")
                    f.write("="*60 + "\n\n")
                    f.write(f"File: {self.analysis_results.get('file', 'N/A')}\n")
                    f.write(f"Size: {self.analysis_results.get('size', 0)} bytes\n")
                    f.write(f"Timestamp: {self.analysis_results.get('timestamp', 'N/A')}\n\n")
                    
                    f.write("STATISTICS\n")
                    f.write("-"*40 + "\n")
                    for key, value in self.analysis_results.get("statistics", {}).items():
                        f.write(f"  {key}: {value}\n")
                    
                    f.write("\nPROTOCOLS\n")
                    f.write("-"*40 + "\n")
                    for proto, count in self.analysis_results.get("protocols", {}).items():
                        f.write(f"  {proto}: {count}\n")
                    
                    f.write(f"\nUnique Connections: {self.analysis_results.get('unique_connections', 0)}\n")
                    f.write(f"DNS Queries: {self.analysis_results.get('dns_count', 0)}\n")
                    f.write(f"HTTP Requests: {self.analysis_results.get('http_count', 0)}\n")
            
            print(f"✓ Exported to {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Export error: {e}")
            return None
    
    def _print_analysis_summary(self):
        """Print analysis summary to console"""
        print("\n" + "="*60)
        print("ANALYSIS SUMMARY")
        print("="*60)
        
        stats = self.analysis_results.get("statistics", {})
        print(f"Total Packets: {stats.get('total_packets', 0)}")
        print(f"TCP Packets: {stats.get('tcp_packets', 0)}")
        print(f"UDP Packets: {stats.get('udp_packets', 0)}")
        print(f"ICMP Packets: {stats.get('icmp_packets', 0)}")
        
        print(f"\nDNS Queries: {self.analysis_results.get('dns_count', 0)}")
        print(f"HTTP Requests: {self.analysis_results.get('http_count', 0)}")
        print(f"HTTPS Connections: {stats.get('https_connections', 0)}")
        
        print(f"\nUnique Connections: {self.analysis_results.get('unique_connections', 0)}")
        
        print("\nTop Protocols:")
        protocols = sorted(self.analysis_results.get("protocols", {}).items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        for proto, count in protocols:
            print(f"  {proto}: {count}")
        
        print("="*60)


if __name__ == "__main__":
    # Test packet analyzer
    print("="*60)
    print("WiFiNexus Guardian - Packet Analyzer Test")
    print("="*60)
    
    analyzer = PacketAnalyzer()
    
    # Check if we have any captures to analyze
    from pathlib import Path
    
    capture_dir = Path("captures")
    pcap_files = list(capture_dir.glob("*.pcap"))
    
    if pcap_files:
        print(f"\nFound {len(pcap_files)} capture file(s)")
        
        for pcap in pcap_files[:1]:  # Analyze first file
            print(f"\nAnalyzing: {pcap.name}")
            results = analyzer.analyze_pcap(str(pcap))
            
            if results:
                # Extract handshake info
                hs_info = analyzer.extract_handshake_info(str(pcap))
                
                # Get top talkers
                talkers = analyzer.get_top_talkers(str(pcap), limit=5)
                if talkers:
                    print("\nTop Talkers:")
                    for t in talkers:
                        print(f"  {t['ip']}: {t['total']} packets")
                
                # Export analysis
                output_file = str(pcap).replace('.pcap', '_analysis.json')
                analyzer.export_analysis(output_file, format="json")
    else:
        print("\nNo capture files found in ./captures/")
        print("Run handshake_capturer.py first to generate captures")
    
    print("\n" + "="*60)
    print("Packet Analyzer ready")
    print("="*60)
