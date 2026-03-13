# Safety Documentation

Scout is a robot that moves around your home. It has motors, a lithium battery, and it operates near children and pets. Safety is not optional.

## Safety Philosophy

Every safety system operates independently. If the Linux side crashes, the STM32H5 watchdog stops the motors. If the STM32H5 crashes, the hardware watchdog resets it to safe mode. If both crash, the E-stop button physically disconnects motor power via relay.

No single point of failure can cause unsafe behavior. This is defense in depth applied to physical safety.

## Physical Safety

### Speed Limits

Scout's maximum speed is **0.3 m/s** (about 1 km/h - a slow walking pace). This limit is enforced by the STM32H5 safety controller, which monitors encoder feedback independently of the Linux side.

| Layer | Enforcer | Speed Limit |
|-------|----------|-------------|
| ROS2 Nav2 | Qualcomm Linux | Configurable per-room (default 0.3 m/s) |
| STM32H5 firmware | STM32H5 co-processor | Hard cap at 0.3 m/s regardless of commands |
| Motor driver current limit | Hardware | Physical limit based on motor specs |

The STM32H5 reads wheel encoders directly. If encoder feedback indicates speed exceeding 0.3 m/s, the STM32H5 cuts motor power immediately - even if the Qualcomm side is commanding higher speed. The Linux side cannot override this limit.

### Obstacle Avoidance (4 Layers)

Scout uses four independent sensing layers for obstacle avoidance. Each layer can stop the robot on its own.

| Layer | Sensor | Range | Response |
|-------|--------|-------|----------|
| 1. Planning | RPLIDAR C1 (2D LIDAR) | 2-12 m | Path planning avoids obstacles before reaching them |
| 2. Close range | VL53L5CX ToF array | 30 mm - 4 m | Slow down and reroute when objects detected within 1 m |
| 3. Cliff detection | IR cliff sensors (x4) | Edge detection | Immediate stop at stairs, ledges, or drop-offs |
| 4. Contact | Bump sensors (x4) | Physical contact | Immediate stop and reverse 10 cm |

Layers 3 and 4 are processed entirely on the STM32H5. They do not depend on the Linux side being functional.

### Mechanical Safety

- **Rounded edges**: All 3D-printed parts have 3 mm minimum fillet radius on external edges
- **Enclosed wheels**: Guards prevent fingers from reaching the wheel-chassis gap. Gap width is less than 5 mm at all points
- **No exposed screws**: All fasteners at child-accessible height are recessed or covered
- **No sharp edges**: Sheet metal edges (if any) are folded or covered with edge trim
- **Weight**: Target total weight under 3 kg. Light enough that tipping onto a child causes no injury

### Stability

- Low center of gravity: battery and heaviest components mounted at base level
- Wide wheelbase relative to height
- Anti-tip casters at front and rear

## Electrical Safety

### Battery System

Scout uses a 4S1P LiPo battery (14.8V nominal). Lithium polymer batteries require respect.

| Protection | Implementation |
|------------|----------------|
| Over-discharge | BMS cuts power at 3.0V per cell |
| Over-charge | BMS limits charge to 4.2V per cell |
| Over-current | BMS limit: 15A continuous, 30A peak (5s) |
| Short circuit | BMS electronic disconnect + inline 15A fuse |
| Physical containment | LiPo safety bag inside ventilated battery compartment |
| Thermal | BMS with temperature monitoring (if supported by chosen BMS) |
| Charge safety | Hardware relay disconnects battery from load during charging |

### Fusing

An inline 15A automotive blade fuse sits between the battery and the power distribution board. This is the last line of defense if the BMS fails. It is a physical fuse - no software can bypass it.

### Connectors

All power connections use one of:
- **Soldered joints** with heat-shrink tubing
- **JST-XH locking connectors** (keyed, cannot be inserted backwards)
- **XT60 connectors** for main battery connection (rated 60A)

No bare wire connections. No breadboard jumpers in the final build. No crimp connections without proper tooling.

### Voltage Levels

| Rail | Voltage | Purpose |
|------|---------|---------|
| Battery | 14.8V nominal (12.0-16.8V) | Motors via motor drivers |
| 5V regulated | 5V | Raspberry Pi, servos, USB devices |
| 3.3V regulated | 3.3V | STM32H5, sensors, logic |

All logic operates at 3.3V or 5V. The only high-voltage path (14.8V) runs from battery to motor drivers. It is fused and BMS-protected.

### Charging Rules

- **Never charge while Scout is operating.** A hardware relay physically disconnects the battery from the load circuit during charging.
- Use only the charger specified in the BOM (balanced LiPo charger, 1C rate max).
- Never charge unattended. This is standard LiPo safety.
- Charge on a fire-resistant surface.
- If the battery is warm to the touch, stop charging and inspect.

## Software Safety

### STM32H5 Hardware Watchdog

The STM32H5 safety controller runs an independent hardware watchdog timer with a 100 ms timeout. If the STM32H5 firmware fails to pet the watchdog within 100 ms, the hardware automatically resets the microcontroller.

On reset, the STM32H5 boots into **safe mode**:
1. All motor outputs set to zero
2. Motor driver enable pins pulled LOW
3. Status LED flashes red
4. Buzzer sounds three short beeps
5. Waits for heartbeat from Qualcomm side before resuming normal operation

### Heartbeat Protocol

The Qualcomm Linux side sends a heartbeat message to the STM32H5 every 50 ms over the UART link.

| Condition | STM32H5 Response |
|-----------|-----------------|
| Heartbeat received within 50 ms | Normal operation |
| 1-5 missed heartbeats (50-250 ms) | Log warning, continue |
| 6-9 missed heartbeats (300-450 ms) | Reduce speed to 50% |
| 10 missed heartbeats (500 ms) | Enter safe mode: stop motors, flash red LED, announce "Scout needs help" via speaker |

The STM32H5 makes this decision independently. It does not ask the Qualcomm side for permission. If the Linux side is hung, crashed, or unresponsive, Scout stops.

### Emergency Stop (E-Stop)

A red mushroom-head button on Scout's top panel.

**Press once:**
1. GPIO interrupt fires on STM32H5 (highest priority ISR)
2. All motor PWM outputs set to zero within 1 ms
3. Motor driver enable relay opens (physical disconnect)
4. Status LED solid red
5. Speaker announces "Emergency stop activated"
6. Scout will not move until E-stop is released and confirmed

**Long-press (3 seconds) to resume:**
1. STM32H5 verifies E-stop button is released
2. Status LED changes to amber
3. Speaker announces "Resuming in 3... 2... 1..."
4. Normal operation resumes

**Hardware guarantee:** The E-stop relay is wired independently of the microcontroller. Even if the STM32H5 is completely frozen, pressing E-stop opens the relay and disconnects motor power. This is a physical circuit, not a software handler.

### Geofencing

Configure keep-out zones in the Nav2 costmap. Scout will not enter these areas.

```yaml
# config/geofence.yaml
keep_out_zones:
  - name: "baby_room_night"
    polygon: [[2.1, 3.0], [2.1, 5.5], [4.8, 5.5], [4.8, 3.0]]
    schedule:
      start: "19:00"
      end: "07:00"
    action: "avoid"  # Scout routes around this zone

  - name: "stairs"
    polygon: [[0.0, 0.0], [0.0, 1.2], [0.8, 1.2], [0.8, 0.0]]
    schedule: "always"
    action: "forbidden"  # Never enter, even if commanded
```

### Speed Zones

Configure per-room speed limits:

```yaml
# config/speed_zones.yaml
speed_zones:
  - name: "nursery"
    polygon: [[2.1, 3.0], [2.1, 5.5], [4.8, 5.5], [4.8, 3.0]]
    max_speed: 0.15  # Half speed near baby

  - name: "hallway"
    polygon: [[0.0, 5.5], [0.0, 6.5], [8.0, 6.5], [8.0, 5.5]]
    max_speed: 0.3  # Full speed in hallway

  - name: "kitchen"
    polygon: [[4.8, 0.0], [4.8, 5.5], [8.0, 5.5], [8.0, 0.0]]
    max_speed: 0.2  # Reduced speed near cooking area
```

Speed zone limits are enforced by Nav2 on the Linux side. The STM32H5 hard cap of 0.3 m/s still applies as the absolute maximum regardless of configuration.

## Battery Safety

### LiPo Handling Rules

1. **Inspect before every charge.** Look for swelling, dents, punctures, or unusual warmth.
2. **Never charge above 1C rate.** For a 5000 mAh pack, max charge current is 5A.
3. **Never discharge below 3.0V per cell.** The BMS enforces this, but monitor it yourself too.
4. **Store at 3.8V per cell** if Scout will be unused for more than a week. Most LiPo chargers have a "storage" mode.
5. **Never charge unattended.** Stay in the room. Have a fire extinguisher (Class D or sand) accessible.
6. **Charge on fire-resistant surface.** LiPo bag, ceramic tile, or concrete. Never on carpet or wood.
7. **Never puncture, crush, or short-circuit the battery.**
8. **Keep away from water and extreme heat.**

### Battery Disposal

LiPo batteries are hazardous waste. Do not throw them in household trash.

1. Discharge to below 1V per cell (use a LiPo discharger or a 12V incandescent bulb as a load)
2. Take to a battery recycling center or electronics waste facility
3. Check local regulations - many hardware stores accept LiPo batteries

### If the Battery Swells

1. **Stop using Scout immediately.**
2. Do not charge the battery.
3. If safe to do so, remove the battery from Scout (wear gloves, work in a ventilated area).
4. Place the battery in a LiPo safety bag or metal container on a non-flammable surface outdoors.
5. Contact your local hazardous waste facility for disposal.
6. Do not puncture or crush the swollen battery.

## Child Safety by Age

Scout is a family project. Kids should be involved - at age-appropriate levels.

### Under 6 Years Old

- **Interaction**: Supervised only. An adult must be present during all Scout interactions.
- **Build participation**: None. Small parts, soldering, and batteries are hazards.
- **What they can do**: Talk to Scout, ask it to find things, watch it patrol. With an adult present.

### Ages 6-10

- **Interaction**: Can interact with Scout independently after initial supervised sessions.
- **Build participation**: Phase 1 only (voice assistant, no hardware). No soldering. No battery handling.
- **What they can do**:
  - Help design Scout's personality (choose wake word, voice style)
  - Label training data for object detection ("That's a teddy bear!")
  - Draw Scout's face for the display
  - Learn basic coding concepts through Scout's behavior scripts

### Ages 10-14

- **Interaction**: Independent.
- **Build participation**: Hardware assembly with adult supervision.
- **What they can do**:
  - Help with 3D printing (supervised for hot end and moving parts)
  - Wire connections using JST connectors (no soldering without direct supervision)
  - Configure software (edit YAML files, run CLI commands)
  - Learn ROS2 basics through Scout's node structure
- **Restrictions**: No soldering without direct adult supervision. No battery handling.

### Ages 14+

- **Interaction**: Independent.
- **Build participation**: All phases with basic safety training.
- **What they can do**:
  - Solder (after demonstrating safe technique to an adult)
  - Handle batteries (after reading and understanding the battery safety section above)
  - Flash firmware
  - Modify source code and test changes
  - Full mechanical assembly
- **Restrictions**: Battery charging still requires adult awareness (someone else home).

### Phase 6 - Drone Module

The optional drone module (future roadmap) has additional restrictions:

- **Age**: 16+ with adult supervision at all times during flight
- **Prop guards**: Mandatory. No exceptions.
- **Indoor only**: Never fly the drone module outdoors without checking local aviation regulations
- **Battery**: Drone LiPo handled only by adults or trained 16+ users

## Safety Verification Checklist

### Before First Power-On

- [ ] All solder joints inspected (no cold joints, no bridges, no loose connections)
- [ ] Battery polarity verified with multimeter before connecting
- [ ] Fuse installed (15A automotive blade fuse)
- [ ] Battery secured in LiPo bag inside battery compartment
- [ ] All connectors seated and locked (JST-XH click, XT60 fully inserted)
- [ ] No loose wires or components
- [ ] E-stop button installed and relay wired
- [ ] Wheel guards installed and secure
- [ ] 3D-printed parts inspected for sharp edges or layer separation

### Before First Drive

- [ ] E-stop test: press E-stop, verify motors have no power (try to turn wheels by hand - they should spin freely)
- [ ] E-stop release test: long-press 3 seconds, verify Scout announces countdown, verify motors engage
- [ ] Speed limit test: command Scout to drive forward, verify speed does not exceed 0.3 m/s (use a stopwatch and a measured distance)
- [ ] Bump sensor test: place hand in front of Scout while driving, verify it stops on contact
- [ ] Cliff sensor test: drive Scout toward a table edge, verify it stops before the edge
- [ ] LIDAR test: place obstacles at various distances, verify Scout routes around them
- [ ] ToF test: place hand 30 cm in front of Scout, verify it slows and stops
- [ ] Heartbeat test: SSH into Scout and kill the ROS2 navigation stack. Verify STM32H5 enters safe mode within 500 ms.
- [ ] Watchdog test: (advanced) disconnect UART between Qualcomm and STM32H5. Verify STM32H5 enters safe mode.

### Periodic Checks (Monthly)

- [ ] Battery inspection: no swelling, no damage, voltage within normal range
- [ ] Connector inspection: all connections tight, no corrosion
- [ ] Wheel inspection: no excessive wear, guards intact
- [ ] Fuse inspection: not blown, correct rating
- [ ] E-stop test: still functions correctly
- [ ] Bump sensor test: still triggers reliably
- [ ] Cliff sensor test: still triggers reliably
- [ ] Run `scout-cli safety test` for automated software safety verification

## Emergency Procedures

### Battery Swelling or Overheating

1. Press E-stop immediately.
2. If safe, disconnect the battery (XT60 connector).
3. Move Scout to a non-flammable surface (concrete, tile).
4. Do not use water on a lithium battery fire - use sand, Class D extinguisher, or let it burn out in a safe location.
5. Ventilate the room.
6. See "If the Battery Swells" section above for disposal.

### Robot Gets Stuck

1. Press E-stop.
2. Physically move Scout to open space.
3. Release E-stop (long-press 3 seconds).
4. Check for obstacles that confused the sensors.
5. If Scout keeps getting stuck in the same spot, check cliff sensors and ToF sensors for dust or damage.

### E-Stop Does Not Work

This should never happen because the E-stop is a physical relay circuit. If it does:

1. **Disconnect the battery immediately.** Pull the XT60 connector.
2. Do not use Scout until the E-stop circuit is repaired and tested.
3. Inspect the relay, wiring, and E-stop button for damage.
4. File a bug report - this is a critical safety issue.

### Unexpected Movement

If Scout moves when it should not:

1. Press E-stop.
2. If E-stop is not reachable, pick Scout up (it weighs under 3 kg).
3. Disconnect battery.
4. Check: is the heartbeat protocol working? Run `scout-cli safety status` after reconnecting.
5. Check: are motor driver enable pins being held correctly?
6. File a bug report with logs from `scout-cli logs --last 5m`.

### Water Exposure

1. Press E-stop.
2. Disconnect battery immediately.
3. Do not power on Scout until fully dry (48 hours minimum).
4. Inspect all electronics for corrosion before reconnecting.
5. If the battery got wet, do not attempt to charge it. Dispose of it safely.
