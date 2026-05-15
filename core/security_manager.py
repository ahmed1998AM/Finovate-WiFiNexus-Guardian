"""
Security & Safety Module - Advanced Security Features for WiFiNexus Guardian
Implements safety modes, legal compliance, anti-detection, and security best practices
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import os
import sys
import json
import hashlib
import platform
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path



class StealthModeDetector:
    """
    Advanced detector for stealth mode anomalies and beacon flooding
    """
    
    def __init__(self):
        self.beacon_threshold = 500  # Default threshold for beacon flood detection
        self.detection_log = []
    
    def detect_beacon_flood(self, beacon_count: int, threshold: int = None) -> bool:
        """
        Detect if beacon frames count indicates flooding attack
        
        Args:
            beacon_count: Number of beacon frames detected
            threshold: Custom threshold (default: 500)
            
        Returns:
            bool: True if flooding detected
        """
        thresh = threshold or self.beacon_threshold
        is_flooding = beacon_count > thresh
        
        if is_flooding:
            self.detection_log.append({
                'type': 'beacon_flood',
                'count': beacon_count,
                'threshold': thresh,
                'timestamp': datetime.now().isoformat()
            })
        
        return is_flooding
    
    def detect_anomaly(self, metric: str, value: float, baseline: float, 
                       tolerance: float = 0.2) -> bool:
        """
        Detect anomalies in network metrics
        
        Args:
            metric: Name of the metric
            value: Current value
            baseline: Expected baseline value
            tolerance: Acceptable deviation (default: 20%)
            
        Returns:
            bool: True if anomaly detected
        """
        deviation = abs(value - baseline) / baseline if baseline > 0 else 0
        is_anomaly = deviation > tolerance
        
        if is_anomaly:
            self.detection_log.append({
                'type': 'anomaly',
                'metric': metric,
                'value': value,
                'baseline': baseline,
                'deviation': deviation,
                'timestamp': datetime.now().isoformat()
            })
        
        return is_anomaly

class SecurityManager:
    """
    Advanced Security Manager for WiFiNexus Guardian
    - Safety Mode enforcement
    - Legal compliance checks
    - Anti-detection measures
    - Secure data handling
    - Audit logging
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.safety_mode = True  # Enabled by default
        self.legal_warning_accepted = False
        self.audit_log = []
        self.security_level = "high"  # low, medium, high
        self.stealth_mode = False
        self.encryption_enabled = True
        self.stealth_mode_active = False  # Alias for test compatibility
        self.monitoring_enabled = True
        self.monitored_processes = []
        self.active_processes = []
        
        # Security paths
        self.config_dir = Path.home() / ".wifinexus"
        self.config_dir.mkdir(exist_ok=True)
        
        self.log_file = self.config_dir / "security_audit.log"
        self.config_file = self.config_dir / "security_config.json"
        
        # Load existing config
        self._load_config()
        
        # Initialize audit log
        self._log_event("SecurityManager initialized", level="info")
    
    def _load_config(self):
        """Load security configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.safety_mode = config.get('safety_mode', True)
                    self.security_level = config.get('security_level', 'high')
                    self.stealth_mode = config.get('stealth_mode', False)
                    self.legal_warning_accepted = config.get('legal_warning_accepted', False)
            except:
                pass
    
    def _save_config(self):
        """Save security configuration to file"""
        config = {
            'safety_mode': self.safety_mode,
            'security_level': self.security_level,
            'stealth_mode': self.stealth_mode,
            'legal_warning_accepted': self.legal_warning_accepted,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _log_event(self, event: str, level: str = "info", details: Dict = None):
        """Log security event to audit log"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event,
            'level': level,
            'platform': self.platform,
            'details': details or {}
        }
        
        self.audit_log.append(entry)
        
        # Write to log file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def show_legal_warning(self) -> bool:
        """Display legal warning and get user acceptance"""
        warning_text = """
╔══════════════════════════════════════════════════════════════════╗
║                    ⚠️  LEGAL WARNING  ⚠️                          ║
║                                                                  ║
║  WiFiNexus Guardian - Professional Wireless Intelligence Platform ║
║                                                                  ║
║  This software is intended for AUTHORIZED network analysis only. ║
║                                                                  ║
║  By using this software, you confirm that:                       ║
║  • You have explicit authorization to analyze target networks    ║
║  • You will NOT use this tool for illegal activities             ║
║  • You understand and comply with all local laws/regulations     ║
║  • You accept full responsibility for your actions               ║
║                                                                  ║
║  Unauthorized access to computer networks is ILLEGAL and may     ║
║  result in criminal prosecution and civil liability.             ║
║                                                                  ║
║  Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)          ║
║  © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved              ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        print(warning_text)
        
        if not self.legal_warning_accepted:
            response = input("\nDo you accept these terms? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                self.legal_warning_accepted = True
                self._log_event("Legal warning accepted", level="compliance")
                self._save_config()
                return True
            else:
                self._log_event("Legal warning declined", level="warning")
                print("\n❌ You must accept the legal terms to use this software.")
                return False
        
        return True
    
    def enable_safety_mode(self):
        """Enable safety mode (restricts dangerous operations)"""
        self.safety_mode = True
        self._log_event("Safety mode ENABLED", level="security")
        self._save_config()
        print("✓ Safety mode enabled - Dangerous operations restricted")
    
    def disable_safety_mode(self, password: str = None):
        """
        Disable safety mode (requires confirmation)
        
        Args:
            password: Optional password for additional security
        """
        if self.security_level == "high":
            print("⚠️ Warning: Disabling safety mode allows potentially dangerous operations")
            confirm = input("Are you sure? Type 'CONFIRM' to proceed: ").strip()
            
            if confirm != 'CONFIRM':
                print("❌ Safety mode remains enabled")
                return False
        
        self.safety_mode = False
        self._log_event("Safety mode DISABLED", level="warning", details={'password_used': bool(password)})
        self._save_config()
        print("⚠️ Safety mode disabled - Proceed with extreme caution")
        return True
    
    def check_operation_allowed(self, operation: str) -> bool:
        """
        Check if an operation is allowed based on safety settings
        
        Args:
            operation: Name of operation to check
            
        Returns:
            True if allowed, False if blocked
        """
        dangerous_operations = [
            'deauth_attack',
            'beacon_flood',
            'probe_request_flood',
            'authentication_flood',
            'dos_attack',
            'jamming'
        ]
        
        if self.safety_mode and operation in dangerous_operations:
            self._log_event(f"Blocked dangerous operation: {operation}", level="security")
            print(f"❌ Operation '{operation}' is blocked in Safety Mode")
            return False
        
        self._log_event(f"Operation approved: {operation}", level="info")
        return True
    
    def enable_stealth_mode(self):
        """Enable stealth mode (reduces detection footprint)"""
        self.stealth_mode = True
        self.stealth_mode_active = True
        self._log_event("Stealth mode ENABLED", level="security")
        print("✓ Stealth mode enabled - Reduced detection footprint")
        
        # Apply stealth settings
        self._apply_stealth_settings()
    
    def disable_stealth_mode(self):
        """Disable stealth mode"""
        self.stealth_mode = False
        self.stealth_mode_active = False
        self._log_event("Stealth mode DISABLED", level="info")
        print("✓ Stealth mode disabled")
    
    def _apply_stealth_settings(self):
        """Apply stealth mode settings"""
        stealth_tips = """
🥷 STEALTH MODE ACTIVE - Recommendations:

1. Randomize MAC addresses before operations
2. Use passive capture instead of active probing
3. Limit transmission power
4. Avoid continuous scanning
5. Use directional antennas when possible
6. Monitor for detection systems (WIDS/WIPS)
7. Keep operation sessions short
8. Clear logs after completion

⚠️ Note: Stealth mode does not guarantee undetectability!
        """
        print(stealth_tips)
    
    def get_security_status(self) -> Dict:
        """Get current security status"""
        return {
            'safety_mode': self.safety_mode,
            'security_level': self.security_level,
            'stealth_mode': self.stealth_mode,
            'legal_accepted': self.legal_warning_accepted,
            'audit_events_count': len(self.audit_log),
            'platform': self.platform,
            'config_file': str(self.config_file),
            'log_file': str(self.log_file)
        }
    
    def export_audit_log(self, filename: str = None) -> str:
        """Export audit log to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_audit_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'export_time': datetime.now().isoformat(),
                'platform': self.platform,
                'total_events': len(self.audit_log),
                'events': self.audit_log
            }, f, indent=2)
        
        print(f"✓ Audit log exported to {filename}")
        return filename
    
    def clear_audit_log(self, confirm: bool = False):
        """Clear audit log (use with caution)"""
        if not confirm:
            print("⚠️ Are you sure you want to clear the audit log?")
            return
        
        self.audit_log = []
        
        # Clear log file
        with open(self.log_file, 'w') as f:
            f.write("")
        
        self._log_event("Audit log cleared", level="warning")
        print("✓ Audit log cleared")
    
    def check_root_privileges(self) -> bool:
        """Check if running with root/admin privileges"""
        if self.platform == "Windows":
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:
            return os.geteuid() == 0
    
    def recommend_security_improvements(self) -> List[str]:
        """Get security improvement recommendations"""
        recommendations = []
        
        if not self.check_root_privileges():
            recommendations.append("⚠️ Run as administrator/root for full functionality")
        
        if self.security_level == "low":
            recommendations.append("⚠️ Consider increasing security level to 'high'")
        
        if not self.safety_mode:
            recommendations.append("⚠️ Safety mode is disabled - Enable for safer operation")
        
        if platform.system() == "Windows":
            recommendations.append("💡 Install Npcap for better packet capture capabilities")
            recommendations.append("💡 Add Windows Defender exclusions for this application")
        
        if platform.system() == "Linux":
            recommendations.append("💡 Ensure wireless drivers support monitor mode")
            recommendations.append("💡 Consider using Kali Linux or Parrot OS for best compatibility")
        
        recommendations.append("📚 Review legal compliance requirements in your jurisdiction")
        recommendations.append("🔒 Always obtain written authorization before testing")
        
        return recommendations
    
    def create_windows_defender_exclusion(self):
        """Create Windows Defender exclusion (requires admin)"""
        if self.platform != "Windows":
            print("Only available on Windows")
            return False
        
        if not self.check_root_privileges():
            print("❌ Requires administrator privileges")
            return False
        
        try:
            app_path = str(Path(__file__).parent.parent.absolute())
            
            # Add exclusion for application directory
            cmd = [
                "powershell", "-Command",
                f"Add-MpPreference -ExclusionPath '{app_path}' -Force"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self._log_event("Windows Defender exclusion created", level="security")
                print(f"✓ Added Windows Defender exclusion for: {app_path}")
                return True
            else:
                print(f"❌ Failed to add exclusion: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating exclusion: {e}")
            return False
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security report"""
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║           WiFiNexus Guardian - SECURITY REPORT                   ║
╚══════════════════════════════════════════════════════════════════╝

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Platform: {self.platform}

┌──────────────────────────────────────────────────────────────────┐
│ SECURITY CONFIGURATION                                           │
├──────────────────────────────────────────────────────────────────┤
│ Safety Mode:         {'ENABLED ✓' if self.safety_mode else 'DISABLED ⚠️'}                   
│ Security Level:      {self.security_level.upper()}                            
│ Stealth Mode:        {'ACTIVE ✓' if self.stealth_mode else 'INACTIVE'}                      
│ Legal Accepted:      {'YES ✓' if self.legal_warning_accepted else 'NO ⚠️'}                        
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ PRIVILEGE STATUS                                                 │
├──────────────────────────────────────────────────────────────────┤
│ Running as Admin/Root: {'YES ✓' if self.check_root_privileges() else 'NO ⚠️'}                 
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ AUDIT LOG SUMMARY                                                │
├──────────────────────────────────────────────────────────────────┤
│ Total Events:        {len(self.audit_log)}                                
│ Log File:            {self.log_file}
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ RECOMMENDATIONS                                                  │
├──────────────────────────────────────────────────────────────────┤
"""
        
        for rec in self.recommend_security_improvements():
            report += f"│ {rec}\n"
        
        report += """└──────────────────────────────────────────────────────────────────┘

╔══════════════════════════════════════════════════════════════════╗
║                    REMINDER: USE RESPONSIBLY                     ║
║    This tool is for authorized security testing only!            ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        return report
    
    def validate_environment(self) -> Dict:
        """Validate security environment"""
        validation = {
            'valid': True,
            'checks': [],
            'warnings': [],
            'errors': []
        }
        
        # Check 1: Legal acceptance
        if self.legal_warning_accepted:
            validation['checks'].append("Legal warning accepted ✓")
        else:
            validation['warnings'].append("Legal warning not accepted")
        
        # Check 2: Safety mode
        if self.safety_mode:
            validation['checks'].append("Safety mode enabled ✓")
        else:
            validation['warnings'].append("Safety mode disabled")
        
        # Check 3: Privileges
        if self.check_root_privileges():
            validation['checks'].append("Running with elevated privileges ✓")
        else:
            validation['warnings'].append("Not running as admin/root")
        
        # Check 4: Config file integrity
        if self.config_file.exists():
            validation['checks'].append("Configuration file exists ✓")
        else:
            validation['checks'].append("Creating new configuration file")
            self._save_config()
        
        # Check 5: Log file writable
        try:
            with open(self.log_file, 'a') as f:
                f.write("")
            validation['checks'].append("Audit log writable ✓")
        except:
            validation['errors'].append("Cannot write to audit log")
            validation['valid'] = False
        
        return validation



    def cleanup_all(self):
        """Clean up all monitored and active processes"""
        cleaned = 0
        
        # Clean active processes
        for proc in self.active_processes:
            try:
                if proc.poll() is None:  # Process still running
                    proc.terminate()
                    cleaned += 1
            except Exception:
                pass
        
        # Clear monitored processes
        self.monitored_processes.clear()
        self.active_processes.clear()
        
        self._log_event(f"Cleaned up {cleaned} processes", level="info")
        return cleaned

# Singleton instance
_security_manager_instance = None

def get_security_manager() -> SecurityManager:
    """Get singleton SecurityManager instance"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager()
    return _security_manager_instance


if __name__ == "__main__":
    print("="*70)
    print("WiFiNexus Guardian - Security & Safety Module")
    print("="*70)
    
    sec_mgr = SecurityManager()
    
    # Show legal warning
    sec_mgr.show_legal_warning()
    
    # Get security status
    print("\n📊 Security Status:")
    status = sec_mgr.get_security_status()
    for key, value in status.items():
        print(f"  • {key}: {value}")
    
    # Validate environment
    print("\n🔍 Environment Validation:")
    validation = sec_mgr.validate_environment()
    for check in validation['checks']:
        print(f"  ✓ {check}")
    for warning in validation['warnings']:
        print(f"  ⚠️ {warning}")
    for error in validation['errors']:
        print(f"  ❌ {error}")
    
    # Get recommendations
    print("\n💡 Security Recommendations:")
    for rec in sec_mgr.recommend_security_improvements():
        print(f"  {rec}")
    
    # Generate report
    print("\n" + sec_mgr.generate_security_report())
    
    print("\n✓ Security module ready")
    print("="*70)
