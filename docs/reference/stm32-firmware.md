# STM32H5 Firmware Reference

The STM32H5F5 (Cortex-M33 @ 250 MHz) handles real-time motor control, sensor reading, and safety enforcement on the VENTUNO Q. It runs independently of the Qualcomm Linux side. If Linux crashes, the STM32H5 stops all motors and enters safe mode.

This reference covers building, flashing, configuring, and tuning the firmware.

## Prerequisites

- [PlatformIO Core](https://platformio.org/install/cli) (CLI or VS Code extension)
- ST-Link V2 programmer (for SWD flashing) OR USB cable (for DFU flashing)
- The `firmware/stm32-motor-control/` directory from the Home Scout repository

---

## Project Structure

```
firmware/stm32-motor-control/
  platformio.ini          # Build configuration
  src/
    main.cpp              # Entry point and main loop (1 kHz)
    can_protocol.cpp      # CAN-FD message parsing and dispatch
    can_protocol.h
    motor_control.cpp     # PID controller and PWM output
    motor_control.h
    safety.cpp            # Watchdog, E-stop, cliff sensors, heartbeat
    safety.h
    encoder.cpp           # Quadrature encoder reading
    encoder.h
    battery.cpp           # ADC-based voltage and current monitoring
    battery.h
    telemetry.cpp         # Telemetry frame assembly and transmission
    telemetry.h
  include/
    config.h              # Pin definitions, PID defaults, CAN IDs
    scout_types.h         # Shared data structures
  test/
    test_pid.cpp          # PID controller unit tests
    test_can_protocol.cpp # CAN frame parsing tests
    test_safety.cpp       # Safety state machine tests
```

---

## Building

### Build with PlatformIO CLI

```bash
cd firmware/stm32-motor-control

# Build the default target
pio run

# Build and upload (requires connected ST-Link or USB DFU)
pio run --target upload

# Run unit tests on native platform (no hardware required)
pio test -e native
```

### Build with VS Code

1. Open the `firmware/stm32-motor-control/` folder in VS Code
2. Install the PlatformIO extension if not already installed
3. Click the PlatformIO checkmark icon in the bottom toolbar to build
4. Click the arrow icon to upload

### platformio.ini overview

```ini
[env:ventuno_stm32h5]
platform = ststm32
board = nucleo_h563zi        ; Closest supported board - adjust for VENTUNO Q
framework = zephyr
build_flags =
    -DSCOUT_FIRMWARE
    -DCAN_FD_ENABLED
    -DWATCHDOG_TIMEOUT_MS=100
    -DHEARTBEAT_INTERVAL_MS=50
    -DPID_LOOP_HZ=100
    -DMAX_SPEED_MPS=0.3
monitor_speed = 115200
debug_tool = stlink

[env:native]
platform = native
test_framework = unity
build_flags = -DUNIT_TEST
```

---

## Flashing

### Option A: ST-Link (SWD)

ST-Link is the recommended method. It supports debugging and does not require the STM32H5 to be in a special boot mode.

1. Connect the ST-Link V2 to the VENTUNO Q's SWD header:

| ST-Link Pin | VENTUNO Q SWD Pin |
|-------------|-------------------|
| SWDIO | SWDIO |
| SWCLK | SWCLK |
| GND | GND |
| 3.3V | (optional - board has its own power) |

2. Flash:

```bash
pio run --target upload
```

3. Verify:

```bash
# Open serial monitor to see boot messages
pio device monitor --baud 115200
```

You should see:

```
[SCOUT-FW] Home Scout STM32H5 Firmware v1.0.0
[SCOUT-FW] CAN-FD initialized: 500k/2M
[SCOUT-FW] Watchdog armed: 100ms
[SCOUT-FW] Waiting for heartbeat from Qualcomm...
```

### Option B: USB DFU (No ST-Link Required)

If you do not have an ST-Link, use the STM32's built-in USB DFU bootloader.

1. Put the STM32H5 into DFU mode:
   - Hold the BOOT0 button (or set BOOT0 jumper HIGH)
   - Press and release RESET
   - Release BOOT0
2. Verify the STM32 appears as a USB DFU device:

```bash
# Linux
lsusb | grep "STMicroelectronics"
# Should show "STM32 BOOTLOADER" or similar

# Install dfu-util if needed
sudo apt install -y dfu-util
dfu-util -l
```

3. Flash:

```bash
pio run --target upload --upload-protocol dfu
```

4. Reset the STM32H5 (press RESET or power-cycle the board)

---

## CAN-FD Message Protocol

All communication between the Qualcomm SoC (Linux/ROS 2) and the STM32H5 uses CAN-FD frames on the `can0` interface. CAN-FD allows up to 64 bytes per frame at the higher data bitrate.

### Message ID Map

| ID | Name | Direction | Payload | Rate |
|----|------|-----------|---------|------|
| `0x100` | `CMD_VELOCITY` | Qualcomm -> STM32 | Target linear and angular velocity | 20 Hz |
| `0x101` | `CMD_MOTOR_DIRECT` | Qualcomm -> STM32 | Direct PWM duty per motor (calibration mode only) | On demand |
| `0x102` | `CMD_PID_TUNE` | Qualcomm -> STM32 | PID gains (Kp, Ki, Kd) for a specific motor | On demand |
| `0x103` | `CMD_CONFIG` | Qualcomm -> STM32 | Runtime configuration updates | On demand |
| `0x104` | `CMD_CALIBRATE` | Qualcomm -> STM32 | Start motor calibration sequence | On demand |
| `0x1FF` | `SAFETY_ALERT` | Both | Safety state change notification | On event |
| `0x200` | `HEARTBEAT` | Both | Alive signal with timestamp and state | 20 Hz |
| `0x201` | `TELEM_ODOMETRY` | STM32 -> Qualcomm | Wheel encoder ticks, computed velocity | 50 Hz |
| `0x202` | `TELEM_BATTERY` | STM32 -> Qualcomm | Voltage, current, charge estimate | 1 Hz |
| `0x203` | `TELEM_SENSORS` | STM32 -> Qualcomm | Cliff sensor states, bump sensor states | 10 Hz |
| `0x204` | `TELEM_MOTOR_STATE` | STM32 -> Qualcomm | Per-motor RPM, current draw, temperature | 10 Hz |
| `0x205` | `TELEM_IMU_RAW` | STM32 -> Qualcomm | Raw accelerometer and gyroscope data | 50 Hz |
| `0x2FF` | `TELEM_DIAGNOSTICS` | STM32 -> Qualcomm | Error counters, uptime, firmware version | 0.1 Hz |

### Payload Formats

#### CMD_VELOCITY (0x100) - 8 bytes

```
Byte 0-3: linear_velocity  (float32, m/s, positive = forward)
Byte 4-7: angular_velocity  (float32, rad/s, positive = counter-clockwise)
```

#### TELEM_ODOMETRY (0x201) - 16 bytes

```
Byte  0-3:  left_ticks   (int32, cumulative encoder ticks)
Byte  4-7:  right_ticks  (int32, cumulative encoder ticks)
Byte  8-11: left_rpm     (float32, current RPM)
Byte 12-15: right_rpm    (float32, current RPM)
```

#### TELEM_BATTERY (0x202) - 12 bytes

```
Byte 0-3: voltage      (float32, volts)
Byte 4-7: current      (float32, amps, positive = discharging)
Byte 8-11: charge_pct  (float32, estimated state of charge 0.0 - 1.0)
```

#### HEARTBEAT (0x200) - 8 bytes

```
Byte 0-3: timestamp_ms  (uint32, milliseconds since boot)
Byte 4:   state          (uint8, see state enum below)
Byte 5:   error_flags    (uint8, bitfield)
Byte 6-7: reserved
```

State values:

| Value | State | Description |
|-------|-------|-------------|
| `0x00` | `BOOT` | Firmware just started, waiting for heartbeat |
| `0x01` | `IDLE` | Ready, no velocity command active |
| `0x02` | `RUNNING` | Executing velocity commands |
| `0x03` | `SAFE_MODE` | Motors stopped due to safety condition |
| `0x04` | `ESTOP` | E-stop pressed, motors physically disconnected |
| `0x05` | `CALIBRATING` | Running motor calibration sequence |
| `0xFF` | `ERROR` | Unrecoverable error, requires power cycle |

Error flags (bitfield):

| Bit | Flag | Meaning |
|-----|------|---------|
| 0 | `ERR_HEARTBEAT_LOST` | No heartbeat from Qualcomm for 500ms+ |
| 1 | `ERR_MOTOR_OVERCURRENT` | Motor current exceeds safe limit |
| 2 | `ERR_BATTERY_LOW` | Battery voltage below 12.0V |
| 3 | `ERR_BATTERY_CRITICAL` | Battery voltage below 11.0V |
| 4 | `ERR_CLIFF_DETECTED` | Cliff sensor triggered |
| 5 | `ERR_WATCHDOG_RESET` | Previous boot was a watchdog reset |
| 6 | `ERR_CAN_BUS_OFF` | CAN controller entered bus-off state |
| 7 | Reserved | |

#### SAFETY_ALERT (0x1FF) - 4 bytes

```
Byte 0: alert_type  (uint8, see below)
Byte 1: severity    (uint8, 0=info, 1=warning, 2=critical)
Byte 2-3: detail    (uint16, alert-specific data)
```

Alert types:

| Value | Alert | Detail Field |
|-------|-------|-------------|
| `0x01` | E-stop pressed | 0 |
| `0x02` | E-stop released | 0 |
| `0x03` | Cliff detected | Sensor bitmask (which sensors triggered) |
| `0x04` | Bump detected | Sensor bitmask |
| `0x05` | Battery low | Voltage in mV |
| `0x06` | Battery critical | Voltage in mV |
| `0x07` | Motor overcurrent | Motor index |
| `0x08` | Heartbeat lost | Missed count |
| `0x09` | Watchdog reset | Previous error flags |

---

## PID Tuning Guide

Each motor runs an independent PID loop at 100 Hz. The controller converts a target RPM into a PWM duty cycle using encoder feedback.

### Default PID Gains

```
Kp = 1.0    (proportional gain)
Ki = 0.5    (integral gain)
Kd = 0.05   (derivative gain)
```

These defaults are conservative and work for the Pololu 37D 50:1 motors listed in the BOM. You will likely need to tune them for your specific build.

### Tuning Procedure

1. **Set Ki and Kd to zero.** Start with proportional-only control.

```bash
# Send PID tune command via CAN (from Qualcomm side)
# Motor 0 (front-left), Kp=1.0, Ki=0.0, Kd=0.0
cansend can0 102#00000000003F8000000000000000000000000000
```

Or use the Scout CLI:

```bash
scout-cli motor pid --motor 0 --kp 1.0 --ki 0.0 --kd 0.0
```

2. **Increase Kp** until the motor responds quickly to velocity changes but does not oscillate. If the motor overshoots and oscillates, reduce Kp.

3. **Add Ki** to eliminate steady-state error. Start small (0.1) and increase until the motor reaches and holds the target RPM. If it starts to oscillate or wind up, reduce Ki.

4. **Add Kd** to dampen oscillation. Start small (0.01). Increase if the motor oscillates around the target. Too much Kd makes the response sluggish.

5. **Test at different speeds.** Verify the PID holds at 10%, 50%, and 100% of max speed.

6. **Save gains.** Once tuned, update the defaults in `include/config.h`:

```cpp
#define PID_KP_DEFAULT  1.2f
#define PID_KI_DEFAULT  0.4f
#define PID_KD_DEFAULT  0.03f
```

### Monitoring PID Performance

Use the `TELEM_MOTOR_STATE` (0x204) frames to monitor actual vs. commanded RPM:

```bash
# Watch motor telemetry on the Qualcomm side
candump can0,204:7FF

# Or use the CLI
scout-cli motor status --live
```

Look for:
- **Steady-state error**: actual RPM consistently below or above target -> increase Ki
- **Oscillation**: RPM swings above and below target repeatedly -> reduce Kp or increase Kd
- **Slow response**: takes more than 500ms to reach target RPM -> increase Kp
- **Overshoot**: RPM spikes past target then settles -> increase Kd or reduce Kp

---

## Motor Calibration

Run calibration after first assembly or whenever you change motors, wheels, or gearing.

### What calibration measures

- **Encoder CPR verification**: confirms ticks-per-revolution matches the motor spec (64 CPR for Pololu 37D with 50:1 gear ratio = 3200 ticks/wheel revolution)
- **Wheel diameter**: computes effective wheel circumference from encoder ticks over a measured distance
- **Motor direction**: verifies that positive PWM = forward movement for each motor
- **Dead zone**: finds the minimum PWM duty cycle that actually moves each motor (overcoming static friction)

### Running calibration

```bash
# From the Qualcomm side
scout-cli motor calibrate

# Or send the calibration command via CAN
cansend can0 104#01
```

The calibration sequence:

1. Scout asks you to place it on a flat surface with wheels free to spin (lift it up on a stand)
2. Each motor spins forward for 2 seconds, then backward for 2 seconds
3. Encoder ticks are counted and compared to expected values
4. Dead zone is measured by ramping PWM from 0 until motion is detected
5. Results are stored in flash and printed to the serial console

### Calibration output example

```
[CAL] Motor 0 (front-left):
[CAL]   Direction: OK (forward = positive PWM)
[CAL]   Encoder CPR: 3198 (expected 3200, error 0.06%)
[CAL]   Dead zone: 12% duty
[CAL]   Max RPM: 150

[CAL] Motor 1 (front-right):
[CAL]   Direction: REVERSED - swapping polarity
[CAL]   Encoder CPR: 3204 (expected 3200, error 0.12%)
[CAL]   Dead zone: 14% duty
[CAL]   Max RPM: 148
```

If a motor's direction is reversed, calibration fixes this in software. You do not need to rewire anything.

---

## Watchdog Configuration

The STM32H5's hardware watchdog (IWDG) resets the microcontroller if the firmware hangs. This is a silicon-level feature - no software can disable it once armed.

### Configuration

```cpp
// include/config.h
#define WATCHDOG_TIMEOUT_MS  100    // Reset if not fed within 100ms
#define WATCHDOG_WINDOW_MS   0      // No window (feed anytime before timeout)
```

### Behavior on watchdog reset

1. STM32H5 reboots into safe mode (all motors stopped)
2. Error flag `ERR_WATCHDOG_RESET` is set in the heartbeat frame
3. Status LED flashes red
4. Buzzer sounds three short beeps
5. STM32H5 waits for heartbeat from Qualcomm before resuming

### Feeding the watchdog

The main loop feeds the watchdog at the end of each 1 kHz cycle. If any part of the main loop blocks for more than 100ms, the watchdog resets the system. This is intentional - a hung loop means motors could be running without supervision.

```cpp
// Main loop structure (simplified)
void loop() {
    safety_check();           // E-stop, cliff sensors, battery
    heartbeat_check();        // Qualcomm heartbeat monitoring
    process_can_messages();   // Handle incoming CAN-FD frames
    pid_update();             // Motor PID at 100 Hz (every 10th iteration)
    send_telemetry();         // Transmit odometry, battery, sensor data
    feed_watchdog();          // Must happen within 100ms of previous feed
}
```

---

## Serial Debug Console

The STM32H5 outputs debug logs over UART at 115200 baud. Connect a USB-to-UART adapter to the SWD header's TX/RX pins, or use the ST-Link's virtual COM port.

```bash
# PlatformIO serial monitor
pio device monitor --baud 115200

# Or use screen/minicom
screen /dev/ttyACM0 115200
```

### Log levels

Control log verbosity by sending a `CMD_CONFIG` (0x103) frame or editing `config.h`:

```cpp
#define LOG_LEVEL  LOG_INFO   // LOG_DEBUG, LOG_INFO, LOG_WARN, LOG_ERROR
```

---

## Firmware Update Procedure

1. Pull the latest firmware from the repository
2. Build: `pio run`
3. Flash via ST-Link or DFU (see Flashing section above)
4. Verify by checking the `TELEM_DIAGNOSTICS` (0x2FF) frame for the new firmware version
5. Re-run motor calibration if motor-related code changed: `scout-cli motor calibrate`

---

## Troubleshooting

### STM32H5 not responding to CAN frames

- Verify CAN-FD interface is up on both sides: `ip link show can0`
- Check CAN-H/CAN-L wiring and 120-ohm termination resistors
- Check error counters: `ip -s link show can0`
- Verify bitrate matches (500k arbitration, 2M data)
- Flash the firmware again - it may have been corrupted

### Motors not spinning

- Check the STM32H5 state in the heartbeat frame (is it in SAFE_MODE or ESTOP?)
- Verify motor driver enable pins are connected and not pulled low
- Check motor power rail voltage with a multimeter (should be ~14.8V from battery)
- Run calibration to test each motor individually

### Watchdog keeps resetting

- Connect the debug console and check for error messages
- A tight loop or blocking I/O in the main loop causes watchdog resets
- Check CAN bus health - bus-off recovery can block the main loop
- Increase `WATCHDOG_TIMEOUT_MS` temporarily for debugging (not for production)

### Encoder readings are wrong

- Verify encoder wiring (A and B channels not swapped)
- Check CPR against motor datasheet (Pololu 37D 50:1 = 64 CPR * 50 = 3200 ticks/rev)
- Run calibration to detect and correct direction issues
- Inspect encoder disc for debris or damage

---

## Related Documentation

- [VENTUNO Q Setup](ventuno-q-setup.md) - board setup and CAN-FD configuration on the Linux side
- [Architecture](../ARCHITECTURE.md) - system-level overview of the CAN-FD bridge
- [Safety](../../SAFETY.md) - watchdog, E-stop, and defense-in-depth safety layers
