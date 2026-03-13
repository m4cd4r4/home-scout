# Phase 6: Sky Eye (Optional)

After this phase, Scout has an optional drone companion that can provide aerial views of rooms and greet family members arriving home. This is the most advanced phase and is entirely optional.

!!! warning
    Drones require extra safety precautions. Indoor flight near people and pets carries real risk. Read SAFETY.md thoroughly. Consider your local drone regulations even for indoor use.

## What You Need (Phase 6 additions)

| Part | Model | Cost |
|------|-------|------|
| Frame | 65mm micro brushless frame | ~$15 |
| Flight controller | BetaFPV F4 1S AIO | ~$30 |
| Motors | 0802 19500KV brushless (x4) | ~$20 |
| Props | 31mm tri-blade (x8, spares) | ~$5 |
| Battery | 1S 450mAh LiHV (x3) | ~$20 |
| Camera | Caddx Ant Nano | ~$15 |
| VTX | Built-in on F4 AIO | $0 |
| Prop guards | 65mm full guards | ~$10 |
| ESP32-S3 module | For WiFi bridge to ScoutNet | ~$8 |
| Charger | 1S USB charger | ~$10 |

**Phase 6 total: ~$133** (cumulative: ~$1,128)

## Architecture

The drone is a semi-autonomous micro quadcopter that communicates with Scout via the ScoutNet WiFi network. It does NOT carry AI processing - it streams video back to the VENTUNO Q for inference.

```
Drone (ESP32-S3 + F4 FC)
    |
    | WiFi (ScoutNet 10.0.77.0/24)
    v
VENTUNO Q
    |
    | CAN-FD
    v
STM32H5 (landing pad detection)
```

## Step 1: Build the Drone

Follow standard micro quad building guides. Key points:
- Solder the ESP32-S3 to the F4 FC's UART
- Install full prop guards (required for indoor use)
- Keep total weight under 50g

## Step 2: Flash Drone Firmware

```bash
cd firmware/esp32-drone-bridge  # TODO: Not yet implemented
pio run --target upload
```

The ESP32-S3 acts as a WiFi bridge, forwarding video and receiving waypoint commands.

## Step 3: Safety Configuration

Configure strict flight boundaries:
- Maximum altitude: 2m
- Maximum speed: 1 m/s
- Geofenced to mapped rooms only
- Auto-land on low battery (3.3V/cell)
- Auto-land on lost connection (2 second timeout)

## Step 4: Landing Pad

Scout's chassis top plate serves as the drone landing pad. An ArUco marker on the top plate provides visual landing guidance.

## Status

!!! note
    Phase 6 is a design outline. The drone firmware, control nodes, and landing system are not yet implemented. This is the most complex phase and benefits from community contributions.

**Contributions welcome:** If you have experience with micro drones and ROS 2, see [Contributing](../../CONTRIBUTING.md).

## What's Next

You've completed all phases! Share your build in [GitHub Discussions](https://github.com/YOUR_USERNAME/home-scout/discussions) under "Show and Tell".
