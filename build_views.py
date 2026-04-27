#!/usr/bin/env python3
"""build_views.py - orthographic SVG views of the clements47 harp.

Body geometry from clements47.py (SB Bezier, K_KNOTS, COL_X_LEFT/RIGHT,
BASE_DIAM, TOP_DIAM, compute_S_full, compute_U, build_neck_segments,
chamber_axis, limacon_3d). String positions from strings.csv (Ng_*,
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
# constants (SB_P0..P3, K_KNOTS, COL_X_LEFT/RIGHT) are authored in the
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
# Chamber 3D: limacon sweep from SBB along S to G7g, plus floor limacon at SF.
# Replicated from clements47.write_svg's inline logic so we don't modify
# clements47.py.
# ---------------------------------------------------------------------------

# Diameter taper per clements47.write_svg.
BASE_DIAM = 500.0                                       # at SBB
TOP_DIAM  = float(np.linalg.norm(c.K_KNOTS[3] - c.K_KNOTS[5]))   # K6-K4 distance


def _D_and_perp_at_arclen(s_val, sb_bez, sb_ext, ts_sb, arc_sb, ts_ex, arc_ex, L_sb):
    if s_val <= L_sb:
        ti = float(np.interp(s_val, arc_sb, ts_sb))
        D_pt = c.bez(*sb_bez, ti)
        t_dir = c.bez_tan(*sb_bez, ti)
    else:
        ti = float(np.interp(s_val - L_sb, arc_ex, ts_ex))
        D_pt = c.bez(*sb_ext, ti)
        t_dir = c.bez_tan(*sb_ext, ti)
    t_dir = t_dir / np.linalg.norm(t_dir)
    perp = np.array([t_dir[1], -t_dir[0]])
    return D_pt, perp


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


def chamber_stations_to_g7g(n=N_STATIONS_DRAWN):
    """Stations along S from SBB (s=0) to G7g (s=L_sb), each with limacon
    cross-section perpendicular to S in 3D."""
    S = c.compute_S_full()
    sb_bez = S["sb_bezier"]                  # SBB -> G7g
    sb_ext = S["sb_extension"]               # G7g -> K6
    ts_sb, arc_sb = c.bez_arclen_table(*sb_bez, n=2000)
    ts_ex, arc_ex = c.bez_arclen_table(*sb_ext, n=500)
    L_sb = float(arc_sb[-1])
    L_ex = float(arc_ex[-1])
    L_total = L_sb + L_ex

    out = []
    for s in np.linspace(0.0, L_sb, n):
        D, perp = _D_and_perp_at_arclen(s, sb_bez, sb_ext, ts_sb, arc_sb,
                                          ts_ex, arc_ex, L_sb)
        frac = s / L_total
        diam = BASE_DIAM * (1 - frac) + TOP_DIAM * frac
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
    """Side view (xz, look +y). Body geometry (SB Bezier, K_KNOTS, chamber)
    drawn in the canonical un-raked frame; only the column and strings get
    the at-rest -7 deg rake (the column as a parallelogram with its top in
    -x, the strings as csv-encoded -x rake offsets)."""
    S = c.compute_S_full()
    U = c.compute_U(S["F"])
    neck_segs = c.build_neck_segments()
    F = S["F"]

    sts = chamber_stations_to_g7g(N_STATIONS_DRAWN)

    elems = []

    x_vals = ([k[0] for k in c.K_KNOTS] +
              [c.COL_X_LEFT, c.COL_X_RIGHT, S["SF"][0], U["U3"][0],
               S["sb_bezier"][0][0], S["sb_bezier"][3][0]] +
              [s["g"][0] for s in strings] +
              [s["Nf_flat"][0] for s in strings])
    z_vals = ([k[1] for k in c.K_KNOTS] + [F, S["sb_bezier"][0][1],
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

    # Chamber body: closed path along un-raked SB top + un-raked B-locus + floor
    sb_top_pts = []
    for t in np.linspace(0, 1, 80):
        sb_top_pts.append(c.bez(*S["sb_bezier"], t))
    Bs = [st["D"] + st["diam"] * st["perp"] for st in sts]
    body_pts = sb_top_pts + Bs[::-1] + [np.array([U["U3"][0], 0.0]),
                                        np.array([S["SF"][0], 0.0])]
    body_d = "M " + " L ".join(f"{p[0]:.2f} {p[1]:.2f}" for p in body_pts) + " Z"
    elems.append(f'<path d="{body_d}" fill="{PAL["chamber_fill"]}" '
                 f'stroke="{PAL["chamber_edge"]}" stroke-width="1.5" '
                 f'stroke-linejoin="round"/>')

    # Soundboard (green un-raked SB Bezier)
    elems.append(f'<path d="{bez_to_d(*S["sb_bezier"])}" '
                 f'fill="none" stroke="{PAL["soundboard"]}" stroke-width="1.5"/>')
    elems.append(f'<path d="{bez_to_d(*S["sb_extension"])}" '
                 f'fill="none" stroke="{PAL["soundboard"]}" stroke-width="1.0" '
                 f'stroke-dasharray="4,3" opacity="0.7"/>')
    elems.append(f'<path d="{bez_to_d(*S["bass_tail_front"])}" '
                 f'fill="none" stroke="{PAL["chamber_edge"]}" stroke-width="1.0"/>')

    # Floor limacon segment (gold dashed reference)
    elems.append(f'<line x1="{S["SF"][0]:.2f}" y1="0" x2="{U["U3"][0]:.2f}" y2="0" '
                 f'stroke="{PAL["ref_dashed"]}" stroke-width="1.2" '
                 f'stroke-dasharray="6,4" opacity="0.85"/>')

    # Limacon stations (faint cross-bars D->B, un-raked)
    for st in sts:
        D = st["D"]; B = D + st["diam"] * st["perp"]
        elems.append(f'<line x1="{D[0]:.2f}" y1="{D[1]:.2f}" '
                     f'x2="{B[0]:.2f}" y2="{B[1]:.2f}" '
                     f'stroke="{PAL["ref_dashed"]}" stroke-width="0.4" '
                     f'opacity="0.35"/>')

    # Neck Bezier loop: K_KNOTS raked so the loop's bass corner (K1) sits at
    # the (raked) column top and the loop encloses the -x-raked Nf buffers.
    for seg in neck_segs:
        seg_r = tuple(rake_xz(p) for p in seg)
        elems.append(f'<path d="{bez_to_d(*seg_r)}" '
                     f'fill="none" stroke="{PAL["neck"]}" stroke-width="1.0"/>')

    # Column: parallelogram raked -7 deg in x at rest
    col_top_dx = -c.K_KNOTS[0, 1] * TAN_RAKE
    col_pts = [
        (c.COL_X_LEFT,                F),
        (c.COL_X_RIGHT,               F),
        (c.COL_X_RIGHT + col_top_dx,  c.K_KNOTS[0, 1]),
        (c.COL_X_LEFT  + col_top_dx,  c.K_KNOTS[0, 1]),
    ]
    pts_str = " ".join(f"{x:.2f},{y:.2f}" for x, y in col_pts)
    elems.append(f'<polygon points="{pts_str}" '
                 f'fill="{PAL["column"]}" fill-opacity="0.35" '
                 f'stroke="{PAL["neck"]}" stroke-width="0.8"/>')

    # Strings: grommet on SB, top raked into -x (csv.z encodes the rake)
    for s in strings:
        col = string_colour(s["note"])
        w = string_width(s["OD"])
        elems.append(f'<line x1="{s["g"][0]:.2f}" y1="{s["g"][2]:.2f}" '
                     f'x2="{s["Nf_flat"][0]:.2f}" y2="{s["Nf_flat"][2]:.2f}" '
                     f'stroke="{col}" stroke-width="{w:.3f}" '
                     f'stroke-linecap="round"/>')

    # Buffer disks (Nf_flat red, Nf_sharp blue) at the raked Nf positions
    for s in strings:
        elems.append(f'<circle cx="{s["Nf_flat"][0]:.2f}" cy="{s["Nf_flat"][2]:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#c00000" fill-opacity="0.13"/>')
        elems.append(f'<circle cx="{s["Nf_sharp"][0]:.2f}" cy="{s["Nf_sharp"][2]:.2f}" '
                     f'r="{c.CLEARANCE:.1f}" fill="#1060d0" fill-opacity="0.13"/>')

    # Anchor markers (body un-raked, neck raked)
    for pt in [S["sb_bezier"][0], S["sb_bezier"][3], S["SF"], U["U3"]]:
        elems.append(f'<circle cx="{pt[0]:.2f}" cy="{pt[1]:.2f}" '
                     f'r="2.0" fill="{PAL["label"]}"/>')
    for k in c.K_KNOTS:
        kr = rake_xz(k)
        elems.append(f'<circle cx="{kr[0]:.2f}" cy="{kr[1]:.2f}" '
                     f'r="2.0" fill="{PAL["label"]}"/>')

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
    z_max_view = c.K_KNOTS[:, 1].max() + 50
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
    S = c.compute_S_full()
    sb_bez = S["sb_bezier"]
    sb_ext = S["sb_extension"]
    ts_sb, arc_sb = c.bez_arclen_table(*sb_bez, n=2000)
    ts_ex, arc_ex = c.bez_arclen_table(*sb_ext, n=500)
    L_sb = float(arc_sb[-1])
    L_total = L_sb + float(arc_ex[-1])

    # Map grommet x to arc length along the SBB->G7g portion.
    s_samples = np.linspace(0, L_sb, 2000)
    x_samples = np.array([
        _D_and_perp_at_arclen(s, sb_bez, sb_ext, ts_sb, arc_sb, ts_ex, arc_ex, L_sb)[0][0]
        for s in s_samples
    ])

    sts = []
    for s in np.linspace(0.0, L_sb, 180):
        D, perp = _D_and_perp_at_arclen(s, sb_bez, sb_ext, ts_sb, arc_sb,
                                          ts_ex, arc_ex, L_sb)
        frac = s / L_total
        diam = BASE_DIAM * (1 - frac) + TOP_DIAM * frac
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
