"""Add remaining mechanism parts to Clements47.FCStd.

Parts added:
1. Coupling links — short rods connecting rockers to first bell crank in each chain
2. Pedal assembly — 7 pedals with springs and zigzag notch plates
3. Soundboard — flat panel at z=0 spanning string extent
4. String grommets/eyelets — at soundboard where strings pass through
5. Disc rotation stops — small blocks limiting disc travel to ~45 deg
6. Return springs — coil springs at each rocker lever

Run:  echo 'exec(open("add_remaining_parts.py").read())' | ./squashfs-root/usr/bin/freecadcmd
"""
import json, math
import FreeCAD, Part

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

# Coupling links (connect rocker tip to first bell crank's natural arm pin)
LINK_DIA         = 3.0     # mm rod diameter
LINK_CLEVIS_R    = 4.0     # mm clevis end radius
LINK_CLEVIS_T    = 3.0     # mm clevis thickness
LINK_PIN_R       = 1.75    # mm clevis pin hole radius

# Pedal assembly
PEDAL_WIDTH      = 25.0    # mm pedal plate width
PEDAL_LENGTH     = 120.0   # mm pedal plate length (foot surface)
PEDAL_THICK      = 5.0     # mm pedal plate thickness
PEDAL_ARM_LEN    = 80.0    # mm lever arm from pivot to rod attachment
PEDAL_ARM_W      = 15.0    # mm arm width
PEDAL_ARM_T      = 5.0     # mm arm thickness
PEDAL_PIVOT_R    = 6.0     # mm pivot boss radius
PEDAL_PIVOT_L    = 30.0    # mm pivot boss length (axle span)
PEDAL_BASE_Z     = 0.0     # mm floor level
PEDAL_SPACING    = 40.0    # mm between pedal centers

# Notch plate (zigzag plate with 3 detent positions)
NOTCH_PLATE_H    = 60.0    # mm height
NOTCH_PLATE_W    = 20.0    # mm width
NOTCH_PLATE_T    = 3.0     # mm thickness
NOTCH_DEPTH      = 5.0     # mm depth of each zigzag notch
NOTCH_SPACING    = 20.0    # mm between notch centers (3 notches)

# Pedal spring
SPRING_OD        = 10.0    # mm outer diameter
SPRING_WIRE_D    = 1.5     # mm wire diameter
SPRING_LENGTH    = 40.0    # mm free length
SPRING_COILS     = 8       # number of active coils

# Soundboard
SB_THICK         = 4.0     # mm spruce soundboard thickness
SB_MARGIN        = 20.0    # mm beyond outermost strings

# Grommets
GROMMET_OD       = 6.0     # mm outer diameter
GROMMET_ID       = 2.5     # mm inner diameter (string clearance)
GROMMET_THICK    = 3.0     # mm

# Disc rotation stops
STOP_SIZE        = 4.0     # mm cube side
STOP_OFFSET      = 2.0     # mm gap between stop and disc edge

# Return springs (torsion springs at rocker pivots)
RSPRING_OD       = 8.0     # mm coil outer diameter
RSPRING_WIRE     = 1.0     # mm wire diameter
RSPRING_LEN      = 10.0    # mm axial length

# Shared constants (from other scripts)
AXLE_LEN         = 44.0
CRANK_BORE       = 1.0
NAT_ARM_LEN      = 20.0
SHP_ARM_LEN      = 18.0
CRANK_THICK      = 5.0
PIN_HOLE_R       = 1.75
COL_X            = -50.0   # column center X

NOTE_GROUPS = {
    'C': ['c1','c2','c3','c4','c5','c6','c7'],
    'D': ['d1','d2','d3','d4','d5','d6','d7'],
    'E': ['e1','e2','e3','e4','e5','e6','e7'],
    'F': ['f1','f2','f3','f4','f5','f6','f7'],
    'G': ['g1','g2','g3','g4','g5','g6','g7'],
    'A': ['a1','a2','a3','a4','a5','a6'],
    'B': ['b1','b2','b3','b4','b5','b6'],
}

import os
PROJECT = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '/home/clementsj/projects/clements47'

with open(f'{PROJECT}/clements47.json') as f:
    data = json.load(f)

doc = FreeCAD.open(f'{PROJECT}/Clements47.FCStd')

strings = {k: v for k, v in data['st'].items() if isinstance(v, dict) and 'sn' in v}
axles = data['as']

ordered = sorted(strings.items(), key=lambda kv: kv[1]['sn'])

print("Adding remaining mechanism parts...")

# ── 1. COUPLING LINKS ────────────────────────────────────────────────────────
# Short rods connecting each rocker lever tip to the first (bass) bell crank
# in its note chain. Each link has clevis ends with pin holes.
# 7 natural links + 7 sharp links = 14 total.

link_count = 0
for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
    # Rocker position (from add_missing_parts.py)
    angle = i * 2 * math.pi / 7
    rocker_x = COL_X + 15.0 * math.cos(angle)
    rocker_y = 15.0 * math.sin(angle)

    bass_key = NOTE_GROUPS[note][0]  # first (bass) string in chain
    s = strings[bass_key]
    a = axles[bass_key]
    ox = s['o']['x']
    nz = s['n']['z']
    ar = a['ad'] / 2.0
    side = a['sd']
    boss_r = ar + CRANK_BORE + 2.0

    if side == 'L':
        crank_y = -AXLE_LEN
    else:
        crank_y = AXLE_LEN

    # Natural coupling link: rocker tip -> bass crank natural arm pin hole
    nat_pin_z = nz + boss_r + NAT_ARM_LEN - PIN_HOLE_R - 2.0
    nat_pin_y = crank_y + CRANK_THICK / 2.0

    for chain, target_x, target_y, target_z in [
        ("Nat", ox, nat_pin_y, nat_pin_z),
        ("Shp", ox + boss_r + SHP_ARM_LEN - PIN_HOLE_R - 2.0, nat_pin_y, nz),
    ]:
        lname = f"{chain}Link_{note}"
        if doc.getObject(lname):
            continue

        # Link from rocker tip to crank pin
        p1 = FreeCAD.Vector(rocker_x + 30.0, rocker_y, nz)  # rocker horiz arm tip
        p2 = FreeCAD.Vector(target_x, target_y, target_z)
        direction = p2 - p1
        rod_len = direction.Length

        if rod_len < 1.0:
            continue

        # Rod body
        rod = Part.makeCylinder(LINK_DIA / 2.0, rod_len, p1, direction)

        # Clevis ends (small cylinders perpendicular to rod at each end)
        clevis1 = Part.makeCylinder(LINK_CLEVIS_R, LINK_CLEVIS_T,
            FreeCAD.Vector(p1.x, p1.y - LINK_CLEVIS_T/2, p1.z),
            FreeCAD.Vector(0, 1, 0))
        clevis2 = Part.makeCylinder(LINK_CLEVIS_R, LINK_CLEVIS_T,
            FreeCAD.Vector(p2.x, p2.y - LINK_CLEVIS_T/2, p2.z),
            FreeCAD.Vector(0, 1, 0))

        # Pin holes in clevises
        hole1 = Part.makeCylinder(LINK_PIN_R, LINK_CLEVIS_T + 0.2,
            FreeCAD.Vector(p1.x, p1.y - LINK_CLEVIS_T/2 - 0.1, p1.z),
            FreeCAD.Vector(0, 1, 0))
        hole2 = Part.makeCylinder(LINK_PIN_R, LINK_CLEVIS_T + 0.2,
            FreeCAD.Vector(p2.x, p2.y - LINK_CLEVIS_T/2 - 0.1, p2.z),
            FreeCAD.Vector(0, 1, 0))

        shape = rod.fuse(clevis1).fuse(clevis2).cut(hole1).cut(hole2)
        obj = doc.addObject("Part::Feature", lname)
        obj.Shape = shape
        link_count += 1

print(f"  {link_count} coupling links done")

# ── 2. PEDAL ASSEMBLY ────────────────────────────────────────────────────────
# 7 pedals arranged side by side at the base of the column.
# Each pedal: foot plate + lever arm + pivot boss + notch plate + spring.
# Standard order: D C B | E F G A (from left to right, harpist's view)

PEDAL_ORDER = ['D', 'C', 'B', 'E', 'F', 'G', 'A']
pedal_base_x = COL_X  # centered under column
pedal_base_y_start = -(len(PEDAL_ORDER) * PEDAL_SPACING) / 2.0

pedal_count = 0
for idx, note in enumerate(PEDAL_ORDER):
    # ── Pedal plate (foot surface) ──
    pname = f"Pedal_{note}"
    if doc.getObject(pname):
        continue

    py = pedal_base_y_start + idx * PEDAL_SPACING

    # Foot plate: horizontal, at floor level, extending forward (-X from column)
    foot = Part.makeBox(PEDAL_LENGTH, PEDAL_WIDTH, PEDAL_THICK,
        FreeCAD.Vector(pedal_base_x - PEDAL_LENGTH, py - PEDAL_WIDTH/2, PEDAL_BASE_Z))

    # Lever arm: extends upward from pivot to pedal rod attachment
    arm = Part.makeBox(PEDAL_ARM_W, PEDAL_ARM_T, PEDAL_ARM_LEN,
        FreeCAD.Vector(pedal_base_x - PEDAL_ARM_W/2, py - PEDAL_ARM_T/2,
                       PEDAL_BASE_Z + PEDAL_THICK))

    # Pivot boss: horizontal cylinder at pedal hinge point
    pivot = Part.makeCylinder(PEDAL_PIVOT_R, PEDAL_PIVOT_L,
        FreeCAD.Vector(pedal_base_x, py - PEDAL_PIVOT_L/2, PEDAL_BASE_Z + PEDAL_THICK),
        FreeCAD.Vector(0, 1, 0))

    shape = foot.fuse(arm).fuse(pivot)
    obj = doc.addObject("Part::Feature", pname)
    obj.Shape = shape
    pedal_count += 1

    # ── Notch plate (zigzag detent, 3 positions) ──
    npname = f"NotchPlate_{note}"
    if not doc.getObject(npname):
        # Plate sits beside the pedal arm, with 3 notches cut into it
        plate = Part.makeBox(NOTCH_PLATE_T, NOTCH_PLATE_W, NOTCH_PLATE_H,
            FreeCAD.Vector(pedal_base_x + PEDAL_ARM_W/2 + 2,
                           py - NOTCH_PLATE_W/2,
                           PEDAL_BASE_Z + PEDAL_THICK))

        # Cut 3 notches (flat, natural, sharp positions)
        for ni in range(3):
            notch_z = PEDAL_BASE_Z + PEDAL_THICK + 10 + ni * NOTCH_SPACING
            notch = Part.makeBox(NOTCH_DEPTH, NOTCH_PLATE_W + 0.2, 8,
                FreeCAD.Vector(pedal_base_x + PEDAL_ARM_W/2 + 2 - NOTCH_DEPTH + NOTCH_PLATE_T,
                               py - NOTCH_PLATE_W/2 - 0.1,
                               notch_z))
            plate = plate.cut(notch)

        obj = doc.addObject("Part::Feature", npname)
        obj.Shape = plate

    # ── Pedal spring ──
    spname = f"PedalSpring_{note}"
    if not doc.getObject(spname):
        # Approximate coil spring as a series of torus segments
        # For simplicity: cylinder representing the spring envelope
        spring = Part.makeCylinder(SPRING_OD / 2.0, SPRING_LENGTH,
            FreeCAD.Vector(pedal_base_x - PEDAL_ARM_W, py, PEDAL_BASE_Z + PEDAL_THICK + 5),
            FreeCAD.Vector(0, 0, 1))
        # Hollow it out to suggest coil
        inner = Part.makeCylinder(SPRING_OD / 2.0 - SPRING_WIRE_D, SPRING_LENGTH + 0.2,
            FreeCAD.Vector(pedal_base_x - PEDAL_ARM_W, py,
                           PEDAL_BASE_Z + PEDAL_THICK + 5 - 0.1),
            FreeCAD.Vector(0, 0, 1))
        shape = spring.cut(inner)
        obj = doc.addObject("Part::Feature", spname)
        obj.Shape = shape

print(f"  {pedal_count} pedals (with notch plates and springs) done")

# ── 3. SOUNDBOARD ────────────────────────────────────────────────────────────
# Flat spruce panel at z=0 where strings emerge. Spans full string extent.

sb_name = "Soundboard"
if not doc.getObject(sb_name):
    all_x = [s['o']['x'] for _, s in ordered]
    min_x = min(all_x) - SB_MARGIN
    max_x = max(all_x) + SB_MARGIN
    sb_len = max_x - min_x

    # Soundboard width in Y: extends from harpist side to audience side
    # Typical concert harp soundboard: ~100mm wide at bass, ~40mm at treble
    # Simplified as a flat rectangle for now
    sb_width = 100.0  # mm

    sb = Part.makeBox(sb_len, sb_width, SB_THICK,
        FreeCAD.Vector(min_x, -sb_width/2, -SB_THICK))

    obj = doc.addObject("Part::Feature", sb_name)
    obj.Shape = sb
    print("  soundboard done")
else:
    print("  soundboard exists")

# ── 4. STRING GROMMETS ───────────────────────────────────────────────────────
# Brass eyelets at z=0 where each string passes through the soundboard.

grommet_count = 0
for key, s in ordered:
    gname = f"Grommet_{key.upper()}"
    if doc.getObject(gname):
        continue

    ox = s['o']['x']
    sr = s['d'] / 2.0  # string radius

    # Grommet: annular ring at z=0
    outer = Part.makeCylinder(GROMMET_OD / 2.0, GROMMET_THICK,
        FreeCAD.Vector(ox, 0, -GROMMET_THICK / 2.0), FreeCAD.Vector(0, 0, 1))
    inner = Part.makeCylinder(GROMMET_ID / 2.0, GROMMET_THICK + 0.2,
        FreeCAD.Vector(ox, 0, -GROMMET_THICK / 2.0 - 0.1), FreeCAD.Vector(0, 0, 1))

    shape = outer.cut(inner)
    obj = doc.addObject("Part::Feature", gname)
    obj.Shape = shape
    grommet_count += 1

print(f"  {grommet_count} grommets done")

# ── 5. DISC ROTATION STOPS ──────────────────────────────────────────────────
# Small steel blocks on the action plate limiting disc rotation to ~45 degrees.
# Two per axle: one natural stop, one sharp stop.
# Positioned at 45 deg CW from the disc rest position (9 o'clock = rest).

stop_count = 0
for key, s in ordered:
    a = axles[key]
    ox = s['o']['x']
    nz = s['n']['z']
    dr = s['dr']  # disc radius
    side = a['sd']
    sign = -1.0 if side == 'L' else 1.0

    for prefix, disc_pos in [('NatStop', a['np']), ('ShpStop', a['sp'])]:
        sname = f"{prefix}_{key.upper()}"
        if doc.getObject(sname):
            continue

        # Stop block positioned at ~45 deg from rest (12 o'clock = engaged)
        # Rest position is 9 o'clock (prongs at 3 and 9)
        # Stop at ~1 o'clock position to limit overtravel
        stop_angle = math.radians(60)  # 60 deg from +X axis (~ 1 o'clock)
        stop_x = ox + (dr + STOP_OFFSET + STOP_SIZE/2) * math.cos(stop_angle)
        stop_z = nz + (dr + STOP_OFFSET + STOP_SIZE/2) * math.sin(stop_angle)

        disc_center_y = sign * disc_pos
        stop_y = disc_center_y

        block = Part.makeBox(STOP_SIZE, STOP_SIZE, STOP_SIZE,
            FreeCAD.Vector(stop_x - STOP_SIZE/2, stop_y - STOP_SIZE/2,
                           stop_z - STOP_SIZE/2))

        obj = doc.addObject("Part::Feature", sname)
        obj.Shape = block
        stop_count += 1

print(f"  {stop_count} rotation stops done")

# ── 6. RETURN SPRINGS ────────────────────────────────────────────────────────
# Torsion springs at each rocker lever pivot, providing return force.
# Modeled as hollow cylinders (spring envelope) at rocker pivot locations.

spring_count = 0
for i, note in enumerate(['C', 'D', 'E', 'F', 'G', 'A', 'B']):
    rsname = f"ReturnSpring_{note}"
    if doc.getObject(rsname):
        continue

    angle = i * 2 * math.pi / 7
    rx = COL_X + 15.0 * math.cos(angle)
    ry = 15.0 * math.sin(angle)

    bass_key = NOTE_GROUPS[note][0]
    rz = strings[bass_key]['n']['z']

    # Spring coil around the rocker pivot axis (Y-axis)
    outer = Part.makeCylinder(RSPRING_OD / 2.0, RSPRING_LEN,
        FreeCAD.Vector(rx, ry - RSPRING_LEN/2, rz), FreeCAD.Vector(0, 1, 0))
    inner = Part.makeCylinder(RSPRING_OD / 2.0 - RSPRING_WIRE, RSPRING_LEN + 0.2,
        FreeCAD.Vector(rx, ry - RSPRING_LEN/2 - 0.1, rz), FreeCAD.Vector(0, 1, 0))

    shape = outer.cut(inner)
    obj = doc.addObject("Part::Feature", rsname)
    obj.Shape = shape
    spring_count += 1

print(f"  {spring_count} return springs done")

# ── SAVE ──────────────────────────────────────────────────────────────────────
doc.recompute()
doc.save()
print(f"Saved. Total objects: {len(doc.Objects)}")
