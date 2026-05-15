#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Digital Forensics Module
وحدة التحليل الجنائي الرقمي للشبكات اللاسلكية

يوفر:
- تحليل ملفات PCAP المتقدمة
- استخراج البيانات الاعتمادية
- إعادة بناء الجلسات
- تحليل السلوك الزمني
- تقارير جنائية مفصلة
"""

import os
import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ForensicAnalyzer:
    """محلل جنائي رقمي متقدم لملفات الواي فاي"""
    
    def __init__(self, pcap_file: str = None):
        self.pcap_file = pcap_file
        self.networks = {}
        self.clients = {}
        self.handshakes = []
        self.credentials = []
        self.timeline = []
        self.evidence_log = []
        
        if pcap_file and os.path.exists(pcap_file):
            self.load_pcap(pcap_file)
    
    def load_pcap(self, pcap_file: str) -> bool:
        """تحميل ملف PCAP للتحليل"""
        self.pcap_file = pcap_file
        
        # في التطبيق الفعلي، سيتم استخدام scapy أو tshark
        # هنا محاكاة للتحليل
        logger.info(f"Loading PCAP file: {pcap_file}")
        
        # حساب بصمة الملف
        self.file_hash = self._calculate_hash(pcap_file)
        
        # استخراج البيانات (محاكاة)
        self._extract_networks()
        self._extract_clients()
        self._extract_handshakes()
        self._build_timeline()
        
        logger.info(f"PCAP analysis complete. Found {len(self.networks)} networks, {len(self.clients)} clients")
        return True
    
    def _calculate_hash(self, filepath: str) -> Dict[str, str]:
        """حساب تجزئات الملف للأدلة الجنائية"""
        hashes = {
            'md5': hashlib.md5(),
            'sha1': hashlib.sha1(),
            'sha256': hashlib.sha256()
        }
        
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    for h in hashes.values():
                        h.update(chunk)
            
            return {
                'md5': hashes['md5'].hexdigest(),
                'sha1': hashes['sha1'].hexdigest(),
                'sha256': hashes['sha256'].hexdigest()
            }
        except Exception as e:
            logger.error(f"Failed to calculate hash: {e}")
            return {}
    
    def _extract_networks(self):
        """استخراج معلومات الشبكات من الملف"""
        # محاكاة استخراج البيانات
        sample_networks = [
            {
                'ssid': 'TargetNetwork',
                'bssid': 'AA:BB:CC:DD:EE:FF',
                'channel': 6,
                'encryption': 'WPA2-PSK',
                'signal_strength': -45,
                'first_seen': '2024-01-15T10:30:00',
                'last_seen': '2024-01-15T11:45:00',
                'beacon_count': 1250
            },
            {
                'ssid': 'GuestWiFi',
                'bssid': '11:22:33:44:55:66',
                'channel': 11,
                'encryption': 'WPA3-SAE',
                'signal_strength': -62,
                'first_seen': '2024-01-15T10:32:00',
                'last_seen': '2024-01-15T11:40:00',
                'beacon_count': 890
            }
        ]
        
        for net in sample_networks:
            self.networks[net['bssid']] = net
            self._log_evidence('network_discovered', net)
    
    def _extract_clients(self):
        """استخراج معلومات الأجهزة المتصلة"""
        # محاكاة استخراج البيانات
        sample_clients = [
            {
                'mac': 'DE:AD:BE:EF:00:01',
                'vendor': 'Apple Inc.',
                'connected_to': 'AA:BB:CC:DD:EE:FF',
                'first_seen': '2024-01-15T10:35:00',
                'last_seen': '2024-01-15T11:30:00',
                'packets_sent': 15420,
                'packets_received': 23100,
                'probe_requests': ['HomeWiFi', 'OfficeNet', 'CafeFree']
            },
            {
                'mac': 'CA:FE:BA:BE:00:02',
                'vendor': 'Samsung Electronics',
                'connected_to': 'AA:BB:CC:DD:EE:FF',
                'first_seen': '2024-01-15T10:40:00',
                'last_seen': '2024-01-15T11:25:00',
                'packets_sent': 8900,
                'packets_received': 12300,
                'probe_requests': ['Starbucks', 'Airport_WiFi']
            }
        ]
        
        for client in sample_clients:
            self.clients[client['mac']] = client
            self._log_evidence('client_discovered', client)
    
    def _extract_handshakes(self):
        """استخراج مصافحات WPA الكاملة"""
        # محاكاة استخراج المصافحات
        sample_handshakes = [
            {
                'network_bssid': 'AA:BB:CC:DD:EE:FF',
                'client_mac': 'DE:AD:BE:EF:00:01',
                'timestamp': '2024-01-15T10:36:15',
                'complete': True,
                'file_path': '/captures/handshake_1.cap',
                'hashcat_ready': True,
                'pmkid_available': False
            }
        ]
        
        self.handshakes = sample_handshakes
        for hs in self.handshakes:
            self._log_evidence('handshake_captured', hs)
    
    def _build_timeline(self):
        """بناء خط زمني للأحداث"""
        # تجميع جميع الأحداث زمنياً
        events = []
        
        # إضافة أحداث الشبكات
        for bssid, net in self.networks.items():
            events.append({
                'timestamp': net['first_seen'],
                'type': 'network_appeared',
                'description': f"Network {net['ssid']} ({bssid}) first detected"
            })
            events.append({
                'timestamp': net['last_seen'],
                'type': 'network_last_seen',
                'description': f"Network {net['ssid']} ({bssid}) last detected"
            })
        
        # إضافة أحداث العملاء
        for mac, client in self.clients.items():
            events.append({
                'timestamp': client['first_seen'],
                'type': 'client_connected',
                'description': f"Client {mac} connected to network"
            })
        
        # إضافة أحداث المصافحة
        for hs in self.handshakes:
            events.append({
                'timestamp': hs['timestamp'],
                'type': 'handshake_completed',
                'description': f"WPA Handshake captured for {hs['network_bssid']}"
            })
        
        # ترتيب الأحداث زمنياً
        self.timeline = sorted(events, key=lambda x: x['timestamp'])
    
    def _log_evidence(self, evidence_type: str, data: Dict):
        """تسجيل الدليل الجنائي"""
        evidence = {
            'id': len(self.evidence_log) + 1,
            'type': evidence_type,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'hash': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
        }
        self.evidence_log.append(evidence)
    
    def get_network_summary(self) -> Dict:
        """الحصول على ملخص الشبكات المكتشفة"""
        return {
            'total_networks': len(self.networks),
            'encrypted_networks': sum(1 for n in self.networks.values() if n.get('encryption') != 'Open'),
            'wpa2_networks': sum(1 for n in self.networks.values() if 'WPA2' in n.get('encryption', '')),
            'wpa3_networks': sum(1 for n in self.networks.values() if 'WPA3' in n.get('encryption', '')),
            'networks_list': list(self.networks.values())
        }
    
    def get_client_analysis(self) -> Dict:
        """تحليل سلوك العملاء"""
        analysis = {
            'total_clients': len(self.clients),
            'active_clients': 0,
            'probing_networks': defaultdict(list),
            'high_activity_clients': []
        }
        
        for mac, client in self.clients.items():
            # تحليل شبكات Probe
            for probe in client.get('probe_requests', []):
                analysis['probing_networks'][probe].append(mac)
            
            # تحديد العملاء عاليي النشاط
            total_packets = client.get('packets_sent', 0) + client.get('packets_received', 0)
            if total_packets > 10000:
                analysis['high_activity_clients'].append({
                    'mac': mac,
                    'vendor': client.get('vendor'),
                    'total_packets': total_packets
                })
                analysis['active_clients'] += 1
        
        return analysis
    
    def extract_credentials(self) -> List[Dict]:
        """استخراج بيانات الاعتماد المكتشفة"""
        # في التطبيق الفعي، سيتم تحليل حزم EAPOL واستخراج الكلمات
        # هنا محاكاة للنتائج
        found_credentials = [
            {
                'network': 'TargetNetwork',
                'bssid': 'AA:BB:CC:DD:EE:FF',
                'password': 'Summer2024!',
                'method': 'handshake_crack',
                'crack_time': '45.3s',
                'confidence': 'high'
            }
        ]
        
        self.credentials = found_credentials
        for cred in found_credentials:
            self._log_evidence('credential_found', cred)
        
        return found_credentials
    
    def generate_forensic_report(self, output_file: str = None) -> Dict:
        """توليد تقرير جنائي شامل"""
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyst': 'WiFiNexus Guardian Forensic Module',
                'case_id': hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12],
                'source_file': self.pcap_file,
                'file_hashes': getattr(self, 'file_hash', {})
            },
            'executive_summary': {
                'networks_found': len(self.networks),
                'clients_identified': len(self.clients),
                'handshakes_captured': len(self.handshakes),
                'credentials_recovered': len(self.credentials),
                'risk_level': self._assess_risk_level()
            },
            'detailed_findings': {
                'networks': self.get_network_summary(),
                'clients': self.get_client_analysis(),
                'handshakes': self.handshakes,
                'credentials': self.credentials
            },
            'timeline': self.timeline,
            'evidence_chain': self.evidence_log,
            'recommendations': self._generate_recommendations()
        }
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                logger.info(f"Forensic report saved to: {output_file}")
            except Exception as e:
                logger.error(f"Failed to save report: {e}")
        
        return report
    
    def _assess_risk_level(self) -> str:
        """تقييم مستوى الخطورة"""
        risk_score = 0
        
        # زيادة الخطورة لكثرة الشبكات المشفرة
        if len(self.networks) > 5:
            risk_score += 1
        
        # زيادة الخطورة لوجود مصافحات
        risk_score += len(self.handshakes) * 2
        
        # زيادة الخطورة لكلمات المرور المكسورة
        risk_score += len(self.credentials) * 5
        
        if risk_score >= 10:
            return 'CRITICAL'
        elif risk_score >= 5:
            return 'HIGH'
        elif risk_score >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self) -> List[str]:
        """توليد توصيات أمنية"""
        recommendations = []
        
        # توصيات عامة
        if any(n.get('encryption') == 'Open' for n in self.networks.values()):
            recommendations.append("⚠️ Open networks detected. Enable WPA3 encryption immediately.")
        
        if any('WPA2' in n.get('encryption', '') and 'WPA3' not in n.get('encryption', '') for n in self.networks.values()):
            recommendations.append("📌 Consider upgrading from WPA2 to WPA3 for enhanced security.")
        
        if self.handshakes:
            recommendations.append("🔐 Handshakes captured. Ensure strong passwords (12+ chars, complex).")
        
        if self.credentials:
            recommendations.append("🚨 Credentials compromised! Change passwords immediately and audit access logs.")
        
        # تحليل سلوك العملاء
        client_analysis = self.get_client_analysis()
        if client_analysis['probing_networks']:
            recommendations.append("📡 Clients probing multiple networks. Review device security policies.")
        
        if not recommendations:
            recommendations.append("✅ No critical issues detected. Continue monitoring.")
        
        return recommendations


# مثال على الاستخدام
if __name__ == "__main__":
    print("=" * 70)
    print("WiFiNexus Guardian - Digital Forensics Module")
    print("=" * 70)
    
    # إنشاء محلل جنائي
    analyzer = ForensicAnalyzer()
    
    # محاكاة تحميل ملف PCAP
    print("\n🔍 Initializing forensic analysis...")
    analyzer._extract_networks()
    analyzer._extract_clients()
    analyzer._extract_handshakes()
    analyzer._build_timeline()
    
    # عرض ملخص الشبكات
    print("\n📊 Network Summary:")
    summary = analyzer.get_network_summary()
    print(f"  Total Networks: {summary['total_networks']}")
    print(f"  Encrypted: {summary['encrypted_networks']}")
    print(f"  WPA2: {summary['wpa2_networks']}")
    print(f"  WPA3: {summary['wpa3_networks']}")
    
    # تحليل العملاء
    print("\n📱 Client Analysis:")
    client_analysis = analyzer.get_client_analysis()
    print(f"  Total Clients: {client_analysis['total_clients']}")
    print(f"  Active Clients: {client_analysis['active_clients']}")
    
    # استخراج البيانات الاعتمادية
    print("\n🔑 Credential Extraction:")
    creds = analyzer.extract_credentials()
    for cred in creds:
        print(f"  ✓ Network: {cred['network']} | Password: {cred['password']}")
    
    # توليد التقرير الجنائي
    print("\n📄 Generating Forensic Report...")
    report = analyzer.generate_forensic_report('/workspace/forensics/forensic_report.json')
    
    print(f"\n  Risk Level: {report['executive_summary']['risk_level']}")
    print(f"  Evidence Items: {len(report['evidence_chain'])}")
    print(f"  Recommendations: {len(report['recommendations'])}")
    
    print("\n" + "=" * 70)
    print("Forensic Analysis Complete - Report Saved")
    print("=" * 70)
