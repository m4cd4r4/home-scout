# Phase 3: Scout Can Move

After this phase, Scout is a fully autonomous wheeled robot that can navigate your home, avoid obstacles, and patrol rooms on a schedule. This is the most involved build phase.

## What You Need (Phase 3 additions)

| Part | Model | Cost |
|------|-------|------|
| Chassis | 3D printed or 4WD kit | ~$35 |
| Motors | Pololu 37D 50:1 with 64 CPR encoder (x4) | ~$100 |
| Wheels | Pololu 80mm rubber (x4) | ~$32 |
| Motor driver | Cytron MDD10A (x2) | ~$30 |
| LIDAR | SLAMTEC RPLIDAR C1 | ~$100 |
| IMU | BNO055 9-DOF | ~$30 |
| ToF sensors | VL53L1X (x4) | ~$56 |
| Cliff sensors | TCRT5000 (x2) | ~$4 |
| Navigation camera | Arducam IMX219 120-deg MIPI-CSI | ~$15 |
| Battery | 4S 14.8V 5000mAh LiPo | ~$40 |
| BMS + charger | 4S BMS + ISDT Q6 Nano | ~$45 |
| Buck converter | DFRobot 16A DC-DC | ~$12 |
| Wiring/connectors | JST-XH, cables, standoffs | ~$70 |

**Phase 3 total: ~$569** (cumulative: ~$995)

## Step 1: Build the Chassis

### Option A: 3D Print

Print the parts from `hardware/chassis/v1-starter/stl/`. See [print-settings.md](../../hardware/chassis/v1-starter/print-settings.md) for settings.

### Option B: Off-the-shelf

Use any 4WD robot chassis kit (~250mm x 200mm). The key requirements are:
- Space for 4x Pololu 37D motors
- Flat top plate for mounting electronics
- Ground clearance for cliff sensors

## Step 2: Motor and Encoder Wiring

Wire each motor + encoder to the Cytron MDD10A drivers. See `hardware/wiring/schematics/` for the full wiring diagram.

| Motor Driver Pin | VENTUNO Q / STM32H5 | Notes |
|------------------|---------------------|-------|
| PWM1 | STM32H5 TIM PWM CH1 | Motor 1 speed |
| DIR1 | STM32H5 GPIO | Motor 1 direction |
| PWM2 | STM32H5 TIM PWM CH2 | Motor 2 speed |
| DIR2 | STM32H5 GPIO | Motor 2 direction |

Repeat for second MDD10A (motors 3 and 4).

## Step 3: Flash STM32H5 Firmware

```bash
cd firmware/stm32-motor-control
pio run --target upload
```

Or use ST-Link if USB DFU is not available. See [STM32 Firmware Reference](../reference/stm32-firmware.md).

## Step 4: Safety Sensors

Wire cliff sensors (TCRT5000) under the front of the chassis, pointing down. Wire the e-stop button to the STM32H5 GPIO interrupt pin.

```
Cliff sensors -> STM32H5 ADC
E-stop button -> STM32H5 EXTI (interrupt)
ToF sensors -> I2C bus (with address jumpers)
```

## Step 5: LIDAR and IMU

Mount the RPLIDAR C1 elevated 80mm above the chassis using the LIDAR mount. Connect via USB. Connect the BNO055 IMU via I2C.

## Step 6: Power System

!!! warning
    LiPo batteries require careful handling. Read SAFETY.md before proceeding. Always use the BMS, never charge unattended, store in a LiPo bag.

1. Install 4S BMS between battery and power distribution
2. Wire buck converter: 14.8V input -> 5V output for VENTUNO Q and peripherals
3. Install inline 15A fuse between battery and distribution board
4. Wire charging relay (hardware disconnect during operation)

## Step 7: Initial Room Mapping

```bash
# Start in mapping mode
ros2 launch scout_bringup scout_full.launch.py slam_mode:=mapping

# Drive Scout around manually (or use keyboard teleop)
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# Save the map when done
ros2 service call /scout/slam/save_map std_srvs/srv/Trigger
```

## Step 8: Define Patrol Routes

Edit `config/patrol-routes/` to define rooms and waypoints. See the example config for format.

## Step 9: Launch Full System

```bash
ros2 launch scout_bringup scout_full.launch.py
```

## Test It

- "Hey Scout, patrol the house"
- "Hey Scout, go to the kitchen"
- Place an obstacle in Scout's path - should navigate around it
- Test cliff detection at a stair edge (hold Scout, don't let it fall!)
- Press the e-stop button - motors should stop instantly

## What's Next

[Phase 4: Scout Remembers](phase-4-memory.md) - add object memory so Scout remembers where things are.
