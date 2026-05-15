#!/bin/bash
# WiFiNexus Guardian - Quick Start Script
# سكريبت التشغيل السريع

echo "=========================================="
echo "  WiFiNexus Guardian - Quick Start"
echo "=========================================="

# Check Python version
python3 --version

# Run validation first
echo ""
echo "[1/3] Validating environment..."
python3 tools/validator.py --json > /tmp/validation_report.json 2>&1 || echo "Validation report generated."

# Run simulation demo (Safe Mode)
echo ""
echo "[2/3] Running Simulation Demo (Safe Mode)..."
python3 simulation/network_simulator.py

# Show help
echo ""
echo "[3/3] Available Commands:"
echo "  python3 main.py              # Launch GUI"
echo "  python3 cli.py --help        # CLI Help"
echo "  python3 installers/auto_installer.py  # Install Dependencies"
echo ""
echo "=========================================="
echo "Ready to launch!"
echo "=========================================="
