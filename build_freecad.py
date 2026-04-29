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
    print(">>> Building neck (K-knot polyline extruded in y) ...")
    neck_segs = c.build_neck_segments()
    poly_xz = []
    for seg in neck_segs:
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


def make_scoop(doc, scoop):
    """Stub: place a marker for the future parabolic-scoop boolean cut.

    For now this just drops a thin Part::Sphere at the rim centre as a
    visual placeholder. A future pass should:

      1. Build a Part::Surface of revolution about scoop['axis_unit']
         (passing through scoop['rim_center_xz'] in xz, full +/- y revolve)
         using the parabola z = u**2 / (4 * scoop['paraboloid_focal']) for
         u in [0, scoop['rim_radius']], where u is radial distance from
         the axis and z is depth into the chamber along axis_unit.
      2. Boolean-cut (Part::Cut) that surface (closed by a rim cap) out of
         the Chamber loft to form the dish.

    TODO: wire the boolean cut once the chamber loft is itself a single
    closed solid. Focal length f = R^2 / (4 * depth) =
    {scoop['paraboloid_focal']} mm with R = {scoop['rim_radius']} mm and
    depth = {scoop['depth']} mm.
    """
    rc = scoop["rim_center_xz"]
    # Place a small placeholder sphere at the rim center (xz; y=0).
    sphere = Part.makeSphere(8.0, Vec(float(rc[0]), 0.0, float(rc[1])))
    obj = doc.addObject("Part::Feature", "ScoopMarker")
    obj.Shape = sphere
    return obj


def main():
    if not HAS_FC:
        print("FreeCAD not available; nothing to do.", file=sys.stderr)
        return
    doc = FreeCAD.newDocument(DOC_NAME)
    build_chamber(doc)
    build_floor_limacon(doc)
    build_column(doc)
    build_neck(doc)
    build_strings(doc)
    doc.recompute()
    doc.saveAs(OUTPUT_FCSTD)
    print(f">>> Saved: {OUTPUT_FCSTD}")
    print(">>> Done.")


if __name__ == "__main__":
    main()
