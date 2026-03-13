# V1 Starter Chassis

> 3D-printable 4WD differential-drive chassis for Home Scout Phase 3+.

## Overview

The v1 starter chassis is a PLA/PETG-printable robot platform sized at approximately **250mm x 200mm x 150mm** (L x W x H). It holds the VENTUNO Q board, 4S LiPo battery, RPLIDAR C1, motor drivers, and all Phase 3 sensors. The design prioritizes printability on consumer FDM printers (200mm+ bed) over compactness - every part prints flat without supports.

## Design Goals

- Print on any FDM printer with a 200mm x 200mm bed or larger
- No supports required for most parts
- Snap-fit or M3 bolt assembly - no glue, no tapping
- Accessible battery bay for quick swaps
- Top-access wiring for easy maintenance
- Compatible with both 2WD (minimum viable) and 4WD configurations

## Dimensions

| Measurement | Value |
|-------------|-------|
| Length | ~250mm |
| Width | ~200mm |
| Height (chassis only) | ~100mm |
| Height (with LIDAR mast) | ~150mm |
| Ground clearance | ~20mm |
| Weight (printed, empty) | ~350-400g |
| Wheel diameter | 80mm (Pololu silicone wheels) |
| Wheelbase | ~180mm |
| Track width | ~170mm |

## Layer Diagram

The chassis stacks vertically in four layers. Each layer is a separate print.

```
┌─────────────────────────────────────────────┐
│               TOP PLATE                      │
│   LIDAR mount, camera mount, OLED cutouts   │
│   NeoPixel ring recess, e-stop hole         │
├─────────────────────────────────────────────┤
│              ELECTRONICS TRAY                │
│   VENTUNO Q board, motor drivers,           │
│   buck converter, BMS, wiring channels      │
├─────────────────────────────────────────────┤
│              BATTERY BAY                     │
│   4S LiPo (rear-loading), XT60 connector,   │
│   battery strap slots                        │
├─────────────────────────────────────────────┤
│              BASE PLATE                      │
│   Motor mounts (x4), encoder clearance,     │
│   cliff sensor brackets, bump sensor arms,  │
│   caster mount (2WD config)                 │
└─────────────────────────────────────────────┘
```

## Component Mounting Locations

### Base Plate

| Component | Location | Mounting |
|-----------|----------|----------|
| Pololu 37D motors (x4) | Corners, inline with wheel wells | M3 bolts through motor bracket flats |
| Cliff sensors (x2) | Front edge, angled down 45 degrees | Press-fit into slots |
| Bump sensor arms (x2) | Front-left and front-right | Hinge pin through chassis ears |
| Caster wheel (2WD only) | Rear center | M3 bolts, removable for 4WD upgrade |

### Battery Bay

| Component | Location | Mounting |
|-----------|----------|----------|
| 4S LiPo 5000mAh | Center, rear-loading | Velcro strap through guide slots |
| XT60 connector | Rear panel cutout | Friction-fit + hot glue (optional) |

### Electronics Tray

| Component | Location | Mounting |
|-----------|----------|----------|
| VENTUNO Q board | Center | M2.5 standoffs (x4) into heat-set inserts |
| Cytron MDD10A drivers (x2) | Left and right of VENTUNO Q | M3 standoffs (x2 each) |
| DFRobot buck converter | Rear, next to battery connector | M3 standoffs (x2) |
| BMS board | Above battery bay, underside of tray | M3 bolts (x2) |
| BNO055 IMU | Center of tray, close to center of rotation | M2 standoffs (x2) |

### Top Plate

| Component | Location | Mounting |
|-----------|----------|----------|
| RPLIDAR C1 | Center, on elevated mast | See `hardware/mounts/lidar-mount/` |
| Arducam IMX219/477 | Front edge, tilting mount | See `hardware/mounts/camera-mount/` |
| OLED displays (x2) | Front face, side by side | Press-fit into rectangular cutouts |
| NeoPixel ring | Front, between OLEDs | Recessed pocket, friction-fit |
| E-stop button | Rear-right, easily reachable | 16mm panel-mount hole |
| Speaker (40mm) | Front-facing, behind grille | See `hardware/mounts/speaker-mount/` |

## Assembly Order

1. **Print all parts** - see [print-settings.md](print-settings.md) for recommended settings
2. **Install heat-set inserts** into the electronics tray (M2.5 for VENTUNO Q, M3 for drivers)
3. **Mount motors** to base plate with M3 bolts
4. **Press-fit cliff sensors** into base plate slots
5. **Install bump sensor arms** on hinge pins
6. **Stack battery bay** onto base plate (M3 bolts at four corners)
7. **Wire battery connector** through rear panel
8. **Stack electronics tray** onto battery bay
9. **Mount VENTUNO Q, drivers, and converter** to tray standoffs
10. **Route all wiring** through the tray's cable channels
11. **Stack top plate** onto electronics tray
12. **Attach LIDAR mast, camera mount, speaker mount** to top plate
13. **Press-fit OLEDs and NeoPixel ring** into front cutouts
14. **Install e-stop button** in rear-right panel-mount hole
15. **Attach wheels** to motor shafts

## 2WD vs 4WD Configuration

The base plate supports both configurations.

| Config | Motors | Rear | Tradeoff |
|--------|--------|------|----------|
| 2WD | Front 2 motors only | Rear caster wheel (included mount) | Cheaper, simpler wiring, less traction |
| 4WD | All 4 motors | No caster | Better traction, better odometry, slightly more complex |

To convert from 2WD to 4WD: remove the caster mount (2x M3 bolts), install rear motors, wire to second motor driver.

## Files

| File | Description |
|------|-------------|
| `v1-base-plate.step` | Base plate with motor mounts and sensor slots |
| `v1-base-plate.stl` | Print-ready STL |
| `v1-battery-bay.step` | Battery compartment with rear-loading slot |
| `v1-battery-bay.stl` | Print-ready STL |
| `v1-electronics-tray.step` | Board mounts, cable channels, standoff bosses |
| `v1-electronics-tray.stl` | Print-ready STL |
| `v1-top-plate.step` | LIDAR mast base, camera mount, display cutouts |
| `v1-top-plate.stl` | Print-ready STL |
| `print-settings.md` | Recommended slicer settings |

> **Note:** STEP and STL files are coming in a future PR. This README documents the intended design.

## Design Software

The chassis was designed in FreeCAD 0.21+. The STEP files are the canonical source. STL exports are provided for convenience but should be regenerated from STEP if you modify the design.

## Community Variants

Want to build a different chassis? See [community/SUBMISSION_GUIDE.md](../community/SUBMISSION_GUIDE.md) for how to submit your own design. All community chassis designs must be compatible with the VENTUNO Q board mounting pattern and use the same motor/sensor positions documented above.

## Related Docs

- [print-settings.md](print-settings.md) - Slicer settings for all chassis parts
- [BOM.md](../../../BOM.md) - Full bill of materials
- [SAFETY.md](../../../SAFETY.md) - Build safety guidelines
