"""Add missing mechanism parts to Clements47.FCStd.

Missing parts identified from ML Harps reference images:
1. Bearings/bushings — cylindrical sleeves in action plates where axles pass through
2. Spindle nuts/collars — threaded fasteners locking discs onto axles
3. Guide rails — curved steel rods running parallel to linkage chains
4. Column/pillar — structural tube from base to neck
5. Tuning pins — at top of neck where strings terminate
6. Rocker levers — at column top, connect pedal rods to first crank in chain
7. Pedal rods — steel rods inside column, one per note

Run:  echo 'exec(open("add_missing_parts.py").read())' | ~/.local/bin/freecad -c
"""
import json, math
import FreeCAD, Part

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

# Bearing dimensions (visible as white cylindrical sleeves in frame 0142)
BEARING_OD_BASS  = 12.0    # mm outer diameter, bass bearings (6008 series)
BEARING_OD_MID   = 10.0    # mm outer diameter, mid-range (6006/6905)
BEARING_OD_TREB  = 8.0     # mm outer diameter, treble (6904 series)
BEARING_WIDTH    = 6.0     # mm width (axial length)
BEARING_FLANGE   = 1.5     # mm flange extension beyond OD

# Spindle nut/collar (dark threaded fasteners on axle, visible frame 0298)
NUT_OD           = 8.0     # mm hex nut across flats
NUT_THICK        = 3.0     # mm

# Guide rails (curved steel rods parallel to linkage chains, frame 0134)
RAIL_DIA         = 5.0     # mm rail rod diameter
RAIL_OFFSET_Y    = 10.0    # mm offset from crank plane

# Column/pillar
COL_OD           = 60.0    # mm outer diameter
COL_ID           = 50.0    # mm inner diameter (hollow for pedal rods)
COL_BASE_Z       = 0.0     # mm floor level

# Tuning pins (at top of neck)
PIN_DIA          = 7.0     # mm tuning pin diameter
PIN_LENGTH       = 40.0    # mm exposed length above neck

# Rocker levers (at column top, 7 total)
ROCKER_LEN       = 30.0    # mm lever arm length
ROCKER_WIDTH     = 8.0     # mm
ROCKER_THICK     = 5.0     # mm

# Pedal rods (inside column)
PEDAL_ROD_DIA    = 4.0     # mm

# Action plate dimensions (matching add_linkage.py)
AXLE_LEN         = 44.0
PLATE_THICK      = 3.0

import os
PROJECT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '/home/clementsj/projects/clements47'

with open(f'{PROJECT}/clements47.json') as f:
    data = json.load(f)

doc = FreeCAD.open(f'{PROJECT}/Clements47.FCStd')

strings = {k: v for k, v in data['st'].items() if isinstance(v, dict) and 'sn' in v}
axles = data['as']
neck = data['nk']

ordered = sorted(strings.items(), key=lambda kv: kv[1]['sn'])

print("Adding missing mechanism parts...")

# ── 1. BEARINGS ──────────────────────────────────────────────────────────────
# Flanged sleeve bearings at each action plate hole. Two per axle (front + back).
# Visible in frame 0142 as white cylindrical sleeves with dark center bore.

bearing_count = 0
for key, s in ordered:
    a = axles[key]
    ox = s['o']['x']
    nz = s['n']['z']
    ar = a['ad'] / 2.0
    side = a['sd']
    bearing_code = a['b']

    # Select bearing OD based on bearing code
    if bearing_code == '6008':
        bod = BEARING_OD_BASS
    elif bearing_code in ('6006', '6905'):
        bod = BEARING_OD_MID
    else:
        bod = BEARING_OD_TREB

    # Front bearing (audience side, y = +AXLE_LEN + PLATE_THICK)
    # Back bearing (harpist side, y = -AXLE_LEN - PLATE_THICK)
    front_y = AXLE_LEN + 2.0  # matches plate position from add_linkage.py
    back_y = -AXLE_LEN - 2.0 - PLATE_THICK

    for pos_name, py in [("F", front_y), ("B", back_y)]:
        bname = f"Brg{pos_name}_{key.upper()}"
        if doc.getObject(bname):
            continue

        # Outer sleeve
        outer = Part.makeCylinder(bod / 2.0, BEARING_WIDTH,
            FreeCAD.Vector(ox, py - BEARING_WIDTH / 2.0, nz),
            FreeCAD.Vector(0, 1, 0))

        # Flange ring (wider, thin)
        flange = Part.makeCylinder(bod / 2.0 + BEARING_FLANGE, 1.0,
            FreeCAD.Vector(ox, py - 0.5, nz),
            FreeCAD.Vector(0, 1, 0))

        # Inner bore (axle clearance)
        bore = Part.makeCylinder(ar + 0.25, BEARING_WIDTH + 0.2,
            FreeCAD.Vector(ox, py - BEARING_WIDTH / 2.0 - 0.1, nz),
            FreeCAD.Vector(0, 1, 0))

        shape = outer.fuse(flange).cut(bore)
        obj = doc.addObject("Part::Feature", bname)
        obj.Shape = shape
        bearing_count += 1

print(f"  {bearing_count} bearings done")

# ── 2. SPINDLE NUTS/COLLARS ──────────────────────────────────────────────────
# Locking collars on each axle between disc and bearing. Visible as dark
# hexagonal fasteners in frame 0298. Two per axle (one per disc).

nut_count = 0
for key, s in ordered:
    a = axles[key]
    ox = s['o']['x']
    nz = s['n']['z']
    ar = a['ad'] / 2.0
    side = a['sd']
    sign = -1.0 if side == 'L' else 1.0

    # Nut positions: just outside each disc (between disc and bearing)
    # Natural disc at np mm, sharp disc at sp mm from string plane
    for disc_pos, prefix in [(a['np'], 'NatNut'), (a['sp'], 'ShpNut')]:
        nname = f"{prefix}_{key.upper()}"
        if doc.getObject(nname):
            continue

        # Nut sits just outside the disc (away from string plane)
        nut_center_y = sign * (disc_pos + 2.0 + NUT_THICK / 2.0)

        # Hexagonal nut approximated as cylinder
        nut = Part.makeCylinder(NUT_OD / 2.0, NUT_THICK,
            FreeCAD.Vector(ox, nut_center_y - NUT_THICK / 2.0, nz),
            FreeCAD.Vector(0, 1, 0))

        # Bore
        bore = Part.makeCylinder(ar + 0.1, NUT_THICK + 0.2,
            FreeCAD.Vector(ox, nut_center_y - NUT_THICK / 2.0 - 0.1, nz),
            FreeCAD.Vector(0, 1, 0))

        shape = nut.cut(bore)
        obj = doc.addObject("Part::Feature", nname)
        obj.Shape = shape
        nut_count += 1

print(f"  {nut_count} spindle nuts done")

# ── 3. GUIDE RAILS ───────────────────────────────────────────────────────────
# Curved steel rods running parallel to the linkage rod chains.
# Visible in frame 0134 as long gray rods with the linkage rods sliding
# between them. 4 rails total: 2 for natural chain, 2 for sharp chain.
# Each pair brackets the linkage rods (above/below or inside/outside).

# Get the X-Z path from bass to treble (following pin line)
path_points = []
for key, s in ordered:
    path_points.append((s['o']['x'], s['n']['z']))

# Sort by x
path_points.sort(key=lambda p: p[0])

# Rails follow the pin line with Y offset
# Natural rails at crank natural arm tip Z level
# Sharp rails at crank sharp arm tip X level
# We'll create segmented rails connecting adjacent string positions

NAT_ARM_LEN_V = 20.0

rail_count = 0
for rail_name, z_offset, y_offset in [
    ("NatRailU", NAT_ARM_LEN_V + 5.0, -AXLE_LEN - RAIL_OFFSET_Y),
    ("NatRailL", NAT_ARM_LEN_V - 5.0, -AXLE_LEN - RAIL_OFFSET_Y),
    ("ShpRailU", 5.0, AXLE_LEN + RAIL_OFFSET_Y),
    ("ShpRailL", -5.0, AXLE_LEN + RAIL_OFFSET_Y),
]:
    if doc.getObject(rail_name):
        continue

    # Build rail as a pipe (wire + circular cross-section) along the pin line
    edges = []
    for i in range(len(path_points) - 1):
        x1, z1 = path_points[i]
        x2, z2 = path_points[i + 1]
        p1 = FreeCAD.Vector(x1, y_offset, z1 + z_offset)
        p2 = FreeCAD.Vector(x2, y_offset, z2 + z_offset)
        edges.append(Part.makeLine(p1, p2))

    wire = Part.Wire(edges)
    # makePipeShell with circular profile
    circle = Part.makeCircle(RAIL_DIA / 2.0,
        FreeCAD.Vector(path_points[0][0], y_offset, path_points[0][1] + z_offset),
        FreeCAD.Vector(0, 0, 1))
    profile = Part.Wire([circle])
    try:
        rail = Part.makeSweep(wire, [profile], True, False)  # solid, not Frenet
    except Exception:
        # Fallback: individual cylinder segments
        segments = []
        for e in edges:
            p1 = e.Vertexes[0].Point
            p2 = e.Vertexes[1].Point
            d = p2 - p1
            seg = Part.makeCylinder(RAIL_DIA / 2.0, d.Length, p1, d)
            segments.append(seg)
        rail = segments[0]
        for seg in segments[1:]:
            rail = rail.fuse(seg)

    obj = doc.addObject("Part::Feature", rail_name)
    obj.Shape = rail
    rail_count += 1

print(f"  {rail_count} guide rails done")

# ── 4. COLUMN / PILLAR ───────────────────────────────────────────────────────
# Structural tube from base to neck. Visible throughout as dark striped
# cylinder at left side of images.
# Position: at the bass end (x~0), connecting floor to neck.

col_name = "Column"
if not doc.getObject(col_name):
    bass_z = strings['c1']['n']['z']  # ~1430mm (top of column at neck)

    outer = Part.makeCylinder(COL_OD / 2.0, bass_z,
        FreeCAD.Vector(-50, 0, 0), FreeCAD.Vector(0, 0, 1))
    inner = Part.makeCylinder(COL_ID / 2.0, bass_z - 20,
        FreeCAD.Vector(-50, 0, 10), FreeCAD.Vector(0, 0, 1))

    shape = outer.cut(inner)
    obj = doc.addObject("Part::Feature", col_name)
    obj.Shape = shape
    print("  column done")
else:
    print("  column exists")

# ── 5. TUNING PINS ───────────────────────────────────────────────────────────
# Steel pins at top of neck where strings wrap. One per string.
# Extend upward from pin height.

pin_count = 0
for key, s in ordered:
    pname = f"Pin_{key.upper()}"
    if doc.getObject(pname):
        continue

    ox = s['o']['x']
    nz = s['n']['z']

    pin = Part.makeCylinder(PIN_DIA / 2.0, PIN_LENGTH,
        FreeCAD.Vector(ox, 0, nz), FreeCAD.Vector(0, 0, 1))
    obj = doc.addObject("Part::Feature", pname)
    obj.Shape = pin
    pin_count += 1

print(f"  {pin_count} tuning pins done")

# ── 6. PEDAL RODS ────────────────────────────────────────────────────────────
# 7 steel rods inside the column, one per note (C,D,E,F,G,A,B).
# Run from near floor level up to the neck where they connect to rockers.

NOTE_GROUPS = {
    'C': ['c1','c2','c3','c4','c5','c6','c7'],
    'D': ['d1','d2','d3','d4','d5','d6','d7'],
    'E': ['e1','e2','e3','e4','e5','e6','e7'],
    'F': ['f1','f2','f3','f4','f5','f6','f7'],
    'G': ['g1','g2','g3','g4','g5','g6','g7'],
    'A': ['a1','a2','a3','a4','a5','a6'],
    'B': ['b1','b2','b3','b4','b5','b6'],
}

rod_count = 0
col_x = -50.0  # column center X
for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
    rname = f"PedalRod_{note}"
    if doc.getObject(rname):
        continue

    # Distribute 7 rods in a circle inside the column
    angle = i * 2 * math.pi / 7
    rod_x = col_x + 15.0 * math.cos(angle)
    rod_y = 15.0 * math.sin(angle)

    # Rod runs from base (~z=50) to neck entry point
    # Top Z: average pin height of this note's bass string
    bass_key = NOTE_GROUPS[note][0]
    top_z = strings[bass_key]['n']['z']

    rod = Part.makeCylinder(PEDAL_ROD_DIA / 2.0, top_z - 50,
        FreeCAD.Vector(rod_x, rod_y, 50), FreeCAD.Vector(0, 0, 1))
    obj = doc.addObject("Part::Feature", rname)
    obj.Shape = rod
    rod_count += 1

print(f"  {rod_count} pedal rods done")

# ── 7. ROCKER LEVERS ─────────────────────────────────────────────────────────
# 7 rocker levers at column top, each connecting a pedal rod to the first
# bell crank in its note chain. Visible in frame 0943 (animated bell crank).
# L-shaped lever that pivots to convert vertical pedal rod motion into
# horizontal linkage rod motion.

rocker_count = 0
for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
    rname = f"Rocker_{note}"
    if doc.getObject(rname):
        continue

    # Rocker sits at top of column, at the bass end
    angle = i * 2 * math.pi / 7
    rod_x = col_x + 15.0 * math.cos(angle)
    rod_y = 15.0 * math.sin(angle)

    bass_key = NOTE_GROUPS[note][0]
    rocker_z = strings[bass_key]['n']['z']

    # Vertical arm (connects to pedal rod)
    vert_arm = Part.makeBox(ROCKER_WIDTH, ROCKER_THICK, ROCKER_LEN,
        FreeCAD.Vector(rod_x - ROCKER_WIDTH/2, rod_y - ROCKER_THICK/2,
                       rocker_z - ROCKER_LEN))

    # Horizontal arm (connects to first bell crank linkage)
    horiz_arm = Part.makeBox(ROCKER_LEN, ROCKER_THICK, ROCKER_WIDTH,
        FreeCAD.Vector(rod_x, rod_y - ROCKER_THICK/2,
                       rocker_z - ROCKER_WIDTH/2))

    # Pivot boss
    pivot = Part.makeCylinder(ROCKER_WIDTH / 2.0 + 1, ROCKER_THICK,
        FreeCAD.Vector(rod_x, rod_y - ROCKER_THICK/2, rocker_z),
        FreeCAD.Vector(0, 1, 0))

    shape = vert_arm.fuse(horiz_arm).fuse(pivot)
    obj = doc.addObject("Part::Feature", rname)
    obj.Shape = shape
    rocker_count += 1

print(f"  {rocker_count} rocker levers done")

# ── SAVE ──────────────────────────────────────────────────────────────────────
doc.recompute()
doc.save()
print(f"Saved. Total objects: {len(doc.Objects)}")
