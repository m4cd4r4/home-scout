# Bill of Materials

Complete parts list for building Home Scout. Organized by build phase so you only buy what you need right now.

## Build Tiers

Three tiers depending on your budget and goals.

| Tier | What You Get | Approx. Cost |
|------|-------------|-------------|
| **Minimum Viable** (~$750) | Voice + 1 onboard camera + 2 room cameras + basic chassis, no LIDAR | ~$750 |
| **Recommended** (~$1,110) | Full spec - all 6 phases of hardware as listed below | ~$1,110 |
| **Premium** (~$1,500) | Recommended + charging dock, 3D depth camera, extra battery, metal chassis | ~$1,500 |

Start with Phase 1. Add phases when you are ready.

---

## Phase-by-Phase Buying Guide

### Phase 1: Scout Can Talk (~$300)

Buy this first. Everything else builds on top of it.

| # | Part | Model | Purpose | Cost (USD) | Where to Buy | Phase |
|---|------|-------|---------|-----------|-------------|-------|
| 1 | Main board | Arduino VENTUNO Q | Compute brain - Jetson Orin NX + STM32H5 on one board | ~$300 | [Arduino Store](https://store.arduino.cc/) | 1 |
| 2 | Storage | Samsung 970 EVO Plus 250GB NVMe M.2 | OS + models + object memory database | ~$40 | [Amazon](https://amazon.com), [Newegg](https://newegg.com) | 1 |
| 3 | Microphone (x2) | INMP441 I2S MEMS Microphone | Stereo audio input for wake word and speech recognition | ~$6 (pair) | [AliExpress](https://aliexpress.com), [Amazon](https://amazon.com) | 1 |
| 4 | Amplifier | Adafruit MAX98357A I2S Mono Amp | Drives the speaker from I2S digital audio | ~$6 | [Adafruit](https://www.adafruit.com/product/3006), [DigiKey](https://digikey.com) | 1 |
| 5 | Speaker | 40mm 4-ohm 3W speaker | Audio output for Scout's voice | ~$5 | [Adafruit](https://www.adafruit.com), [AliExpress](https://aliexpress.com) | 1 |

**Phase 1 total: ~$357**

---

### Phase 2: Scout Can See (~$30-135 extra)

Choose your camera setup. The IMX219 is the budget pick. The IMX477 is sharper but costs more. Room cameras are optional but recommended.

| # | Part | Model | Purpose | Cost (USD) | Where to Buy | Phase |
|---|------|-------|---------|-----------|-------------|-------|
| 6 | Onboard camera (budget) | Arducam IMX219 120-deg MIPI-CSI | Wide-angle onboard vision - good enough for object detection | ~$15 | [Arducam](https://www.arducam.com), [Amazon](https://amazon.com) | 2 |
| 7 | Onboard camera (upgrade) | Arducam IMX477 HQ MIPI-CSI | Higher resolution onboard vision - better at range | ~$60 | [Arducam](https://www.arducam.com), [Amazon](https://amazon.com) | 2 |
| 8 | Room cameras (x4) | Freenove ESP32-S3-CAM | Fixed Wi-Fi cameras for persistent room monitoring (local network only) | ~$60 (set of 4) | [Amazon](https://amazon.com), [AliExpress](https://aliexpress.com) | 2 |

**Phase 2 total: ~$15-60 (onboard only) or ~$75-120 (with room cameras)**

> **Note:** Room cameras connect to Scout's local network via ESP-NOW or local Wi-Fi AP. They never touch the internet. Scout runs its own isolated access point.

---

### Phase 3: Scout Can Move (~$250-300 extra)

This is the biggest single purchase. Scout becomes a mobile robot.

| # | Part | Model | Purpose | Cost (USD) | Where to Buy | Phase |
|---|------|-------|---------|-----------|-------------|-------|
| 9 | Chassis | 4WD aluminum chassis kit OR 3D printed | Robot body - holds everything together | ~$35 | [Amazon](https://amazon.com), [RobotShop](https://robotshop.com) | 3 |
| 10 | Motors (x4) | Pololu 37D 50:1 metal gearmotor with 64 CPR encoder | Drive motors with built-in encoders for odometry | ~$100 (set of 4) | [Pololu](https://www.pololu.com/product/4753) | 3 |
| 11 | Wheels (x4) | Pololu 80mm silicone wheels | Traction on indoor surfaces | ~$32 (set of 4) | [Pololu](https://www.pololu.com/product/1435) | 3 |
| 12 | Motor drivers (x2) | Cytron MDD10A dual 10A motor driver | PWM motor control, 2 motors per driver | ~$30 (pair) | [Cytron](https://www.cytron.io), [Amazon](https://amazon.com) | 3 |
| 13 | LIDAR | SLAMTEC RPLIDAR C1 | 360-degree laser scanning for SLAM mapping | ~$100 | [SLAMTEC](https://www.slamtec.com), [Amazon](https://amazon.com) | 3 |
| 14 | IMU | Bosch BNO055 9-axis IMU | Orientation and acceleration for sensor fusion | ~$30 | [Adafruit](https://www.adafruit.com/product/2472), [DigiKey](https://digikey.com) | 3 |
| 15 | ToF sensors (x4) | VL53L1X Time-of-Flight | Close-range obstacle detection (front, back, left, right) | ~$56 (set of 4) | [Pololu](https://www.pololu.com), [Adafruit](https://www.adafruit.com) | 3 |
| 16 | Cliff sensors (x2) | TCRT5000 IR reflective sensor | Detects stairs and drop-offs | ~$4 (pair) | [AliExpress](https://aliexpress.com), [Amazon](https://amazon.com) | 3 |
| 17 | Bump sensors (x2) | Microswitch with lever arm | Physical contact detection for obstacle backup | ~$4 (pair) | [AliExpress](https://aliexpress.com), [Amazon](https://amazon.com) | 3 |
| 18 | Battery | 4S 14.8V 5000mAh LiPo | Main power source - approximately 2-3 hours runtime | ~$40 | [HobbyKing](https://hobbyking.com), [Amazon](https://amazon.com) | 3 |
| 19 | Battery management | 4S BMS board + balance charger | Safe charging and discharge protection | ~$45 | [Amazon](https://amazon.com), [AliExpress](https://aliexpress.com) | 3 |
| 20 | Power converter | DFRobot 16A DC-DC buck converter | Steps 14.8V battery down to 5V/12V rails | ~$12 | [DFRobot](https://www.dfrobot.com), [DigiKey](https://digikey.com) | 3 |
| 21 | OLED displays (x2) | SH1106 1.3" I2C OLED 128x64 | Scout's "eyes" - shows expressions and status | ~$26 (pair) | [AliExpress](https://aliexpress.com), [Amazon](https://amazon.com) | 3 |
| 22 | LED ring | NeoPixel 16-LED ring (WS2812B) | Status indicator and emotional expression lighting | ~$8 | [Adafruit](https://www.adafruit.com/product/1463), [AliExpress](https://aliexpress.com) | 3 |
| 23 | E-stop button | Mushroom head emergency stop, NO+NC | Kills all motor power immediately | ~$3 | [AliExpress](https://aliexpress.com), [Amazon](https://amazon.com) | 3 |
| 24 | Wiring and connectors | JST-XH, Dupont, XT60 connectors, 18-22 AWG wire, standoffs, zip ties, heat shrink | All the bits that hold it together | ~$70 | [Amazon](https://amazon.com), [AliExpress](https://aliexpress.com) | 3 |

**Phase 3 total: ~$595**

---

### Phase 4: Scout Remembers Everything ($0 extra)

No new hardware. This phase is a software upgrade that adds the spatial object memory system. It uses the cameras from Phase 2 and the navigation stack from Phase 3 to build a persistent database of where objects are.

---

### Phase 5: Scout Knows Us ($0 extra)

No new hardware. Uses the existing onboard camera to capture face embeddings with ArcFace. Enrollment takes about 5 seconds per person - Scout captures multiple angles and stores encrypted embeddings locally.

---

### Phase 6: Scout's Sky Eye (~$150-200 extra)

Advanced build. Not required for a fully functional Scout.

| # | Part | Model | Purpose | Cost (USD) | Where to Buy | Phase |
|---|------|-------|---------|-----------|-------------|-------|
| 25 | Drone frame | 65-85mm micro brushless frame | Lightweight indoor drone airframe | ~$15 | [Amazon](https://amazon.com), [GetFPV](https://www.getfpv.com) | 6 |
| 26 | Motors (x4) | 0802/1103 brushless motors | Drone propulsion | ~$40 (set of 4) | [GetFPV](https://www.getfpv.com), [Amazon](https://amazon.com) | 6 |
| 27 | Flight controller | BetaFlight F4/F7 FC + ESC AIO | Motor control and stabilization | ~$35 | [GetFPV](https://www.getfpv.com), [Amazon](https://amazon.com) | 6 |
| 28 | FPV camera | Caddx Ant Nano | Lightweight camera for aerial vision | ~$20 | [GetFPV](https://www.getfpv.com), [Caddx](https://caddxfpv.com) | 6 |
| 29 | Props | 40mm triblade props (x8) | Propellers - buy spares, you will break them | ~$8 | [GetFPV](https://www.getfpv.com), [Amazon](https://amazon.com) | 6 |
| 30 | Drone battery | 1S 450mAh LiPo (x2) OR tether cable | Power source - tether gives unlimited flight time | ~$15 | [Amazon](https://amazon.com), [GetFPV](https://www.getfpv.com) | 6 |
| 31 | Tether spool | Custom 3D printed + thin power wire | Physical tether for safety and continuous power | ~$10 (materials) | 3D print + wire | 6 |

**Phase 6 total: ~$143-200**

---

## Full BOM Summary

| Phase | Description | Component Count | Phase Cost | Cumulative Cost |
|-------|------------|----------------|-----------|----------------|
| 1 | Scout Can Talk | 5 parts | ~$357 | ~$357 |
| 2 | Scout Can See | 2-3 parts | ~$15-120 | ~$372-477 |
| 3 | Scout Can Move | 16 parts | ~$595 | ~$967-1,072 |
| 4 | Scout Remembers | 0 parts (software) | $0 | ~$967-1,072 |
| 5 | Scout Knows Us | 0 parts (software) | $0 | ~$967-1,072 |
| 6 | Scout's Sky Eye | 7 parts | ~$143-200 | ~$1,110-1,272 |

---

## Tools Required

You need these tools to build Scout. Most makers already have them.

| Tool | Purpose | Approx. Cost |
|------|---------|-------------|
| Soldering iron (temp-controlled) | Wiring connections, headers, sensor boards | ~$30-60 |
| Solder (60/40 or lead-free) + flux | Soldering consumables | ~$15 |
| Multimeter | Testing voltages, continuity, debugging | ~$20-40 |
| Wire strippers | Preparing wires for connectors | ~$10 |
| Hex driver set (M2, M2.5, M3) | Chassis assembly, motor mounting | ~$10 |
| 3D printer (or printing service) | Custom mounts, brackets, chassis parts | ~$200+ (or $5-20 per part via service) |
| Crimping tool (JST/Dupont) | Making clean connectors | ~$25 |
| Heat gun or lighter | Heat shrink tubing | ~$15 |

> **No 3D printer?** Use [JLCPCB](https://jlcpcb.com), [Craftcloud](https://craftcloud3d.com), or your local library's makerspace. STL files are in `hardware/3d-models/`.

---

## Why These Parts

### Why Pololu 37D motors over cheap yellow TT motors?

TT motors have no encoders, inconsistent speed between units, and plastic gearboxes that strip under load. The Pololu 37D motors have metal gears, built-in 64 CPR encoders for precise odometry, and consistent performance. Good odometry is critical for SLAM. Cheap motors make navigation unreliable and frustrating to debug.

### Why RPLIDAR C1 over cheaper LIDAR units?

The C1 hits a sweet spot: 12-meter range, 8000 samples/second, compact form factor, and direct ROS 2 driver support. Cheaper units (like the A1) have lower sample rates and shorter range. More expensive units (A2, A3) are overkill for indoor home use. The C1 also draws only ~1W - important on battery power.

### Why ESP32-S3-CAM instead of the original ESP32-CAM?

The ESP32-S3 has a faster processor, native USB, and better Wi-Fi performance. The original ESP32-CAM uses a slow serial interface for programming and has less RAM. The S3 variant also supports ESP-NOW for low-latency peer-to-peer communication with Scout's main board - no router required.

### Why BNO055 IMU?

The BNO055 has an onboard sensor fusion processor that outputs calibrated quaternion orientation directly. Most IMUs (MPU6050, ICM-20948) require you to implement your own sensor fusion algorithm (Madgwick, EKF). The BNO055 handles this in hardware - one less thing to debug and tune.

### Why Samsung 970 EVO Plus?

It is one of the most reliable and widely tested NVMe drives. The 250GB size gives plenty of room for the OS, AI models (Whisper ~1.5GB, YOLOv8n ~6MB, Llama 3.2 1B ~1.3GB, ArcFace ~250MB), the spatial database, and recorded data. The Jetson Orin NX boots from NVMe, so drive reliability matters.

---

## Regional Purchasing Notes

Prices above are approximate USD. Availability and pricing vary by region.

| Region | Best Sources | Notes |
|--------|-------------|-------|
| **USA** | Amazon, Pololu, Adafruit, DigiKey, Mouser | Fastest shipping. Pololu and Adafruit ship direct. |
| **EU** | Mouser EU, Farnell, RS Components, AliExpress | Check RS Components for Pololu equivalents. VAT adds 20-25%. |
| **Australia** | Core Electronics, RS Components AU, AliExpress | [Core Electronics](https://core-electronics.com.au) stocks Adafruit and Pololu. AliExpress for bulk sensors. |
| **UK** | Pimoroni, RS Components, The Pi Hut, Amazon UK | Pimoroni carries Adafruit products. |
| **Budget (global)** | AliExpress, Banggood | 2-4 week shipping. Good for sensors, connectors, and wiring. Avoid for critical components (board, LIDAR, motors). |

> **Tip:** Buy the VENTUNO Q board, LIDAR, motors, and NVMe from reputable retailers. Buy sensors, connectors, and wiring from AliExpress to save 40-60% on those parts.

---

## What About the Minimum Viable Build?

If ~$1,100 is too much to start, here is the stripped-down Minimum Viable build at ~$750:

| Change | Saves |
|--------|-------|
| Skip the 4 room cameras (ESP32-S3-CAM) - use onboard camera only | ~$60 |
| Skip the RPLIDAR C1 - use ToF sensors only for obstacle avoidance (no SLAM mapping) | ~$100 |
| Use 2 motors instead of 4 (2WD with caster wheel) | ~$50 |
| Use 1 motor driver instead of 2 | ~$15 |
| Use 1 OLED display instead of 2 | ~$13 |
| Skip the IMX477 upgrade - use IMX219 only | ~$45 |
| Smaller battery (3S 2200mAh) | ~$15 |

This gives you a working Scout that talks, sees, moves (2WD), and remembers objects. You lose room-wide monitoring, accurate SLAM maps, and 4WD stability - but it all still works. Upgrade parts later as your budget allows.
