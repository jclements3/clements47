# Clements 47

47-string concert pedal harp design.

## What's here

- `clements47.py` — single source of truth: SB Bezier control points,
  K-knot neck outline, column footprint, limaçon chamber convention.
  Reads `strings.csv` for note / OD / lengths / frequencies.
- `strings.csv` — per-string physics data and explicit grommet / disc-engagement
  positions for all 47 strings.
- `harp_profile.svg` — canonical reference output of `clements47.py`.
- `build_views.py` — produces the 5 orthographic SVGs (side / top / front /
  rear / SBF) plus the 2×2 composite, in the look-and-feel of the
  Erand→Clements47 tablet app.
- `build_freecad.py` — builds `clements47.FCStd` (chamber loft + column +
  neck + 47 string cylinders) from clements47.py + strings.csv.
- `build_techdraw.py` — runs FreeCAD TechDraw HLR on the FCStd to emit
  engineering drawings with hidden lines dashed.
- `index.html` + `svg-pan-zoom.min.js` — local viewer mirroring the tablet
  app's 5-column layout. `python3 -m http.server 8001` then
  http://localhost:8001/.

## Strings — source verification

`strings.csv` does **not** cite a manufacturer or catalog. Values appear
**physics-derived** — for every string, `T = μ · (2 · L · f)²` checks out
against the listed L_flat / f_nat / μ / T columns. Frequencies match
equal temperament for the labelled note (e.g. C1 = 32.70 Hz).

The design is **structurally consistent with real concert pedal harps**:

| Aspect | csv | Real concert pedal harp |
|--------|-----|-------------------------|
| Range | C1 → G7 (47 strings) | C♭1 → G♭7 (47 strings, tuned in C♭ major) |
| Lowest 2 strings | C1, D1 — single position | C1, D1 — hand-tuned, no pedal action |
| Bass (sn 1–12, C1–G2) | `wound_bass_steel_bronze` | Bow Brand "Tarnish-Resistant Wire" (oct 5GF, 6, 7EDC) |
| Mid (oct 2–5 EDCBA) | `gut` | Bow Brand "Natural Gut" |
| Treble (oct 0–1) | `nylon` / `fluorocarbon` | Bow Brand "Artist Nylon", or fluorocarbon options |
| C1 specs | L=1551 mm, OD=1.5 mm, μ=15.4 g/m, T=158.4 N (35.6 lb) | Concert-bass wire range |
| Tension | 35–50 lb across bass | Typical |

Note the harp world numbers octaves **opposite** scientific pitch notation:
"octave 0" is the highest, "octave 7" is the lowest.

### Real string sets that match

You can buy a stock 47-string concert pedal harp set from the same vendors
that supply Salvi / Lyon & Healy / Camac instruments:

- [Bow Brand Concert Grand Pedal Harp Complete String Set (47 Strings) — The Sydney String Centre](https://www.violins.com.au/products/concert-grand-pedal-harp-bow-brand-complete-string-set-47-strings)
- [Bow Brand Complete Set 47 String Pedal Harp — HarpConnection](https://www.harpconnection.com/store/product.php?sku=500-111-712)
- [Bow Brand Strings — Thomann](https://www.thomannmusic.com/bow_brand_strings_harp.html)
- [String Chart Pedal 47 — HarpConnection PDF](https://www.harpconnection.com/PDF%20String%20Charts/String%20Chart%20Pedal%2047.pdf)

To actually order: read each row's note + material + L_flat from
`strings.csv` and substitute the closest stock string in the supplier's
gauge chart. The csv values are sane targets (frequencies and tensions
are right) but no row is traceably copied from a single product.

### References

- [Pedal harp — Wikipedia](https://en.wikipedia.org/wiki/Pedal_harp)
- [Pedal Harp 101 — Harp Spectrum](https://www.harpspectrum.org/pedal/wooster.shtml)
- [Understanding the Range of the Pedal Harp — Danielle Kuntz](https://daniellekuntz.com/understanding-the-range-of-the-pedal-harp-a-composers-guide/)

## Real-harp dimension references

  - Lyon & Healy Style 23 / 30 (47-string concert grand, range C1–G7 same as clements47):
    - 74" H × 21.75" W × 38.75" ExW  (1880 mm × 552 mm × 984 mm)
  - Salvi Daphne 47 (47-string student/concert):
    - 177 cm H × 98 cm W × 53 cm soundboard width (1770 × 980 × 530 mm)
  - clements47 (this design, 47-string, range C1–G7):
    - 73.5" H × 21.7" W × 30.1" ExW  (1867 mm × 550 mm × 763 mm)
    - String span (C1g → G7g) = 643 mm (25.3").
    - Pillar to shoulder reach (col LEFT → K5) = 744 mm (29.3").
    - Slightly wider string span than the Lyon & Healy concert grands (~17%);
      reach is shorter than L&H ExW (744 vs 984 mm) — room to push the
      pillar farther from the strings if a wider stance is wanted.

## Geometry conventions

- Origin at C1 grommet (= SBB, soundboard bass start).
- `+x` toward G7 (treble), `+z` upward toward the neck, `+y` toward the
  player (depth). The 7° rake is encoded into +y (perpendicular to the
  side projection), so the side view shows strings vertical.
- All measurements in millimeters. Z_OFFSET = 186.78 mm = SBB above floor.
- Soundboard is a cubic Bezier; control points documented in
  `strings.csv` and mirrored in `clements47.py`. Soundboard runs from
  `(0, 187)` (C1g = SBB) to `(643.29, 1664)` (G7g).
- Effective inter-string AIR_GAP = 13 mm (csv center_spacing = AIR_GAP +
  (OD_prev + OD_curr) / 2). This is wider than the standard ~10–11 mm
  used on L&H Style 23 / 30 concert grands; it follows Carlos Salzedo's
  custom-harp spec (Lyon & Healy 1931–54, 40 instruments built), which
  added 1/8″ ≈ 3.2 mm to the middle-register spacing to reduce buzzing.
  clements47 applies that extra clearance uniformly across all 47 strings.
- Chamber cross-section: limaçon `r(θ) = a + b·cos(θ)` with `a = 2b`,
  D-to-B distance = 4b = "diam" tapering linearly from 500 mm at SBB
  down to ‖K6 − K4‖ at the neck end.
