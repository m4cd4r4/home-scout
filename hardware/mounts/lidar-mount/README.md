# LIDAR Mount

> Elevated mount for the RPLIDAR C1 with 360-degree clearance.

## Overview

This mount raises the RPLIDAR C1 sensor 80mm above the chassis top plate on a cylindrical mast. The elevation prevents the chassis body, camera mount, and other top-plate components from blocking the LIDAR's 360-degree scan plane. The RPLIDAR C1 needs an unobstructed view in all directions to produce accurate SLAM maps.

## Why 80mm?

The tallest component on the Scout top plate (excluding the LIDAR itself) is the camera mount at approximately 50mm. The 80mm mast height places the LIDAR scan plane 30mm above the camera mount, giving comfortable clearance even if the tilt bracket is angled upward. This height also keeps the LIDAR beam at a level that detects walls, furniture legs, and doorframes without shooting over low obstacles like pet bowls or shoes.

## Compatibility

| LIDAR | Supported | Notes |
|-------|-----------|-------|
| SLAMTEC RPLIDAR C1 | Yes | Primary supported unit. M3 mounting holes on 4-point pattern. |
| SLAMTEC RPLIDAR A1 | Partial | Different mounting hole pattern. Needs adapter plate. |
| SLAMTEC RPLIDAR A2 | Partial | Larger diameter. Needs wider mast cap. |

This mount is designed for the RPLIDAR C1. If you use a different LIDAR, you will need to modify the mast cap to match its mounting hole pattern.

## Dimensions

| Measurement | Value |
|-------------|-------|
| Mast height | 80mm |
| Mast outer diameter | 25mm |
| Mast inner diameter (cable channel) | 14mm |
| Base flange diameter | 40mm |
| Cap diameter | 50mm (matches RPLIDAR C1 footprint) |
| Total height (base to top of LIDAR) | ~115mm |
| Weight (printed, without LIDAR) | ~25g |

## Parts

| File | Description |
|------|-------------|
| `lidar-mast.step` | Cylindrical mast with internal cable channel and base flange |
| `lidar-mast.stl` | Print-ready STL |
| `lidar-cap.step` | Top cap with M3 mounting holes for RPLIDAR C1 |
| `lidar-cap.stl` | Print-ready STL |

> **Note:** STEP and STL files are coming in a future PR.

## Mounting

### Mast to Chassis

The mast base flange attaches to the center of the chassis top plate.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M3 x 10mm bolt | 3 | Attach mast base flange to top plate |
| M3 nut | 3 | Secure from below |

The top plate has three pre-positioned M3 holes in a triangular pattern at center for the LIDAR mast.

### RPLIDAR C1 to Cap

The RPLIDAR C1 bolts to the mast cap through its four mounting holes.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M3 x 6mm bolt | 4 | Attach RPLIDAR C1 to mast cap |
| M3 nut | 4 | Secure from below cap |

### Cap to Mast

The cap press-fits onto the top of the mast with a 0.2mm interference fit. If the fit is too loose on your printer, use a drop of cyanoacrylate (super glue) on the joint. If it is too tight, sand the mast top lightly.

## Cable Routing

The mast is hollow with a 14mm internal channel. The RPLIDAR C1 USB cable routes down through this channel, keeping it protected and tidy.

1. Feed the USB cable down through the mast before press-fitting the cap.
2. The cable exits at the base flange through a side slot.
3. Route the cable along the underside of the top plate to the nearest USB 3.0 port on the VENTUNO Q board.
4. Secure the cable with a zip tie at the base flange slot to act as a strain relief.

**Cable length:** The RPLIDAR C1 comes with a USB cable that is long enough to reach from the mast top to the VENTUNO Q. No extension needed.

## Print Settings

| Setting | Value |
|---------|-------|
| Material | PLA or PETG |
| Layer height | 0.2mm |
| Infill | 25% |
| Walls | 4 |
| Supports | None (mast is a simple cylinder, cap is flat) |
| Estimated time | ~1.5 hours (both parts) |
| Filament | ~20g |

### Orientation

| Part | Print Orientation |
|------|------------------|
| Mast | Standing upright (base flange on bed) |
| Cap | Flat, top face up |

The mast prints vertically. This means layer lines run perpendicular to any bending forces, which is the strongest orientation for a tall cylindrical part. If you print the mast on its side, it will be much weaker and may snap at a layer line from a bump.

## Assembly

1. Print both parts (mast and cap).
2. Feed the RPLIDAR USB cable down through the mast's internal channel.
3. Press-fit the cap onto the top of the mast. Apply light, even pressure. Do not hammer.
4. Bolt the RPLIDAR C1 to the cap using four M3 x 6mm bolts and nuts.
5. Bolt the mast base flange to the chassis top plate using three M3 x 10mm bolts.
6. Route the USB cable from the base flange slot to the VENTUNO Q USB port.
7. Secure the cable at the base flange with a small zip tie.

## Clearance Check

After assembly, verify 360-degree clearance by slowly rotating the RPLIDAR by hand (with power off). The spinning LIDAR head should not contact any part of the chassis, cables, camera mount, or e-stop button at any angle.

If anything blocks the scan:

- Reposition the obstructing component.
- Trim or re-route cables that cross the scan plane.
- As a last resort, increase mast height by reprinting with a taller mast (edit the STEP file).

## Vibration

The RPLIDAR C1 has a spinning motor that can introduce vibration into the chassis through the mast. If you notice vibration artifacts in SLAM maps:

- Add a small rubber washer (1mm thick) between the cap and the RPLIDAR mounting flange. This dampens vibration transfer.
- Ensure the mast base bolts are tight but not overtightened - overtightening PLA parts can crack them.
