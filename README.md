# Clements47 Harp

A parametric Erard concert harp modeled in FreeCAD 1.1, with a soundbox defined by limacon cross-sections.

## Soundbox Surface Generation

The soundbox is defined by two planar curves and a family of limacon cross-sections swept between them.

### 1. Soundboard Curve (Limacon Origins)

A clamped cubic spline through 11 nodes with vertical takeoff (dx/dt = 0) at both endpoints.

**Nodes (base to neck):**

| # | Point | Description |
|---|-------|-------------|
| 1 | (7.0, -65.6486) | Base — 3" left, 6" below C1 grommet |
| 2 | bass extension | 2" beyond string 1 along tangent |
| 3 | (10.0, -59.6486) | Grommet — string 1 (C1) |
| 4 | (14.943, -51.8946) | Grommet — string 8 |
| 5 | (20.512, -36.3672) | Grommet — string 16 |
| 6 | (25.476, -19.0939) | Grommet — string 24 |
| 7 | (30.076, -10.2416) | Grommet — string 32 |
| 8 | (34.313, -5.2852) | Grommet — string 40 |
| 9 | (37.986, -2.3942) | Grommet — string 47 (G7) |
| 10 | treble extension | 2" beyond string 47 along tangent |
| 11 | (40.3802, 0.0) | Neck — G7 string length right of G7 pin |

**Extension points** are computed from the tangent direction between the first/last two grommet nodes, extended 2" outward.

**Boundary conditions:** `bc_type=((1, 0.0), (1, 0.0))` for x(t), `bc_type=((1, v), (1, v))` for y(t), where v is the average parametric speed. This forces the curve to depart vertically at both the base and neck, ensuring the limacon cross-sections there lie flat (horizontal).

### 2. Cusp Curve (Limacon Cusps)

A clamped cubic spline through 9 nodes, also with vertical takeoff at both endpoints.

The 9 nodes are sampled from 51 cusp points. To compute each cusp point:

1. Evaluate the soundboard curve at the corresponding parameter value
2. Compute the unit tangent **(tx, ty)** and right-hand normal **(ty, -tx)**
3. Interpolate the limacon diameter linearly:
   - **18"** at the base (x = 7.0)
   - **4"** at the neck (x = 40.3802)
4. Compute **b = diameter / 6** (the polar axis length, since a = 2b)
5. Offset: **cusp = origin + b * right_normal**

The 9 nodes are taken at indices [0, 6, 12, 19, 25, 31, 37, 44, 50] of the 51 cusp points.

### 3. Limacon Cross-Sections

Each cross-section is a limacon of Pascal: **r(theta) = a + b * cos(theta)**

Given a pair of corresponding points (origin on soundboard curve, cusp on cusp curve):

- **b** = distance(origin, cusp) = polar axis length
- **a** = 2b (the a = 2b constraint ensures a smooth D-shape with no inner loop)
- **Polar axis direction** = unit vector from origin toward cusp
- **Limacon plane** is perpendicular to the soundboard tangent at that point

Orientation:
- **theta = 0**: points opposite the cusp (toward the strings / bulge side), r = a + b = 3b
- **theta = pi**: points toward the cusp, r = a - b = b

The 3D transformation for each point on the limacon:

```
u = r(theta) * cos(theta)    # component along polar axis (in XY plane)
v = r(theta) * sin(theta)    # component along Z axis

x = origin_x + u * (-polar_dir_x)
y = origin_y + u * (-polar_dir_y)
z = v
```

Where `polar_dir` is the unit vector from origin to cusp (so `-polar_dir` points toward the bulge at theta = 0).

### 4. Limacon Dimensions

| Property | Formula | Base (18" dia) | Neck (4" dia) |
|----------|---------|----------------|---------------|
| Diameter (max width) | 2(a + b) = 6b | 18" | 4" |
| Depth (along polar axis) | 4b | 12" | 2.67" |
| Bulge radius (theta=0) | a + b = 3b | 9" | 2" |
| Cusp distance (theta=pi) | a - b = b | 3" | 0.667" |
| Perpendicular width | 2a = 4b | 12" | 2.67" |
| Aspect ratio (width:depth) | 6b : 4b | 3:2 | 3:2 |

### 5. Lofting

50 limacon cross-sections are sampled evenly along the soundboard curve parameter and lofted into a solid using FreeCAD's `Part::Loft` with `Solid = True, Ruled = False`.

## Files

| File | Description |
|------|-------------|
| `erard_harp.FCMacro` | Stringband sketch (47 strings, keys, soundboard B-spline) |
| `erard_soundbox.FCMacro` | Soundbox generation (limacon cross-sections, loft) |
| `erard_harp.FCStd` | FreeCAD project with stringband sketch |
| `Clements47.FCStd` | FreeCAD project with soundbox |
| `erard%20original%20stringband%20tutorial.dxf` | Source string positions (harpcanada.com) |
| `soundboard_curve.svg` | 2D visualization of soundboard + cusp curves |

## Parameters

| Parameter | Value |
|-----------|-------|
| Strings | 47 (C1 to G7) |
| String lengths | 59.65" (C1) to 2.39" (G7) |
| Base diameter | 18" |
| Neck diameter | 4" |
| Limacon ratio | a = 2b |
| Diameter taper | Linear |
| Extension length | 2" at each end |
| Base point offset | (-3, -6) from C1 grommet |
| Neck point offset | (+2.3942, 0) from G7 pin |
| Soundboard nodes | 11 (clamped cubic spline) |
| Cusp nodes | 9 (clamped cubic spline) |
| Cross-sections | 50 |
| Takeoff angles | 90" (vertical) at base and neck |

## Running

Requires FreeCAD 1.1 with Python 3.11 and scipy:

```bash
# Using extracted AppImage
export LD_LIBRARY_PATH=./squashfs-root/usr/lib:$LD_LIBRARY_PATH
./squashfs-root/usr/bin/freecadcmd -c "exec(open('erard_soundbox.FCMacro').read())"
```
