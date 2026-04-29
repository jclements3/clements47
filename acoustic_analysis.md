# Acoustic analysis -- clements47 carbon-fiber concert pedal harp

Author: acoustic-analysis sub-agent
Date: 2026-04-27 (re-tuned for new chamber profile)
Inputs: `clements47.py` (geometry constants), `strings.csv` (string physics).
Geometry conventions: see `clements47.py` and `README.md`.

**Re-tune note (2026-04-27):** The chamber diameter profile in `clements47.py`
was re-shaped to match real concert pedal harps -- peak D dropped from
620 mm to 280 mm. This shrank V from 133 L to 79.9 L; the soundhole inner
diameters in `soundholes.csv` were correspondingly scaled by k = 0.557 to
keep the multi-port Helmholtz frequency at the canonical f_H = 85 Hz.

This report computes the geometric volume of the limaçon-cross-section
chamber, then estimates the Helmholtz resonance, the first standing-wave
cavity mode along the chamber axis, and compares the carbon-fiber soundboard
material against spruce. All numbers are derived analytically or by
numerical integration on the as-designed Bezier centerline.

Speed of sound `c = 343 m/s` at 20 C, 1 atm, used throughout.

---

## 1. Limaçon cross-section area

The chamber cross-section is the limaçon
`r(θ) = a + b·cos(θ)` with `a = 2b` (convex; flat side faces the
soundboard, bulb hangs into the chamber). Per the project convention
`diam = 4b` is the D-to-B distance — the long axis of the limaçon, NOT
its perpendicular width. `b = D/4`, `a = D/2`.

The polar area integral is

```
A = (1/2) ∫₀^{2π} r²(θ) dθ
  = (1/2) ∫₀^{2π} [a² + 2ab cos(θ) + b² cos²(θ)] dθ
  = (1/2) [2π a² + 0 + π b²]
  = π (a² + b²/2)
```

With `a = 2b`:

```
A = π (4b² + b²/2) = π · 9b²/2 = 4.5 π b²
```

Substituting `b = D/4`:

```
A(D) = (9π / 32) · D² ≈ 0.8836 · D²
```

Sanity check (numerical quadrature at D=500 mm) matches the closed form
to 5 decimal places (220,893.23 mm²).

The perpendicular y-extent (across the limaçon, transverse to the D-B
axis) is also useful to know — this is the "width" you see in
cross-section orthographic. Maximizing `r(θ)·sin(θ)` with `a = 2b`
gives `cos(θ) = (√3 − 1)/2 ≈ 0.366` (θ ≈ 68.5°), `r = 2.366b`,
so `y_max = 2.202·b` and the **full perpendicular width is 4.404·b ≈
1.101·D**. (The prompt's "0.55·diam" is half-width above the axis;
the full transverse width is twice that.)

| Station                    | Diameter D | Limacon area A(D) |
|----------------------------|-----------|-------------------|
| Floor / S'b (s=170 mm)     | 290.00 mm |  743.0 cm^2 |
| Peak (s=700 mm)            | 280.00 mm |  692.7 cm^2 |
| K6 (s=s_total~=1937 mm)    |  73.12 mm |   47.2 cm^2 |
| Mean over chamber (V/L)    |    --     |  452.5 cm^2 |

The mean cross-section has equivalent circular radius
`r_eq = sqrt(A/pi) ~= 120 mm`.

---

## 2. Total chamber volume

The chamber path runs from SF through the bass-tail-front Bezier, the SB
Bezier (SBB -> G7g), and the SB extension Bezier (G7g -> K6) -- see
`chamber_axis()` in `clements47.py`. The diameter profile `diam_at_s()`
is now a centripetal Catmull-Rom curve through three knots:

  - constant D = 290 mm from SF (s = 0) up through S'b (s ~= 170 mm)
  - peak D = 280 mm at s = 700 mm
  - taper to D = TOP_DIAM ~= 73 mm at K6 (s = s_total)

The base region [SF, S'b] is solid CF (bass-tail joinery), NOT chamber
volume, so it is excluded from the integral.

| Segment                         | s span (mm)        | Arc length |
|---------------------------------|--------------------|-----------:|
| Bass-tail base (SOLID, excluded)| [0, 170]           |  170 mm    |
| Chamber proper (S'b -> K6)      | [170, 1937]        | 1767 mm    |
| **Chamber length L**            |                    | **1767 mm** |

Volume (trapezoidal integration of A(D(s)) ds, 8000-point grid, with
A(D) = (9*pi/32) * D^2 ~= 0.8836 * D^2):

```
V = integral_{s=170}^{1937} A(D(s)) ds  =  79.94 L  ~=  7.99e4 cm^3
```

That is comparable to a Lyon & Healy Style 23 / Salvi Apollo soundbox
(~40-80 L is typical for concert pedal harps; the upper end of this
range fits the clements47 wider Salzedo-style spacing). The peak chamber
diameter dropped from 620 mm (previous design, V = 133 L) to 280 mm
(this design) to fit the geometry of a real player; the volume fell
proportionally to ~60 % of its previous value.

---

## 3. Helmholtz resonator estimate

The first acoustically significant mode of a stringed-instrument
soundbox is typically the A0 (Helmholtz) mode — air mass in the
soundholes oscillating against the cavity compliance. The standard
formula (rigid-walled approximation):

```
f_H = (c / 2π) · √(A_h / (V · L_eff))
```

where
- `A_h` = total area of the soundholes,
- `V`   = chamber volume,
- `L_eff = t + 2·Δ` = soundboard thickness + end correction,
- `Δ ≈ 0.85 · r` per flanged opening (typical),
- `r`   = effective radius of one hole (per-hole, summed in parallel
  through `A_h`, with the per-hole `r` controlling the end correction).

With the new V = 79.94 L chamber, the as-built 5-hole layout in
`soundholes.csv` (inner diameters 55.2, 47.9, 40.1, 32.3, 25.1 mm; total
open area 67.7 cm^2) hits the canonical f0 = 85 Hz target cleanly:

| Configuration                              | A_h total | n holes | f_H        |
|--------------------------------------------|----------:|--------:|-----------:|
| As-built (re-tuned for V = 79.9 L)         | 67.7 cm^2 | 5       | **85.0 Hz** |

Per-hole effective length uses `Leff = t + 0.85*r_in + 0.61*r_out -
0.5*(r_out - r_in)` with t = 3 mm wall (flanged on the chamber-interior
side, unflanged on the open side, plus the trumpet-flare correction at
the flared mouth). See `soundholes.md` for the full per-hole table.

**Assumptions and caveats:**
- Rigid-wall Helmholtz formula. In a real harp the SB is itself a
  vibrating membrane, and the A0 mode couples to the T1 plate mode
  ([Le Carrou et al., JASA 2007](https://pubs.aip.org/asa/jasa/article-abstract/121/1/559/631527))
  through the cavity → both modes are pulled apart in frequency, with
  the actual radiated A0 typically a few Hz above the rigid-wall
  estimate. Plus, end correction depends on how flanged the opening is
  (0.85·r per side for fully flanged; closer to 0.61·r for unflanged).
- The chamber walls are CF, not wood — much higher specific stiffness;
  the rigid-wall approximation is closer to true than for a spruce
  soundbox.
- Le Carrou et al. note a key fact about real harps:
  "the [harp] does not really take advantage of the soundbox
  resonance to increase its radiated sound in low frequencies."
  The A0 mode of a Lyon & Healy concert grand sits **above** the
  lowest important plate mode T1 — i.e. the soundholes are sized for
  stringing access, not Helmholtz tuning. This design choice is
  worth examining: shifting the clements47 A0 down to ~50 Hz
  (between G1 and A1 fundamentals) actually fills a gap in the
  conventional design, and may help the lowest octave radiate, but
  it will shift coloration of the tap tone away from the L&H
  reference.

---

## 4. First-mode cavity standing wave

Treating the chamber as an air column with one effectively closed end
(the small K6 end is not a free open boundary — it's framed by the
neck and the action plates) and one effectively open end (the
soundboard, even when intact, is a low-impedance boundary at low
frequencies), the quarter-wavelength fundamental is

```
f1 = c / (4 L) = 343 / (4 * 1.767) = 48.5 Hz
```

If both ends were the same (both open or both closed), the half-
wavelength fundamental would be `f1 = c / (2L) = 97.0 Hz`. The
real situation is intermediate, depending on how leaky the
soundboard is at the bottom and how rigid the K6 end is.

**Comparison to bass strings** (bass-octave fundamentals):

| String | f (Hz) | Quarter-wave 48.5 Hz | Half-wave 97.0 Hz  |
|-------:|-------:|:--------------------:|:------------------:|
| C1     | 32.70  | string < cavity      | string < cavity    |
| D1     | 36.71  | string < cavity      | string < cavity    |
| E1     | 41.20  | string < cavity      | string < cavity    |
| F1     | 43.65  | string < cavity      | string < cavity    |
| G1     | 49.00  | **near match**       | string < cavity    |
| A1     | 55.00  | string > cavity      | string < cavity    |
| C2     | 65.41  | —                    | string < cavity    |
| F2     | 87.31  | —                    | **near match**     |
| C3     | 130.81 | —                    | —                  |
| E3     | 164.81 | —                    | —                  |

**Acoustic mismatch in the lowest octave**: C1 (32.7 Hz) is
**well below** the chamber's quarter-wave fundamental — meaning the
five lowest strings (C1, D1, E1, F1) drive the cavity below its first
axial resonance. They will radiate **almost entirely through direct
soundboard motion** (T1-type plate modes), not through cavity-air
amplification. This is consistent with how real concert pedal harps
behave (per Le Carrou et al.): the bass octave is structurally
radiated, not Helmholtz-amplified.

If the design goal is to *amplify* the lowest octave, this analysis
suggests:
- **Lengthen the chamber.** L = 1.71 m is already long; getting f₁
  below C1 would mean L ≈ 2.6 m (impractical).
- **Or, lower the Helmholtz frequency further** (open hole area
  effectively shrinks the cavity below A0 → can't fix sub-A0).
- **Practical answer**: accept that bass-octave amplification will
  be soundboard-radiation-dominated. Optimize the CF plate's
  fundamental T1 mode to fall near 35-50 Hz.

---

## 5. Carbon fiber vs. spruce: material tradeoffs

| Property                          | Sitka spruce (parallel grain) | CFRP quasi-isotropic |
|-----------------------------------|-------------------------------|----------------------|
| Young's modulus E                 | ~11 GPa                       | ~70 GPa              |
| Density ρ                         | 0.40 g/cm³ (400 kg/m³)        | 1.60 g/cm³ (1600 kg/m³) |
| Specific stiffness E/ρ            | 27.5 (Mm/s)²                  | 43.8 (Mm/s)²         |
| Longitudinal speed √(E/ρ)         | 5244 m/s                      | 6614 m/s             |
| Sound radiation R = √(E/ρ)/ρ      | 13.1                          | 4.13                 |
| Acoustic impedance ρc_l (rel.)    | 4400                          | 112,000              |

**Key implications for the harp:**

1. **CF is ~26× higher in (ρ·E)** — a much higher-impedance plate.
   It will couple **less efficiently to air** at low frequencies
   than spruce does, despite having higher specific stiffness.
   The radiation coefficient R = c_l / ρ is a standard luthier's
   figure of merit ("the higher, the better the soundboard
   radiates")
   ([Acoustic Guitar Tonewood Primer](https://acousticguitar.com/a-tonewood-primer-how-to-pick-the-right-materials-for-your-optimal-sound/)) —
   spruce's R is ~3× CF's. Translation: a CF top of equal thickness
   to a spruce top will feel "tighter" and sound less full at low
   frequencies, but project louder in the mids/highs.
2. **CF can be made thinner**, recovering some of that lost
   radiation efficiency
   ([Acoustic Guitar — Best of Carbon Fiber and Spruce](https://acousticguitar.com/best-of-carbon-fiber-and-spruce/))
   notes that "the laws of physics say that the thinner the
   soundboard, the better the sound quality". RainSong / KLOS
   guitars use ~2-3 mm CF tops; many luthiers find 3-4 mm CF
   gives near-spruce radiation while remaining structurally sound.
   The 5 mm assumption above is conservative.
3. **CF is dimensionally stable** — no humidity warping, no
   re-strung-and-retuned drift after climate change. Concert harps
   typically use Sitka or Engelmann spruce, which moves with humidity;
   a CF plate would simplify maintenance for outdoor / touring
   instruments
   ([Rees Harps — pros and cons of CF harps](https://reesharps.com/pros-and-cons-of-carbon-fiber-harps)).
4. **Decay characteristics**: CF has lower internal damping than
   wood. Notes will sustain longer (good for cantabile lines, harder
   for damped articulation). Attack transient is sharper because the
   plate accelerates faster (higher specific stiffness).
5. **Tonal character**: KLOS Guitars' acoustic-analysis comparison
   ([KLOS Guitars — CF vs Wood](https://klosguitars.com/blogs/klos-insights/comparing-carbon-fiber-vs-wood-in-guitarmaking-acoustic-analysis))
   reports CF tops are perceived as "warmer / more nuanced" by
   fingerstyle players, with consistent unit-to-unit response.
   Concert-grand harpists used to spruce will likely perceive a
   different attack envelope and a more uniform per-string voicing.

**Recommendation on plate thickness**: 5 mm is heavy for CF. Consider
3-4 mm with appropriate internal bracing/ribbing for the bass-end
loading. For a 47-string set the total tension is ~1466 lb (per
clements47.md / strings.csv summary); a 3-4 mm CFRP plate with
unidirectional carbon spars under the bass strings is a realistic
target and would substantially improve low-frequency radiation
compared to 5 mm.

---

## 6. Recommendations for soundhole + chamber design

Given V ~= 79.9 L and chamber L ~= 1.77 m:

1. **f_H = 85 Hz target is now hit.** With the re-shaped diameter
   profile (peak D = 280 mm) the chamber volume came down to 79.9 L,
   and the 5-hole layout in `soundholes.csv` was re-scaled (k =
   0.557) to total inner area 67.7 cm^2. This places f_H squarely
   between E2 and F2 -- the canonical concert-harp Helmholtz value.

2. **Soundhole layout**: 5 holes on the back-wall B-locus at fixed
   s = 171, 462, 770, 1078, 1369 mm (Lyon & Healy convention).
   Inner diameters now 55.2 / 47.9 / 40.1 / 32.3 / 25.1 mm,
   graduated bass-to-treble. Outer (flared) diameters 61.7 / 54.4 /
   46.6 / 38.8 / 31.6 mm fit comfortably within the local back-wall
   transverse extent (~1.10 * D(s)) at every station -- the largest
   ratio is hole #1 with 61.7 mm vs 319 mm wall extent.

3. **Bass-tail base (s in [0, 170 mm])**: this region is now SOLID
   CF (not a chamber) and is excluded from V. The bass-tail joinery
   functions as a structural cap, not a resonator. If a future
   variant opens it up, V will rise and f_H will fall accordingly
   (about 14 cm^3 per mm of additional s opened up, near the base).

4. **Plate-mode (T1) tuning** still matters most for the bottom
   octave. The lowest 4-5 strings (C1-F1, ~33-44 Hz) sit below
   both the cavity quarter-wave mode and f_H, so they radiate
   through plate motion, not Helmholtz amplification. Specify the
   CF plate's T1 mode in the 30-45 Hz range via fiber layup, plate
   thickness, and bracing. RainSong-style sandwich panels (CF skins
   + Nomex honeycomb core) give better radiation per unit mass than
   solid CF and are worth considering
   ([Acoustical architecture -- CompositesWorld](https://www.compositesworld.com/articles/acoustical-architecture-making-beautiful-music)).

---

## Summary of computed numbers

| Quantity                               | Value |
|----------------------------------------|------:|
| Limacon area formula                   | A(D) = 9*pi*D^2/32 ~= 0.8836*D^2 |
| Limacon perpendicular width            | 1.101*D (full width across) |
| Chamber arc length L (S'b -> K6)       | 1767 mm |
| Diameter at S'b (floor cap)            | 290 mm  |
| Peak diameter (s = 700 mm)             | 280 mm  |
| Top diameter at K6                     | 73.12 mm |
| Total chamber volume V                 | **79.94 L** |
| Mean cross-section area                | 452.5 cm^2 |
| Total soundhole open area              | **67.7 cm^2** (5 trumpet-flared holes) |
| Helmholtz f_H (re-tuned, V = 79.9 L)   | **85.0 Hz** |
| Cavity 1/4-wave fundamental f_axial    | **48.5 Hz** |
| Cavity 1/2-wave fundamental f_axial    | 97.0 Hz |
| CF c_long = sqrt(E/rho)                | 6614 m/s |
| Spruce c_long = sqrt(E/rho)            | 5244 m/s |
| CF radiation coeff R = c_long/rho      | 4.13 |
| Spruce radiation coeff R = c_long/rho  | 13.1 (~3x CF) |

Lowest 4 strings (C1-F1, ~33-44 Hz) sit **below** both the cavity
1/4-wave mode (48.5 Hz) and the Helmholtz f_H (85 Hz) -- these will
be radiated by direct CF plate motion, not by air-mode amplification.
The Helmholtz mode now reinforces E2-F2 (lowest octave second-tier
strings); the previous design had f_H ~55 Hz which couldn't be tuned
to the canonical 85 Hz value because V was 133 L (too large).

---

## References

- Le Carrou, J.-L., Gautier, F., Dauchez, N. & Gilbert, J. (2007).
  *Experimental study of A0 and T1 modes of the concert harp.*
  J. Acoust. Soc. Am. 121(1):559-567.
  [pubs.aip.org/asa/jasa/article-abstract/121/1/559/631527](https://pubs.aip.org/asa/jasa/article-abstract/121/1/559/631527)
  — establishes that on a Lyon & Healy concert grand the A0
  Helmholtz mode lies *above* the T1 plate fundamental, so the
  harp does not heavily exploit Helmholtz amplification in the bass.
- Le Carrou, J.-L. *Sympathetic String Modes in the Concert Harp.*
  [academia.edu/20015414](https://www.academia.edu/20015414/Sympathetic_String_Modes_in_the_Concert_Harp)
- *Acoustic intensity measurement of the sound field radiated by a
  concert harp.* Applied Acoustics, 2004.
  [sciencedirect.com/science/article/abs/pii/S0003682X04001069](https://www.sciencedirect.com/science/article/abs/pii/S0003682X04001069)
- *Helmholtz Resonance.* UNSW Music Acoustics.
  [newt.phys.unsw.edu.au/jw/Helmholtz.html](https://newt.phys.unsw.edu.au/jw/Helmholtz.html)
- Rees Harps — *Pros and cons of carbon-fiber harps.*
  [reesharps.com/pros-and-cons-of-carbon-fiber-harps](https://reesharps.com/pros-and-cons-of-carbon-fiber-harps)
- Acoustic Guitar — *Best of Carbon Fiber and Spruce.*
  [acousticguitar.com/best-of-carbon-fiber-and-spruce/](https://acousticguitar.com/best-of-carbon-fiber-and-spruce/)
- Acoustic Guitar — *A Tonewood Primer (radiation coefficient R).*
  [acousticguitar.com/a-tonewood-primer-how-to-pick-the-right-materials-for-your-optimal-sound/](https://acousticguitar.com/a-tonewood-primer-how-to-pick-the-right-materials-for-your-optimal-sound/)
- KLOS Guitars — *Comparing Carbon Fiber vs Wood (Acoustic Analysis).*
  [klosguitars.com/blogs/klos-insights/comparing-carbon-fiber-vs-wood-in-guitarmaking-acoustic-analysis](https://klosguitars.com/blogs/klos-insights/comparing-carbon-fiber-vs-wood-in-guitarmaking-acoustic-analysis)
- CompositesWorld — *Acoustical architecture: Making beautiful music.*
  [compositesworld.com/articles/acoustical-architecture-making-beautiful-music](https://www.compositesworld.com/articles/acoustical-architecture-making-beautiful-music)
- RainSong — *Carbon Fiber Acoustic Guitar Soundboards.*
  [rainsong.com/post/carbon-fiber-acoustic-guitar-soundboards](https://www.rainsong.com/post/carbon-fiber-acoustic-guitar-soundboards)
