"""
External Tools Manager - Install and manage external security tools
Legal Use Only: Authorized security testing and network auditing
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

Features:
- Auto-detect installed tools
- Download and install missing tools
- Configure tool paths
- Update management
- Platform-specific installation
"""

import os
import sys
import platform
import subprocess
import json
import shutil
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ExternalToolsManager:
    """
    Professional External Tools Manager
    Handles installation, configuration, and management of security tools
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.arch = platform.machine()
        self.tools_dir = Path("external_tools")
        self.tools_dir.mkdir(exist_ok=True)
        
        # Tools database with download URLs and installation commands
        self.tools_database = {
            'aircrack-ng': {
                'description': 'WiFi packet capture and cracking suite',
                'category': 'wireless',
                'required_for': ['capture', 'crack', 'monitor'],
                'windows': {
                    'installer_url': 'https://www.aircrack-ng.org/files/aircrack-ng-1.7-win.zip',
                    'manual_install': True,
                    'install_guide': 'https://www.aircrack-ng.org/installation.html',
                    'choco_package': 'aircrack-ng'
                },
                'linux': {
                    'apt': 'aircrack-ng',
                    'yum': 'aircrack-ng',
                    'pacman': 'aircrack-ng',
                    'source_url': 'https://github.com/aircrack-ng/aircrack-ng/archive/refs/tags/1.7.tar.gz'
                },
                'darwin': {
                    'brew': 'aircrack-ng',
                    'macports': 'aircrack-ng'
                }
            },
            'hashcat': {
                'description': 'Advanced password recovery tool',
                'category': 'cracking',
                'required_for': ['crack'],
                'windows': {
                    'installer_url': 'https://hashcat.net/hashcat/hashcat-6.2.6.7z',
                    'manual_install': True,
                    'install_guide': 'https://hashcat.net/wiki/doku.php?id=installation',
                    'choco_package': 'hashcat'
                },
                'linux': {
                    'apt': 'hashcat',
                    'yum': 'hashcat',
                    'pacman': 'hashcat',
                    'source_url': 'https://github.com/hashcat/hashcat/releases/download/v6.2.6/hashcat-6.2.6.tar.gz'
                },
                'darwin': {
                    'brew': 'hashcat',
                    'macports': 'hashcat'
                }
            },
            'npcap': {
                'description': 'Windows packet capture library',
                'category': 'capture',
                'required_for': ['capture', 'analyze'],
                'windows': {
                    'installer_url': 'https://npcap.com/dist/npcap-1.79.exe',
                    'silent_install': '/S',
                    'install_guide': 'https://npcap.com/guide/'
                },
                'linux': None,  # Not needed on Linux
                'darwin': None  # Not needed on macOS
            },
            'wireshark': {
                'description': 'Network protocol analyzer',
                'category': 'analysis',
                'required_for': ['analyze', 'capture'],
                'windows': {
                    'installer_url': 'https://2.na.dl.wireshark.org/win64/Wireshark-win64-4.2.0.exe',
                    'silent_install': '/S',
                    'choco_package': 'wireshark'
                },
                'linux': {
                    'apt': 'wireshark',
                    'yum': 'wireshark',
                    'pacman': 'wireshark-qt'
                },
                'darwin': {
                    'brew': 'wireshark',
                    'macports': 'wireshark'
                }
            },
            'tshark': {
                'description': 'Command-line network analyzer',
                'category': 'analysis',
                'required_for': ['analyze', 'capture'],
                'windows': {
                    'installer_url': 'https://2.na.dl.wireshark.org/win64/Wireshark-win64-4.2.0.exe',
                    'note': 'Included with Wireshark',
                    'choco_package': 'wireshark'
                },
                'linux': {
                    'apt': 'tshark',
                    'yum': 'wireshark-cli',
                    'pacman': 'wireshark-cli'
                },
                'darwin': {
                    'brew': 'wireshark',
                    'macports': 'wireshark'
                }
            },
            'john': {
                'description': 'John the Ripper password cracker',
                'category': 'cracking',
                'required_for': ['crack'],
                'windows': {
                    'installer_url': 'https://github.com/openwall/john/releases/download/v1.9.0-jumbo-1/john-1.9.0-jumbo-1-win64.zip',
                    'manual_install': True,
                    'choco_package': 'john'
                },
                'linux': {
                    'apt': 'john',
                    'yum': 'john',
                    'pacman': 'john'
                },
                'darwin': {
                    'brew': 'john-jumbo',
                    'macports': 'john'
                }
            },
            'reaver': {
                'description': 'WPS attack tool',
                'category': 'wireless',
                'required_for': ['wps_attack'],
                'windows': None,  # Not available on Windows
                'linux': {
                    'apt': 'reaver',
                    'yum': 'reaver',
                    'pacman': 'reaver',
                    'source_url': 'https://github.com/t6x/reaver-wps-fork-t6x/archive/refs/tags/v1.6.3.tar.gz'
                },
                'darwin': {
                    'brew': 'reaver'
                }
            },
            'bully': {
                'description': 'WPS brute force attack tool',
                'category': 'wireless',
                'required_for': ['wps_attack'],
                'windows': None,
                'linux': {
                    'apt': 'bully',
                    'yum': 'bully',
                    'pacman': 'bully'
                },
                'darwin': None
            },
            'hcxdumptool': {
                'description': 'WiFi capture tool for PMKID/Handshake',
                'category': 'wireless',
                'required_for': ['capture'],
                'windows': None,
                'linux': {
                    'apt': 'hcxdumptool',
                    'source_url': 'https://github.com/ZerBea/hcxdumptool/archive/refs/tags/v6.3.4.tar.gz'
                },
                'darwin': None
            },
            'hcxtools': {
                'description': 'WiFi hash conversion tools',
                'category': 'conversion',
                'required_for': ['crack', 'analyze'],
                'windows': None,
                'linux': {
                    'apt': 'hcxtools',
                    'source_url': 'https://github.com/ZerBea/hcxtools/archive/refs/tags/v6.3.4.tar.gz'
                },
                'darwin': None
            }
        }
        
        # Installation status cache
        self.installation_status = {}
        self.tool_paths = {}
        
    def detect_all_tools(self) -> Dict[str, Dict]:
        """Detect all installed tools and their versions"""
        print("\n🔍 Scanning for installed tools...")
        print("=" * 60)
        
        results = {}
        
        for tool_name, tool_info in self.tools_database.items():
            status = self.detect_tool(tool_name)
            results[tool_name] = status
            
            icon = "✅" if status['installed'] else "❌"
            category = tool_info.get('category', 'unknown')
            print(f"{icon} {tool_name:15} - {status['version'] if status['installed'] else 'Not Installed':20} [{category}]")
        
        print("=" * 60)
        
        # Summary
        installed_count = sum(1 for r in results.values() if r['installed'])
        total_count = len(results)
        
        print(f"\n📊 Summary: {installed_count}/{total_count} tools installed")
        
        if installed_count < total_count:
            missing = [name for name, status in results.items() if not status['installed']]
            print(f"⚠️  Missing tools: {', '.join(missing)}")
        
        self.installation_status = results
        return results
    
    def detect_tool(self, tool_name: str) -> Dict:
        """Detect if a specific tool is installed"""
        result = {
            'installed': False,
            'version': 'N/A',
            'path': None,
            'executable': None
        }
        
        try:
            # Try to find the tool executable
            executable = self._find_executable(tool_name)
            
            if executable:
                result['installed'] = True
                result['executable'] = executable
                result['path'] = str(Path(executable).parent)
                
                # Get version
                version = self._get_tool_version(tool_name, executable)
                result['version'] = version
                
                # Store in cache
                self.tool_paths[tool_name] = executable
            
            # Special checks for Windows tools
            if self.platform == "Windows":
                if tool_name == 'npcap':
                    npcap_paths = [
                        r"C:\Program Files\Npcap",
                        r"C:\Program Files (x86)\Npcap",
                        r"C:\Windows\System32\Npcap"
                    ]
                    for path in npcap_paths:
                        if os.path.exists(path):
                            result['installed'] = True
                            result['path'] = path
                            result['version'] = 'Latest'
                            break
                
                elif tool_name == 'hashcat':
                    # Check common hashcat locations
                    hashcat_paths = [
                        r"C:\Program Files\hashcat\hashcat.exe",
                        r"C:\hashcat\hashcat.exe",
                        str(self.tools_dir / 'hashcat' / 'hashcat.exe')
                    ]
                    for path in hashcat_paths:
                        if os.path.exists(path):
                            result['installed'] = True
                            result['executable'] = path
                            result['path'] = str(Path(path).parent)
                            version = self._get_tool_version('hashcat', path)
                            result['version'] = version
                            break
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _find_executable(self, tool_name: str) -> Optional[str]:
        """Find executable path for a tool"""
        # Map tool names to executable names
        executable_map = {
            'aircrack-ng': 'aircrack-ng',
            'hashcat': 'hashcat',
            'wireshark': 'wireshark',
            'tshark': 'tshark',
            'john': 'john',
            'reaver': 'reaver',
            'bully': 'bully',
            'hcxdumptool': 'hcxdumptool',
            'hcxtools': 'hcxpcapngtool'
        }
        
        exe_name = executable_map.get(tool_name, tool_name)
        
        # Try using shutil.which
        exe_path = shutil.which(exe_name)
        if exe_path:
            return exe_path
        
        # Try common locations based on platform
        if self.platform == "Windows":
            common_paths = [
                f"C:\\Program Files\\{tool_name}\\{exe_name}.exe",
                f"C:\\Program Files (x86)\\{tool_name}\\{exe_name}.exe",
                f"C:\\{tool_name}\\{exe_name}.exe"
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def _get_tool_version(self, tool_name: str, executable: str) -> str:
        """Get version string for a tool"""
        try:
            # Common version flags
            version_flags = ['--version', '-version', '-v', '/version']
            
            for flag in version_flags:
                try:
                    result = subprocess.run(
                        [executable, flag],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        # Extract first line or version pattern
                        output = result.stdout.strip().split('\n')[0]
                        return output[:50]  # Limit length
                except:
                    continue
            
            return "Unknown"
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def install_tool(self, tool_name: str, auto: bool = False) -> bool:
        """Install a specific tool"""
        if tool_name not in self.tools_database:
            print(f"❌ Unknown tool: {tool_name}")
            return False
        
        tool_info = self.tools_database[tool_name]
        print(f"\n📦 Installing {tool_name}...")
        print("=" * 60)
        print(f"Description: {tool_info['description']}")
        print(f"Category: {tool_info['category']}")
        print("=" * 60)
        
        # Get platform-specific installation info
        platform_info = tool_info.get(self.platform.lower(), None)
        
        if not platform_info:
            print(f"⚠️  {tool_name} is not available on {self.platform}")
            return False
        
        if self.platform == "Windows":
            return self._install_windows(tool_name, platform_info, auto)
        elif self.platform == "Linux":
            return self._install_linux(tool_name, platform_info, auto)
        elif self.platform == "Darwin":
            return self._install_macos(tool_name, platform_info, auto)
        
        return False
    
    def _install_windows(self, tool_name: str, info: Dict, auto: bool) -> bool:
        """Install tool on Windows"""
        print(f"\n🪟 Windows Installation Method:")
        
        # Method 1: Chocolatey (if available)
        if 'choco_package' in info:
            print("  Trying Chocolatey package manager...")
            if self._check_chocolatey():
                return self._install_with_choco(info['choco_package'])
            else:
                print("  ⚠️  Chocolatey not found")
        
        # Method 2: Direct download
        if 'installer_url' in info:
            print(f"  Downloading from: {info['installer_url']}")
            
            if auto:
                print("  ⚠️  Automatic download requires user confirmation")
                print(f"  Please visit: {info.get('install_guide', 'N/A')}")
                return False
            else:
                print("\n📋 Manual Installation Steps:")
                print(f"  1. Visit: {info['installer_url']}")
                print(f"  2. Download the installer")
                print(f"  3. Run the installer as Administrator")
                print(f"  4. Add installation directory to PATH")
                return True
        
        # Method 3: Manual installation
        if info.get('manual_install'):
            print("\n📋 Manual Installation Required:")
            print(f"  Guide: {info.get('install_guide', 'No guide available')}")
            return True
        
        return False
    
    def _install_linux(self, tool_name: str, info: Dict, auto: bool) -> bool:
        """Install tool on Linux"""
        print(f"\n🐧 Linux Installation Method:")
        
        # Detect package manager
        pkg_manager = self._detect_linux_pkg_manager()
        
        if pkg_manager and pkg_manager in info:
            package_name = info[pkg_manager]
            print(f"  Using {pkg_manager}: {package_name}")
            
            if auto:
                return self._install_with_pkg_manager(pkg_manager, package_name)
            else:
                print(f"\nRun this command:")
                if pkg_manager == 'apt':
                    print(f"  sudo apt update && sudo apt install -y {package_name}")
                elif pkg_manager == 'yum':
                    print(f"  sudo yum install -y {package_name}")
                elif pkg_manager == 'pacman':
                    print(f"  sudo pacman -S --noconfirm {package_name}")
                return True
        
        # Source installation
        if 'source_url' in info:
            print(f"\n📦 Building from source:")
            print(f"  URL: {info['source_url']}")
            print(f"  Steps:")
            print(f"    1. wget {info['source_url']}")
            print(f"    2. tar -xzf *.tar.gz")
            print(f"    3. cd <extracted_dir>")
            print(f"    4. make && sudo make install")
            return True
        
        return False
    
    def _install_macos(self, tool_name: str, info: Dict, auto: bool) -> bool:
        """Install tool on macOS"""
        print(f"\n🍎 macOS Installation Method:")
        
        # Try Homebrew first
        if 'brew' in info:
            print("  Trying Homebrew...")
            if self._check_homebrew():
                if auto:
                    return self._install_with_brew(info['brew'])
                else:
                    print(f"\nRun this command:")
                    print(f"  brew install {info['brew']}")
                    return True
            else:
                print("  ⚠️  Homebrew not found")
        
        # Try MacPorts
        if 'macports' in info:
            print("  Trying MacPorts...")
            print(f"  Command: sudo port install {info['macports']}")
            return True
        
        return False
    
    def _check_chocolatey(self) -> bool:
        """Check if Chocolatey is installed"""
        try:
            result = subprocess.run(
                ['choco', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_homebrew(self) -> bool:
        """Check if Homebrew is installed"""
        try:
            result = subprocess.run(
                ['brew', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _detect_linux_pkg_manager(self) -> Optional[str]:
        """Detect Linux package manager"""
        managers = [
            ('apt', '/usr/bin/apt'),
            ('yum', '/usr/bin/yum'),
            ('pacman', '/usr/bin/pacman'),
            ('dnf', '/usr/bin/dnf'),
            ('zypper', '/usr/bin/zypper')
        ]
        
        for name, path in managers:
            if os.path.exists(path):
                return name
        
        return None
    
    def _install_with_choco(self, package: str) -> bool:
        """Install using Chocolatey"""
        try:
            print(f"  Running: choco install {package} -y")
            result = subprocess.run(
                ['choco', 'install', package, '-y'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"  ✅ {package} installed successfully")
                return True
            else:
                print(f"  ❌ Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def _install_with_pkg_manager(self, manager: str, package: str) -> bool:
        """Install using Linux package manager"""
        try:
            if manager == 'apt':
                cmd = ['sudo', 'apt', 'update', '&&', 'sudo', 'apt', 'install', '-y', package]
                print(f"  Running: sudo apt update && sudo apt install -y {package}")
            elif manager == 'yum':
                cmd = ['sudo', 'yum', 'install', '-y', package]
            elif manager == 'pacman':
                cmd = ['sudo', 'pacman', '-S', '--noconfirm', package]
            else:
                return False
            
            # Note: This is informational - actual install requires user interaction
            print(f"  ℹ️  Package manager installation initiated")
            return True
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def _install_with_brew(self, package: str) -> bool:
        """Install using Homebrew"""
        try:
            print(f"  Running: brew install {package}")
            result = subprocess.run(
                ['brew', 'install', package],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"  ✅ {package} installed successfully")
                return True
            else:
                print(f"  ❌ Installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    def get_recommended_tools(self) -> List[str]:
        """Get list of recommended tools based on usage"""
        recommendations = []
        
        # Core tools for basic functionality
        core_tools = ['aircrack-ng', 'tshark']
        
        # Platform-specific recommendations
        if self.platform == "Windows":
            core_tools.append('npcap')
        elif self.platform == "Linux":
            core_tools.extend(['hcxdumptool', 'hcxtools'])
        
        # Cracking tools
        core_tools.extend(['hashcat', 'john'])
        
        # Check what's missing
        for tool in core_tools:
            if tool in self.tools_database:
                status = self.detect_tool(tool)
                if not status['installed']:
                    recommendations.append(tool)
        
        return recommendations
    
    def install_recommended(self, auto: bool = False) -> Dict[str, bool]:
        """Install all recommended tools"""
        print("\n📦 Installing Recommended Tools...")
        print("=" * 60)
        
        recommendations = self.get_recommended_tools()
        results = {}
        
        if not recommendations:
            print("✅ All recommended tools are already installed!")
            return results
        
        print(f"Tools to install: {', '.join(recommendations)}\n")
        
        for tool in recommendations:
            print(f"\n{'='*60}")
            success = self.install_tool(tool, auto)
            results[tool] = success
        
        return results
    
    def configure_tool_path(self, tool_name: str, custom_path: str) -> bool:
        """Configure custom path for a tool"""
        if not os.path.exists(custom_path):
            print(f"❌ Path does not exist: {custom_path}")
            return False
        
        # Save to config file
        config_file = self.tools_dir / 'tool_paths.json'
        
        config = {}
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except:
                config = {}
        
        config[tool_name] = custom_path
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configured {tool_name} path: {custom_path}")
        self.tool_paths[tool_name] = custom_path
        
        return True
    
    def get_tool_paths_config(self) -> Dict:
        """Get configured tool paths"""
        config_file = self.tools_dir / 'tool_paths.json'
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        
        return {}
    
    def export_tools_report(self, filename: str = None) -> str:
        """Export tools status report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tools_report_{timestamp}.json"
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'platform': self.platform,
            'architecture': self.arch,
            'tools': {}
        }
        
        for tool_name in self.tools_database.keys():
            report['tools'][tool_name] = self.detect_tool(tool_name)
        
        report['recommendations'] = self.get_recommended_tools()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Tools report exported: {filename}")
        return filename
    
    def display_tools_gui(self):
        """Display interactive tools management interface"""
        print("\n" + "=" * 70)
        print("  EXTERNAL TOOLS MANAGER - Interactive Menu")
        print("=" * 70)
        
        while True:
            print("\nOptions:")
            print("  1. Scan for installed tools")
            print("  2. Install a specific tool")
            print("  3. Install all recommended tools")
            print("  4. Configure custom tool path")
            print("  5. Export tools report")
            print("  6. Show tool details")
            print("  7. Return to main menu")
            
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == '1':
                self.detect_all_tools()
            
            elif choice == '2':
                tool_name = input("Enter tool name: ").strip().lower()
                self.install_tool(tool_name, auto=False)
            
            elif choice == '3':
                self.install_recommended(auto=False)
            
            elif choice == '4':
                tool_name = input("Enter tool name: ").strip().lower()
                custom_path = input("Enter custom path: ").strip()
                self.configure_tool_path(tool_name, custom_path)
            
            elif choice == '5':
                self.export_tools_report()
            
            elif choice == '6':
                tool_name = input("Enter tool name: ").strip().lower()
                if tool_name in self.tools_database:
                    info = self.tools_database[tool_name]
                    print(f"\n{'='*60}")
                    print(f"Tool: {tool_name}")
                    print(f"Description: {info['description']}")
                    print(f"Category: {info['category']}")
                    print(f"Required for: {', '.join(info.get('required_for', []))}")
                    
                    platform_info = info.get(self.platform.lower())
                    if platform_info:
                        print(f"\nInstallation on {self.platform}:")
                        for key, value in platform_info.items():
                            print(f"  {key}: {value}")
                    else:
                        print(f"\nNot available on {self.platform}")
                    print("=" * 60)
                else:
                    print(f"❌ Unknown tool: {tool_name}")
            
            elif choice == '7':
                break
            
            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point for tools manager"""
    manager = ExternalToolsManager()
    manager.display_tools_gui()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(0)
