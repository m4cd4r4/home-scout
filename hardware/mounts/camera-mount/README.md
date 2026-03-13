# Camera Mount

> Tilt-adjustable mount for Arducam IMX219 or IMX477 MIPI-CSI cameras.

## Overview

This mount attaches the Scout's onboard camera to the chassis top plate. It holds the Arducam camera module at an adjustable tilt angle (0 to 30 degrees downward) so you can aim the field of view for optimal object detection at floor level and table height.

## Compatibility

| Camera | Supported | Notes |
|--------|-----------|-------|
| Arducam IMX219 (standard) | Yes | Budget pick - 8MP, 120-degree FOV wide-angle version recommended |
| Arducam IMX477 (HQ) | Yes | 12.3MP, sharper at range, interchangeable C/CS-mount lenses |
| Raspberry Pi Camera Module v2 | Yes | Same IMX219 sensor, same PCB dimensions |
| Raspberry Pi HQ Camera | Yes | Same IMX477 sensor, same PCB dimensions |

Both camera modules use the same PCB outline and mounting hole pattern. The mount accommodates either without modification.

## Dimensions

| Measurement | Value |
|-------------|-------|
| Mount footprint (base) | 35mm x 30mm |
| Mount height | 25mm (at 0-degree tilt) |
| Camera PCB clearance | 25mm x 24mm (fits both IMX219 and IMX477 PCBs) |
| Tilt range | 0 to 30 degrees downward |
| Weight | ~8g (PLA) |

## Mounting

### To the Chassis

The mount base attaches to the front edge of the chassis top plate using two M3 bolts through the base flange.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M3 x 8mm bolt | 2 | Attach mount base to top plate |
| M3 nut | 2 | Secure from below |

The top plate has two pre-positioned M3 holes at the front edge for this mount.

### Camera to Mount

The camera PCB attaches to the tilt bracket using M2 screws through the camera's corner mounting holes.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M2 x 5mm screw | 4 | Attach camera PCB to tilt bracket |
| M2 nut | 4 | Secure from behind |

### Tilt Adjustment

The tilt bracket pivots on a single M3 bolt through the mount's side walls. Tighten the bolt to lock the desired angle. Loosen to adjust.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M3 x 20mm bolt | 1 | Tilt pivot axle |
| M3 nyloc nut | 1 | Holds tilt angle with friction |

A nyloc nut is recommended over a standard nut - the nylon insert prevents the tilt from drifting from motor vibration.

## Parts

| File | Description |
|------|-------------|
| `camera-mount-base.step` | Base flange that bolts to top plate |
| `camera-mount-base.stl` | Print-ready STL |
| `camera-tilt-bracket.step` | Pivoting bracket that holds the camera PCB |
| `camera-tilt-bracket.stl` | Print-ready STL |

> **Note:** STEP and STL files are coming in a future PR.

## Print Settings

| Setting | Value |
|---------|-------|
| Material | PLA or PETG |
| Layer height | 0.2mm |
| Infill | 30% |
| Walls | 3 |
| Supports | None |
| Estimated time | ~30 minutes (both parts) |
| Filament | ~5g |

Both parts print flat. The tilt bracket prints with the pivot holes oriented vertically - no supports needed.

## Assembly

1. Print both parts (base and tilt bracket).
2. Thread the M3 x 20mm bolt through one side wall of the base, through the tilt bracket, and out the other side wall.
3. Finger-tighten the M3 nyloc nut on the bolt. The bracket should pivot with moderate resistance.
4. Attach the camera PCB to the tilt bracket using four M2 x 5mm screws and nuts.
5. Route the MIPI-CSI ribbon cable down through the slot in the mount base. Avoid sharp bends in the ribbon cable.
6. Bolt the assembled mount to the chassis top plate using two M3 x 8mm bolts.
7. Adjust tilt angle. For general indoor use, 10-15 degrees downward works well.
8. Tighten the pivot nyloc nut to lock the angle.

## Cable Routing

The MIPI-CSI ribbon cable runs from the camera module down through a slot in the mount base, then along the underside of the top plate to the VENTUNO Q's CSI connector. Keep the ribbon cable away from motor wires to avoid electromagnetic interference.

- Do not bend the ribbon cable tighter than a 10mm radius.
- Secure the cable to the underside of the top plate with a small piece of Kapton tape.
- Leave 10-15mm of slack so the tilt bracket can move without pulling the cable.

## Field of View Considerations

| Tilt Angle | Best For |
|------------|----------|
| 0 degrees (level) | Scanning room at eye level, face recognition at distance |
| 10-15 degrees down | General object detection - sees both floor and table height |
| 25-30 degrees down | Close-range floor scanning, finding small objects directly ahead |

The IMX219 wide-angle (120-degree FOV) version is recommended for Scout because it captures a wide scene without needing to pan. The IMX477 has a narrower FOV but better resolution at range - useful if you want Scout to read labels or identify small objects from across the room.
