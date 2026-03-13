# Contributing Hardware Designs

Scout is a physical robot. Hardware contributions - chassis parts, mounts, brackets, enclosures, cable management, alternative assemblies - directly improve the build experience for everyone. This guide covers what we need, what formats to use, and how to submit your work.

---

## What We Need

### High priority

- **Alternative chassis designs** - different wheel configurations, smaller footprints, easier-to-print versions
- **Camera mounts** - adjustable pan/tilt for the onboard MIPI-CSI camera, wall mounts for ESP32-CAMs
- **LIDAR mounts** - vibration-isolated mounting for the RPLIDAR C1
- **Battery compartments** - secure enclosures with ventilation and easy access
- **Cable management** - wire routing channels, strain relief brackets, connector panels
- **Speaker enclosures** - acoustic chambers that improve audio quality from the small 40mm driver

### Medium priority

- **Sensor brackets** - ToF sensor mounts, cliff sensor mounts, bump sensor lever arms
- **OLED display bezels** - frames for the eye displays that integrate with the chassis
- **NeoPixel ring mounts** - diffuser rings that spread light evenly
- **E-stop button mounts** - mushroom button panel with wiring pass-through
- **Charging dock** - alignment cradle with pogo pin contacts

### Community chassis submissions

We welcome full alternative chassis designs. If you have designed a chassis that works with Scout's electronics, we want to see it. Community chassis designs are credited and listed in the BOM as alternatives.

---

## Required Files

Every hardware submission must include these files:

### 1. STEP file (.step) - Required

The parametric CAD source file. This lets other contributors modify your design in FreeCAD, Fusion 360, SolidWorks, or OnShape. STL files alone are not sufficient because they cannot be edited parametrically.

```
hardware/chassis/your-part-name/your-part-name.step
```

**STEP export settings:**
- AP214 or AP203 format (AP214 preferred)
- Include all bodies if the design has multiple components
- Use millimeters as the unit

### 2. STL file (.stl) - Required

The print-ready mesh. One STL per printable part. If your design has multiple parts, provide one STL for each.

```
hardware/chassis/your-part-name/your-part-name.stl
hardware/chassis/your-part-name/your-part-name-lid.stl
```

**STL export settings:**
- Binary format (smaller file size)
- Deviation/tolerance: 0.01mm or finer
- Verify the STL is watertight (no holes, no inverted normals)

### 3. Photos - Required

Photos of the actual printed and assembled part. Not renders - real photos. We need to see that the part works in practice.

```
hardware/chassis/your-part-name/photos/
  printed.jpg            # The part as it comes off the printer
  assembled.jpg          # The part installed on Scout
  detail.jpg             # Close-up of any critical fit areas
  with-electronics.jpg   # Part with electronics installed (if applicable)
```

**Photo requirements:**
- Minimum 1024x768 resolution
- Good lighting (no flash shadows that hide detail)
- Include a ruler or known-size reference object in at least one photo
- Show the part from multiple angles if geometry is complex
- JPEG format, reasonable compression (under 2MB per photo)

### 4. Print settings document - Required

A README.md in the part directory with print settings and assembly notes.

```markdown
# Your Part Name

Brief description of what this part does and where it goes on Scout.

## Print Settings

| Setting | Value |
|---------|-------|
| Material | PLA (PETG recommended for battery compartment) |
| Layer height | 0.2mm |
| Infill | 20% grid |
| Walls | 3 perimeters |
| Supports | Yes - tree supports, touching buildplate only |
| Brim | 5mm brim recommended for bed adhesion |
| Print time | ~3h 15m (Bambu Lab X1C at default speed) |
| Filament used | ~45g |

## Critical Dimensions

| Dimension | Nominal | Tolerance |
|-----------|---------|-----------|
| Motor shaft hole | 6.0mm | +0.1mm / -0.0mm |
| M3 bolt hole | 3.2mm | +0.1mm / -0.0mm |
| Camera ribbon slot | 16.0mm x 1.0mm | +0.2mm / -0.0mm |

## Assembly Notes

- Insert M3 heat-set inserts before assembly (solder iron at 220C, press straight down)
- The camera ribbon cable routes through the slot on the left side
- Tighten motor mounting bolts to finger-tight plus 1/4 turn - do not overtorque

## Known Issues

- Bridge over the cable channel sags slightly at 0.2mm layer height.
  Use 0.16mm for that section or add a support blocker.
- The snap-fit latch on the battery door weakens after ~50 open/close cycles.
  Consider adding a small magnet for long-term use.

## Photos

![Printed part](photos/printed.jpg)
![Assembled on Scout](photos/assembled.jpg)
```

---

## File Organization

Place your files in the appropriate `hardware/` subdirectory:

```
hardware/
  chassis/
    your-chassis-name/
      your-chassis-name.step
      your-chassis-name.stl
      README.md
      photos/
        printed.jpg
        assembled.jpg

  mounts/
    camera-pan-tilt/
      camera-pan-tilt-base.step
      camera-pan-tilt-base.stl
      camera-pan-tilt-arm.step
      camera-pan-tilt-arm.stl
      README.md
      photos/

  wiring/
    connector-panel-v2/
      connector-panel-v2.step
      connector-panel-v2.stl
      README.md
      photos/
```

Use `kebab-case` for directory and file names.

---

## Design Guidelines

### Printability

- **No supports preferred.** Design parts to print without supports when possible. Use chamfers instead of overhangs, split parts along natural planes.
- **When supports are needed**, design support-friendly geometry (45-degree maximum overhang, generous bridge distances).
- **3mm minimum wall thickness** for structural parts. 2mm minimum for non-structural.
- **3mm minimum fillet radius** on all external edges that a person might touch. This is a safety requirement - see [SAFETY.md](../../SAFETY.md).
- **Design for common printers.** Maximum build volume assumption: 220x220x250mm (Ender 3 / Prusa MK3 class). If your part exceeds this, split it into pieces that bolt together.

### Compatibility

- All parts must fit the VENTUNO Q board. Reference the board dimensions in `hardware/reference/ventuno-q-dimensions.step`.
- Use standard metric fasteners: M2, M2.5, M3, M4. Do not use imperial fasteners.
- Motor mounts must fit the Pololu 37D motor pattern (see [BOM](../../BOM.md)).
- Sensor mounts must accommodate the specific sensors in the BOM.

### Tolerances

- Hole diameters: add 0.1-0.2mm to nominal for press-fit or bolt clearance
- Shaft fits: test on your printer first. FDM printers vary by 0.1-0.3mm depending on calibration
- Note your printer and slicer in the README so others can adjust

### Material recommendations

| Application | Recommended Material | Why |
|-------------|---------------------|-----|
| Structural chassis | PETG | Stronger than PLA, heat-resistant, moderate flexibility |
| Decorative / low-stress | PLA | Easy to print, wide color selection |
| Battery compartment | PETG or ABS | Higher heat resistance near electronics |
| Wheel guards | TPU (flexible) | Absorbs bumps, protects wheels |
| Snap-fit latches | PETG | Better layer adhesion than PLA for living hinges |

---

## Submission Process

### Before you submit

1. **Print the part yourself.** We do not accept untested designs. The part must be physically printed, assembled, and verified to fit.
2. **Test the fit.** Mount it on Scout (or on the specific component it attaches to). Verify all bolt holes align, cables route correctly, and nothing interferes with motion.
3. **Take photos.** Real photos, not renders.
4. **Write the README.** Include print settings, critical dimensions, assembly notes, and known issues.

### Opening the PR

1. Fork the Home Scout repository
2. Create a branch: `git checkout -b hardware/your-part-description`
3. Add your files to the appropriate `hardware/` subdirectory
4. Commit with a conventional commit message: `hardware(mounts): add adjustable camera pan-tilt mount`
5. Open a PR against `main`

### PR checklist for hardware

- [ ] STEP file included (parametric source)
- [ ] STL file included (print-ready mesh, watertight)
- [ ] Photos of printed and assembled part (not renders)
- [ ] README with print settings, dimensions, and assembly notes
- [ ] Part physically tested on Scout or target component
- [ ] Uses standard metric fasteners (M2/M2.5/M3/M4)
- [ ] External edges have 3mm+ fillet radius (safety requirement)
- [ ] Fits within 220x220x250mm print volume (or is split into smaller pieces)
- [ ] Does not interfere with existing parts when assembled

### Review process

1. A maintainer reviews the design files and photos
2. If possible, a second person prints and tests the part independently
3. Feedback is given in the PR comments
4. Once approved and merged, the part is listed in the documentation

---

## Tools

### Free CAD software

| Tool | Platform | Notes |
|------|----------|-------|
| [FreeCAD](https://www.freecadweb.org/) | Windows, macOS, Linux | Fully open source, STEP import/export |
| [OnShape](https://www.onshape.com/en/education) | Browser | Free for personal use, cloud-based |
| [Fusion 360](https://www.autodesk.com/products/fusion-360/personal) | Windows, macOS | Free personal license, STEP export |
| [OpenSCAD](https://openscad.org/) | Windows, macOS, Linux | Programmatic CAD - good for parametric parts |

### STL validation

```bash
# Check STL for errors (requires admesh)
sudo apt install -y admesh
admesh --check your-part.stl

# Or use PrusaSlicer - it highlights non-manifold edges and holes
```

### STEP validation

Open your STEP file in a different CAD tool than the one you created it in. If it opens correctly with all features intact, the export is good.

---

## Community Credits

All accepted hardware contributions are credited in the part's README and in the project [CHANGELOG](../../CHANGELOG.md). If your chassis becomes popular, we will feature it in the main build guide.

---

## Questions?

If you are unsure whether a design fits the project, open a [Discussion](../../discussions) with a sketch or screenshot. We are happy to give feedback before you invest time in a full design and print.

---

## Related Documentation

- [BOM](../../BOM.md) - parts list with dimensions
- [SAFETY.md](../../SAFETY.md) - safety requirements for physical design
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - general contribution guidelines
- [Software Contributions](software-contributions.md) - contributing code instead of hardware
