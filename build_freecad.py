"""build_freecad.py - build clements47.FCStd from canonical clements47.py
geometry and strings.csv positions.

Run via freecadcmd:

    echo "_p='/home/james.clements/projects/clements47/build_freecad.py'; \\
          exec(open(_p).read(), {'__file__': _p, '__name__': '__main__'})" \\
        | freecadcmd

Produces a single FreeCAD document with:
  Chamber       - limacon-cross-section loft along S from SBB to G7g, plus
                  the floor limacon at SF.
  Column        - rectangular prism between (COL_X_LEFT, COL_X_RIGHT) at the
                  bass end of the soundbox.
  Neck          - K1..K9 polyline in xz extruded by NECK_W_Y in y.
  Strings       - 47 cylinders from grommet to Nf_flat using csv positions.

CSV axis mapping: csv.x -> clements.x, csv.y -> clements.z, csv.z -> clements.y.
"""
import csv as _csv
import math
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:
    import FreeCAD
    import Part
    HAS_FC = True
except ImportError:
    FreeCAD = None
    Part = None
    HAS_FC = False

import numpy as np

# clements47.py does `from scipy.optimize import brentq`. Under freecadcmd
# the system scipy is incompatible with the user-installed numpy 2.x and
# the import fails. Inject a stub scipy.optimize module with a vendored
# bisection brentq before importing clements47.
def _vendored_brentq(fn, a, b, tol=1e-9, max_iter=80):
    fa, fb = fn(a), fn(b)
    if fa == 0: return a
    if fb == 0: return b
    if fa * fb > 0: raise ValueError("brentq: f(a) and f(b) have same sign")
    for _ in range(max_iter):
        m = 0.5 * (a + b)
        fm = fn(m)
        if abs(fm) < tol or (b - a) < tol: return m
        if fa * fm < 0: b, fb = m, fm
        else:           a, fa = m, fm
    return 0.5 * (a + b)

if "scipy.optimize" not in sys.modules:
    _scipy_mod = types.ModuleType("scipy")
    _opt_mod = types.ModuleType("scipy.optimize")
    _opt_mod.brentq = _vendored_brentq
    _scipy_mod.optimize = _opt_mod
    sys.modules["scipy"] = _scipy_mod
    sys.modules["scipy.optimize"] = _opt_mod

import clements47 as c

DOC_NAME      = "Clements47"
OUTPUT_FCSTD  = os.path.join(_HERE, "clements47.FCStd")
STRINGS_CSV   = os.path.join(_HERE, "strings.csv")

CHAMBER_N_STATIONS = 32
LIMACON_N_PTS      = 64
COLUMN_W_Y         = 32.0
NECK_W_Y           = 32.0

BASE_DIAM = 500.0
TOP_DIAM  = float(np.linalg.norm(c.K_KNOTS[3] - c.K_KNOTS[5]))

TAN_RAKE = float(math.tan(math.radians(c.RAKE_DEG)))

def rake_xz(p):
    """Apply -7 deg rake to a 2D xz tuple/array."""
    a = np.asarray(p, dtype=float)
    o = a.copy()
    o[..., 0] = a[..., 0] - a[..., 1] * TAN_RAKE
    return o

def grommet_z_on_RAKED_S(raked_x):
    P0r = rake_xz(c.SB_P0); P1r = rake_xz(c.SB_P1)
    P2r = rake_xz(c.SB_P2); P3r = rake_xz(c.SB_P3)
    if raked_x < min(P0r[0], P3r[0]) or raked_x > max(P0r[0], P3r[0]):
        return None
    def fx(t):
        return ((1-t)**3)*P0r[0] + 3*(1-t)**2*t*P1r[0] + \
               3*(1-t)*t**2*P2r[0] + t**3*P3r[0] - raked_x
    from clements47 import brentq as _brentq
    t = _brentq(fx, 0, 1)
    return float((1-t)**3*P0r[1] + 3*(1-t)**2*t*P1r[1] +
                 3*(1-t)*t**2*P2r[1] + t**3*P3r[1])


# ---------------------------------------------------------------------------
# CSV strings
# ---------------------------------------------------------------------------

def load_strings_csv():
    """csv frame: csv.x=treble-axis, csv.y=vertical-from-SBB-plane, csv.z=rake
    offset (applied to -x in clements). Grommet z is locked to grommet_z_on_S
    so strings sit on the canonical soundboard."""
    with open(STRINGS_CSV) as fh:
        clean = "\n".join(ln for ln in fh
                          if not ln.lstrip().startswith("#") and ln.strip())
    reader = _csv.DictReader(clean.splitlines())
    out = []
    for r in reader:
        def f(name):
            v = r.get(name, "").strip()
            return float(v) if v else 0.0
        Ng_x = f("Ng_x_mm"); Ng_y = f("Ng_y_mm"); Ng_z = f("Ng_z_mm")
        # Soundboard un-raked: grommets on canonical SB Bezier at csv.x
        gz = c.grommet_z_on_S(Ng_x)
        if gz is None:
            gz = Ng_y + c.Z_OFFSET
        Nfx = f("Nf_flat_x_mm")
        Nfy = f("Nf_flat_y_mm")
        Nfz_raw = f("Nf_flat_z_mm")
        out.append({
            "sn":      int(r["sn"]),
            "note":    r["note"],
            "OD":      f("OD_mm"),
            "g":       (Ng_x - Ng_z, 0.0, gz),
            "Nf_flat": (Nfx - Nfz_raw, 0.0, gz + (Nfy - Ng_y)),
        })
    return out


# ---------------------------------------------------------------------------
# Chamber geometry helpers (replicated from clements47.write_svg's inline code)
# ---------------------------------------------------------------------------

def _limacon_3d(D_pt, perp_into, diam, n=LIMACON_N_PTS):
    b = diam / 4.0
    a = 2.0 * b
    O_xz = np.asarray(D_pt) + b * np.asarray(perp_into)
    thetas = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    r = a + b * np.cos(thetas)
    u_local = r * np.cos(thetas)
    v_local = r * np.sin(thetas)
    pts = np.zeros((n, 3))
    pts[:, 0] = O_xz[0] + u_local * perp_into[0]
    pts[:, 1] = v_local
    pts[:, 2] = O_xz[1] + u_local * perp_into[1]
    return pts


def Vec(x, y, z):
    return FreeCAD.Vector(float(x), float(y), float(z))


def _make_wire_from_pts(pts):
    vecs = [Vec(p[0], p[1], p[2]) for p in pts]
    vecs.append(vecs[0])
    return Part.makePolygon(vecs)


def build_chamber(doc):
    print(">>> Building chamber loft (SBB -> G7g) ...")
    S = c.compute_S_full()
    sb_bez = S["sb_bezier"]
    sb_ext = S["sb_extension"]
    ts_sb, arc_sb = c.bez_arclen_table(*sb_bez, n=2000)
    ts_ex, arc_ex = c.bez_arclen_table(*sb_ext, n=500)
    L_sb = float(arc_sb[-1])
    L_total = L_sb + float(arc_ex[-1])

    wires = []
    for s in np.linspace(0.0, L_sb, CHAMBER_N_STATIONS):
        ti = float(np.interp(s, arc_sb, ts_sb))
        D = c.bez(*sb_bez, ti)
        t_dir = c.bez_tan(*sb_bez, ti)
        t_dir = t_dir / np.linalg.norm(t_dir)
        perp = np.array([t_dir[1], -t_dir[0]])
        frac = s / L_total
        diam = BASE_DIAM * (1 - frac) + TOP_DIAM * frac
        pts = _limacon_3d(D, perp, diam)
        wires.append(_make_wire_from_pts(pts))

    loft = Part.makeLoft(wires, True, False, False)
    obj = doc.addObject("Part::Feature", "Chamber")
    obj.Shape = loft
    return obj


def build_floor_limacon(doc):
    print(">>> Building floor limacon (D=SF, B=U3 on z=0) ...")
    S = c.compute_S_full()
    U = c.compute_U(S["F"])
    # SF and U3 are at z=0 so rake doesn't change them, but we apply for
    # consistency (rake of (x, 0) leaves x unchanged anyway).
    SF = rake_xz(np.asarray(S["SF"]))
    U3 = rake_xz(np.asarray(U["U3"]))
    diam = float(np.linalg.norm(U3 - SF))
    direction = (U3 - SF) / diam
    pts = _limacon_3d(SF, direction, diam)
    wire = _make_wire_from_pts(pts)
    face = Part.Face(wire)
    obj = doc.addObject("Part::Feature", "FloorLimacon")
    obj.Shape = face
    return obj


def build_column(doc):
    """Column: HOLLOW elliptical CF tube (COL_OD_X x COL_OD_Y, COL_WALL_T
    wall) raked -7 deg in x.  Loft an outer ellipse and an inner ellipse
    each at base and top, then subtract inner from outer."""
    print(">>> Building column (hollow elliptical CF tube) ...")
    F = float(c.compute_S_full()["F"])
    z0 = F
    z1 = float(c.K_KNOTS[0, 1])
    h = z1 - z0
    dx_top = -h * TAN_RAKE

    a_out = c.COL_OD_X / 2.0
    b_out = c.COL_OD_Y / 2.0
    a_in  = a_out - c.COL_WALL_T
    b_in  = b_out - c.COL_WALL_T

    cx0 = (c.COL_X_LEFT + c.COL_X_RIGHT) / 2.0
    cx1 = cx0 + dx_top

    def ell_face(cx, z, a, b):
        """Ellipse wire centered at (cx, 0, z) in the xy plane.  Sample
        parametrically and stitch as a polygon (Part.Ellipse is finicky
        about which axis is "major"; this is bullet-proof)."""
        n = 96
        pts = []
        for i in range(n):
            t = 2.0 * 3.141592653589793 * i / n
            pts.append(Vec(cx + a * np.cos(t), b * np.sin(t), z))
        pts.append(pts[0])
        return Part.makePolygon(pts)

    out_base = ell_face(cx0, z0, a_out, b_out)
    out_top  = ell_face(cx1, z1, a_out, b_out)
    in_base  = ell_face(cx0, z0, a_in,  b_in)
    in_top   = ell_face(cx1, z1, a_in,  b_in)

    outer = Part.makeLoft([out_base, out_top], True, True, False)
    inner = Part.makeLoft([in_base,  in_top],  True, True, False)
    tube = outer.cut(inner)
    obj = doc.addObject("Part::Feature", "Column")
    obj.Shape = tube
    return obj


def build_neck(doc):
    """Neck solid: K-knot polyline (xz) extruded by NECK_W_Y in y.

    build_neck_segments() skips i=3 (K4->K5) and i=4 (K5->K6) because in the
    canonical 2D drawing the K4-K5-K6 path is replaced by the chamber cap
    (limaçon B-locus). For the 3D neck SOLID we need K5 = K_KNOTS[4] = N_KNOTS[6]
    in the polyline so that the chamber-cap edge is part of the neck polygon
    -- otherwise the treble scoop (whose cap chord runs B2=N_KNOTS[6] -> B3=
    N_KNOTS[5] = K6) lies mostly OUTSIDE the neck polygon and the boolean cut
    removes nothing. We splice K5 in between segs[2] (ending at K4) and segs[3]
    (starting at K6).

    Polyline -> Part.makePolygon -> Part.Face -> face.extrude. The result is a
    closed prism solid suitable as the boolean-cut "minuend" for the treble
    scoop.
    """
    print(">>> Building neck (K-knot polyline extruded in y) ...")
    neck_segs = c.build_neck_segments()
    K5 = c.K_KNOTS[4]  # = N_KNOTS[6] = (730.39, 1622.08); the chamber-cap apex
    poly_xz = []
    for seg_idx, seg in enumerate(neck_segs):
        # Splice K5 between K3->K4 (seg index 2) and K6->K7 (seg index 3) so
        # the neck polygon closes around the chamber cap chord.
        if seg_idx == 3:
            poly_xz.append((float(K5[0]), float(K5[1])))
        for t in np.linspace(0.0, 1.0, 30):
            P = c.bez(*seg, t)
            poly_xz.append((float(P[0]), float(P[1])))
    uniq = [poly_xz[0]]
    for p in poly_xz[1:]:
        if abs(p[0] - uniq[-1][0]) > 1e-6 or abs(p[1] - uniq[-1][1]) > 1e-6:
            uniq.append(p)
    uniq.append(uniq[0])
    y_half = NECK_W_Y / 2.0
    vecs = [Vec(x, -y_half, z) for x, z in uniq]
    base = Part.Face(Part.makePolygon(vecs))
    prism = base.extrude(Vec(0, NECK_W_Y, 0))
    obj = doc.addObject("Part::Feature", "Neck")
    obj.Shape = prism
    return obj


def build_pedestal_solid(doc):
    """Solid CF pedestal: lofted between the floor limacon (at
    PEDESTAL_FLOOR_Z) and the chamber-bottom limacon at S'b.

    The bass-tail-front diameter is constant D_KNOT_FLOOR through this region,
    so the cross-section is a uniform limacon whose D-point migrates from the
    floor footprint up to the BTF curve at S'b. We linearly interpolate
    D-point and perp_into across N_STATIONS for a smoothly lofted closed
    solid; minimum acceptable would be just floor + S'b.
    """
    print(">>> Building pedestal solid (floor -> chamber-bottom limacon at S'b) ...")
    S = c.compute_S_full()
    SF = np.asarray(S["SF"], dtype=float)            # xz; SF[1] = 0
    U3 = np.asarray(S["U3"], dtype=float)            # xz; U3[1] = 0
    floor_z = float(c.PEDESTAL_FLOOR_Z)

    # Floor station: D-point at SF translated to floor_z; perp_into points
    # from SF toward U3 (+x).
    D_floor = np.array([SF[0], floor_z], dtype=float)
    diam_floor = float(np.linalg.norm(U3 - SF))
    perp_floor = (U3 - SF) / diam_floor

    # Top station: chamber-bottom limacon at S'b.
    s_top = c._CHAMBER['s_at_Sprime_b']
    D_top, perp_top = c.chamber_axis(s_top)
    D_top = np.asarray(D_top, dtype=float)
    perp_top = np.asarray(perp_top, dtype=float)
    diam_top = float(c.diam_at_s(s_top))

    N_STATIONS = 16
    wires = []
    for i in range(N_STATIONS):
        u = i / float(N_STATIONS - 1)
        D_i = (1.0 - u) * D_floor + u * D_top
        perp_i = (1.0 - u) * perp_floor + u * perp_top
        n = float(np.linalg.norm(perp_i))
        if n > 1e-12:
            perp_i = perp_i / n
        diam_i = (1.0 - u) * diam_floor + u * diam_top
        pts = _limacon_3d(D_i, perp_i, diam_i)
        wires.append(_make_wire_from_pts(pts))

    loft = Part.makeLoft(wires, True, True, False)
    obj = doc.addObject("Part::Feature", "Pedestal")
    obj.Shape = loft
    return obj


def make_scoop_cut_volume(scoop, frustum_extension_mm=15.0):
    """Build the closed 3D solid to subtract for a parabolic scoop cut.

    Two pieces fused into one solid:
      a) Paraboloid bowl: revolve the half-profile (in xz, y=0) about
         axis_unit. Profile traces vertex -> outward parabola to rim edge,
         then closes along the axis.
      b) Frustum extension: a cylinder of radius R, height
         frustum_extension_mm, starting at rim_center and pointing along
         axis_unit (INTO the chamber) so the cut punches through the cap.
    """
    rc_xz = np.asarray(scoop["rim_center_xz"], dtype=float)
    axis_xz = np.asarray(scoop["axis_unit"], dtype=float)
    chord_xz = np.asarray(scoop["rim_chord_dir"], dtype=float)
    R = float(scoop["rim_radius"])
    depth = float(scoop["depth"])
    focal = float(scoop["paraboloid_focal"])

    # Vertex sits depth*(-axis_unit) away from rim center in the xz plane.
    vertex_xz = rc_xz - depth * axis_xz

    # Half-profile in xz (y=0), from vertex outward to the rim edge in
    # +chord_dir. Sample u in [0, R].
    N = 30
    profile_pts = []
    for i in range(N):
        u = R * i / float(N - 1)
        # depth_at_u measured from vertex along +axis_unit
        d = (u * u) / (4.0 * focal)
        p = vertex_xz + d * axis_xz + u * chord_xz
        profile_pts.append((float(p[0]), 0.0, float(p[1])))

    # Rim edge sits at vertex + depth*axis_unit + R*chord_dir (= rim_center
    # offset by R along chord). Close back to vertex along the axis.
    rim_edge_at_axis = vertex_xz + depth * axis_xz   # = rc_xz
    profile_pts.append((float(rim_edge_at_axis[0]), 0.0, float(rim_edge_at_axis[1])))
    # Close back to first point (vertex).
    profile_pts.append(profile_pts[0])

    vecs = [Vec(*p) for p in profile_pts]
    wire = Part.makePolygon(vecs)
    face = Part.Face(wire)

    # Revolution: axis goes through vertex in 3D, direction axis_xz lifted
    # to (axis_x, 0, axis_z).
    vertex_vec = Vec(vertex_xz[0], 0.0, vertex_xz[1])
    axis_vec = Vec(axis_xz[0], 0.0, axis_xz[1])
    bowl = face.revolve(vertex_vec, axis_vec, 360.0)

    # Frustum extension cylinder: radius R, height frustum_extension_mm,
    # starting at rim_center, direction axis_unit.
    rc_vec = Vec(rc_xz[0], 0.0, rc_xz[1])
    cyl = Part.makeCylinder(R, float(frustum_extension_mm), rc_vec, axis_vec)

    fused = bowl.fuse(cyl)
    return fused


def build_strings(doc):
    print(">>> Building strings (47 cylinders from csv) ...")
    strings = load_strings_csv()
    parts = []
    for s in strings:
        gx, gy, gz = s["g"]
        nx, ny, nz = s["Nf_flat"]
        p0 = Vec(gx, gy, gz)
        p1 = Vec(nx, ny, nz)
        d = p1.sub(p0)
        h = d.Length
        if h <= 0:
            continue
        cyl = Part.makeCylinder(s["OD"] / 2.0, h, p0, d)
        parts.append(cyl)
    if parts:
        comp = Part.makeCompound(parts)
        obj = doc.addObject("Part::Feature", "Strings")
        obj.Shape = comp
        return obj
    return None


def make_scoop(doc, scoop, host_obj, label):
    """Subtract the parabolic-scoop volume from `host_obj` and add a new
    Part::Feature with the cut shape.

    The original host_obj is preserved (as Pedestal / Neck) and the new
    feature is added with `label` (e.g. PedestalScooped / NeckScooped) so
    we can compare before/after.
    """
    print(f">>> Cutting scoop volume from {host_obj.Label} -> {label} ...")
    volume = make_scoop_cut_volume(scoop)
    cut_shape = host_obj.Shape.cut(volume)
    obj = doc.addObject("Part::Feature", label)
    obj.Shape = cut_shape
    return obj


def main():
    if not HAS_FC:
        print("FreeCAD not available; nothing to do.", file=sys.stderr)
        return
    doc = FreeCAD.newDocument(DOC_NAME)
    build_chamber(doc)
    build_floor_limacon(doc)
    build_column(doc)
    pedestal = build_pedestal_solid(doc)
    make_scoop(doc, c.compute_scoop(), pedestal, "PedestalScooped")
    neck = build_neck(doc)
    make_scoop(doc, c.compute_scoop_treble(), neck, "NeckScooped")
    build_strings(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FCSTD)
    print(f">>> Saved: {OUTPUT_FCSTD}")
    print(">>> Done.")


if __name__ == "__main__":
    main()
