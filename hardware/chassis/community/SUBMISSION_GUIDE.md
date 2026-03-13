# Community Chassis Submission Guide

Build your own Scout chassis? Share it with the community.

This guide covers what files you need, how to name them, and what license to use. Follow these steps and your chassis design can be merged into the official repo for other builders to use.

## Why Submit a Chassis?

The v1 starter chassis is a general-purpose design. Your chassis might be better for a specific use case:

- Smaller footprint for apartments
- Waterproof enclosure for outdoor use
- Metal or laser-cut acrylic for durability
- Two-wheel differential for tight spaces
- Mecanum wheels for omnidirectional movement
- Tank treads for rough surfaces

All community designs live in `hardware/chassis/community/` and are linked from the main hardware docs.

## Required Files

Every submission must include these files. Incomplete submissions will be asked to add the missing pieces before review.

| File | Required | Purpose |
|------|----------|---------|
| `your-chassis-name.step` | Yes | Parametric CAD source. This is the editable design. |
| `your-chassis-name.stl` | Yes | Print-ready mesh. Exported from the STEP file. |
| `README.md` | Yes | Description, dimensions, print settings, assembly notes, photos. |
| `photos/assembled.jpg` | Yes | At least one photo of the printed and assembled chassis. |
| `photos/printed-parts.jpg` | Recommended | Photo of raw printed parts before assembly. |
| `print-settings.md` | Recommended | Slicer settings if they differ from the v1 defaults. |
| `LICENSE` | Yes (if different from repo MIT) | Must be MIT or CC-BY-SA 4.0. See [License Requirements](#license-requirements). |

### About STEP Files

STEP (.step or .stp) is the required source format. It is an open ISO standard (ISO 10303) that works across all major CAD tools - FreeCAD, Fusion 360, SolidWorks, Onshape, and others. Do not submit proprietary-only formats (e.g., .f3d, .sldprt) as the sole source.

If you designed in a proprietary tool, export to STEP before submitting. Keep your native file as a bonus, but the STEP file is mandatory.

### About STL Files

Export STL in binary format (not ASCII) to keep file sizes manageable. Use high enough resolution that curved surfaces are smooth - a chord tolerance of 0.05mm or deviation angle of 10 degrees is a good starting point.

## Naming Convention

Use lowercase kebab-case for your chassis directory and files.

```
hardware/chassis/community/
  your-chassis-name/
    your-chassis-name.step
    your-chassis-name.stl
    README.md
    print-settings.md          (recommended)
    photos/
      assembled.jpg
      printed-parts.jpg        (recommended)
      detail-motor-mount.jpg   (optional)
```

### Name Format

```
[descriptor]-[drive-type]-[version]
```

**Examples:**

| Name | Meaning |
|------|---------|
| `compact-2wd-v1` | Compact two-wheel-drive chassis, first version |
| `outdoor-4wd-v2` | Outdoor-rated four-wheel-drive, second revision |
| `mecanum-omni-v1` | Mecanum wheel omnidirectional platform |
| `tank-treads-v1` | Tracked (tank tread) platform |

Avoid generic names like `my-chassis` or `test-v1`. The name should tell someone what makes your design different.

## README Template

Your `README.md` should cover at minimum:

```markdown
# [Your Chassis Name]

> One-sentence description of what makes this design different.

## Dimensions

| Measurement | Value |
|-------------|-------|
| Length | XXXmm |
| Width | XXXmm |
| Height | XXXmm |
| Weight (printed, empty) | XXXg |

## Design Goals

<!-- Why did you build this? What problem does it solve that v1 doesn't? -->

## Compatibility

<!-- Which Scout components does it support? -->
- [ ] VENTUNO Q board
- [ ] 4S LiPo battery
- [ ] Pololu 37D motors (x2 or x4)
- [ ] RPLIDAR C1
- [ ] Arducam CSI camera
- [ ] OLED displays
- [ ] E-stop button

## Print Settings

<!-- Material, infill, layer height, estimated time -->

## Assembly

<!-- Step-by-step with photos -->

## Known Limitations

<!-- Be honest about tradeoffs -->

## Author

<!-- Your name or handle, and a link to your profile -->
```

## License Requirements

Community chassis designs must use one of these two licenses:

| License | SPDX ID | When to Use |
|---------|---------|-------------|
| **MIT** | `MIT` | Maximum freedom. Anyone can use, modify, sell. Matches the Home Scout repo license. |
| **CC-BY-SA 4.0** | `CC-BY-SA-4.0` | Requires attribution and share-alike. Good if you want derivatives to stay open. |

### Why Only These Two?

- **MIT** matches the project's existing license. No friction for integration.
- **CC-BY-SA 4.0** is the standard open hardware license. It ensures derivatives stay open-source while giving you credit.

Designs with NC (non-commercial), ND (no derivatives), or proprietary restrictions will not be accepted. The whole point of community chassis is that anyone can print, modify, and share them.

### How to Specify Your License

Add a `LICENSE` file in your chassis directory if you choose CC-BY-SA 4.0. If you choose MIT, the repo-level MIT license covers your submission automatically - no extra file needed.

## Testing Checklist

Before submitting a PR, verify your design meets these requirements. Include the completed checklist in your PR description.

### Mandatory

- [ ] **Physically printed** - you have printed every part on a real FDM printer
- [ ] **Physically assembled** - the chassis holds together with all parts mounted
- [ ] **VENTUNO Q fits** - the board mounts securely on standoffs with correct hole spacing
- [ ] **Motors mount cleanly** - motor shafts align with wheel wells, bolts seat flush
- [ ] **Battery accessible** - battery can be inserted and removed without disassembling the chassis
- [ ] **E-stop reachable** - the e-stop button is accessible from the outside without moving parts
- [ ] **STEP file opens** - the STEP file opens in FreeCAD 0.21+ without errors
- [ ] **STL is watertight** - the STL has no holes, non-manifold edges, or inverted normals
- [ ] **Photos included** - at least one clear photo of the assembled chassis

### Recommended

- [ ] **Wiring clearance** - cables route without pinching or sharp bends
- [ ] **Ground clearance** - robot clears typical household thresholds (15-20mm)
- [ ] **Cliff sensors unobstructed** - front-facing cliff sensors have a clear view of the floor
- [ ] **LIDAR 360 clearance** - LIDAR has unobstructed 360-degree line of sight
- [ ] **Camera field of view** - camera mount does not clip the chassis in its field of view
- [ ] **Tested driving** - the robot has driven at least 10 minutes without mechanical failure
- [ ] **Documented tolerances** - bolt hole sizes and press-fit clearances are noted

## STL Validation

The repo CI pipeline runs automatic validation on all STL files in `hardware/`. It checks for:

- File size within limits (< 50MB per STL)
- Watertight mesh (no holes)
- No degenerate triangles (zero-area faces)
- No non-manifold edges

If CI fails on your STL, open it in your slicer or [Meshmixer](https://meshmixer.com) and run the repair/analysis tool. Fix any issues before re-pushing.

## Submitting Your PR

1. Fork the repo and create a branch: `git checkout -b hardware/my-chassis-name`
2. Add your files to `hardware/chassis/community/your-chassis-name/`
3. Run the STL validation locally if possible
4. Open a PR with the title: `hardware(chassis): add your-chassis-name community chassis`
5. Fill out the PR template and include the testing checklist above
6. Include at least one photo in the PR description (drag and drop into GitHub)

A maintainer will review your submission for completeness and compatibility. Expect feedback - we want every community chassis to be buildable by someone who has never seen it before.

## Questions?

Open a [Discussion](../../../discussions) with the `hardware` tag, or comment on an existing chassis issue. We are happy to help with CAD, printing, or design questions.
