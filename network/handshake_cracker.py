"""
Handshake Cracker Module - Professional WPA/WPA2 Password Cracking
Supports Wordlist attacks and AI-powered password generation
Legal Use Only: Authorized security testing and network auditing
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import subprocess
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
import json
import hashlib


class HandshakeCracker:
    """
    Professional Handshake Cracker with multiple attack modes
    - Wordlist Attack
    - Dictionary Attack with Rules
    - AI-Powered Password Generation
    - Brute Force (limited)
    """
    
    def __init__(self):
        self.platform = "Linux"  # Default to Linux for aircrack-ng compatibility
        self.capture_dir = Path("captures")
        self.capture_dir.mkdir(exist_ok=True)
        self.wordlists_dir = Path("wordlists")
        self.wordlists_dir.mkdir(exist_ok=True)
        
        # Default wordlists
        self.default_wordlists = {
            "rockyou": str(self.wordlists_dir / "rockyou.txt"),
            "common": str(self.wordlists_dir / "common_passwords.txt"),
            "ai_generated": str(self.wordlists_dir / "ai_passwords.txt")
        }
        
        # Create common passwords wordlist
        self._create_common_wordlist()
        
        # Crack statistics
        self.crack_attempts = 0
        self.successful_cracks = 0
        self.last_crack_time = None
    
    def _create_common_wordlist(self):
        """Create common passwords wordlist"""
        common_passwords = [
            "password", "123456", "12345678", "123456789", "qwerty",
            "abc123", "monkey", "1234567", "letmein", "trustno1",
            "dragon", "baseball", "iloveyou", "master", "sunshine",
            "ashley", "bailey", "shadow", "123123", "654321",
            "superman", "qazwsx", "michael", "football", "password1",
            "password123", "welcome", "jesus", "ninja", "mustang",
            "password1234", "admin", "admin123", "root", "toor",
            "wifi1234", "wifi123", "wireless", "network", "internet",
            "TP-LINK", "TP-LINK_1234", "NETGEAR", "Linksys", "D-Link",
            "Huawei", "ZTE", "Cisco", "Belkin", "Arris",
            "guest", "user", "test", "demo", "default"
        ]
        
        wordlist_path = self.wordlists_dir / "common_passwords.txt"
        with open(wordlist_path, 'w') as f:
            f.write('\n'.join(common_passwords))
    
    def crack_with_wordlist(self, capture_file: str, wordlist: str, 
                           timeout: int = 3600) -> Dict:
        """
        Attempt to crack handshake using wordlist
        
        Args:
            capture_file: Path to pcap or hccapx file
            wordlist: Path to wordlist file
            timeout: Maximum time in seconds
        
        Returns:
            Dictionary with crack results
        """
        result = {
            "success": False,
            "password": None,
            "method": "wordlist",
            "wordlist_used": wordlist,
            "time_taken": None,
            "error": None
        }
        
        if not os.path.exists(capture_file):
            result["error"] = f"Capture file not found: {capture_file}"
            return result
        
        if not os.path.exists(wordlist):
            result["error"] = f"Wordlist not found: {wordlist}"
            return result
        
        start_time = time.time()
        print(f"\n🔑 Starting wordlist attack...")
        print(f"📁 Capture: {capture_file}")
        print(f"📝 Wordlist: {wordlist}")
        
        try:
            # Use aircrack-ng
            cmd = ["aircrack-ng", "-w", wordlist, capture_file]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            
            result["time_taken"] = time.time() - start_time
            
            # Check for success
            if "KEY FOUND" in stdout:
                match = re.search(r'KEY FOUND! \[ ([^\]]+) \]', stdout)
                if match:
                    password = match.group(1)
                    result["success"] = True
                    result["password"] = password
                    self.successful_cracks += 1
                    print(f"\n✅✅✅ PASSWORD FOUND: {password} ✅✅✅")
                    
                    # Log successful crack
                    self._log_crack_result(capture_file, password, "wordlist")
                    
                    return result
            
            # Try hashcat if available
            if self._check_hashcat():
                print(f"\n🔄 Trying hashcat...")
                return self._crack_with_hashcat(capture_file, wordlist, result)
            
            result["error"] = "Password not found in wordlist"
            print(f"❌ Password not found")
            
        except subprocess.TimeoutExpired:
            result["error"] = "Crack operation timed out"
            print(f"⏱️ Operation timed out")
        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Error: {e}")
        
        self.crack_attempts += 1
        return result
    
    def _crack_with_hashcat(self, capture_file: str, wordlist: str, 
                           base_result: Dict) -> Dict:
        """Use hashcat for cracking (faster than aircrack-ng)"""
        try:
            # Convert to hccapx if needed
            hccapx_file = capture_file.replace('.pcap', '.hccapx')
            if not os.path.exists(hccapx_file):
                subprocess.run(["cap2hccapx", capture_file, hccapx_file],
                             capture_output=True, timeout=30)
            
            if not os.path.exists(hccapx_file):
                return base_result
            
            # Get hash mode
            hash_mode = "2500"  # WPA-EAPOL-PBKDF2
            
            cmd = [
                "hashcat",
                "-m", hash_mode,
                "-a", "0",  # Dictionary attack
                "-o", "cracked.txt",
                "--force",
                hccapx_file,
                wordlist
            ]
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            
            if os.path.exists("cracked.txt"):
                with open("cracked.txt", 'r') as f:
                    line = f.readline().strip()
                    if ':' in line:
                        password = line.split(':')[-1]
                        base_result["success"] = True
                        base_result["password"] = password
                        base_result["method"] = "hashcat"
                        print(f"\n✅ PASSWORD FOUND (hashcat): {password}")
                        os.remove("cracked.txt")
            
            return base_result
            
        except Exception as e:
            print(f"Hashcat error: {e}")
            return base_result
    
    def crack_with_ai(self, capture_file: str, use_advanced: bool = True) -> Dict:
        """
        Crack handshake using AI-generated passwords
        
        Args:
            capture_file: Path to capture file
            use_advanced: Use advanced password generation
        
        Returns:
            Dictionary with crack results
        """
        print(f"\n🤖 Starting AI-powered password cracking...")
        
        # Generate AI passwords
        passwords = self.generate_ai_passwords(use_advanced)
        
        # Save to temp wordlist
        ai_wordlist = str(self.wordlists_dir / "ai_passwords.txt")
        with open(ai_wordlist, 'w') as f:
            f.write('\n'.join(passwords))
        
        print(f"📝 Generated {len(passwords)} AI passwords")
        
        # Try cracking
        result = self.crack_with_wordlist(capture_file, ai_wordlist, timeout=1800)
        result["method"] = "ai_powered"
        result["passwords_tried"] = len(passwords)
        
        return result
    
    def generate_ai_passwords(self, advanced: bool = True) -> List[str]:
        """
        Generate passwords using AI patterns and rules
        
        Args:
            advanced: Use advanced generation techniques
        
        Returns:
            List of generated passwords
        """
        passwords = set()
        
        # Base patterns
        base_words = [
            "password", "admin", "wifi", "wireless", "network",
            "internet", "router", "modem", "connect", "secure",
            "home", "office", "guest", "private", "public"
        ]
        
        # Common substitutions
        substitutions = {
            'a': '@', 'e': '3', 'i': '1', 'o': '0',
            's': '$', 't': '7', 'l': '!', 'b': '8'
        }
        
        # Numbers and special chars
        numbers = ["", "1", "12", "123", "1234", "2024", "2025", "00", "01"]
        specials = ["", "!", "@", "#", "$", ".", "_"]
        
        # Generate variations
        for word in base_words:
            # Basic variations
            passwords.add(word)
            passwords.add(word.upper())
            passwords.add(word.capitalize())
            
            # With numbers
            for num in numbers:
                passwords.add(word + num)
                passwords.add(num + word)
                passwords.add(word.upper() + num)
            
            # With specials
            for spec in specials:
                passwords.add(word + spec)
                passwords.add(spec + word)
            
            # Combined
            for num in numbers[:5]:
                for spec in specials[:3]:
                    passwords.add(word + num + spec)
                    passwords.add(word + spec + num)
        
        # Router-specific defaults
        router_defaults = self._get_router_defaults()
        passwords.update(router_defaults)
        
        # Advanced patterns
        if advanced:
            advanced_patterns = self._generate_advanced_patterns()
            passwords.update(advanced_patterns)
        
        return list(passwords)
    
    def _get_router_defaults(self) -> List[str]:
        """Get default passwords for common routers"""
        defaults = []
        
        # TP-Link
        for i in range(1000, 9999):
            defaults.append(f"TP-LINK_{i}")
            defaults.append(f"tplink{i}")
        
        # Netgear
        defaults.extend([
            "NETGEAR123", "netgear123", "NETGEAR1234",
            "admin123", "password123"
        ])
        
        # D-Link
        defaults.extend([
            "D-Link1234", "dlink1234", "admin", ""
        ])
        
        # Huawei
        defaults.extend([
            "Huawei1234", "huawei1234", "Admin@huawei"
        ])
        
        # ZTE
        defaults.extend([
            "ZTE12345678", "zte12345678"
        ])
        
        return defaults
    
    def _generate_advanced_patterns(self) -> List[str]:
        """Generate advanced password patterns"""
        patterns = []
        
        # Pattern: Word + Special + Number
        words = ["wifi", "password", "admin", "network"]
        for word in words:
            for num in range(100):
                patterns.append(f"{word}{num}")
                patterns.append(f"{word.upper()}{num}")
                patterns.append(f"{word.capitalize()}{num}")
        
        # Pattern: Date-based
        for year in [2020, 2021, 2022, 2023, 2024, 2025]:
            for month in range(1, 13):
                patterns.append(f"wifi{year}{month:02d}")
                patterns.append(f"password{year}{month:02d}")
        
        # Pattern: Keyboard walks
        keyboard_walks = [
            "qwerty", "asdfgh", "zxcvbn", "123qwe",
            "qazwsx", "1qaz2wsx", "qwerty123"
        ]
        patterns.extend(keyboard_walks)
        
        return patterns
    
    def _check_hashcat(self) -> bool:
        """Check if hashcat is available"""
        try:
            result = subprocess.run(["hashcat", "--version"],
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _log_crack_result(self, capture_file: str, password: str, method: str):
        """Log successful crack to file"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "capture_file": capture_file,
            "password": password,
            "method": method
        }
        
        log_file = self.capture_dir / "crack_log.json"
        
        logs = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get crack statistics"""
        return {
            "total_attempts": self.crack_attempts,
            "successful_cracks": self.successful_cracks,
            "success_rate": f"{(self.successful_cracks/max(1,self.crack_attempts)*100):.1f}%",
            "last_crack_time": self.last_crack_time
        }


if __name__ == "__main__":
    print("="*60)
    print("WiFiNexus Guardian - Handshake Cracker")
    print("="*60)
    
    cracker = HandshakeCracker()
    
    print("\n📁 Wordlists available:")
    for name, path in cracker.default_wordlists.items():
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {exists} {name}: {path}")
    
    print("\n📊 Statistics:")
    stats = cracker.get_statistics()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    print("\n" + "="*60)
    print("Ready for cracking operations")
    print("="*60)
