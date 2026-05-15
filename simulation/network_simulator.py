#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulation Environment for WiFiNexus Guardian
بيئة محاكاة آمنة لاختبار أدوات WiFiNexus بدون الحاجة لعتاد حقيقي

This module provides a safe sandbox to test scanning, attacking, and defense logic
using simulated data packets and network scenarios.
"""

import random
import time
import json
from datetime import datetime
from typing import List, Dict, Optional

class SimulatedNetwork:
    """تمثل شبكة واي فاي وهمية للاختبار"""
    
    def __init__(self, ssid: str, bssid: str, channel: int, 
                 signal: int, encryption: str, has_clients: bool = True):
        self.ssid = ssid
        self.bssid = bssid
        self.channel = channel
        self.signal = signal
        self.encryption = encryption
        self.has_clients = has_clients
        self.clients = []
        self.handshake_available = False
        
        if has_clients:
            num_clients = random.randint(1, 5)
            for i in range(num_clients):
                mac = f"00:11:22:33:{random.randint(10,99)}:{random.randint(10,99)}"
                self.clients.append({
                    'mac': mac,
                    'active': random.choice([True, False]),
                    'last_seen': datetime.now()
                })

    def generate_beacon(self) -> Dict:
        """توليد حزمة Beacon وهمية"""
        return {
            'type': 'Beacon',
            'ssid': self.ssid,
            'bssid': self.bssid,
            'channel': self.channel,
            'signal': self.signal + random.randint(-5, 5),
            'encryption': self.encryption,
            'timestamp': datetime.now().isoformat()
        }

    def simulate_handshake(self) -> bool:
        """محاكاة التقاط مصافحة WPA"""
        if self.has_clients and random.random() > 0.3:
            self.handshake_available = True
            return True
        return False


class NetworkSimulator:
    """المحرك الرئيسي للمحاكاة"""
    
    def __init__(self):
        self.networks: List[SimulatedNetwork] = []
        self.running = False
        self.captured_handshakes = []
        self.detected_attacks = []
        
        # Initialize default simulated networks
        self._init_default_networks()

    def _init_default_networks(self):
        """إنشاء شبكات وهمية افتراضية"""
        default_ssids = [
            ("Home_Network", "WPA2", True),
            ("Office_Secure", "WPA3", True),
            ("CoffeeShop_Free", "Open", False),
            ("Guest_WiFi", "WPA2", True),
            ("Legacy_System", "WEP", True),
            ("Hidden_Net", "WPA2", False), # Hidden SSID
        ]
        
        for i, (ssid, enc, has_clients) in enumerate(default_ssids):
            bssid = f"AA:BB:CC:DD:EE:{i:02X}"
            channel = random.choice([1, 6, 11, 36, 40, 149])
            signal = random.randint(-90, -30)
            
            net = SimulatedNetwork(ssid, bssid, channel, signal, enc, has_clients)
            self.networks.append(net)

    def start_scanning(self, duration: int = 10) -> List[Dict]:
        """محاكاة عملية مسح للشبكات"""
        print(f"📡 Starting simulation scan for {duration} seconds...")
        results = []
        
        for _ in range(duration):
            for net in self.networks:
                # Simulate signal fluctuation
                net.signal = max(-95, min(-20, net.signal + random.randint(-2, 2)))
                beacon = net.generate_beacon()
                results.append(beacon)
            time.sleep(0.5) # Fast simulation
            
        return results

    def simulate_deauth_attack(self, target_bssid: str) -> Dict:
        """محاكاة هجوم Deauthentication"""
        target = next((n for n in self.networks if n.bssid == target_bssid), None)
        if not target:
            return {'success': False, 'error': 'Target not found'}
        
        print(f"⚡ Simulating Deauth attack on {target.ssid}...")
        time.sleep(1)
        
        # Simulate success rate
        if random.random() > 0.2:
            clients_disconnected = len([c for c in target.clients if c['active']])
            for client in target.clients:
                client['active'] = False
            
            return {
                'success': True,
                'target_ssid': target.ssid,
                'clients_disconnected': clients_disconnected,
                'packets_sent': random.randint(50, 200)
            }
        else:
            return {'success': False, 'error': 'Client reconnected too fast'}

    def simulate_handshake_capture(self, target_bssid: str) -> Dict:
        """محاكاة التقاط المصافحة"""
        target = next((n for n in self.networks if n.bssid == target_bssid), None)
        if not target:
            return {'success': False, 'error': 'Target not found'}
        
        print(f"🎣 Waiting for handshake on {target.ssid}...")
        time.sleep(1.5)
        
        if target.simulate_handshake():
            filename = f"handshake_{target.ssid}_{target.bssid.replace(':', '')}.cap"
            self.captured_handshakes.append(filename)
            return {
                'success': True,
                'filename': filename,
                'ssid': target.ssid,
                'bssid': target.bssid,
                'size_kb': random.randint(2, 15)
            }
        else:
            return {'success': False, 'error': 'No handshake captured (timeout)'}

    def simulate_wids_detection(self) -> List[Dict]:
        """محاكاة كشف الهجمات عبر WIDS"""
        attacks = []
        
        # Randomly generate some attacks for detection
        if random.random() > 0.6:
            attacks.append({
                'type': 'Deauth Flood',
                'source': f"00:DE:AD:BE:EF:{random.randint(10,99)}",
                'target': random.choice(self.networks).bssid,
                'severity': 'High',
                'packets_per_sec': random.randint(100, 1000)
            })
            
        if random.random() > 0.8:
            attacks.append({
                'type': 'Evil Twin Detected',
                'rogue_bssid': f"66:66:66:66:{random.randint(10,99)}:{random.randint(10,99)}",
                'impersonating': random.choice(self.networks).ssid,
                'severity': 'Critical'
            })
            
        self.detected_attacks.extend(attacks)
        return attacks

    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات المحاكاة"""
        return {
            'total_networks': len(self.networks),
            'wpa2_networks': len([n for n in self.networks if n.encryption == 'WPA2']),
            'open_networks': len([n for n in self.networks if n.encryption == 'Open']),
            'captured_handshakes': len(self.captured_handshakes),
            'detected_attacks': len(self.detected_attacks),
            'total_clients': sum(len(n.clients) for n in self.networks)
        }

def run_demo():
    """تشغيل عرض توضيحي للمحاكاة"""
    print("="*60)
    print("🛡️  WiFiNexus Guardian - Simulation Mode Demo")
    print("="*60)
    
    sim = NetworkSimulator()
    
    # 1. Scan
    print("\n[1] Scanning for networks...")
    scan_results = sim.start_scanning(duration=3)
    print(f"✅ Found {len(set(r['ssid'] for r in scan_results))} unique networks.")
    
    # 2. Attack Sim
    if sim.networks:
        target = sim.networks[0]
        print(f"\n[2] Simulating attack on '{target.ssid}'...")
        
        deauth_res = sim.simulate_deauth_attack(target.bssid)
        if deauth_res['success']:
            print(f"   ✅ Deauth Success: {deauth_res['clients_disconnected']} clients disconnected.")
            
            cap_res = sim.simulate_handshake_capture(target.bssid)
            if cap_res['success']:
                print(f"   ✅ Handshake Captured: {cap_res['filename']}")
    
    # 3. WIDS
    print("\n[3] Running WIDS Detection...")
    detected = sim.simulate_wids_detection()
    if detected:
        for atk in detected:
            print(f"   ⚠️  ALERT: {atk['type']} detected! Severity: {atk['severity']}")
    else:
        print("   ✅ No active attacks detected.")
    
    # 4. Stats
    print("\n[4] Final Statistics:")
    stats = sim.get_statistics()
    for k, v in stats.items():
        print(f"   • {k}: {v}")
    
    print("\n" + "="*60)
    print("✅ Simulation Complete. Safe environment verified.")
    print("="*60)

if __name__ == "__main__":
    run_demo()
