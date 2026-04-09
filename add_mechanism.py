"""Add mechanism components (strings, axles, discs, prongs, neck) to Clements47."""
import json, math
import FreeCAD, Part

# Constants
DISC_THICK = 2.0       # mm
PRONG_DIA  = 3.0       # mm (M3)
PRONG_EXT  = 12.7      # mm extension from disc surface
NECK_WALL  = 10.0      # mm

PROJECT = '/home/james.clements/projects/clements47'

with open(f'{PROJECT}/clements47.json') as f:
    data = json.load(f)

doc = FreeCAD.open(f'{PROJECT}/Clements47.FCStd')

# Extract string entries (skip non-dict metadata keys)
strings = {k: v for k, v in data['st'].items() if isinstance(v, dict) and 'sn' in v}
axles = data['as']
neck = data['nk']

# Ordered by string number for consistent processing
ordered = sorted(strings.items(), key=lambda kv: kv[1]['sn'])

print(f"Adding {len(ordered)} strings with discs and axles...")

# ── 1. STRINGS ──────────────────────────────────────────────────────────────
for key, s in ordered:
    sn = s['sn']
    name = f"Str_{key.upper()}"
    if doc.getObject(name):
        continue
    r = s['d'] / 2.0
    h = s['n']['z']  # string length (pin Z, grommet at z=0)
    ox = s['o']['x']
    cyl = Part.makeCylinder(r, h, FreeCAD.Vector(ox, 0, 0), FreeCAD.Vector(0, 0, 1))
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = cyl

print("  strings done")

# ── 2. AXLES + 3. DISCS + 4. PRONGS ────────────────────────────────────────
for key, s in ordered:
    sn = s['sn']
    a = axles[key]
    ox = s['o']['x']
    nz = s['n']['z']       # pin height = axle Z
    dr = s['dr']            # disc radius
    side = a['sd']          # 'L' or 'R'
    ad = a['ad'] / 2.0      # axle radius
    al = a['al']            # axle length = 44mm

    # Axle: extends along Y from string plane
    # L side extends toward harpist (-Y), R side toward audience (+Y)
    if side == 'L':
        axle_start_y = -al
    else:
        axle_start_y = 0.0

    cyl = Part.makeCylinder(ad, al,
        FreeCAD.Vector(ox, axle_start_y, nz), FreeCAD.Vector(0, 1, 0))
    obj = doc.addObject("Part::Feature", f"Axle_{key.upper()}")
    obj.Shape = cyl

    # Sign: disc positions along Y from the string plane (y=0)
    sign = -1.0 if side == 'L' else 1.0

    # Natural and sharp discs
    for disc_pos_mm, prefix in [(a['np'], 'NatDisc'), (a['sp'], 'ShpDisc')]:
        # Disc center Y along axle
        disc_center_y = sign * disc_pos_mm
        disc_base_y = disc_center_y - sign * (DISC_THICK / 2.0)

        # Disc is a thin cylinder in XZ plane, face normal along Y
        dcyl = Part.makeCylinder(dr, DISC_THICK,
            FreeCAD.Vector(ox, disc_base_y, nz), FreeCAD.Vector(0, 1, 0))
        dobj = doc.addObject("Part::Feature", f"{prefix}_{key.upper()}")
        dobj.Shape = dcyl

        # Prongs: 2 per disc, 180 deg apart at 12/6 o'clock (+Z / -Z)
        # Prong center is (dr + prong_radius) from disc center
        pr = PRONG_DIA / 2.0
        prong_offset = dr + pr  # distance from disc axis to prong axis

        # Prong extends from disc face TOWARD the string (toward y=0)
        if side == 'L':
            # Disc is at negative Y, prong extends in +Y toward y=0
            prong_base_y = disc_center_y + DISC_THICK / 2.0
            prong_dir = FreeCAD.Vector(0, 1, 0)
        else:
            # Disc is at positive Y, prong extends in -Y toward y=0
            # makeCylinder needs positive height, so offset base
            prong_base_y = disc_center_y - DISC_THICK / 2.0 - PRONG_EXT
            prong_dir = FreeCAD.Vector(0, 1, 0)

        for z_sign, suffix in [(1, 'U'), (-1, 'D')]:
            prong_z = nz + z_sign * prong_offset
            pcyl = Part.makeCylinder(pr, PRONG_EXT,
                FreeCAD.Vector(ox, prong_base_y, prong_z), prong_dir)
            tag = 'Nat' if prefix.startswith('Nat') else 'Shp'
            pobj = doc.addObject("Part::Feature", f"{tag}Pr{suffix}_{key.upper()}")
            pobj.Shape = pcyl

print("  axles, discs, prongs done")

# ── 5. NECK ─────────────────────────────────────────────────────────────────
# Hollow box beam from bass (x=0) to treble (x~720), tilted to follow pin line
# Bass pin: C1 at z=1429.9, Treble pin: G7 at z=57.2
# Neck centered on Y, box dimensions: 720 x 200 x 250

bass_x = 0.0
bass_z = strings['c1']['n']['z']   # 1429.9
treb_x = strings['g7']['o']['x']   # 717.4
treb_z = strings['g7']['n']['z']   # 57.2

neck_len = neck['l']   # 720
neck_w = neck['iw']    # 200 internal width
neck_h = neck['ih']    # 250 internal height

# Tilt angle (rotation around Y axis, negative = treble end goes down)
dx = treb_x - bass_x
dz = treb_z - bass_z
angle_rad = math.atan2(dz, dx)
angle_deg = math.degrees(angle_rad)

# Outer box: create at origin, centered on Y
outer = Part.makeBox(neck_len, neck_w, neck_h,
    FreeCAD.Vector(0, -neck_w / 2.0, 0))
inner = Part.makeBox(neck_len - 2 * NECK_WALL,
                     neck_w - 2 * NECK_WALL,
                     neck_h - 2 * NECK_WALL,
    FreeCAD.Vector(NECK_WALL, -neck_w / 2.0 + NECK_WALL, NECK_WALL))
neck_shape = outer.cut(inner)

neck_obj = doc.addObject("Part::Feature", "Neck")
neck_obj.Shape = neck_shape

# Position: bass end bottom-center at (bass_x, 0, bass_z)
# The box was built with corner at (0, -100, 0), so bottom-center is at (0, 0, 0)
# We want the bottom of the neck to sit slightly above the pin line (pins inside neck)
# Offset: put bottom at pin_z - some margin so pins are inside
neck_z_offset = -50  # pins sit 50mm above neck bottom (inside the neck)

rot = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), angle_deg)
neck_obj.Placement = FreeCAD.Placement(
    FreeCAD.Vector(bass_x, 0, bass_z + neck_z_offset),
    rot,
    FreeCAD.Vector(0, 0, 0)  # rotate around bass end corner
)

print("  neck done")

# ── SAVE ────────────────────────────────────────────────────────────────────
doc.recompute()
doc.save()
print(f"Saved. Total objects: {len(doc.Objects)}")
