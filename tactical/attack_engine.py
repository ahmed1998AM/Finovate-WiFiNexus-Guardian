#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WiFiNexus Guardian - Tactical Attack Engine
Professional Penetration Testing Tool
Module: Intelligent Attack Decision Making

Features:
- Context-aware attack selection
- Risk assessment and mitigation
- Adaptive timing and pacing
- Multi-stage attack chains
- Real-time success monitoring
- Automatic fallback strategies
"""

import time
import random
import json
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AttackPhase(Enum):
    """Attack lifecycle phases"""
    RECONNAISSANCE = "reconnaissance"
    SCANNING = "scanning"
    ANALYSIS = "analysis"
    EXPLOITATION = "exploitation"
    POST_EXPLOITATION = "post_exploitation"
    CLEANUP = "cleanup"


class RiskLevel(Enum):
    """Risk assessment levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class StealthMode(Enum):
    """Stealth operation modes"""
    AGGRESSIVE = "aggressive"  # Fast, detectable
    BALANCED = "balanced"      # Moderate speed and stealth
    SILENT = "silent"          # Slow, minimal detection
    GHOST = "ghost"            # Ultra-stealth with delays


@dataclass
class TargetNetwork:
    """Represents a target network with metadata"""
    bssid: str
    ssid: str
    channel: int
    signal_strength: int
    encryption: str
    wps_enabled: bool
    clients_count: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    vulnerability_score: float = 0.0
    attack_history: List[Dict] = field(default_factory=list)
    
    def update_activity(self):
        self.last_seen = time.time()
    
    def is_active(self, timeout: float = 300.0) -> bool:
        return (time.time() - self.last_seen) < timeout


@dataclass
class AttackStrategy:
    """Defines an attack strategy with parameters"""
    name: str
    phase: AttackPhase
    risk_level: RiskLevel
    stealth_mode: StealthMode
    success_probability: float
    estimated_duration: float  # seconds
    required_tools: List[str]
    prerequisites: List[str]
    description: str
    parameters: Dict = field(default_factory=dict)


class TacticalAttackEngine:
    """
    Intelligent attack engine with tactical decision-making
    """
    
    def __init__(self):
        self.targets: Dict[str, TargetNetwork] = {}
        self.active_attacks: Dict[str, Dict] = {}
        self.attack_history: List[Dict] = []
        self.stealth_mode = StealthMode.BALANCED
        self.risk_threshold = RiskLevel.MEDIUM
        
        # Attack strategies database
        self.strategies = self._initialize_strategies()
        
        # Timing parameters based on stealth mode
        self.timing_config = {
            StealthMode.AGGRESSIVE: {"scan_delay": 0.1, "attack_delay": 0.5, "retry_delay": 2},
            StealthMode.BALANCED: {"scan_delay": 1.0, "attack_delay": 3.0, "retry_delay": 10},
            StealthMode.SILENT: {"scan_delay": 5.0, "attack_delay": 15.0, "retry_delay": 60},
            StealthMode.GHOST: {"scan_delay": 30.0, "attack_delay": 120.0, "retry_delay": 300}
        }
    
    def _initialize_strategies(self) -> Dict[str, AttackStrategy]:
        """Initialize attack strategies database"""
        return {
            "passive_scan": AttackStrategy(
                name="Passive Scanning",
                phase=AttackPhase.RECONNAISSANCE,
                risk_level=RiskLevel.LOW,
                stealth_mode=StealthMode.SILENT,
                success_probability=0.95,
                estimated_duration=60.0,
                required_tools=["airodump-ng"],
                prerequisites=[],
                description="Passive network discovery without transmitting"
            ),
            
            "active_probe": AttackStrategy(
                name="Active Probing",
                phase=AttackPhase.SCANNING,
                risk_level=RiskLevel.MEDIUM,
                stealth_mode=StealthMode.BALANCED,
                success_probability=0.85,
                estimated_duration=30.0,
                required_tools=["aireplay-ng"],
                prerequisites=["passive_scan"],
                description="Active probe requests to discover hidden SSIDs"
            ),
            
            "deauth_attack": AttackStrategy(
                name="Deauthentication Attack",
                phase=AttackPhase.EXPLOITATION,
                risk_level=RiskLevel.HIGH,
                stealth_mode=StealthMode.AGGRESSIVE,
                success_probability=0.75,
                estimated_duration=10.0,
                required_tools=["aireplay-ng", "mdk4"],
                prerequisites=["target_selected"],
                description="Force clients to disconnect for handshake capture",
                parameters={"packets": 10, "delay": 1}
            ),
            
            "handshake_capture": AttackStrategy(
                name="Handshake Capture",
                phase=AttackPhase.EXPLOITATION,
                risk_level=RiskLevel.MEDIUM,
                stealth_mode=StealthMode.BALANCED,
                success_probability=0.70,
                estimated_duration=120.0,
                required_tools=["airodump-ng"],
                prerequisites=["deauth_attack"],
                description="Capture WPA/WPA2 4-way handshake"
            ),
            
            "pmkid_attack": AttackStrategy(
                name="PMKID Attack",
                phase=AttackPhase.EXPLOITATION,
                risk_level=RiskLevel.MEDIUM,
                stealth_mode=StealthMode.BALANCED,
                success_probability=0.80,
                estimated_duration=30.0,
                required_tools=["hcxdumptool"],
                prerequisites=["target_selected"],
                description="Extract PMKID hash without client interaction"
            ),
            
            "evil_twin": AttackStrategy(
                name="Evil Twin Attack",
                phase=AttackPhase.EXPLOITATION,
                risk_level=RiskLevel.HIGH,
                stealth_mode=StealthMode.AGGRESSIVE,
                success_probability=0.65,
                estimated_duration=300.0,
                required_tools=["hostapd", "dnsmasq"],
                prerequisites=["monitor_mode"],
                description="Create rogue access point mimicking target"
            ),
            
            "wps_pixie": AttackStrategy(
                name="WPS Pixie-Dust Attack",
                phase=AttackPhase.EXPLOITATION,
                risk_level=RiskLevel.MEDIUM,
                stealth_mode=StealthMode.BALANCED,
                success_probability=0.60,
                estimated_duration=60.0,
                required_tools=["reaver", "bully"],
                prerequisites=["wps_enabled"],
                description="Offline WPS PIN recovery attack"
            ),
            
            "captive_portal": AttackStrategy(
                name="Captive Portal Phishing",
                phase=AttackPhase.POST_EXPLOITATION,
                risk_level=RiskLevel.HIGH,
                stealth_mode=StealthMode.AGGRESSIVE,
                success_probability=0.50,
                estimated_duration=600.0,
                required_tools=["hostapd", "nginx"],
                prerequisites=["evil_twin"],
                description="Fake login portal to harvest credentials"
            )
        }
    
    def add_target(self, bssid: str, ssid: str, channel: int, 
                   signal: int, encryption: str, wps: bool = False) -> TargetNetwork:
        """Add or update a target network"""
        if bssid in self.targets:
            target = self.targets[bssid]
            target.update_activity()
            target.signal_strength = signal
            target.channel = channel
        else:
            target = TargetNetwork(
                bssid=bssid,
                ssid=ssid,
                channel=channel,
                signal_strength=signal,
                encryption=encryption,
                wps_enabled=wps
            )
            self.targets[bssid] = target
        
        # Calculate vulnerability score
        target.vulnerability_score = self._calculate_vulnerability(target)
        
        return target
    
    def _calculate_vulnerability(self, target: TargetNetwork) -> float:
        """Calculate vulnerability score (0-100)"""
        score = 0.0
        
        # Encryption weakness
        if "WEP" in target.encryption:
            score += 40
        elif "WPA" in target.encryption and "WPA2" not in target.encryption:
            score += 20
        elif "WPA3" in target.encryption:
            score -= 10
        
        # WPS enabled
        if target.wps_enabled:
            score += 25
        
        # Signal strength (stronger = easier to attack)
        if target.signal_strength > -50:
            score += 15
        elif target.signal_strength > -70:
            score += 10
        
        # Client count (more clients = more opportunities)
        if target.clients_count > 5:
            score += 10
        elif target.clients_count > 2:
            score += 5
        
        # Previous attack success
        if target.attack_history:
            successful = sum(1 for a in target.attack_history if a.get("success", False))
            if successful > 0:
                score += min(10, successful * 5)
        
        return min(100.0, max(0.0, score))
    
    def select_best_target(self, criteria: str = "vulnerability") -> Optional[TargetNetwork]:
        """Select the best target based on criteria"""
        active_targets = [t for t in self.targets.values() if t.is_active()]
        
        if not active_targets:
            return None
        
        if criteria == "vulnerability":
            return max(active_targets, key=lambda t: t.vulnerability_score)
        elif criteria == "signal":
            return max(active_targets, key=lambda t: t.signal_strength)
        elif criteria == "clients":
            return max(active_targets, key=lambda t: t.clients_count)
        elif criteria == "stealth":
            # Prefer targets with low activity (less likely to notice)
            return min(active_targets, key=lambda t: t.clients_count)
        
        return active_targets[0]
    
    def plan_attack_chain(self, target: TargetNetwork) -> List[AttackStrategy]:
        """Plan a sequence of attacks based on target profile"""
        chain = []
        
        # Always start with reconnaissance
        chain.append(self.strategies["passive_scan"])
        
        # Add PMKID attack if supported (no client needed)
        if "PMKID" in target.encryption or "WPA" in target.encryption:
            chain.append(self.strategies["pmkid_attack"])
        
        # If WPS enabled, add WPS attack
        if target.wps_enabled:
            chain.append(self.strategies["wps_pixie"])
        
        # If clients present, plan deauth + handshake
        if target.clients_count > 0 or self.stealth_mode == StealthMode.AGGRESSIVE:
            chain.append(self.strategies["deauth_attack"])
            chain.append(self.strategies["handshake_capture"])
        
        # High-risk operations only if stealth mode allows
        if self.stealth_mode in [StealthMode.AGGRESSIVE, StealthMode.BALANCED]:
            if target.vulnerability_score > 50:
                chain.append(self.strategies["evil_twin"])
                chain.append(self.strategies["captive_portal"])
        
        return chain
    
    def assess_risk(self, target: TargetNetwork, strategy: AttackStrategy) -> RiskLevel:
        """Assess the risk level of an attack on a target"""
        base_risk = strategy.risk_level
        
        # Adjust based on target characteristics
        if target.clients_count > 10:
            if base_risk == RiskLevel.LOW:
                base_risk = RiskLevel.MEDIUM
            elif base_risk == RiskLevel.MEDIUM:
                base_risk = RiskLevel.HIGH
        
        # Adjust based on time of day (simplified)
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Business hours
            if base_risk == RiskLevel.MEDIUM:
                base_risk = RiskLevel.HIGH
        
        # Adjust based on previous failures
        recent_failures = sum(
            1 for a in target.attack_history[-5:]
            if not a.get("success", False) and time.time() - a.get("timestamp", 0) < 3600
        )
        if recent_failures >= 3:
            if base_risk == RiskLevel.LOW:
                base_risk = RiskLevel.MEDIUM
            elif base_risk == RiskLevel.MEDIUM:
                base_risk = RiskLevel.HIGH
        
        return base_risk
    
    def should_proceed(self, target: TargetNetwork, strategy: AttackStrategy) -> Tuple[bool, str]:
        """Determine if attack should proceed based on risk assessment"""
        risk = self.assess_risk(target, strategy)
        
        # Check against threshold
        risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        if risk_order.index(risk) > risk_order.index(self.risk_threshold):
            return False, f"Risk level {risk.value} exceeds threshold {self.risk_threshold.value}"
        
        # Check prerequisites
        for prereq in strategy.prerequisites:
            if prereq == "monitor_mode":
                # Would check actual monitor mode status here
                pass
            elif prereq == "target_selected":
                if not target:
                    return False, "No target selected"
            elif prereq == "wps_enabled":
                if not target.wps_enabled:
                    return False, "WPS not enabled on target"
            elif prereq.endswith("_scan"):
                # Check if prerequisite scan completed
                pass
        
        # Check stealth mode compatibility
        if strategy.stealth_mode.value > self.stealth_mode.value:
            return False, f"Strategy requires {strategy.stealth_mode.value} mode"
        
        return True, "Approved"
    
    def execute_attack(self, target: TargetNetwork, strategy: AttackStrategy,
                      callback: Optional[Callable] = None) -> Dict:
        """Execute an attack strategy with monitoring"""
        # Pre-execution check
        approved, reason = self.should_proceed(target, strategy)
        if not approved:
            logger.warning(f"Attack blocked: {reason}")
            return {"success": False, "reason": reason, "phase": "blocked"}
        
        logger.info(f"Starting attack: {strategy.name} on {target.bssid}")
        
        attack_record = {
            "target_bssid": target.bssid,
            "strategy": strategy.name,
            "phase": strategy.phase.value,
            "start_time": time.time(),
            "status": "running"
        }
        
        self.active_attacks[target.bssid] = attack_record
        
        try:
            # Apply timing based on stealth mode
            timing = self.timing_config[self.stealth_mode]
            time.sleep(timing["attack_delay"])
            
            # Simulate attack execution (would integrate with actual tools)
            success = self._simulate_attack_execution(strategy, target)
            
            # Record result
            attack_record["end_time"] = time.time()
            attack_record["duration"] = attack_record["end_time"] - attack_record["start_time"]
            attack_record["success"] = success
            attack_record["status"] = "completed"
            
            # Update target history
            target.attack_history.append(attack_record.copy())
            self.attack_history.append(attack_record.copy())
            
            # Callback for progress updates
            if callback:
                callback(attack_record)
            
            logger.info(f"Attack {'succeeded' if success else 'failed'}: {strategy.name}")
            
            return attack_record
            
        except Exception as e:
            logger.error(f"Attack failed with exception: {e}")
            attack_record["status"] = "error"
            attack_record["error"] = str(e)
            return attack_record
        finally:
            if target.bssid in self.active_attacks:
                del self.active_attacks[target.bssid]
    
    def _simulate_attack_execution(self, strategy: AttackStrategy, 
                                   target: TargetNetwork) -> bool:
        """Simulate attack execution (replace with actual tool integration)"""
        # This would integrate with actual attack modules
        # For now, use probability-based simulation
        
        base_prob = strategy.success_probability
        
        # Adjust for signal strength
        if target.signal_strength < -80:
            base_prob *= 0.7
        elif target.signal_strength > -50:
            base_prob *= 1.1
        
        # Adjust for previous failures (learning)
        recent_attempts = [a for a in target.attack_history[-3:] 
                          if a["strategy"] == strategy.name]
        if len(recent_attempts) >= 2:
            base_prob *= 0.8  # Diminishing returns
        
        success = random.random() < base_prob
        
        # Simulate duration
        time.sleep(min(strategy.estimated_duration / 10, 5))  # Scaled down for demo
        
        return success
    
    def set_stealth_mode(self, mode: StealthMode):
        """Change operational stealth mode"""
        self.stealth_mode = mode
        logger.info(f"Stealth mode changed to: {mode.value}")
    
    def set_risk_threshold(self, level: RiskLevel):
        """Set maximum acceptable risk level"""
        self.risk_threshold = level
        logger.info(f"Risk threshold set to: {level.value}")
    
    def get_attack_statistics(self) -> Dict:
        """Get comprehensive attack statistics"""
        total = len(self.attack_history)
        successful = sum(1 for a in self.attack_history if a.get("success", False))
        
        by_phase = {}
        by_strategy = {}
        
        for attack in self.attack_history:
            phase = attack.get("phase", "unknown")
            strategy = attack.get("strategy", "unknown")
            
            by_phase[phase] = by_phase.get(phase, 0) + 1
            by_strategy[strategy] = by_strategy.get(strategy, 0) + 1
        
        return {
            "total_attacks": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "by_phase": by_phase,
            "by_strategy": by_strategy,
            "active_targets": len([t for t in self.targets.values() if t.is_active()]),
            "current_stealth_mode": self.stealth_mode.value,
            "risk_threshold": self.risk_threshold.value
        }
    
    def cleanup(self):
        """Cleanup active attacks and restore state"""
        logger.info("Cleaning up active attacks...")
        
        for bssid in list(self.active_attacks.keys()):
            # Send cleanup signals to attack modules
            logger.info(f"Stopping attack on {bssid}")
        
        self.active_attacks.clear()
        
        # Additional cleanup logic would go here
        logger.info("Cleanup completed")


# Singleton instance
_tactical_engine = None

def get_tactical_engine() -> TacticalAttackEngine:
    """Get singleton instance of tactical engine"""
    global _tactical_engine
    if _tactical_engine is None:
        _tactical_engine = TacticalAttackEngine()
    return _tactical_engine


if __name__ == "__main__":
    # Demo usage
    engine = get_tactical_engine()
    
    print("="*60)
    print("WiFiNexus Guardian - Tactical Attack Engine")
    print("="*60)
    
    # Add sample targets
    engine.add_target("AA:BB:CC:DD:EE:01", "HomeWiFi", 6, -45, "WPA2-PSK", wps=True)
    engine.add_target("AA:BB:CC:DD:EE:02", "OfficeNet", 11, -60, "WPA2-Enterprise", wps=False)
    engine.add_target("AA:BB:CC:DD:EE:03", "GuestNetwork", 1, -75, "WPA-PSK", wps=True)
    
    # Set operational parameters
    engine.set_stealth_mode(StealthMode.BALANCED)
    engine.set_risk_threshold(RiskLevel.HIGH)
    
    # Select best target
    target = engine.select_best_target("vulnerability")
    if target:
        print(f"\n🎯 Selected Target: {target.ssid} ({target.bssid})")
        print(f"   Vulnerability Score: {target.vulnerability_score:.1f}/100")
        print(f"   Signal: {target.signal_strength} dBm")
        print(f"   Clients: {target.clients_count}")
        print(f"   WPS: {'Enabled' if target.wps_enabled else 'Disabled'}")
        
        # Plan attack chain
        chain = engine.plan_attack_chain(target)
        print(f"\n📋 Planned Attack Chain:")
        for i, strategy in enumerate(chain, 1):
            print(f"   {i}. {strategy.name} (Risk: {strategy.risk_level.value})")
        
        # Execute first attack in chain
        if chain:
            print(f"\n⚔️  Executing: {chain[0].name}")
            result = engine.execute_attack(target, chain[0])
            print(f"   Result: {'✅ Success' if result.get('success') else '❌ Failed'}")
            print(f"   Duration: {result.get('duration', 0):.2f}s")
    
    # Show statistics
    stats = engine.get_attack_statistics()
    print(f"\n📊 Attack Statistics:")
    print(f"   Total Attacks: {stats['total_attacks']}")
    print(f"   Success Rate: {stats['success_rate']*100:.1f}%")
    print(f"   Active Targets: {stats['active_targets']}")
    
    print("\n" + "="*60)
