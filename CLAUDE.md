# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Clements 47-string concert harp CAD model in FreeCAD. Based on the Erard concert harp stringband geometry from a DXF template.

## Key Files

- `clements47.FCStd` — Main FreeCAD model (FreeCAD 1.1+)
- `erard_harp.FCMacro` — Original macro that generates the stringband sketch, key segments, soundboard B-spline, and limaçon cross-sections from DXF data
- `erard_soundbox.FCMacro` — Soundbox generation macro
- `erard original stringband tutorial.dxf` — Source DXF with string positions and angles
- `clements47_backup.FCStd` — Pre-modification backup

## Model Structure

The FreeCAD model contains:

- **HarpStringband** (Sketcher::SketchObject): 47 vertical strings + 47 key segments (1.5" at 78°) + soundboard B-spline through 7 grommet points. Fully constrained (329 constraints): vertical strings, distance constraints for string lengths, horizontal spacing between strings, pin alignment at Y=0.
- **String_01 through String_47** (Part::Feature): 3D cylinders with Erard gauge diameters from harpcanada.com/harpmaking/erard.htm
- **Limacon_01 through Limacon_47** (Part::Feature): Limaçon cross-section curves, `r = a + b·cos(θ)` with `a = 2b`
- **Soundbox** (Part::Feature): Part::Loft solid through all 47 limaçon wires

## Soundbox Geometry

Limaçon equation: `r = a + b·cos(θ)` where **a = 2b** (convex, flat on one side, round on the other).

- Flat side (θ=π, r=a−b=b) faces UP toward pins/tuners on the soundboard
- Round side (θ=0, r=a+b=3b) hangs BELOW into the resonating chamber
- Diameter = 2(a+b) = 6b. So b = diameter/6, a = diameter/3
- Diameter tapers linearly: 10" at string 1 (bass) → 3" at string 47 (treble)
- Polar origin is **shifted by b** along the normal so the flat side (θ=π) lands exactly on the string bottom
- Each limaçon is perpendicular to the soundboard curve, oriented using normal vectors from the DXF
- Normals are **negated** from the DXF values so the body extends away from the strings (below the soundboard)
- Origin shift: `ox = string_x[i] - b*normals_x[i]`, `oy = -string_lengths[i] - b*normals_y[i]`

## String Data

- String positions, lengths, spacings, and key segment angles: from DXF via `erard_harp.FCMacro`
- String diameters: Erard specs from harpcanada.com (0.025"–0.104" nylon/wrapped/steel)
- Strings start at X=10 (not X=0)
- All string tops align at Y=0 (pin line)

## Build / Regenerate

To regenerate the model from scratch:
```bash
echo 'exec(open("/tmp/clements47_v3.py").read())' | ~/.local/bin/freecad -c
```
The generation script is at `/tmp/clements47_v3.py` (or copy from git history).

To open in FreeCAD 1.1:
```bash
~/.local/bin/freecad ~/projects/clements47/clements47.FCStd
```

## Coordinate System

- X: along the soundboard curve (bass=10 to treble=38)
- Y: string direction (pins at Y=0, soundboard at negative Y)
- Z: width/thickness direction (perpendicular to XY plane)
