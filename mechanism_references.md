# Mechanism Reference Notes — Compiled 2026-04-12

Synthesized from Erard book, Buckwell patent, Salvi manual, Camac manual,
and web sources. For designing bell cranks, linkage rods, and pedal action
in Clements47.FCStd.

## Reference PDFs in this repo

- `erard_grecian_harp.pdf` — Poulopoulos 2023 (319pp, CC-BY-NC-ND 4.0).
  Full history of Erard Grecian harp mechanism. Key pages:
  - p.28 Figure 4: 1810 patent drawings for double-action fourchettes
  - p.39 Figure 7: brass plate mechanism photo (Erard No.2631)
  - pp.31-32: dead centre toggle linkage description
  - pp.22-25: Empire model fourchettes, brass plate mounting
  - p.42: Grecian harp dimensions (1700x360x830mm, 43 strings, ~20kg)
- `salvi_technical_manual.pdf` — Salvi official tech manual (24pp).
  Key pages:
  - pp.8-9: structure diagram + mechanism diagram (action plates, discs)
  - pp.12-14: "How a Harp Works" — complete mechanical chain diagram
  - p.14: disc engagement illustration (flat/natural/sharp positions)
- `camac_technical_manual.pdf` — Camac owner's manual (38pp).
  Key pages:
  - p.4: nomenclature with photo labels (A=pin, B=nut, C=natural disc, D=sharp disc)
  - pp.13-15: dead point adjustment, cable length, rod-tuner procedure
  - pp.17-20: disc regulation, friction cone attachment, set screw details
  - p.19: sharp discs have LEFT-HAND threads (critical!)

## Complete Mechanical Chain (modern Salvi/Camac)

```
PEDAL (3 grooves in base: flat / natural / sharp)
  |-- pedal spring (returns pedal upward)
  |-- felt cushion (dampens impact at each groove)
  v
PEDAL ROD COUPLING (screw at base, 2.5mm Allen adjustable)
  v
PEDAL ROD (steel, slides vertically inside column)
  v
ACTION COUPLING (at top of column, 5mm Allen bolt)
  v
MAIN ACTION GROUP (inside neck, distributes to 7 note lines)
  |-- 7 upper lines (natural, "becarre")
  |-- 7 lower lines (sharp, "diese")
  v
LEVERS (slide between two brass action plates)
  |-- connection levers: high-strength steel
  |-- sliding parts: copper-zinc alloy
  v
DISC SPINDLES (rotate in action plate bearings)
  |-- conical end extends through front plate
  |-- friction cone locks disc to spindle
  |-- set screw secures (CW for natural, CCW/LH for sharp!)
  v
DISCS (brass, with 2 prongs each)
  |-- natural disc: upper row
  |-- sharp disc: lower row
  |-- prongs grip string when rotated to 12:30 position
```

## Key Engineering Principles

### Dead Point / Dead Centre (Camac pp.13-14, Erard pp.31-32)

The "dead point" is the precise moment where:
- Natural discs STOP turning and reach maximum grip on strings
- Sharp discs BEGIN turning

This must coincide EXACTLY with the natural pedal position in the base.
If the cable stretches, the dead point drifts (called "overmotion"):
- Natural discs don't fully engage at natural position
- Result: bad intonation + buzzing

**For Clements47 toggle linkage**: The dead point is inherent in the
over-center geometry. The compound bell crank arm angle (~90 deg)
creates a natural dead center when one chain reaches full extension
and the other chain's linkage passes through its straight-line position.

### Disc Rotation Angles (USC/illumin article)

- Flat -> Natural: upper disc rotates ~45 deg CW to engage
- Flat -> Natural: lower disc rotates ~45 deg but does NOT touch string
- Natural -> Sharp: lower disc rotates additional ~35 deg to engage
- Total lower disc travel: ~80 deg (45 + 35)

### Disc Attachment — Friction Cone (Camac p.17)

- Spindle has conical taper extending through front action plate
- Cone inserts into disc bore
- Tightening screw wedges disc onto cone
- Friction alone holds disc — removing screw won't free it
- To free: lever screwdriver between prongs, pop cone loose
- Natural discs: right-hand threads (normal)
- Sharp discs: LEFT-HAND threads (reversed!)

### Disc Sizes — Four Families (Camac pp.18-20)

1. Natural notes E43 to E8 (large discs, 2 prongs)
2. Sharp notes E43 to E8 (large discs, 2 prongs, LH threads)
3. Natural notes F7 to F0 (small discs, 1 prong only — space constraint)
4. Sharp notes F7 to F0 (small discs, 1 prong, LH threads)

### Regulation Tools (Camac p.7)

- 4mm slot screwdriver: large discs
- 2.5mm slot screwdriver: medium discs
- 2.0mm slot screwdriver: small discs
- 2.5mm Allen key: cable length adjustment + large string nuts
- 2.0mm Allen key: small string nuts
- 5.0mm Allen key: column top attachment screws

## Buckwell Patent US1332885A (1920) — Component Architecture

Buckwell's patent for a hand-operated harp action provides the clearest
"exploded view" of the rocker-crank-shaft-disc chain:

| Ref | Part | Function |
|-----|------|----------|
| 5 | Combs | Brass mounting plates (= front/back action plates) |
| 7 | Perforated plate | Top plate where rockers sit |
| 8 | Rocker | Input lever (= bell crank at input) |
| 9 | Upright stem | Rocker handle |
| 10 | Lateral base | Rocker pivot platform |
| 11 | Central pivot | Rocker pivot point |
| 12 | Link | Linkage rod (connects rocker to crank) |
| 14 | Crank | Drive crank fixed to shaft |
| 16 | Coil spring | Return spring on link |
| 17 | Shaft | Disc axle (journaled in combs) |
| 18 | Screw cup | Axle bearing mount |
| 20 | Disk | Tuning disc |
| 21 | Fingers | Prongs / pins on disc |
| 22 | Vertical crank | Compound bell crank for multi-octave |
| 23,24 | Links | Chain linkage rods (different cross-sections: tension vs compression) |

**Key detail**: Links 23 and 24 have DIFFERENT cross-sections because
"one acts in tension and the other in compression."

## Erard Grecian Harp Dimensions (Poulopoulos p.42)

- Height: 1,700 mm
- Soundboard width: 360 mm
- Depth (capital to shoulder): 830 mm
- Strings: 43 (gut treble, silk/brass bass)
- Weight: ~20 kg
- Mechanism: enclosed between 2 brass plates on neck
- Pedals: 7 single-arm with springs, zigzag notches
- Total string tension: ~1,200 kg (Salvi concert grand)

## Erard Historical Mechanism Details (Poulopoulos pp.22-32)

### Fourchettes (Discs)
- First patented 1794 (single action)
- Double-action patent 1810 (No. 3332)
- Enclosed between two brass plates screwed to neck
- Back covered by removable wooden panel
- Adjustable brass nuts with horizontal screws for intonation
- On Grecian: nuts face toward SHOULDER (reversed from Empire)
- First 12 bass strings: no adjustable nuts
- Last treble string: no fourchette AND no adjustable nut

### Mechanism Simplicity (1823 review, p.32)
"Five pieces only are employed: the flat plate or disk, and prongs,
are two, and the motion distributed form one axis only."

Per string, only 5 parts: disc body + 2 prongs + axle + set screw

### Construction Materials (Salvi manual p.6)
- Connection levers: high-strength steel
- Sliding parts: copper-zinc alloy (wear resistance)
- Action plates: special brass
- Neck: high-strength beech + maple plywood
- Column: solid Canadian maple
- Soundboard: Fiemme Valley red spruce

## Mapping to Clements47 Design

### What EXISTS in the model (448 objects via add_mechanism.py):
- 47 strings (Str_C1 through Str_G7)
- 47 axles (Axle_C1 through Axle_G7), 44mm, 4-8mm dia
- 94 discs (NatDisc_*, ShpDisc_*), 4.27-25mm radius
- 188 prongs (NatPrU/D_*, ShpPrU/D_*), M3, 12.7mm ext
- 1 neck (720x200x250mm hollow box)

### What NEEDS to be added:
1. Bell cranks — compound (natural + sharp arms at ~90 deg)
2. Linkage rods — connect bell cranks along each note's chain
3. Front/back action plates — brass, hold spindle bearings
4. Pedal rods — steel, inside column
5. Column — structural tube
6. Pedal assembly — 7 pedals with springs and zigzag notches
7. Disc rotation stops — limit to ~45 deg
8. Return springs — at each link/rocker

### Design Sequence for Next Session:
1. Define bell crank geometry (arm lengths, pivot locations, angles)
2. Calculate linkage rod lengths from string spacing data
3. Add bell cranks to add_mechanism.py
4. Add linkage rods to add_mechanism.py
5. Add action plates (front/back brass plates)
6. Add pedal rods and column
7. Animate the 3-position cycle for verification
