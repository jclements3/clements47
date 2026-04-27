"""build_techdraw.py - generate TechDraw HLR engineering drawings from
clements47.FCStd (built by build_freecad.py).

Run via freecadcmd:

    echo "_p='/home/james.clements/projects/clements47/build_techdraw.py'; \\
          exec(open(_p).read(), {'__file__': _p, '__name__': '__main__'})" \\
        | freecadcmd

Outputs:
    clements47_techdraw.svg          - Top / Front / Right of full assembly
    clements47_shoulder_techdraw.svg - Neck-only HLR detail
"""
import os
import re
import sys

import FreeCAD as App
import TechDraw

_HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_FCSTD = os.path.join(_HERE, "clements47.FCStd")
OUT_FULL     = os.path.join(_HERE, "clements47_techdraw.svg")
OUT_SHOULDER = os.path.join(_HERE, "clements47_shoulder_techdraw.svg")

EXPECTED_FULL     = ("Chamber", "FloorLimacon", "Column", "Neck", "Strings")
EXPECTED_SHOULDER = ("Neck",)

PAGE_W_MM = 1189.0
PAGE_H_MM =  841.0
HIDDEN_W  = ("0.35", "0.350")


def find_features(doc, expected):
    found, seen = [], set()
    for nm in expected:
        obj = doc.getObject(nm)
        if obj is not None:
            found.append(obj)
            seen.add(nm)
    for obj in doc.Objects:
        if obj.TypeId == "Part::Feature" and obj.Name not in seen:
            found.append(obj)
            seen.add(obj.Name)
    return found


def view_svg(view, doc):
    doc.recompute()
    raw = TechDraw.viewPartAsSvg(view)

    def _restyle(match):
        chunk = match.group(0)
        for w in HIDDEN_W:
            if f'stroke-width="{w}"' in chunk or f"stroke-width:{w}" in chunk:
                if "stroke-dasharray" not in chunk:
                    chunk = chunk.replace("<g", '<g stroke-dasharray="2,2"', 1)
                break
        return chunk
    return re.sub(r"<g[^>]*>", _restyle, raw, count=0)


def render_views(views, dest_path, title, doc):
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {PAGE_W_MM:.1f} {PAGE_H_MM:.1f}" '
        f'width="1600" height="{int(1600 * PAGE_H_MM / PAGE_W_MM)}" '
        f'font-family="sans-serif" font-size="10">',
        f'<text x="20" y="20" font-weight="bold" font-size="16">{title}</text>',
    ]
    for view, (cx, cy), label in views:
        frag = view_svg(view, doc)
        parts.append(f'<g transform="translate({cx:.1f}, {cy:.1f})">')
        parts.append(f'<text x="0" y="-6" font-weight="bold">{label}</text>')
        parts.append(frag)
        parts.append("</g>")
    parts.append("</svg>")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))


def make_view(page, sources, name, direction, scale):
    v = page.Document.addObject("TechDraw::DrawViewPart", name)
    v.Source = sources
    v.Direction = App.Vector(*direction)
    v.Scale = scale
    # Enable hidden-line generation so HLR emits dashed-eligible edges.
    try:
        v.HardHidden = True
        v.SmoothVisible = True
    except Exception:
        pass
    page.addView(v)
    return v


def main():
    if not os.path.exists(SOURCE_FCSTD):
        print(f"ERROR: missing {SOURCE_FCSTD}", file=sys.stderr)
        sys.exit(1)
    print(f"opening {SOURCE_FCSTD}")
    doc = App.openDocument(SOURCE_FCSTD)

    full = find_features(doc, EXPECTED_FULL)
    print(f"full-assembly sources: {[o.Name for o in full]}")

    page = doc.addObject("TechDraw::DrawPage", "Page_full")
    tmpl = doc.addObject("TechDraw::DrawSVGTemplate", "Tmpl_full")
    tmpl.Width  = PAGE_W_MM
    tmpl.Height = PAGE_H_MM
    page.Template = tmpl

    SCALE = 0.25
    v_top   = make_view(page, full, "V_top",   (0, 0, 1),  SCALE)
    v_front = make_view(page, full, "V_front", (0, -1, 0), SCALE)
    v_right = make_view(page, full, "V_right", (1, 0, 0),  SCALE)
    v_top.X   = 250; v_top.Y   = 600
    v_front.X = 250; v_front.Y = 200
    v_right.X = 800; v_right.Y = 200

    print("recomputing document (slow HLR step)")
    doc.recompute()

    print("rendering full-assembly SVG")
    render_views(
        [(v_top,   (250, 200), "TOP (look -z)"),
         (v_front, (250, 600), "FRONT (look +y)"),
         (v_right, (800, 600), "RIGHT (look -x)")],
        OUT_FULL, "Clements47 - assembly HLR", doc,
    )
    sz = os.path.getsize(OUT_FULL)
    has_dashed = "stroke-dasharray" in open(OUT_FULL).read()
    print(f"  wrote {OUT_FULL} ({sz:,} bytes, dashed={has_dashed})")

    shoulder = find_features(doc, EXPECTED_SHOULDER)
    if shoulder:
        page2 = doc.addObject("TechDraw::DrawPage", "Page_sh")
        tmpl2 = doc.addObject("TechDraw::DrawSVGTemplate", "Tmpl_sh")
        tmpl2.Width = PAGE_W_MM
        tmpl2.Height = PAGE_H_MM
        page2.Template = tmpl2

        SH_SCALE = 0.5
        v_sh_top   = make_view(page2, shoulder, "V_sh_top",   (0, 0, 1),  SH_SCALE)
        v_sh_front = make_view(page2, shoulder, "V_sh_front", (0, -1, 0), SH_SCALE)
        v_sh_right = make_view(page2, shoulder, "V_sh_right", (1, 0, 0),  SH_SCALE)
        v_sh_top.X   = 250; v_sh_top.Y   = 600
        v_sh_front.X = 250; v_sh_front.Y = 200
        v_sh_right.X = 800; v_sh_right.Y = 200
        doc.recompute()

        print("rendering shoulder-detail SVG")
        render_views(
            [(v_sh_top,   (250, 200), "TOP (look -z)"),
             (v_sh_front, (250, 600), "FRONT (look +y)"),
             (v_sh_right, (800, 600), "RIGHT (look -x)")],
            OUT_SHOULDER, "Clements47 - neck HLR detail", doc,
        )
        sz = os.path.getsize(OUT_SHOULDER)
        has_dashed = "stroke-dasharray" in open(OUT_SHOULDER).read()
        print(f"  wrote {OUT_SHOULDER} ({sz:,} bytes, dashed={has_dashed})")

    print("done.")


if __name__ == "__main__":
    main()
