# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Clements 47-string concert harp CAD model in FreeCAD 1.1. Based on the Erard concert harp stringband geometry from a DXF template. Features a toggle linkage mechanism for pedal/lever-actuated semitone discs.

## Key Files

### FreeCAD Models
- `Clements47.FCStd` — Main model with soundbox + mechanism (448 objects). FreeCAD 1.1+
- `clements47.FCStd` — Older model with stringband sketch (HarpStringband, String_01-47)
- `erard_harp.FCStd` — Stringband sketch source

### Generation Scripts
- `add_mechanism.py` — Adds discs, strings, axles, prongs, neck to Clements47.FCStd from JSON
- `erard_harp.FCMacro` — Generates stringband sketch, key segments, soundboard B-spline from DXF
- `erard_soundbox.FCMacro` — Generates 70 limacon cross-sections and lofted soundbox

### Specifications (machine-readable)
- `clements47.json` — Complete specs for all 47 strings, discs, axles, bearings, neck
- `schema.json` — Field abbreviation decoder for clements47.json
- `clements47_string_analysis.csv` — String frequencies, materials, tensions (1,466 lbs total)

### Design Documents
- `clements47.md` — Full toggle linkage mechanism spec (865 lines): disc geometry, bell cranks, linkage rods, assembly procedures, manufacturing specs
- `base.md` — Pedal base bottom-view with SVG bell crank diagram
- `paraguayan.md` — ASCII side/front/rear views of full harp
- `README.md` — Soundbox geometry, acoustic analysis, string data, material sources

### Visualization Scripts
- `lever_positions.py` — Text-based animation of 3 lever positions
- `lever_animation.py` — Animated pedal cycle visualization

### Source Data
- `erard%20original%20stringband%20tutorial.dxf` — Source DXF with string positions and angles

## Clements47.FCStd Model Structure (448 objects)

### Soundbox (71 objects)
- **Limacon_01 through Limacon_70** (Part::Feature): Limacon cross-section curves, `r = a + b*cos(theta)` with `a = 2b`
- **Soundbox** (Part::Loft): Solid loft through all 70 limacon wires

### Strings (47 objects) — added 2026-04-09
- **Str_C1 through Str_G7** (Part::Feature): Vertical cylinders from soundboard (z=0) to tuning pin (z=n.z). Diameters from Erard specs (0.64mm to 2.31mm)

### Disc Axles (47 objects) — added 2026-04-09
- **Axle_C1 through Axle_G7** (Part::Feature): 44mm horizontal cylinders along Y-axis at pin height. Alternating L(-Y)/R(+Y) sides for clearance. Diameters: 4mm (treble) to 8mm (bass)

### Tuning Discs (94 objects) — added 2026-04-09
- **NatDisc_C1 through NatDisc_G7** (Part::Feature): Natural discs, 2mm thick, at 6mm along axle
- **ShpDisc_C1 through ShpDisc_G7** (Part::Feature): Sharp discs, 2mm thick, at 8mm along axle
- Radii: 4.27mm (F7, smallest) to 25.0mm (C1, largest)

### Prongs (188 objects) — added 2026-04-09
- **NatPrU_*/NatPrD_*** (Part::Feature): Natural disc prongs, upper(+Z) and lower(-Z)
- **ShpPrU_*/ShpPrD_*** (Part::Feature): Sharp disc prongs, upper(+Z) and lower(-Z)
- All M3 (1.5mm radius), 12.7mm extension from disc surface, positioned at 12/6 o'clock

### Neck (1 object) — added 2026-04-09
- **Neck** (Part::Feature): 720x200x250mm hollow box beam, 10mm walls, tilted from bass (z=1429.9) to treble (z=57.2)

## Coordinate System

- X: along the soundboard curve, bass (0mm) to treble (717.4mm)
- Y: harpist (-Y) to audience (+Y), all strings at y=0
- Z: vertical, floor (0mm) to pins at top (z = string length)

Note: clements47.FCStd (the older stringband model) uses a different coordinate system where X is along soundboard (bass=10 to treble=38 inches), Y is string direction (pins at Y=0), and Z is width.

## Soundbox Geometry

Limacon equation: `r = a + b*cos(theta)` where **a = 2b** (convex, flat on one side, round on the other).

- Flat side (theta=pi, r=a-b=b) faces UP toward pins/tuners on the soundboard
- Round side (theta=0, r=a+b=3b) hangs BELOW into the resonating chamber
- Diameter = 2(a+b) = 6b. So b = diameter/6, a = diameter/3
- Base diameter: 14" (bass end), Neck diameter: 4" (treble end), linear taper
- Volume: ~43L (1.2x modern concert harps), Helmholtz resonance: ~85 Hz (E2)

## Mechanism Overview

Toggle linkage over-center mechanism with dual natural/sharp chains. Each of 7 notes (C,D,E,F,G,A,B) has two parallel chains of bell cranks and linkage rods.

- **Three positions**: Flat (discs at 9:15, disengaged) -> Natural (natural discs at 12:30) -> Sharp (both discs at 12:30)
- **Disc rotation**: ~45 degrees CW, rocking (not continuous)
- **Prongs**: 2 per disc, 180 degrees apart, engage string to shorten vibrating length
- **Input**: Hand levers at shoulder (or foot pedals at pillar base)
- **Detent**: Ball detent at input only (3 positions), toggle geometry holds disc positions

## Build / Regenerate

To add mechanism components to Clements47.FCStd:
```bash
echo 'exec(open("add_mechanism.py").read())' | ~/.local/bin/freecad -c
```

To regenerate soundbox from scratch:
```bash
echo 'exec(open("erard_soundbox.FCMacro").read())' | ~/.local/bin/freecad -c
```

To open in FreeCAD 1.1:
```bash
~/.local/bin/freecad ~/projects/clements47/Clements47.FCStd
```

## Current Status (2026-04-09)

### Completed
- Soundbox geometry (70 limacon cross-sections, lofted solid)
- All 47 string cylinders in FreeCAD model
- All 47 disc axles with correct bearing sizes and alternating L/R placement
- All 94 tuning discs (natural + sharp) with correct radii
- All 188 prongs at engagement positions
- Neck box beam structure
- Complete JSON specifications for all components
- Full mechanical design document (clements47.md)
- String analysis with tensions, materials, frequencies
- Acoustic analysis (volume, Helmholtz resonance, tonal character)

### Next Steps (Session 9+)
- Timing diagrams for disc rotation and prong engagement sequences
- Correct prong tangent geometry visualization (prongs tangent to disc edge, not centered)
- Three-position comparison visualization (flat/natural/sharp)
- Force analysis at prong-string contact points
- Kinematic simulation of toggle linkage action
- Bell crank and linkage rod CAD models (not yet in FreeCAD)
- FEA on disc/bell crank stresses
- CadQuery plate() extension for multi-view engineering drawings (see `prompt` file)

### Not Modeled Yet
- Bell cranks (compound bell cranks with ~90 degree arm angles)
- Linkage rods between bell cranks
- Pedal/lever input mechanism
- Pillar structure
- Soundboard (flat panel, separate from soundbox body)
