# VENTUNO Q Pin Mapping Reference

Pin assignments for connecting Scout's peripherals to the Arduino VENTUNO Q board.

> **Status:** Pin numbers marked **TBD** are pending final VENTUNO Q hardware documentation from Arduino. This reference documents the signal types and header locations based on early board specifications. Exact GPIO numbers will be updated when the official pinout is published.

## Board Overview

The VENTUNO Q combines two processors on one board:

| Processor | Role in Scout | Connectivity |
|-----------|---------------|-------------|
| Jetson Orin NX (Cortex-A78AE) | AI workloads, ROS 2, Linux | MIPI-CSI, USB, PCIe, I2C, SPI, UART |
| STM32H5 (Cortex-M33) | Real-time motor/sensor control | CAN-FD, GPIO, PWM, ADC, I2C |

The two processors communicate over a **CAN-FD bus** that is internal to the board. Scout's firmware (`firmware/stm32-motor-control/`) runs on the STM32H5 side and exchanges velocity commands and sensor data with the Linux/ROS 2 side via CAN-FD messages.

## JMISC Header

The JMISC header exposes signals from both processors. This is the primary expansion header for Scout peripherals.

### I2S Signals (Audio)

Used for INMP441 microphones and MAX98357A amplifier.

| Signal | Direction | Connected To | JMISC Pin | GPIO |
|--------|-----------|-------------|-----------|------|
| I2S_BCLK | Output | Mic + Amp bit clock | TBD | TBD |
| I2S_WS | Output | Mic + Amp word select (L/R) | TBD | TBD |
| I2S_DIN | Input | INMP441 mic data (stereo, 2 mics on one line) | TBD | TBD |
| I2S_DOUT | Output | MAX98357A amp data | TBD | TBD |

**Notes:**
- Two INMP441 microphones share the same I2S bus. One is configured as left channel (L/R pin LOW), the other as right channel (L/R pin HIGH).
- The MAX98357A uses a separate I2S data-out line (DOUT) but shares BCLK and WS.
- Sample rate: 16 kHz for speech recognition (Whisper), 22.05 kHz for TTS playback (Piper).

### SPI Signals

Available for expansion. Not used by base Scout hardware, but reserved for future peripherals (e.g., display driver, additional sensors).

| Signal | Direction | JMISC Pin | GPIO |
|--------|-----------|-----------|------|
| SPI_MOSI | Output | TBD | TBD |
| SPI_MISO | Input | TBD | TBD |
| SPI_SCLK | Output | TBD | TBD |
| SPI_CS0 | Output | TBD | TBD |

### CAN-FD Bus

Internal to the board - connects the Jetson Orin NX (Linux side) to the STM32H5 (real-time side). Scout uses this for all motor commands and sensor telemetry.

| Signal | Notes |
|--------|-------|
| CAN_H | CAN-FD high line (internal) |
| CAN_L | CAN-FD low line (internal) |

The CAN-FD bus is pre-wired on the VENTUNO Q. No external connections needed. See `firmware/stm32-motor-control/src/can_bridge.h` for the message protocol.

**CAN-FD Message IDs:**

| ID | Direction | Payload |
|----|-----------|---------|
| 0x100 | Orin NX to STM32 | Heartbeat |
| 0x101 | Orin NX to STM32 | Velocity command (4 floats) |
| 0x200 | STM32 to Orin NX | Odometry (4 encoder counts) |
| 0x201 | STM32 to Orin NX | Battery voltage (float) |
| 0x202 | STM32 to Orin NX | Cliff sensor readings (2 ints) |
| 0x2FF | STM32 to Orin NX | Safety alert (string) |

## STM32H5 GPIO Assignments

These pins are managed by the STM32H5 firmware. The Jetson Orin NX does not access them directly - it receives processed data over CAN-FD.

### Motor Control

Four Pololu 37D motors driven by two Cytron MDD10A dual motor drivers. Each motor needs one PWM and one direction pin.

| Motor | PWM Pin | DIR Pin | Driver | Channel |
|-------|---------|---------|--------|---------|
| Front-Left (M0) | TBD | TBD | MDD10A #1 | CH A |
| Front-Right (M1) | TBD | TBD | MDD10A #1 | CH B |
| Rear-Left (M2) | TBD | TBD | MDD10A #2 | CH A |
| Rear-Right (M3) | TBD | TBD | MDD10A #2 | CH B |

PWM frequency: 20 kHz (above audible range to avoid motor whine).

### Encoder Inputs

Each Pololu 37D motor has a 64 CPR quadrature encoder (two channels per encoder).

| Encoder | Channel A Pin | Channel B Pin |
|---------|--------------|--------------|
| Front-Left (E0) | TBD | TBD |
| Front-Right (E1) | TBD | TBD |
| Rear-Left (E2) | TBD | TBD |
| Rear-Right (E3) | TBD | TBD |

Encoders use hardware timer input capture for accurate counting at high speeds.

### Cliff Sensors

Two TCRT5000 IR reflective sensors on the front edge of the chassis. They detect drop-offs (stairs, table edges) by measuring reflected IR intensity.

| Sensor | Analog Pin | Threshold | Action |
|--------|-----------|-----------|--------|
| Cliff-Left | TBD (ADC) | < 200 (12-bit ADC) | Emergency stop + reverse |
| Cliff-Right | TBD (ADC) | < 200 (12-bit ADC) | Emergency stop + reverse |

Threshold is configurable via CAN-FD command. The default value of 200 (out of 4096) is conservative - a low reading means no surface detected below the sensor.

### Emergency Stop

The e-stop button connects to a GPIO with an external pull-up. Pressing the button pulls the pin LOW and triggers an interrupt that kills motor power immediately via the motor relay.

| Signal | Pin | Type | Active |
|--------|-----|------|--------|
| E-stop input | TBD | GPIO input, external pull-up, interrupt-enabled | LOW = stop |
| Motor relay control | TBD | GPIO output | HIGH = motors enabled, LOW = motors killed |

The e-stop is handled entirely in hardware interrupt context. It does not depend on the main firmware loop or CAN-FD communication. See `firmware/stm32-motor-control/src/safety.h`.

### Battery Monitoring

Battery voltage is read through an INA219 current/voltage sensor on the I2C bus.

| Signal | Pin/Bus | Notes |
|--------|---------|-------|
| Battery voltage | I2C (INA219 at address 0x40) | 4S LiPo: 12.0V (empty) to 16.8V (full) |

The STM32H5 reads battery voltage periodically and sends it to the Orin NX side via CAN-FD message 0x201.

### Bump Sensors

Two microswitches with lever arms on the front of the chassis.

| Sensor | Pin | Type |
|--------|-----|------|
| Bump-Left | TBD | GPIO input, internal pull-up |
| Bump-Right | TBD | GPIO input, internal pull-up |

## Jetson Orin NX Connections

These are managed by the Linux/ROS 2 side.

### MIPI-CSI Camera

| Signal | Connector | Notes |
|--------|-----------|-------|
| CSI camera | Onboard MIPI-CSI connector | Arducam IMX219 or IMX477 |

The CSI camera is directly supported by the Jetson Orin NX through its onboard MIPI-CSI interface. No GPIO configuration needed - it appears as a V4L2 device under Linux.

### RPLIDAR C1

| Signal | Interface | Notes |
|--------|-----------|-------|
| RPLIDAR C1 | USB (onboard USB 3.0 port) | Shows up as `/dev/ttyUSB0` or similar |

### I2C Bus (Shared)

Several sensors share the Orin NX I2C bus.

| Device | Address | Purpose |
|--------|---------|---------|
| BNO055 IMU | 0x28 | 9-axis orientation + acceleration |
| SH1106 OLED #1 | 0x3C | Left eye display |
| SH1106 OLED #2 | 0x3D | Right eye display (address jumper) |
| VL53L1X ToF #1 | 0x29 (default, remapped) | Front distance |
| VL53L1X ToF #2 | 0x2A (remapped) | Left distance |
| VL53L1X ToF #3 | 0x2B (remapped) | Right distance |
| VL53L1X ToF #4 | 0x2C (remapped) | Rear distance |

The four VL53L1X sensors share the I2C bus. At boot, the firmware holds all XSHUT pins LOW, then brings each sensor up one at a time to assign unique I2C addresses.

### NeoPixel LED Ring

| Signal | Pin | Notes |
|--------|-----|-------|
| NeoPixel data | TBD (GPIO) | WS2812B protocol, 16 LEDs, 5V logic |

The NeoPixel ring runs on 5V power but the data line may need a level shifter from 3.3V GPIO. Use a 74AHCT125 or similar if the LEDs are unreliable on 3.3V data.

## Power Rails

| Rail | Voltage | Source | Consumers |
|------|---------|--------|-----------|
| Battery raw | 14.8V nominal (12.0-16.8V) | 4S LiPo via BMS | Motor drivers (direct) |
| 5V regulated | 5.0V | DFRobot buck converter | VENTUNO Q, NeoPixel ring, sensors |
| 3.3V regulated | 3.3V | VENTUNO Q onboard regulator | I2C sensors, OLED displays, cliff sensors |

### Power Budget (Estimated)

| Consumer | Voltage | Max Current | Notes |
|----------|---------|-------------|-------|
| VENTUNO Q (Orin NX + STM32H5) | 5V | ~3A (15W peak) | GPU inference draws peak power |
| Motors (x4) | 14.8V | ~2A each, 8A total peak | Stall current is higher - motor drivers limit it |
| RPLIDAR C1 | 5V | ~0.5A | |
| Sensors + displays | 3.3V/5V | ~0.3A total | |
| NeoPixel ring (16 LEDs) | 5V | ~1A peak (all white) | Typically < 0.3A with animations |
| **Total system peak** | | **~12-13A from battery** | |

The 4S 5000mAh LiPo provides roughly 2-3 hours of runtime with typical patrol usage (motors running ~50% of the time, AI inference continuous).

## Wiring Diagram

A full wiring diagram is planned for `hardware/wiring/diagrams/`. Until then, use this reference and the CAN-FD message table to understand the data flow between processors.

## Updating This Document

When Arduino publishes the final VENTUNO Q pinout documentation, update all **TBD** entries in this file and remove the status notice at the top. Open a PR with the branch name `hardware/ventuno-q-pinout-final`.
