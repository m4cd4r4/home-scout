# Architecture

## System Overview

Scout runs on the Arduino VENTUNO Q, a dual-brain board with a Qualcomm Dragonwing IQ-8275 SoC (8x ARM Cortex-A cores, 40 TOPS NPU, 16GB LPDDR5) and an STM32H5F5 MCU (Cortex-M33 @ 250MHz). The two processors communicate over CAN-FD.

```
+----------------------------------------------------------+
|              VENTUNO Q  (Linux + ROS 2 Jazzy)            |
|                                                          |
|  +----------+  +----------+  +---------+  +------------+ |
|  |  voice   |  |  vision  |  |   nav   |  |   memory   | |
|  | Phase 1  |  | Phase 2  |  | Phase 3 |  |  Phase 4   | |
|  +----------+  +----------+  +---------+  +------------+ |
|  +----------+  +--------------------------------------+  |
|  |  faces   |  |         hardware_bridge              |  |
|  | Phase 5  |  |    (base_driver_node.py)             |  |
|  +----------+  +------------------+-------------------+  |
|                                   | CAN-FD                |
+-----------------------------------+----------------------+
|              STM32H5  (Zephyr RTOS)                      |
|   Motor PWM | Encoders | PID | Safety Watchdog           |
+----------------------------------------------------------+
```

The Qualcomm side runs Ubuntu 24.04 with ROS 2 Jazzy. Six bounded subsystems communicate through ROS 2 topics, services, and actions. The STM32H5 runs real-time motor control with an independent safety watchdog.

---

## AI Model Stack

All inference runs locally on the 40 TOPS NPU. No cloud APIs.

| Function | Model | Size | RAM | Runs On |
|----------|-------|------|-----|---------|
| Wake word | openWakeWord | ~2MB | ~10MB | CPU/DSP |
| Speech recognition | Whisper-Small-En (Qualcomm) | ~500MB | ~1GB | NPU |
| Speech synthesis | Piper TTS (VITS, amy voice) | ~100MB | ~200MB | CPU |
| Conversation | Llama-3.2-1B-Instruct (INT4) | ~1.5GB | ~2GB | NPU |
| Object detection | SmolVLM-256M (INT4) | ~1.5GB | ~2GB | NPU |
| Face detection | SCRFD-2.5G | ~10MB | ~100MB | NPU |
| Face embedding | MobileFaceNet (ArcFace) | ~10MB | ~100MB | NPU |
| **Total** | | **~3.6GB disk** | **~5.4GB RAM** | |

With 16GB total RAM, this leaves ~10.6GB for ROS 2, Nav2, SLAM, and OS overhead.

### NPU Scheduling

- Wake word detection runs continuously on the DSP
- ASR preempts VLM inference when triggered (voice takes priority)
- During patrol: VLM at 2 Hz + face detection at 5 Hz uses ~9 TOPS, leaving 31 TOPS headroom
- LLM runs on-demand after ASR completes a transcription

---

## Subsystem Details

### Voice (Phase 1)

```
Mic -> wake_word_node -> asr_node -> conversation_node -> tts_node -> Speaker
              |                              |
        /scout/wake_detected          /scout/transcript
                                             |
                                      /scout/speak
```

**Nodes:**
- `wake_word_node` - Runs openWakeWord on the audio stream. Publishes a trigger when "Hey Scout" is detected.
- `asr_node` - Records audio after wake detection, runs Whisper inference, publishes transcript text.
- `conversation_node` - Classifies intent (object query, patrol command, face query, general chat). Routes object queries to the memory subsystem, everything else to the LLM.
- `tts_node` - Converts response text to audio via Piper TTS, plays through MAX98357A amplifier.

### Vision (Phase 2)

```
MIPI-CSI Camera -> camera_node -> detector_node -> tracker_node -> ObjectSighting
                                       |
                                  npu_inference
```

**Nodes:**
- `camera_node` - V4L2 driver for MIPI-CSI cameras. Publishes `sensor_msgs/Image`.
- `detector_node` - Runs SmolVLM-256M on the NPU at a configurable rate (default 2 Hz). Publishes bounding boxes and object names.
- `tracker_node` - Multi-object IoU tracker that assigns stable IDs across frames and prunes lost tracks.
- `npu_inference` - Utility module wrapping QNN/ONNX Runtime for NPU model loading and inference.

### Navigation (Phase 3)

```
LIDAR + Camera -> slam_node -> /map
                                 |
cmd_vel <- patrol_node <- Nav2 costmap + planner
   |
base_driver_node -> CAN-FD -> STM32H5 -> Motors
   |
odometry_node -> /odom + /tf
```

**Nodes:**
- `slam_node` - Wraps RTAB-Map. Two modes: mapping (initial room setup) and localization (normal operation).
- `patrol_node` - Loads patrol route YAML configs. Manages room-to-room navigation using Nav2 action clients.
- `base_driver_node` - CAN-FD bridge to the STM32H5. Sends velocity commands, receives encoder data.
- `odometry_node` - Computes differential drive odometry from wheel encoders. Publishes `/odom` and TF.

**Safety layers (defense in depth):**
1. LIDAR (2m+ range) via Nav2 costmap
2. ToF sensors (30mm - 4m range) as virtual bumpers
3. Cliff sensors (TCRT5000) for stair detection
4. STM32H5 hardware watchdog (100ms timeout, independent of Linux)

### Memory (Phase 4)

```
ObjectSighting -> object_memory_node -> SQLite + FTS5
                        |
                  WhereIs service
                        |
              conversation_node queries
```

**Nodes:**
- `object_memory_node` - Stores object sightings with room/zone assignment (via point-in-polygon from SLAM pose). Serves WhereIs queries. Runs periodic confidence decay.

**Data model (SQLite):**
- `object_sightings` - name, room, zone, position (x,y,z), confidence, source, timestamp, expiry
- `object_aliases` - maps natural language ("my keys") to canonical names ("keys")
- `rooms` / `zones` - Polygon boundaries from SLAM occupancy grid

**Confidence decay:**
- Portable items (keys, phone): 4-hour half-life
- Semi-fixed items (books, bags): 24-hour half-life
- Fixed items (furniture): 168-hour half-life (1 week)

**Retention:**
- Personal items: 30 days
- Household items: 14 days
- Transient items: 2 days
- Face sightings: 7 days

### Faces (Phase 5)

```
Camera -> recognition_node -> FaceDetection
               |                    |
          SCRFD + MobileFaceNet   greeting_node -> /scout/speak
               |
         enrollment_node (EnrollFace service)
```

**Nodes:**
- `enrollment_node` - Consent-required enrollment. Captures face samples, generates 128-d embeddings, encrypts with Fernet (AES-128-CBC). No photos stored.
- `recognition_node` - Runs SCRFD face detection + MobileFaceNet embedding. Matches against enrolled faces via cosine similarity.
- `greeting_node` - Time-of-day aware greetings with per-person cooldown to avoid repetition.

**Privacy:**
- Face embeddings encrypted at rest (AES-256-GCM, key derived from user passphrase via Argon2id)
- No face images are ever saved to disk
- Enrollment requires explicit consent flag in the service request

### Fixed Camera Network (ESP32-S3-CAM)

Scout creates a dedicated WiFi access point ("ScoutNet", hidden SSID, 10.0.77.0/24) with **no internet gateway**. Up to 4 ESP32-S3-CAMs serve MJPEG streams over this local network.

- 1 FPS baseline, 5 FPS on motion detection
- Each camera has a fixed room/zone assignment
- Scout pulls frames as needed for VLM inference

---

## STM32H5 Firmware

The STM32H5 runs real-time motor control independently of Linux. If the Qualcomm side crashes, the STM32H5 stops all motors.

**Main loop (1 kHz):**
1. Safety check (e-stop, cliff sensors, battery voltage)
2. Heartbeat check (expects ping every 50ms from Qualcomm; 10 missed = safe mode)
3. Process CAN-FD commands
4. PID control at 100 Hz
5. Send telemetry (odometry, battery, sensor state)
6. Feed hardware watchdog

**CAN-FD message IDs:**
- `0x100` - Velocity command (Qualcomm -> STM32)
- `0x101` - Odometry data (STM32 -> Qualcomm)
- `0x102` - Battery status
- `0x103` - Cliff sensor alert
- `0x1FF` - Safety alert (emergency)
- `0x200` - Heartbeat

---

## Network Architecture

```
+------------------+     ScoutNet WiFi (10.0.77.0/24)
|   VENTUNO Q      |<------->  ESP32-CAM #1 (10.0.77.11)
|   10.0.77.1      |<------->  ESP32-CAM #2 (10.0.77.12)
|   (AP + DHCP)    |<------->  ESP32-CAM #3 (10.0.77.13)
+------------------+<------->  ESP32-CAM #4 (10.0.77.14)
       |
       X  (no default gateway, no DNS, no internet)
```

- VENTUNO Q runs hostapd as WiFi AP
- DHCP range: 10.0.77.10 - 10.0.77.50
- No DNS servers configured
- No default route
- `scripts/verify-privacy.sh` audits this configuration

---

## Directory Structure

```
home-scout/
  ros2_ws/src/
    scout_interfaces/    # Shared msg/srv/action definitions
    scout_bringup/       # Launch files + config
    scout_voice/         # Phase 1: ASR, TTS, wake word, conversation
    scout_vision/        # Phase 2: Camera, detector, tracker, NPU
    scout_nav/           # Phase 3: Base driver, odometry, patrol, SLAM
    scout_memory/        # Phase 4: Object memory, query engine, spatial index
    scout_faces/         # Phase 5: Enrollment, recognition, greeting
    scout_description/   # URDF robot model
    scout_simulation/    # Gazebo worlds + launch
  firmware/
    stm32-motor-control/ # PlatformIO - motor PID, CAN-FD bridge, safety
    esp32-cam/           # PlatformIO - MJPEG streaming, motion detection
  config/
    personalities/       # YAML personality definitions
    patrol-routes/       # Patrol waypoint configs
    room-maps/           # Room/zone polygon definitions
  hardware/
    chassis/             # 3D printable STL + source files
    wiring/              # Schematics + Fritzing diagrams
    mounts/              # Camera, LIDAR, speaker mounts
```

---

## Build Phases

Each phase adds one capability. You can stop after any phase and have a working robot.

| Phase | Capability | Packages Added |
|-------|-----------|----------------|
| 1 | Voice | scout_voice, scout_bringup |
| 2 | Vision | scout_vision |
| 3 | Mobility | scout_nav, scout_description, firmware/ |
| 4 | Memory | scout_memory |
| 5 | Faces | scout_faces |
| 6 | Drone | (separate drone controller, not in ros2_ws) |
