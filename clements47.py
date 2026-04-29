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
# SB Bezier: chord at 23.5 deg off vertical, the Erand reference geometry.
# This is NOT a wood-imposed limitation -- it is the structural condition
# for the string tops (Nf_flat z's) to lie nearly horizontal across the
# 47 strings, which is what makes the neck near-horizontal and the harp
# playable: the soundboard rises at exactly the rate that compensates
# the string-length variation. Any steeper SB makes the string-tops slope
# diagonally and forces the player's hands to span a huge vertical range.
SB_P1 = np.array([325.29,    971.14   + Z_OFFSET])
SB_P2 = np.array([350.50,   1142.59   + Z_OFFSET])
SB_P3 = np.array([643.29,   1477.0    + Z_OFFSET])     # = G7g (Erand reference)

BASS_TAIL_LEN = 200.0

# U2 placement: arc-fraction along S, perpendicular depth into chamber
U2_S_FRAC = 0.50
U2_DEPTH = 250.0

# U floor extension length
U_FLOOR_LEN = 300.0    # legacy alias; the floor footprint Uf - Sf is now
                       # derived from D_KNOT_FLOOR (= the lima\u00e7on's D-to-B
                       # distance at SF), not from this constant. Kept only
                       # for back-compat with anything reading the symbol.
FLOOR_EXTENSION = 0.0  # B_floor coincides with floor_end (below B1 at x=466.95)

# Column footprint. Scaled by csv ratio (643.29/735.29 = 0.8748) so K1, K9
# (column corners) line up with the column LEFT face after the SB Bezier
# was rescaled to fit strings.csv.
COL_X_LEFT = -17.755         # column bottom-outer x (= center - COL_OD_X/2)
COL_X_RIGHT = 14.245         # column bottom-inner x (= center + COL_OD_X/2)
COL_TOP_Z = 1690.42          # column top z (= C1f.z, was 1600 + Z_OFFSET = 1786.78)
# Elliptical CF column cross-section (replaces the old 28x32 mm rectangle).
# OD chosen for SF >= 3 in Euler buckling under 7079 N axial load with
# K=0.7 clamped base.
COL_OD_X = 32.0              # mm; column outer diameter in x (chord plane)
COL_OD_Y = 36.0              # mm; column outer diameter in y (depth)
COL_WALL_T = 4.0             # mm; CF wall thickness (hollow tube)

# Neck knots N0..N9 — AT-REST frame (xz, CCW from column outer top, then
# inward across the column top, down through the inner face, around the
# back of the neck loop, back up to the top arc bass).
#
# Region naming convention (used across clements47/build_views/etc):
#   F = Floor (z = 0 reference)
#   P = Pedestal (solid CF base under the soundbox)
#   B = Soundbox (hollow chamber)
#   E = Elbow (solid CF morph zone above the chamber cap)
#   N = Neck (this 10-knot loop above the elbow), points N0..N9
#   C = Column
#   S = Scoop (parabolic dish carved into the pedestal)
#
# Original K-name -> new N-name mapping (preserved for context only):
#   N0 = K1   (column outer top, col LEFT raked at K1.z)
#   N1 = K10  (column inner top, derived = (N0.x + col_w, N0.z))
#   N2 = K9   (column inner face, matches user's Inkscape edit)
#   N3 = K8   (optimized)
#   N4 = K7   (optimized)
#   N5 = K6 = St  (top of S; G7g + 2*AIR_GAP*tan1_unit)
#   N6 = K5 = Ut  (top of U; B-locus extension at top)
#   N7 = K4   (top arc treble end, above F7 Nf, raised 50)
#   N8 = K3   (S-knot, optimized)
#   N9 = K2   (top arc bass peak, optimized)
#
# Values from optimize_knots.py / optimize_neck.py (Nelder-Mead, 3 of 94
# buffer disks marginally inside the 8 mm clearance, K4-K5 separation
# enforced). build_views.py renders these directly without applying rake_xz.
# K1, K9 already encode the -7 deg rake from the column LEFT face; K6 is
# anchored to SBN on the un-raked soundboard so it doesn't shift further.
N_KNOTS = np.array([
    [-225.34,  1690.42],  # N0 = K1  - column outer top, raked 7 deg from COL_X_LEFT to z=C1f
    [-193.34,  1690.42],  # N1 = K10 - column inner top = N0 + (COL_OD_X, 0)
    [-169.54,  1494.49],  # N2 = K9  - slid DOWN 2*AIR_GAP along column inner face from prior
    [ 265.05,  1562.88],  # N3 = K8  - re-optimized (Nelder-Mead)
    [ 596.29,  1668.12],  # N4 = K7  - re-optimized
    [ 660.42,  1683.34],  # N5 = K6 = St (top of S; G7g + 2*AIR_GAP*tan1_unit)
    [ 730.38795897,  1622.07804902],  # N6 = K5 = Ut (top of U; B-locus extension at top)
    [ 613.08,  1861.49],  # N7 = K4  - top arc treble end (above F7 Nf, raised 50)
    [ 405.59,  1693.28],  # N8 = K3  - re-optimized
    [  87.98,  1894.18],  # N9 = K2  - re-optimized
])

# Back-compat alias: legacy code that referenced K_KNOTS expects 9 rows in
# CW path order [K1, K2, K3, K4, K5, K6, K7, K8, K9]. Reconstruct that view
# from N_KNOTS via fancy indexing. Read-only; downstream callers .copy() it
# before mutating, which still works because fancy indexing returns a copy.
K_KNOTS = N_KNOTS[[0, 9, 8, 7, 6, 5, 4, 3, 2]]

# Buffer disk radius around grommets (Nf, Ns)
CLEARANCE = 8.0

# ---------------------------------------------------------------------------
# Chamber diameter profile constants
# ---------------------------------------------------------------------------
# The chamber sweep path (arc length s) covers:
#   SF -> bass-tail-front Bezier -> SBB -> sb_bezier -> G7g -> sb_extension -> K6
# Diameter follows a smooth centripetal Catmull-Rom curve through D_KNOTS
# (defined after _CHAMBER is built). This gives a pear / teardrop stack-of-
# limacons -- no constant-D regions, no kinks, no parallel walls.
D_KNOT_FLOOR = 343.56                                          # D at SF -- shortened so the arc from B2 to floor (centered at the
                                                                # B1-B2 ∩ P0-P1 intersection) lands EXACTLY at P1.
PEDESTAL_TOP_Z   = -20.65    # mm; top of the pedestal (BEFORE sliding).
PEDESTAL_FLOOR_Z = -70.65    # mm; bottom of the pedestal (BEFORE sliding).
PEDESTAL_LEFT_X  = -69.74    # mm; pedestal P0 x (BEFORE sliding).
PEDESTAL_FLOOR_LENGTH = 380.0  # mm; |P0-P1| floor base of pedestal -- FIXED
                                # constant. 380 mm ~= 15 in, in line with
                                # typical Concert Grand base footprint.
FLOOR_BASE       = 380.0     # mm; alias of PEDESTAL_FLOOR_LENGTH.
BASE_ARC_CENTER  = 301.93    # mm; x-offset from P0 to the shared center of
                              # both pedestal arcs. Sized so the LEFT arc
                              # (R = BASE_ARC_CENTER, vertical tangent at P0)
                              # is TANGENT to the C1g->D1g line. Tangent
                              # point T sits below C1g on the line extension.
PEDESTAL_FILLET_R = 10.0     # mm; radius of the fillet arc at each lower
                              # pedestal corner (P0 and P1) -- "rounded edge"
                              # to break the sharp corner so the harp is safe
                              # to handle while moving.
# Slide the entire pedestal UP along the C1g->D1g line direction. The
# slide is a rigid translation: P0/P1/P2 all shift by the same vector,
# preserving (a) P0/P1 horizontal alignment, (b) arc tangency at P2 to
# the line, (c) P2-on-line. Sized so P2 lands exactly on the floor (z=0).
PEDESTAL_SLIDE_T = 41.54      # mm of slide along sb_tan_unit (D1g-C1g UP
                              # direction). Tuned so the line P2-P1 (right
                              # edge of pedestal sector) just clears the
                              # parabolic dish around R1 -- 1 mm safety
                              # margin below the first-touch geometry.
D_KNOT_PEAK  = 280.0                                           # D at s_peak (~ Lyon&Healy 23 / Salvi Apollo)
D_KNOT_PEAK_S = 700.0                                          # arc length where D peaks
D_KNOT_TOP    = 93.0                                           # D at G7g = Eb (Ht; chamber CAP, full limaçon)
D_KNOT_ET     = 50.0                                           # D at Et (G7-buffer tangent; elbow top, HALF limaçon)
D_KNOT_NECK  = 32.0                                            # legacy: matches NECK_W_Y_REF
TOP_DIAM = float(np.linalg.norm(N_KNOTS[7] - N_KNOTS[5]))      # ‖N7-N5‖ (= ‖K4-K6‖) — neck-pocket diameter, NOT chamber
D_FLOOR  = D_KNOT_FLOOR                                        # alias for back-compat
# Architectural note: the resonant chamber CAPS at G7g with the Ut-St
# straight-line cross-section (D = D_KNOT_TOP). Above G7g (s > s_at_G7g)
# the SB extension and K6 region are SOLID CF NECK material with an
# internal pocket for the G7-string Nf buffers; they are NOT chamber.
# `chamber_axis()` therefore restricts to s in [s_at_SF, s_at_G7g].
# NECK_W_Y mirrors build_freecad.py's neck-thickness-in-y (32 mm). At S'_t
# the chamber u-extent should match this so the chamber-to-neck handoff is
# cross-sectionally consistent.
NECK_W_Y_REF = 32.0

# ---------------------------------------------------------------------------
# Parabolic scoop (in chamber bass interior, focusing toward sound-holes)
# ---------------------------------------------------------------------------
# A paraboloid of revolution carved (CUT) into the chamber's bass-end
# interior. The Erand precedent (~/projects/Erand/soundbox/geometry.py) used
# this for two reasons: (1) added chamber volume to drop Helmholtz, and
# (2) collimated mid-band partials (~300 Hz - 1 kHz) toward the sound-hole
# cluster on the chamber back wall.
#
# In clements47 the chamber volume is already large (133 L per the acoustic
# analysis) so the volume-add purpose is OFF; the collimation purpose
# remains -- the scoop's parabolic axis aims toward the soundhole-cluster
# centroid so partials in the band where chamber Ø ~ λ get a directivity
# boost out the soundholes.
#
# Geometry (xz-plane parameters; the scoop is a paraboloid of revolution
# about SCOOP_AXIS_U, so it has full y-extent in 3D):
#   SCOOP_RIM_CENTER_XZ : centre of the rim circle, on the chamber back
#                          wall (B-locus) near the bass tail.
#   SCOOP_AIM_XZ        : focal target = soundhole-cluster centroid in xz.
#   SCOOP_AXIS_U        : unit vector from rim_center toward aim.
#   SCOOP_RIM_RADIUS    : rim circle radius (full aperture is 2 * radius).
#   SCOOP_DEPTH         : depth from rim plane to vertex along -SCOOP_AXIS_U.
#   SCOOP_FOCAL_LENGTH  : derived = rim_radius**2 / (4 * depth).
#
# The soundhole-cluster centroid uses the area-weighted mean of the five
# trumpet-flared holes in soundholes.csv (s = 171, 462, 770, 1078, 1369).
# Area-weighted mean s ~= 600-700 mm; we use s = 700 mm for the aim point
# and project onto the chamber-back-wall (B-locus) via the SB Bezier
# tangent + perp_into convention.
SCOOP_ENABLED        = True
# CF wall thickness. The parabolic scoop is inset INSIDE the chamber's
# carbon-fiber outer wall; shifting the rim center by CF_WALL_T in +x keeps
# the rim's higher-z endpoint (R2) clear of the pedestal's outer arc.
CF_WALL_T            = 5.0     # mm; CF outer-wall thickness (scoop inset).
SCOOP_RIM_RADIUS     = 120.0   # mm; matches Erand precedent (was 120.75 there)
# Soundboard thickness gradient: thicker at bass for stiffness/efficiency,
# thinner at treble for responsiveness (where there's no cavity assistance).
# Linearly interpolated along the SB Bezier parameter t in [0, 1].
SOUNDBOARD_THICKNESS_BASS    = 4.0   # mm; at C1g (t=0)
SOUNDBOARD_THICKNESS_TREBLE  = 1.2   # mm; at G7g (t=1)
# Backward-compatible alias used by the rim-anchor calc (rim sits at the
# bass end of the soundboard, so use the bass thickness).
SOUNDBOARD_THICKNESS = SOUNDBOARD_THICKNESS_BASS
SCOOP_DEPTH          = 60.0    # mm; matches Erand precedent
# Rim and aim centres (xz mm); see compute_scoop() for the derivation that
# turns these into the full scoop geometry. Initial values place rim at the
# SF/SBB transition and aim at s ~= 700 mm along the chamber back wall.
SCOOP_RIM_S_BASE     =  None   # set after _CHAMBER is built (= s_at_Sprime_b)
SCOOP_AIM_S_BASE     =  950.0  # arc length s (mm) at aim point. 950 = mid-treble
                               # hole region; the parabola only collimates above
                               # ~1 kHz, so aim it where treble strings need help.
                               # Bass already gets cavity-mode amplification.

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

    # Full SB extension to N5 (= K6 = St = sbn)
    sbn = N_KNOTS[5]
    h_sb = (np.linalg.norm(sbn - SB_P3) / 3) * 2
    sb_ext = (SB_P3, SB_P3 + h_sb * tan1_unit, sbn + h_sb * np.array([1.0, 0.0]), sbn)

    # Bass tail front Bezier from SBB to SF. SF is locked to the column's
    # outer face on the floor (Sf.x = COL_X_LEFT, z = 0) so the floor
    # footprint F starts where the column does. The BTF Bezier is no longer
    # a straight line; it curves from SBB down-left to SF with a vertical
    # handle at SF (matching the body's flat-on-floor landing).
    backward = -tan0_unit
    SF = np.array([float(COL_X_LEFT), 0.0])
    chord = np.linalg.norm(SF - SB_P0)
    h_btf_out = chord / 3                # outgoing handle from SBB
    h_sf_in = 30.0                       # incoming vertical handle at SF
    btf = (SB_P0, SB_P0 + h_btf_out * backward,
           SF + h_sf_in * np.array([0.0, 1.0]), SF)

    # Bass tail BACK Bezier from U'b (back wall at S'b, top of solid base)
    # down to U3 (back-wall floor corner). The BOTTOM handle at U3 is
    # vertical (length 30 mm) so the body lands flat on the floor like SF.
    # The TOP handle at U'b is aligned with the chamber B-locus tangent
    # (approached from above) so the join at U'b is C^1-smooth -- no kink
    # between the chamber back wall and the solid-base back wall.
    # Uf = SF + (300, 0): floor footprint length = 300 mm exactly. P0-P1.
    U3 = SF + np.array([300.0, 0.0])
    z_Sprime_b = SB_P0[1] - 2.0 * AIR_GAP
    _ts_test = np.linspace(0.0, 1.0, 4001)
    _zs_test = np.array([bez(*btf, t)[1] for t in _ts_test])
    t_sb = float(_ts_test[int(np.argmin(np.abs(_zs_test - z_Sprime_b)))])
    S_pb = bez(*btf, t_sb)
    btf_tan = bez_tan(*btf, t_sb); btf_tan = btf_tan / np.linalg.norm(btf_tan)
    chamber_tan = -btf_tan
    perp_into = np.array([chamber_tan[1], -chamber_tan[0]])
    U_pb = S_pb + U_FLOOR_LEN * perp_into                # U'b
    # Approximate B-locus tangent at U'b by walking the chamber path slightly
    # above S'b. We need to know diam at the next station, but D is constant
    # = D_KNOT_FLOOR through the BTF/base region, so just use perp at S'b
    # plus a tiny d-step for the stable direction.
    _btf_tan_above = bez_tan(*btf, max(t_sb - 0.01, 0.0))
    _btf_tan_above = _btf_tan_above / np.linalg.norm(_btf_tan_above)
    _chamber_tan_above = -_btf_tan_above
    _perp_above = np.array([_chamber_tan_above[1], -_chamber_tan_above[0]])
    _S_pb_above = bez(*btf, max(t_sb - 0.01, 0.0))
    _U_above = _S_pb_above + U_FLOOR_LEN * _perp_above
    btb_top_tan_up = _U_above - U_pb
    btb_top_tan_up = btb_top_tan_up / np.linalg.norm(btb_top_tan_up)
    # P1 (handle below U'b heading to U3) goes the OPPOSITE direction of the
    # B-locus tangent-from-above (smooth continuation downward).
    btb_h_top = 30.0   # top handle length (smooth match to B-locus tangent)
    btb_h_bot = 12.0   # short bottom handle so the curve doesn't bow past
                       # the Ub -> U'b chamber back-wall line
    btb = (U_pb,
           U_pb - btb_h_top * btb_top_tan_up,
           U3   + np.array([0.0,  btb_h_bot]),
           U3)

    # NOTE: compute_S_full's dict keys (e.g. "SF", "U3", "sb_bezier",
    # "sprime_treb_phantom") predate the F/P/B/E/N/C/S region naming
    # convention and are retained for back-compat. Future deprecation candidate
    # — rename in lockstep with downstream callers in build_views.py,
    # build_freecad.py, build_techdraw.py, optimize_neck*.py, and
    # make_neck_edit_svg.py.
    return {
        'sb_bezier': (SB_P0, SB_P1, SB_P2, SB_P3),
        'sprime_bass_phantom': sprime_bass,   # outer bass end of S'
        'sprime_treb_phantom': sprime_treb,   # outer treble end of S'
        'sb_extension': sb_ext,               # G7g -> sbn (N5 / K6)
        'bass_tail_front': btf,               # SBB -> SF (vertical handle at SF)
        'bass_tail_back':  btb,               # U'b -> U3 (vertical handles both ends)
        'U_pb': U_pb, 'U3': U3,
        'SF': SF,
        'F': SF[1],
    }

def compute_scoop():
    """Parabolic-dish scoop carved into the SOLID CF BASE at the bottom of
    the hollow chamber. The rim sits in the limaçon cross-section plane at
    S'b (the chamber's bottom cap, where the hollow meets the solid base).
    The dish opens UPWARD into the chamber; its axis points along the
    chamber tangent at S'b. The aim_xz field still records the soundhole-
    cluster centroid for documentation.

    Geometry:
      rim_center_xz = midpoint of the S'b -> U'b limaçon diameter (on the
                      chamber axis at s_at_Sprime_b)
      axis_unit     = chamber tangent at S'b, in xz (90 deg from perp_into)
      rim plane     = cross-section plane at S'b -> contains perp_into and y
                      so the rim chord in side view overlays the S'b->U'b line
      paraboloid_focal = R^2 / (4 * depth)
    """
    # Reference position: rim_center_S3 = "2 air gaps below C1g along
    # soundboard" (= S3). axis_unit is computed from this reference rim
    # center toward the soundhole-cluster aim point (its original
    # derivation), then FROZEN. The scoop is then translated as a rigid
    # body (rim_center + axis_unit + chord direction all shift together)
    # so the higher-z chord endpoint (R1) lands at "2 air gaps below S3
    # along soundboard". This keeps the parabolic dish orientation exactly
    # as it was; only its position changes.
    sb_tan_at_C1g = SB_P1 - SB_P0
    sb_tan_unit = sb_tan_at_C1g / float(np.linalg.norm(sb_tan_at_C1g))
    # perp_into points perpendicular to soundboard tangent at C1g, INTO
    # the chamber (+x side of the soundboard plane).
    perp_into_C1g = np.array(
        [sb_tan_unit[1], -sb_tan_unit[0]], dtype=float)
    # S3 anchor offset INWARD by SOUNDBOARD_THICKNESS so the rim and the
    # whole scoop sit on the INTERIOR face of the soundboard CF, not on
    # the exterior surface.
    rim_center_S3 = (SB_P0
                     - 2.0 * AIR_GAP * sb_tan_unit
                     + SOUNDBOARD_THICKNESS * perp_into_C1g)
    # s_rim and chamber-derived values used downstream.
    s_rim = SCOOP_RIM_S_BASE
    D_pt, perp_into = chamber_axis(s_rim)
    diam = diam_at_s(s_rim)
    Dp_aim, perp_aim = chamber_axis(SCOOP_AIM_S_BASE)
    aim_xz = Dp_aim + diam_at_s(SCOOP_AIM_S_BASE) * perp_aim
    # Frozen axis_unit (derived from rim_center_S3 toward aim_xz).
    axis_unit = (aim_xz - rim_center_S3)
    axis_unit = axis_unit / float(np.linalg.norm(axis_unit))
    # Compute the original R1 (higher-z chord endpoint) at rim_center_S3
    # so we know how far to translate.
    perp_xz = np.array([-axis_unit[1], axis_unit[0]], dtype=float)
    e1_orig = rim_center_S3 + SCOOP_RIM_RADIUS * perp_xz
    e2_orig = rim_center_S3 - SCOOP_RIM_RADIUS * perp_xz
    R1_orig = e1_orig if e1_orig[1] >= e2_orig[1] else e2_orig
    # Target: R1 = "2 air gaps below S3 along soundboard down" (on the
    # interior face of the soundboard, so SOUNDBOARD_THICKNESS shift is
    # already baked into rim_center_S3).
    R1_target = rim_center_S3 - 2.0 * AIR_GAP * sb_tan_unit
    shift = R1_target - R1_orig
    rim_center_xz = rim_center_S3 + shift
    # Inset the scoop INSIDE the CF outer wall by translating rc in +x by
    # CF_WALL_T. axis_unit and aim_xz are already frozen above; shifting rc
    # leaves the scoop axis direction (and therefore perp_xz) unchanged, so
    # R1/R2 simply translate by the same +x amount. This keeps R2 clear of
    # the pedestal's outer arc.
    rim_center_xz = rim_center_xz + np.array([CF_WALL_T, 0.0], dtype=float)
    paraboloid_focal = SCOOP_RIM_RADIUS ** 2 / (4.0 * SCOOP_DEPTH)
    return {
        'rim_center_xz':    rim_center_xz,
        'rim_radius':       SCOOP_RIM_RADIUS,
        'depth':            SCOOP_DEPTH,
        'aim_xz':           aim_xz,
        'axis_unit':        axis_unit,
        'paraboloid_focal': paraboloid_focal,
    }


def compute_U(F):
    """Return U knots and segments. U = U1 -> U2 -> U3 -> U4."""
    # U1 at N6 (= K5 = Ut)
    U1 = N_KNOTS[6].copy()
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
    # Match SF: extension length so U4.z == 0 (single source-of-truth with SF).
    if abs(backward[1]) > 1e-9:
        ext_len = SB_P0[1] / (-backward[1])
    else:
        ext_len = BASS_TAIL_LEN
    U4 = SB_P0 + ext_len * backward

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

# ---------------------------------------------------------------------------
# Chamber path: arc-length parameterization spanning
#   SF -> bass-tail-front -> SBB -> sb_bezier -> G7g -> sb_extension -> K6
# ---------------------------------------------------------------------------

def _chamber_arclen_data():
    """Compute arc-length tables and breakpoints for the chamber path.
    Returns a dict with arc-length tables for each Bezier segment and the
    breakpoint s-values (s = 0 at SF, increasing toward K6 at s = s_total).
    """
    S_data = compute_S_full()
    btf    = S_data['bass_tail_front']     # SBB -> SF Bezier
    sb_bez = S_data['sb_bezier']           # SBB -> G7g
    sb_ext = S_data['sb_extension']        # G7g -> K6

    ts_btf, arc_btf = bez_arclen_table(*btf,    n=2000)
    ts_sb,  arc_sb  = bez_arclen_table(*sb_bez, n=2000)
    ts_ex,  arc_ex  = bez_arclen_table(*sb_ext, n=500)
    L_btf = float(arc_btf[-1])
    L_sb  = float(arc_sb[-1])
    L_ex  = float(arc_ex[-1])

    # Phantom extension lengths (along SB tangents at SBB, G7g)
    strings = compute_string_positions()
    phantom_b_x, phantom_t_x = compute_phantom_grommets(strings)
    tan0 = bez_tan(*sb_bez, 0.0); tan0_unit = tan0 / np.linalg.norm(tan0)
    tan1 = bez_tan(*sb_bez, 1.0); tan1_unit = tan1 / np.linalg.norm(tan1)
    ext_b_len = (sb_bez[0][0] - phantom_b_x) / tan0_unit[0] if abs(tan0_unit[0]) > 1e-9 else 0.0
    ext_t_len = (phantom_t_x - sb_bez[3][0]) / tan1_unit[0] if abs(tan1_unit[0]) > 1e-9 else 0.0

    # s-breakpoints. s=0 at SF, increasing toward K6.
    #   S'b = 2*AIR_GAP of arclength PAST Sb (= SBB) along S, going down
    #         the BTF. So in chamber-arclength: s_at_Sprime_b = L_btf - 2*AIR_GAP.
    #   S't = 2*AIR_GAP of arclength PAST St (= G7g) along S, going up the
    #         SB tangent (sb_extension). So s_at_St = s_at_G7g + 2*AIR_GAP.
    s_at_SF        = 0.0
    s_at_SBB       = L_btf
    s_at_Sprime_b  = max(0.0, L_btf - 2.0 * AIR_GAP)        # 2 air-gaps along S below Sb
    s_at_G7g       = s_at_SBB + L_sb
    s_at_St        = s_at_G7g + 2.0 * AIR_GAP                # 2 air-gaps along S above St
    s_total        = s_at_SBB + L_sb + L_ex

    # s_at_Et: ELBOW TOP. Distance from G7g along the SB tangent until z
    # reaches the G7-buffer-tangent line height. The elbow region spans
    # [s_at_G7g, s_at_Et] and morphs from full limaçon (D = D_KNOT_TOP at
    # Eb) to half limaçon (D = D_KNOT_ET at Et).
    G7_BUF_Z = SB_P0[1]    # placeholder; recomputed below from strings.csv
    # Use the soundboard tangent at G7g and the G7-grommet-to-buffer dz.
    # G7's Nf-flat z = grommet_z + (csv.y_Nf - csv.y_Ng), tangent y-component
    # already known. We just sample the strings.csv G7 entry for the average
    # buffer z.
    try:
        import csv as _csv_local, os as _os_local
        _here = _os_local.path.dirname(_os_local.path.abspath(__file__))
        with open(_os_local.path.join(_here, 'strings.csv')) as _f:
            _clean = '\n'.join(ln for ln in _f
                               if not ln.lstrip().startswith('#') and ln.strip())
        _g7 = next(r for r in _csv_local.DictReader(_clean.splitlines())
                   if r['note'].strip() == 'G7')
        def _fn(k):
            v=(_g7.get(k) or '').strip(); return float(v) if v else 0.0
        _gz = grommet_z_on_S(_fn('Ng_x_mm'))
        _zf = _gz + (_fn('Nf_flat_y_mm')  - _fn('Ng_y_mm'))
        _zs = _gz + (_fn('Nf_sharp_y_mm') - _fn('Ng_y_mm'))
        # Tangent point on each buffer is offset CLEARANCE in +perp; both
        # share the same z when projected by their perp's z-components, so
        # use the average buffer-disk z as the elbow-top z.
        G7_BUF_Z = 0.5 * (_zf + _zs)
    except Exception:
        G7_BUF_Z = SB_P3[1] + 75.0
    # Compute Et midpoint = midpoint of the G7 buffer external tangent line
    # (sharp-side and flat-side tangent points). The ELBOW PATH runs from
    # G7g STRAIGHT TO Et midpoint -- this is the "inner loop" the limaçon
    # origins follow. Limaçons in the elbow are perpendicular to this path.
    try:
        import csv as _csv_local, os as _os_local
        _here = _os_local.path.dirname(_os_local.path.abspath(__file__))
        with open(_os_local.path.join(_here, 'strings.csv')) as _f:
            _clean = '\n'.join(ln for ln in _f
                               if not ln.lstrip().startswith('#') and ln.strip())
        _g7 = next(r for r in _csv_local.DictReader(_clean.splitlines())
                   if r['note'].strip() == 'G7')
        def _fn(k):
            v=(_g7.get(k) or '').strip(); return float(v) if v else 0.0
        _gz = grommet_z_on_S(_fn('Ng_x_mm'))
        _Pf = np.array([_fn('Nf_flat_x_mm')  - _fn('Nf_flat_z_mm'),
                        _gz + (_fn('Nf_flat_y_mm')  - _fn('Ng_y_mm'))])
        _Ps = np.array([_fn('Nf_sharp_x_mm') - _fn('Nf_sharp_z_mm'),
                        _gz + (_fn('Nf_sharp_y_mm') - _fn('Ng_y_mm'))])
        _v   = _Ps - _Pf; _v_unit = _v / np.linalg.norm(_v)
        _perp_buf = np.array([-_v_unit[1], _v_unit[0]])
        _Ef = _Pf + CLEARANCE * _perp_buf
        _Es = _Ps + CLEARANCE * _perp_buf
        Et_midpoint = 0.5 * (_Es + _Ef)
    except Exception:
        Et_midpoint = SB_P3 + 75.0 * tan1_unit
    # Elbow runs from S't (the chamber's TOP CAP per design) to Et midpoint.
    St_phantom_pt = SB_P3 + 2.0 * AIR_GAP * tan1_unit
    elbow_dir = Et_midpoint - St_phantom_pt
    elbow_len = float(np.linalg.norm(elbow_dir))
    elbow_unit = elbow_dir / elbow_len if elbow_len > 0 else tan1_unit
    s_at_Et = s_at_St + elbow_len

    return {
        'btf': btf, 'sb_bez': sb_bez, 'sb_ext': sb_ext,
        'ts_btf': ts_btf, 'arc_btf': arc_btf, 'L_btf': L_btf,
        'ts_sb':  ts_sb,  'arc_sb':  arc_sb,  'L_sb':  L_sb,
        'ts_ex':  ts_ex,  'arc_ex':  arc_ex,  'L_ex':  L_ex,
        'ext_b_len': ext_b_len, 'ext_t_len': ext_t_len,
        's_at_SF': s_at_SF, 's_at_SBB': s_at_SBB,
        's_at_Sprime_b': s_at_Sprime_b, 's_at_G7g': s_at_G7g,
        's_at_St': s_at_St, 's_at_Et': s_at_Et,
        's_total': s_total,
        'elbow_unit': elbow_unit, 'elbow_len': elbow_len,
        'Et_midpoint': Et_midpoint,
    }

# Module-level cache of chamber path data (computed once at import).
_CHAMBER = _chamber_arclen_data()
s_at_SF       = _CHAMBER['s_at_SF']
s_at_SBB      = _CHAMBER['s_at_SBB']
s_at_Sprime_b = _CHAMBER['s_at_Sprime_b']
s_at_G7g      = _CHAMBER['s_at_G7g']
s_at_St       = _CHAMBER['s_at_St']
s_at_Et       = _CHAMBER['s_at_Et']
s_total       = _CHAMBER['s_total']

def chamber_axis(s_val):
    """Return (D_xz, perp_into_xz) along the chamber path for arc length s.

    s = 0 at SF, increasing through SBB, G7g, K6 (s = s_total). The path is:
        [0, s_at_SBB]            -> bass-tail-front Bezier (parameter goes
                                    SBB->SF, so map s in [0, L_btf] to t s.t.
                                    arc(t) = L_btf - s, giving the SF->SBB
                                    direction along btf)
        [s_at_SBB, s_at_G7g]     -> sb_bezier (SBB->G7g)
        [s_at_G7g, s_total]      -> sb_extension (G7g->K6)

    perp_into_xz is the unit normal pointing INTO the chamber (rotated -90deg
    from the path tangent, matching the existing convention).
    """
    C = _CHAMBER
    if s_val <= C['s_at_SBB']:
        # Bass-tail-front. btf parameter t=0 at SBB, t=1 at SF.
        # As s increases from 0 (SF) to L_btf (SBB), t decreases from 1 -> 0.
        # arc(t)_btf at t=1 is L_btf, at t=0 is 0.
        # We want s_path = L_btf - arc(t_btf). So arc(t_btf) = L_btf - s.
        target_arc = C['L_btf'] - s_val
        ti = float(np.interp(target_arc, C['arc_btf'], C['ts_btf']))
        D_pt = bez(*C['btf'], ti)
        t_dir = bez_tan(*C['btf'], ti)
        # btf tangent points SBB->SF. We want path direction SF->K6, which is
        # the REVERSE of btf along this segment. Flip sign.
        t_dir = -t_dir
    elif s_val <= C['s_at_G7g']:
        s_local = s_val - C['s_at_SBB']
        ti = float(np.interp(s_local, C['arc_sb'], C['ts_sb']))
        D_pt = bez(*C['sb_bez'], ti)
        t_dir = bez_tan(*C['sb_bez'], ti)
    elif s_val <= C['s_at_St']:
        # SB tangent extension G7g -> S't (2*AIR_GAP along the SB tangent).
        # Chamber continues here; this region is INSIDE the chamber (below Ht).
        u = (s_val - C['s_at_G7g']) / max(2.0 * AIR_GAP, 1e-9)
        tan1 = bez_tan(*C['sb_bez'], 1.0); tan1_u = tan1 / np.linalg.norm(tan1)
        D_pt = SB_P3 + (s_val - C['s_at_G7g']) * tan1_u
        t_dir = tan1_u
    elif s_val <= C['s_at_Et']:
        # ELBOW region: STRAIGHT line from S't to Et midpoint. Limaçon
        # origins follow this inner-loop path; cross-sections perpendicular.
        u = (s_val - C['s_at_St']) / max(C['elbow_len'], 1e-9)
        St_pt = SB_P3 + 2.0 * AIR_GAP * (bez_tan(*C['sb_bez'], 1.0) /
                np.linalg.norm(bez_tan(*C['sb_bez'], 1.0)))
        D_pt = St_pt + u * C['elbow_len'] * C['elbow_unit']
        t_dir = C['elbow_unit'].copy()
    else:
        # Above Et: continue along sb_extension Bezier (legacy fallback).
        s_local = s_val - C['s_at_G7g']
        ti = float(np.interp(s_local, C['arc_ex'], C['ts_ex']))
        D_pt = bez(*C['sb_ext'], ti)
        t_dir = bez_tan(*C['sb_ext'], ti)
    t_dir = t_dir / np.linalg.norm(t_dir)
    perp = np.array([t_dir[1], -t_dir[0]])
    return D_pt, perp


def _solve_D_at_St():
    """Solve D_AT_St from clearance constraints.

    Constraints:
      (1) Chamber surface at S'_t must clear the F7 Nf-flat buffer disk by
          at least CLEARANCE = 8 mm.
      (2) Chamber u-extent at S'_t should match neck thickness in y
          (NECK_W_Y_REF = 32 mm) for a clean chamber-to-neck handoff.

    F7 Nf-flat at-rest position from strings.csv (sn=46):
        x_at_rest = csv.x_Nf - csv.z_Nf = 629.870 - 11.882 = 617.988
        z_at_rest = gz + (csv.y_Nf - csv.y_Ng) where gz = grommet_z_on_S(629.870).
    The chamber/SB are in the un-raked frame; we evaluate clearance in 3D
    using the un-raked F7 position (x = csv.x_Nf, y = -L_flat * sin(rake),
    z = gz + L_flat * cos(rake)).

    Returns (D_AT_St, info_dict) where info_dict records which constraint
    bound and the F7 clearance value at the chosen diameter.
    """
    # F7 Nf-flat in un-raked 3D world coords
    csv_x_F7 = 629.870
    csv_y_Nf = 1558.342
    csv_y_Ng = 1461.568
    gz = grommet_z_on_S(csv_x_F7)
    L_flat_F7 = 97.5
    F7_3d = np.array([csv_x_F7,
                      -L_flat_F7 * np.sin(np.radians(RAKE_DEG)),
                      gz + L_flat_F7 * np.cos(np.radians(RAKE_DEG))])

    # Chamber cross-section axis at S'_t
    D_xz, perp_into = chamber_axis(s_at_St)

    def min_dist_chamber_to_F7(diam):
        """Sample limacon points and return min 3D distance to F7."""
        b = diam / 4.0
        a = 2.0 * b
        thetas = np.linspace(0.0, 2.0 * np.pi, 720, endpoint=False)
        r = a + b * np.cos(thetas)
        u = r * np.cos(thetas)
        v = r * np.sin(thetas)
        pts = np.zeros((720, 3))
        pts[:, 0] = D_xz[0] + u * perp_into[0]
        pts[:, 1] = v
        pts[:, 2] = D_xz[1] + u * perp_into[1]
        return float(np.min(np.linalg.norm(pts - F7_3d, axis=1)))

    # Constraint (2): match neck cross-section in y. Cross-section is a
    # limacon u-extent = diam, v-extent (in y) = ~1.1009 * diam. We match
    # the u-extent (diam) directly to NECK_W_Y_REF: a clean chamber-to-neck
    # handoff in the perpendicular-to-S direction.
    D_neck_match = NECK_W_Y_REF
    clearance_at_neck_match = min_dist_chamber_to_F7(D_neck_match)

    # Constraint (1): F7 clearance. Search for the largest diameter such that
    # min_dist >= CLEARANCE. (For most reasonable diameters the chamber bulb
    # at S'_t points AWAY from F7, so this is satisfied for a wide range.)
    # If the neck-match diameter satisfies clearance, use it; otherwise back
    # off until clearance is met.
    if clearance_at_neck_match >= CLEARANCE:
        D = D_neck_match
        bound_by = 'neck_match (NECK_W_Y_REF)'
        clearance = clearance_at_neck_match
    else:
        # Bisect down from the neck-match value to find a diameter that
        # respects clearance.
        lo, hi = 0.0, D_neck_match
        for _ in range(64):
            mid = 0.5 * (lo + hi)
            if min_dist_chamber_to_F7(mid) >= CLEARANCE:
                lo = mid
            else:
                hi = mid
        D = lo
        bound_by = 'F7_clearance'
        clearance = min_dist_chamber_to_F7(D)

    info = {
        'F7_3d': F7_3d, 'D_xz_at_St': D_xz, 'perp_at_St': perp_into,
        'D_AT_St': D, 'bound_by': bound_by, 'clearance_3d': clearance,
        'D_neck_match': D_neck_match, 'CLEARANCE': CLEARANCE,
    }
    return D, info

D_AT_St, _D_AT_St_INFO = _solve_D_at_St()


# ---------------------------------------------------------------------------
# Diameter profile: smooth pear-shape via centripetal Catmull-Rom through
# D_KNOTS. Uniform-time CR with phantom end-knots (mirrored). Pre-computed
# table at module load; diam_at_s() is np.interp on that table.
# ---------------------------------------------------------------------------
D_KNOTS = np.array([
    [_CHAMBER['s_at_Sprime_b'],    D_KNOT_FLOOR],   # S'b (end of flat base)
    [D_KNOT_PEAK_S,                D_KNOT_PEAK ],   # peak (~36% along)
    [_CHAMBER['s_at_St'],          D_KNOT_TOP  ],   # S't cap (Ht = U't-S't line)
])

def _build_diam_table(K, n_per_seg=80):
    """Centripetal Catmull-Rom (alpha=0.5) through K, with phantom end-knots.
    The leading phantom shares K[0]'s D value (tangent at K[0] is forced
    horizontal so the pear taper joins the constant-D base C^1-smoothly at
    S'b). The trailing phantom is the usual mirror reflection.
    Returns (s_arr, D_arr) sorted by s."""
    pre  = np.array([K[0, 0] - 50.0, K[0, 1]])  # same D as K[0] -> dD/ds = 0 at K[0]
    post = 2 * K[-1] - K[-2]
    Kf   = np.vstack([pre, K, post])
    ss, Ds = [], []
    alpha = 0.5
    def t_next(ti, Pi, Pj):
        d = float(np.sqrt(np.sum((Pj - Pi) ** 2)))
        return ti + d ** alpha
    for i in range(len(K) - 1):
        P0, P1, P2, P3 = Kf[i], Kf[i+1], Kf[i+2], Kf[i+3]
        t0 = 0.0
        t1 = t_next(t0, P0, P1)
        t2 = t_next(t1, P1, P2)
        t3 = t_next(t2, P2, P3)
        for u in np.linspace(0.0, 1.0, n_per_seg, endpoint=(i == len(K) - 2)):
            t = t1 + u * (t2 - t1)
            A1 = (t1 - t)/(t1 - t0) * P0 + (t - t0)/(t1 - t0) * P1
            A2 = (t2 - t)/(t2 - t1) * P1 + (t - t1)/(t2 - t1) * P2
            A3 = (t3 - t)/(t3 - t2) * P2 + (t - t2)/(t3 - t2) * P3
            B1 = (t2 - t)/(t2 - t0) * A1 + (t - t0)/(t2 - t0) * A2
            B2 = (t3 - t)/(t3 - t1) * A2 + (t - t1)/(t3 - t1) * A3
            C  = (t2 - t)/(t2 - t1) * B1 + (t - t1)/(t2 - t1) * B2
            ss.append(float(C[0])); Ds.append(float(C[1]))
    s_arr = np.array(ss); D_arr = np.array(Ds)
    order = np.argsort(s_arr)
    return s_arr[order], D_arr[order]

_DIAM_S, _DIAM_D = _build_diam_table(D_KNOTS)

# Scoop rim placed at S'b (transition from constant base to pear taper).
SCOOP_RIM_S_BASE = float(_CHAMBER['s_at_Sprime_b'])


def diam_at_s(s_val):
    """Constant D = D_KNOT_FLOOR from SF up to S'b (the base limaçon stack
    has parallel sides through the bass-tail bulb). Above S'b the smooth
    Catmull-Rom pear taper carries D up to the peak and then down to D at
    G7g (= D_KNOT_TOP = Eb, where the chamber CAPS). Above G7g the ELBOW
    region tapers linearly D_KNOT_TOP -> D_KNOT_ET over [s_at_G7g, s_at_Et].
    Above s_at_Et the elbow has terminated; clamp at D_KNOT_ET."""
    if s_val <= _CHAMBER['s_at_Sprime_b']:
        return float(D_KNOT_FLOOR)
    if s_val >= _CHAMBER['s_at_Et']:
        return float(D_KNOT_ET)
    if s_val >= _CHAMBER['s_at_St']:
        # Elbow region: linear taper from Ht (D_KNOT_TOP at S't) -> Et
        frac = (s_val - _CHAMBER['s_at_St']) / (_CHAMBER['s_at_Et'] - _CHAMBER['s_at_St'])
        return float(D_KNOT_TOP * (1.0 - frac) + D_KNOT_ET * frac)
    if s_val >= _DIAM_S[-1]:
        return float(D_KNOT_TOP)
    return float(np.interp(s_val, _DIAM_S, _DIAM_D))


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
    z_max = max(N_KNOTS[:, 1].max(), max(s['Nf_z'] for s in strings)) + 50
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

    # ----- Limaçon series along the FULL chamber path
    # (SF -> bass-tail -> SBB -> G7g -> K6), with the new piecewise
    # diameter profile (constant D_FLOOR through S'_b, taper to D_AT_St
    # at S'_t, taper to TOP_DIAM at K6). See diam_at_s() and chamber_axis()
    # at module level. -----
    SF_pt = S_data['SF']
    U3_pt = U['U3']

    # Compute B locus densely along the full chamber path
    n_dense = 300
    ss_dense = np.linspace(s_at_SF, s_total, n_dense)
    B_locus_full = []
    for s_val in ss_dense:
        D_pt, perp_into = chamber_axis(s_val)
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
    n_lim = 20
    sample_ss = np.linspace(s_at_SF, s_total, n_lim)
    for s_val in sample_ss:
        D_pt, perp_into = chamber_axis(s_val)
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

    # Neck knots N0..N9 (CCW from column outer top)
    if label_knots:
        for i, k in enumerate(N_KNOTS):
            svg.append(f'<circle cx="{k[0]:.2f}" cy="{-k[1]:.2f}" r="1.5" fill="black"/>')
            # Label offset
            if k[1] > 1500:
                dx, dy = 0, -8
            else:
                dx, dy = 0, 12
            svg.append(f'<text x="{k[0]+dx:.2f}" y="{-k[1]+dy:.2f}" '
                       f'font-size="9" text-anchor="middle">N{i}</text>')

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
        (N_KNOTS[5], 'SBN', 'black'),
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
