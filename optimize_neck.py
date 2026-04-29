#!/usr/bin/env python3
"""optimize_neck.py — solve K2, K3, K7, K8 so the closed neck loop encloses
all 141 buffer disks (47 Nf_flat + 47 Nf_sharp + 47 pin-tip) with CLEARANCE
= 8 mm margin.

This module predates the F/P/B/E/N/C/S region naming (see clements47.py).
The K-names below map to N-names as: K1=N0, K2=N9, K3=N8, K4=N7, K5=N6,
K6=N5, K7=N4, K8=N3, K9=N2, K10=N1. We read positions out of N_KNOTS via
the legacy column ordering (CW path order = N indices [0,9,8,7,6,5,4,3,2]).

Fixed knots/handles (NOT adjusted):
  K1 (N0), K9 (N2), K10 (N1)  -- column corners; handles along column edges
  K5 = Ut (N6), K6 = St (N5)  -- top extension points; K5 corner, K6 smooth along Ht
  K4 (N7)  -- treated fixed in this pass (user didn't list as adjustable)

Free knots:
  K2 (N9), K3 (N8), K7 (N4), K8 (N3)  -- positions free; handles use CR style
"""
import csv as _csv
import math
import os
import sys

import numpy as np
import clements47 as c

try:
    from scipy.optimize import minimize
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False

HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS_CSV = os.path.join(HERE, "strings.csv")
CLEARANCE = c.CLEARANCE

PIN_LEN = 38.96
PIN_ANGLE_DEG = 12.01


# ---------------------------------------------------------------------------
def load_strings():
    with open(STRINGS_CSV) as f:
        clean = "\n".join(ln for ln in f
                          if not ln.lstrip().startswith("#") and ln.strip())
    rows = list(_csv.DictReader(clean.splitlines()))

    def fnum(r, k):
        v = (r.get(k) or "").strip()
        return float(v) if v else 0.0

    out = []
    for r in rows:
        Ng_x = fnum(r, "Ng_x_mm"); Ng_y = fnum(r, "Ng_y_mm")
        gz = c.grommet_z_on_S(Ng_x)
        if gz is None:
            gz = Ng_y + c.Z_OFFSET

        def disc(prefix):
            dx = fnum(r, prefix + "_x_mm")
            dy = fnum(r, prefix + "_y_mm")
            dz = fnum(r, prefix + "_z_mm")
            return (dx - dz, gz + (dy - Ng_y))

        Nf_flat  = disc("Nf_flat")
        Nf_sharp = disc("Nf_sharp")
        out.append({
            "note": r["note"], "g": (Ng_x, gz),
            "Nf_flat": Nf_flat, "Nf_sharp": Nf_sharp,
        })
    return out


def all_buffers(strings):
    """Return list of (x, z) centres for the 141 buffer disks to enclose."""
    pts = []
    cos_p = math.cos(math.radians(PIN_ANGLE_DEG))
    sin_p = math.sin(math.radians(PIN_ANGLE_DEG))
    for s in strings:
        Nf_f = s["Nf_flat"]; Nf_s = s["Nf_sharp"]
        gx, gz = s["g"]
        nx, nz = Nf_f
        # String direction
        dx = nx - gx; dz = nz - gz
        L = math.hypot(dx, dz)
        ux, uz = (dx/L, dz/L) if L > 0 else (0.0, 1.0)
        # Pin rotated -PIN_ANGLE_DEG (toward +x).
        px =  ux * cos_p + uz * sin_p
        pz = -ux * sin_p + uz * cos_p
        pin_top = (nx + PIN_LEN * px, nz + PIN_LEN * pz)
        pts.append(Nf_f)
        pts.append(Nf_s)
        pts.append(pin_top)
    return pts


# ---------------------------------------------------------------------------
def build_neck_pts(N_full, n_per_seg=60):
    """Sample a dense polyline of the closed neck path. N_full is a 10-row
    array stored CCW (N0..N9 per the F/P/B/E/N/C/S region naming). The
    closed loop has 11 knots in CW path order:
       N0 (K1), N9 (K2), N8 (K3), N7 (K4), N6 (K5=Ut), N5 (K6=St),
       N4 (K7), N3 (K8), N2 (K9), N1 (K10), back to N0
    Tangents for fixed knots use the locked directions; tangents for free
    knots use Catmull-Rom through neighbours.
    """
    # Walk N_full in CW path order (legacy convention) so the segment
    # geometry exactly matches the original K-indexed implementation.
    seq_idx = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]   # N indices in CW order
    seq = [N_full[i] for i in seq_idx] + [N_full[seq_idx[0]]]   # close
    nseq = len(seq)

    # SB tangent at G7g for U-path direction at K5/K6 (= N6/N5).
    SB = (c.SB_P0, c.SB_P1, c.SB_P2, c.SB_P3)
    tan1 = c.bez_tan(*SB, 1.0); tan1_u = tan1 / np.linalg.norm(tan1)
    St_pt = c.SB_P3 + 2.0 * c.AIR_GAP * tan1_u
    Ut_pt_top = N_full[6]   # = N6 = K5 = Ut
    Ht_dir = (St_pt - Ut_pt_top); Ht_dir = Ht_dir / np.linalg.norm(Ht_dir)
    # K5 outgoing along K5->K6 = -Ht_dir (toward St)... actually since K5 is at Ut
    # and K6 is at St, K5->K6 direction is St - Ut = Ht_dir. Wait the user wants
    # K5 outgoing toward K6 along Ht line. -Ht_dir was used in build_views;
    # let's match that. The sign here reflects: K5_out_tangent points along
    # the segment direction K5 -> K6, which is St_pt - Ut_pt_top.
    K5_out_tan = (St_pt - Ut_pt_top) / np.linalg.norm(St_pt - Ut_pt_top)
    K6_smooth_tan = K5_out_tan   # K6 smooth along Ht

    # Column-edge tangents (seq[9] = N1 = K10, seq[10] = closure back to N0 = K1,
    # seq[8] = N2 = K9).
    col_top_dir  = (seq[10] - seq[9]) / np.linalg.norm(seq[10] - seq[9])  # K10 -> K1
    col_left_dir = (seq[9]  - seq[8]) / np.linalg.norm(seq[9]  - seq[8])  # K9 -> K10

    def _u(v):
        n = float(np.linalg.norm(v));  return v / n if n > 0 else v

    K5_idx, K6_idx = 4, 5
    K9_idx, K10_idx = 8, 9
    tangents = [None] * nseq
    for i in range(1, nseq - 1):
        if i == K5_idx:
            tangents[i] = K5_out_tan
        elif i == K6_idx:
            tangents[i] = K6_smooth_tan
        elif i == K9_idx:
            tangents[i] = col_left_dir
        elif i == K10_idx:
            tangents[i] = col_top_dir
        else:
            tangents[i] = _u(np.array(seq[i+1]) - np.array(seq[i-1]))
    tangents[0] = col_top_dir
    tangents[-1] = col_top_dir

    # Sample each Bezier segment.
    pts = []
    for i in range(nseq - 1):
        P0 = np.array(seq[i]); P3 = np.array(seq[i+1])
        chord_vec = P3 - P0; chord = float(np.linalg.norm(chord_vec))
        h_out = chord / 3.0; h_in = chord / 3.0
        if i == K9_idx or i == K10_idx:
            cu = chord_vec / chord if chord > 0 else np.array([1.0, 0.0])
            P1 = P0 + h_out * cu; P2 = P3 - h_in * cu
        elif i == 3:    # K4 -> K5 corner: P2 along +tan1_u, length to G7 pin top
            # K5 incoming from up-right with handle ~ chord/3 (simpler than
            # the build_views variant; the optimizer handles it via free
            # K2..K8 motion).
            P1 = P0 + h_out * tangents[i]
            P2 = P3 + h_in * tan1_u
        else:
            P1 = P0 + h_out * tangents[i]
            P2 = P3 - h_in * tangents[i+1]
        for tt in np.linspace(0.0, 1.0, n_per_seg):
            pt = ((1-tt)**3) * P0 + 3*(1-tt)**2*tt*P1 + 3*(1-tt)*tt**2*P2 + tt**3*P3
            pts.append(pt)
    return np.array(pts)


def point_in_polygon(pt, poly):
    x, y = pt
    n = len(poly); inside = False; j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-12) + xi):
            inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------------------
def main():
    if not HAS_SCIPY:
        print("scipy required."); return

    strings = load_strings()
    buffers = all_buffers(strings)
    print(f"strings: {len(strings)}, buffer disks to enclose: {len(buffers)}")
    Nc = c.N_KNOTS.copy()

    # Free variables: K2x, K2z, K3x, K3z, K7x, K7z, K8x, K8z (8 total)
    # In N-naming: K2 = N9, K3 = N8, K7 = N4, K8 = N3.
    x0 = np.array([
        Nc[9, 0], Nc[9, 1],     # K2 = N9
        Nc[8, 0], Nc[8, 1],     # K3 = N8
        Nc[4, 0], Nc[4, 1],     # K7 = N4
        Nc[3, 0], Nc[3, 1],     # K8 = N3
    ])

    def assemble(x):
        N = Nc.copy()
        N[9] = (x[0], x[1])     # K2 = N9
        N[8] = (x[2], x[3])     # K3 = N8
        N[4] = (x[4], x[5])     # K7 = N4
        N[3] = (x[6], x[7])     # K8 = N3
        return N

    # CW-path neighbour windows for the four free knots, expressed as
    # (prev, this, next) triples of N indices. Used by the smoothness
    # penalty below. Order matches the original (K2, K3, K7, K8).
    smooth_triples = [
        (0, 9, 8),   # K2 = N9: prev K1 = N0, next K3 = N8
        (9, 8, 7),   # K3 = N8: prev K2 = N9, next K4 = N7
        (5, 4, 3),   # K7 = N4: prev K6 = N5, next K8 = N3
        (4, 3, 2),   # K8 = N3: prev K7 = N4, next K9 = N2
    ]

    def objective(x):
        N = assemble(x)
        try:
            poly = build_neck_pts(N, n_per_seg=40)
        except Exception:
            return 1e9
        total = 0.0
        for b in buffers:
            inside_ = point_in_polygon(b, poly)
            dx = poly[:, 0] - b[0]; dz = poly[:, 1] - b[1]
            md = float(np.sqrt(dx*dx + dz*dz).min())
            if not inside_:
                total += 5000.0 + 1000.0 * (CLEARANCE + md)
            elif md < CLEARANCE:
                total += 200.0 * (CLEARANCE - md) ** 2
        # Smoothness: penalise huge tangent-angle changes between consecutive
        # free knots so the optimizer prefers smooth shapes.
        N_check = assemble(x)
        for ip, ic, in_ in smooth_triples:
            v1 = N_check[ic]  - N_check[ip]
            v2 = N_check[in_] - N_check[ic]
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cosang = float(v1.dot(v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
                total += max(0.0, 1.0 - cosang) * 50.0
        return total

    print("starting optimisation ...")
    res = minimize(objective, x0, method="Nelder-Mead",
                   options={"xatol": 0.5, "fatol": 0.01,
                            "maxiter": 12000, "adaptive": True, "disp": True})
    print(f"\nfinal objective: {res.fun:.3f}")
    N = assemble(res.x)

    # Verify
    poly = build_neck_pts(N, n_per_seg=80)
    violations = 0; worst = 0.0
    for b in buffers:
        ins = point_in_polygon(b, poly)
        dx = poly[:, 0] - b[0]; dz = poly[:, 1] - b[1]
        md = float(np.sqrt(dx*dx + dz*dz).min())
        if (not ins) or md < CLEARANCE:
            violations += 1
            worst = max(worst, (CLEARANCE - md) if ins else md)
    print(f"violations: {violations} / {len(buffers)}  worst={worst:.2f} mm")

    print("\n# Optimised N_KNOTS (paste into clements47.py):")
    labels = [
        "N0 = K1 column outer top",
        "N1 = K10 column inner top (derived)",
        "N2 = K9 column inner face",
        "N3 = K8",
        "N4 = K7",
        "N5 = K6 = St",
        "N6 = K5 = Ut",
        "N7 = K4 (above F7)",
        "N8 = K3 (S-knot)",
        "N9 = K2 (top arc bass)",
    ]
    print("N_KNOTS = np.array([")
    for i, n in enumerate(N):
        print(f"    [{n[0]:8.2f}, {n[1]:8.2f}],   # {labels[i]}")
    print("])")


if __name__ == "__main__":
    main()
