"""
Tool Validator for WiFiNexus Guardian
Comprehensive validation of external tools, versions, and dependencies.
"""

import logging
import shutil
import subprocess
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToolStatus(Enum):
    NOT_INSTALLED = "not_installed"
    OUTDATED = "outdated"
    COMPATIBLE = "compatible"
    VERSION_MISMATCH = "version_mismatch"
    PERMISSION_DENIED = "permission_denied"

@dataclass
class ToolInfo:
    name: str
    status: ToolStatus
    version: Optional[str] = None
    path: Optional[str] = None
    min_version: Optional[str] = None
    recommended_version: Optional[str] = None
    message: str = ""

class RequiredTool:
    """Definition of a required external tool"""
    def __init__(
        self,
        name: str,
        package_names: List[str],
        version_check_cmd: List[str],
        min_version: Optional[str] = None,
        critical: bool = True,
        description: str = ""
    ):
        self.name = name
        self.package_names = package_names  # Different names on different OS
        self.version_check_cmd = version_check_cmd
        self.min_version = min_version
        self.critical = critical
        self.description = description

class ToolValidator:
    """
    Validates all required external tools for WiFiNexus Guardian
    """
    
    REQUIRED_TOOLS = [
        RequiredTool(
            name="aircrack-ng",
            package_names=["aircrack-ng"],
            version_check_cmd=["aircrack-ng", "--help"],
            min_version="1.6",
            critical=True,
            description="WiFi security auditing suite"
        ),
        RequiredTool(
            name="airodump-ng",
            package_names=["aircrack-ng"],
            version_check_cmd=["airodump-ng", "--help"],
            min_version="1.6",
            critical=True,
            description="Packet capture tool"
        ),
        RequiredTool(
            name="aireplay-ng",
            package_names=["aircrack-ng"],
            version_check_cmd=["aireplay-ng", "--help"],
            min_version="1.6",
            critical=True,
            description="Packet injection tool"
        ),
        RequiredTool(
            name="hashcat",
            package_names=["hashcat"],
            version_check_cmd=["hashcat", "--version"],
            min_version="6.0",
            critical=False,
            description="GPU-accelerated password recovery"
        ),
        RequiredTool(
            name="hcxdumptool",
            package_names=["hcxdumptool"],
            version_check_cmd=["hcxdumptool", "-v"],
            min_version="6.0",
            critical=False,
            description="WiFi security tool for capturing PMKID"
        ),
        RequiredTool(
            name="hcxpcapngtool",
            package_names=["hcftools"],
            version_check_cmd=["hcxpcapngtool", "-v"],
            min_version="6.0",
            critical=False,
            description="Convert pcap to hashcat format"
        ),
        RequiredTool(
            name="tshark",
            package_names=["wireshark-common", "wireshark"],
            version_check_cmd=["tshark", "--version"],
            min_version="3.0",
            critical=False,
            description="Network protocol analyzer"
        ),
        RequiredTool(
            name="reaver",
            package_names=["reaver", "reaver-wps"],
            version_check_cmd=["reaver", "--help"],
            min_version="1.4",
            critical=False,
            description="WPS attack tool"
        ),
        RequiredTool(
            name="bully",
            package_names=["bully"],
            version_check_cmd=["bully", "--version"],
            min_version="1.0",
            critical=False,
            description="WPS brute force tool"
        ),
        RequiredTool(
            name="macchanger",
            package_names=["macchanger"],
            version_check_cmd=["macchanger", "--version"],
            min_version=None,
            critical=False,
            description="MAC address changer"
        ),
        RequiredTool(
            name="iw",
            package_names=["iw"],
            version_check_cmd=["iw", "version"],
            min_version=None,
            critical=True,
            description="Wireless device configuration"
        ),
        RequiredTool(
            name="ip",
            package_names=["iproute2"],
            version_check_cmd=["ip", "-V"],
            min_version=None,
            critical=True,
            description="Network interface management"
        )
    ]
    
    def __init__(self):
        self.tool_results: Dict[str, ToolInfo] = {}
        
    def validate_all(self) -> Dict[str, ToolInfo]:
        """Validate all required tools"""
        logger.info("Starting comprehensive tool validation...")
        
        for tool in self.REQUIRED_TOOLS:
            result = self._validate_tool(tool)
            self.tool_results[tool.name] = result
            
            if result.critical and result.status != ToolStatus.COMPATIBLE:
                logger.error(f"Critical tool {tool.name} is not properly installed: {result.message}")
            elif result.status == ToolStatus.OUTDATED:
                logger.warning(f"Tool {tool.name} is outdated: {result.version}")
        
        return self.tool_results
    
    def _validate_tool(self, tool: RequiredTool) -> ToolInfo:
        """Validate a single tool"""
        # Check if command exists
        cmd_path = shutil.which(tool.package_names[0])
        
        if not cmd_path:
            # Try alternative package names
            for alt_name in tool.package_names[1:]:
                cmd_path = shutil.which(alt_name)
                if cmd_path:
                    break
        
        if not cmd_path:
            return ToolInfo(
                name=tool.name,
                status=ToolStatus.NOT_INSTALLED,
                message=f"{tool.name} is not installed. Install with: {' or '.join(tool.package_names)}"
            )
        
        # Get version
        version = self._get_version(tool.version_check_cmd)
        
        if not version:
            return ToolInfo(
                name=tool.name,
                status=ToolStatus.PERMISSION_DENIED,
                path=cmd_path,
                message=f"Cannot execute {tool.name}. Check permissions."
            )
        
        # Check version compatibility
        status = ToolStatus.COMPATIBLE
        message = f"{tool.name} v{version} found at {cmd_path}"
        
        if tool.min_version and version:
            if not self._version_compare(version, tool.min_version):
                status = ToolStatus.OUTDATED
                message = f"{tool.name} v{version} is outdated. Minimum required: {tool.min_version}"
        
        return ToolInfo(
            name=tool.name,
            status=status,
            version=version,
            path=cmd_path,
            min_version=tool.min_version,
            message=message
        )
    
    def _get_version(self, check_cmd: List[str]) -> Optional[str]:
        """Extract version from command output"""
        try:
            result = subprocess.run(
                check_cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout + result.stderr
            
            # Common version patterns
            patterns = [
                r'version\s+([\d\.]+)',
                r'v?([\d\.]+)',
                r'(\d+\.\d+(?:\.\d+)?)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            # If no pattern matches, return first line
            if output:
                return output.split('\n')[0][:50]
                
        except Exception as e:
            logger.debug(f"Failed to get version: {e}")
        
        return None
    
    def _version_compare(self, version: str, min_version: str) -> bool:
        """Compare two version strings"""
        def normalize(v):
            return [int(x) for x in re.sub(r'[^\d.]', '', v).split('.') if x.isdigit()]
        
        try:
            v1 = normalize(version)
            v2 = normalize(min_version)
            
            # Pad shorter version with zeros
            while len(v1) < len(v2):
                v1.append(0)
            while len(v2) < len(v1):
                v2.append(0)
            
            return v1 >= v2
        except Exception:
            return True  # Assume compatible if comparison fails
    
    def get_summary(self) -> str:
        """Get validation summary"""
        total = len(self.tool_results)
        installed = sum(1 for r in self.tool_results.values() if r.status != ToolStatus.NOT_INSTALLED)
        compatible = sum(1 for r in self.tool_results.values() if r.status == ToolStatus.COMPATIBLE)
        critical_missing = sum(
            1 for tool in self.REQUIRED_TOOLS 
            if tool.critical and self.tool_results.get(tool.name, ToolInfo(tool.name, ToolStatus.NOT_INSTALLED)).status != ToolStatus.COMPATIBLE
        )
        
        summary = f"""
=== Tool Validation Summary ===
Total Tools Checked: {total}
Installed: {installed}/{total}
Compatible: {compatible}/{total}
Critical Issues: {critical_missing}

"""
        for name, info in self.tool_results.items():
            status_icon = {
                ToolStatus.COMPATIBLE: "✅",
                ToolStatus.OUTDATED: "⚠️",
                ToolStatus.NOT_INSTALLED: "❌",
                ToolStatus.PERMISSION_DENIED: "🔒",
                ToolStatus.VERSION_MISMATCH: "⚠️"
            }.get(info.status, "❓")
            
            summary += f"{status_icon} {name}: {info.message}\n"
        
        return summary
    
    def export_report(self, filepath: str) -> None:
        """Export validation report to file"""
        import json
        from datetime import datetime
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.tool_results),
                "installed": sum(1 for r in self.tool_results.values() if r.status != ToolStatus.NOT_INSTALLED),
                "compatible": sum(1 for r in self.tool_results.values() if r.status == ToolStatus.COMPATIBLE)
            },
            "tools": {
                name: {
                    "status": info.status.value,
                    "version": info.version,
                    "path": info.path,
                    "message": info.message
                }
                for name, info in self.tool_results.items()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Validation report exported to {filepath}")
