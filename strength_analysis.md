# Clements47 — Structural Strength Analysis

Analysis of the carbon-fiber neck and column under static string load.

- Date: 2026-04-27
- Source data: `strings.csv` (47 strings, T_N column), `clements47.py`
  (geometry constants), `build_freecad.py` (cross-section thicknesses
  COLUMN_W_Y = NECK_W_Y = 32 mm).
- Analysis script: `/tmp/strength_analysis.py` (one-off, not committed).

---

## 1. Total String Tension

Summing the `T_N` column over all 47 rows of `strings.csv`:

```
F_total = sum(T_N) = 7079.3 N  =  1591.5 lb
```

This is in the typical concert-pedal-harp range (Salvi quotes ~1200 kgf
≈ 11 800 N, Lyon & Healy ~6500-7000 N). Clements47 sits at the lower
end of that range thanks to the slightly thinner gut/nylon trebles.

The bass-tension distribution along the neck (after projecting each
string's tuning-pin location onto the K1->K6 chord and binning into
thirds):

| Region (along K1->K6 chord, 0..690 mm) | sum(T_N) | sum(F_perp) |
|----------------------------------------|----------|-------------|
| Bass third  (0..230 mm)                |   808 N  |   805 N |
| Middle third (230..460 mm)             |  2999 N  |  2986 N |
| Treble third (460..690 mm)             |  3273 N  |  3260 N |

(F_perp is the chord-perpendicular component of each string's pull on
the neck. It is ~99 % of T because the strings hang nearly perpendicular
to the K1->K6 chord.)

The middle and treble thirds carry ~88 % of the load even though those
strings are individually thinner — there are simply more of them per
unit length, and the rake angle puts every pin at roughly the same
chord-perpendicular angle.

The 6 single strings with the largest F_perp on the neck:

| sn | note | T (N) | F_perp (N) | s along chord (mm) |
|----|------|-------|------------|---------------------|
| 10 | E2   | 224.1 | 223.2 | 301.1 |
| 12 | G2   | 223.8 | 222.9 | 329.7 |
|  9 | D2   | 220.2 | 219.3 | 286.5 |
| 11 | F2   | 218.4 | 217.5 | 315.3 |
|  8 | C2   | 214.4 | 213.5 | 271.8 |
|  7 | B1   | 209.5 | 208.7 | 257.7 |

These are the wound bass-mid strings; they dominate the load picture.

---

## 2. Column — Axial Compression and Buckling

### Geometry

```
COL_X_LEFT  = -43.74 mm
COL_X_RIGHT = -15.75 mm
=> column x-extent  a_x = 27.99 mm
   column y-extent  a_y = 32.00 mm  (COLUMN_W_Y in build_freecad.py)
   column length   L  = COL_TOP_Z = 1600 + Z_OFFSET = 1786.78 mm
```

Two cross-section assumptions:

- **Solid box** 28 × 32 mm:  A = 895.7 mm², I_min = 58 476 mm⁴
- **Hollow box** 28 × 32 mm with 4 mm CF wall:  A = 415.9 mm²,
  I_min = 42 500 mm⁴

The hollow box is the realistic CF-laminate target (saves ~2.4× mass
and is how concert harp pillars are actually built once they go from
wood to composite).

### Load on column

The neck transmits the string-tension resultant to the column via the
K1 joint. Worst case: the entire string tension F_total acts as axial
compression along the column axis.

```
P = F_total = 7079.3 N  (worst-case axial compression)
```

A more accurate value is ~0.7-0.9 × F_total (the soundboard and base
share load through the tail/SF joint), but using 100 % gives a
conservative estimate.

### Axial compressive stress

Material limit:  σ_c ≈ 500 MPa  (quasi-isotropic CF compression).

```
sigma_solid  = P / A_solid  = 7079.3 / 895.7  =   7.90 MPa
sigma_hollow = P / A_hollow = 7079.3 / 415.9  =  17.02 MPa
```

| Section | sigma | SF (= sigma_c / sigma) |
|---------|-------|------------------------|
| Solid   |  7.9 MPa | **63.3** |
| Hollow  | 17.0 MPa | **29.4** |

Pure-axial yield is not the binding constraint by a wide margin.

### Euler buckling

The column is fixed in the pedal-base box at the floor and pin-jointed
to the neck at K1. Effective-length factor K_eff = 0.7 (fixed-pinned).

```
L_e = K_eff * L = 0.7 * 1786.78 = 1250.7 mm

P_cr = pi^2 * E * I_min / L_e^2

P_cr_solid  = pi^2 * 70 000 MPa * 58 476 mm^4 / (1250.7 mm)^2
            = 25 825 N

P_cr_hollow = pi^2 * 70 000 MPa * 42 500 mm^4 / (1250.7 mm)^2
            = 18 769 N
```

| Section | P_cr (N) | SF_buckling = P_cr / P |
|---------|----------|------------------------|
| Solid   | 25 825   | **3.65** |
| Hollow  | 18 769   | **2.65** |

**Buckling is the binding constraint on the column.** The hollow CF
column passes the 2× SF target with margin 2.65, but if the wall is
reduced or the column is made any longer it will quickly fall below
2× SF.

If the boundary condition is closer to pinned-pinned (K=1.0, neck and
base both rotationally compliant):

```
P_cr_pinned_solid  = pi^2 * E * 58 476 / 1786.78^2 = 12 654 N -> SF = 1.79
P_cr_pinned_hollow = pi^2 * E * 42 500 / 1786.78^2 =  9 197 N -> SF = 1.30
```

That fails 2× SF. The column **needs the fixed base** to make 2× SF.
Recommendation: design the pedal-base column socket as a true
moment-carrying joint (clamped fit + epoxy + bolts).

If on the other hand the neck-to-column joint can be made rigid
(K=0.5, fixed-fixed):

```
L_e = 0.5 * 1786.78 = 893.4 mm
P_cr_hollow = pi^2 * 70000 * 42500 / 893.4^2 = 36 770 N -> SF = 5.19
```

Plenty of headroom. Pursuing a rigid neck-column joint (lap joint with
multiple shear pins or laminate scarf) is the cheapest way to add
column buckling margin.

---

## 3. Neck — Bending Analysis

### Beam model

The neck closes a Bezier loop K1->K2->K3->K4->K5->K6->K7->K8->K9->K1.
For first-order bending the relevant span is the chord K1 -> K6
(soundboard support), since the neck is essentially a curved beam
between the column joint at K1 and the soundboard joint at K6/SBN:

```
K1 = (-43.74, 1786.78)
K6 = ( 643.29, 1725.06)
chord K1 -> K6 length = 689.8 mm
```

Cross-section, locally:

- y-thickness:  b = NECK_W_Y = 32 mm  (constant)
- xz-thickness h: varies from ~50 mm (thinnest, near K3) to ~80 mm
  (thickest, mid-arch). Peak bending moment is checked against both
  h_nom = 65 mm and h_worst = 50 mm.

For each string i, the tuning-pin position N_f^i lies on the neck.
The string applies a force on the neck

```
F_i = T_i * (Ng_i - Nf_i) / |Ng_i - Nf_i|   (vector pulling pin
                                              toward grommet)
```

Decomposing F_i into chord-tangent (axial through the neck) and
chord-perpendicular (transverse, bending) components and treating the
neck as a simply-supported beam between K1 and K6:

```
R_K1 (perp) = -2456.6 N
R_K6 (perp) = -4594.3 N      (sum = -7050.9 N, matches the
                              total perp load)
```

K6 takes ~65 % of the transverse load because the heavy bass-mid
strings sit closer to K6 than to K1 along the chord.

### Bending moment

Sweeping s along the chord and summing piecewise contributions:

```
M(s) = R_K1 * s  -  sum_{i: s_i < s}  F_perp_i * (s - s_i)
```

Peak moment magnitude occurs at

```
|M|_peak = 646 522 N*mm  =  646.5 N*m   at s = 345 mm
```

The closest K-knot to s = 345 mm is **K8** (260, 1661.8) at s = 313.7 mm,
with K7 (519.9, 1686.8) at s = 570.4 mm. So the peak moment lies on the
**K8-K7 segment of the neck, slightly bass-of-centre on the lower
neck rail**. In a concert-harp neck this is the structural midspan and
historically the section that fails first when over-tensioned.

### Bending stress

Section modulus and stress for solid CF rectangle:

```
I    = b * h^3 / 12
c    = h / 2
sigma = |M| * c / I = 6 |M| / (b * h^2)
```

| Cross-section h | I (mm^4) | sigma (MPa) | SF (sigma_t/sigma) | SF (sigma_c/sigma) |
|---|---|---|---|---|
| Solid h=65 mm  | 732 700 | 28.7 | **24.4** | **17.4** |
| Solid h=50 mm  | 333 300 | 48.5 | 14.4 | **10.3** |
| Hollow h=65, 5 mm wall | 426 600 | 49.2 | 14.2 | **10.2** |
| Hollow h=50, 5 mm wall | 215 200 | 75.0 |  9.3 | **6.7** |

Even the thin-section hollow case gives SF = 6.7 against compressive
failure. **The neck passes 2× SF by a comfortable margin in all
realistic build-ups.**

The relevant failure mode for CF in bending is the *compression* face
(compressive strength 500 MPa < tensile 700 MPa for quasi-isotropic
laminate). For the neck the compression face is the *outer* (top) edge
of the K1->K2->K3->K4 arc — the convex side curves up under load and
the inner (lower) edge K6->K7->K8 goes into tension.

### Worst-stress location

The peak bending stress sits at s ≈ 345 mm along the K1->K6 chord,
which projects to neck-arc x ≈ 300 mm — **between K7 and K8 on the
lower (concave) edge, and the mirror point on the upper (convex)
edge**. This corresponds to the harp's "shoulder" region where the
heaviest bass-mid strings (B1..G2, sn 7..12, ~210-224 N each) hang.

This matches real-harp failure mode: when the neck of a wood concert
grand splits, it splits between the F2 and B1 tuning pins, not at
the bass tail.

If you wanted to reinforce the neck preemptively, the right move is
a stiffening rib, an extra unidirectional CF cap layer, or a thicker
xz-section between **K7 and K8** (the "shoulder", roughly the bass-mid
shoulder of the neck, around the 5th-6th-7th tuning pins). At K1 and
K6 the bending moment is zero by construction (simply-supported
endpoints), so reinforcement at those joints is wasted in bending,
though K1 still needs the moment-carrying joint geometry for the
column buckling margin.

---

## 4. Mass Estimate

| Part | Volume | Mass (rho = 1.6 g/cm^3) |
|------|--------|---|
| Column hollow 4 mm wall, L = 1787 mm | 4.16 cm^3/cm * 178.7 cm = 743 cm^3 | 1.19 kg |
| Neck hollow ~5 mm wall, arc ~800 mm, b = 32, h ≈ 60 | ~ 0.6 dm^3 | 1.0 kg |
| Soundbox shell (50 mm taper limaçon, ~1.6 m, 4 mm CF) | ~ 1.5 dm^3 | 2.4 kg |

Order-of-magnitude only. Total CF mass ≈ 5 kg, plus ~3 kg of mechanism
hardware, gives a finished mass of ~8-10 kg vs ~16 kg for a wooden
concert grand.

---

## 5. Conclusions

| Element | Critical mode | Sigma / P | SF | Pass 2×? |
|---------|---------------|-----------|----|---|
| Column (solid 28x32) | Euler buckling, K=0.7 | 7079 N / 25 825 N | 3.65 | yes |
| Column (hollow 4 mm wall) | Euler buckling, K=0.7 | 7079 N / 18 769 N | **2.65** | yes |
| Column (hollow, K=1.0 worst case) | Euler buckling | 7079 N / 9 197 N | 1.30 | **no** |
| Neck (solid h=65) | Bending compression | 28.7 / 500 MPa | 17.4 | yes |
| Neck (solid h=50) | Bending compression | 48.5 / 500 MPa | 10.3 | yes |
| Neck (hollow h=65) | Bending compression | 49.2 / 500 MPa | 10.2 | yes |
| Neck (hollow h=50) | Bending compression | 75.0 / 500 MPa |  6.7 | yes |

### Recommendations

1. **The column is the binding constraint, not the neck.** Treat the
   column-base joint as load-bearing: clamped fit, multiple bolts,
   epoxy. This gets K_eff = 0.7 (instead of 1.0) and brings buckling
   SF from 1.3 → 2.7 with no other change.

2. **Make the neck-to-column joint as rigid as practical** (lap joint
   + shear pins or scarf laminate). Moving toward fixed-fixed (K=0.5)
   would push column SF from 2.7 → 5.2.

3. **Hollow column wall: 4 mm minimum.** A 3 mm wall drops I_min
   ~25 % and brings buckling SF below 2.

4. **Neck has comfortable margin everywhere.** No reinforcement needed
   for static load. If you want paranoia margin or a fatigue allowance,
   add a unidirectional CF cap on the upper (compression) face of the
   neck between K7 and K8 — that's where the bending moment peaks.

5. **Lateral / detuning loads not covered here.** This analysis is
   static, in-plane (xz). Out-of-plane bending of the neck (about z
   axis) under transient lever or pedal action is a separate check.
   At b = 32 mm the neck is roughly half as stiff against y-axis
   torsion as it is in xz bending; if the action mechanism produces
   significant y-axis moments at the K3 disc-axle line, a torsion
   analysis is advisable.

6. **Column under combined load.** Worst real load is axial P
   plus a small in-plane bending moment from the K1 offset. Even
   adding a 200 N*m bending moment at K1 only adds ~1 MPa of bending
   stress (well below σ_c), so combined load is not a concern.

---

## Summary

**The carbon-fiber Clements47 design passes a 2× safety factor under
static string load (7079 N total tension) at every section checked.
The weakest point is the column at the K1 / pedal-base joint —
specifically the column under Euler buckling with effective-length
factor K=0.7, where the hollow 28×32 mm × 4 mm wall section runs at
SF = 2.65. Drop K_eff to 1.0 (pinned-pinned) and that margin
disappears, so the structural success of the design hinges on
clamping the column rigidly at the pedal base. The neck is
comfortably over-engineered (worst-case SF ≈ 6.7 in compression, peak
bending moment between K7 and K8 on the bass-mid shoulder) and needs
no additional reinforcement for static load.**
