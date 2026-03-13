# VENTUNO Q Initial Setup

This reference covers first-time setup of the Arduino VENTUNO Q board for Home Scout. By the end, you will have Ubuntu 24.04 running from NVMe, with I2S audio, MIPI-CSI camera, and CAN-FD communication between the Qualcomm and STM32H5 processors all working.

## Prerequisites

- Arduino VENTUNO Q board (Qualcomm Dragonwing IQ-8275 + STM32H5)
- Samsung 970 EVO Plus 250GB NVMe M.2 SSD (or compatible)
- microSD card (16GB+, Class 10 or faster)
- USB-C cable for power and initial console access
- Monitor with HDMI input (for initial setup only)
- USB keyboard (for initial setup only)
- A temporary internet connection (WiFi or USB Ethernet adapter)

You will disconnect from the internet permanently after setup. Download everything you need during this process.

---

## Step 1: Flash Ubuntu 24.04 to microSD

Download the Ubuntu 24.04 Server image for the VENTUNO Q from the [Arduino Software page](https://www.arduino.cc/en/software).

### Linux / macOS

```bash
# Identify your SD card device (BE CAREFUL - wrong device = data loss)
lsblk

# Flash the image
sudo dd if=ubuntu-24.04-ventuno-q.img of=/dev/sdX bs=4M status=progress conv=fsync
sync
```

### Windows

Use [Balena Etcher](https://etcher.balena.io/) or [Rufus](https://rufus.ie/):

1. Select the VENTUNO Q Ubuntu image
2. Select your microSD card
3. Flash

### Verify the flash

```bash
# Check the partition table was written correctly
sudo fdisk -l /dev/sdX
```

You should see at least two partitions: a small boot partition and a larger root partition.

---

## Step 2: First Boot and Initial Configuration

1. Insert the flashed microSD card into the VENTUNO Q
2. Connect HDMI monitor and USB keyboard
3. Connect USB-C power
4. Wait for the Ubuntu login prompt (first boot takes 1-2 minutes)

Default credentials (check Arduino documentation for current defaults):

```
Username: ubuntu
Password: ubuntu
```

You will be prompted to change the password on first login. Choose a strong password - this is the only user account on the robot.

### Set hostname and timezone

```bash
sudo hostnamectl set-hostname scout
sudo timedatectl set-timezone YOUR_TIMEZONE  # e.g., America/New_York, Australia/Perth
```

### Connect to internet temporarily

```bash
# List available WiFi networks
sudo nmcli device wifi list

# Connect (you will remove this connection later)
sudo nmcli device wifi connect "YOUR_WIFI_SSID" password "YOUR_WIFI_PASSWORD"

# Verify connectivity
ping -c 3 archive.ubuntu.com
```

### Update the system

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Step 3: Install NVMe SSD

The VENTUNO Q has an M.2 M-key slot for NVMe storage. Scout runs its OS, AI models, and object memory database from this drive.

### Physical installation

1. Power off the board completely (disconnect USB-C)
2. Locate the M.2 slot on the VENTUNO Q (check the board silkscreen or pinout diagram)
3. Insert the NVMe SSD at a 30-degree angle into the M.2 connector
4. Press down and secure with the M.2 mounting screw
5. Reconnect USB-C power and boot from microSD

### Partition and format

```bash
# Verify the NVMe drive is detected
lsblk
# You should see nvme0n1

# Create a GPT partition table and a single ext4 partition
sudo parted /dev/nvme0n1 mklabel gpt
sudo parted /dev/nvme0n1 mkpart primary ext4 0% 100%
sudo mkfs.ext4 -L scout-root /dev/nvme0n1p1
```

### Clone the microSD root to NVMe

```bash
# Mount the NVMe partition
sudo mkdir -p /mnt/nvme
sudo mount /dev/nvme0n1p1 /mnt/nvme

# Clone the running system (excluding virtual filesystems)
sudo rsync -axHAWX --numeric-ids --info=progress2 \
  --exclude={"/dev/*","/proc/*","/sys/*","/tmp/*","/run/*","/mnt/*","/media/*","/lost+found"} \
  / /mnt/nvme/

# Update fstab on the NVMe copy
sudo sed -i 's|/dev/mmcblk.*|/dev/nvme0n1p1 / ext4 defaults,noatime 0 1|' /mnt/nvme/etc/fstab

sudo umount /mnt/nvme
```

### Configure boot from NVMe

The exact boot configuration depends on the VENTUNO Q's bootloader. Consult the Arduino documentation for updating the boot device priority. The general approach:

```bash
# Option A: U-Boot environment variable (if applicable)
sudo fw_setenv boot_targets "nvme0 mmc0"

# Option B: Update extlinux.conf (if applicable)
# Edit the boot configuration to point root= at the NVMe partition UUID
sudo blkid /dev/nvme0n1p1
# Copy the UUID and update the kernel command line
```

Reboot and verify you are running from NVMe:

```bash
sudo reboot

# After reboot, confirm root is on NVMe
df -h /
# Should show /dev/nvme0n1p1
```

You can now remove the microSD card and keep it as a recovery image.

---

## Step 4: I2S Audio Configuration

Scout uses I2S for both microphone input (INMP441) and speaker output (MAX98357A). Both connect through the VENTUNO Q's I2S peripheral.

### Device tree overlay

The VENTUNO Q may need a device tree overlay to enable the I2S controller and configure the correct pins. Check if an overlay already exists:

```bash
ls /boot/dtb/overlays/ | grep i2s
# or
ls /boot/firmware/overlays/ | grep i2s
```

If no I2S overlay exists, you may need to compile one. A reference overlay is provided in the Home Scout repository:

```bash
# From the home-scout repo root
sudo cp config/dtb/ventuno-q-i2s.dtbo /boot/dtb/overlays/
```

Enable the overlay in the boot configuration:

```bash
# Add to /boot/firmware/config.txt or equivalent
dtoverlay=ventuno-q-i2s
```

### Verify I2S devices

After rebooting with the overlay applied:

```bash
arecord -l   # Should list the I2S capture device (INMP441 mics)
aplay -l     # Should list the I2S playback device (MAX98357A amp)
```

### ALSA configuration

Create or edit `/etc/asound.conf` to set up the I2S devices as defaults:

```
# /etc/asound.conf
pcm.!default {
    type asym
    playback.pcm "speaker"
    capture.pcm "microphone"
}

pcm.speaker {
    type hw
    card 0    # Adjust card number based on aplay -l output
    device 0
}

pcm.microphone {
    type hw
    card 1    # Adjust card number based on arecord -l output
    device 0
}
```

### Test audio

```bash
# Record 5 seconds from the INMP441 microphones
arecord -D default -f S32_LE -r 16000 -c 2 -d 5 test.wav

# Play back through the MAX98357A
aplay -D default test.wav

# Clean up test file
rm test.wav
```

If you hear your recording, audio is working. If not, check wiring against the [Phase 1 build guide](../build-guides/phase-1-voice.md) pin table.

---

## Step 5: MIPI-CSI Camera Setup

The VENTUNO Q has a MIPI-CSI connector for the onboard camera (Arducam IMX219 or IMX477).

### Connect the camera

1. Power off the board
2. Lift the MIPI-CSI connector latch
3. Insert the camera ribbon cable with contacts facing down (toward the PCB)
4. Press the latch closed
5. Power on

### Verify detection

```bash
# Check for video devices
ls /dev/video*

# Check media controller topology
sudo apt install -y v4l-utils
v4l2-ctl --list-devices

# Query camera capabilities
v4l2-ctl -d /dev/video0 --all
```

### Test capture

```bash
# Capture a single JPEG frame
v4l2-ctl -d /dev/video0 --set-fmt-video=width=1920,height=1080,pixelformat=MJPG \
  --stream-mmap --stream-count=1 --stream-to=test-frame.jpg

# View the captured frame (copy to a machine with a display, or use fbi)
fbi test-frame.jpg

# Clean up
rm test-frame.jpg
```

### Camera parameters

| Parameter | IMX219 | IMX477 |
|-----------|--------|--------|
| Resolution (max) | 3280x2464 | 4056x3040 |
| Frame rate (1080p) | 30 fps | 30 fps |
| Field of view | 62.2 deg (standard), 120 deg (wide) | 73 deg |
| Interface | MIPI-CSI 2-lane | MIPI-CSI 2-lane |
| Focus | Fixed | C/CS-mount (adjustable) |

For Scout's object detection pipeline, 640x480 at 30 fps is sufficient. Higher resolutions are useful for face enrollment (Phase 5).

---

## Step 6: CAN-FD Between Qualcomm and STM32H5

The VENTUNO Q uses CAN-FD (Controller Area Network with Flexible Data-rate) as the communication link between the Qualcomm SoC (running Linux + ROS 2) and the STM32H5 microcontroller (running real-time motor control).

### Enable the CAN interface

```bash
# Load the CAN kernel modules
sudo modprobe can
sudo modprobe can-raw
sudo modprobe can-fd

# Bring up the CAN-FD interface
# Arbitration bitrate: 500 kbps, Data bitrate: 2 Mbps
sudo ip link set can0 type can bitrate 500000 dbitrate 2000000 fd on
sudo ip link set can0 up

# Verify the interface is active
ip -details link show can0
```

### Persist across reboots

Create a systemd network configuration:

```ini
# /etc/systemd/network/80-can0.network
[Match]
Name=can0

[CAN]
BitRate=500000
DataBitRate=2000000
FDMode=yes
RestartSec=100ms
```

```bash
sudo systemctl enable systemd-networkd
sudo systemctl restart systemd-networkd
```

### Test CAN-FD communication

Use `can-utils` to verify the link between processors:

```bash
sudo apt install -y can-utils

# Terminal 1: Monitor incoming CAN frames from the STM32H5
candump can0

# Terminal 2: Send a test heartbeat frame
cansend can0 200#DEADBEEF

# You should see the frame appear in Terminal 1
# If the STM32H5 firmware is running, you should also see
# periodic telemetry frames (0x101, 0x102) from the STM32H5
```

### CAN-FD message ID map

Scout uses a structured message ID space. See [stm32-firmware.md](stm32-firmware.md) for the full protocol definition.

| ID Range | Direction | Purpose |
|----------|-----------|---------|
| `0x100-0x1FE` | Qualcomm -> STM32 | Commands (velocity, config, calibration) |
| `0x1FF` | Both | Safety alerts |
| `0x200` | Both | Heartbeat |
| `0x201-0x2FF` | STM32 -> Qualcomm | Telemetry (odometry, battery, sensors) |

---

## Step 7: GPIO Pinout Reference (JMISC Header)

The VENTUNO Q exposes general-purpose I/O through the JMISC header. Scout uses these pins for I2S audio, I2C sensors, and status LEDs.

### JMISC Header Pinout

Pin assignments below are placeholders. Check the official VENTUNO Q pinout sheet for your board revision.

| Pin | Function | Scout Usage | Direction |
|-----|----------|-------------|-----------|
| 1 | 3.3V | Sensor power | Power |
| 2 | 5V | MAX98357A power | Power |
| 3 | GND | Common ground | Power |
| 4 | GND | Common ground | Power |
| 5 | I2S_BCLK | Audio bit clock (shared mic + amp) | Output |
| 6 | I2S_WS | Audio word select / LRCK | Output |
| 7 | I2S_DIN | Mic data input (INMP441 SD) | Input |
| 8 | I2S_DOUT | Speaker data output (MAX98357A DIN) | Output |
| 9 | I2C_SDA | IMU, OLED displays, ToF sensors | Bidirectional |
| 10 | I2C_SCL | I2C clock | Output |
| 11 | GPIO_A | NeoPixel LED ring data | Output |
| 12 | GPIO_B | Camera indicator LED | Output |
| 13 | GPIO_C | Mic mute switch sense | Input |
| 14 | GPIO_D | Available for expansion | - |
| 15 | UART_TX | Debug console (optional) | Output |
| 16 | UART_RX | Debug console (optional) | Input |
| 17 | SPI_MOSI | Available for expansion | Output |
| 18 | SPI_MISO | Available for expansion | Input |
| 19 | SPI_CLK | Available for expansion | Output |
| 20 | SPI_CS0 | Available for expansion | Output |

### I2C bus scan

After connecting I2C devices (IMU, OLED, ToF sensors), verify they are detected:

```bash
sudo apt install -y i2c-tools
sudo i2cdetect -y 1
```

Expected addresses for Scout peripherals:

| Address | Device |
|---------|--------|
| `0x28` | BNO055 IMU |
| `0x29` | VL53L1X ToF sensor (default) |
| `0x3C` | SH1106 OLED display #1 |
| `0x3D` | SH1106 OLED display #2 |

---

## Step 8: Install ROS 2 and Home Scout Software

With hardware verified, install the software stack:

```bash
# Install ROS 2 Jazzy
sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep
sudo rosdep init && rosdep update

# Clone Home Scout
git clone https://github.com/m4cd4r4/home-scout.git ~/home-scout
cd ~/home-scout

# Install ROS 2 dependencies
cd ros2_ws
rosdep install --from-paths src --ignore-src -y

# Build
colcon build --symlink-install
source install/setup.bash
```

### Download AI models

```bash
~/home-scout/scripts/download-models.sh /home/scout/models
```

This pulls approximately 3.6 GB of model files. Do this while you still have internet access.

---

## Step 9: Disconnect from the Internet

This is the final setup step. After this, Scout has no internet connectivity.

```bash
# Remove all WiFi connections
sudo nmcli connection delete "YOUR_WIFI_SSID"

# Disable WiFi hardware (if the board has a WiFi radio)
sudo nmcli radio wifi off

# Verify isolation
ping -c 1 8.8.8.8
# Expected: "Network is unreachable" or 100% packet loss

ip route
# Expected: no default gateway

cat /etc/resolv.conf
# Expected: no nameserver entries (or localhost only)
```

Run the privacy verification script:

```bash
~/home-scout/scripts/verify-privacy.sh
```

All checks should pass. Scout is now fully offline.

---

## Troubleshooting

### NVMe drive not detected

- Verify the SSD is seated fully in the M.2 slot
- Check that the mounting screw is not over-tightened (can crack the SSD PCB)
- Run `dmesg | grep nvme` for kernel-level detection messages
- Try a different NVMe drive to rule out compatibility issues

### I2S audio not working

- Double-check wiring against the [Phase 1 build guide](../build-guides/phase-1-voice.md) pin table
- Verify the device tree overlay is loaded: `sudo dtoverlay -l`
- Check ALSA mixer levels: `alsamixer`
- Run `dmesg | grep i2s` for driver errors

### CAN-FD interface errors

- Check `ip -s link show can0` for error counters
- If error counters are high, verify CAN-H and CAN-L wiring
- Make sure the STM32H5 firmware is flashed and running (see [stm32-firmware.md](stm32-firmware.md))
- CAN-FD requires proper termination (120 ohm resistor between CAN-H and CAN-L at each end of the bus)

### Camera not detected

- Verify the ribbon cable is fully seated and the latch is locked
- Check orientation - contacts face the PCB
- Run `dmesg | grep imx` for driver messages
- If using IMX477, ensure the correct device tree overlay is active

---

## Next Steps

- [STM32H5 Firmware Reference](stm32-firmware.md) - flash and configure the real-time controller
- [Camera Calibration](camera-calibration.md) - calibrate intrinsics for accurate object localization
- [Network Isolation](network-isolation.md) - set up ScoutNet for ESP32-CAM connectivity
- [Phase 1: Scout Can Talk](../build-guides/phase-1-voice.md) - launch the voice pipeline
