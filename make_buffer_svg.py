#!/usr/bin/env python3
"""make_buffer_svg.py — emit a clean buffer.svg containing only the buffer
disks (Nf_flat red, Nf_nat green, Nf_sharp blue, pin tip yellow-ochre) and
the current outer envelope path. No labels, no points, no string lines.
Intended for hand-editing in Inkscape.

Side-view convention (xz):
  x increases to the right (treble)
  z increases upward (away from the floor)
SVG y is flipped via a group transform so z renders upward in Inkscape.
"""
import csv, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clements47 as c
import build_views as bv

OUT_PATH = os.path.join(HERE, "buffer.svg")

R = float(c.CLEARANCE)
PIN_LEN = 38.96
PIN_ANG = 12.01
COL_FLAT = "#c00000"
COL_NAT  = "#2ca02c"
COL_SHARP = "#1060d0"
COL_PIN  = "#e0a020"
COL_ENV  = "#0a8"


def buffer_centres(strings):
    """Return (centres, types) where centres is (N,2) xz and types is a
    parallel list of 'flat'/'nat'/'sharp'/'pin'."""
    centres, types = [], []
    cos_p = math.cos(math.radians(PIN_ANG))
    sin_p = math.sin(math.radians(PIN_ANG))
    for s in strings:
        nx, nz = s["Nf_flat"][0], s["Nf_flat"][2]
        centres.append((s["Nf_flat"][0],  s["Nf_flat"][2]));  types.append("flat")
        centres.append((s["Nf_nat"][0],   s["Nf_nat"][2]));   types.append("nat")
        centres.append((s["Nf_sharp"][0], s["Nf_sharp"][2])); types.append("sharp")
        gx, gz = s["g"][0], s["g"][2]
        dx, dz = nx - gx, nz - gz
        L = math.hypot(dx, dz)
        if L > 0:
            ux, uz = dx/L, dz/L
            px = ux*cos_p + uz*sin_p
            pz = -ux*sin_p + uz*cos_p
            centres.append((nx + PIN_LEN*px, nz + PIN_LEN*pz))
            types.append("pin")
    return np.array(centres), types


def envelope_path_d(centres, R):
    """Convex-hull-with-arcs envelope, smoothed to cubic Beziers. Matches
    the side-view envelope in build_views.py."""
    from scipy.spatial import ConvexHull
    hull = ConvexHull(centres)
    hp = centres[hull.vertices]
    nh = len(hp)
    signed = sum((hp[(i+1)%nh,0]-hp[i,0])*(hp[(i+1)%nh,1]+hp[i,1]) for i in range(nh))
    if signed > 0: hp = hp[::-1]
    edge_normals = []
    for i in range(nh):
        a = hp[i]; b = hp[(i+1)%nh]
        dd = b - a; dd = dd / np.linalg.norm(dd)
        edge_normals.append(np.array([dd[1], -dd[0]]))
    parts = []
    for i in range(nh):
        n_in = edge_normals[(i-1)%nh]; n_out = edge_normals[i]
        tan_in = hp[i] + R * n_in; tan_out = hp[i] + R * n_out
        if i == 0: parts.append(f"M {tan_in[0]:.3f},{tan_in[1]:.3f}")
        th_a = math.atan2(n_in[1], n_in[0])
        th_b = math.atan2(n_out[1], n_out[0])
        sweep = (th_b - th_a) % (2*math.pi)
        n_quad = max(1, int(math.ceil(sweep / (0.5*math.pi))))
        step = sweep / n_quad
        f_ctl = (4.0/3.0) * math.tan(step/4.0)
        for k in range(n_quad):
            a0 = th_a + k*step; a1 = a0 + step
            c0,s0 = math.cos(a0), math.sin(a0)
            c1,s1 = math.cos(a1), math.sin(a1)
            P1 = hp[i] + R*np.array([c0 - f_ctl*s0, s0 + f_ctl*c0])
            P2 = hp[i] + R*np.array([c1 + f_ctl*s1, s1 - f_ctl*c1])
            P3 = hp[i] + R*np.array([c1, s1])
            parts.append(f"C {P1[0]:.3f},{P1[1]:.3f} {P2[0]:.3f},{P2[1]:.3f} {P3[0]:.3f},{P3[1]:.3f}")
        next_tan_in = hp[(i+1)%nh] + R * n_out
        parts.append(f"L {next_tan_in[0]:.3f},{next_tan_in[1]:.3f}")
    parts.append("Z")
    return " ".join(parts)


def _legacy_disk_union(centres, R):
    """Old gift-wrap (kept as a fallback / reference)."""
    n = len(centres)
    TWO_PI = 2.0 * np.pi
    EPS = 1e-9
    order = np.lexsort((centres[:, 1], centres[:, 0]))
    i0 = int(order[0])
    theta_start = np.pi
    i = i0
    theta_curr = theta_start
    segments = []
    for _step in range(n + 5):
        ci = centres[i]
        candidates = []
        for j in range(n):
            if j == i: continue
            d = centres[j] - ci
            D = float(np.hypot(d[0], d[1]))
            if D < EPS: continue
            alpha = math.atan2(d[1], d[0])
            if D >= 2.0 * R:
                ts_i = (alpha - 0.5*math.pi) % TWO_PI
                tc_j = ts_i
                is_t = True
            else:
                beta = math.acos(max(-1.0, min(1.0, D/(2.0*R))))
                ts_i = (alpha - beta) % TWO_PI
                tc_j = (alpha + math.pi + beta) % TWO_PI
                is_t = False
            dth = (ts_i - theta_curr) % TWO_PI
            if dth < EPS: dth = TWO_PI
            candidates.append((dth, D, j, ts_i, tc_j, is_t))
        if not candidates: break
        candidates.sort(key=lambda t: (t[0], t[1]))
        ANG_TOL = 1e-3
        chosen = None
        for cand in candidates:
            cdth = cand[0]
            near = [t for t in candidates if t[0] - cdth < ANG_TOL]
            near.sort(key=lambda t: t[1])
            cand2 = near[0]
            blocked = False
            if cand2[5]:  # tangent — check blocking
                cts = cand2[3]
                n_vec = np.array([math.cos(cts), math.sin(cts)])
                p_from = ci + R*n_vec
                p_to = centres[cand2[2]] + R*n_vec
                seg_dir = p_to - p_from
                seg_len = float(np.hypot(*seg_dir))
                if seg_len > EPS:
                    seg_u = seg_dir/seg_len
                    seg_perp = np.array([-seg_u[1], seg_u[0]])
                    for k in range(n):
                        if k == i or k == cand2[2]: continue
                        v = centres[k] - p_from
                        perp = abs(v[0]*seg_perp[0] + v[1]*seg_perp[1])
                        along = v[0]*seg_u[0] + v[1]*seg_u[1]
                        if perp < R - EPS and EPS < along < seg_len - EPS:
                            blocked = True; break
            if not blocked:
                chosen = cand2; break
        if chosen is None: break
        _, _, bj, bts, btcj, bisT = chosen
        segments.append(("arc", i, theta_curr, bts))
        if bisT:
            n_vec = np.array([math.cos(bts), math.sin(bts)])
            segments.append(("line", ci + R*n_vec, centres[bj] + R*n_vec))
        if bj == i0:
            segments.append(("arc", i0, btcj, theta_start))
            break
        i = bj; theta_curr = btcj
    parts = []; first = True
    for seg in segments:
        if seg[0] == "arc":
            _, idx, ta, tb = seg
            ca = centres[idx]
            pa = ca + R*np.array([math.cos(ta), math.sin(ta)])
            pb = ca + R*np.array([math.cos(tb), math.sin(tb)])
            if first:
                parts.append(f"M {pa[0]:.3f},{pa[1]:.3f}"); first = False
            sweep = (tb - ta) % TWO_PI
            large = 1 if sweep > math.pi else 0
            parts.append(f"A {R:.3f},{R:.3f} 0 {large} 1 {pb[0]:.3f},{pb[1]:.3f}")
        else:
            _, p_from, p_to = seg
            if first:
                parts.append(f"M {p_from[0]:.3f},{p_from[1]:.3f}"); first = False
            parts.append(f"L {p_to[0]:.3f},{p_to[1]:.3f}")
    parts.append("Z")
    return " ".join(parts)


def main():
    strings = bv.load_strings()
    centres, types = buffer_centres(strings)
    env_d = envelope_path_d(centres, R)

    # ViewBox: bounding box of buffers + envelope, with a small margin.
    xs = centres[:, 0]; zs = centres[:, 1]
    pad = 30.0
    x_min = float(xs.min()) - R - pad
    x_max = float(xs.max()) + R + pad
    z_min = float(zs.min()) - R - pad
    z_max = float(zs.max()) + R + pad
    W = x_max - x_min
    H = z_max - z_min

    # SVG: y-flip group so z renders upward in Inkscape.
    color = {"flat": COL_FLAT, "nat": COL_NAT, "sharp": COL_SHARP, "pin": COL_PIN}
    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{x_min:.2f} {-z_max:.2f} {W:.2f} {H:.2f}" '
        f'width="{W:.0f}mm" height="{H:.0f}mm">')
    out.append(f'<g transform="scale(1,-1)">')
    # Buffer disks — fill, no stroke, semi-opaque.
    for (cx, cz), t in zip(centres, types):
        out.append(
            f'<circle cx="{cx:.3f}" cy="{cz:.3f}" r="{R:.3f}" '
            f'fill="{color[t]}" fill-opacity="0.18" stroke="{color[t]}" '
            f'stroke-width="0.4" stroke-opacity="0.6"/>')
    # Envelope.
    out.append(
        f'<path d="{env_d}" fill="none" stroke="{COL_ENV}" '
        f'stroke-width="1.0" stroke-dasharray="4,3"/>')
    out.append("</g>")
    out.append("</svg>")
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out))
    print(f"Wrote {OUT_PATH}")
    print(f"  centres: {len(centres)} (47x4)   envelope path: "
          f"{env_d.count('A')} arcs, {env_d.count(' L ')} lines")


if __name__ == "__main__":
    main()
