# Network Isolation Setup

Scout creates its own isolated WiFi network called ScoutNet. This network connects the VENTUNO Q to ESP32-CAM room cameras with zero internet access. No default gateway, no DNS, no forwarding. Data stays on ScoutNet.

This reference covers the full network configuration: hostapd, DHCP, firewall rules, and the `verify-privacy.sh` audit script.

---

## Network Architecture

```
                   ScoutNet WiFi (10.0.77.0/24)
                   Hidden SSID, WPA3-SAE
                          |
        +-----------------+-----------------+
        |                 |                 |
  VENTUNO Q          ESP32-CAM #1     ESP32-CAM #2
  10.0.77.1          10.0.77.11       10.0.77.12
  (AP + DHCP)
        |
        X  (no default gateway, no DNS, no NAT, no internet)
```

Scout (VENTUNO Q) is the access point. It runs hostapd and dnsmasq. ESP32-CAMs and your management device connect as clients. There is no upstream link. Packets cannot leave the 10.0.77.0/24 subnet.

---

## Prerequisites

- VENTUNO Q with Ubuntu 24.04 running (see [VENTUNO Q Setup](ventuno-q-setup.md))
- WiFi adapter capable of AP mode (the VENTUNO Q's onboard WiFi, if present)
- Packages: `hostapd`, `dnsmasq`, `iptables-persistent`

```bash
sudo apt install -y hostapd dnsmasq iptables-persistent
```

---

## Step 1: Configure hostapd (WiFi Access Point)

### Identify the WiFi interface

```bash
iw dev
# Look for the interface name, typically wlan0
```

### Create the hostapd configuration

```bash
sudo tee /etc/hostapd/hostapd.conf << 'EOF'
# ScoutNet Access Point Configuration
interface=wlan0
driver=nl80211

# Network identity
ssid=ScoutNet
ignore_broadcast_ssid=1    # Hidden SSID - devices must know the name to connect

# Radio settings
hw_mode=a                  # 5 GHz band (use 'g' for 2.4 GHz if 5 GHz is unavailable)
channel=36                 # Channel 36 for 5 GHz (adjust to avoid interference)
ieee80211n=1               # 802.11n support
ieee80211ac=1              # 802.11ac support (if hardware supports it)
wmm_enabled=1              # Required for 802.11n/ac

# Security - WPA3-SAE (strongest available)
wpa=2
wpa_key_mgmt=SAE
wpa_pairwise=CCMP
rsn_pairwise=CCMP
ieee80211w=2               # Management frame protection (required for SAE)
sae_password=YOUR_STRONG_PASSWORD_HERE

# Performance
max_num_sta=10             # Max 10 connected devices (4 cameras + management devices)
EOF
```

Replace `YOUR_STRONG_PASSWORD_HERE` with a strong password. This password is used by ESP32-CAMs and your management device to join ScoutNet.

**Important:** If your ESP32-S3-CAMs do not support WPA3-SAE, fall back to WPA2:

```
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=CCMP
wpa_passphrase=YOUR_STRONG_PASSWORD_HERE
```

### Enable hostapd

```bash
# Point the systemd service at our config
sudo sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

# Unmask and enable
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
```

---

## Step 2: Configure the Network Interface

Assign a static IP to the WiFi interface. Do not add a default gateway.

### Using netplan (Ubuntu default)

```bash
sudo tee /etc/netplan/60-scoutnet.yaml << 'EOF'
network:
  version: 2
  wifis:
    wlan0:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.0.77.1/24
      # NO gateway4 - intentional
      # NO nameservers - intentional
EOF

sudo netplan apply
```

### Using NetworkManager (alternative)

```bash
sudo nmcli connection add \
  type wifi \
  ifname wlan0 \
  con-name ScoutNet \
  ssid ScoutNet \
  ipv4.method manual \
  ipv4.addresses 10.0.77.1/24 \
  ipv6.method disabled

# Do NOT set ipv4.gateway or ipv4.dns
```

---

## Step 3: Configure DHCP (dnsmasq)

dnsmasq serves DHCP leases to ESP32-CAMs and management devices. It does not serve DNS.

```bash
sudo tee /etc/dnsmasq.d/scoutnet.conf << 'EOF'
# ScoutNet DHCP Configuration
interface=wlan0
bind-interfaces

# DHCP range
dhcp-range=10.0.77.10,10.0.77.50,255.255.255.0,24h

# Static leases for ESP32-CAMs (optional but recommended)
dhcp-host=AA:BB:CC:DD:EE:01,esp32-cam-1,10.0.77.11
dhcp-host=AA:BB:CC:DD:EE:02,esp32-cam-2,10.0.77.12
dhcp-host=AA:BB:CC:DD:EE:03,esp32-cam-3,10.0.77.13
dhcp-host=AA:BB:CC:DD:EE:04,esp32-cam-4,10.0.77.14

# Do NOT serve DNS
port=0

# Do NOT serve a default gateway
# (omitting dhcp-option=3 means no gateway is advertised)

# Do NOT serve DNS servers to clients
# (port=0 disables DNS, and we do not set dhcp-option=6)
EOF
```

Replace the MAC addresses with your actual ESP32-CAM MAC addresses. Find them by checking the ESP32-CAM serial output during boot, or from your router's DHCP log before setting up ScoutNet.

```bash
sudo systemctl enable dnsmasq
sudo systemctl restart dnsmasq
```

---

## Step 4: Remove Default Routes and DNS

Make sure the VENTUNO Q itself has no route to the internet.

### Remove any existing default route

```bash
# Check for default routes
ip route | grep default

# Delete any that exist
sudo ip route del default

# Verify
ip route
# Should show only: 10.0.77.0/24 dev wlan0 ...
```

### Remove DNS configuration

```bash
# Clear resolv.conf
sudo tee /etc/resolv.conf << 'EOF'
# No DNS - Scout does not resolve domain names
# This is intentional. Do not add nameservers.
EOF

# Prevent NetworkManager or systemd-resolved from overwriting it
sudo chattr +i /etc/resolv.conf
```

### Disable systemd-resolved (if running)

```bash
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo systemctl mask systemd-resolved
```

---

## Step 5: Firewall Rules

Belt and suspenders. Even though there is no default route, add iptables rules to block any outbound traffic that is not destined for ScoutNet.

```bash
# Flush existing rules
sudo iptables -F
sudo iptables -X
sudo iptables -t nat -F

# Default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT DROP

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A OUTPUT -o lo -j ACCEPT

# Allow all traffic on ScoutNet (10.0.77.0/24)
sudo iptables -A INPUT -i wlan0 -s 10.0.77.0/24 -j ACCEPT
sudo iptables -A OUTPUT -o wlan0 -d 10.0.77.0/24 -j ACCEPT

# Allow established connections (for responses to our own traffic)
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Block everything else (default DROP policies handle this, but be explicit)
sudo iptables -A OUTPUT -d 0.0.0.0/0 -j DROP
sudo iptables -A FORWARD -j DROP

# Save rules to persist across reboots
sudo netfilter-persistent save
```

### Verify firewall

```bash
sudo iptables -L -v -n
# OUTPUT chain should show:
#   ACCEPT for 10.0.77.0/24
#   DROP for 0.0.0.0/0
#   No ACCEPT rules for external subnets
```

---

## Step 6: Disable Unused Network Services

Remove or disable anything that might try to reach the internet.

```bash
# Disable automatic updates (no internet anyway, but prevent retry loops)
sudo systemctl disable apt-daily.timer
sudo systemctl disable apt-daily-upgrade.timer

# Disable snapd (if installed)
sudo systemctl disable snapd 2>/dev/null
sudo systemctl mask snapd 2>/dev/null

# Disable cloud-init (if installed)
sudo touch /etc/cloud/cloud-init.disabled

# Disable NTP (no time servers reachable - use RTC or manual time)
sudo timedatectl set-ntp false
```

---

## Step 7: Start ScoutNet

```bash
# Start all services
sudo systemctl start hostapd
sudo systemctl start dnsmasq

# Verify the AP is broadcasting (hidden, so it will not show in normal scans)
sudo hostapd_cli status

# Check the interface
ip addr show wlan0
# Should show 10.0.77.1/24

# Check DHCP leases (after ESP32-CAMs connect)
cat /var/lib/misc/dnsmasq.leases
```

---

## Using verify-privacy.sh

The `verify-privacy.sh` script audits Scout's network configuration. Run it after setup and periodically as a health check.

```bash
~/home-scout/scripts/verify-privacy.sh
```

### What it checks

| Check | Pass Condition | Fail Means |
|-------|---------------|-----------|
| Default gateway | No default route in routing table | Something added an internet route |
| DNS resolvers | No nameservers in resolv.conf | DNS configured - could leak queries |
| Outbound connections | No established connections to non-local IPs | Something is connecting outbound |
| Listening services | Only services listening on 10.0.77.x or 127.0.0.1 | A service is exposed on a non-ScoutNet interface |
| Firewall rules | OUTPUT and FORWARD chains block non-local traffic | Firewall is misconfigured |
| WiFi client mode | No WiFi client connections active | Scout is connected to an external network |
| ESP32-CAM check | All connected cameras are on 10.0.77.0/24 | A camera is on the wrong network |

### Sample output (all passing)

```
[PASS] No default gateway configured
[PASS] No DNS resolvers configured
[PASS] No outbound connections to non-local addresses
[PASS] All listening services bound to ScoutNet or localhost
[PASS] Firewall blocks non-local OUTPUT and FORWARD
[PASS] No WiFi client connections active
[PASS] All ESP32-CAMs on ScoutNet (4 found)

Privacy audit: 7/7 checks passed
Scout is fully isolated from the internet.
```

### Sample output (failure)

```
[PASS] No default gateway configured
[FAIL] DNS resolver found: nameserver 8.8.8.8
       Fix: Remove nameservers from /etc/resolv.conf
[PASS] No outbound connections to non-local addresses
[PASS] All listening services bound to ScoutNet or localhost
[PASS] Firewall blocks non-local OUTPUT and FORWARD
[PASS] No WiFi client connections active
[PASS] All ESP32-CAMs on ScoutNet (4 found)

Privacy audit: 6/7 checks passed
ACTION REQUIRED: Fix the failing checks above.
```

### Running in CI

The `verify-privacy.sh` script runs as part of the CI pipeline. Any PR that introduces a new outbound network call, hardcoded external IP, or DNS lookup will fail CI.

---

## Connecting Your Management Device

To access Scout's web UI or SSH into it, connect your laptop or phone to ScoutNet.

### Connect to the hidden SSID

**Linux:**

```bash
nmcli device wifi connect ScoutNet password "YOUR_PASSWORD" hidden yes
```

**macOS:**

1. Click the WiFi icon in the menu bar
2. Select "Other Network..."
3. Enter SSID: `ScoutNet`, Security: WPA2/WPA3, Password: your password

**Windows:**

1. Open Settings > Network & Internet > WiFi
2. Click "Manage known networks" > "Add a new network"
3. Enter SSID: `ScoutNet`, Security: WPA2-Personal or WPA3-Personal
4. Check "Connect even if the network is not broadcasting"
5. Enter the password

### Access Scout

After connecting to ScoutNet:

```bash
# SSH into Scout
ssh scout@10.0.77.1

# Open Scout's web UI (if running)
# http://10.0.77.1:8080
```

**Warning:** While connected to ScoutNet, your management device has no internet access. This is expected and intentional. Disconnect from ScoutNet when you need internet.

---

## VLAN Isolation (Alternative to WiFi AP)

If you prefer to use Ethernet instead of WiFi, place Scout on an isolated VLAN.

### Switch configuration

1. Create VLAN 77 on your managed switch
2. Assign Scout's Ethernet port to VLAN 77 (untagged)
3. Assign your management device's port to VLAN 77 (tagged or untagged)
4. Do NOT add a gateway or internet uplink to VLAN 77

### Scout Ethernet configuration

```bash
sudo tee /etc/netplan/60-scout-vlan.yaml << 'EOF'
network:
  version: 2
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.0.77.1/24
      # NO gateway4
      # NO nameservers
EOF

sudo netplan apply
```

Run `verify-privacy.sh --interface eth0` to confirm isolation on the wired interface.

---

## ESP32-CAM Network Configuration

Each ESP32-CAM connects to ScoutNet as a WiFi client. Configure the network credentials in the ESP32 firmware:

```cpp
// firmware/esp32-cam/src/config.h
#define WIFI_SSID     "ScoutNet"
#define WIFI_PASSWORD "YOUR_PASSWORD"

// Static IP configuration (recommended over DHCP for cameras)
#define STATIC_IP     IPAddress(10, 0, 77, 11)  // Adjust per camera
#define GATEWAY       IPAddress(10, 0, 77, 1)
#define SUBNET        IPAddress(255, 255, 255, 0)
#define DNS           IPAddress(0, 0, 0, 0)      // No DNS
```

The ESP32-CAMs serve MJPEG streams. Scout pulls frames as needed. The cameras do not initiate outbound connections.

---

## Troubleshooting

### ESP32-CAM cannot connect to ScoutNet

- Verify hostapd is running: `sudo systemctl status hostapd`
- Check the WiFi password matches between hostapd.conf and ESP32 firmware
- If using WPA3-SAE, verify the ESP32-S3 firmware supports SAE (some older ESP-IDF versions do not - fall back to WPA2)
- Check hostapd logs: `sudo journalctl -u hostapd -f`
- Verify the ESP32-CAM is trying the correct SSID (case-sensitive)

### Management device connects but cannot reach Scout

- Verify your device got a DHCP lease in the 10.0.77.x range: `ip addr` or check your device's network settings
- Ping Scout: `ping 10.0.77.1`
- Check firewall rules on Scout: `sudo iptables -L INPUT -v -n`
- Verify the SSH service is running: `sudo systemctl status ssh`

### verify-privacy.sh reports a failing check after a system update

System updates can reset network configuration. After any package installation (done offline via USB or local repo), re-run verify-privacy.sh and fix any regressions:

- Check for new default routes: `ip route`
- Check for new resolv.conf entries: `cat /etc/resolv.conf`
- Check for new listening services: `ss -tunlp`
- Re-apply firewall rules if iptables were reset

---

## Related Documentation

- [VENTUNO Q Setup](ventuno-q-setup.md) - initial board configuration
- [Privacy Policy](../../PRIVACY.md) - what data Scout stores and how
- [Architecture](../ARCHITECTURE.md) - network architecture diagram
- [Security](../../SECURITY.md) - threat model and security reporting
