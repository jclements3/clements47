#!/usr/bin/env python3
"""make_neck_svg.py - emit a clean neck.svg containing the closed neck
Bezier path (N0..N9 + close), reference dots for the N knots, and the
buffer disks for visual context. No labels, no envelope, no extras.
Intended for hand-editing in Inkscape.

Side-view convention (xz):
  x increases right (treble), z increases upward (away from floor).
  SVG y flipped via group transform so z renders upward in Inkscape.
"""
import os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import clements47 as c
import build_views as bv
from make_buffer_svg import buffer_centres

OUT_PATH = os.path.join(HERE, "neck.svg")

R = float(c.CLEARANCE)
COL_FLAT  = "#c00000"
COL_NAT   = "#2ca02c"
COL_SHARP = "#1060d0"
COL_PIN   = "#e0a020"
COL_NECK  = "#3a2a14"
COL_KNOT  = "#202020"


def main():
    # Build the side view to populate _LAST_NECK_D.
    strings = bv.load_strings()
    bv.side_view_content(strings)
    neck_d = bv._LAST_NECK_D

    centres, types = buffer_centres(strings)

    # Bounding box for the viewBox: include all buffers, all N knots, and
    # the neck path samples (just use buffers and knots since the path is
    # close to those).
    pts = [centres]
    pts.append(c.N_KNOTS)
    pts = np.vstack(pts)
    pad = 30.0
    x_min = float(pts[:, 0].min()) - pad
    x_max = float(pts[:, 0].max()) + pad
    z_min = float(pts[:, 1].min()) - pad
    z_max = float(pts[:, 1].max()) + pad
    W = x_max - x_min
    H = z_max - z_min

    out = []
    out.append('<?xml version="1.0" encoding="UTF-8"?>')
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{x_min:.2f} {-z_max:.2f} {W:.2f} {H:.2f}" '
        f'width="{W:.0f}mm" height="{H:.0f}mm">')
    out.append('<g transform="scale(1,-1)">')

    # Buffer disks (context, semi-transparent).
    color = {"flat": COL_FLAT, "nat": COL_NAT, "sharp": COL_SHARP, "pin": COL_PIN}
    for (cx, cz), t in zip(centres, types):
        out.append(
            f'<circle cx="{cx:.3f}" cy="{cz:.3f}" r="{R:.3f}" '
            f'fill="{color[t]}" fill-opacity="0.12" stroke="{color[t]}" '
            f'stroke-width="0.3" stroke-opacity="0.45"/>')

    # Neck path (the editable curve).
    out.append(
        f'<path d="{neck_d}" fill="none" stroke="{COL_NECK}" '
        f'stroke-width="1.4"/>')

    # N-knot dots + labels for reference.
    N = c.N_KNOTS
    for i, (x, z) in enumerate(N):
        out.append(
            f'<circle cx="{x:.3f}" cy="{z:.3f}" r="2.5" fill="{COL_KNOT}"/>')
        # Label (matrix flips text upright in y-flipped group).
        out.append(
            f'<text transform="matrix(1,0,0,-1,{x+6:.1f},{z+6:.1f})" '
            f'font-family="sans-serif" font-size="11" font-weight="700" '
            f'fill="{COL_KNOT}">N{i}</text>')

    out.append('</g>')
    out.append('</svg>')
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out))
    print(f"Wrote {OUT_PATH}")
    print(f"  neck path: M={neck_d.count('M')} C={neck_d.count('C')} "
          f"Z={neck_d.count('Z')} len={len(neck_d)} chars")
    print(f"  N-knots: {len(N)}")


if __name__ == "__main__":
    main()
