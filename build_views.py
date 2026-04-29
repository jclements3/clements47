#!/usr/bin/env python3
"""build_views.py - orthographic SVG views of the clements47 harp.

Body geometry from clements47.py (SB Bezier, N_KNOTS, COL_X_LEFT/RIGHT,
D_FLOOR, D_AT_St, TOP_DIAM, diam_at_s, chamber_axis, compute_S_full,
compute_U, build_neck_segments). String positions from strings.csv (Ng_*,
Nf_flat/nat/sharp_*).

CSV axis mapping into clements47.py's frame:
    csv.x  -> clements.x  (bass to treble)
    csv.y  -> clements.z  (floor to neck, i.e. height)
    csv.z  -> clements.y  (depth)

Outputs:
    clements47_side.svg         (xz, look +y)
    clements47_top.svg          (xy, look -z)
    clements47_front.svg        (yz, look +x, from bass)
    clements47_rear.svg         (yz, look -x, from treble)
    clements47_sbf.svg          (u, y) face-on to soundboard
    clements47_views.svg        2x2 composite
"""
import argparse
import csv
import os
import sys

import numpy as np

import clements47 as c

HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS_CSV = os.path.join(HERE, "strings.csv")

OUT_SIDE   = os.path.join(HERE, "clements47_side.svg")
OUT_TOP    = os.path.join(HERE, "clements47_top.svg")
OUT_FRONT  = os.path.join(HERE, "clements47_front.svg")
OUT_REAR   = os.path.join(HERE, "clements47_rear.svg")
OUT_SBF    = os.path.join(HERE, "clements47_sbf.svg")
OUT_VIEWS  = os.path.join(HERE, "clements47_views.svg")

N_STATIONS_DRAWN  = 24
N_LIMACON_SAMPLES = 80

# ---------------------------------------------------------------------------
# Erand-style visual conventions (palette and helpers shared across views).
# ---------------------------------------------------------------------------
PAL = {
    "bg":           "#fff",
    "frame":        "#ccc",
    "title":        "#000",
    "soundboard":   "#0a7",       # teal-green
    "chamber_fill": "#e4d4b5",    # warm tan body
    "chamber_edge": "#222",
    "neck":         "#3a2a14",    # dark brown
    "column":       "#666",
    "floor":        "#888",
    "ref_dashed":   "#b8862b",    # gold reference lines
    "string_C":     "#c00000",
    "string_F":     "#1060d0",
    "string_other": "#888",
    "label":        "#222",
}

def string_colour(note):
    if note.startswith("C"):
        return PAL["string_C"]
    if note.startswith("F"):
        return PAL["string_F"]
    return PAL["string_other"]

def string_width(OD_mm):
    """Scale stroke width by OD (Erand convention)."""
    return max(0.5, min(2.7, OD_mm * 1.7))

# At-rest rake: shear x by -z*tan(7 deg). The clements47.py geometry
# constants (SB_P0..P3, N_KNOTS, COL_X_LEFT/RIGHT) are authored in the
# un-raked frame; this transform moves them into the at-rest frame.
# Floor (z=0) and any other z=0 reference are unaffected. csv string
# positions are already at-rest, so strings don't get the additional rake.
TAN_RAKE = float(np.tan(np.radians(c.RAKE_DEG)))

def rake_xz(p):
    """Apply -7 deg rake to a 2D xz point or array (last dim 2)."""
    a = np.asarray(p, dtype=float)
    out = a.copy()
    out[..., 0] = a[..., 0] - a[..., 1] * TAN_RAKE
    return out

def _load_neck_from_edit_svg():
    """Read the user-edited neck path from clements47_neck_edit.svg and
    return its 'd' attribute translated into clements xz coordinates so it
    can be dropped into any view that uses xz mm.

    The neck-edit SVG was authored with x_min, z_max derived from the N_KNOTS
    + buffer + handle bounds (see make_neck_edit_svg.py). Its viewBox is
    "0 0 W H" with svg(x,y) = (x_clements - x_min, z_max - z_clements).
    To convert back: x_clements = svg.x + x_min, z_clements = z_max - svg.y.
    """
    import re
    edit_path = os.path.join(HERE, "clements47_neck_edit.svg")
    if not os.path.exists(edit_path):
        return None
    with open(edit_path) as f:
        s = f.read()
    m = re.search(r'id="neck_path"[^>]*?d="([^"]+)"', s, re.DOTALL)
    if not m:
        m = re.search(r'd="([^"]+)"\s+id="neck_path"', s, re.DOTALL)
    if not m:
        return None
    d_svg = m.group(1)
    # Recover (x_min, z_max) from the same calc as make_neck_edit_svg.py.
    K1_xz = c.N_KNOTS[0]   # N0 = K1 (column outer top)
    # First M command's start is at K1 in svg coords (60, 182.61 in current
    # generator). Parse first absolute MOVE to derive offsets.
    toks = re.findall(r'[A-Za-z]|-?\d+\.?\d*(?:e-?\d+)?', d_svg)
    if not toks or toks[0] not in ('m', 'M'):
        return None
    sx0, sy0 = float(toks[1]), float(toks[2])
    x_min = float(K1_xz[0]) - sx0
    z_max = float(K1_xz[1]) + sy0

    # Re-parse the path, converting every coordinate to clements xz.
    out_d = []
    i = 0; cmd = None; cur = (0.0, 0.0); prev_emitted = None
    def to_cle(x, y):
        return (x + x_min, z_max - y)
    def emit_pt(x, y):
        return f"{x:.2f},{y:.2f}"
    def ensure_cmd(c_emit):
        """Emit absolute command letter only if it's different from the
        last emitted command. (SVG allows multi-coord continuations.)"""
        nonlocal prev_emitted
        if prev_emitted != c_emit:
            out_d.append(c_emit); prev_emitted = c_emit

    while i < len(toks):
        if toks[i].isalpha():
            cmd = toks[i]; i += 1
            if cmd in ('z', 'Z'):
                ensure_cmd('Z'); continue
        if cmd in ('m', 'M'):
            x, y = float(toks[i]), float(toks[i+1]); i += 2
            if cmd == 'm': x += cur[0]; y += cur[1]
            cur = (x, y)
            ensure_cmd('M')
            cx, cy = to_cle(x, y)
            out_d.append(emit_pt(cx, cy))
            cmd = 'L' if cmd == 'M' else 'l'   # implicit lineto follows m/M
        elif cmd in ('c', 'C'):
            c1x, c1y = float(toks[i]),     float(toks[i+1])
            c2x, c2y = float(toks[i+2]),   float(toks[i+3])
            ex,  ey  = float(toks[i+4]),   float(toks[i+5]); i += 6
            if cmd == 'c':
                c1x, c1y = c1x + cur[0], c1y + cur[1]
                c2x, c2y = c2x + cur[0], c2y + cur[1]
                ex,  ey  = ex  + cur[0], ey  + cur[1]
            ensure_cmd('C')
            for x, y in ((c1x, c1y), (c2x, c2y), (ex, ey)):
                cx, cy = to_cle(x, y)
                out_d.append(emit_pt(cx, cy))
            cur = (ex, ey)
        elif cmd in ('l', 'L'):
            x, y = float(toks[i]), float(toks[i+1]); i += 2
            if cmd == 'l': x += cur[0]; y += cur[1]
            cur = (x, y)
            ensure_cmd('L')
            cx, cy = to_cle(x, y)
            out_d.append(emit_pt(cx, cy))
        else:
            i += 1
    return " ".join(out_d)


def grommet_z_on_RAKED_S(raked_x):
    """Find z on the RAKED SB Bezier at the given (raked) x. Returns None
    if raked_x is outside the raked Bezier's domain. Lock for csv grommet
    positions so they sit on S in the at-rest frame."""
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
# Strings: from strings.csv (canonical positions)
# ---------------------------------------------------------------------------

def load_strings():
    """Read strings.csv. csv -> clements with the 7 deg rake AT-REST in xz
    (visible in the side view):
        clements.x = csv.x - csv.z        (rake offset along -x)
        clements.y = 0                    (strings live in xz plane)
        clements.z = grommet_z_on_S(csv.x) for grommets, with a vertical
                     delta added for Nf_*: gz + (csv.y_Nf - csv.y_Ng)
    """
    with open(STRINGS_CSV) as fh:
        clean = "\n".join(ln for ln in fh
                          if not ln.lstrip().startswith("#") and ln.strip())
    reader = csv.DictReader(clean.splitlines())
    out = []
    for r in reader:
        def f(name):
            v = r.get(name, "").strip()
            return float(v) if v else 0.0

        Ng_x = f("Ng_x_mm"); Ng_y = f("Ng_y_mm"); Ng_z = f("Ng_z_mm")
        gz = c.grommet_z_on_S(Ng_x)
        if gz is None:
            gz = Ng_y + c.Z_OFFSET
        gx = Ng_x - Ng_z
        g  = np.array([gx, 0.0, gz])

        def disc(prefix):
            dx = f(prefix + "_x_mm")
            dy = f(prefix + "_y_mm")
            dz = f(prefix + "_z_mm")
            return np.array([dx - dz, 0.0, gz + (dy - Ng_y)])

        out.append({
            "sn":      int(r["sn"]),
            "note":    r["note"],
            "OD":      f("OD_mm"),
            "L_flat":  f("L_flat_mm"),
            "L_nat":   f("L_nat_mm"),
            "L_sharp": f("L_sharp_mm"),
            "f_nat":   f("f_nat_Hz"),
            "g":       g,
            "Nf_flat": disc("Nf_flat"),
            "Nf_nat":  disc("Nf_nat"),
            "Nf_sharp":disc("Nf_sharp"),
        })
    return out


# ---------------------------------------------------------------------------
# Chamber 3D: limacon sweep along the FULL chamber path
# (SF -> bass-tail -> SBB -> G7g -> K6), plus floor limacon at SF.
# Diameter profile and chamber axis come from clements47.diam_at_s and
# clements47.chamber_axis (single source of truth).
# ---------------------------------------------------------------------------

# Re-exported diameter constants (mirror clements47 module-level values).
D_FLOOR  = c.D_FLOOR
D_AT_St  = c.D_AT_St
TOP_DIAM = c.TOP_DIAM
# Backwards-compat aliases for any external readers expecting BASE_DIAM.
BASE_DIAM = D_FLOOR


def _limacon_3d(D_pt, perp_into, diam, n=N_LIMACON_SAMPLES):
    """Return (n, 3) world xyz of limacon cross-section perpendicular to S
    at D_pt. Convention r=a+b*cos(theta), a=2b, b=diam/4. D = flat side
    (theta=pi); B = round bulge (theta=0) at distance diam from D along
    +perp_into. Cross-section plane: u-axis = perp_into (in xz),
    v-axis = +y world. Origin O = D + b*perp_into."""
    b = diam / 4.0
    a = 2.0 * b
    O_xz = D_pt + b * perp_into
    thetas = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    r = a + b * np.cos(thetas)
    u_local = r * np.cos(thetas)
    v_local = r * np.sin(thetas)
    pts = np.zeros((n, 3))
    pts[:, 0] = O_xz[0] + u_local * perp_into[0]
    pts[:, 1] = v_local
    pts[:, 2] = O_xz[1] + u_local * perp_into[1]
    return pts


def chamber_stations_to_g7g(n=N_STATIONS_DRAWN, s_lo=None, s_hi=None):
    """Stations along the chamber path with limacon cross-sections in 3D.

    By default, sweeps the FULL path: s in [s_at_SF, s_total]. Pass s_lo /
    s_hi to restrict (e.g. s_lo=s_at_SBB to draw only the soundboard
    portion). Diameter is from clements47.diam_at_s; axis from
    clements47.chamber_axis. Note: the function name is kept for backwards
    compatibility -- it now spans the full chamber, not just SBB->G7g.
    """
    if s_lo is None:
        s_lo = c.s_at_SF
    if s_hi is None:
        # Chamber sweep stops at Ht (= s_at_St). Above Ht is solid CF
        # (elbow + neck), no chamber limaçons drawn.
        s_hi = c._CHAMBER['s_at_St']
    out = []
    for s in np.linspace(s_lo, s_hi, n):
        D, perp = c.chamber_axis(s)
        diam = c.diam_at_s(s)
        pts = _limacon_3d(D, perp, diam)
        out.append({"s": s, "D": D, "perp": perp, "diam": diam, "pts3d": pts})
    return out


def floor_limacon_3d(n=N_LIMACON_SAMPLES):
    """Horizontal limacon on the floor: D=SF, B=U3 in xz (both at z=0),
    diameter = U_FLOOR_LEN. Sweep around its D-B axis with y-extent."""
    S = c.compute_S_full()
    U = c.compute_U(S["F"])
    SF = S["SF"]
    U3 = U["U3"]
    diam = float(np.linalg.norm(U3 - SF))
    direction_xz = (U3 - SF) / diam        # unit, in xz, on floor (z=0)
    return _limacon_3d(SF, direction_xz, diam, n=n)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def bez_to_d(P0, P1, P2, P3):
    return (f"M {P0[0]:.2f} {P0[1]:.2f} "
            f"C {P1[0]:.2f} {P1[1]:.2f}, {P2[0]:.2f} {P2[1]:.2f}, "
            f"{P3[0]:.2f} {P3[1]:.2f}")


def polyline_d(pts2d):
    if len(pts2d) == 0:
        return ""
    head = f"M {pts2d[0][0]:.2f} {pts2d[0][1]:.2f}"
    tail = " ".join(f"L {p[0]:.2f} {p[1]:.2f}" for p in pts2d[1:])
    return head + " " + tail


def svg_open(viewbox, width_px=900, font_size=12):
    x0, y0, w, h = viewbox
    height_px = max(1, int(width_px * h / w))
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}" '
        f'width="{width_px}" height="{height_px}" '
        f'font-family="sans-serif" font-size="{font_size}">',
    ]


# ---------------------------------------------------------------------------
# Side view (xz plane)
# ---------------------------------------------------------------------------

def side_view_content(strings):
    """Side view (xz, look +y). Body geometry (SB Bezier, N_KNOTS, chamber)
    drawn in the canonical un-raked frame; only the column and strings get
    the at-rest -7 deg rake (the column as a parallelogram with its top in
    -x, the strings as csv-encoded -x rake offsets)."""
    S = c.compute_S_full()
    U = c.compute_U(S["F"])
    neck_segs = c.build_neck_segments()
    F = S["F"]

    # Span the FULL chamber path (SF -> bass-tail -> SBB -> SB -> G7g -> SB
    # extension -> K6) so the side-view polygon traces the complete chamber
    # outline (bass-tail visible, plus the constant-diameter section near
    # SBB that the new diameter profile makes wider).
    sts = chamber_stations_to_g7g(N_STATIONS_DRAWN * 2)

    elems = []

    x_vals = ([k[0] for k in c.N_KNOTS] +
              [c.COL_X_LEFT, c.COL_X_RIGHT, S["SF"][0], U["U3"][0],
               S["sb_bezier"][0][0], S["sb_bezier"][3][0]] +
              [st["D"][0] + st["diam"] * st["perp"][0] for st in sts] +
              [s["g"][0] for s in strings] +
              [s["Nf_flat"][0] for s in strings])
    z_vals = ([k[1] for k in c.N_KNOTS] + [F, S["sb_bezier"][0][1],
              S["sb_bezier"][3][1]] +
              [s["g"][2] for s in strings] +
              [s["Nf_flat"][2] for s in strings])
    x_min = min(x_vals) - 30
    x_max = max(x_vals) + 30
    z_min = min(F, min(z_vals)) - 50
    z_max = max(z_vals) + 50

    # Floor (dashed)
    elems.append(f'<line x1="{x_min:.1f}" y1="0" x2="{x_max:.1f}" y2="0" '
                 f'stroke="{PAL["floor"]}" stroke-width="0.6" '
                 f'stroke-dasharray="4,3" opacity="0.7"/>')

    # PEDESTAL: 4-corner wedge with two parallel ARCS (left & right) and
    # two LIMAÇON cross-section lines (top & bottom). The scoop (parabolic
    # dish) is a VOID inside this pedestal solid -- still rendered.
    # Old S3, S2 labels at the chamber-junction limaçon are now both "B"
    # since they're part of the soundbox bass end.
    # Four corners:
    #   P0 (lower-left)  - bottom of pedestal on chamber-axis side
    #   P1 (lower-right) - bottom of pedestal on back-wall side
    #   P2 = old S3 - chamber axis at S'b (upper-left, also labeled B)
    #   P3 = old S2 - back wall at S'b (upper-right, also labeled B)
    # Sides:
    #   P0 -> P1: line (lower limaçon diameter)
    #   P1 -> P3: arc (right side, parallel to left arc)
    #   P3 -> P2: line (upper limaçon diameter, = soundbox bass boundary)
    #   P2 -> P0: arc (left side, tangent to BTF at P2)
    PED_TOP = c.PEDESTAL_TOP_Z
    PED_BOT = c.PEDESTAL_FLOOR_Z
    PED_LX  = c.PEDESTAL_LEFT_X
    # D1g and C1g
    _c1_str = next((s for s in strings if s["note"].strip() == "C1"), None)
    _d1_str = next((s for s in strings if s["note"].strip() == "D1"), None)
    _C1g = np.array([_c1_str["g"][0], _c1_str["g"][2]])
    _D1g = np.array([_d1_str["g"][0], _d1_str["g"][2]])
    _line_dir = (_C1g - _D1g) / np.linalg.norm(_C1g - _D1g)   # D1g -> C1g
    # P2 on the D1g->C1g line at z = PED_TOP. line(t) = D1g + t * line_dir.
    # z(t) = D1g.z + t*line_dir.z = PED_TOP -> t = (PED_TOP - D1g.z)/line_dir.z
    _t_P2 = (PED_TOP - _D1g[1]) / _line_dir[1]
    # Pedestal corners: P0, P1, S2, S3 (P2 removed). Two ARCS:
    #   left arc (S3 -> P0) tangent to BTF at S3 -- merges into soundbox
    #   right arc (P1 -> S2) tangent to chamber back wall at S2 --
    #     merges into chamber back wall on the right
    # Plus two straight sides: P0-P1 (floor) and S2-S3 (top, = soundbox
    # bass boundary; the closing line of the body polygon below).
    # P0 is now ON the D1g->C1g line, at the floor level (z = PED_BOT after
    # the slide). The line equation: line(t) = C1g + t * (D1g - C1g) / |..|.
    _slide_dir_up = (_D1g - _C1g) / np.linalg.norm(_D1g - _C1g)
    _slide_vec = c.PEDESTAL_SLIDE_T * _slide_dir_up
    _ped_floor_z = float((np.array([0.0, PED_BOT]) + _slide_vec)[1])    # post-slide floor z
    # Solve for t such that C1g.z + t*line_dir.z = _ped_floor_z
    _t_floor = (_ped_floor_z - _C1g[1]) / _slide_dir_up[1]
    P0_arr = _C1g + _t_floor * _slide_dir_up
    P1_arr = np.array([P0_arr[0] + c.FLOOR_BASE, P0_arr[1]])
    # S3 = chamber-axis at S'b
    _Dp_Spb, _p_Spb = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
    S3_arr = np.array(_Dp_Spb)
    # S2 = chamber back wall at S'b (= Sb + diam*perp_into)
    _diam_Spb = c.diam_at_s(c._CHAMBER['s_at_Sprime_b'])
    S2_arr = _Dp_Spb + _diam_Spb * _p_Spb
    # BTF tangent at S'b (used for both arc tangencies; chamber tangent
    # at S'b ~= back-wall tangent there for low curvature).
    _btf_tan = np.array([-_p_Spb[1], _p_Spb[0]])
    if _btf_tan[1] < 0: _btf_tan = -_btf_tan
    _btf_tan = _btf_tan / np.linalg.norm(_btf_tan)
    # P0 is now on the D1g->C1g line; the LEFT side of the pedestal is a
    # straight line from P0 up to C1g. P2 is no longer a separate vertex
    # (the arc is gone). Pedestal is now a triangle: P0, P1, C1g.
    # Fillet helper: given corner point V and the two unit vectors of the
    # edges leaving V (e_in, e_out), return the two tangent points and the
    # arc samples replacing the corner with an arc of radius R.
    def _fillet(V, e_in, e_out, R, n_samples=20):
        # Half-angle between edges (interior angle).
        cos_a = float(e_in @ e_out)
        cos_a = max(-1.0, min(1.0, cos_a))
        ang = np.arccos(cos_a)
        half = ang / 2.0
        d = R / np.tan(half)            # tangent-point offset from V
        T_in  = V + d * e_in            # tangent point on incoming edge
        T_out = V + d * e_out           # tangent point on outgoing edge
        # Arc center on the bisector, inside the corner.
        bis = (e_in + e_out)
        bis = bis / np.linalg.norm(bis)
        C = V + (R / np.sin(half)) * bis
        # Sweep from T_in to T_out around C.
        a_in  = np.arctan2(T_in[1] - C[1],  T_in[0] - C[0])
        a_out = np.arctan2(T_out[1] - C[1], T_out[0] - C[0])
        sw = a_out - a_in
        while sw >  np.pi: sw -= 2*np.pi
        while sw < -np.pi: sw += 2*np.pi
        thetas = np.linspace(a_in, a_in + sw, n_samples)
        return T_in, T_out, [C + R * np.array([np.cos(t), np.sin(t)]) for t in thetas]

    # NEW pedestal: 4-corner wedge bounded by the two concentric arcs (left
    # outer arc, right inner arc), floor at bottom, and B1-B2 edge at top.
    # P0 = outer-arc floor end. P1 unchanged. P2 = B2. P3 = B1.
    # B1 = chamber axis at S'b; B2 = chamber back wall at S'b.
    _Dp_lim_ped, _p_lim_ped = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
    _diam_lim_ped = c.diam_at_s(c._CHAMBER['s_at_Sprime_b'])
    _B1_ped = np.array(_Dp_lim_ped)
    _B2_ped = _B1_ped + _diam_lim_ped * _p_lim_ped
    # ARC_CENTER = intersection of B1-B2 line (extended) with floor.
    _floor_z_ped = float(P0_arr[1])
    _t_AC = (_floor_z_ped - _B1_ped[1]) / (_B2_ped[1] - _B1_ped[1])
    _AC_for_poly = _B1_ped + _t_AC * (_B2_ped - _B1_ped)
    _R_outer_poly = float(np.linalg.norm(_B1_ped - _AC_for_poly))
    _R_inner_poly = float(np.linalg.norm(_B2_ped - _AC_for_poly))
    # New P0 = outer-arc landing on floor (at angle pi from ARC_CENTER).
    P0_arr = np.array([_AC_for_poly[0] - _R_outer_poly, _floor_z_ped])
    # P1 = inner-arc landing on floor (also at angle pi).
    P1_arr = np.array([_AC_for_poly[0] - _R_inner_poly, _floor_z_ped])
    # P2 = B2 (upper-right). P3 = B1 (upper-left).
    P2_arr = np.array(_B2_ped)
    P3_arr = np.array(_B1_ped)
    # Sample arcs (both go from floor angle pi up to B-point angle, CW).
    _aB1_p = np.arctan2(_B1_ped[1] - _AC_for_poly[1], _B1_ped[0] - _AC_for_poly[0])
    _aB2_p = np.arctan2(_B2_ped[1] - _AC_for_poly[1], _B2_ped[0] - _AC_for_poly[0])
    _outer_arc = [_AC_for_poly + _R_outer_poly * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(np.pi, _aB1_p, 60)]   # P0 -> P3
    _inner_arc = [_AC_for_poly + _R_inner_poly * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(np.pi, _aB2_p, 60)]   # P1 -> P2
    # Polygon CCW: P0 -> P1 (floor, left to right) -> inner arc P1 -> P2
    # -> top edge P2 -> P3 (B1-B2 line) -> outer arc reversed P3 -> P0.
    ped_pts = ([P0_arr, P1_arr]
               + _inner_arc[1:-1] + [P2_arr, P3_arr]
               + _outer_arc[::-1][1:-1])
    # B label points at C1g (the only chamber-junction corner now).
    S3_arr = np.array(_C1g)
    S2_arr = np.array(_C1g)
    ped_d = "M " + " L ".join(f"{p[0]:.2f} {p[1]:.2f}" for p in ped_pts) + " Z"
    elems.append(f'<path d="{ped_d}" fill="#a000a0" fill-opacity="0.18" '
                 f'stroke="#a000a0" stroke-width="1.5" '
                 f'stroke-linejoin="round"/>')
    # Label the four pedestal wedge corners. P2/P3 are at the soundbox
    # bass-end limacon (same physical points as B1/B0); offset labels
    # downward into the pedestal interior to avoid colliding with B0/B1.
    for label, pt, dx, dy in [("P0", P0_arr, -18,  14),
                              ("P1", P1_arr,   6,   4),
                              ("P2", P2_arr,   8,  16),
                              ("P3", P3_arr, -22,  16)]:
        elems.append(
            f'<circle cx="{pt[0]:.2f}" cy="{pt[1]:.2f}" '
            f'r="2.0" fill="#3a2a14"/>')
        elems.append(
            f'<text transform="matrix(1,0,0,-1,{pt[0]+dx:.1f},{pt[1]+dy:.1f})" '
            f'font-family="sans-serif" font-size="11" font-weight="700" '
            f'fill="#3a2a14">{label}</text>')

    # (P1-to-N0 arc removed -- it was sweeping the long way around its very
    #  distant center and cluttering the side view.)

    # Soundbox front side: chamber AXIS from B0 (s_at_Sprime_b) up to SBB
    # (s_at_SBB). This stays inside the chamber outline (NOT the BTF curve
    # which extends below B0 to the floor). Then SB Bezier from SBB to G7g.
    _s_b1 = c._CHAMBER['s_at_Sprime_b']
    _s_b2 = c._CHAMBER['s_at_St']
    _s_sbb = c._CHAMBER['s_at_SBB']
    front_lo = [c.chamber_axis(s)[0] for s in np.linspace(_s_b1, _s_sbb, 12)]
    sb_top  = [c.bez(*S["sb_bezier"],       t)
               for t in np.linspace(0.0, 1.0, 80)]   # SBB -> G7g
    # SB tangent extension G7g -> St (= S't), the chamber's TOP CAP point.
    G7g = S["sb_bezier"][3]
    tan1 = c.bez_tan(*S["sb_bezier"], 1.0); tan1_unit = tan1 / np.linalg.norm(tan1)
    St_phantom = G7g + 2.0 * c.AIR_GAP * tan1_unit
    # Back-wall stations between B1 (s_at_Sprime_b) and B2 (s_at_St).
    Bs_back = []
    for st in sts:
        if _s_b1 <= st["s"] <= _s_b2:
            Bs_back.append(st["D"] + st["diam"] * st["perp"])
    # Bracket with exact B1 and B2 so the soundbox closes cleanly at the
    # bass-end limaçon line (B0-B1) and the treble-end cap line (B3-B2).
    _B1_pt = c.chamber_axis(_s_b1)[0] + c.diam_at_s(_s_b1) * c.chamber_axis(_s_b1)[1]
    _B2_pt = c.chamber_axis(_s_b2)[0] + c.diam_at_s(_s_b2) * c.chamber_axis(_s_b2)[1]
    Bs_back = [_B1_pt] + Bs_back + [_B2_pt]
    # Body polygon: B0 -> chamber-axis -> SBB -> SB Bezier -> G7g
    # -> St_phantom (B3) -> back-wall stations -> B1 -> close to B0.
    body_pts = front_lo + sb_top[1:] + [St_phantom] + Bs_back[::-1]
    body_d = "M " + " L ".join(f"{p[0]:.2f} {p[1]:.2f}" for p in body_pts) + " Z"
    # Soundbox: green border (was the standalone soundboard line) now traces
    # the entire B0 -> SBB -> G7g -> B3 -> back wall -> B0 perimeter, with a
    # light-green fill tint for shading.
    elems.append(f'<path d="{body_d}" fill="{PAL["soundboard"]}" '
                 f'fill-opacity="0.18" '
                 f'stroke="{PAL["soundboard"]}" stroke-width="1.5" '
                 f'stroke-linejoin="round"/>')

    # Sound ports:
    #   s=750, 950, 1150: small trumpet-flared CF ports for fine acoustic
    #         tuning. Throat r=5, mouth r=8, 35 mm exponential flare.
    # (Bass-end access oval at s=400 removed -- it rendered as a stray
    #  empty circle inside the soundbox.)
    SH_THROAT_R = 5.0
    SH_MOUTH_R  = 8.0
    SH_FLARE_LEN = 35.0
    # Small trumpet ports
    sh_stations = [750.0, 950.0, 1150.0]   # arclength s in mm
    for s_sh in sh_stations:
        D_sh, p_sh = c.chamber_axis(s_sh)
        diam_sh = c.diam_at_s(s_sh)
        B_sh = D_sh + diam_sh * p_sh   # back-wall point in xz
        cx, cz = float(B_sh[0]), float(B_sh[1])
        # Outer (mouth) circle
        elems.append(
            f'<circle cx="{cx:.2f}" cy="{cz:.2f}" r="{SH_MOUTH_R:.2f}" '
            f'fill="#fff" fill-opacity="0.85" stroke="#664400" '
            f'stroke-width="0.9"/>')
        # Inner (throat) circle - dashed to indicate it's behind the mouth
        elems.append(
            f'<circle cx="{cx:.2f}" cy="{cz:.2f}" r="{SH_THROAT_R:.2f}" '
            f'fill="none" stroke="#664400" stroke-width="0.6" '
            f'stroke-dasharray="2,2" opacity="0.85"/>')
        # Crosshair
        ext = SH_MOUTH_R + 4.0
        elems.append(
            f'<line x1="{cx-ext:.2f}" y1="{cz:.2f}" '
            f'x2="{cx+ext:.2f}" y2="{cz:.2f}" '
            f'stroke="#664400" stroke-width="0.5" '
            f'stroke-dasharray="3,2" opacity="0.85"/>')
        elems.append(
            f'<line x1="{cx:.2f}" y1="{cz-ext:.2f}" '
            f'x2="{cx:.2f}" y2="{cz+ext:.2f}" '
            f'stroke="#664400" stroke-width="0.5" '
            f'stroke-dasharray="3,2" opacity="0.85"/>')

    # (Trumpet flare cross-section drafting inset removed -- it was drawn
    #  outside the harp body and inflated index.html's auto-fit viewBox,
    #  making it appear as a "huge empty" shape in the side view.)
    # SB extension is now part of the solid CF NECK (above the G7g chamber
    # cap), not the chamber. It is no longer drawn as a separate dotted
    # green line; the user-edited neck path covers that region.
    # (Old BTF Bezier separate stroke removed -- the soundbox front now
    #  uses chamber axis from B0 to SBB; BTF below B0 was visual debris.)

    # (Floor limacon gold reference and chamber station crossbars removed --
    # they were construction debris cluttering the soundbox/pedestal area.)

    # Neck path: computed directly from N_KNOTS so changes to N positions
    # propagate to the drawn shape. N6 (= K5 = U't) is the top of the back
    # wall; the path passes through it on its way to N5 (= K6 = St). N6's
    # tangent is ALIGNED with the U-path tangent at U't so the chamber
    # back-wall flows smoothly into the elbow without a kink.
    N = c.N_KNOTS
    # CW path order through the knots (preserved from the legacy K-naming):
    # N0 (K1), N9 (K2), N8 (K3), N7 (K4), N6 (K5=Ut), N5 (K6=St), N4 (K7),
    # N3 (K8), N2 (K9), N1 (K10). The N-array stores them CCW; we re-index
    # to walk the original CW order. This keeps the rendered SVG path
    # byte-for-byte identical with the pre-refactor output.
    seq_idx = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]   # N indices, CW order
    seq = [N[i] for i in seq_idx] + [N[seq_idx[0]]]   # close back to N0
    nseq = len(seq)

    def _u(v):
        n = float(np.linalg.norm(v))
        return v / n if n > 0 else v

    # N6 (K5) = U't, N5 (K6) = S't. The chamber TOP CAP runs S't -> U't
    # (the red Ht diameter line). N5 and N6 both have HANDLES ALIGNED WITH
    # THIS LINE, so the neck passes through both knots tangent to the Ht
    # line.
    Dp_g, p_g = c.chamber_axis(c._CHAMBER['s_at_G7g'])
    Ut_pt = Dp_g + c.diam_at_s(c._CHAMBER['s_at_G7g']) * p_g
    _tan1 = c.bez_tan(*S["sb_bezier"], 1.0)
    _tan1_u = _tan1 / np.linalg.norm(_tan1)
    St_pt    = c.SB_P3 + 2.0 * c.AIR_GAP * _tan1_u                # = N5 (K6)
    Upt_pt   = Ut_pt   + 2.0 * c.AIR_GAP * _tan1_u                # = N6 (K5)
    Ht_dir   = _u(Upt_pt - St_pt)        # S't -> U't direction (Ht line)
    # N6 (= K5) incoming/outgoing handles along Ht direction. Path: N7 (K4)
    # -> N6 (K5) -> N5 (K6). N6 sits at U't, U't is the +Ht_dir end of the
    # Ht line; tangent along the Ht line means handles point along (+/- Ht_dir).
    Upath_tan_at_K5 = -Ht_dir            # outgoing toward S't side (= toward N5/K6 eventually)

    # Sequence-index aliases — positions in `seq`, NOT positions in N_KNOTS.
    # The CW seq order is [N0, N9, N8, N7, N6, N5, N4, N3, N2, N1, N0]:
    #   K5 (= N6) lives at seq[4]
    #   K6 (= N5) lives at seq[5]
    #   K9 (= N2) lives at seq[8]
    #   K10 (= N1) lives at seq[9]
    # Tangent at each interior knot = chord through neighbours (CR style),
    # with overrides:
    #   K5 -> U-path tangent at U't (chamber back-wall continuity)
    #   K9, K10, K1: handles for the column-edge segments must be ALONG
    #       those column edges so the column sides render as STRAIGHT lines:
    #         K9 outgoing  || (K10 - K9)   along column LEFT face
    #         K10 incoming || (K10 - K9)   "  "
    #         K10 outgoing || (K1  - K10)  along column TOP face
    #         K1  incoming || (K1  - K10)  "  "
    K5_idx = 4                   # seq position of K5 (= N6 = Ut)
    K6_idx = 5                   # seq position of K6 (= N5 = St)
    K9_idx = nseq - 3            # seq position of K9 (= N2 = seq[8] when nseq=11)
    K10_idx = nseq - 2           # seq position of K10 (= N1 = seq[9])
    K1_close_idx = nseq - 1      # seq position of closing K1 (= N0 = seq[10])

    # Compute the two column-edge tangent overrides.
    col_left_dir = _u(np.array(seq[K10_idx]) - np.array(seq[K9_idx]))   # K9 -> K10
    col_top_dir  = _u(np.array(seq[K1_close_idx]) - np.array(seq[K10_idx]))  # K10 -> K1
    tangents = [None] * nseq
    for i in range(1, nseq - 1):
        if i == K5_idx:
            tangents[i] = Upath_tan_at_K5      # along Ht line (-Ht_dir)
        elif i == K6_idx:
            tangents[i] = -Ht_dir              # also along Ht line, same orientation as K5
        elif i == K9_idx:
            # Incoming handle at N2 (= K9): perpendicular to the column
            # inner face, pointing AWAY from the neck loop (left/-x side).
            # P2 of segment 7 (N3 -> N2) = N2 - h * tangents[K9_idx], so
            # tangents[K9_idx] is the curve's tangent direction AT N2.
            # For perpendicular-to-column-left arrival, use rotated
            # col_left_dir by -90 deg, then flip sign so it points left.
            _col_perp_cw = np.array([col_left_dir[1], -col_left_dir[0]])
            tangents[i] = -_col_perp_cw            # left-down perpendicular to column
        elif i == K10_idx:
            # straight-line corner: incoming and outgoing both along their
            # column edges. We use the BISECTOR for a single tangent value
            # but emit the segment with overridden P1/P2 below.
            tangents[i] = col_top_dir
        else:
            tangents[i] = _u(np.array(seq[i+1]) - np.array(seq[i-1]))
    # K1's outgoing handle is INLINE WITH THE COLUMN (continuing the
    # column LEFT face direction K9 -> K1 past K1, i.e. the column's
    # rake direction). Handle length is set to reach the C1 pin buffer
    # top (so the arc sweeps over the C1 region toward K2).
    _c1 = next((s for s in strings if s["note"].strip() == "C1"), None)
    if _c1 is not None:
        _c1_g = np.array([_c1["g"][0],       _c1["g"][2]])
        _c1_Nf = np.array([_c1["Nf_flat"][0], _c1["Nf_flat"][2]])
        _csd = (_c1_Nf - _c1_g) / np.linalg.norm(_c1_Nf - _c1_g)
        _cang = np.radians(12.01)
        _cpd = np.array([_csd[0]*np.cos(-_cang) - _csd[1]*np.sin(-_cang),
                         _csd[0]*np.sin(-_cang) + _csd[1]*np.cos(-_cang)])
        _c1_pin_top = _c1_Nf + 38.96 * _cpd
        K1_out_handle_len = float(np.linalg.norm(_c1_pin_top - N[0]))
    else:
        K1_out_handle_len = None
    # K1 outgoing handle: STRAIGHT UP, continuing the column outer (left)
    # face upward past K1 (= +z direction). Inline with the column going up.
    tangents[0] = np.array([0.0, 1.0])
    tangents[K1_close_idx] = col_top_dir
    tangents[-1] = col_top_dir

    # Build cubic Bezier segments. Special cases:
    #   K9->K10, K10->K1 : straight-line column edges (P1, P2 along chord).
    #   K4->K5           : K5 is a CORNER. The incoming handle at K5 points
    #                       UP-AND-RIGHT along the U-path (+tan1_unit), so
    #                       P2 = K5 + h * tan1_unit. Outgoing handle of K5
    #                       (in the next segment K5->K6) uses the Ht-line
    #                       tangent toward K6.
    neck_d_parts = [f'M {seq[0][0]:.2f},{seq[0][1]:.2f}']
    K4_idx = 3
    for i in range(nseq - 1):
        P0 = np.array(seq[i]); P3 = np.array(seq[i+1])
        chord_vec = P3 - P0; chord = float(np.linalg.norm(chord_vec))
        h_out = chord / 3.0; h_in = chord / 3.0
        is_col_edge = (i == K9_idx or i == K10_idx)
        if is_col_edge:
            # Both column-edge segments STRAIGHT (chord-aligned handles).
            chord_unit = chord_vec / chord if chord > 0 else np.array([1.0, 0.0])
            P1 = P0 + h_out * chord_unit
            P2 = P3 - h_in  * chord_unit
        elif i == K4_idx:
            # K4 -> K5 : default P1 from K4 tangent; P2 (K5 incoming handle)
            # points UP-AND-RIGHT along +tan1_unit (U-path direction at Ut).
            # Handle length scaled to reach the G7 pin buffer top region so
            # the arc passes smoothly past it.
            P1 = P0 + h_out * tangents[i]
            # Find G7 pin buffer top to set the handle length.
            _g7 = next((s for s in strings if s["note"].strip() == "G7"), None)
            if _g7 is not None:
                _Nf = np.array([_g7["Nf_flat"][0], _g7["Nf_flat"][2]])
                _gx = np.array([_g7["g"][0],       _g7["g"][2]])
                _sd = (_Nf - _gx) / np.linalg.norm(_Nf - _gx)
                _ang = np.radians(12.0)
                _pd = np.array([_sd[0]*np.cos(-_ang) - _sd[1]*np.sin(-_ang),
                                _sd[0]*np.sin(-_ang) + _sd[1]*np.cos(-_ang)])
                _pin_top = _Nf + 38.96 * _pd
                _h_K5_in = float(np.linalg.norm(_pin_top - P3))
            else:
                _h_K5_in = h_in
            P2 = P3 + _h_K5_in * _tan1_u   # corner: handle along +tan1_unit, length to G7 pin buffer top
        else:
            # Override K1->K2 outgoing handle length so the handle reaches
            # the C1 pin buffer top exactly.
            if i == 0 and K1_out_handle_len is not None:
                P1 = P0 + K1_out_handle_len * tangents[i]
            else:
                P1 = P0 + h_out * tangents[i]
            P2 = P3 - h_in  * tangents[i+1]
        neck_d_parts.append(f' C {P1[0]:.2f},{P1[1]:.2f} {P2[0]:.2f},{P2[1]:.2f} {P3[0]:.2f},{P3[1]:.2f}')
    neck_d_parts.append(' Z')
    neck_d_kk = ''.join(neck_d_parts)
    # PRIMARY SOURCE for the neck path: edit_paths.svg (hand-edited).
    # If unavailable, fall back to the computed Catmull-Rom neck above.
    _neck_d_user = None
    try:
        import re as _re_n
        _ep = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "edit_paths.svg")
        with open(_ep) as _ef:
            _et = _ef.read()
        _mn = _re_n.search(
            r'<path[^>]*\bid="neck"[^>]*\bd="([^"]+)"',
            _et, flags=_re_n.DOTALL)
        if _mn is None:
            _mn = _re_n.search(
                r'<path[^>]*\bd="([^"]+)"[^>]*\bid="neck"',
                _et, flags=_re_n.DOTALL)
        if _mn:
            _neck_d_user = _mn.group(1)
    except Exception:
        _neck_d_user = None
    neck_d_final = _neck_d_user if _neck_d_user else neck_d_kk
    elems.append(f'<path d="{neck_d_final}" fill="none" '
                 f'stroke="{PAL["neck"]}" stroke-width="1.2"/>')
    # Save the FINAL neck path (user-edited if present, else computed) so
    # make_neck_svg.py can extract it without re-running the whole build.
    globals().setdefault("_LAST_NECK_D", "")
    globals()["_LAST_NECK_D"] = neck_d_final

    # (U-curve / chamber-back-wall reference removed -- the chamber body
    # polygon now traces the actual B-locus of the limacon stations, so the
    # decorative U-curve is redundant.)

    # Parabolic scoop on the chamber back wall (pink). Rim is a 3D
    # circle of radius R in the plane perpendicular to axis_unit; the
    # rim chord projects to a line of length 2R perpendicular to
    # axis_unit through rc in side view. Re-enabled per request.
    scoop = c.compute_scoop()
    rc = scoop["rim_center_xz"]; aim = scoop["aim_xz"]
    R  = scoop["rim_radius"]
    au = scoop["axis_unit"]
    perp_xz = np.array([-au[1], au[0]])
    e1 = rc + R * perp_xz
    e2 = rc - R * perp_xz
    elems.append(f'<line x1="{e1[0]:.2f}" y1="{e1[1]:.2f}" '
                 f'x2="{e2[0]:.2f}" y2="{e2[1]:.2f}" '
                 f'stroke="#a000a0" stroke-width="1.6"/>')
    _sb_tan = c.SB_P1 - c.SB_P0
    _sb_u = _sb_tan / np.linalg.norm(_sb_tan)
    if np.dot(e1 - rc, -_sb_u) > np.dot(e2 - rc, -_sb_u):
        r1_pt, r2_pt = e1, e2
    else:
        r1_pt, r2_pt = e2, e1
    elems.append(f'<circle cx="{r1_pt[0]:.2f}" cy="{r1_pt[1]:.2f}" '
                 f'r="2.0" fill="#a000a0"/>')
    elems.append(f'<circle cx="{r2_pt[0]:.2f}" cy="{r2_pt[1]:.2f}" '
                 f'r="2.0" fill="#a000a0"/>')
    elems.append(
        f'<text transform="matrix(1,0,0,-1,{r1_pt[0]+5:.1f},{r1_pt[1]-14:.1f})" '
        f'font-family="sans-serif" font-size="14" font-weight="700" '
        f'fill="#a000a0">R1</text>')
    elems.append(
        f'<text transform="matrix(1,0,0,-1,{r2_pt[0]+5:.1f},{r2_pt[1]+8:.1f})" '
        f'font-family="sans-serif" font-size="14" font-weight="700" '
        f'fill="#a000a0">R2</text>')
    # Frustum side walls: R1->P2 and R2->P3. Revolving these about the scoop
    # axis sweeps a truncated cone connecting the scoop rim to the bass-end
    # limaçon (B0-B1 = P3-P2). The interior (R2-R1-P2-P3 quadrilateral) is
    # hollow -- filled white -- so sound passes from the rim chord through
    # the open B0-B1 chord into the soundbox interior.
    _frustum_pts = [r2_pt, r1_pt, P2_arr, P3_arr]
    _frustum_d = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in _frustum_pts) + " Z"
    elems.append(
        f'<path d="{_frustum_d}" fill="#fff" stroke="#a000a0" '
        f'stroke-width="1.2" stroke-linejoin="round"/>')
    # B1, B2: bass-end limaçon endpoints (chamber axis and back wall at S'b).
    _Dp_lim, _p_lim = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
    _B1 = np.array(_Dp_lim)
    _diam_lim = c.diam_at_s(c._CHAMBER['s_at_Sprime_b'])
    _B2 = _B1 + _diam_lim * _p_lim
    elems.append(
        f'<line x1="{_B1[0]:.2f}" y1="{_B1[1]:.2f}" '
        f'x2="{_B2[0]:.2f}" y2="{_B2[1]:.2f}" '
        f'stroke="#a000a0" stroke-width="1.0" stroke-dasharray="4,3" '
        f'opacity="0.7"/>')
    # ARC_CENTER = intersection of B1-B2 line (extended) and the P0-P1
    # floor line. Two concentric arcs around ARC_CENTER:
    #   (a) From B2 to floor (lands at P1)  -- inner arc, R = |B2 - AC|
    #   (b) From B1 to floor (lands left of P0) -- outer arc, R = |B1 - AC|
    _p0p1_z  = float(P0_arr[1])
    _t_floor_int = (_p0p1_z - _B1[1]) / (_B2[1] - _B1[1])
    ARC_CENTER = _B1 + _t_floor_int * (_B2 - _B1)
    _R_back  = float(np.linalg.norm(_B2 - ARC_CENTER))    # inner (B2-side)
    _R_front = float(np.linalg.norm(_B1 - ARC_CENTER))    # outer (B1-side)
    _aB2 = np.arctan2(_B2[1] - ARC_CENTER[1], _B2[0] - ARC_CENTER[0])
    _aB1 = np.arctan2(_B1[1] - ARC_CENTER[1], _B1[0] - ARC_CENTER[0])
    _aFloor = np.pi   # left floor crossing for both circles
    _back_arc  = [ARC_CENTER + _R_back  * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(_aB2, _aFloor, 60)]
    _front_arc = [ARC_CENTER + _R_front * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(_aB1, _aFloor, 60)]
    _back_d  = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in _back_arc)
    _front_d = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in _front_arc)
    elems.append(
        f'<path d="{_back_d}" fill="none" stroke="#a000a0" '
        f'stroke-width="1.2" opacity="0.85"/>')
    elems.append(
        f'<path d="{_front_d}" fill="none" stroke="#a000a0" '
        f'stroke-width="1.2" opacity="0.85"/>')
    # Mark and label ARC_CENTER.
    elems.append(
        f'<circle cx="{ARC_CENTER[0]:.2f}" cy="{ARC_CENTER[1]:.2f}" '
        f'r="2.5" fill="#a000a0"/>')
    elems.append(
        f'<text transform="matrix(1,0,0,-1,{ARC_CENTER[0]+5:.1f},{ARC_CENTER[1]+4:.1f})" '
        f'font-family="sans-serif" font-size="11" font-weight="700" '
        f'fill="#a000a0">ARC_CENTER</text>')
    # Radii of the outer arc: dashed lines from ARC_CENTER to P0 and P3.
    elems.append(
        f'<line x1="{ARC_CENTER[0]:.2f}" y1="{ARC_CENTER[1]:.2f}" '
        f'x2="{P0_arr[0]:.2f}" y2="{P0_arr[1]:.2f}" '
        f'stroke="#a000a0" stroke-width="0.9" '
        f'stroke-dasharray="6,3" opacity="0.85"/>')
    elems.append(
        f'<line x1="{ARC_CENTER[0]:.2f}" y1="{ARC_CENTER[1]:.2f}" '
        f'x2="{P3_arr[0]:.2f}" y2="{P3_arr[1]:.2f}" '
        f'stroke="#a000a0" stroke-width="0.9" '
        f'stroke-dasharray="6,3" opacity="0.85"/>')
    # Label rim_center (rc) and vertex (v) -- both below the S3-S2 line.
    elems.append(
        f'<text transform="matrix(1,0,0,-1,{rc[0]+6:.1f},{rc[1]+4:.1f})" '
        f'font-family="sans-serif" font-size="12" font-weight="700" '
        f'fill="#a000a0">rc</text>')
    vertex = rc - scoop["depth"] * au
    elems.append(
        f'<circle cx="{vertex[0]:.2f}" cy="{vertex[1]:.2f}" '
        f'r="2.0" fill="#a000a0"/>')
    elems.append(
        f'<text transform="matrix(1,0,0,-1,{vertex[0]+6:.1f},{vertex[1]+4:.1f})" '
        f'font-family="sans-serif" font-size="12" font-weight="700" '
        f'fill="#a000a0">v</text>')
    # Parabolic scoop white-filled void path (the visible scoop bowl).
    fl = scoop["paraboloid_focal"]
    samples = []
    for r in np.linspace(-R, R, 41):
        zprime = r * r / (4.0 * fl)
        pt = vertex + zprime * au + r * perp_xz
        samples.append(pt)
    void_d = "M " + " L ".join(f"{p[0]:.2f},{p[1]:.2f}" for p in samples) + " Z"
    elems.append(f'<path d="{void_d}" fill="#fff" stroke="#a000a0" '
                 f'stroke-width="1.0" opacity="1.0"/>')
    elems.append(f'<line x1="{rc[0]:.2f}" y1="{rc[1]:.2f}" '
                 f'x2="{aim[0]:.2f}" y2="{aim[1]:.2f}" '
                 f'stroke="#a000a0" stroke-width="0.6" '
                 f'stroke-dasharray="3,2" opacity="0.8"/>')
    elems.append(f'<circle cx="{rc[0]:.2f}" cy="{rc[1]:.2f}" '
                 f'r="2.0" fill="#a000a0"/>')
    elems.append(f'<circle cx="{aim[0]:.2f}" cy="{aim[1]:.2f}" '
                 f'r="2.0" fill="#a000a0"/>')

    # Hb (S'b -> U'b limaçon at the chamber/pedestal boundary) removed --
    # this line lived in the pedestal area which is now its own polygon
    # with arcs on both sides, no longer needing the Hb construction.
    Dp_spb, p_spb = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
    Upb = Dp_spb + c.diam_at_s(c._CHAMBER['s_at_Sprime_b']) * p_spb
    # Ht = chamber CAP at S't (NOT at G7g): limaçon diameter at s_at_St.
    Dp_St, p_St = c.chamber_axis(c._CHAMBER['s_at_St'])
    Up_t = Dp_St + c.diam_at_s(c._CHAMBER['s_at_St']) * p_St
    elems.append(f'<line x1="{Dp_St[0]:.2f}" y1="{Dp_St[1]:.2f}" '
                 f'x2="{Up_t[0]:.2f}" y2="{Up_t[1]:.2f}" '
                 f'stroke="#cc0000" stroke-width="1.0" '
                 f'stroke-dasharray="4,3" opacity="0.7"/>')   # Eb (= Ht) at S't

    # Et: elbow top = external common tangent to G7's Nf_flat and Nf_sharp
    # disks (both R = CLEARANCE), drawn on the OUTER (+perp, back-of-neck)
    # side. The line ends are:
    #   Ef = tangent point on G7 Nf_flat  (elbow flat-side neck boundary)
    #   Es = tangent point on G7 Nf_sharp (elbow sharp-side neck boundary)
    # Et runs Es -> Ef (segment only, no extension).
    # (Et dashed-red line and Es/Ef tangent dots removed per user request.)
    g7_buf = None  # kept as None so downstream code that checks for it skips

    # ------------------------------------------------------------------
    # Part-region labels: BASE / SOUNDBOX / ELBOW / NECK / COLUMN
    # Each placed at a representative xz inside its region with sans-serif,
    # bold, small font and matrix(1,0,0,-1,...) to flip-correct vertical.
    # Also Hb / Ht / Et tag-labels at the right end of each diameter line.
    # ------------------------------------------------------------------
    # (Region labels BASE/SOUNDBOX/ELBOW/NECK/COLUMN removed per user request.)

    # Hb (300) text label removed -- the Hb line itself is gone.

    # New curved column (replaces the old rectangle). Four corners in CCW:
    #   C0 = bottom-left   (on the P0-P1 floor)
    #   C1 = bottom-right  (on the P0-P1 floor, col_width to the right of C0)
    #   C2 = top-right     (column inner top, raked)
    #   C3 = top-left      (column outer top, raked)
    C0_arr = np.array([c.COL_X_LEFT,  _floor_z_ped])
    C1_arr = np.array([c.COL_X_RIGHT, _floor_z_ped])
    C2_arr = np.array([float(c.N_KNOTS[0, 0]) + (c.COL_X_RIGHT - c.COL_X_LEFT),
                       c.N_KNOTS[0, 1]])
    C3_arr = np.array([float(c.N_KNOTS[0, 0]), c.N_KNOTS[0, 1]])
    _col_width = float(c.COL_X_RIGHT - c.COL_X_LEFT)

    # Right arc from C1 to C2 tangent to the C0-C3 line (the new column's
    # left edge), bowing LEFT into the column body by exactly col_width.
    _mid_C1C2 = 0.5 * (C1_arr + C2_arr)
    _chord = C2_arr - C1_arr
    _half = float(np.linalg.norm(_chord)) / 2.0
    _chord_u = _chord / (2.0 * _half)
    _n_in = np.array([_chord_u[1], -_chord_u[0]])
    if _n_in[0] < 0:
        _n_in = -_n_in
    _d_outer = float(np.dot(C1_arr - C0_arr, _n_in))
    _t_arc = (_half * _half - _d_outer * _d_outer) / (2.0 * _d_outer)
    _R_arc = _t_arc + _d_outer
    _C_arc = _mid_C1C2 + _t_arc * _n_in
    _aC1 = np.arctan2(C1_arr[1] - _C_arc[1], C1_arr[0] - _C_arc[0])
    _aC2 = np.arctan2(C2_arr[1] - _C_arc[1], C2_arr[0] - _C_arc[0])
    _sw_col = (_aC2 - _aC1 + np.pi) % (2.0 * np.pi) - np.pi
    _arc_right = [_C_arc + _R_arc * np.array([np.cos(a), np.sin(a)])
                  for a in np.linspace(_aC1, _aC1 + _sw_col, 80)]
    # Left arc = right arc translated horizontally by -col_width so its
    # endpoints land at C0 (on the floor) and C3.
    _arc_left = [p + np.array([-_col_width, 0.0]) for p in _arc_right]

    # Closed band: C0 -> left arc -> C3 -> straight top to C2
    # -> reversed right arc back to C1 -> straight close to C0.
    _shape_pts = _arc_left + _arc_right[::-1]
    _shape_d = ("M " +
                " L ".join(f"{p[0]:.2f} {p[1]:.2f}" for p in _shape_pts) +
                " Z")
    elems.append(
        f'<path d="{_shape_d}" fill="#1060d0" fill-opacity="0.25" '
        f'stroke="#1060d0" stroke-width="1.0" stroke-linejoin="round"/>')
    # Label the four column corners.
    for label, pt, dx, dy in [("C0", C0_arr, -22,   4),
                              ("C1", C1_arr,   4,   4),
                              ("C2", C2_arr,   6,  -4),
                              ("C3", C3_arr, -22,  -4)]:
        elems.append(
            f'<circle cx="{pt[0]:.2f}" cy="{pt[1]:.2f}" '
            f'r="2.0" fill="#3a2a14"/>')
        elems.append(
            f'<text transform="matrix(1,0,0,-1,{pt[0]+dx:.1f},{pt[1]+dy:.1f})" '
            f'font-family="sans-serif" font-size="11" font-weight="700" '
            f'fill="#3a2a14">{label}</text>')

    # Strings: grommet on SB, top raked into -x (csv.z encodes the rake)
    for s in strings:
        col = string_colour(s["note"])
        w = string_width(s["OD"])
        elems.append(f'<line x1="{s["g"][0]:.2f}" y1="{s["g"][2]:.2f}" '
                     f'x2="{s["Nf_flat"][0]:.2f}" y2="{s["Nf_flat"][2]:.2f}" '
                     f'stroke="{col}" stroke-width="{w:.3f}" '
                     f'stroke-linecap="round"/>')

    # Pin segments at each Nf_flat (lever pivot extension). Length 1.534"
    # = 38.96 mm, angle 12.01 deg off the string direction toward +x.
    # Uniform across all 47 strings; values from erand.dxf (real imperial).
    PIN_LEN = 38.96
    PIN_ANGLE_DEG = 12.01
    cos_p = np.cos(np.radians(PIN_ANGLE_DEG))
    sin_p = np.sin(np.radians(PIN_ANGLE_DEG))
    for s in strings:
        # String direction: from grommet up to Nf_flat (raked). Normalize.
        gx, gz = s["g"][0], s["g"][2]
        nx, nz = s["Nf_flat"][0], s["Nf_flat"][2]
        dx = nx - gx; dz = nz - gz
        L = float(np.hypot(dx, dz))
        if L < 1e-6: continue
        ux, uz = dx/L, dz/L
        # Rotate string direction by -PIN_ANGLE (CW in xz with z up = toward +x).
        # u' = ( ux*cos + uz*sin, -ux*sin + uz*cos )
        px = ux * cos_p + uz * sin_p
        pz = -ux * sin_p + uz * cos_p
        ex = nx + PIN_LEN * px
        ez = nz + PIN_LEN * pz
        # Light-green clearance buffer at the pin tip (lever pivot).
        elems.append(f'<circle cx="{ex:.2f}" cy="{ez:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#e0a020" fill-opacity="0.13"/>')
        elems.append(f'<line x1="{nx:.2f}" y1="{nz:.2f}" '
                     f'x2="{ex:.2f}" y2="{ez:.2f}" '
                     f'stroke="#444" stroke-width="0.6" '
                     f'stroke-linecap="round"/>')

    # Buffer disks at all three Nf positions (flat / nat / sharp). Colors:
    #   Nf_flat   red    #c00000
    #   Nf_nat    green  #2ca02c  (Erand convention)
    #   Nf_sharp  blue   #1060d0
    for s in strings:
        elems.append(f'<circle cx="{s["Nf_flat"][0]:.2f}" cy="{s["Nf_flat"][2]:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#c00000" fill-opacity="0.13"/>')
        elems.append(f'<circle cx="{s["Nf_nat"][0]:.2f}" cy="{s["Nf_nat"][2]:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#2ca02c" fill-opacity="0.13"/>')
        elems.append(f'<circle cx="{s["Nf_sharp"][0]:.2f}" cy="{s["Nf_sharp"][2]:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#1060d0" fill-opacity="0.13"/>')

    # Outer buffer envelope. PRIMARY SOURCE: hand-drawn path in
    # buffer.svg (canonical, edited in Inkscape). If buffer.svg is missing
    # or unreadable, fall back to the convex-hull-with-arcs envelope below.
    env_d = None
    try:
        import re as _re_env
        _bp = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "buffer.svg")
        with open(_bp) as _bf:
            _btxt = _bf.read()
        _paths = _re_env.findall(
            r'<path[^>]*\bd="([^"]+)"[^>]*>', _btxt, flags=_re_env.DOTALL)
        # Prefer the dashed path (the envelope); fall back to first.
        _dashed = [d for d in _paths if 'dasharray' in
                   _re_env.search(
                       r'<path[^>]*\bd="' + _re_env.escape(d) + r'"[^>]*>',
                       _btxt).group(0)]
        env_d = (_dashed[0] if _dashed else _paths[0]) if _paths else None
    except Exception as _e:
        env_d = None
    try:
        from scipy.spatial import ConvexHull
        all_centres = []
        cos_p = np.cos(np.radians(12.01)); sin_p = np.sin(np.radians(12.01))
        for s in strings:
            all_centres.append((s["Nf_flat"][0],  s["Nf_flat"][2]))
            all_centres.append((s["Nf_nat"][0],   s["Nf_nat"][2]))
            all_centres.append((s["Nf_sharp"][0], s["Nf_sharp"][2]))
            gx, gz = s["g"][0], s["g"][2]
            nx, nz = s["Nf_flat"][0], s["Nf_flat"][2]
            dx = nx - gx; dz = nz - gz
            L = np.hypot(dx, dz)
            if L > 0:
                ux, uz = dx/L, dz/L
                px = ux*cos_p + uz*sin_p; pz = -ux*sin_p + uz*cos_p
                all_centres.append((nx + 38.96*px, nz + 38.96*pz))
        bpts = np.array(all_centres)
        R = float(c.CLEARANCE)
        N = len(bpts)
        TWO_PI = 2.0 * np.pi
        EPS = 1e-9

        def _disk_union_outer_boundary(centres, radius):
            """Gift-wrap CCW around the union of equal-radius disks.

            Returns a list of segments alternating ('arc', i, theta_start,
            theta_end) and ('line', p_from, p_to). Walks CCW; each arc is
            on disk i with both angles in standard math convention
            (atan2). Arc sweep = (theta_end - theta_start) mod 2pi.
            """
            n = len(centres)
            # Start: leftmost centre (min x, ties min y); start at compass
            # angle pi on that disk (point c_i + R*(-1,0), the western
            # extremum -- guaranteed on the union boundary).
            order = np.lexsort((centres[:, 1], centres[:, 0]))
            i0 = int(order[0])
            theta_start = np.pi
            i = i0
            theta_curr = theta_start
            segments = []
            max_iters = n + 5
            for _step in range(max_iters):
                ci = centres[i]
                # Find next disk j and swap angle theta_swap on disk i.
                # Collect all candidates first so we can resolve near-ties
                # by picking the closest disk -- otherwise near-collinear
                # configurations let a far-away disk win by a hair of
                # floating-point angle difference, skipping the closer
                # disk that physically lies on the union boundary.
                candidates = []  # list of (dtheta, D, j, theta_swap_i,
                                 # theta_curr_j, is_tangent)
                for j in range(n):
                    if j == i:
                        continue
                    d = centres[j] - ci
                    D = float(np.hypot(d[0], d[1]))
                    if D < EPS:
                        continue
                    alpha = np.arctan2(d[1], d[0])
                    if D >= 2.0 * radius:
                        # Disjoint disks: swap via external common tangent
                        # at compass angle alpha - pi/2 on both disks. For
                        # a CCW walk around the union the interior is on
                        # the LEFT of the walking direction, so the
                        # outward normal at the tangent point is to the
                        # RIGHT of the chord direction d -- i.e. d rotated
                        # by -pi/2.
                        theta_swap_i = (alpha - 0.5 * np.pi) % TWO_PI
                        theta_curr_j = theta_swap_i  # same angle on j
                        is_tangent = True
                    else:
                        # Overlapping disks: swap at the leading
                        # intersection. CCW on disk i, the boundary leaves
                        # i (enters j's interior) at compass angle
                        # alpha - beta where beta = acos(D / 2R). The same
                        # point on disk j sits at angle (alpha + pi) + beta.
                        beta = np.arccos(max(-1.0, min(1.0, D / (2.0 * radius))))
                        theta_swap_i = (alpha - beta) % TWO_PI
                        theta_curr_j = (alpha + np.pi + beta) % TWO_PI
                        is_tangent = False
                    dtheta = (theta_swap_i - theta_curr) % TWO_PI
                    # Tiny dtheta (<EPS) means we just swapped to here;
                    # don't re-pick the same disk in a degenerate cycle.
                    if dtheta < EPS:
                        dtheta = TWO_PI
                    candidates.append(
                        (dtheta, D, j, theta_swap_i, theta_curr_j,
                         is_tangent))
                if not candidates:
                    best_j = -1
                else:
                    # Sort: smallest dtheta first; ties broken by smallest
                    # distance D (closest disk wins).
                    candidates.sort(key=lambda t: (t[0], t[1]))
                    # Walk candidates in dtheta order; reject any whose
                    # tangent segment is BLOCKED by a closer disk (per
                    # the spec). The first non-rejected candidate wins.
                    ANG_TOL = 1e-3  # radians (~0.06 deg) for near-ties
                    best_j = -1
                    for (cdtheta, cD, cj, cts, ctcj, cisT) in candidates:
                        # Among candidates within ANG_TOL of cdtheta, pick
                        # the closest by D (handles near-collinear ties
                        # robustly: a far-away disk that wins min-dtheta
                        # by floating-point hair gets bumped by a closer
                        # disk that physically lies on the boundary).
                        # Then verify the chosen tangent (or intersection)
                        # is not blocked by any other disk.
                        # Step 1: nearest-tie selection.
                        near = [t for t in candidates
                                if t[0] - cdtheta < ANG_TOL]
                        near.sort(key=lambda t: t[1])
                        (cdtheta, cD, cj, cts, ctcj, cisT) = near[0]
                        # Step 2: blocking check.
                        blocked = False
                        if cisT:
                            # Tangent segment: from c_i + R*n to c_j +
                            # R*n where n = (cos cts, sin cts). Reject if
                            # any other disk k has perp distance from c_k
                            # to that line < R AND projection inside the
                            # segment.
                            n_vec = np.array(
                                [np.cos(cts), np.sin(cts)])
                            p_from = ci + radius * n_vec
                            p_to = centres[cj] + radius * n_vec
                            seg_dir = p_to - p_from
                            seg_len = float(np.hypot(*seg_dir))
                            if seg_len > EPS:
                                seg_u = seg_dir / seg_len
                                seg_perp = np.array(
                                    [-seg_u[1], seg_u[0]])
                                for k in range(n):
                                    if k == i or k == cj:
                                        continue
                                    v = centres[k] - p_from
                                    perp = abs(
                                        v[0]*seg_perp[0]
                                        + v[1]*seg_perp[1])
                                    along = (v[0]*seg_u[0]
                                             + v[1]*seg_u[1])
                                    if (perp < radius - EPS
                                            and EPS < along
                                            < seg_len - EPS):
                                        blocked = True
                                        break
                        if not blocked:
                            (best_dtheta, _bestD, best_j,
                             best_theta_swap, best_theta_curr_j,
                             best_is_tangent) = (
                                cdtheta, cD, cj, cts, ctcj, cisT)
                            break
                if best_j < 0:
                    break
                # Emit arc on disk i from theta_curr to best_theta_swap.
                segments.append(('arc', i, theta_curr, best_theta_swap))
                if best_is_tangent:
                    # Disjoint disks: straight external tangent segment to
                    # next disk's matching tangent point.
                    p_from = ci + radius * np.array(
                        [np.cos(best_theta_swap), np.sin(best_theta_swap)])
                    p_to = centres[best_j] + radius * np.array(
                        [np.cos(best_theta_swap), np.sin(best_theta_swap)])
                    segments.append(('line', p_from, p_to))
                # Overlapping disks: no straight segment -- the swap point
                # IS the same physical point on both disks (intersection).
                # Termination: about to start on disk i0 again. Close by
                # walking the remaining arc back to the original start
                # angle.
                if best_j == i0:
                    segments.append(
                        ('arc', i0, best_theta_curr_j, theta_start))
                    return segments
                i = best_j
                theta_curr = best_theta_curr_j
            # Bail out -- caller falls back to convex-hull envelope.
            raise RuntimeError(
                f'disk-union gift-wrap did not close in {max_iters} steps')

        # Convex-hull envelope (smooth, flowing) -- only the outer hull
        # disks contribute arcs, with external common-tangent lines between
        # them. Arcs emitted as cubic Beziers ((4/3)*tan(step/4) handles,
        # <0.5 micron deviation from true circles at R=8). This matches
        # the smooth style sketched by hand earlier.
        hull = ConvexHull(bpts)
        hp_idx = hull.vertices
        hp = bpts[hp_idx]
        nh = len(hp)
        # CCW orient (ConvexHull returns CCW already in 2D, but verify).
        signed = 0.0
        for i in range(nh):
            a = hp[i]; b = hp[(i + 1) % nh]
            signed += (b[0] - a[0]) * (b[1] + a[1])
        if signed > 0:
            hp = hp[::-1]
        edge_normals = []
        for i in range(nh):
            a = hp[i]; b = hp[(i + 1) % nh]
            dd = b - a; dd = dd / np.linalg.norm(dd)
            edge_normals.append(np.array([dd[1], -dd[0]]))
        env_parts = []
        for i in range(nh):
            n_in = edge_normals[(i - 1) % nh]
            n_out = edge_normals[i]
            tan_in = hp[i] + R * n_in
            tan_out = hp[i] + R * n_out
            if i == 0:
                env_parts.append(f'M {tan_in[0]:.2f},{tan_in[1]:.2f}')
            # Arc on this hull-vertex disk from compass angle of n_in to
            # compass angle of n_out (CCW).
            th_a = np.arctan2(n_in[1], n_in[0])
            th_b = np.arctan2(n_out[1], n_out[0])
            sweep = (th_b - th_a) % TWO_PI
            n_quad = max(1, int(np.ceil(sweep / (0.5 * np.pi))))
            step = sweep / n_quad
            f_ctl = (4.0 / 3.0) * np.tan(step / 4.0)
            for k in range(n_quad):
                a0 = th_a + k * step
                a1 = a0 + step
                c0, s0 = np.cos(a0), np.sin(a0)
                c1, s1 = np.cos(a1), np.sin(a1)
                P1 = hp[i] + R * np.array(
                    [c0 - f_ctl * s0, s0 + f_ctl * c0])
                P2 = hp[i] + R * np.array(
                    [c1 + f_ctl * s1, s1 - f_ctl * c1])
                P3 = hp[i] + R * np.array([c1, s1])
                env_parts.append(
                    f'C {P1[0]:.2f},{P1[1]:.2f} '
                    f'{P2[0]:.2f},{P2[1]:.2f} '
                    f'{P3[0]:.2f},{P3[1]:.2f}')
            next_tan_in = hp[(i + 1) % nh] + R * n_out
            env_parts.append(
                f'L {next_tan_in[0]:.2f},{next_tan_in[1]:.2f}')
        env_parts.append('Z')
        # Only overwrite if the hand-drawn buffer.svg path wasn't loaded.
        if env_d is None:
            env_d = ' '.join(env_parts)
    except Exception as _e:
        pass
    if env_d is not None:
        elems.append(f'<path d="{env_d}" fill="none" stroke="#0a8" '
                     f'stroke-width="0.8" stroke-dasharray="4,3" opacity="0.85"/>')

    # Critical anchor dots + labels (small, dark grey, off to the side).
    import csv as _csv
    import numpy as _np
    # S and U are the EXTENDED path / back-wall envelope. Their endpoints
    # (Sb, St, Ub, Ut) are 2*AIR_GAP beyond the SB Bezier's actual ends.
    _tan1_lbl = c.bez_tan(*S["sb_bezier"], 1.0)
    _tan1_lbl_u = _tan1_lbl / _np.linalg.norm(_tan1_lbl)
    # St = top of S (= G7g + 2*AIR_GAP * tan1_unit)
    St_xz = c.SB_P3 + 2.0 * c.AIR_GAP * _tan1_lbl_u
    # Ut = top of U (= B-locus at G7g + 2*AIR_GAP * tan1_unit, parallel to St)
    Dp_g, p_g = c.chamber_axis(c._CHAMBER['s_at_G7g'])
    Ut_xz = Dp_g + c.diam_at_s(c._CHAMBER['s_at_G7g']) * p_g \
            + 2.0 * c.AIR_GAP * _tan1_lbl_u
    # Sb = bottom of S (= where the BTF is at z = SBB.z - 2*AIR_GAP, on BTF curve)
    Dp_Spb, p_Spb = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
    Sb_xz = Dp_Spb
    # Ub = bottom of U (= B-locus at Sb)
    Ub_xz = Dp_Spb + c.diam_at_s(c._CHAMBER['s_at_Sprime_b']) * p_Spb
    # G7 buffer tangent endpoints
    g7s = next((s for s in strings if s["note"].strip() == "G7"), None)
    Es_xz = Ef_xz = None
    Etn_xz = Ets_xz = None
    if g7s is not None:
        Pf = _np.array([g7s["Nf_flat"][0],  g7s["Nf_flat"][2]])
        Ps = _np.array([g7s["Nf_sharp"][0], g7s["Nf_sharp"][2]])
        v_u = (Ps - Pf) / _np.linalg.norm(Ps - Pf)
        perp_buf = _np.array([-v_u[1], v_u[0]])
        Ef_xz = Pf + c.CLEARANCE * perp_buf
        Es_xz = Ps + c.CLEARANCE * perp_buf
        mid = 0.5 * (Es_xz + Ef_xz)
        Et_len = 50.0
        Etn_xz = mid - 0.5 * Et_len * v_u    # north (flat side)
        Ets_xz = mid + 0.5 * Et_len * v_u    # south (sharp side)
    # Build the (label, point, label-offset-dx-dy) list.
    N = c.N_KNOTS
    # N1 is the column inner top corner (was K10, derived = N0 + col_w).
    # Pedestal corners P2, P3 are 60 mm below Hb perpendicular to it,
    # leaving the 60 mm scoop region between pedestal top and Hb.
    _ped_perp_raw = np.array([p_Spb[1], -p_Spb[0]])
    _ped_perp_raw = _ped_perp_raw / np.linalg.norm(_ped_perp_raw)
    _ped_perp = _ped_perp_raw if _ped_perp_raw[1] < 0 else -_ped_perp_raw
    SCOOP_THICK = 60.0
    P3_xz = Sb_xz + SCOOP_THICK * _ped_perp     # 60 mm below S'b along Hb perp
    P2_xz = Ub_xz + SCOOP_THICK * _ped_perp     # 60 mm below U'b along Hb perp

    # Neck CCW: N0..N9 stored directly in N_KNOTS, CCW from column outer top.
    # Legacy K-name mapping: N0=K1, N1=K10, N2=K9, N3=K8, N4=K7, N5=K6,
    # N6=K5, N7=K4, N8=K3, N9=K2. Region corners P (pedestal), S (scoop),
    # B (soundbox).
    pts = [
        ("N0",   N[0],                      ( 8,   8)),
        ("N1",   N[1],                      ( 8,  -8)),
        ("N2",   N[2],                      (-25,  -8)),
        ("N3",   N[3],                      ( 6,   8)),
        ("N4",   N[4],                      ( 6,   8)),
        ("N5",   N[5],                      ( 8,  10)),
        ("N6",   N[6],                      ( 6,   8)),
        ("N7",   N[7],                      ( 6,  -8)),
        ("N8",   N[8],                      ( 6,   8)),
        ("N9",   N[9],                      ( 6,   8)),
        # P0/P1/P2 are now drawn at the pedestal triangle corners earlier
        # (see build_views.py pedestal section). The old P0/P1/P2/P3
        # chamber-construction labels are removed; their structural roles
        # (S2 = Ub, S3 = Sb, plus B-locus points) remain labeled below.
        # Soundbox 4 corners (CCW from bass-front):
        # B0 = bass-front (chamber axis at S'b, dimple side)
        # B1 = bass-back  (chamber back wall at S'b, bulge side)
        # B2 = treble-back (chamber back wall at S't)
        # B3 = treble-front (chamber axis at S't)
        ("B0",   Sb_xz,                     (-22, -12)),
        ("B1",   Ub_xz,                     (  8, -12)),
        ("B2",   Ut_xz,                     (  8, -10)),
        ("B3",   St_xz,                     (-18, -10)),
    ]
    # (Etn, Ets, Es, Ef labels removed per user request.)
    for name, p, (dx, dy) in pts:
        elems.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" '
                     f'r="2.0" fill="#202020"/>')
        tx = p[0] + dx; ty = p[1] + dy
        elems.append(f'<text transform="matrix(1,0,0,-1,{tx:.1f},{ty:.1f})" '
                     f'font-family="sans-serif" font-size="14" font-weight="700" '
                     f'fill="#202020">{name}</text>')

    return elems, (x_min, -z_max, x_max - x_min, z_max - z_min)


# ---------------------------------------------------------------------------
# Top view (xy plane)
# ---------------------------------------------------------------------------

def top_view_content(strings):
    sts = chamber_stations_to_g7g(120)
    floor_lim = floor_limacon_3d()

    elems = []

    # Outer envelope (chamber footprint silhouette)
    env_top, env_bot = [], []
    for st in sts:
        xy = st["pts3d"][:, [0, 1]]
        env_top.append(tuple(xy[int(np.argmax(xy[:, 1]))]))
        env_bot.append(tuple(xy[int(np.argmin(xy[:, 1]))]))
    outline = env_top + env_bot[::-1] + [env_top[0]]
    elems.append(f'<path d="{polyline_d(outline)}" '
                 f'fill="{PAL["chamber_fill"]}" fill-opacity="0.7" '
                 f'stroke="{PAL["chamber_edge"]}" stroke-width="1.5"/>')

    # Floor limacon footprint (gold dashed reference)
    flr_xy = floor_lim[:, [0, 1]]
    elems.append(f'<path d="{polyline_d(np.vstack([flr_xy, flr_xy[:1]]))}" '
                 f'fill="none" stroke="{PAL["ref_dashed"]}" stroke-width="1.0" '
                 f'stroke-dasharray="4,3"/>')

    # Soundboard centerline (grommet line at y=0)
    if strings:
        elems.append(f'<line x1="{strings[0]["g"][0]:.2f}" y1="0" '
                     f'x2="{strings[-1]["g"][0]:.2f}" y2="0" '
                     f'stroke="{PAL["soundboard"]}" stroke-width="1.0"/>')
    for s in strings:
        elems.append(f'<circle cx="{s["g"][0]:.2f}" cy="0" r="0.9" '
                     f'fill="{string_colour(s["note"])}"/>')

    # Column footprint (rough 32mm in y)
    col_w_y = 32.0
    elems.append(
        f'<rect x="{c.COL_X_LEFT:.2f}" y="{-col_w_y/2:.2f}" '
        f'width="{c.COL_X_RIGHT - c.COL_X_LEFT:.2f}" height="{col_w_y:.2f}" '
        f'fill="{PAL["column"]}" fill-opacity="0.3" '
        f'stroke="{PAL["neck"]}" stroke-width="0.6"/>')

    # Parabolic scoop footprint (top view).
    # The rim is a 3D circle of radius R in a plane perpendicular to
    # axis_unit (which lies in xz). When projected onto xy (top view),
    # it appears as an ellipse:
    #   center = (rim_center_xz.x, 0)
    #   rx     = R * |axis_unit.z|     (foreshortening in x)
    #   ry     = R                     (full extent in y)
    scoop = c.compute_scoop()
    rc = scoop["rim_center_xz"]; au = scoop["axis_unit"]; R = scoop["rim_radius"]
    rx_top = R * abs(au[1])
    ry_top = R
    elems.append(f'<ellipse cx="{rc[0]:.2f}" cy="0" '
                 f'rx="{rx_top:.2f}" ry="{ry_top:.2f}" '
                 f'fill="none" stroke="#a000a0" stroke-width="0.9" '
                 f'stroke-dasharray="3,2" opacity="0.85"/>')

    all_pts = np.array(env_top + env_bot + list(flr_xy)
                       + [(s["g"][0], s["g"][1]) for s in strings])
    x_min = min(all_pts[:, 0].min(), c.COL_X_LEFT) - 30
    x_max = all_pts[:, 0].max() + 30
    y_min = all_pts[:, 1].min() - 30
    y_max = all_pts[:, 1].max() + 30
    return elems, (x_min, -y_max, x_max - x_min, y_max - y_min)


# ---------------------------------------------------------------------------
# Front view (yz plane, look +x)
# ---------------------------------------------------------------------------

def front_view_content(strings):
    sts = chamber_stations_to_g7g(120)
    floor_lim = floor_limacon_3d()

    all_pts = np.vstack([st["pts3d"] for st in sts] + [floor_lim])
    z_bins = np.linspace(0, all_pts[:, 2].max(), 120)

    elems = []

    # Silhouette in yz: at each z slice, find min/max y.
    hull_top, hull_bot = [], []
    for i in range(len(z_bins) - 1):
        m = (all_pts[:, 2] >= z_bins[i]) & (all_pts[:, 2] < z_bins[i + 1])
        if m.sum() < 2:
            continue
        slab = all_pts[m]
        zm = 0.5 * (z_bins[i] + z_bins[i + 1])
        hull_top.append((slab[:, 1].max(), zm))
        hull_bot.append((slab[:, 1].min(), zm))
    if hull_top:
        sil = hull_top + hull_bot[::-1] + [hull_top[0]]
        elems.append(f'<path d="{polyline_d(sil)}" '
                     f'fill="{PAL["chamber_fill"]}" fill-opacity="0.7" '
                     f'stroke="{PAL["chamber_edge"]}" stroke-width="1.5"/>')

    # Floor limacon (gold dashed reference)
    flr_yz = floor_lim[:, [1, 2]]
    elems.append(f'<path d="{polyline_d(np.vstack([flr_yz, flr_yz[:1]]))}" '
                 f'fill="none" stroke="{PAL["ref_dashed"]}" stroke-width="1.0" '
                 f'stroke-dasharray="4,3"/>')

    # Floor line
    y_min = min(p[0] for p in hull_bot) if hull_bot else -300
    y_max = max(p[0] for p in hull_top) if hull_top else 300
    elems.append(f'<line x1="{y_min - 30:.1f}" y1="0" x2="{y_max + 30:.1f}" y2="0" '
                 f'stroke="{PAL["floor"]}" stroke-width="0.6" '
                 f'stroke-dasharray="4,3" opacity="0.7"/>')

    # Strings collapse onto y=0 in this view; show a few sample heights
    # by drawing tiny vertical marks at y=0 colour-coded by note.
    for s in strings[:: max(1, len(strings) // 8)]:
        col = string_colour(s["note"])
        elems.append(f'<line x1="0" y1="{s["g"][2]:.2f}" '
                     f'x2="0" y2="{s["Nf_flat"][2]:.2f}" '
                     f'stroke="{col}" stroke-width="{string_width(s["OD"]):.3f}" '
                     f'opacity="0.6" stroke-linecap="round"/>')

    z_min_view = -50
    z_max_view = c.N_KNOTS[:, 1].max() + 50
    return elems, (y_min - 30, -z_max_view, (y_max - y_min) + 60, z_max_view - z_min_view)


# ---------------------------------------------------------------------------
# Rear view (mirror of front)
# ---------------------------------------------------------------------------

def rear_view_content(strings):
    elems, vb = front_view_content(strings)
    out = ['<g transform="scale(-1,1)">'] + elems + ["</g>"]
    x0, y0, w, h = vb
    return out, (-(x0 + w), y0, w, h)


# ---------------------------------------------------------------------------
# SBF view (face-on to soundboard): u along S arc length vs y depth
# ---------------------------------------------------------------------------

def sbf_view_content(strings):
    # Sweep along the soundboard portion of the chamber path: SBB -> G7g.
    # We use clements47.chamber_axis / diam_at_s for cross-sections so the
    # diameter profile (constant D_FLOOR through S'_b, taper to D_AT_St at
    # S'_t, taper to TOP_DIAM at K6) is consistent with the side view.
    s_lo = c.s_at_SBB
    s_hi = c.s_at_G7g

    # Map grommet x to arc length along the SBB->G7g portion.
    s_samples = np.linspace(s_lo, s_hi, 2000)
    x_samples = np.array([c.chamber_axis(s)[0][0] for s in s_samples])

    sts = []
    for s in np.linspace(s_lo, s_hi, 180):
        D, perp = c.chamber_axis(s)
        diam = c.diam_at_s(s)
        pts = _limacon_3d(D, perp, diam)
        sts.append({"s": s, "pts3d": pts})

    elems = []

    # Chamber silhouette in (u, y) plane
    u_top, u_bot = [], []
    for st in sts:
        v = st["pts3d"][:, 1]
        u_top.append((st["s"], v.max()))
        u_bot.append((st["s"], v.min()))
    sil = u_top + u_bot[::-1] + [u_top[0]]
    elems.append(f'<path d="{polyline_d(sil)}" '
                 f'fill="{PAL["chamber_fill"]}" fill-opacity="0.7" '
                 f'stroke="{PAL["chamber_edge"]}" stroke-width="1.5"/>')

    # Centerline (grommet line at y=0)
    elems.append(f'<line x1="{u_top[0][0]:.2f}" y1="0" '
                 f'x2="{u_top[-1][0]:.2f}" y2="0" '
                 f'stroke="{PAL["soundboard"]}" stroke-width="1.0"/>')

    # Grommets coloured by note, located at u along S, y=0
    for s in strings:
        gx = s["g"][0]
        if gx < x_samples[0] or gx > x_samples[-1]:
            continue
        u = float(np.interp(gx, x_samples, s_samples))
        elems.append(f'<circle cx="{u:.2f}" cy="0" r="0.9" '
                     f'fill="{string_colour(s["note"])}"/>')

    u_min = min(p[0] for p in u_top) - 40
    u_max = max(p[0] for p in u_top) + 40
    v_min = min(p[1] for p in u_bot) - 40
    v_max = max(p[1] for p in u_top) + 40
    return elems, (u_min, -v_max, u_max - u_min, v_max - v_min)


# ---------------------------------------------------------------------------
# Emit
# ---------------------------------------------------------------------------

def emit_view(out_path, content_fn, strings, title=None):
    elems, vb = content_fn(strings)
    x0, y0, w, h = vb
    # Add a title-strip and frame to the viewbox.
    title_h = 40
    pad = 12
    new_vb = (x0 - pad, y0 - title_h, w + 2 * pad, h + title_h + pad)
    svg = svg_open(new_vb, width_px=900)
    # white background
    svg.append(f'<rect x="{new_vb[0]:.1f}" y="{new_vb[1]:.1f}" '
               f'width="{new_vb[2]:.1f}" height="{new_vb[3]:.1f}" fill="{PAL["bg"]}"/>')
    # Frame around content area
    svg.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" '
               f'width="{w:.1f}" height="{h:.1f}" fill="none" '
               f'stroke="{PAL["frame"]}" stroke-width="0.6"/>')
    # Title at top of view
    if title:
        svg.append(f'<text x="{x0 + 10:.1f}" y="{y0 - 12:.1f}" '
                   f'font-family="sans-serif" font-size="22" font-weight="bold" '
                   f'fill="{PAL["title"]}">{title}</text>')
    svg.append('<g transform="scale(1,-1)">')
    svg.extend(elems)
    svg.append("</g>")
    svg.append("</svg>")
    with open(out_path, "w") as fh:
        fh.write("\n".join(svg))


def emit_composite(out_path, strings):
    side_e, side_vb   = side_view_content(strings)
    top_e,  top_vb    = top_view_content(strings)
    front_e, front_vb = front_view_content(strings)
    sbf_e,  sbf_vb    = sbf_view_content(strings)

    PAD = 80.0
    TITLE_H = 50.0
    cell_w = max(side_vb[2], top_vb[2], front_vb[2], sbf_vb[2]) + PAD
    cell_h = max(side_vb[3], top_vb[3], front_vb[3], sbf_vb[3]) + PAD + TITLE_H
    grid_w = 2 * cell_w
    grid_h = 2 * cell_h

    def cell(elems, vb, lbl, dx, dy):
        x0, y0, w, h = vb
        out = [f'<g transform="translate({dx:.1f}, {dy:.1f})">']
        # cell frame
        out.append(f'<rect x="0" y="{TITLE_H:.1f}" width="{cell_w:.1f}" '
                   f'height="{cell_h - TITLE_H:.1f}" fill="none" '
                   f'stroke="{PAL["frame"]}" stroke-width="0.6"/>')
        # title (bold, top of cell)
        out.append(f'<text x="10" y="32" font-family="sans-serif" '
                   f'font-size="22" font-weight="bold" '
                   f'fill="{PAL["title"]}">{lbl}</text>')
        cx = (cell_w - w) / 2 - x0
        cy = TITLE_H + (cell_h - TITLE_H - h) / 2 - y0
        out.append(f'<g transform="translate({cx:.1f}, {cy:.1f})">')
        out.append('<g transform="scale(1,-1)">')
        out.extend(elems)
        out.append("</g></g></g>")
        return out

    svg = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {grid_w:.1f} {grid_h:.1f}" '
        f'width="1600" height="{int(1600 * grid_h / grid_w)}" '
        f'font-family="sans-serif" font-size="12">',
        f'<rect x="0" y="0" width="{grid_w:.1f}" height="{grid_h:.1f}" fill="{PAL["bg"]}"/>',
    ]
    svg.extend(cell(side_e,  side_vb,  "Side view (xz, project along +y)",     0,      0))
    svg.extend(cell(top_e,   top_vb,   "Top view (xy, project along -z)",     cell_w, 0))
    svg.extend(cell(front_e, front_vb, "Front view (yz, project along +x)",    0,     cell_h))
    svg.extend(cell(sbf_e,   sbf_vb,   "Soundboard face-on (u, y)",           cell_w, cell_h))
    svg.append("</svg>")
    with open(out_path, "w") as fh:
        fh.write("\n".join(svg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["side", "top", "front", "rear", "sbf", "composite"],
                    default=None)
    args = ap.parse_args()
    strings = load_strings()
    print(f"Loaded {len(strings)} strings from {STRINGS_CSV}", file=sys.stderr)

    targets = {
        "side":  (OUT_SIDE,  side_view_content,  "SIDE (xz, look +y)"),
        "top":   (OUT_TOP,   top_view_content,   "TOP (xy, look -z)"),
        "front": (OUT_FRONT, front_view_content, "FRONT (yz, look +x)"),
        "rear":  (OUT_REAR,  rear_view_content,  "REAR (yz, look -x)"),
        "sbf":   (OUT_SBF,   sbf_view_content,   "SBF (u,y soundboard)"),
    }

    if args.only and args.only != "composite":
        path, fn, title = targets[args.only]
        emit_view(path, fn, strings, title=title)
        print(f"wrote {path}", file=sys.stderr)
    elif args.only == "composite":
        emit_composite(OUT_VIEWS, strings)
        print(f"wrote {OUT_VIEWS}", file=sys.stderr)
    else:
        for path, fn, title in targets.values():
            emit_view(path, fn, strings, title=title)
            print(f"wrote {path}", file=sys.stderr)
        emit_composite(OUT_VIEWS, strings)
        print(f"wrote {OUT_VIEWS}", file=sys.stderr)


if __name__ == "__main__":
    main()
