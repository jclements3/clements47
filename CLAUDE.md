# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Clements 47-string concert harp CAD model in FreeCAD 1.1. Based on the Erard concert harp stringband geometry from a DXF template. Features a toggle linkage mechanism for pedal/lever-actuated semitone discs.

## Key Files

### FreeCAD Models
- `Clements47.FCStd` — Main model with soundbox + mechanism (577 objects). FreeCAD 1.1+
- `clements47.FCStd` — Older model with stringband sketch (HarpStringband, String_01-47)
- `erard_harp.FCStd` — Stringband sketch source

### Generation Scripts
- `add_mechanism.py` — Adds discs, strings, axles, prongs, neck to Clements47.FCStd from JSON
- `add_linkage.py` — Adds bell cranks, linkage rods, action plates to Clements47.FCStd
- `add_missing_parts.py` — Adds bearings, nuts, guide rails, column, tuning pins, pedal rods, rockers
- `add_remaining_parts.py` — Adds coupling links, pedals, soundboard, grommets, stops, springs
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

### Mechanism Reference PDFs
- `erard_grecian_harp.pdf` — Poulopoulos 2023, 319pp, Erard Grecian harp history + mechanism
- `salvi_technical_manual.pdf` — Salvi official tech manual with mechanism chain diagrams
- `camac_technical_manual.pdf` — Camac owner's manual with disc regulation + dead point adjustment

### Source Data
- `erard%20original%20stringband%20tutorial.dxf` — Source DXF with string positions and angles

## Clements47.FCStd Model Structure (1015 objects)

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

### Crank Arms (47 objects) — added 2026-04-12
- **Crank_C1 through Crank_G7** (Part::Feature): Compound bell cranks at each axle end
- Boss (cylinder on axle) + natural arm (+Z, 20mm) + sharp arm (+X, 18mm)
- Pin holes (M3) at arm tips for linkage rod connections
- 5mm thick, 8mm wide arms

### Linkage Rods (80 objects) — added 2026-04-12
- **NatRod_*_*** (Part::Feature): Natural chain rods connecting same-note crank natural arms
- **ShpRod_*_*** (Part::Feature): Sharp chain rods connecting same-note crank sharp arms
- 3mm diameter steel rods, 40 natural + 40 sharp
- Connect bass-to-treble within each of 7 notes (C,D,E,F,G,A,B)

### Action Plates (2 objects) — added 2026-04-12
- **FrontPlate** (Part::Feature): Brass plate at y=+46mm (audience side), 3mm thick
- **BackPlate** (Part::Feature): Brass plate at y=-49mm (harpist side), 3mm thick
- Both span full string extent with 15mm margin, drilled for 47 axle bearings

### Bearings (94 objects) — added 2026-04-13
- **BrgF_C1 through BrgF_G7** (Part::Feature): Front (audience) flanged sleeve bearings
- **BrgB_C1 through BrgB_G7** (Part::Feature): Back (harpist) flanged sleeve bearings
- OD: 8mm (treble/6904) to 12mm (bass/6008), 6mm width, 1.5mm flange

### Spindle Nuts (94 objects) — added 2026-04-13
- **NatNut_C1 through NatNut_G7** (Part::Feature): Natural disc locking collars
- **ShpNut_C1 through ShpNut_G7** (Part::Feature): Sharp disc locking collars
- 8mm OD, 3mm thick, bored for axle clearance

### Guide Rails (4 objects) — added 2026-04-13
- **NatRailU / NatRailL** (Part::Feature): Upper/lower natural chain guide rails
- **ShpRailU / ShpRailL** (Part::Feature): Upper/lower sharp chain guide rails
- 5mm diameter steel, follow pin line from bass to treble

### Column (1 object) — added 2026-04-13
- **Column** (Part::Feature): Hollow structural tube, 60mm OD / 50mm ID
- Position: x=-50mm, from floor (z=0) to neck (z=1430mm)

### Tuning Pins (47 objects) — added 2026-04-13
- **Pin_C1 through Pin_G7** (Part::Feature): 7mm diameter, 40mm exposed length
- At pin height (z = string length) extending upward into neck

### Pedal Rods (7 objects) — added 2026-04-13
- **PedalRod_C through PedalRod_B** (Part::Feature): 4mm diameter steel rods
- Run inside column from base to neck, one per note, arranged in circle (r=15mm)

### Rocker Levers (7 objects) — added 2026-04-13
- **Rocker_C through Rocker_B** (Part::Feature): L-shaped input levers
- At column top, convert vertical pedal rod motion to horizontal linkage motion
- 30mm arms, 8mm wide, 5mm thick, with pivot boss

### Coupling Links (14 objects) — added 2026-04-13
- **NatLink_C through NatLink_B** (Part::Feature): Natural chain coupling links
- **ShpLink_C through ShpLink_B** (Part::Feature): Sharp chain coupling links
- 3mm rods with clevis ends, connect rockers to first bell crank in each chain

### Pedal Assembly (21 objects) — added 2026-04-13
- **Pedal_D, Pedal_C, Pedal_B, Pedal_E, Pedal_F, Pedal_G, Pedal_A** (Part::Feature): Foot plates + lever arms + pivot bosses
- **NotchPlate_*** (Part::Feature): Zigzag detent plates with 3 positions (flat/nat/sharp)
- **PedalSpring_*** (Part::Feature): Return springs (hollow cylinders)
- Standard pedal order L-R: D C B | E F G A, 40mm spacing under column

### Soundboard (1 object) — added 2026-04-13
- **Soundboard** (Part::Feature): 4mm thick flat spruce panel at z=0
- Spans full string extent with 20mm margin, 100mm wide

### String Grommets (47 objects) — added 2026-04-13
- **Grommet_C1 through Grommet_G7** (Part::Feature): Brass eyelets at z=0
- 6mm OD, 2.5mm ID, 3mm thick

### Disc Rotation Stops (94 objects) — added 2026-04-13
- **NatStop_C1 through NatStop_G7** (Part::Feature): Natural disc stops
- **ShpStop_C1 through ShpStop_G7** (Part::Feature): Sharp disc stops
- 4mm steel blocks at ~60 deg from disc edge, limit travel to ~45 deg

### Return Springs (7 objects) — added 2026-04-13
- **ReturnSpring_C through ReturnSpring_B** (Part::Feature): Torsion springs at rocker pivots
- 8mm OD hollow cylinders, 10mm length

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
echo 'exec(open("add_mechanism.py").read())' | ./squashfs-root/usr/bin/freecadcmd
```

To add linkage (cranks, rods, plates):
```bash
echo 'exec(open("add_linkage.py").read())' | ./squashfs-root/usr/bin/freecadcmd
```

To add missing parts (bearings, nuts, rails, column, pins, pedal rods, rockers):
```bash
echo 'exec(open("add_missing_parts.py").read())' | ./squashfs-root/usr/bin/freecadcmd
```

To regenerate soundbox from scratch:
```bash
echo 'exec(open("erard_soundbox.FCMacro").read())' | ./squashfs-root/usr/bin/freecadcmd
```

To open in FreeCAD 1.1:
```bash
~/.local/bin/freecad ~/projects/clements47/Clements47.FCStd
```

## Current Status (2026-04-13)

### Recent work this session: mechanism reference research + design prep

Downloaded and analyzed three key reference PDFs for designing the missing
mechanism components (bell cranks, linkage rods, pedal action):

**Reference PDFs added to repo (DO NOT DELETE)**:
- `erard_grecian_harp.pdf` (51MB) — Poulopoulos 2023, full Erard mechanism history
- `salvi_technical_manual.pdf` (1.3MB) — Salvi official tech manual with mechanism diagrams
- `camac_technical_manual.pdf` (1.2MB) — Camac owner's manual with disc regulation details

**Key findings documented in** `mechanism_references.md`:
- Complete mechanical chain: pedal -> rod -> coupling -> action group -> levers -> spindle -> disc
- Dead point/dead centre = where natural discs stop and sharp discs start turning
- Disc rotation: ~45 deg flat->natural, additional ~35 deg natural->sharp
- Disc attachment: friction cone on spindle, set screw locks
- Sharp discs use LEFT-HAND threads (natural use right-hand)
- Treble discs (F7-F0) have only 1 prong due to space constraints
- Buckwell patent US1332885A maps rocker->link->crank->shaft->disk->fingers
- Links in tension vs compression have different cross-sections
- Salvi total string stress: ~1,200 kg for concert grand

**Soundbox alignment issue from 2026-04-10 is STILL OPEN** (Option A vs B).
User has not chosen yet. See section below for details.

### Previous session (2026-04-10): smoothing the soundboard curve
The soundbox in `Clements47.FCStd` had a visible kink between strings 10 and
11 in the limacon loft.  Spent this session diagnosing and fixing the source.

**Root cause**: The `string_lengths[]` array in `erard_harp.FCMacro:140` was
generated from the raw DXF using `scipy.UnivariateSpline(k=5, s=0.5)` (commit
a5950f4) but the smoothing was too light.  String 11's smoothed length is
48.1801 -- about 1" longer than a smooth interpolation between strings 10
(49.06) and 12 (46.33) would predict.  That 1" anomaly propagates as a kink
into any soundboard curve fit through `(x[i], -string_lengths[i])`.

The raw DXF stringband itself is actually a **straight line** (slope 1.6) --
the curve only appears because every pin is top-aligned to y=0, which
subtracts the noisy DXF neckline from a straight grommet line.

**Constraints locked in by user (do not change)**:
- `string_lengths[47]` -- IMMUTABLE (already in `erard_harp.FCMacro:140`)
- `spacings[46]`       -- IMMUTABLE (already in `erard_harp.FCMacro:135`)
- Pins must NOT be forced to y=0 (the old `DistanceY=0` Sketcher constraint
  is the source of the propagation problem)
- "minimize the jaggedness of the pins without making the soundboard have
  kinks" -- pins can deviate from horizontal slightly so that the soundboard
  can be smooth

**Solution implemented**: `fix_soundbox.py` now builds the soundboard curve
as a `scipy.interpolate.CubicSpline` through 9 anchor points (strings
1, 6, 12, 18, 24, 30, 36, 42, 47) with **clamped endpoint tangents** derived
from least-squares fit of the first/last 5 raw grommets:
  - bass slope:   +1.4675  (+55.73 deg from horizontal)
  - treble slope: +0.7398  (+36.49 deg from horizontal)
The smooth curve has max curvature 0.045 (radius ~22"), max tangent jump
1.5 deg per limacon station, and pin deviation max 0.647" / RMS 0.156"
(at string 11, the residual of the original 1" anomaly).

70 limacon cross-sections are placed at equal arc length along the curve
and lofted into `Soundbox`.  `erard_soundbox.FCMacro` is auto-regenerated by
`fix_soundbox.py` to match.

### CRITICAL OPEN ISSUE -- pick up here on the next session
**The soundbox does not physically align with the strings/discs/axles.**

- Strings/axles/discs/neck (added by `add_mechanism.py`) live in
  **mm coordinates**: X[0..717.4 mm] Y[0] Z[0..1430 mm].
- The soundbox `fix_soundbox.py` builds lives in **inches treated as mm**
  (legacy from the inch-based Erard tutorial): bbox X[4..38] Y[-61..-1]
  Z[-5..5].  Volume reads as 2253 mm^3 because the model is ~25x smaller
  than the strings.
- The two are in completely different regions of 3D space.  They don't
  intersect, don't align, don't share a meaningful coordinate frame.

The user observed this and said "the soundbox has no relationship to the
strings, disks, and axles".  Two options were proposed:

**Option A (simple)**: Rebuild soundbox in mm units.  Centerline along the
X axis from x=0 (bass) to x=717.4 (treble).  Cross-sections perpendicular
to X.  Limacon orientation: bulb at -Z (bottom of resonating chamber),
narrow tip at +Z=0 (top, where strings emerge).  Linear diameter taper
from 14" (355.6 mm) at bass to 4" (101.6 mm) at treble.  This **abandons
the smooth-curve work** because in this representation the soundboard top
is straight along X.  Strings remain as they are.

**Option B (preserves smooth curve)**: Rebuild soundbox with the smooth
curve as its centerline in 3D, in the X-Z plane.  Bass at z ≈ -1500 mm,
treble at z ≈ 0.  Cross-sections perpendicular to local tangent.  Requires
**modifying `add_mechanism.py`** to move each string's grommet to
`z = curve(x_string)` instead of z=0, and pin to `z = curve(x) + L`.
Significant restructuring of the model semantics.

**User has not chosen yet.**  When you pick up: ask which option, then
implement it.  My read was that A is the simpler interpretation matching
their words, but B preserves 3 days of curve-fitting work.  Don't assume.

**The current `Clements47.FCStd` is in the broken state described above**:
the soundbox is the smooth 9-pt cubic clamped curve (fix_soundbox.py output)
but in inch coordinates, NOT aligned with the mm mechanism.

### Files added/changed this session
- `fix_soundbox.py` (new) -- production rebuild script.  Uses scipy
  CubicSpline.  Has a `DRY_RUN` flag at top.  Creates Clements47.FCStd if
  it doesn't exist; otherwise opens and replaces the Soundbox + Limacon_*
  objects in place.  Also rewrites `erard_soundbox.FCMacro`.  **Must be
  rewritten when picking option A or B.**
- `erard_soundbox.FCMacro` (regenerated) -- now reflects the 9-pt curve.
  Will be regenerated again when option A/B is chosen.
- `Clements47.FCStd` (modified) -- has the new soundbox geometry +
  unchanged mechanism.  Soundbox still doesn't align with mechanism.

### Key data the rebuild needs (in fix_soundbox.py constants)
- `STRING_LENGTHS[47]` -- copied from erard_harp.FCMacro line 140
- `SPACINGS[46]`       -- copied from erard_harp.FCMacro line 135
- `ANCHOR_IDX = [0, 5, 11, 17, 23, 29, 35, 41, 46]` (the 9 anchor strings)
- `slope_bass = 1.4675`  (clamped tangent at bass endpoint)
- `slope_treble = 0.7398`  (clamped tangent at treble endpoint)
- limacon convention `b = dia/6, a = 2b` so max_r = 3b = dia/2

### Other context the user mentioned
- "the goal is to minimize the jaggedness of the pins without making the
  soundboard have kinks"
- "the grommets are undefined until after the curve is smooth"
- "the soundbox has no relationship to the strings, disks, and axles"
- Shopping list of immutable inputs above

### CLAUDE.md "Volume: ~43L" caveat
The 43L number assumes the soundbox dimensions are interpreted as inches
(b=2.333 inch, length 65 inch arc => ~43 L).  In actual mm units treated
as mm, the same 14"/4" diameter taper gives ~16-19 L for the pure straight-
along-X centerline.  Whichever option (A or B) is chosen, the volume will
need to be recomputed -- the 43L claim may not survive.

### Session 2026-04-13: Added missing mechanism parts + reference images

**Reference images**: Extracted 1,468 frames from ML Harps assembly video
(`/mnt/c/Users/clementsj/Downloads/images.zip`) into `images/` directory.
Deduped to 187 unique frames using perceptual hashing (`dedup_images.py`).
Shows sequential assembly of full pedal harp mechanism in Fusion 360.

**New parts added via `add_missing_parts.py`** (254 new objects, 577->831):

- 94 bearings (BrgF_*/BrgB_*) — flanged sleeve bearings at each action plate hole
- 94 spindle nuts (NatNut_*/ShpNut_*) — locking collars on axles
- 4 guide rails (NatRailU/L, ShpRailU/L) — curved 5mm steel rods parallel to chains
- 1 column (Column) — 60mm OD hollow tube, x=-50mm, floor to neck
- 47 tuning pins (Pin_*) — 7mm dia, 40mm length at pin height
- 7 pedal rods (PedalRod_C through PedalRod_B) — 4mm inside column
- 7 rocker levers (Rocker_C through Rocker_B) — L-shaped at column top

**FreeCAD executable on this machine**: `./squashfs-root/usr/bin/freecadcmd`
(not `~/.local/bin/freecad` as in older scripts)

### Other Next Steps (still pending from earlier)
- Timing diagrams for disc rotation and prong engagement sequences
- Correct prong tangent geometry visualization (prongs tangent to disc edge, not centered)
- Three-position comparison visualization (flat/natural/sharp)
- Force analysis at prong-string contact points
- Kinematic simulation of toggle linkage action
- FEA on disc/bell crank stresses
- CadQuery plate() extension for multi-view engineering drawings (see `prompt` file)
- **Assembly animation macro** — recreate ML Harps video sequence in FreeCAD
  (progressively show/hide objects, export frames)

### All mechanism parts now modeled (1015 objects)
No remaining unmodeled parts in the mechanical chain from pedal to disc.

### Key Files Added 2026-04-12
- `mechanism_references.md` — Synthesized design reference from all sources
- `erard_grecian_harp.pdf` — Primary historical reference (Poulopoulos 2023)
- `salvi_technical_manual.pdf` — Modern mechanism reference (Salvi)
- `camac_technical_manual.pdf` — Disc regulation reference (Camac)

**Additional parts added via `add_remaining_parts.py`** (184 new objects, 831->1015):
- 14 coupling links (NatLink_*/ShpLink_*) — connect rockers to first bell cranks
- 21 pedal assembly objects (Pedal_*/NotchPlate_*/PedalSpring_*) — 7 pedals with detents
- 1 soundboard (Soundboard) — 4mm spruce panel at z=0
- 47 grommets (Grommet_*) — brass eyelets at soundboard
- 94 disc rotation stops (NatStop_*/ShpStop_*) — 4mm steel blocks
- 7 return springs (ReturnSpring_*) — torsion springs at rockers

### Key Files Added 2026-04-13
- `add_missing_parts.py` — Adds bearings, nuts, rails, column, pins, pedal rods, rockers
- `add_remaining_parts.py` — Adds coupling links, pedals, soundboard, grommets, stops, springs
- `dedup_images.py` — Perceptual hash dedup for reference image frames
- `images/` — 187 deduped reference frames from ML Harps assembly video
