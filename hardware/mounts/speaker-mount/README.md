# Speaker Mount

> Enclosed baffle mount for a 40mm speaker driven by the MAX98357A I2S amplifier.

## Overview

This mount holds a 40mm 4-ohm 3W speaker in a front-facing enclosed baffle with ventilation holes. The baffle improves bass response compared to an open-back mount by preventing sound wave cancellation between the front and rear of the speaker cone. Scout sounds clearer and louder with a baffle than with a bare speaker glued to the chassis.

The mount also holds the MAX98357A amplifier breakout board directly behind the speaker, keeping the wiring short and tidy.

## Compatibility

| Speaker | Supported | Notes |
|---------|-----------|-------|
| Generic 40mm 4-ohm 3W speaker | Yes | Primary supported speaker. Widely available. |
| Adafruit 40mm 4-ohm 3W (PID 3968) | Yes | Same dimensions. |
| 40mm 8-ohm 2W speaker | Yes | Fits the same baffle. Lower volume but works. |
| 28mm speakers | No | Too small for this mount. Needs a redesigned baffle. |
| 50mm speakers | No | Too large. Needs a wider baffle. |

Any round 40mm speaker with standard mounting tabs or a friction-fit edge will work.

## Dimensions

| Measurement | Value |
|-------------|-------|
| Mount width | 50mm |
| Mount height | 45mm |
| Mount depth | 25mm |
| Speaker opening | 38mm diameter (front grille) |
| Baffle internal volume | ~15 cm3 |
| Weight | ~12g (PLA) |

## Parts

| File | Description |
|------|-------------|
| `speaker-baffle.step` | Enclosed baffle with front grille, rear vent holes, and amp bracket |
| `speaker-baffle.stl` | Print-ready STL |
| `speaker-grille.step` | Snap-on front grille (optional - the baffle has a built-in grille) |
| `speaker-grille.stl` | Print-ready STL |

> **Note:** STEP and STL files are coming in a future PR.

## Design Details

### Front Grille

The front face has a circular array of 2mm ventilation holes that let sound pass through while protecting the speaker cone from fingers and debris. The hole pattern is cosmetic - you can modify it to match your preferred style.

### Rear Ventilation

Three 3mm holes on the rear wall of the baffle provide a controlled bass port. These holes are tuned for the 40mm speaker's resonant frequency range. Blocking them (e.g., with tape) turns the baffle into a fully sealed enclosure, which reduces bass but tightens mid-range response. Experiment to find what sounds best in your home.

### Amplifier Bracket

The MAX98357A breakout board clips into a bracket on the rear of the baffle. The bracket has two alignment posts that match the board's mounting holes (2.54mm pitch). The board press-fits onto the posts - no screws needed for the amplifier.

## Mounting

### To the Chassis

The speaker mount attaches to the inside of the chassis top plate, front-facing. The grille is flush with or slightly recessed below the top plate's front edge.

| Hardware | Quantity | Purpose |
|----------|----------|---------|
| M3 x 8mm bolt | 2 | Attach mount to top plate underside |
| M3 nut | 2 | Secure from above |

### Speaker to Baffle

The 40mm speaker friction-fits into the baffle's circular pocket. The pocket has a 0.2mm interference fit. If the speaker is loose, use a thin ring of hot glue around the edge. If too tight, sand the pocket walls lightly.

No screws needed for the speaker - friction and the front grille hold it in place.

### MAX98357A to Bracket

Press the breakout board onto the two alignment posts on the rear bracket. The board should click into place. If the fit is too loose, add a small dab of hot glue.

## Print Settings

| Setting | Value |
|---------|-------|
| Material | PLA |
| Layer height | 0.2mm |
| Infill | 30% |
| Walls | 3 |
| Supports | None |
| Estimated time | ~40 minutes |
| Filament | ~8g |

PETG is not necessary for this mount - it carries no mechanical load. PLA is fine.

### Orientation

Print the baffle with the front grille face-down on the bed. This puts the smoothest surface finish on the visible front face and ensures the grille holes print cleanly without stringing.

## Assembly

1. Print the speaker baffle.
2. Press the 40mm speaker into the front pocket of the baffle. The cone should face outward (toward the grille holes). Verify the speaker is seated flat.
3. Press the MAX98357A breakout board onto the rear bracket posts.
4. Solder or connect wires:
   - MAX98357A VIN to 5V power rail
   - MAX98357A GND to ground
   - MAX98357A BCLK to I2S_BCLK (see `hardware/wiring/pinout/ventuno-q-pinout.md`)
   - MAX98357A LRC to I2S_WS
   - MAX98357A DIN to I2S_DOUT
   - MAX98357A speaker + to speaker positive terminal
   - MAX98357A speaker - to speaker negative terminal
5. Bolt the assembled mount to the underside of the chassis top plate using two M3 x 8mm bolts.
6. Route wires through the top plate's cable channel to the VENTUNO Q board.

## Wiring Reference

| MAX98357A Pin | Connects To | Notes |
|---------------|-------------|-------|
| VIN | 5V rail | From buck converter 5V output |
| GND | Common ground | |
| BCLK | I2S_BCLK (JMISC header) | Bit clock, shared with microphones |
| LRC | I2S_WS (JMISC header) | Word select / left-right clock, shared with microphones |
| DIN | I2S_DOUT (JMISC header) | Audio data from Orin NX to amplifier |
| Speaker + | Speaker positive terminal | Short wire, keep under 50mm |
| Speaker - | Speaker negative terminal | Short wire, keep under 50mm |

**Gain selection:** The MAX98357A gain is set by the GAIN pin.

| GAIN Pin | Gain |
|----------|------|
| Unconnected (floating) | 9 dB (default) |
| Connected to GND | 12 dB |
| Connected to VIN | 15 dB |

Start with the default (GAIN pin unconnected). If Scout is too quiet in your home, bridge GAIN to GND for a 3 dB boost. Going to 15 dB can introduce distortion on a small speaker - test before committing.

## Sound Quality Tips

- **Face the speaker outward.** Sound aimed at a wall or into the chassis body gets muffled.
- **Seal the baffle edges.** If there are gaps between the speaker and the baffle pocket, sound leaks around the cone and reduces clarity. Hot glue seals the gaps.
- **Keep speaker wires short.** Long wires between the amp and speaker can pick up noise from motor PWM signals. Under 50mm is ideal.
- **Separate audio and motor wiring.** Do not bundle I2S signal wires with motor PWM cables. Cross them at 90 degrees if they must intersect.
