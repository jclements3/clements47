#!/usr/bin/env python3
"""make_neck_edit_svg.py - emit clements47_neck_edit.svg for Inkscape.

WARNING: this script OVERWRITES any user edits in clements47_neck_edit.svg.
Run only when you want a fresh template; pass --force to confirm.

Layout: standard SVG y-down. Coordinates are at-rest xz from clements47.py
mirrored to (x, -z) so the harp draws upright in Inkscape.

Convention used by the optimizer (you can change colors to switch):
    fill='#cc0000' (red) -> fixed knot (anchored, optimizer must not move)
    fill='#000000' (black) -> free knot (optimizer is allowed to move)

Anchor handles (control points) are drawn as small grey circles connected to
their parent K-knot by a thin grey line. Grab them in Inkscape to set the
in/out tangent direction and length.

Saved knot/handle positions read by parse_neck_edit_svg.py (TODO).
"""
import os
import sys
import numpy as np
import clements47 as c

if "--force" not in sys.argv and os.path.exists(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "clements47_neck_edit.svg")):
    print("clements47_neck_edit.svg already exists. Pass --force to overwrite.")
    sys.exit(0)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "clements47_neck_edit.svg")

# N_KNOTS source-of-truth (10 rows, CCW). For this Inkscape template we
# walk the CW path order and inject the chamber back-wall corner detour
# (U't, Ut, St, S't) between K5 (= N6 = Ut) and K7 (= N4) so the user can
# edit those reference points too.
N_orig = c.N_KNOTS
# Legacy K-array view (9 rows, CW order K1..K9). Keeps the rest of the
# script's K[i] indexing semantics intact.
K_orig = N_orig[[0, 9, 8, 7, 6, 5, 4, 3, 2]]

# Path knots, in order (12 total):
#   K1 (col-top, fixed)
#   K2, K3, K4, K5/U1 (free)
#   U't (back-wall = B-locus at chamber arclength s_at_St; B-locus is
#         derived from S't + D(s_at_St) * perp_into; FIXED — its xz follows
#         from S't and the chamber diameter at top)
#   Ut, St, S't (three more fixed reference points)
#   K7, K8 (free)
#   K9 (col-bot, fixed)
_S   = c.compute_S_full()
_St_phantom = _S["sprime_treb_phantom"]                         # S't = treble phantom
_St_g7g     = c.SB_P3                                           # St  = G7g (treble end of S)
_Dp_S,  _perp_S = c.chamber_axis(c.s_at_St)
_U_at_St = _Dp_S + c.diam_at_s(c.s_at_St) * _perp_S             # U't = B-locus at S't
_Dp_Sg, _perp_Sg = c.chamber_axis(c._CHAMBER['s_at_G7g'])
_U_at_G7g = _Dp_Sg + c.diam_at_s(c._CHAMBER['s_at_G7g']) * _perp_Sg  # Ut = B-locus at St

# Path order goes around the chamber-top corner: down the back wall (U't,
# Ut) then across to the soundboard side (St, S't), then on to K7.
K = np.array([
    K_orig[0],     # K1 (= N0)
    K_orig[1],     # K2 (= N9)
    K_orig[2],     # K3 (= N8)
    K_orig[3],     # K4 (= N7)
    K_orig[4],     # K5/U1 (= N6)
    _U_at_St,      # U't   (B-locus at S't, top of back wall)
    _U_at_G7g,     # Ut    (B-locus at St=G7g, just below U't on back wall)
    _St_g7g,       # St    (G7g, top of actual soundboard)
    _St_phantom,   # S't   (phantom on SB extension)
    K_orig[6],     # K7 (= N4)
    K_orig[7],     # K8 (= N3)
    K_orig[8],     # K9 (= N2)
])
N = len(K)
FIXED = {0, 5, 6, 7, 8, 11}     # K1, U't, Ut, St, S't, K9

LABELS = ["K1 col-top", "K2", "K3", "K4 (above F7)", "K5/U1 BN shoulder",
          "U't", "Ut", "St (G7g)", "S't (phantom)",
          "K7", "K8", "K9 col-bot"]

# In/out tangent unit vectors -- match optimize_knots.build_neck_pts() and
# build_neck_segments() conventions.
def unit(v):
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

def cr(K, i):
    return unit(K[(i + 1) % N] - K[(i - 1) % N])

in_tan  = [None] * N
out_tan = [None] * N
for i in range(N):
    if i == 0:
        in_tan[i] = np.array([0.0, 1.0]); out_tan[i] = np.array([0.0, 1.0])
    elif i == 3:
        in_tan[i] = np.array([1.0, 0.0]); out_tan[i] = np.array([1.0, 0.0])
    elif i == 4:
        in_tan[i] = np.array([0.0, -1.0]); out_tan[i] = np.array([-1.0, 0.0])
    elif i == 5:
        in_tan[i] = np.array([-1.0, 0.0]); out_tan[i] = unit(K[(i + 1) % N] - K[i])
    elif i == 7:
        in_tan[i] = np.array([-0.9826, -0.1859])
        out_tan[i] = np.array([-0.9826, -0.1859])
    elif i == N - 1:
        in_tan[i] = np.array([0.0, -1.0]); out_tan[i] = np.array([0.0, 1.0])
    else:
        t = cr(K, i)
        in_tan[i] = t; out_tan[i] = t

# Handle endpoints. Length = |chord to previous/next| / 3.
def handle_len(i_from, i_to):
    return np.linalg.norm(K[i_to] - K[i_from]) / 3.0

in_handles  = []
out_handles = []
for i in range(N):
    j_prev = (i - 1) % N
    j_next = (i + 1) % N
    h_in  = handle_len(j_prev, i)
    h_out = handle_len(i, j_next)
    in_handles.append (K[i] - h_in  * in_tan[i])
    out_handles.append(K[i] + h_out * out_tan[i])

# Reference geometry: SB Bezier, BTF curve, floor, column, buffers
S = c.compute_S_full()
sb = S["sb_bezier"]; btf = S["bass_tail_front"]; sb_ext = S["sb_extension"]
SF = S["SF"]
COL_X_LEFT = c.COL_X_LEFT; COL_X_RIGHT = c.COL_X_RIGHT
F = S["F"]

# Buffer disks from strings.csv (relevant only the ones near the neck).
import csv as _csv
TAN_RAKE  = float(np.tan(np.radians(c.RAKE_DEG)))
def grommet_z_on_S(x):
    return c.grommet_z_on_S(x)
buffers = []
strings_csv = os.path.join(HERE, "strings.csv")
with open(strings_csv) as f:
    clean = "\n".join(ln for ln in f if not ln.lstrip().startswith("#") and ln.strip())
for r in _csv.DictReader(clean.splitlines()):
    def fn(k):
        v = (r.get(k) or "").strip(); return float(v) if v else 0.0
    Ng_x = fn("Ng_x_mm"); Ng_y = fn("Ng_y_mm")
    gz = grommet_z_on_S(Ng_x);  gz = gz if gz is not None else Ng_y + c.Z_OFFSET
    for which, color in (("Nf_flat", "#c00000"), ("Nf_sharp", "#1060d0")):
        dx = fn(which + "_x_mm"); dy = fn(which + "_y_mm"); dz = fn(which + "_z_mm")
        Nf_x = dx - dz; Nf_z = gz + (dy - Ng_y)
        buffers.append((float(Nf_x), float(Nf_z), color))

# --- Bounds (in xz; y in svg = -z) -----------------------------------------
xs = [k[0] for k in K] + [c.COL_X_LEFT, c.COL_X_RIGHT, SF[0], sb[3][0], sb[0][0]]
zs = [k[1] for k in K] + [F, sb[0][1], sb[3][1]]
xs += [b[0] for b in buffers] + [h[0] for h in in_handles] + [h[0] for h in out_handles]
zs += [b[1] for b in buffers] + [h[1] for h in in_handles] + [h[1] for h in out_handles]
x_min = min(xs) - 60; x_max = max(xs) + 60
z_min = min(zs) - 60; z_max = max(zs) + 60
W = x_max - x_min; H = z_max - z_min

def to_svg(x, z):  # SVG y-down
    return (x - x_min, (z_max - z))

# --- Build SVG --------------------------------------------------------------
def bez(P0, P1, P2, P3, t):
    return ((1 - t) ** 3) * P0 + 3 * (1 - t) ** 2 * t * P1 + \
           3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3

elems = []

def bez_path(P0, P1, P2, P3):
    a = to_svg(*P0); b = to_svg(*P1); c2 = to_svg(*P2); d = to_svg(*P3)
    return f'M {a[0]:.2f},{a[1]:.2f} C {b[0]:.2f},{b[1]:.2f} {c2[0]:.2f},{c2[1]:.2f} {d[0]:.2f},{d[1]:.2f}'

# Column outline (raked parallelogram from K1 LEFT-TOP to K9 LEFT-BOTTOM,
# extended down to the floor). Reference geometry, not part of the editable
# neck path.
K1_pt = K[0]; K9_pt = K[N - 1]
col_top_x_left  = K1_pt[0]; col_top_x_right = col_top_x_left  + (COL_X_RIGHT - COL_X_LEFT)
col_bot_x_left  = K9_pt[0]; col_bot_x_right = col_bot_x_left  + (COL_X_RIGHT - COL_X_LEFT)
def pt2(x, y): return f"{to_svg(x,y)[0]:.2f},{to_svg(x,y)[1]:.2f}"
elems.append(f'<polygon points="'
             f'{pt2(COL_X_LEFT, F)} {pt2(COL_X_RIGHT, F)} '
             f'{pt2(col_bot_x_right, K9_pt[1])} '
             f'{pt2(col_top_x_right, K1_pt[1])} '
             f'{pt2(col_top_x_left, K1_pt[1])} '
             f'{pt2(col_bot_x_left, K9_pt[1])}" '
             f'fill="#bbb" fill-opacity="0.30" stroke="#666" stroke-width="0.8"/>')

# Buffer disks (Nf_flat red, Nf_sharp blue) -- the keep-out cluster the
# neck loop must enclose with CLEARANCE = 8 mm margin.
for bx, bz, col in buffers:
    sx, sy = to_svg(bx, bz)
    elems.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{c.CLEARANCE:.1f}" '
                 f'fill="{col}" fill-opacity="0.13" stroke="none"/>')

# Soundboard S: solid green Bezier (SBB -> G7g).
elems.append(f'<path d="{bez_path(*sb)}" fill="none" stroke="#0a7" stroke-width="1.2"/>')
# S' phantom extensions (dotted green): straight tangent lines at both ends
# of the SB Bezier. Top extends G7g -> S't; bottom extends SBB <- S'b. These
# match how S't and S'b are defined in clements47.compute_S_full.
SBB = sb[0]; G7g = sb[3]
tan0 = c.bez_tan(*sb, 0.0); tan0_unit = tan0 / np.linalg.norm(tan0)
tan1 = c.bez_tan(*sb, 1.0); tan1_unit = tan1 / np.linalg.norm(tan1)
ext_top = G7g + 1.10 * c._CHAMBER['ext_t_len'] * tan1_unit
ext_bot = SBB - 1.10 * c._CHAMBER['ext_b_len'] * tan0_unit
for p_a, p_b in ((G7g, ext_top), (SBB, ext_bot)):
    g_a = to_svg(*p_a); g_b = to_svg(*p_b)
    elems.append(f'<line x1="{g_a[0]:.2f}" y1="{g_a[1]:.2f}" '
                 f'x2="{g_b[0]:.2f}" y2="{g_b[1]:.2f}" '
                 f'stroke="#0a7" stroke-width="0.9" stroke-dasharray="4,3"/>')

# U' (chamber back wall reference): U1 -> U2 -> U3 as solid magenta Bezier
# segments. U continuation U3 -> U4 (floor segment) as dashed magenta.
U_data = c.compute_U(_S["F"])
for key in ("seg1", "seg2"):
    elems.append(f'<path d="{bez_path(*U_data[key])}" fill="none" '
                 f'stroke="#a000a0" stroke-width="1.0" opacity="0.85"/>')
# seg3 is U3 -> U4 along the floor (the U continuation past U' into U).
elems.append(f'<path d="{bez_path(*U_data["seg3"])}" fill="none" '
             f'stroke="#a000a0" stroke-width="0.9" stroke-dasharray="4,3" '
             f'opacity="0.75"/>')

# Limacon cross-section diameters at four soundboard reference points.
# Region boundaries (top to bottom):
#   neck     <- Et (external tangent to G7 Nf-flat / Nf-sharp buffer disks)
#   ELBOW    <- Eb = Ht = St -> Ut (chamber cap at G7g, half-limacon morph
#                                   zone between Eb and Et)
#   chamber  <- Hb = S'b -> U'b (where hollow chamber meets solid CF base)
#   solid base
#   floor
# Other reference: Sb -> Ub at SBB / C1g (informational, not a region boundary).
# All shown as red dashed lines.
_Dp_Sb,  _p_Sb  = c.chamber_axis(c.s_at_SBB)
_Ub      = _Dp_Sb + c.diam_at_s(c.s_at_SBB) * _p_Sb
_Dp_Spb, _p_Spb = c.chamber_axis(c._CHAMBER['s_at_Sprime_b'])
_Upb     = _Dp_Spb + c.diam_at_s(c._CHAMBER['s_at_Sprime_b']) * _p_Spb
for D_pt, B_pt in ((_St_phantom, _U_at_St),     # S't -> U't  (D = 85.85)
                   (_St_g7g,     _U_at_G7g),    # St  -> Ut   (D = 92.88)
                   (c.SB_P0,     _Ub),          # Sb  -> Ub   (D = 290.05)
                   (_Dp_Spb,     _Upb)):        # S'b -> U'b  (D = 290.00)
    da = to_svg(*D_pt); db = to_svg(*B_pt)
    elems.append(f'<line x1="{da[0]:.2f}" y1="{da[1]:.2f}" '
                 f'x2="{db[0]:.2f}" y2="{db[1]:.2f}" '
                 f'stroke="#cc0000" stroke-width="1.0" '
                 f'stroke-dasharray="4,3" opacity="0.7"/>')

# Bass tail front (S continuation: SBB curving down to SF along the front).
btf_curve = _S["bass_tail_front"]
elems.append(f'<path d="{bez_path(*btf_curve)}" fill="none" stroke="#0a7" '
             f'stroke-width="0.9" opacity="0.7"/>')

# Neck-and-shoulder = ONE continuous open Bezier path through all 9 knots
# (K1 -> K2 -> K3 -> K4 -> K5 -> S't -> K7 -> K8 -> K9). The path starts at
# the column top, traces the top arc + shoulder, hands off to the soundboard
# extension at S't, and continues around the back to the column bottom.
neck_idx = list(range(N))         # 0..8 -> K1, K2, K3, K4, K5, S't, K7, K8, K9

def cubic_seg(i_start, i_end):
    P0 = K[i_start]; P3 = K[i_end]
    if (i_start, i_end) == (3, 4):                   # K4 -> K5  (CR-ish)
        t_out = unit(K[4] - K[2]); t_in = unit(K[4] - K[3])
    elif (i_start, i_end) == (4, 5):                 # K5 -> S't (CR-ish)
        t_out = unit(K[5] - K[4]); t_in = unit(K[6] - K[4])
    else:
        t_out = out_tan[i_start]; t_in = in_tan[i_end]
    h = np.linalg.norm(P3 - P0) / 3.0
    return P0 + h * t_out, P3 - h * t_in

a = to_svg(*K[neck_idx[0]])
neck_d = f'M {a[0]:.2f},{a[1]:.2f}'
# Generate cubic-Bezier segments for every consecutive pair AROUND the loop,
# i.e. last segment is K9 -> K1 (the closure). Range is N (not N-1) to wrap.
for k in range(N):
    i_from = neck_idx[k]
    i_to   = neck_idx[(k + 1) % N]
    P1, P2 = cubic_seg(i_from, i_to)
    P3 = K[i_to]
    p1 = to_svg(*P1); p2 = to_svg(*P2); p3 = to_svg(*P3)
    neck_d += f' C {p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f} {p3[0]:.2f},{p3[1]:.2f}'
neck_d += " Z"
elems.append(f'<path id="neck_path" d="{neck_d}" fill="none" '
             f'stroke="#1060d0" stroke-width="2.0" opacity="0.85"/>')

# Knot labels only -- NO dots/circles. Small black/red text next to each
# knot's location (red = fixed, black = free). Edit nodes via Inkscape's
# node tool (N).
LABEL_OFFSETS = {
    0:  ( 5, -3),   # K1
    1:  ( 5, -3),   # K2
    2:  ( 5, -3),   # K3
    3:  ( 5, -3),   # K4
    4:  ( 5, -3),   # K5/U1
    5:  ( 5, -3),   # U't
    6:  (-22,  9),  # Ut
    7:  (-22, -3),  # St
    8:  ( 5, -3),   # S't
    9:  ( 5, -3),   # K7
    10: ( 5, -3),   # K8
    11: ( 5,  4),   # K9
}
for i in range(N):
    sx, sy = to_svg(*K[i])
    fill = "#cc0000" if i in FIXED else "#000000"
    dx, dy = LABEL_OFFSETS.get(i, (5, -3))
    elems.append(f'<text x="{sx + dx:.1f}" y="{sy + dy:.1f}" '
                 f'font-family="sans-serif" font-size="9" font-weight="600" '
                 f'fill="{fill}">{LABELS[i]}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
       f'viewBox="0 0 {W:.1f} {H:.1f}" width="{W:.1f}" height="{H:.1f}">\n  ' +
       "\n  ".join(elems) + "\n</svg>\n")

with open(OUT, "w") as f:
    f.write(svg)
print(f"wrote {OUT}  ({W:.0f} x {H:.0f} mm)")
