# Finovate WiFiNexus Guardian

## Professional Wireless Intelligence Platform

**Version:** 1.0.0  
**Developer:** Ahmed Mostafa Ibrahim (Finovate – AHMED EG)  
**© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved**

---

## 📡 Overview

WiFiNexus Guardian is a professional cross-platform WiFi analysis, monitoring and diagnostics platform with advanced Windows support, AI-powered network intelligence, real-time wireless analytics, and enterprise-grade architecture.

### Key Features

- 🌐 **WiFi Scanning** - Discover and analyze nearby wireless networks
- 📶 **Signal Analysis** - Real-time signal strength monitoring and analytics
- 🔍 **Hidden Network Detection** - Passive discovery of hidden SSIDs
- 📱 **Device Monitoring** - Track connected devices on your network
- 📊 **Packet Analysis** - Authorized packet inspection and protocol analysis
- 📈 **Spectrum Analyzer** - Channel congestion and interference detection
- ⚡ **Speed Test** - Network performance testing
- 🤖 **AI Center** - AI-powered network diagnostics and recommendations
- 📋 **Logs Center** - Comprehensive event and security logging
- 🔌 **Plugin System** - Extensible architecture with plugin support
- 🎨 **Multiple Themes** - Cyber Neon, Dark, and Light themes
- 🔄 **Auto-Updater** - Automatic update checking and installation

---

## 🖥️ System Requirements

### Supported Operating Systems
- Windows 10/11
- Windows Server 2019+
- Linux (Ubuntu, Debian, Fedora, etc.)
- macOS 10.15+

### Hardware Requirements
- **CPU:** Dual-core processor or better
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Network:** WiFi adapter (internal or external)

### Recommended Adapters
- Intel WiFi adapters
- Realtek RTL8812AU based adapters
- Alfa AWUS series
- TP-Link Archer series

---

## 🚀 Installation

### Prerequisites

```bash
# Python 3.8 or higher required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

```txt
PySide6>=6.6.0
psutil>=5.9.0
scapy>=2.5.0
pyshark>=0.6
fastapi>=0.109.0
uvicorn>=0.27.0
sqlite3
```

### Windows-Specific

For full packet capture functionality on Windows:

1. Download Npcap from: https://npcap.com/
2. Install with these options enabled:
   - WinPcap API compatibility mode
   - Raw 802.11 traffic support
3. Restart your computer

---

## 🎯 Usage

### Running the Application

```bash
# From project root directory
python main.py
```

### First Run

On first launch, you will see a legal warning. You must accept to continue:

⚠️ **AUTHORIZED USE ONLY** - This software is for authorized network analysis only.

---

## 📁 Project Structure

```
WiFiNexus Guardian/
├── main.py                 # Application entry point
├── config.py               # Central configuration
├── cli.py                  # Command-line interface
├── core/                   # Core system modules
│   ├── initializer.py      # System initialization
│   ├── hardware_layer.py   # Hardware abstraction
│   ├── security_manager.py # Security management
│   └── process_manager.py  # Process management
├── gui/                    # Graphical user interface
│   └── main_window.py      # Main application window
├── ai/                     # AI engine and intelligence
│   └── ai_engine.py        # Network analysis AI
├── network/                # Network scanning modules
├── attacks/                # Attack modules (authorized use only)
├── defense/                # Defense and monitoring modules
├── forensics/              # Forensic analysis tools
├── automation/             # Automation engine
├── simulation/             # Simulation environment
├── packet_analyzer/        # Packet capture & analysis
├── drivers/                # Driver management
├── adapters/               # Network adapter management
├── plugins/                # Plugin system
│   └── examples/           # Example plugins
├── database/               # Data storage
├── reports/                # Report generation
├── logs/                   # Application logs
├── themes/                 # UI themes
├── assets/                 # Images, icons, resources
├── updates/                # Auto-update system
└── wordlists/              # Password wordlists
```

---

## 🎨 UI Themes

### Available Themes

1. **Cyber Neon** (Default)
   - Primary: #00D9FF (Cyan)
   - Secondary: #00FF88 (Green)
   - Accent: #FF00FF (Magenta)
   - Background: #0A0A0A (Dark)

2. **Dark Mode**
   - Primary: #2196F3 (Blue)
   - Secondary: #03DAC6 (Teal)
   - Background: #121212

3. **Light Mode**
   - Primary: #1976D2 (Blue)
   - Secondary: #424242 (Gray)
   - Background: #FAFAFA

### Changing Theme

Themes can be changed in Settings → Appearance, or programmatically:

```python
from themes import load_stylesheet

stylesheet = load_stylesheet('cyber_neon')
app.setStyleSheet(stylesheet)
```

---

## 🔌 Plugin System

WiFiNexus Guardian supports a plugin ecosystem for extended functionality.

### Creating a Plugin

```bash
# Use the plugin manager to create a template
from plugins.plugin_manager import PluginManager

pm = PluginManager()
pm.initialize()
pm.create_plugin_template("my_custom_plugin")
```

### Plugin Structure

```
plugins/my_plugin/
├── manifest.json    # Plugin metadata
├── plugin.py        # Plugin code
└── README.md        # Documentation
```

### Example Plugin

See `plugins/examples/sample_plugin.py` for a complete working example.

---

## 🤖 AI Integration

Supported AI Providers:
- Ollama (Local LLM)
- OpenAI GPT
- Google Gemini
- Anthropic Claude
- DeepSeek
- Local Models

Configure AI provider in Settings → AI Center.

---

## 📊 Reporting

Export formats supported:
- PDF
- Excel (XLSX)
- CSV
- JSON
- HTML

---

## 🔒 Security & Privacy

### Legal Compliance
- Authorized use only
- No unauthorized access features
- No credential theft capabilities
- No illegal interception tools

### Privacy Features
- Encrypted logs
- Local data protection
- Secure report export
- Session isolation
- Permission-based modules

---

## 🏢 Enterprise Edition

WiFiNexus Guardian Enterprise includes:
- Centralized monitoring
- Cloud dashboard
- Multi-site management
- SIEM integration
- Advanced reporting
- API access
- RBAC permissions

Contact: gogom8870@gmail.com

---

## 🛣️ Roadmap

### Version 1.0.0 (Current Release)
- ✅ Core UI and GUI
- ✅ WiFi scanning and analysis
- ✅ Windows integration with Npcap
- ✅ Signal analytics
- ✅ AI-powered network analysis
- ✅ Plugin system
- ✅ Multiple themes
- ✅ Auto-updater
- ✅ Automation engine
- ✅ Forensic analysis tools
- ✅ WIDS monitoring
- ✅ Evil Twin engine (authorized testing)
- ✅ PMKID attack module
- ✅ Handshake capture/cracking

### Future Versions
- 📅 Cloud sync and dashboard
- 📅 Enterprise deployment tools
- 📅 Distributed monitoring
- 📅 Plugin marketplace
- 📅 Mobile companion app

---

## 📞 Support & Contact

**Developer:** Ahmed Mostafa Ibrahim  
**Brand:** Finovate – AHMED EG  
**Email:** gogom8870@gmail.com  
**Phone:** 01225155329  

**GitHub:** https://github.com/ahmed1998AM  
**Facebook:** https://www.facebook.com/profile.php?id=100049475271023

---

## 📄 License

© 2025 Ahmed Mostafa Ibrahim — All Rights Reserved

Commercial + Community Edition

---

## ⚠️ Legal Disclaimer

This software is provided for authorized network analysis and educational purposes only. Users are responsible for complying with all applicable laws and regulations. Unauthorized access to computer networks is illegal.

The developer assumes no liability for misuse of this software.

---

**Built with ❤️ by Finovate**
