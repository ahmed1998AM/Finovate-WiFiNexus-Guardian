"""
Report Generator - Generate comprehensive security and network analysis reports
Legal Use Only: Authorized security testing and network auditing
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class ReportGenerator:
    """
    Professional Report Generator for WiFiNexus Guardian
    Generates detailed reports in multiple formats (JSON, CSV, HTML, TXT)
    """

    def __init__(self, output_dir: str = "reports_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.report_data = {}
        self.generated_reports = []

    def create_scan_report(self, scan_results: Dict, format: str = "json") -> str:
        """
        Create a comprehensive WiFi scan report

        Args:
            scan_results: Dictionary containing scan results
            format: Output format (json, csv, html, txt)

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"wifi_scan_{timestamp}"

        self.report_data = {
            "report_type": "WiFi Scan Report",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "summary": {
                "total_networks": len(scan_results.get("networks", [])),
                "secure_networks": sum(1 for net in scan_results.get("networks", []) if net.get("security", "Open") != "Open"),
                "open_networks": sum(1 for net in scan_results.get("networks", []) if net.get("security", "Open") == "Open"),
                "hidden_networks": sum(1 for net in scan_results.get("networks", []) if net.get("hidden", False)),
                "band_2_4ghz": sum(1 for net in scan_results.get("networks", []) if net.get("frequency", "").startswith("2.4")),
                "band_5ghz": sum(1 for net in scan_results.get("networks", []) if net.get("frequency", "").startswith("5")),
            },
            "networks": scan_results.get("networks", []),
            "scan_parameters": {
                "interface": scan_results.get("interface", "unknown"),
                "duration": scan_results.get("duration", 0),
                "band": scan_results.get("band", "all"),
            }
        }

        return self._save_report(report_name, format)

    def create_security_report(self, security_status: Dict, format: str = "json") -> str:
        """
        Create a security audit report

        Args:
            security_status: Dictionary containing security status
            format: Output format

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"security_audit_{timestamp}"

        self.report_data = {
            "report_type": "Security Audit Report",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "security_status": security_status,
            "recommendations": self._generate_security_recommendations(security_status),
            "compliance_checklist": self._generate_compliance_checklist(),
        }

        return self._save_report(report_name, format)

    def create_analysis_report(self, analysis_results: Dict, format: str = "json") -> str:
        """
        Create a packet analysis report

        Args:
            analysis_results: Dictionary containing analysis results
            format: Output format

        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"packet_analysis_{timestamp}"

        self.report_data = {
            "report_type": "Packet Analysis Report",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0.0",
            "analysis_summary": analysis_results.get("summary", {}),
            "protocol_breakdown": analysis_results.get("protocols", {}),
            "statistics": analysis_results.get("stats", {}),
            "findings": analysis_results.get("findings", []),
        }

        return self._save_report(report_name, format)

    def _save_report(self, report_name: str, format: str) -> str:
        """
        Save report in specified format

        Args:
            report_name: Base name for the report
            format: Output format

        Returns:
            Path to saved report
        """
        filepath = self.output_dir / f"{report_name}.{format}"

        if format == "json":
            self._save_json(filepath)
        elif format == "csv":
            self._save_csv(filepath)
        elif format == "html":
            self._save_html(filepath)
        elif format == "txt":
            self._save_txt(filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.generated_reports.append(str(filepath))
        return str(filepath)

    def _save_json(self, filepath: Path):
        """Save report as JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False)

    def _save_csv(self, filepath: Path):
        """Save report as CSV"""
        networks = self.report_data.get("networks", [])
        if not networks:
            # If no networks, save summary instead
            summary = self.report_data.get("summary", {})
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Metric", "Value"])
                for key, value in summary.items():
                    writer.writerow([key, value])
            return

        # Save networks as CSV
        fieldnames = list(networks[0].keys()) if networks else []
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(networks)

    def _save_html(self, filepath: Path):
        """Save report as HTML"""
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #0a0a0a; color: #00d9ff; }}
        h1 {{ color: #00d9ff; border-bottom: 2px solid #00d9ff; padding-bottom: 10px; }}
        h2 {{ color: #00ff88; }}
        .summary {{ background: rgba(0, 217, 255, 0.1); padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #00ff88; }}
        .metric-label {{ font-size: 12px; color: #888; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #00d9ff; padding: 10px; text-align: left; }}
        th {{ background: rgba(0, 217, 255, 0.2); }}
        tr:nth-child(even) {{ background: rgba(0, 217, 255, 0.05); }}
        .footer {{ margin-top: 40px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>📊 {title}</h1>
    <p><strong>Generated:</strong> {timestamp}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        {summary_content}
    </div>
    
    <h2>Detailed Data</h2>
    {table_content}
    
    <div class="footer">
        <p>WiFiNexus Guardian v1.0.0 | Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)</p>
        <p>© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved</p>
        <p>⚠️ For authorized security testing and network auditing only</p>
    </div>
</body>
</html>"""

        # Generate summary content
        summary = self.report_data.get("summary", {})
        summary_html = ""
        for key, value in summary.items():
            summary_html += f"""
            <div class="metric">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{key.replace('_', ' ').title()}</div>
            </div>
            """

        # Generate table content
        networks = self.report_data.get("networks", [])
        if networks:
            headers = list(networks[0].keys())
            rows = ""
            for net in networks[:20]:  # Limit to first 20 networks
                row_cells = "".join(f"<td>{net.get(h, 'N/A')}</td>" for h in headers)
                rows += f"<tr>{row_cells}</tr>"
            
            header_cells = "".join(f"<th>{h.replace('_', ' ').title()}</th>" for h in headers)
            table_html = f"""
            <table>
                <thead><tr>{header_cells}</tr></thead>
                <tbody>{rows}</tbody>
            </table>
            <p><em>Showing first {min(len(networks), 20)} of {len(networks)} networks</em></p>
            """
        else:
            table_html = "<p>No detailed data available</p>"

        html_content = html_template.format(
            title=self.report_data.get("report_type", "Report"),
            timestamp=self.report_data.get("generated_at", "Unknown"),
            summary_content=summary_html,
            table_content=table_html
        )

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _save_txt(self, filepath: Path):
        """Save report as plain text"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"{self.report_data.get('report_type', 'Report')}")
        lines.append("=" * 80)
        lines.append(f"Generated: {self.report_data.get('generated_at', 'Unknown')}")
        lines.append(f"Version: {self.report_data.get('version', '1.0.0')}")
        lines.append("")

        # Summary
        summary = self.report_data.get("summary", {})
        if summary:
            lines.append("SUMMARY")
            lines.append("-" * 40)
            for key, value in summary.items():
                lines.append(f"  {key.replace('_', ' ').title()}: {value}")
            lines.append("")

        # Detailed data
        networks = self.report_data.get("networks", [])
        if networks:
            lines.append("NETWORK DETAILS")
            lines.append("-" * 40)
            for i, net in enumerate(networks[:20], 1):
                lines.append(f"\n[{i}] {net.get('ssid', 'Hidden')}")
                for key, value in net.items():
                    if key != 'ssid':
                        lines.append(f"    {key.replace('_', ' ').title()}: {value}")
            if len(networks) > 20:
                lines.append(f"\n... and {len(networks) - 20} more networks")

        lines.append("")
        lines.append("=" * 80)
        lines.append("WiFiNexus Guardian v1.0.0")
        lines.append("Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)")
        lines.append("© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved")
        lines.append("⚠️ For authorized security testing and network auditing only")
        lines.append("=" * 80)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _generate_security_recommendations(self, security_status: Dict) -> List[str]:
        """Generate security recommendations based on status"""
        recommendations = []

        if not security_status.get("safety_mode", True):
            recommendations.append("⚠️ Enable Safety Mode for enhanced protection")

        if security_status.get("security_level") == "low":
            recommendations.append("🔒 Increase security level to medium or high")

        if not security_status.get("legal_accepted", False):
            recommendations.append("📋 Accept legal disclaimer before using advanced features")

        if not security_status.get("stealth_mode", False):
            recommendations.append("👤 Consider enabling Stealth Mode for sensitive operations")

        if not recommendations:
            recommendations.append("✅ All security settings are properly configured")

        return recommendations

    def _generate_compliance_checklist(self) -> Dict[str, bool]:
        """Generate compliance checklist"""
        return {
            "Legal authorization obtained": False,
            "Network owner permission granted": False,
            "Testing within authorized scope": False,
            "Data privacy regulations followed": False,
            "Results documented and secured": False,
            "No unauthorized access attempted": True,
            "Safety mode enabled": True,
        }

    def get_generated_reports(self) -> List[str]:
        """Get list of all generated reports"""
        return self.generated_reports

    def clear_reports(self):
        """Clear all generated reports from memory"""
        self.report_data = {}
        self.generated_reports = []


def main():
    """Test report generation"""
    generator = ReportGenerator()

    # Test scan report
    test_scan = {
        "interface": "wlan0",
        "duration": 10,
        "band": "all",
        "networks": [
            {"ssid": "TestNetwork1", "bssid": "AA:BB:CC:DD:EE:01", "security": "WPA2", "signal": -65, "channel": 6, "frequency": "2.4GHz"},
            {"ssid": "TestNetwork2", "bssid": "AA:BB:CC:DD:EE:02", "security": "WPA3", "signal": -70, "channel": 36, "frequency": "5GHz"},
            {"ssid": "OpenNetwork", "bssid": "AA:BB:CC:DD:EE:03", "security": "Open", "signal": -80, "channel": 11, "frequency": "2.4GHz"},
        ]
    }

    report_path = generator.create_scan_report(test_scan, format="json")
    print(f"✓ Generated scan report: {report_path}")

    report_path = generator.create_scan_report(test_scan, format="html")
    print(f"✓ Generated HTML report: {report_path}")

    report_path = generator.create_scan_report(test_scan, format="txt")
    print(f"✓ Generated TXT report: {report_path}")

    # Test security report
    test_security = {
        "safety_mode": True,
        "security_level": "high",
        "stealth_mode": False,
        "legal_accepted": True,
    }

    report_path = generator.create_security_report(test_security, format="json")
    print(f"✓ Generated security report: {report_path}")

    print(f"\nTotal reports generated: {len(generator.get_generated_reports())}")


if __name__ == "__main__":
    main()
