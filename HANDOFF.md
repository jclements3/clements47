# clements47 — 47-string concert pedal harp design

## Current state (end of session 2026-04-27)

Single source of truth: `clements47.py`. Reads `strings.csv` for string physics
(note, OD, lengths, frequency). Computes all geometry and outputs SVG profile.

### Coordinate system
- +x across (treble side), +z up (toward neck), +y depth (away from player)
- Origin at the FLOOR (z=0). Strings rake 7° back from vertical.
- Z_OFFSET = 186.778715 mm: SBB sits at z=Z_OFFSET above the floor.

### Generate the SVG
```
python3 clements47.py -o harp_profile.svg
```

### Key design points

**Soundboard S Bezier (P0..P3)** — unshifted z values; +Z_OFFSET added in code:
- P0=SBB=(0, 0)
- P1=(371.81, 971.14)
- P2=(400.63, 1142.59)
- P3=G7g=(735.29, 1477.0)

**Air gap**: 15 mm. Buffer (clearance) radius: 8 mm.

**Floor segment** (magenta on z=0): from SF (-71.51, 0) to floor_end at
B_floor (466.95, 0). U_FLOOR_LEN=538.46, FLOOR_EXTENSION=0.

**Bass tail front**: SBB → SF Bezier with vertical incoming handle 30 mm at SF.

**SB extension**: G7g → K6 (SBN) Bezier.

### Neck knots (in shifted coords; floor at z=0)
9 knots, K_KNOTS:
- K1: (-50, 1786.78)        column LEFT top
- K2: (102.87, 1866.78)     top arc bass peak
- K3: (434.35, 1796.78)     S-knot
- K4: (735.29, 1753.04)     top arc treble end (touches F7 Nf top buffer)
- K5: (800.11, 1711.78)     U1 (BN)
- K6: (735.29, 1725.06)     SBN (touches G7 Ns bottom buffer)
- K7: (594.37, 1686.78)
- K8: (297.18, 1661.78)     collinear handles at angle (-0.9826, -0.1859) — touches A1 Ns buffer
- K9: (-50, 1506.78)        column LEFT bottom corner; 180° corner (in vertical-down, out vertical-up)

K2 has horizontal-right Catmull-Rom tangent. K1 has vertical-up out tangent.
K4↔K6 distance: 27.98mm (top lima\u00e7on diameter at K6).

K4-K5 segment removed (replaced by lima\u00e7on B-locus).
K5-K6 segment removed (combined neck+S+U into one path).

### Closed path traversal
K6 → K7 → K8 → K9 → K1 → K2 → K3 → K4 → [B-locus] → floor_end → floor → SF → bass_tail_front → SBB → S Bezier → G7g → SB extension → K6.

### Lima\u00e7on series (orange)
- D rides S from SBB up to K6 along sb_bezier + sb_extension (skips bass tail
  to avoid B-locus dipping inward).
- Axis perpendicular to S at each station, B endpoints in chamber side.
- Diameter gradient: linear from base_diam=500 mm (at SBB) to top_diam=K4-K6
  distance (~28 mm) at K6.
- Limaçon r(θ) = a + b·cos(θ), a = 2b (boundary case), D-to-B distance = 4b.
- Floor lima\u00e7on (special): lies flat on floor, D=SF, B=B_floor=(466.95, 0).
  D-B distance 538.46 mm. Drawn as orange line on z=0.

**B-locus (magenta)**: chamber outer wall, traced through all B endpoints
plus prepended floor_end at (466.95, 0).

### Column
- Polygon from CF_l (-50, 0), CF_r (-18, 0), up to K1 along K1-K2 arc.

### Outstanding clearance issues
At time of session end:
- F7 Nf at K3-K4: 4.77 mm (worst)
- E7 Nf at K3-K4: 7.53 mm
- E6 Ns at K6-K7: 7.74 mm
- F6 Ns at K6-K7: 7.62 mm

## Files in this archive
- `clements47.py` — single source of truth (reads strings.csv)
- `harp_profile.svg` — current output
- `strings.csv` — original string physics data
- `ai-tar.py`, `ai-untar.py` — archive tools

## Conventions for next session
- Terse responses, no explanatory prose
- Lead with geometry, dimensions, and numbers
- SVG only (no PNG)
- No clarifying questions when intent is clear
- Manufacturing details belong to the CF shop, not Claude
