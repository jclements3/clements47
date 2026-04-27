#!/usr/bin/env python3
"""
erard47.py - 47-string concert pedal harp (Erard-spec) geometry generator.

Outputs harp profile as SVG.

Coordinate system:
  +x across (treble side), +z up (toward neck), +y depth (away from player).
  Strings rake 7 deg back from vertical. Profile views in xz plane.
  Origin at the FLOOR (bass tail tip touches z=0).

String physics (note, OD, L_flat, L_nat, L_sharp, f_nat, material) is read
from strings.csv. Positions (x, z, Nf, Ns) are computed from the geometry
constants below.

Acoustic naming:
  S' = SB Bezier alone (with phantom grommets +/- 2 air gaps beyond C1, G7).
  U' = U1 -> U2 -> U3 (chamber back wall, no floor segment).
  S  = S' + SB extension to K6 + bass tail front Bezier.
  U  = U' + U3 -> U4 floor segment.
"""
import argparse
import csv
import os
import sys
import numpy as np
from scipy.optimize import brentq

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

AIR_GAP = 13.0   # matches strings.csv center_spacing convention (was 15)
RAKE_DEG = 7.0
COS_R = np.cos(np.radians(RAKE_DEG))
SIN_R = np.sin(np.radians(RAKE_DEG))

# Origin is at the FLOOR. SBB sits at z = Z_OFFSET above the floor.
# Z_OFFSET = the height SBB sits above the floor (= length of bass tail
# projected onto z-axis, derived from the SB tangent at t=0).
# Computed from the unshifted SB Bezier; applied to all z constants below.
Z_OFFSET = 186.778715  # SBB height above floor

# SB Bezier control points: VERIFIED against strings.csv comments. The csv
# documents these as the soundboard curve, so the canonical SB Bezier ends
# at G7g where the csv cumulative spacing puts it (x = 643.29).
SB_P0 = np.array([  0.00,         0.0   + Z_OFFSET])   # = SBB at C1g
SB_P1 = np.array([325.29,    971.14   + Z_OFFSET])
SB_P2 = np.array([350.50,   1142.59   + Z_OFFSET])
SB_P3 = np.array([643.29,   1477.0    + Z_OFFSET])     # = G7g (csv canonical)

BASS_TAIL_LEN = 200.0

# U2 placement: arc-fraction along S, perpendicular depth into chamber
U2_S_FRAC = 0.50
U2_DEPTH = 250.0

# U floor extension length
U_FLOOR_LEN = 538.46   # floor lima\u00e7on D-to-B: D=SF, B=floor_end (below B1)
FLOOR_EXTENSION = 0.0  # B_floor coincides with floor_end (below B1 at x=466.95)

# Column footprint. Scaled by csv ratio (643.29/735.29 = 0.8748) so K1, K9
# (column corners) line up with the column LEFT face after the SB Bezier
# was rescaled to fit strings.csv.
COL_X_LEFT = -43.74          # = -50.00 * 0.8748
COL_X_RIGHT = -15.75         # = -18.00 * 0.8748
COL_TOP_Z = 1600.0 + Z_OFFSET

# Neck knots K1-K9. x values scaled by 0.8748 (= csv G7g.x / clements G7g.x)
# so K4 and K6 land exactly at csv's G7g (x=643.29) and the rest of the
# neck is proportionally fitted to the modern-string-set soundboard.
K_KNOTS = np.array([
    [ -43.74,  1600.00 + Z_OFFSET],  # K1 - column left top
    [  89.99,  1680.00 + Z_OFFSET],  # K2 - top arc bass peak
    [ 380.05,  1610.00 + Z_OFFSET],  # K3 - S-knot
    [ 643.29,  1753.04],             # K4 - top arc treble end (touches F7 Nf top buffer)
    [ 699.94,  1525.00 + Z_OFFSET],  # K5 = U1 (BN) shoulder
    [ 643.29,  1725.06],             # K6 = SBN (touches G7 Ns buffer bottom)
    [ 519.93,  1500.00 + Z_OFFSET],  # K7
    [ 260.01,  1475.00 + Z_OFFSET],  # K8
    [ -43.74,  1450.00],             # K9 - column LEFT bottom corner
])

# Buffer disk radius around grommets (Nf, Ns)
CLEARANCE = 8.0

def load_strings_from_csv(csv_path):
    """Read note, OD, lengths, frequency from strings.csv.

    Position columns in the CSV are IGNORED — they reflect an older coord
    system. Positions are computed from this script's geometry constants.
    """
    rows = []
    with open(csv_path) as f:
        # Strip comment lines (starting with #)
        clean = '\n'.join(ln for ln in f if not ln.lstrip().startswith('#') and ln.strip())
    reader = csv.DictReader(clean.splitlines())
    for r in reader:
        rows.append((
            r['note'],
            float(r['OD_mm']),
            float(r['L_flat_mm']),
            float(r['L_nat_mm']),
            float(r['L_sharp_mm']),
            float(r['f_nat_Hz']),
        ))
    return rows

# Default CSV location: same directory as this script, then /mnt/project/, then cwd
def _find_strings_csv():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, 'strings.csv'),
                 '/mnt/project/strings.csv',
                 'strings.csv'):
        if os.path.isfile(cand):
            return cand
    raise FileNotFoundError('strings.csv not found (looked in script dir, /mnt/project/, cwd)')

STRINGS_CSV_PATH = _find_strings_csv()
STRINGS = load_strings_from_csv(STRINGS_CSV_PATH)

# ---------------------------------------------------------------------------
# Bezier helpers
# ---------------------------------------------------------------------------

def bez(P0, P1, P2, P3, t):
    """Cubic Bezier evaluation. t scalar or array."""
    if np.isscalar(t):
        return ((1 - t) ** 3) * P0 + 3 * (1 - t) ** 2 * t * P1 + \
               3 * (1 - t) * t ** 2 * P2 + t ** 3 * P3
    return ((1 - t) ** 3)[:, None] * P0 + (3 * (1 - t) ** 2 * t)[:, None] * P1 + \
           (3 * (1 - t) * t ** 2)[:, None] * P2 + (t ** 3)[:, None] * P3

def bez_tan(P0, P1, P2, P3, t):
    """Bezier tangent vector."""
    return 3 * (1 - t) ** 2 * (P1 - P0) + \
           6 * (1 - t) * t * (P2 - P1) + \
           3 * t ** 2 * (P3 - P2)

def bez_arclen_table(P0, P1, P2, P3, n=2000):
    """Return (ts, arc_lengths) from t=0 to t=1."""
    ts = np.linspace(0, 1, n)
    pts = bez(P0, P1, P2, P3, ts)
    arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
    return ts, arc

# ---------------------------------------------------------------------------
# Geometry computations
# ---------------------------------------------------------------------------

def compute_string_positions():
    """Return list of dicts with x, z (grommet position) for each string."""
    out = []
    x_cumulative = 0.0
    for i, (note, OD, Lf, Ln, Ls, fn) in enumerate(STRINGS):
        if i > 0:
            prev_OD = STRINGS[i - 1][1]
            spacing = AIR_GAP + (prev_OD + OD) / 2
            x_cumulative += spacing
        out.append({
            'note': note, 'OD': OD,
            'L_flat': Lf, 'L_nat': Ln, 'L_sharp': Ls,
            'f_nat': fn, 'x': x_cumulative,
        })
    return out

def grommet_z_on_S(x):
    """Find z position on SB Bezier given x coordinate."""
    # Endpoints: SBB at x=0 (z=Z_OFFSET) and G7g at x=SB_P3[0] (z=SB_P3[1]).
    if x == 0:
        return SB_P0[1]
    if x == SB_P3[0]:
        return SB_P3[1]
    if x < 0 or x > SB_P3[0]:
        return None
    def fx(t):
        return ((1 - t) ** 3) * SB_P0[0] + 3 * (1 - t) ** 2 * t * SB_P1[0] + \
               3 * (1 - t) * t ** 2 * SB_P2[0] + t ** 3 * SB_P3[0] - x
    t = brentq(fx, 0, 1)
    return ((1 - t) ** 3) * SB_P0[1] + 3 * (1 - t) ** 2 * t * SB_P1[1] + \
           3 * (1 - t) * t ** 2 * SB_P2[1] + t ** 3 * SB_P3[1]

def compute_phantom_grommets(strings):
    """Return phantom_bass and phantom_treble positions (2 air gaps beyond)."""
    OD_C1 = strings[0]['OD']
    OD_G7 = strings[-1]['OD']
    phantom_bass_x = strings[0]['x'] - 2 * AIR_GAP - OD_C1
    phantom_treb_x = strings[-1]['x'] + 2 * AIR_GAP + OD_G7
    return phantom_bass_x, phantom_treb_x

def compute_S_full():
    """Return all S components: S' Bezier (with phantom span), SB extension to
    K6, bass tail front Bezier.

    The original SB Bezier covers C1g (t=0) to G7g (t=1). To incorporate
    phantom grommets at +/- 2 air gaps, we extend S' by ext_b (bass) and
    ext_t (treble) in-line with the Bezier tangents at the endpoints.
    """
    strings = compute_string_positions()
    phantom_b_x, phantom_t_x = compute_phantom_grommets(strings)

    # Bass extension: tangent at t=0 (forward), so backward direction is
    # negative of that. Length = abs(phantom_b_x - C1g.x) along that direction.
    tan0 = bez_tan(SB_P0, SB_P1, SB_P2, SB_P3, 0.0)
    tan0_unit = tan0 / np.linalg.norm(tan0)
    # Backward extension start point = SB_P0 (C1g) extended along -tan0_unit
    # such that x reaches phantom_b_x.
    if abs(tan0_unit[0]) < 1e-9:
        ext_b_len = 0
    else:
        ext_b_len = (SB_P0[0] - phantom_b_x) / tan0_unit[0]
    sprime_bass = SB_P0 - ext_b_len * tan0_unit

    # Treble extension: tangent at t=1, extend forward
    tan1 = bez_tan(SB_P0, SB_P1, SB_P2, SB_P3, 1.0)
    tan1_unit = tan1 / np.linalg.norm(tan1)
    if abs(tan1_unit[0]) < 1e-9:
        ext_t_len = 0
    else:
        ext_t_len = (phantom_t_x - SB_P3[0]) / tan1_unit[0]
    sprime_treb = SB_P3 + ext_t_len * tan1_unit

    # Full SB extension to K6 (sbn)
    sbn = K_KNOTS[5]
    h_sb = (np.linalg.norm(sbn - SB_P3) / 3) * 2
    sb_ext = (SB_P3, SB_P3 + h_sb * tan1_unit, sbn + h_sb * np.array([1.0, 0.0]), sbn)

    # Bass tail front Bezier from SBB to SF (vertical handle at SF, length 30mm).
    backward = -tan0_unit
    SF = SB_P0 + BASS_TAIL_LEN * backward   # SF on floor at z=0
    chord = np.linalg.norm(SF - SB_P0)
    h_btf_out = chord / 3                # outgoing handle from SBB
    h_sf_in = 30.0                       # incoming vertical handle at SF
    btf = (SB_P0, SB_P0 + h_btf_out * backward,
           SF + h_sf_in * np.array([0.0, 1.0]), SF)

    return {
        'sb_bezier': (SB_P0, SB_P1, SB_P2, SB_P3),
        'sprime_bass_phantom': sprime_bass,   # outer bass end of S'
        'sprime_treb_phantom': sprime_treb,   # outer treble end of S'
        'sb_extension': sb_ext,               # G7g -> sbn (K6)
        'bass_tail_front': btf,               # SBB -> SF
        'SF': SF,
        'F': SF[1],
    }

def compute_U(F):
    """Return U knots and segments. U = U1 -> U2 -> U3 -> U4."""
    # U1 at K5
    U1 = K_KNOTS[4].copy()
    # U2 at s_frac along SB Bezier arc, perpendicular depth into chamber
    ts_fine, arc = bez_arclen_table(SB_P0, SB_P1, SB_P2, SB_P3)
    s_peak = U2_S_FRAC * arc[-1]
    t_peak = np.interp(s_peak, arc, ts_fine)
    sb_at_peak = bez(SB_P0, SB_P1, SB_P2, SB_P3, t_peak)
    sb_tan_peak = bez_tan(SB_P0, SB_P1, SB_P2, SB_P3, t_peak)
    sb_tan_peak = sb_tan_peak / np.linalg.norm(sb_tan_peak)
    perp_right = np.array([sb_tan_peak[1], -sb_tan_peak[0]])
    U2 = sb_at_peak + U2_DEPTH * perp_right

    # U4 = SF (tail tip)
    tan0 = bez_tan(SB_P0, SB_P1, SB_P2, SB_P3, 0.0)
    backward = -tan0 / np.linalg.norm(tan0)
    U4 = SB_P0 + BASS_TAIL_LEN * backward

    # U3 = U4 + 500mm in +x direction
    U3 = np.array([U4[0] + U_FLOOR_LEN, F])

    # Segments with handle conventions:
    # U1->U2: leave U1 going (0,-1), arrive at U2 along peak_to_U3 direction
    peak_to_U3 = (U3 - U2) / np.linalg.norm(U3 - U2)
    h1 = np.linalg.norm(U2 - U1) / 3
    seg1 = (U1, U1 + h1 * np.array([0.0, -1.0]), U2 - h1 * peak_to_U3, U2)

    # U2->U3: leave U2 along peak_to_U3, arrive at U3 vertically (handle UP from U3)
    h2 = np.linalg.norm(U3 - U2) / 3
    seg2 = (U2, U2 + h2 * peak_to_U3, U3 + h2 * np.array([0.0, 1.0]), U3)

    # U3->U4: leave U3 horizontally (-1,0), arrive at U4 horizontally
    h3 = np.linalg.norm(U4 - U3) / 3
    seg3 = (U3, U3 + h3 * np.array([-1.0, 0.0]), U4 - h3 * np.array([-1.0, 0.0]), U4)

    return {
        'U1': U1, 'U2': U2, 'U3': U3, 'U4': U4,
        'seg1': seg1, 'seg2': seg2, 'seg3': seg3,
    }

def build_neck_segments():
    """Return list of (P0, P1, P2, P3) cubic Bezier segments connecting K1->K2->...->K10->K1.

    Tangent conventions:
      K1: in horizontal-left (from K10 below going up); out vertical-up (to K2)
      K4 (top arc end), K5 (treble cap), K6 (sbn): special
      K10: in from K9 (Catmull-Rom-ish); out vertical-up (toward K1)
      Others: Catmull-Rom from neighbors.
    """
    QARC = (4.0 / 3.0) * (np.sqrt(2) - 1)

    def unit(v):
        n = np.linalg.norm(v)
        return v / n if n > 0 else v
    def cr(K, i):
        n = len(K)
        return unit(K[(i + 1) % n] - K[(i - 1) % n])

    K = K_KNOTS
    n = len(K)
    in_tan = [None] * n
    out_tan = [None] * n
    for i in range(n):
        next_pt = K[(i + 1) % n]
        if i == 0:
            # K1: comes from K10 below (vertical up), exits toward K2
            in_tan[i] = np.array([0.0, 1.0])  # arriving going up
            out_tan[i] = np.array([0.0, 1.0])  # leaving going up
        elif i == 3:
            # K4: top arc treble end
            in_tan[i] = np.array([1.0, 0.0])
            out_tan[i] = np.array([1.0, 0.0])
        elif i == 4:
            # K5 (treble cap right): incoming horizontal/down, outgoing horizontal-left
            in_tan[i] = np.array([0.0, -1.0])
            out_tan[i] = np.array([-1.0, 0.0])
        elif i == 5:
            # K6 (sbn): incoming horizontal-left, outgoing toward K7
            in_tan[i] = np.array([-1.0, 0.0])
            out_tan[i] = unit(next_pt - K[i])
        elif i == 7:
            # K8: collinear handles for smooth (G1) flow through K8.
            # Tangent direction set so K8->K9 path just touches A1 Ns buffer (8mm).
            in_tan[i] = np.array([-0.9826, -0.1859])
            out_tan[i] = np.array([-0.9826, -0.1859])
        elif i == n - 1:
            # K9 (last knot, the column bottom corner): incoming vertical-DOWN
            # (mirrors K1's vertical-up outgoing, giving K8->K9 a quarter-arc
            # shape mirroring K1->K2), outgoing vertical-UP (toward K1 along
            # column left edge).
            in_tan[i] = np.array([0.0, -1.0])
            out_tan[i] = np.array([0.0, 1.0])
        else:
            t = cr(K, i)
            in_tan[i] = t
            out_tan[i] = t

    segs = []
    for i in range(n):
        j = (i + 1) % n
        # Skip K4->K5 segment (i=3): replaced by limaçon B-locus
        # Skip K5->K6 segment (i=4): replaced by combined U+S+SB-extension path
        if i == 3 or i == 4:
            continue
        P0 = K[i].copy()
        P3 = K[j].copy()
        if i == 4 and j == 5:
            dx = abs(P3[0] - P0[0])
            dy = abs(P3[1] - P0[1])
            h_out = QARC * dx
            h_in = QARC * dy
        else:
            hh = np.linalg.norm(P3 - P0) / 3
            h_out = h_in = hh
        P1 = P0 + h_out * out_tan[i]
        P2 = P3 - h_in * in_tan[j]
        segs.append((P0, P1, P2, P3))
    return segs

# ---------------------------------------------------------------------------
# SVG output
# ---------------------------------------------------------------------------

def bez_to_svg(P0, P1, P2, P3):
    """Return SVG path data (M ... C ...) for a cubic Bezier."""
    return (f"M {P0[0]:.2f} {P0[1]:.2f} "
            f"C {P1[0]:.2f} {P1[1]:.2f}, {P2[0]:.2f} {P2[1]:.2f}, "
            f"{P3[0]:.2f} {P3[1]:.2f}")

def write_svg(out_path, label_knots=True, show_handles=False, show_buffers=True):
    """Generate SVG harp profile."""
    strings = compute_string_positions()
    S_data = compute_S_full()
    U = compute_U(S_data['F'])
    neck_segs = build_neck_segments()

    # Compute Nf, Ns positions for each grommet
    for s in strings:
        z = grommet_z_on_S(s['x'])
        s['z'] = z
        s['Nf_z'] = z + s['L_flat'] * COS_R
        s['Ns_z'] = z + s['L_sharp'] * COS_R
        s['Nf_y'] = -s['L_flat'] * SIN_R
        s['Ns_y'] = -s['L_sharp'] * SIN_R

    # Bounding box for SVG viewBox
    F = S_data['F']
    sprime_b = S_data['sprime_bass_phantom']
    sprime_t = S_data['sprime_treb_phantom']
    x_min = min(COL_X_LEFT, sprime_b[0], U['U4'][0]) - 30
    x_max = max(U['U1'][0], sprime_t[0]) + 30
    z_min = F - 50
    z_max = max(K_KNOTS[:, 1].max(), max(s['Nf_z'] for s in strings)) + 50
    width = x_max - x_min
    height = z_max - z_min

    # SVG: y-axis is inverted (SVG y increases downward, our z increases upward)
    # Use viewBox transform to flip z.
    svg = []
    svg.append(f'<?xml version="1.0" encoding="UTF-8"?>')
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'viewBox="{x_min:.1f} {-z_max:.1f} {width:.1f} {height:.1f}" '
               f'width="800" height="{int(800*height/width)}" '
               f'font-family="sans-serif" font-size="12">')
    # Top group flips z so +z is up
    svg.append('<g transform="scale(1, -1)">')

    # Floor F (dashed brown)
    svg.append(f'<line x1="{x_min:.1f}" y1="{F:.2f}" x2="{x_max:.1f}" y2="{F:.2f}" '
               f'stroke="brown" stroke-width="0.8" stroke-dasharray="6,4" opacity="0.6"/>')

    # Column C (gray polygon, top conforms to K1->K2 neck arc above column footprint)
    # K1 (left edge x=-50) is at z=1600. K1->K2 arc rises as x increases toward 0.
    # Column right edge at x=-18 meets K1->K2 at higher z. Trace K1->K2 from t=0
    # to t = t_at_xR (x = COL_X_RIGHT).
    K1K2 = neck_segs[0]  # P0=K1, P3=K2
    P0_a, P1_a, P2_a, P3_a = K1K2
    def _x_at(t):
        return ((1-t)**3)*P0_a[0] + 3*(1-t)**2*t*P1_a[0] + \
               3*(1-t)*t**2*P2_a[0] + t**3*P3_a[0]
    t_right_edge = brentq(lambda t: _x_at(t) - COL_X_RIGHT, 0, 1)
    arc_ts = np.linspace(0, t_right_edge, 30)
    arc_pts = bez(P0_a, P1_a, P2_a, P3_a, arc_ts)
    # Build polygon: start at bottom-left (CF_l), up left edge to K1,
    # along K1->K2 arc to (COL_X_RIGHT, z_at_right), down right edge to CF_r,
    # back along floor to CF_l.
    poly_pts = [
        (COL_X_LEFT, F),
        (COL_X_LEFT, P0_a[1]),  # K1 = (-50, 1600)
    ]
    for p in arc_pts:
        poly_pts.append((p[0], p[1]))
    poly_pts.append((COL_X_RIGHT, F))
    poly_d = ' '.join(f'{x:.2f},{y:.2f}' for x, y in poly_pts)
    svg.append(f'<polygon points="{poly_d}" '
               f'fill="gray" fill-opacity="0.4" stroke="gray" stroke-width="0.5"/>')

    # Buffer disks around Nf/Ns grommets
    if show_buffers:
        for s in strings:
            svg.append(f'<circle cx="{s["x"]:.2f}" cy="{s["Nf_z"]:.2f}" '
                       f'r="{CLEARANCE:.1f}" fill="red" fill-opacity="0.13"/>')
            svg.append(f'<circle cx="{s["x"]:.2f}" cy="{s["Ns_z"]:.2f}" '
                       f'r="{CLEARANCE:.1f}" fill="blue" fill-opacity="0.13"/>')

    # Strings (vertical lines from grommet to Nf)
    for s in strings:
        svg.append(f'<line x1="{s["x"]:.2f}" y1="{s["z"]:.2f}" '
                   f'x2="{s["x"]:.2f}" y2="{s["Nf_z"]:.2f}" '
                   f'stroke="red" stroke-width="0.3" opacity="0.4"/>')

    # ----- S (soundboard, blue) -----
    # S' phantom extension lines (dashed light blue, indicating phantom span)
    svg.append(f'<line x1="{sprime_b[0]:.2f}" y1="{sprime_b[1]:.2f}" '
               f'x2="{SB_P0[0]:.2f}" y2="{SB_P0[1]:.2f}" '
               f'stroke="lightblue" stroke-width="1" stroke-dasharray="3,3"/>')
    svg.append(f'<line x1="{SB_P3[0]:.2f}" y1="{SB_P3[1]:.2f}" '
               f'x2="{sprime_t[0]:.2f}" y2="{sprime_t[1]:.2f}" '
               f'stroke="lightblue" stroke-width="1" stroke-dasharray="3,3"/>')
    # SB Bezier (S' main)
    svg.append(f'<path d="{bez_to_svg(*S_data["sb_bezier"])}" '
               f'fill="none" stroke="blue" stroke-width="1.2"/>')
    # SB extension to K6
    svg.append(f'<path d="{bez_to_svg(*S_data["sb_extension"])}" '
               f'fill="none" stroke="blue" stroke-width="1.2"/>')
    # Bass tail front
    svg.append(f'<path d="{bez_to_svg(*S_data["bass_tail_front"])}" '
               f'fill="none" stroke="blue" stroke-width="1.2"/>')

    # ----- Limaçon series along ENTIRE S (SF -> SBB -> G7g -> K6),
    # gradient diameter from floor (500mm) to K6-K4 distance (24.54mm) -----
    SF_pt = S_data['SF']
    U3_pt = U['U3']
    base_diam = 500.0
    top_diam = np.linalg.norm(K_KNOTS[3] - K_KNOTS[5])  # K6 to K4 distance

    # S consists of two Bezier pieces traversed: sb_bezier (SBB->G7g),
    # sb_extension (G7g->K6). Bass tail front is skipped to avoid the
    # B-locus dipping inward where the bass-tail tangent rotates rapidly.
    sb_bez   = S_data['sb_bezier']         # SBB -> G7g
    sb_ext   = S_data['sb_extension']      # G7g -> K6

    # Arc length tables for each piece
    ts_sb, arc_sb = bez_arclen_table(*sb_bez, n=2000)
    ts_ex, arc_ex = bez_arclen_table(*sb_ext, n=500)
    L_sb = arc_sb[-1]
    L_ex = arc_ex[-1]
    L_total = L_sb + L_ex

    def D_and_perp_at_arclen(s_val):
        """s=0 at SBB, s=L_total at K6. Return D point and perp_into-chamber."""
        if s_val <= L_sb:
            ti = np.interp(s_val, arc_sb, ts_sb)
            D_pt = bez(*sb_bez, ti)
            t_dir = bez_tan(*sb_bez, ti)
        else:
            s_local = s_val - L_sb
            ti = np.interp(s_local, arc_ex, ts_ex)
            D_pt = bez(*sb_ext, ti)
            t_dir = bez_tan(*sb_ext, ti)
        t_dir = t_dir / np.linalg.norm(t_dir)
        perp = np.array([t_dir[1], -t_dir[0]])
        return D_pt, perp

    def diam_at_s(s_val):
        frac = s_val / L_total
        return base_diam * (1 - frac) + top_diam * frac

    # Compute B locus densely
    n_dense = 200
    ss_dense = np.linspace(0.0, L_total, n_dense)
    B_locus_full = []
    for s_val in ss_dense:
        D_pt, perp_into = D_and_perp_at_arclen(s_val)
        diam = diam_at_s(s_val)
        B_locus_full.append(D_pt + diam * perp_into)
    B_locus_full = np.array(B_locus_full)

    # B-locus starts at the extended floor endpoint (where the SBB lima\u00e7on
    # axis crosses z=0, B_floor + FLOOR_EXTENSION) then traces through the
    # lima\u00e7on B endpoints from SBB up to K6.
    floor_end_pt = np.array([U3_pt[0] + FLOOR_EXTENSION, 0.0])
    B_locus = np.vstack([floor_end_pt, B_locus_full])

    # Draw U as polyline through B locus
    u_path = 'M ' + ' L '.join(f'{p[0]:.2f} {p[1]:.2f}' for p in B_locus)
    svg.append(f'<path d="{u_path}" fill="none" stroke="magenta" stroke-width="1.2"/>')
    # Floor segment: from SF (bass tail tip on floor) to B_floor (= floor_end).
    floor_end_x = U['U3'][0] + FLOOR_EXTENSION
    svg.append(f'<line x1="{S_data["SF"][0]:.2f}" y1="{S_data["SF"][1]:.2f}" '
               f'x2="{floor_end_x:.2f}" y2="0" '
               f'stroke="magenta" stroke-width="1.5"/>')

    # Sample limaçon stations for visualization
    n_lim = 16
    sample_ss = np.linspace(0.0, L_total, n_lim)
    for s_val in sample_ss:
        D_pt, perp_into = D_and_perp_at_arclen(s_val)
        diam = diam_at_s(s_val)
        B_pt_lim = D_pt + diam * perp_into
        O_pt_lim = D_pt + (diam / 4) * perp_into
        svg.append(f'<line x1="{D_pt[0]:.2f}" y1="{D_pt[1]:.2f}" '
                   f'x2="{B_pt_lim[0]:.2f}" y2="{B_pt_lim[1]:.2f}" '
                   f'stroke="orange" stroke-width="1.2" opacity="0.7"/>')
        svg.append(f'<circle cx="{D_pt[0]:.2f}" cy="{D_pt[1]:.2f}" r="2" fill="darkorange"/>')
        svg.append(f'<circle cx="{O_pt_lim[0]:.2f}" cy="{O_pt_lim[1]:.2f}" r="1.5" fill="darkorange"/>')
        svg.append(f'<circle cx="{B_pt_lim[0]:.2f}" cy="{B_pt_lim[1]:.2f}" r="2" fill="darkorange"/>')

    # ----- Lima\u00e7on on the floor (D=SF, B=U3, on floor) -----
    D_lim = np.array([SF_pt[0], 0.0])
    B_lim_floor = np.array([U3_pt[0], 0.0])
    svg.append(f'<line x1="{D_lim[0]:.2f}" y1="0" x2="{B_lim_floor[0]:.2f}" y2="0" '
               f'stroke="orange" stroke-width="2"/>')
    O_lim_floor = D_lim + (np.linalg.norm(B_lim_floor - D_lim) / 4) * \
                  (B_lim_floor - D_lim) / np.linalg.norm(B_lim_floor - D_lim)
    for pt in [D_lim, O_lim_floor, B_lim_floor]:
        svg.append(f'<circle cx="{pt[0]:.2f}" cy="{pt[1]:.2f}" r="2.5" fill="darkorange"/>')

    # ----- U (underbelly) old definition not drawn (replaced above) -----

    # ----- N (neck, black) -----
    for seg in neck_segs:
        svg.append(f'<path d="{bez_to_svg(*seg)}" '
                   f'fill="none" stroke="black" stroke-width="0.8"/>')

    # Bezier handles (optional)
    if show_handles:
        all_beziers = [
            S_data['sb_bezier'], S_data['sb_extension'], S_data['bass_tail_front'],
            U['seg1'], U['seg2'], U['seg3'],
        ] + neck_segs
        for P0, P1, P2, P3 in all_beziers:
            svg.append(f'<line x1="{P0[0]:.2f}" y1="{P0[1]:.2f}" '
                       f'x2="{P1[0]:.2f}" y2="{P1[1]:.2f}" '
                       f'stroke="green" stroke-width="0.4" stroke-dasharray="2,2" opacity="0.7"/>')
            svg.append(f'<line x1="{P3[0]:.2f}" y1="{P3[1]:.2f}" '
                       f'x2="{P2[0]:.2f}" y2="{P2[1]:.2f}" '
                       f'stroke="green" stroke-width="0.4" stroke-dasharray="2,2" opacity="0.7"/>')

    # ----- Grommet dots (Nf red, Ns blue) -----
    for s in strings:
        svg.append(f'<circle cx="{s["x"]:.2f}" cy="{s["Nf_z"]:.2f}" '
                   f'r="1.5" fill="red"/>')
        svg.append(f'<circle cx="{s["x"]:.2f}" cy="{s["Ns_z"]:.2f}" '
                   f'r="1.5" fill="blue"/>')

    # ----- Knot dots and labels -----
    # Need to flip text back since the group flips y
    svg.append('</g>')  # close flipped group; text drawn in normal coords

    # Neck knots
    if label_knots:
        for i, k in enumerate(K_KNOTS):
            svg.append(f'<circle cx="{k[0]:.2f}" cy="{-k[1]:.2f}" r="1.5" fill="black"/>')
            # Label offset
            if k[1] > 1500:
                dx, dy = 0, -8
            elif i == 9:  # K10 on column left side
                dx, dy = -10, 4
            else:
                dx, dy = 0, 12
            svg.append(f'<text x="{k[0]+dx:.2f}" y="{-k[1]+dy:.2f}" '
                       f'font-size="9" text-anchor="middle">K{i+1}</text>')

    # Endpoint labels
    floor_bulge_pt = np.array([U['U3'][0], 0.0])
    floor_end_pt_lbl = np.array([U['U3'][0] + FLOOR_EXTENSION, 0.0])
    # First lima\u00e7on B endpoint (at SBB)
    t0 = bez_tan(SB_P0, SB_P1, SB_P2, SB_P3, 0.0)
    t0 = t0 / np.linalg.norm(t0)
    perp0 = np.array([t0[1], -t0[0]])
    first_B = SB_P0 + 500.0 * perp0
    label_pts = [
        (SB_P0, 'SBB', 'black'),
        (K_KNOTS[5], 'SBN', 'black'),
        (S_data['SF'], 'SF', 'darkred'),
        (sprime_b, "S'_b", 'steelblue'),
        (sprime_t, "S'_t", 'steelblue'),
        (np.array([COL_X_LEFT, F]), 'CF_l', 'darkred'),
        (np.array([COL_X_RIGHT, F]), 'CF_r', 'darkred'),
        (floor_bulge_pt, 'B_floor', 'darkorange'),
        (floor_end_pt_lbl, 'floor_end', 'magenta'),
        (first_B, 'B1', 'darkorange'),
    ]
    for pt, lbl, color in label_pts:
        svg.append(f'<circle cx="{pt[0]:.2f}" cy="{-pt[1]:.2f}" r="1.5" fill="{color}"/>')
        svg.append(f'<text x="{pt[0]+5:.2f}" y="{-pt[1]-5:.2f}" '
                   f'fill="{color}" font-size="10">{lbl}</text>')

    svg.append('</svg>')
    with open(out_path, 'w') as f:
        f.write('\n'.join(svg))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description='Generate Erard-47 harp profile SVG.')
    ap.add_argument('-o', '--output', default='harp_profile.svg',
                    help='Output SVG path (default: harp_profile.svg)')
    ap.add_argument('--no-buffers', action='store_true', help='Hide clearance disks.')
    ap.add_argument('--handles', action='store_true', help='Show Bezier handles.')
    ap.add_argument('--no-knots', action='store_true', help='Hide K knot labels.')
    args = ap.parse_args()

    write_svg(args.output,
              label_knots=not args.no_knots,
              show_handles=args.handles,
              show_buffers=not args.no_buffers)
    print(f'Wrote {args.output}', file=sys.stderr)

if __name__ == '__main__':
    main()
