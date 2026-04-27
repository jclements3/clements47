#!/usr/bin/env python3
"""optimize_knots.py — solve for K_KNOTS positions that enclose all 94
buffer disks (Nf_flat + Nf_sharp) with >= CLEARANCE clearance, anchoring
K1 / K9 to the (raked) column and K6 to SBN above G7.Ns.

Run:
    python3 optimize_knots.py

Output: candidate K_KNOTS values (paste into clements47.py).
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
TAN_RAKE  = float(np.tan(np.radians(c.RAKE_DEG)))


# ---------------------------------------------------------------------------
# Buffer positions (at-rest, in xz plane, csv -> clements with rake into -x)
# ---------------------------------------------------------------------------
def load_buffers():
    with open(STRINGS_CSV) as f:
        clean = "\n".join(ln for ln in f if not ln.lstrip().startswith("#") and ln.strip())
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
        for which in ("Nf_flat", "Nf_sharp"):
            dx = fnum(r, which + "_x_mm")
            dy = fnum(r, which + "_y_mm")
            dz = fnum(r, which + "_z_mm")
            Nf_x = dx - dz                 # rake into -x
            Nf_z = gz + (dy - Ng_y)
            out.append({"note": r["note"], "kind": which,
                        "x": float(Nf_x), "z": float(Nf_z)})
    return out


# ---------------------------------------------------------------------------
# Anchor positions (fixed K knots)
# ---------------------------------------------------------------------------
def anchors():
    """Return fixed K1, K6, K9 (at-rest xz) and the canonical K_KNOTS for
    initial guesses on the free knots."""
    K_canon = c.K_KNOTS

    # K1 = column LEFT-TOP corner in at-rest frame (column raked -7 deg)
    K1_z = float(K_canon[0, 1])                                  # 1786.78
    K1_x = float(c.COL_X_LEFT) - K1_z * TAN_RAKE                 # raked
    K1 = np.array([K1_x, K1_z])

    # K9 = column LEFT face at K9_z (raked)
    K9_z = float(K_canon[8, 1])                                  # 1450
    K9_x = float(c.COL_X_LEFT) - K9_z * TAN_RAKE
    K9 = np.array([K9_x, K9_z])

    # K6 = SBN: at SB_P3.x (un-raked, since soundboard isn't raked) and z
    # just above the highest G7.Ns clearance (with CLEARANCE margin).
    G7_Ns_x = 643.29 - 8.51                       # csv: G7 Nf_sharp x rake
    G7_Ns_z = float(c.SB_P3[1]) + (1546.28 - 1477.0)   # gz + delta y_csv
    K6_x = float(c.SB_P3[0])                      # = 643.29
    K6_z = G7_Ns_z + CLEARANCE + 4                # 8mm clearance + 4mm margin
    K6 = np.array([K6_x, K6_z])

    return K1, K6, K9


# ---------------------------------------------------------------------------
# Build neck Bezier loop given a full K_KNOTS array (uses clements47.py's
# build_neck_segments tangent conventions)
# ---------------------------------------------------------------------------
def build_neck_pts(K_KNOTS, n_per_seg=60):
    """Return a dense polyline of points along the closed neck Bezier loop."""
    QARC = (4.0 / 3.0) * (math.sqrt(2) - 1)

    def unit(v):
        n = np.linalg.norm(v)
        return v / n if n > 0 else v

    def cr(K, i):
        n = len(K)
        return unit(K[(i + 1) % n] - K[(i - 1) % n])

    n = len(K_KNOTS)
    in_tan = [None] * n
    out_tan = [None] * n
    for i in range(n):
        next_pt = K_KNOTS[(i + 1) % n]
        if i == 0:
            in_tan[i] = np.array([0.0, 1.0]); out_tan[i] = np.array([0.0, 1.0])
        elif i == 3:
            in_tan[i] = np.array([1.0, 0.0]); out_tan[i] = np.array([1.0, 0.0])
        elif i == 4:
            in_tan[i] = np.array([0.0, -1.0]); out_tan[i] = np.array([-1.0, 0.0])
        elif i == 5:
            in_tan[i] = np.array([-1.0, 0.0])
            out_tan[i] = unit(next_pt - K_KNOTS[i])
        elif i == 7:
            in_tan[i] = np.array([-0.9826, -0.1859])
            out_tan[i] = np.array([-0.9826, -0.1859])
        elif i == n - 1:
            in_tan[i] = np.array([0.0, -1.0]); out_tan[i] = np.array([0.0, 1.0])
        else:
            t = cr(K_KNOTS, i)
            in_tan[i] = t; out_tan[i] = t

    pts = []
    for i in range(n):
        j = (i + 1) % n
        if i == 3 or i == 4:                         # K4-K5, K5-K6 are skipped
            continue
        P0 = K_KNOTS[i].copy(); P3 = K_KNOTS[j].copy()
        if i == 4 and j == 5:
            dx = abs(P3[0] - P0[0]); dy = abs(P3[1] - P0[1])
            h_out = QARC * dx; h_in = QARC * dy
        else:
            hh = np.linalg.norm(P3 - P0) / 3
            h_out = h_in = hh
        P1 = P0 + h_out * out_tan[i]
        P2 = P3 - h_in * in_tan[j]
        for tt in np.linspace(0, 1, n_per_seg):
            pt = ((1 - tt) ** 3) * P0 + 3 * (1 - tt) ** 2 * tt * P1 + \
                 3 * (1 - tt) * tt ** 2 * P2 + tt ** 3 * P3
            pts.append(pt)
    return np.array(pts)


def point_in_polygon(pt, poly):
    """Even-odd fill rule inside-test."""
    x, y = pt
    n = len(poly)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------------------
# Optimisation
# ---------------------------------------------------------------------------
def main():
    if not HAS_SCIPY:
        print("scipy not available; cannot optimise. Install scipy and rerun.")
        return

    buffers = load_buffers()
    print(f"loaded {len(buffers)} buffer disks")
    K1, K6, K9 = anchors()
    print(f"anchors: K1={K1.tolist()}  K6={K6.tolist()}  K9={K9.tolist()}")

    # Variables: K2x K2z K3x K3z K4x K4z K5x K5z K7x K7z K8x K8z (12)
    # Initial guess from current K_KNOTS but adjusted for csv buffers.
    Kc = c.K_KNOTS
    x0 = np.array([
        Kc[1, 0], Kc[1, 1],         # K2
        Kc[2, 0], Kc[2, 1],         # K3
        Kc[3, 0], Kc[3, 1],         # K4
        Kc[4, 0], Kc[4, 1],         # K5
        Kc[6, 0], Kc[6, 1],         # K7
        Kc[7, 0], Kc[7, 1],         # K8
    ])

    def assemble_K(x):
        K2 = np.array([x[0],  x[1]])
        K3 = np.array([x[2],  x[3]])
        K4 = np.array([x[4],  x[5]])
        K5 = np.array([x[6],  x[7]])
        K7 = np.array([x[8],  x[9]])
        K8 = np.array([x[10], x[11]])
        return np.array([K1, K2, K3, K4, K5, K6, K7, K8, K9])

    def objective(x):
        K = assemble_K(x)
        try:
            poly = build_neck_pts(K, n_per_seg=40)
        except Exception:
            return 1e9
        total = 0.0
        for b in buffers:
            pt = (b["x"], b["z"])
            inside_ = point_in_polygon(pt, poly)
            dx = poly[:, 0] - b["x"]; dz = poly[:, 1] - b["z"]
            min_d = float(np.sqrt(dx * dx + dz * dz).min())
            if not inside_:
                total += 1000.0 + 100.0 * (CLEARANCE - min_d) ** 2 if min_d < CLEARANCE else 1000.0 * min_d
            elif min_d < CLEARANCE:
                total += 50.0 * (CLEARANCE - min_d) ** 2
        # smoothness: penalise large angles between consecutive K knot vectors
        for i in range(1, 9):
            v1 = K[i] - K[i - 1]
            v2 = K[(i + 1) % 9] - K[i]
            n1 = np.linalg.norm(v1); n2 = np.linalg.norm(v2)
            if n1 > 0 and n2 > 0:
                cosang = float(v1.dot(v2) / (n1 * n2))
                # penalise sharp folds (cosang << 1)
                total += max(0.0, 1.0 - cosang) * 20.0
        return total

    print("starting optimisation ...")
    res = minimize(objective, x0, method="Nelder-Mead",
                   options={"xatol": 0.5, "fatol": 0.01, "maxiter": 8000,
                            "adaptive": True, "disp": True})
    print(f"\nfinal objective: {res.fun:.3f}")
    K = assemble_K(res.x)

    # Verify
    poly = build_neck_pts(K, n_per_seg=80)
    violations = 0
    worst = 0.0
    for b in buffers:
        pt = (b["x"], b["z"])
        ins = point_in_polygon(pt, poly)
        dx = poly[:, 0] - b["x"]; dz = poly[:, 1] - b["z"]
        md = float(np.sqrt(dx * dx + dz * dz).min())
        if (not ins) or md < CLEARANCE:
            violations += 1
            worst = max(worst, CLEARANCE - md if ins else md)
    print(f"violations after optimisation: {violations} / {len(buffers)}  worst={worst:.2f} mm")

    # Print K_KNOTS in a paste-ready form
    print("\n# Optimised K_KNOTS (at-rest xz):")
    print("K_KNOTS_RAKED = np.array([")
    labels = ["K1 column LEFT top", "K2 top arc bass peak", "K3 S-knot",
              "K4 top arc treble end", "K5 shoulder", "K6 SBN",
              "K7", "K8", "K9 column LEFT bottom corner"]
    for i, k in enumerate(K):
        print(f"    [{k[0]:8.2f}, {k[1]:8.2f}],   # {labels[i]}")
    print("])")


if __name__ == "__main__":
    main()
