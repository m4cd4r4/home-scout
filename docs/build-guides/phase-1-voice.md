# Phase 1: Scout Can Talk

After this phase, Scout can listen and respond to voice commands using local ASR, TTS, and a small LLM. No cameras, no motors - just a microphone, speaker, and the VENTUNO Q.

## What You Need

| Part | Model | Cost |
|------|-------|------|
| Main board | Arduino VENTUNO Q | ~$300 |
| NVMe SSD | Samsung 970 EVO Plus 250GB | ~$40 |
| Microphone | INMP441 I2S MEMS (x2) | ~$6 |
| Amplifier | Adafruit MAX98357A I2S | ~$6 |
| Speaker | 40mm 4-8 ohm driver | ~$5 |
| USB-C cable | For power | ~$5 |

**Total: ~$362**

## Step 1: Flash Ubuntu on the VENTUNO Q

1. Download Ubuntu 24.04 Server image for VENTUNO Q from Arduino
2. Flash to microSD card using Balena Etcher or `dd`
3. Insert microSD, connect USB-C power and a monitor
4. Boot and complete initial Ubuntu setup
5. Connect to your local WiFi temporarily (for package installation only)
6. Install NVMe SSD in the M.2 slot, format as ext4

!!! warning
    After setup, you will disconnect from the internet permanently. Download everything you need now.

## Step 2: Install ROS 2 Jazzy

```bash
# Install ROS 2 Jazzy (while still connected to internet)
sudo apt update && sudo apt install -y ros-jazzy-desktop python3-colcon-common-extensions python3-rosdep
sudo rosdep init && rosdep update
```

## Step 3: Clone and Build Home Scout

```bash
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout
./scripts/setup-ventuno.sh
```

## Step 4: Connect Audio Hardware

### Microphone Wiring (INMP441 to VENTUNO Q I2S)

| INMP441 Pin | VENTUNO Q Pin | Notes |
|-------------|---------------|-------|
| VDD | 3.3V | Power |
| GND | GND | Ground |
| SD | I2S_DIN | Data out |
| WS | I2S_WS | Word select (left/right) |
| SCK | I2S_BCLK | Bit clock |
| L/R | GND or 3.3V | Left channel = GND, Right = 3.3V |

Wire two INMP441 modules: one with L/R to GND (left), one with L/R to 3.3V (right).

### Speaker Wiring (MAX98357A)

| MAX98357A Pin | VENTUNO Q Pin | Notes |
|---------------|---------------|-------|
| VIN | 5V | Power |
| GND | GND | Ground |
| DIN | I2S_DOUT | Data in |
| BCLK | I2S_BCLK | Bit clock |
| LRC | I2S_WS | Word select |
| GAIN | Leave floating | 9dB default gain |

Connect speaker leads to the + and - terminals on the MAX98357A.

!!! note
    Pin names are placeholders. Check the VENTUNO Q pinout documentation for actual I2S pin locations on the JMISC header.

## Step 5: Download AI Models

```bash
./scripts/download-models.sh /home/scout/models
```

This downloads:
- Whisper Small English (~500MB) - speech recognition
- Piper TTS amy voice (~100MB) - speech synthesis
- Llama 3.2 1B Instruct (~1.5GB) - conversation

## Step 6: Disconnect from Internet

```bash
# Remove WiFi configuration
sudo nmcli connection delete <your-wifi-name>

# Verify no internet
ping -c 1 8.8.8.8  # Should fail
```

From this point forward, Scout has no internet connection.

## Step 7: Launch Scout

```bash
source /opt/ros/jazzy/setup.bash
source ~/home-scout/ros2_ws/install/setup.bash
ros2 launch scout_bringup scout_voice_only.launch.py
```

Say **"Hey Scout"** and wait for the acknowledgment tone. Then ask a question.

## Step 8: Customize Personality

Edit the personality config:

```bash
nano ~/home-scout/config/personalities/default.yaml
```

Or try the playful personality:

```bash
ros2 launch scout_bringup scout_voice_only.launch.py \
  personality:=~/home-scout/config/personalities/playful.yaml
```

## Test It

- "Hey Scout, what time is it?"
- "Hey Scout, tell me a joke"
- "Hey Scout, set a timer for 5 minutes"
- "Hey Scout, what's the weather?" (Scout should say it doesn't have internet access)

## Troubleshooting

See [troubleshooting.md](troubleshooting.md) for common Phase 1 issues.

## What's Next

[Phase 2: Scout Can See](phase-2-vision.md) - add a camera and object detection.
