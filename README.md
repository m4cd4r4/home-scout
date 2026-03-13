<p align="center">
  <img src="media/hero-banner.png" alt="Home Scout - Privacy-First Home Companion Robot" width="700">
</p>

<h1 align="center">Home Scout</h1>

<p align="center">
  <strong>A privacy-first home companion robot that remembers where you left things.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/YOUR_USERNAME/home-scout/actions/workflows/ros2-ci.yml"><img src="https://github.com/YOUR_USERNAME/home-scout/actions/workflows/ros2-ci.yml/badge.svg" alt="ROS 2 CI"></a>
  <a href="https://github.com/YOUR_USERNAME/home-scout/actions/workflows/firmware-ci.yml"><img src="https://github.com/YOUR_USERNAME/home-scout/actions/workflows/firmware-ci.yml/badge.svg" alt="Firmware CI"></a>
  <a href="https://github.com/YOUR_USERNAME/home-scout/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

<p align="center">
  <a href="#what-is-scout">What is Scout?</a> &bull;
  <a href="#features">Features</a> &bull;
  <a href="#build-phases">Build Phases</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#privacy">Privacy</a> &bull;
  <a href="#hardware-overview">Hardware</a> &bull;
  <a href="#architecture">Architecture</a> &bull;
  <a href="#contributing">Contributing</a> &bull;
  <a href="#safety">Safety</a>
</p>

---

## What is Scout?

Scout is an open-source home companion robot you build with your family. It patrols your house, remembers where objects are, greets family members by name, and answers questions - all without ever connecting to the internet. Ask "Scout, where are my keys?" and it tells you exactly where it last saw them.

The brain is an [Arduino VENTUNO Q](https://www.arduino.cc/) board running ROS 2 on Ubuntu. It pairs an Arm Cortex-A78AE (Jetson Orin NX) for AI workloads with an STM32H5 microcontroller for real-time motor and sensor control. One board handles voice recognition, object detection, navigation, and face recognition locally.

Privacy is not a feature - it is the architecture. Scout has no Wi-Fi antenna, no cloud account, no telemetry. Every byte of data stays on the robot. Face embeddings are encrypted at rest. You can audit the entire system with a single script. Families deserve a robot that watches the house without reporting to a corporation.

## Features

| Feature | How It Works | Phase |
|---------|-------------|-------|
| Voice interaction | Wake word detection + on-device speech-to-text and text-to-speech via Whisper + Piper | Phase 1 |
| Object detection | YOLOv8-nano running on Jetson Orin NX GPU at 30 FPS | Phase 2 |
| Autonomous navigation | SLAM mapping with RPLIDAR + IMU, path planning via Nav2 | Phase 3 |
| Object memory | Spatial database linking detected objects to map coordinates with timestamps | Phase 4 |
| Face recognition | On-device face embeddings (ArcFace), encrypted storage, family-only training | Phase 5 |
| Drone module | Tethered or autonomous indoor drone for elevated search and monitoring | Phase 6 |
| Customizable personality | Adjustable voice, response style, LED expressions, OLED face animations | All |
| 100% local processing | Zero internet. Zero cloud. Zero telemetry. Everything runs on-board. | All |

## Build Phases

Scout is designed to be built incrementally. Start with Phase 1 and add capabilities over time. Each phase produces a working robot.

---

### Phase 1: Scout Can Talk

> Voice interface - wake word, speech-to-text, text-to-speech, basic Q&A.

| | |
|---|---|
| **What you need** | VENTUNO Q board, NVMe SSD, 2x MEMS microphones, I2S amplifier, speaker |
| **Cost** | ~$300 |
| **Build time** | One afternoon |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- Responds to "Hey Scout" wake word
- Answers general questions using a local LLM (Llama 3.2 1B or similar)
- Tells jokes, sets timers, reads recipes aloud
- Speaks with a configurable voice (male/female, speed, pitch)
- Runs entirely from a desk or shelf - no mobility required

</details>

---

### Phase 2: Scout Can See

> Object detection - identifies and classifies common household objects in real time.

| | |
|---|---|
| **What you need** | Onboard MIPI-CSI camera, optional wide-angle or HQ camera, ESP32-S3 room cameras |
| **Cost** | ~$30-50 extra |
| **Build time** | One evening |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- Detects 80+ object categories (COCO dataset) at 30 FPS
- "Scout, what do you see?" - describes objects in view
- Room cameras provide persistent monitoring from fixed positions
- Combines with Phase 1 voice: "Scout, is my laptop on the desk?"
- Still stationary - but now it has eyes

</details>

---

### Phase 3: Scout Can Move

> Wheels, motors, LIDAR, and autonomous navigation via SLAM.

| | |
|---|---|
| **What you need** | 4WD chassis, motors, encoders, LIDAR, IMU, battery, motor drivers, bump/cliff sensors |
| **Cost** | ~$250-300 extra |
| **Build time** | One weekend |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- Maps your house autonomously using SLAM
- Navigates between rooms avoiding obstacles
- Runs patrol routes on a schedule or on command
- Returns to charging position when battery is low
- Emergency stop button kills all motor power instantly
- Cliff sensors prevent it from falling down stairs

</details>

---

### Phase 4: Scout Remembers Everything

> Spatial object memory - links detected objects to map locations with timestamps.

| | |
|---|---|
| **What you need** | No new hardware - software-only upgrade |
| **Cost** | $0 extra |
| **Build time** | A few hours |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- "Scout, where are my keys?" - "I last saw your keys on the kitchen counter 2 hours ago."
- Maintains a spatial database of every detected object and its location
- Tracks object movement over time
- Searches specific rooms on request: "Scout, go check if my bag is in the bedroom."
- Combines patrol routes with object scanning for continuous inventory

</details>

---

### Phase 5: Scout Knows Us

> Face recognition - identifies family members and personalizes interactions.

| | |
|---|---|
| **What you need** | No new hardware - software-only upgrade using existing cameras |
| **Cost** | $0 extra |
| **Build time** | ~5 minutes per family member (enrollment) |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- "Good morning, Sarah!" - greets family members by name
- Personalizes responses per person (reminders, preferences, voice style)
- Announces arrivals: "Dad just got home."
- Face embeddings are encrypted and never leave the device
- Enrollment is local - stand in front of Scout for 5 seconds
- Guest mode for visitors (no face stored)

</details>

---

### Phase 6: Scout's Sky Eye

> Drone module - tethered or autonomous indoor aerial unit for elevated search.

| | |
|---|---|
| **What you need** | Micro drone frame, brushless motors, flight controller, FPV camera, tether (optional) |
| **Cost** | ~$150-200 extra |
| **Build time** | Multiple weekends |

<details>
<summary><strong>What can Scout do after this phase?</strong></summary>

- Launches a small indoor drone for elevated search
- Checks high shelves, tops of cabinets, above furniture
- Tethered mode keeps the drone physically connected (safer, unlimited flight time)
- Autonomous mode with indoor GPS-denied navigation
- "Scout, check the top of the bookshelf" triggers a targeted flyover
- This is an advanced build - expect iteration and debugging

</details>

## Quick Start

Two paths: simulation (no hardware needed) or real hardware starting at Phase 1.

### Path A: Simulation (Docker)

Run the full Scout stack in simulation. Requires Docker and 8 GB+ RAM.

```bash
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout

# Pull and start all containers (ROS 2, Gazebo sim, voice pipeline)
docker compose -f docker/docker-compose.sim.yml up

# In another terminal - talk to simulated Scout
docker exec -it scout-voice bash
ros2 topic pub /scout/wake_word std_msgs/msg/String "data: 'hey scout'"
```

Open `http://localhost:8080` in your browser to see the Gazebo simulation with Scout navigating a virtual house.

### Path B: Real Hardware (Phase 1)

Grab the parts listed in [Phase 1 of the BOM](BOM.md#phase-1-scout-can-talk) and follow the hardware guide.

```bash
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout

# Flash the STM32H5 firmware
cd firmware
./flash.sh

# Install ROS 2 workspace on the VENTUNO Q (Ubuntu 24.04)
cd ../ros2_ws
colcon build --packages-select scout_voice scout_core
source install/setup.bash

# Launch the voice pipeline
ros2 launch scout_voice voice_pipeline.launch.py
```

Say "Hey Scout" and ask a question. See [docs/phase1-build-guide.md](docs/phase1-build-guide.md) for the full walkthrough with photos.

## Privacy

Scout is designed from the ground up to protect your family's privacy.

- **Zero internet connectivity.** Scout has no Wi-Fi antenna and no cellular modem. It cannot connect to the internet even if you wanted it to.
- **Zero cloud dependency.** All AI models (speech, vision, LLM, face recognition) run locally on the VENTUNO Q's Jetson Orin NX GPU.
- **Zero telemetry.** No analytics, no crash reports, no usage data leaves the robot. Ever.
- **Encrypted face data.** Face embeddings are encrypted at rest using AES-256. Deleting a family member's profile permanently destroys their biometric data.
- **Auditable by design.** Run `scripts/verify-privacy.sh` to confirm no network interfaces are active, no outbound connections exist, and all data stays on-device.
- **Open source, always.** Every line of code is in this repo. No proprietary blobs, no phone-home binaries, no hidden services.

## Hardware Overview

See [BOM.md](BOM.md) for the full bill of materials with purchase links and per-phase breakdowns.

| Category | Key Components | Approx. Cost |
|----------|---------------|-------------|
| Compute | Arduino VENTUNO Q (Jetson Orin NX + STM32H5) | ~$300 |
| Storage | Samsung 970 EVO Plus 250GB NVMe | ~$40 |
| Audio | 2x INMP441 mics, MAX98357A amp, speaker | ~$17 |
| Vision | Arducam IMX219/IMX477 onboard + 4x ESP32-S3 room cams | ~$75-135 |
| Mobility | 4WD chassis, Pololu motors, wheels, motor drivers | ~$200 |
| Navigation | RPLIDAR C1, BNO055 IMU, ToF sensors, cliff sensors | ~$190 |
| Power | 4S LiPo battery, BMS, buck converter | ~$100 |
| Interface | 2x OLED displays, NeoPixel ring, e-stop | ~$40 |
| Misc | Wiring, connectors, fasteners, bumpers | ~$70 |
| **Total (all phases)** | | **~$1,030-1,100** |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ARDUINO VENTUNO Q                              │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              Jetson Orin NX  (Cortex-A78AE)                  │  │
│  │                    Ubuntu 24.04 + ROS 2 Jazzy                │  │
│  │                                                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │  │
│  │  │  Voice   │ │  Vision  │ │   Nav2   │ │ Object Memory  │  │  │
│  │  │ Pipeline │ │ Pipeline │ │  Stack   │ │   (SQLite)     │  │  │
│  │  │          │ │          │ │          │ │                │  │  │
│  │  │ Whisper  │ │ YOLOv8n  │ │  SLAM    │ │ Spatial index  │  │  │
│  │  │ Piper    │ │ ArcFace  │ │  AMCL    │ │ Timestamps     │  │  │
│  │  │ LLM      │ │ Tracker  │ │  Planner │ │ Confidence     │  │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └───────┬────────┘  │  │
│  │       │             │            │               │            │  │
│  │       └─────────────┴─────┬──────┴───────────────┘            │  │
│  │                           │                                    │  │
│  │                    ROS 2 Topic Bus                             │  │
│  │                           │                                    │  │
│  └───────────────────────────┼───────────────────────────────────┘  │
│                              │                                      │
│                         CAN-FD Bus                                  │
│                              │                                      │
│  ┌───────────────────────────┼───────────────────────────────────┐  │
│  │              STM32H5  (Real-Time Controller)                  │  │
│  │                                                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │  │
│  │  │  Motor   │ │  Sensor  │ │  Power   │ │  Safety  │       │  │
│  │  │  Control │ │  Fusion  │ │  Mgmt    │ │  Monitor │       │  │
│  │  │ 4x PWM   │ │ IMU+Enc  │ │ BMS+Buck │ │ E-Stop   │       │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
         │              │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ RPLIDAR │   │ Cameras │   │ Motors  │   │ Sensors │
    │   C1    │   │ CSI+ESP │   │ 4x 37D  │   │ ToF/IMU │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## Contributing

Scout is a community project. Contributions of all kinds are welcome - code, docs, hardware designs, 3D models, testing, and translations.

```bash
# One-command dev setup (simulation, no hardware needed)
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout
docker compose -f docker/docker-compose.dev.yml up
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for coding standards, PR process, and architecture decisions.

### Ways to Contribute Without Hardware

- **Write tests** for ROS 2 nodes using the simulation environment
- **Improve documentation** - build guides, wiring diagrams, troubleshooting
- **Train or optimize models** - smaller, faster YOLOv8 variants for edge deployment
- **Design 3D-printable parts** - chassis, camera mounts, sensor brackets
- **Add language support** - wake word models and TTS voices for more languages
- **Review and audit** - security review, privacy audit, code quality

## Safety

Read [SAFETY.md](SAFETY.md) before building. Key points:

- **Emergency stop is mandatory for Phase 3+.** The e-stop button cuts all motor power immediately. Do not skip this.
- **Battery handling requires adult supervision.** LiPo batteries can be dangerous if mishandled. Always charge with a proper balance charger. Never leave charging unattended.
- **Phase 6 (drone module) is adults-only.** Indoor drones require careful tuning and understanding of propeller safety. Not suitable for children to build or operate unsupervised.
- **Secure the robot when not in use.** A 5 kg robot moving at 0.5 m/s can knock things over. Use the software speed limiter and keep the e-stop accessible.
- **Test in an open area first.** Before letting Scout patrol your house, test navigation in a single room with obstacles removed.

## License

MIT License. See [LICENSE](LICENSE).

Build it. Modify it. Share it. Teach your kids how robots work.

---

<p align="center">
  <strong>Scout never phones home. That is the point.</strong>
</p>
