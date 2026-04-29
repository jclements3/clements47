#!/usr/bin/env python3
"""optimize_neck_hug.py — minimise area between the neck path and the outer
buffer envelope.

1. Build outer envelope = ConvexHull of all 141 buffer disk centres, offset
   outward by CLEARANCE = 8 mm.
2. Objective: area(neck_polygon) - area(envelope) (minimise excess area)
              + heavy penalty if any buffer disk pokes through the neck.
3. Free vars: K2, K3, K7, K8 (positions). Fixed handles per design.

Uses the F/P/B/E/N/C/S region naming (see clements47.py): K-names in this
file map to N-names as K1=N0, K2=N9, K3=N8, K4=N7, K5=N6, K6=N5, K7=N4,
K8=N3, K9=N2, K10=N1. The optimizer reads/writes N_KNOTS directly.
"""
import csv as _csv, math, os, sys
import numpy as np
import clements47 as c

try:
    from scipy.optimize import minimize
    from scipy.spatial import ConvexHull
    HAS_SCIPY = True
except Exception:
    HAS_SCIPY = False

HERE = os.path.dirname(os.path.abspath(__file__))
STRINGS_CSV = os.path.join(HERE, "strings.csv")
CLEARANCE = c.CLEARANCE
PIN_LEN = 38.96
PIN_ANGLE_DEG = 12.01


def load_buffers():
    with open(STRINGS_CSV) as f:
        clean = "\n".join(ln for ln in f
                          if not ln.lstrip().startswith("#") and ln.strip())
    rows = list(_csv.DictReader(clean.splitlines()))
    def fnum(r, k):
        v = (r.get(k) or "").strip(); return float(v) if v else 0.0
    pts = []
    cos_p = math.cos(math.radians(PIN_ANGLE_DEG))
    sin_p = math.sin(math.radians(PIN_ANGLE_DEG))
    for r in rows:
        Ng_x = fnum(r, "Ng_x_mm"); Ng_y = fnum(r, "Ng_y_mm")
        gz = c.grommet_z_on_S(Ng_x)
        if gz is None: gz = Ng_y + c.Z_OFFSET
        def disc(prefix):
            dx = fnum(r, prefix+"_x_mm"); dy = fnum(r, prefix+"_y_mm"); dz = fnum(r, prefix+"_z_mm")
            return (dx-dz, gz+(dy-Ng_y))
        Nf_f = disc("Nf_flat"); Nf_s = disc("Nf_sharp")
        # Pin tip
        gx, gz_g = Ng_x, gz
        nx, nz = Nf_f
        dx = nx - gx; dz_str = nz - gz_g
        L = math.hypot(dx, dz_str)
        ux, uz = (dx/L, dz_str/L) if L > 0 else (0.0, 1.0)
        px = ux*cos_p + uz*sin_p
        pz = -ux*sin_p + uz*cos_p
        pin_top = (nx + PIN_LEN*px, nz + PIN_LEN*pz)
        pts += [Nf_f, Nf_s, pin_top]
    return pts


def expand_hull_outward(hull_pts, offset):
    """Offset a closed convex polygon outward by `offset`. hull_pts is
    ordered CCW or CW; we ensure CCW."""
    pts = np.array(hull_pts, dtype=float)
    # Ensure CCW
    s = sum((pts[(i+1)%len(pts), 0] - pts[i,0]) * (pts[(i+1)%len(pts), 1] + pts[i,1])
            for i in range(len(pts)))
    if s > 0:
        pts = pts[::-1]
    out = []
    n = len(pts)
    for i in range(n):
        p_prev = pts[(i-1)%n]; p_cur = pts[i]; p_next = pts[(i+1)%n]
        e1 = p_cur - p_prev; e1 = e1 / np.linalg.norm(e1)
        e2 = p_next - p_cur; e2 = e2 / np.linalg.norm(e2)
        n1 = np.array([e1[1], -e1[0]])  # outward normal (CCW)
        n2 = np.array([e2[1], -e2[0]])
        bisector = n1 + n2; bisector = bisector / np.linalg.norm(bisector)
        # Distance to slide along bisector to maintain offset
        cosa = float(n1.dot(bisector))
        d = offset / cosa if abs(cosa) > 1e-9 else offset
        out.append(p_cur + d * bisector)
    return np.array(out)


def build_neck_pts(N_full, n_per_seg=60):
    """N_full is a 10-row CCW array (N0..N9). Walk it in CW path order to
    match the legacy K1..K9->K10->K1 segment geometry exactly."""
    seq_idx = [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]   # CW path: K1..K9 then K10
    seq = [N_full[i] for i in seq_idx] + [N_full[seq_idx[0]]]   # close
    nseq = len(seq)

    SB = (c.SB_P0, c.SB_P1, c.SB_P2, c.SB_P3)
    tan1 = c.bez_tan(*SB, 1.0); tan1_u = tan1 / np.linalg.norm(tan1)
    St_pt = c.SB_P3 + 2.0*c.AIR_GAP*tan1_u
    Ut_top = N_full[6]    # = N6 = K5 = Ut
    K5_out = (St_pt - Ut_top); K5_out = K5_out / np.linalg.norm(K5_out)
    K6_smooth = K5_out
    col_top  = (seq[10]-seq[9]); col_top = col_top/np.linalg.norm(col_top)
    col_left = (seq[9]-seq[8]);  col_left = col_left/np.linalg.norm(col_left)

    def _u(v):
        n = float(np.linalg.norm(v));  return v/n if n>0 else v

    K5_idx, K6_idx = 4, 5
    K9_idx, K10_idx = 8, 9
    tangents = [None]*nseq
    for i in range(1, nseq-1):
        if i == K5_idx:   tangents[i] = K5_out
        elif i == K6_idx: tangents[i] = K6_smooth
        elif i == K9_idx: tangents[i] = col_left
        elif i == K10_idx: tangents[i] = col_top
        else: tangents[i] = _u(np.array(seq[i+1]) - np.array(seq[i-1]))
    tangents[0]  = col_top
    tangents[-1] = col_top

    pts = []
    for i in range(nseq-1):
        P0 = np.array(seq[i]); P3 = np.array(seq[i+1])
        chord = np.linalg.norm(P3-P0)
        h_out = chord/3.0; h_in = chord/3.0
        if i == K9_idx or i == K10_idx:
            cu = (P3-P0)/chord if chord>0 else np.array([1.0,0.0])
            P1 = P0 + h_out*cu; P2 = P3 - h_in*cu
        elif i == 3:
            P1 = P0 + h_out*tangents[i]; P2 = P3 + h_in*tan1_u
        else:
            P1 = P0 + h_out*tangents[i]; P2 = P3 - h_in*tangents[i+1]
        for tt in np.linspace(0,1,n_per_seg):
            pt = ((1-tt)**3)*P0 + 3*(1-tt)**2*tt*P1 + 3*(1-tt)*tt**2*P2 + tt**3*P3
            pts.append(pt)
    return np.array(pts)


def polygon_area(poly):
    x = poly[:,0]; y = poly[:,1]
    return 0.5*abs(np.dot(x, np.roll(y,-1)) - np.dot(np.roll(x,-1), y))


def point_in_poly(pt, poly):
    x, y = pt; n = len(poly); inside = False; j = n-1
    for i in range(n):
        xi,yi = poly[i]; xj,yj = poly[j]
        if ((yi>y)!=(yj>y)) and (x < (xj-xi)*(y-yi)/(yj-yi+1e-12) + xi):
            inside = not inside
        j = i
    return inside


def main():
    if not HAS_SCIPY: print("scipy required."); return
    buffers = load_buffers()
    print(f"loaded {len(buffers)} buffer disks")
    bpts = np.array(buffers)
    hull = ConvexHull(bpts)
    hull_pts = bpts[hull.vertices]
    envelope = expand_hull_outward(hull_pts, CLEARANCE)
    env_area = polygon_area(envelope)
    print(f"buffer convex hull: {len(hull_pts)} points, envelope area: {env_area:.0f} mm^2")

    Nc = c.N_KNOTS.copy()
    # Free vars: K2 (= N9), K3 (= N8), K7 (= N4), K8 (= N3) — same 8 floats
    # as the legacy optimizer; meanings preserved via N-index mapping.
    x0 = np.array([Nc[9,0], Nc[9,1], Nc[8,0], Nc[8,1],
                   Nc[4,0], Nc[4,1], Nc[3,0], Nc[3,1]])

    def assemble(x):
        N = Nc.copy()
        N[9] = (x[0],x[1])    # K2 = N9
        N[8] = (x[2],x[3])    # K3 = N8
        N[4] = (x[4],x[5])    # K7 = N4
        N[3] = (x[6],x[7])    # K8 = N3
        return N

    def objective(x):
        N = assemble(x)
        try:
            poly = build_neck_pts(N, n_per_seg=40)
        except Exception:
            return 1e9
        # Buffer-disk encroachment penalty
        penalty = 0.0
        for b in buffers:
            inside_ = point_in_poly(b, poly)
            if not inside_:
                # Distance to neck
                dx = poly[:,0]-b[0]; dz = poly[:,1]-b[1]
                md = float(np.sqrt(dx*dx + dz*dz).min())
                penalty += 5000.0 + 500.0*md
            else:
                dx = poly[:,0]-b[0]; dz = poly[:,1]-b[1]
                md = float(np.sqrt(dx*dx + dz*dz).min())
                if md < CLEARANCE:
                    penalty += 200.0 * (CLEARANCE-md)**2
        # Excess area: neck area minus envelope area
        neck_area = polygon_area(poly)
        excess = max(0.0, neck_area - env_area)
        return penalty + 0.01 * excess  # weight excess area lightly

    print("optimising ...")
    res = minimize(objective, x0, method="Nelder-Mead",
                   options={"xatol": 0.5, "fatol": 0.5, "maxiter": 15000,
                            "adaptive": True, "disp": True})
    print(f"\nfinal objective: {res.fun:.3f}")
    N = assemble(res.x)
    poly = build_neck_pts(N, n_per_seg=80)
    viol = 0; worst = 0.0
    for b in buffers:
        ins = point_in_poly(b, poly)
        dx = poly[:,0]-b[0]; dz = poly[:,1]-b[1]
        md = float(np.sqrt(dx*dx + dz*dz).min())
        if (not ins) or md < CLEARANCE:
            viol += 1; worst = max(worst, (CLEARANCE-md) if ins else md)
    excess = polygon_area(poly) - env_area
    print(f"violations: {viol}/{len(buffers)}  worst={worst:.2f}mm  excess area: {excess:.0f} mm^2")
    print()
    print("# Optimised N_KNOTS:")
    labels = [
        "N0 = K1 col-top",
        "N1 = K10 col-inner-top (derived)",
        "N2 = K9 col-inner",
        "N3 = K8",
        "N4 = K7",
        "N5 = K6 = St",
        "N6 = K5 = Ut",
        "N7 = K4",
        "N8 = K3",
        "N9 = K2",
    ]
    print("N_KNOTS = np.array([")
    for i, n in enumerate(N):
        print(f"    [{n[0]:8.2f}, {n[1]:8.2f}],   # {labels[i]}")
    print("])")


if __name__ == "__main__":
    main()
