#!/bin/bash
# Home Scout - VENTUNO Q Setup Script
# Run this on a fresh VENTUNO Q with Ubuntu 24.04

set -e

echo "=== Home Scout VENTUNO Q Setup ==="

# Run the dev setup first
"$(dirname "$0")/setup-dev.sh"

# Download AI models
echo "Downloading AI models..."
"$(dirname "$0")/download-models.sh" /home/scout/models

# Configure ScoutNet WiFi AP
echo "Configuring ScoutNet WiFi AP..."
echo "TODO: Configure hostapd for ScoutNet AP"
echo "  SSID: ScoutNet (hidden)"
echo "  Subnet: 10.0.77.0/24"
echo "  Security: WPA3-SAE"
echo "  Gateway: none (no internet)"

# Disable unnecessary network services
echo "Hardening network..."
echo "TODO: Disable avahi, cups, snapd network access"
echo "TODO: Configure firewall (ufw) to block all outbound"

# Create data directories
mkdir -p /home/scout/data
mkdir -p /home/scout/models
mkdir -p /home/scout/maps

echo ""
echo "=== VENTUNO Q setup complete ==="
echo "Run: ros2 launch scout_bringup scout_voice_only.launch.py"
