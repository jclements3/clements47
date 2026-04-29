# Soundhole design — Clements47 carbon-fiber chamber

## Summary

Five circular **trumpet-flared** soundholes on the **back** face of the limacon chamber
(the B-locus), graduated from 55.2 mm at the bass end to 25.1 mm near the neck.
Half-flare angle 22 deg, axial flare extension 8 mm. Wall thickness 3 mm. Centerline
along the soundboard arc length `s`. With the chamber volume V = 79.9 L computed from
the (re-shaped) limacon profile in `clements47.py`, the multi-port Helmholtz resonance
lands at **f0 = 85.0 Hz**, between E2 (82.4 Hz) and F2 (87.3 Hz) -- the canonical
"concert harp Helmholtz" frequency.

The inner diameters were re-tuned (from 99-45 mm down to 55.2-25.1 mm) after the
chamber diameter peak was reduced from 620 mm to 280 mm to match real concert pedal
harps (Lyon & Healy 23, Salvi Apollo). Smaller chamber -> smaller holes needed to keep
f0 = 85 Hz. The five hole positions and the flare profile are unchanged.

| sn | s along soundboard (mm) | s/L_total | d_inner (mm) | d_outer (mm) | flare half-angle | face | inner area (mm^2) |
|----|------------------------|-----------|--------------|--------------|------------------|------|-------------------|
| 1  | 171.1                  | 0.09      | 55.2         | 61.66        | 22 deg           | back | 2,393             |
| 2  | 462.0                  | 0.24      | 47.9         | 54.36        | 22 deg           | back | 1,802             |
| 3  | 770.0                  | 0.40      | 40.1         | 46.56        | 22 deg           | back | 1,263             |
| 4  | 1078.0                 | 0.56      | 32.3         | 38.76        | 22 deg           | back |   819             |
| 5  | 1368.9                 | 0.71      | 25.1         | 31.56        | 22 deg           | back |   495             |
|    |                        |           |              |              |                  | Sum  | **6,772 (67.7 cm^2)** |

(L_total ~= 1937 mm = arc length of the chamber path from SF to K6; chamber proper
spans s in [s_at_Sprime_b ~= 170 mm, s_total ~= 1937 mm].)

## Why this design

### Concert pedal harps use 5 oval holes on the **back** of the resonator

Salvi, Lyon & Healy, and Camac all converged on the same pattern: **five oval-shaped
sound holes cut into the back of the resonator** (Pedal harp — Wikipedia). The
positioning and acoustic behaviour was characterised in detail by Le Carrou, Leclère &
Gautier (2010, *J. Acoust. Soc. Am.* **127**(5), 3203–3211), whose experimental setup
diagram (Fig. 1) explicitly labels "Holes" on the back of a Camac concert harp soundbox
and identifies hole 3 and hole 4 as identifiable acoustic source positions in the
inverse-FRF acoustic-imaging maps. The paper's introduction confirms the 5-hole pattern
as standard:

> "the concert harp is a complex sound source involving coupling of a set of strings,
> a flat panel called the soundboard, and a cavity with five sound holes called the
> sound box."

The same paper notes that **lower (bass-side) holes contribute at the lower end of the
frequency scale, higher (treble-side) holes at the higher end** — which is why this
design grades the diameters from large at the bass tail to small near the neck.

The holes serve a dual purpose: (a) string-mounting access (the only access to the
inside of the chamber for hooking the C1 grommet etc.), and (b) acoustic radiation
ports that, in some frequency bands, radiate **more** acoustic power than the
soundboard itself (Le Carrou et al. 2010, results section).

Modern instruments do not put holes in the soundboard top — that pattern is pre-1750.
Modern concert pedal harps have a thin acoustic-wood (or here, carbon-fiber)
**soundboard** plus a **heavy back** in which the holes are cut.

### Why a trumpet/flared profile (and why CF makes it free)

For a Helmholtz resonator with a parallel-walled neck of length `t` (wall thickness)
and inner radius `r`, the resonance frequency is:

```
        c        ┌  A  ┐½         A = π r²
f₀ = ──────── × │ ──── │
       2π        └ V·Lₑ ┘          Lₑ = t + α_in·r + α_out·r        (effective length)
```

with α ≈ 0.85 for an unflanged opening, α ≈ 0.61 for a flanged opening, applied at
each end (Helmholtz resonance — Wikipedia; Euphonics §4.2.1, "The Helmholtz resonator").
Two important physical effects motivate flaring:

1. **Effective length is reduced.** When the throat is gradually widened into a flared
   "bell," air at the mouth couples to the surrounding free space at a larger
   cross-section, so less of the boundary mass has to be accelerated together. The
   simplest accepted correction (used in vented-loudspeaker port design — see Sahlin
   et al., AES; subwoofer-builder.com "Port Flares") is

   ```
   ΔLₑ ≈ −½ · (r_outer − r_inner)
   ```

   subtracted **once per flared end**. For our geometry,
   `r_outer − r_inner = flare_axial · tan(half_angle) = 8 · tan(22°) ≈ 3.23 mm`,
   so each flared mouth subtracts ~1.6 mm from `Lₑ`.

2. **Higher-mode coupling and lower turbulent loss.** A flared mouth provides a smooth
   impedance transition from the throat into free space — this is the trumpet-bell
   effect. It (a) broadens the bandpass (lower Q) so the chamber couples to a wider
   slice of the soundboard's lowest few modes (T1, A0 in Le Carrou's notation,
   ~135–220 Hz), and (b) raises the velocity threshold at which port turbulence
   becomes audible. Subwoofer-builder.com reports a 40-mm radius flare on a 100-mm
   diameter port permits **27 m/s air velocity at 30 Hz before turbulence**, versus
   only 8 m/s with a sharp-edged port — a 3.4× improvement in clean SPL handling.

For a wood concert harp these benefits are normally given up because moulding a flared
profile in spruce or maple is expensive: the holes are routed straight through. **In a
carbon-fiber lay-up the flare is free** — you mould a 22° trumpet-bell collar around
each hole as part of the same back-skin lay-up, with a chamfered ring of CF tooling.
You get the bandwidth and velocity advantages essentially for the cost of a more
complex tool.

### Number, placement, and graduated sizing

- **N = 5** matches the Salvi/L&H/Camac convention.
- **Longitudinal placement** is at fixed s = 171.1, 462.0, 770.0, 1078.0, 1368.9 mm
  along the chamber path (these positions are unchanged from the previous design).
  These match the visible hole pattern in Le Carrou et al. (2010) Fig. 1 reasonably
  closely.
- **Diameters** decrease from bass to treble (55.2, 47.9, 40.1, 32.3, 25.1 mm). The
  bass-end hole is ~2.2x the treble-end hole, mirroring the chamber diameter taper
  (290 mm at the floor / S'b -> 73 mm at K6). All inner diameters were scaled by
  k = 0.557 from the old (V = 133 L) sizing to hit f0 = 85 Hz at the new (V = 79.9 L)
  volume. Hole sizes remain large enough for harpist stringing-arm access.
- **Face** = "back" — every hole pierces the limaçon B-locus surface (the chamber
  back wall on the audience side, opposite the soundboard top). They are NOT on the
  soundboard top. The soundboard top remains a clean carbon-fiber radiating diaphragm,
  exactly like a modern wood pedal harp.

### Volume calculation

The chamber cross-section is the limacon `r(theta) = a + b*cos(theta)` with `a = 2b`
and `D-to-B distance = 4b = diam(s)`. The closed-curve area is

```
A_lima(s) = pi * (a^2 + b^2/2) = (9*pi/32) * D(s)^2  ~=  0.8836 * D(s)^2
```

`diam(s)` is now a centripetal Catmull-Rom curve with constant D = 290 mm from SF
(s = 0) up through S'b (s ~= 170 mm), a smooth peak of D = 280 mm at s = 700 mm, and
a taper down to D = 73 mm at K6 (s_total ~= 1937 mm). The bass tail base region
(s < s_at_Sprime_b) is solid CF, NOT a chamber, so it is excluded from the volume
integral. Trapezoidal integration of `A_lima(s) ds` over s in [s_at_Sprime_b,
s_total] gives:

```
V = 79.9 L = 0.0799 m^3
```

This is in the realistic concert-pedal-harp range (Lyon & Healy Style 23 / Salvi
Apollo class), about 60 % of the previous (over-sized) clements47 chamber. The new
profile dropped the peak diameter from 620 mm to 280 mm to fit a real player.

### Resulting Helmholtz frequency

For 5 holes treated as parallel ports of a single Helmholtz cavity:

```
        c     [ sum_i (A_i / Leff_i) ] ^ 1/2
f0 = ------ * [ -------------------- ]
       2*pi   [          V           ]
```

With

| sn | A_i (mm^2) | Leff_i (mm) | A_i / Leff_i (mm) |
|----|-----------:|------------:|------------------:|
| 1  | 2393.1     | 43.65       | 54.82             |
| 2  | 1802.0     | 38.32       | 47.02             |
| 3  | 1262.9     | 32.63       | 38.71             |
| 4  |  819.4     | 26.93       | 30.42             |
| 5  |  494.8     | 21.68       | 22.82             |
|    |            | Sum         | **193.80**        |

(c_air = 343 m/s, dry air at 20 C; per-hole effective length:
`Leff = t + 0.85*r_in + 0.61*r_out - 0.5*(r_out - r_in)` with t = 3 mm wall, 0.85*r
flanged on the chamber-interior side and 0.61*r unflanged on the open side, plus the
trumpet-flare correction `-0.5*(r_out - r_in)` once at the flared mouth.)

```
f0 = (343000 / (2*pi)) * sqrt(193.80 / 79.94e6) = 85.0 Hz
```

This sits between **E2 (82.41 Hz)** and **F2 (87.31 Hz)** -- the canonical concert-harp
Helmholtz frequency reported in the literature ("typical concert harp Helmholtz is
~85 Hz, near E2").

## Implementation notes for build_freecad.py

- The CSV `soundholes.csv` is the machine-readable spec.
- For each row, the hole centerline is on the chamber back wall (the **B-locus** in
  `clements47.py`), at arc-length `s_mm` along the chamber path. Compute the back-wall
  point at `s_mm` by:
  ```python
  D_pt, perp = chamber_axis(s_mm)           # function in clements47.py
  diam = diam_at_s(s_mm)                    # smooth Catmull-Rom profile
  B_pt = D_pt + diam * perp                 # the back wall
  ```
  Then the hole centerline points along `perp` (out of the chamber, radially away
  from the soundboard).
- The flare profile is a frustum: inner cylinder of `diam_inner_mm` × wall thickness
  3 mm, then a cone whose larger base is `diam_outer_mm` and axial length 8 mm,
  flush-blended with the chamber back surface on the outside.
- Holes go through the limaçon back wall, NOT the soundboard top.

## References

- Le Carrou, J.-L., Leclère, Q., & Gautier, F. (2010). *Some characteristics of the
  concert harp's acoustic radiation.* J. Acoust. Soc. Am. **127**(5), 3203–3211.
  Confirms the 5-hole back-of-chamber convention and identifies the holes as primary
  radiators in three frequency bands.
- "Pedal harp" — Wikipedia: "Five oval-shaped sound holes are cut into the back of
  the resonator."
- "Helmholtz resonance" — Wikipedia: standard formula and end-correction values.
- Euphonics, *§4.2.1 The Helmholtz resonator*: derivation of f₀ = (c/2π)√(S/VL) and
  the flanged/unflanged end correction.
- Subwoofer-builder.com, *Port Flares*: empirical flare effective-length correction
  `ΔLₑ ≈ −½ · r_flare` and turbulent-velocity tables motivating flared mouths.
- US7498495B1 (harp soundbox patent) — example of three apertures with graduated
  sizing in the front-facing panel; confirms the principle of graduated-hole sizing
  used by harp makers.
