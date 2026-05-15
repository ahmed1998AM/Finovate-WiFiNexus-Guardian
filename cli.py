"""
WiFiNexus Guardian - Complete Command Line Interface
Professional wireless intelligence platform with all advanced features
Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)
© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved
"""

import sys
import os
import argparse
from pathlib import Path

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'network'))


def print_banner():
    """Display application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ██╗    ██╗██╗███╗   ██╗███╗   ██╗███████╗██████╗             ║
║     ██║    ██║██║████╗  ██║████╗  ██║██╔════╝██╔══██╗            ║
║     ██║ █╗ ██║██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝            ║
║     ██║███╗██║██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗            ║
║     ╚███╔███╔╝██║██║ ╚████║██║ ╚████║███████╗██║  ██║            ║
║      ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝            ║
║                                                                  ║
║              WiFiNEXUS GUARDIAN v1.0.0                           ║
║       Professional Wireless Intelligence Platform                ║
║                                                                  ║
║  Developer: Ahmed Mostafa Ibrahim (Finovate – AHMED EG)          ║
║  © 2025 Ahmed Mostafa Ibrahim — All Rights Reserved              ║
╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def cmd_scan(args):
    """Execute network scan command"""
    from network.advanced_scanner import AdvancedNetworkScanner
    
    print("\n📡 Starting WiFi Network Scan...")
    scanner = AdvancedNetworkScanner()
    
    results = scanner.scan_networks(
        band=args.band,
        duration=args.duration
    )
    
    print(f"\n📊 Scan Results:")
    print(f"  Total Networks: {scanner.total_networks}")
    print(f"  Secure Networks: {scanner.secure_networks}")
    print(f"  Open Networks: {scanner.open_networks}")
    print(f"  Hidden Networks: {scanner.hidden_count}")
    
    if args.verbose:
        print(f"\n📡 Detected Networks:")
        for network in results:
            signal_icon = "🟢" if network['signal_strength'] > -60 else "🟡" if network['signal_strength'] > -75 else "🔴"
            lock_icon = "🔒" if network['security'] != 'Open' else "🔓"
            hidden_icon = "👻" if network['is_hidden'] else ""
            print(f"  {signal_icon} {lock_icon} {network['ssid']} ({network['signal_strength']} dBm) [{network['band']}] {hidden_icon}")
    
    if args.export:
        scanner.export_results(format=args.export, filename=args.output)
    
    return 0


def cmd_interfaces(args):
    """Execute interface management command"""
    from network.interface_manager import NetworkInterfaceManager
    
    print("\n🔍 Scanning Network Interfaces...")
    manager = NetworkInterfaceManager()
    manager.scan_all_interfaces()
    
    if args.display:
        manager.display_all_interfaces()
    
    if args.preferred:
        preferred = manager.get_preferred_interface()
        if preferred:
            print(f"\n🎯 Preferred Interface: {preferred.name}")
            print(f"   MAC: {preferred.mac}")
            print(f"   Type: {preferred.type}")
            print(f"   External: {'Yes' if preferred.is_external else 'No'}")
            print(f"   Monitor Mode: {'Capable' if preferred.monitor_mode_capable else 'Not Supported'}")
    
    if args.export:
        manager.export_interfaces(format=args.export, filename=args.output)
    
    return 0


def cmd_capture(args):
    """Execute handshake capture command"""
    from network.handshake_capturer import HandshakeCapturer
    
    print("\n📡 Starting Handshake Capture...")
    capturer = HandshakeCapturer()
    
    # Check requirements
    print("\n🔧 Checking requirements...")
    reqs = capturer.check_requirements()
    for tool, installed in reqs.items():
        status = "✓" if installed else "✗"
        print(f"  {status} {tool}")
    
    if args.target:
        print(f"\n🎯 Targeted capture mode:")
        print(f"   BSSID: {args.target}")
        print(f"   Channel: {args.channel}")
        
        capture_file = capturer.capture_handshake_targeted(
            target_bssid=args.target,
            channel=int(args.channel) if args.channel else None,
            timeout=args.timeout
        )
        
        if capture_file:
            print(f"\n✓ Handshake captured: {capture_file}")
        else:
            print("\n✗ Failed to capture handshake")
    else:
        print(f"\n📡 Passive capture mode (duration: {args.timeout}s)")
        capture_file = capturer.start_capture(duration=args.timeout)
        print(f"Capture file: {capture_file}")
    
    return 0


def cmd_crack(args):
    """Execute handshake cracking command"""
    from network.handshake_cracker import HandshakeCracker
    
    print("\n🔑 Starting Handshake Cracking...")
    cracker = HandshakeCracker()
    
    if not os.path.exists(args.capture):
        print(f"❌ Capture file not found: {args.capture}")
        return 1
    
    if args.ai:
        print("\n🤖 Using AI-powered cracking...")
        result = cracker.crack_with_ai(args.capture, use_advanced=True)
    else:
        wordlist = args.wordlist or cracker.default_wordlists['common']
        print(f"\n📝 Using wordlist: {wordlist}")
        result = cracker.crack_with_wordlist(args.capture, wordlist)
    
    if result['success']:
        print(f"\n✅✅✅ PASSWORD FOUND: {result['password']} ✅✅✅")
        print(f"   Method: {result['method']}")
        print(f"   Time: {result['time_taken']:.2f}s")
    else:
        print(f"\n❌ Password not found")
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    return 0


def cmd_security(args):
    """Execute security management command"""
    from core.security_manager import SecurityManager
    
    print("\n🔒 Security Manager...")
    sec_mgr = SecurityManager()
    
    if args.status:
        status = sec_mgr.get_security_status()
        print("\n📊 Security Status:")
        for key, value in status.items():
            print(f"  • {key}: {value}")
    
    if args.report:
        print(sec_mgr.generate_security_report())
    
    if args.validate:
        validation = sec_mgr.validate_environment()
        print("\n🔍 Environment Validation:")
        for check in validation['checks']:
            print(f"  ✓ {check}")
        for warning in validation['warnings']:
            print(f"  ⚠️ {warning}")
        for error in validation['errors']:
            print(f"  ❌ {error}")
    
    if args.recommendations:
        print("\n💡 Security Recommendations:")
        for rec in sec_mgr.recommend_security_improvements():
            print(f"  {rec}")
    
    return 0


def cmd_monitor(args):
    """Execute device monitoring command"""
    from network.device_monitor import DeviceMonitor
    
    print("\n📱 Starting Device Monitor...")
    monitor = DeviceMonitor()
    
    devices = monitor.scan_devices(duration=args.duration)
    
    print(f"\n📊 Devices Found: {len(devices)}")
    
    if args.verbose:
        for device in devices[:20]:  # Show first 20
            print(f"  • {device.get('mac', 'Unknown')} - {device.get('vendor', 'Unknown')}")
            print(f"    Type: {device.get('type', 'Unknown')}")
            print(f"    First Seen: {device.get('first_seen', 'Unknown')}")
    
    return 0


def cmd_analyze(args):
    """Execute packet analysis command"""
    from network.packet_analyzer_pro import PacketAnalyzerPro
    
    print("\n🔍 Starting Packet Analysis...")
    analyzer = PacketAnalyzerPro()
    
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        return 1
    
    results = analyzer.analyze_pcap(args.file)
    
    if results:
        analyzer.print_summary(results)
        
        if args.export:
            analyzer.export_analysis(results, format=args.export, filename=args.output)
    
    return 0


def cmd_tools(args):
    """Execute external tools management command"""
    from drivers.external_tools_manager import ExternalToolsManager
    
    print("\n🔧 External Tools Manager...")
    manager = ExternalToolsManager()
    
    if args.scan:
        manager.detect_all_tools()
    
    elif args.install:
        manager.install_tool(args.install, auto=args.auto)
    
    elif args.install_recommended:
        manager.install_recommended(auto=args.auto)
    
    elif args.configure:
        manager.configure_tool_path(args.tool, args.path)
    
    elif args.report:
        manager.export_tools_report(args.output)
    
    elif args.interactive:
        manager.display_tools_gui()
    
    else:
        # Default: show status
        manager.detect_all_tools()
        print("\n💡 Use --interactive for full menu or --help for options")
    
    return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WiFiNexus Guardian - Professional Wireless Intelligence Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan --band all --duration 15
  %(prog)s interfaces --display --preferred
  %(prog)s capture --target AA:BB:CC:DD:EE:FF --channel 6
  %(prog)s crack --capture handshake.pcap --ai
  %(prog)s security --status --report
  %(prog)s monitor --duration 30
  %(prog)s analyze --file capture.pcap --export json
  %(prog)s tools --scan
  %(prog)s tools --install aircrack-ng
  %(prog)s tools --install-recommended
  %(prog)s tools --interactive
        """
    )
    
    parser.add_argument('-v', '--version', action='version', version='WiFiNexus Guardian v1.0.0 - Professional Security Edition')
    parser.add_argument('--verbose', '-V', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan WiFi networks')
    scan_parser.add_argument('--band', choices=['2.4GHz', '5GHz', 'all'], default='all', help='Frequency band')
    scan_parser.add_argument('--duration', type=int, default=15, help='Scan duration in seconds')
    scan_parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    scan_parser.add_argument('--output', '-o', help='Output filename')
    scan_parser.set_defaults(func=cmd_scan)
    
    # Interfaces command
    iface_parser = subparsers.add_parser('interfaces', help='Manage network interfaces')
    iface_parser.add_argument('--display', '-d', action='store_true', help='Display all interfaces')
    iface_parser.add_argument('--preferred', '-p', action='store_true', help='Show preferred interface')
    iface_parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    iface_parser.add_argument('--output', '-o', help='Output filename')
    iface_parser.set_defaults(func=cmd_interfaces)
    
    # Capture command
    capture_parser = subparsers.add_parser('capture', help='Capture handshakes')
    capture_parser.add_argument('--target', '-t', help='Target BSSID')
    capture_parser.add_argument('--channel', '-c', help='Target channel')
    capture_parser.add_argument('--timeout', type=int, default=120, help='Capture timeout')
    capture_parser.set_defaults(func=cmd_capture)
    
    # Crack command
    crack_parser = subparsers.add_parser('crack', help='Crack handshakes')
    crack_parser.add_argument('--capture', '-i', required=True, help='Capture file (pcap/hccapx)')
    crack_parser.add_argument('--wordlist', '-w', help='Wordlist file')
    crack_parser.add_argument('--ai', action='store_true', help='Use AI-powered cracking')
    crack_parser.set_defaults(func=cmd_crack)
    
    # Security command
    security_parser = subparsers.add_parser('security', help='Security management')
    security_parser.add_argument('--status', '-s', action='store_true', help='Show security status')
    security_parser.add_argument('--report', '-r', action='store_true', help='Generate security report')
    security_parser.add_argument('--validate', '-v', action='store_true', help='Validate environment')
    security_parser.add_argument('--recommendations', '-R', action='store_true', help='Show recommendations')
    security_parser.set_defaults(func=cmd_security)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor devices')
    monitor_parser.add_argument('--duration', type=int, default=30, help='Monitor duration')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # Analyze command (NEW)
    analyze_parser = subparsers.add_parser('analyze', help='Analyze packet captures')
    analyze_parser.add_argument('--file', '-f', required=True, help='PCAP file to analyze')
    analyze_parser.add_argument('--export', choices=['json', 'csv'], help='Export format')
    analyze_parser.add_argument('--output', '-o', help='Output filename')
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Tools command (NEW - External Tools Manager)
    tools_parser = subparsers.add_parser('tools', help='Manage external security tools')
    tools_parser.add_argument('--scan', '-s', action='store_true', help='Scan for installed tools')
    tools_parser.add_argument('--install', '-i', metavar='TOOL', help='Install specific tool')
    tools_parser.add_argument('--install-recommended', action='store_true', help='Install all recommended tools')
    tools_parser.add_argument('--configure', action='store_true', help='Configure custom tool path')
    tools_parser.add_argument('--tool', '-t', help='Tool name for configuration')
    tools_parser.add_argument('--path', '-p', help='Custom path for tool')
    tools_parser.add_argument('--report', '-r', action='store_true', help='Export tools report')
    tools_parser.add_argument('--output', '-o', help='Report output filename')
    tools_parser.add_argument('--interactive', '-I', action='store_true', help='Interactive mode')
    tools_parser.add_argument('--auto', '-a', action='store_true', help='Automatic installation (no prompts)')
    tools_parser.set_defaults(func=cmd_tools)
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return 0
    
    # Print banner for all commands
    print_banner()
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
