"""Add bell cranks, linkage rods, and action plates to Clements47.FCStd.

Extends the mechanism beyond discs/axles/prongs (add_mechanism.py) to include
the toggle linkage chain connecting same-note strings across octaves.

Reference: mechanism_references.md, Buckwell US1332885A, Camac/Salvi manuals.

Run:  echo 'exec(open("add_linkage.py").read())' | ~/.local/bin/freecad -c
"""
import json, math
import FreeCAD, Part

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

# Crank arm dimensions (compound bell crank)
CRANK_THICK  = 5.0     # mm plate thickness
CRANK_WIDTH  = 8.0     # mm arm width
NAT_ARM_LEN  = 20.0    # mm natural chain arm length (from axle center)
SHP_ARM_LEN  = 18.0    # mm sharp chain arm length (90 deg from natural)
CRANK_BORE   = 1.0     # mm clearance beyond axle radius for bore
PIN_HOLE_R   = 1.75    # mm linkage pin hole radius (M3 clevis pin)
BOSS_LEN     = 6.0     # mm boss length along axle

# Linkage rod dimensions
ROD_DIA      = 3.0     # mm rod diameter
ROD_CLEAR    = 2.0     # mm clearance at each end (pin engagement)

# Action plate dimensions
PLATE_THICK  = 3.0     # mm brass plate thickness
PLATE_MARGIN = 15.0    # mm beyond outermost string in X

# Disc rotation angle
DISC_ROT_DEG = 45.0    # degrees CW for natural engagement

# Note grouping: which strings belong to each of the 7 notes
NOTE_GROUPS = {
    'C': ['c1','c2','c3','c4','c5','c6','c7'],
    'D': ['d1','d2','d3','d4','d5','d6','d7'],
    'E': ['e1','e2','e3','e4','e5','e6','e7'],
    'F': ['f1','f2','f3','f4','f5','f6','f7'],
    'G': ['g1','g2','g3','g4','g5','g6','g7'],
    'A': ['a1','a2','a3','a4','a5','a6'],
    'B': ['b1','b2','b3','b4','b5','b6'],
}

PROJECT = '/home/james.clements/projects/clements47'

with open(f'{PROJECT}/clements47.json') as f:
    data = json.load(f)

doc = FreeCAD.open(f'{PROJECT}/Clements47.FCStd')

strings = {k: v for k, v in data['st'].items() if isinstance(v, dict) and 'sn' in v}
axles = data['as']
neck = data['nk']

print("Adding linkage components...")

# ── HELPER: compute crank arm pivot position ──────────────────────────────────

def get_crank_pivot(key):
    """Return (x, y, z, axle_radius, side) for the crank arm pivot on this axle.

    The crank arm sits at the far end of the axle (away from the discs).
    L-side axles: crank at y = -44mm end
    R-side axles: crank at y = +44mm end
    """
    s = strings[key]
    a = axles[key]
    ox = s['o']['x']
    nz = s['n']['z']
    side = a['sd']
    ar = a['ad'] / 2.0
    al = a['al']  # 44mm

    if side == 'L':
        # Axle extends from y=-44 to y=0; discs near y=0; crank at y=-44
        crank_y = -al
    else:
        # Axle extends from y=0 to y=+44; discs near y=0; crank at y=+44
        crank_y = al

    return ox, crank_y, nz, ar, side


# ── 1. CRANK ARMS (compound bell cranks) ──────────────────────────────────────
# Each axle gets a compound bell crank with two arms at ~90 degrees:
#   - Natural arm: extends in +Z direction (upward from axle)
#   - Sharp arm: extends in +X direction (toward treble)
# The arms have pin holes at their tips for linkage rod connections.

crank_count = 0
for key in sorted(strings.keys(), key=lambda k: strings[k]['sn']):
    name = f"Crank_{key.upper()}"
    if doc.getObject(name):
        continue

    ox, cy, nz, ar, side = get_crank_pivot(key)

    # Boss: cylinder around the axle end
    boss_r = ar + CRANK_BORE + 2.0  # outer radius of boss

    # Crank Y position: center the crank plate at the axle end
    if side == 'L':
        crank_base_y = cy  # y = -44
        crank_dir_y = -1   # extends further in -Y
    else:
        crank_base_y = cy - CRANK_THICK  # just inside the axle end
        crank_dir_y = 1

    # Build crank as a compound of boss + natural arm + sharp arm
    # All geometry in XZ plane at the crank Y position

    # Boss: short cylinder concentric with axle
    boss = Part.makeCylinder(boss_r, CRANK_THICK,
        FreeCAD.Vector(ox, crank_base_y, nz), FreeCAD.Vector(0, 1, 0))

    # Bore: remove axle hole from boss
    bore = Part.makeCylinder(ar + CRANK_BORE, CRANK_THICK + 0.1,
        FreeCAD.Vector(ox, crank_base_y - 0.05, nz), FreeCAD.Vector(0, 1, 0))

    # Natural arm: extends in +Z from boss edge
    nat_arm = Part.makeBox(CRANK_WIDTH, CRANK_THICK, NAT_ARM_LEN,
        FreeCAD.Vector(ox - CRANK_WIDTH/2, crank_base_y, nz + boss_r))

    # Sharp arm: extends in +X (toward treble) from boss edge
    shp_arm = Part.makeBox(SHP_ARM_LEN, CRANK_THICK, CRANK_WIDTH,
        FreeCAD.Vector(ox + boss_r, crank_base_y, nz - CRANK_WIDTH/2))

    # Pin holes at arm tips (remove material for clevis pin)
    nat_pin_z = nz + boss_r + NAT_ARM_LEN - PIN_HOLE_R - 2.0
    nat_pin = Part.makeCylinder(PIN_HOLE_R, CRANK_THICK + 0.2,
        FreeCAD.Vector(ox, crank_base_y - 0.1, nat_pin_z), FreeCAD.Vector(0, 1, 0))

    shp_pin_x = ox + boss_r + SHP_ARM_LEN - PIN_HOLE_R - 2.0
    shp_pin = Part.makeCylinder(PIN_HOLE_R, CRANK_THICK + 0.2,
        FreeCAD.Vector(shp_pin_x, crank_base_y - 0.1, nz), FreeCAD.Vector(0, 1, 0))

    # Fuse arms to boss, subtract bore and pin holes
    shape = boss.fuse(nat_arm).fuse(shp_arm)
    shape = shape.cut(bore).cut(nat_pin).cut(shp_pin)

    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    crank_count += 1

print(f"  {crank_count} crank arms done")

# ── 2. LINKAGE RODS (connect same-note cranks across octaves) ─────────────────
# For each note (C,D,E,F,G,A,B), connect adjacent octave cranks with rods.
# Natural chain: connects natural arm pin holes (+Z tips)
# Sharp chain: connects sharp arm pin holes (+X tips)

rod_count = 0
for note, keys in NOTE_GROUPS.items():
    # Sort by octave (bass to treble = low sn to high... actually sn counts
    # DOWN from 47 at bass to 1 at treble, so sort descending for bass-first)
    sorted_keys = sorted(keys, key=lambda k: -strings[k]['sn'])

    for i in range(len(sorted_keys) - 1):
        k1 = sorted_keys[i]
        k2 = sorted_keys[i + 1]

        ox1, cy1, nz1, ar1, side1 = get_crank_pivot(k1)
        ox2, cy2, nz2, ar2, side2 = get_crank_pivot(k2)

        boss_r1 = ar1 + CRANK_BORE + 2.0
        boss_r2 = ar2 + CRANK_BORE + 2.0

        # ── Natural chain rod: connects +Z arm tips ──
        nat_name = f"NatRod_{k1.upper()}_{k2.upper()}"
        if not doc.getObject(nat_name):
            # Pin hole center positions on natural arms
            p1_x = ox1
            p1_z = nz1 + boss_r1 + NAT_ARM_LEN - PIN_HOLE_R - 2.0
            p1_y = cy1 + CRANK_THICK / 2.0  # center of crank plate

            p2_x = ox2
            p2_z = nz2 + boss_r2 + NAT_ARM_LEN - PIN_HOLE_R - 2.0
            p2_y = cy2 + CRANK_THICK / 2.0

            # Average Y for the rod (cranks alternate L/R sides)
            rod_y = (p1_y + p2_y) / 2.0

            # Rod from p1 to p2
            v1 = FreeCAD.Vector(p1_x, rod_y, p1_z)
            v2 = FreeCAD.Vector(p2_x, rod_y, p2_z)
            direction = v2 - v1
            rod_len = direction.Length

            if rod_len > 1.0:  # sanity check
                rod = Part.makeCylinder(ROD_DIA / 2.0, rod_len,
                    v1, direction)
                obj = doc.addObject("Part::Feature", nat_name)
                obj.Shape = rod
                rod_count += 1

        # ── Sharp chain rod: connects +X arm tips ──
        shp_name = f"ShpRod_{k1.upper()}_{k2.upper()}"
        if not doc.getObject(shp_name):
            p1_x = ox1 + boss_r1 + SHP_ARM_LEN - PIN_HOLE_R - 2.0
            p1_z = nz1
            p1_y = cy1 + CRANK_THICK / 2.0

            p2_x = ox2 + boss_r2 + SHP_ARM_LEN - PIN_HOLE_R - 2.0
            p2_z = nz2
            p2_y = cy2 + CRANK_THICK / 2.0

            rod_y = (p1_y + p2_y) / 2.0

            v1 = FreeCAD.Vector(p1_x, rod_y, p1_z)
            v2 = FreeCAD.Vector(p2_x, rod_y, p2_z)
            direction = v2 - v1
            rod_len = direction.Length

            if rod_len > 1.0:
                rod = Part.makeCylinder(ROD_DIA / 2.0, rod_len,
                    v1, direction)
                obj = doc.addObject("Part::Feature", shp_name)
                obj.Shape = rod
                rod_count += 1

print(f"  {rod_count} linkage rods done")

# ── 3. ACTION PLATES (front and back brass plates) ────────────────────────────
# Two brass plates span the full neck length, holding spindle bearings.
# Front plate: audience side (+Y), holds spindle conical bearing ends
# Back plate: harpist side (-Y), holds spindle screw cup bearings

# Get X extent from bass to treble strings
all_x = [strings[k]['o']['x'] for k in strings]
min_x = min(all_x) - PLATE_MARGIN
max_x = max(all_x) + PLATE_MARGIN
plate_len = max_x - min_x

# Get Z extent from lowest to highest pin
all_z = [strings[k]['n']['z'] for k in strings]
min_z = min(all_z) - PLATE_MARGIN
max_z = max(all_z) + PLATE_MARGIN
plate_height = max_z - min_z

# Plate Y positions: just outside the axle ends
# L-side axles end at y=-44, R-side at y=+44
AXLE_LEN = 44.0
front_y = AXLE_LEN + 2.0        # front plate at y=+46
back_y  = -AXLE_LEN - 2.0 - PLATE_THICK  # back plate at y=-49

for plate_name, py in [("FrontPlate", front_y), ("BackPlate", back_y)]:
    if doc.getObject(plate_name):
        continue
    plate = Part.makeBox(plate_len, PLATE_THICK, plate_height,
        FreeCAD.Vector(min_x, py, min_z))

    # Drill bearing holes for each axle
    for key in strings:
        a = axles[key]
        s = strings[key]
        ox = s['o']['x']
        nz = s['n']['z']
        ar = a['ad'] / 2.0
        hole_r = ar + 0.5  # bearing seat clearance

        hole = Part.makeCylinder(hole_r, PLATE_THICK + 0.2,
            FreeCAD.Vector(ox, py - 0.1, nz), FreeCAD.Vector(0, 1, 0))
        plate = plate.cut(hole)

    obj = doc.addObject("Part::Feature", plate_name)
    obj.Shape = plate

print("  action plates done")

# ── SAVE ──────────────────────────────────────────────────────────────────────
doc.recompute()
doc.save()
print(f"Saved. Total objects: {len(doc.Objects)}")
