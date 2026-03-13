# Print Settings - V1 Starter Chassis

Recommended 3D print settings for all v1 chassis parts. These settings were tested on an FDM printer with a 220mm x 220mm bed.

## Material

| Property | Recommendation |
|----------|---------------|
| **Primary material** | PLA (easiest to print, strong enough for most parts) |
| **Upgrade material** | PETG (better heat resistance, slight flex, recommended for motor mounts) |
| **Avoid** | ABS (warping, fumes), TPU (too flexible for structural parts) |

PLA works for all parts. If your robot will live in a hot garage or car, use PETG for the base plate and motor mounts - PLA softens above 55-60C.

## General Settings

These settings apply to all chassis parts unless a part-specific override is listed below.

| Setting | Value | Notes |
|---------|-------|-------|
| Layer height | 0.2mm | Good balance of speed and strength |
| First layer height | 0.28mm | Better bed adhesion |
| Line width | 0.4mm (0.4mm nozzle) | Standard |
| Wall count | 4 | ~1.6mm wall thickness |
| Top/bottom layers | 5 | ~1.0mm solid shell |
| Infill | 20% | Grid or gyroid pattern |
| Infill pattern | Gyroid (preferred) or Grid | Gyroid is stronger for similar weight |
| Supports | None | All parts designed to print flat without supports |
| Brim | 5mm brim on base plate and top plate | Large flat parts benefit from brim for adhesion |
| Print speed | 50-60mm/s | Reduce to 40mm/s for first 3 layers |
| Nozzle temp (PLA) | 200-210C | Follow your filament's datasheet |
| Nozzle temp (PETG) | 230-240C | Follow your filament's datasheet |
| Bed temp (PLA) | 60C | |
| Bed temp (PETG) | 80C | |
| Cooling fan | 100% after layer 3 (PLA) | PETG: 50-70% |
| Retraction | 6mm at 25mm/s (Bowden) or 1mm at 25mm/s (direct drive) | Tune for your printer |
| Z-seam | Sharpest corner | Hides the seam in corners |

## Part-Specific Overrides

Some parts take higher stress and need stronger settings.

### Base Plate

The base plate holds the motors and takes all the mechanical load from driving.

| Setting | Override | Why |
|---------|----------|-----|
| Infill | **30%** | Motor mount stress, wheel vibration |
| Material | PETG recommended | Better fatigue resistance under repeated motor torque |

### Motor Mount Areas (Base Plate)

If your slicer supports per-region infill modifiers, boost infill around the four motor mount bosses.

| Setting | Override | Why |
|---------|----------|-----|
| Infill (motor boss region) | **40%** | Motor bolts pull directly on infill |
| Wall count (motor boss region) | **5** | More walls around bolt holes prevent cracking |

### Battery Bay

| Setting | Override | Why |
|---------|----------|-----|
| Infill | **20%** (standard) | No high-stress areas |
| Wall count | **5** | Battery slides in and out - thicker walls resist wear |

### Electronics Tray

| Setting | Override | Why |
|---------|----------|-----|
| Infill | **15%** | Lightweight - only holds boards on standoffs |
| Wall count | **4** (standard) | |

### Top Plate

| Setting | Override | Why |
|---------|----------|-----|
| Infill | **20%** (standard) | Needs to support LIDAR mast weight |
| Brim | **5mm** | Large flat surface - brim prevents corner lifting |

## Estimated Print Times

Times based on 50mm/s print speed, 0.2mm layer height, standard settings above. Your printer and slicer will vary.

| Part | Estimated Time | Filament (PLA, 1.75mm) |
|------|---------------|----------------------|
| Base plate | ~6-8 hours | ~120g |
| Battery bay | ~3-4 hours | ~60g |
| Electronics tray | ~4-5 hours | ~80g |
| Top plate | ~5-7 hours | ~100g |
| **Total (all 4 parts)** | **~18-24 hours** | **~360g** |

At typical PLA filament prices ($20-25/kg), the full chassis costs roughly **$7-9 in filament**.

## Orientation

All parts print in their natural flat orientation. No rotation needed.

| Part | Print Orientation | Supports Needed |
|------|------------------|-----------------|
| Base plate | Bottom face down | No |
| Battery bay | Open side up | No |
| Electronics tray | Board-mounting face up | No |
| Top plate | Top face up | No |

## Heat-Set Inserts

The electronics tray has bosses designed for M2.5 and M3 heat-set inserts. Install these after printing, before assembly.

| Insert Size | Quantity | Location |
|-------------|----------|----------|
| M2.5 x 4mm | 4 | VENTUNO Q board mounting holes |
| M3 x 5mm | 4 | Motor driver standoffs (2 per driver) |
| M3 x 5mm | 2 | Buck converter standoffs |
| M3 x 5mm | 2 | BMS board standoffs |

**Tip:** Use a soldering iron at 200-220C with a heat-set insert tip. Press the insert in slowly and straight. Do not overheat - you will melt the surrounding plastic and lose thread grip.

## Tolerances

The design uses these tolerances for fitted parts. If parts are too tight or too loose on your printer, adjust your slicer's horizontal expansion setting.

| Fit Type | Designed Clearance | Example |
|----------|-------------------|---------|
| Bolt holes (M3) | 3.2mm diameter | Motor mount holes |
| Bolt holes (M2.5) | 2.7mm diameter | Board standoff holes |
| Press-fit (sensors) | 0.1mm interference | Cliff sensor slots |
| Snap-fit (displays) | 0.2mm clearance | OLED display cutouts |
| Sliding fit (battery) | 0.5mm clearance per side | Battery bay walls |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Motor mount holes too tight | Drill out with 3.2mm bit, or increase horizontal expansion by 0.1mm |
| Battery bay too snug | Sand inner walls lightly, or increase horizontal expansion |
| Top plate warping during print | Use brim, increase bed temp by 5C, ensure enclosure or no drafts |
| Layer splitting at motor mounts | Switch to PETG, increase nozzle temp by 5C, slow print speed to 40mm/s |
| Heat-set inserts pull out | Hole was over-melted - reprint the tray, use lower iron temp |

## No 3D Printer?

Use an online printing service. Upload the STL files and order in PLA or PETG.

| Service | Notes |
|---------|-------|
| [JLCPCB 3D Printing](https://jlcpcb.com) | Cheapest for PLA/PETG. Ships from China, 5-7 day production. |
| [Craftcloud](https://craftcloud3d.com) | Price comparison across many print shops. |
| Your local library or makerspace | Many have free or low-cost 3D printers. Call first. |
