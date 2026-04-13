# Clements47 Part Inspection TODO

Parts added 2026-04-13 from ML Harps reference image analysis. All are placeholder geometry — correct topology/position but simplified shapes. Open in FreeCAD and compare against `images/` reference frames.

## Priority 1: Mechanically Critical (shape affects function)

- [ ] **Bell cranks** (Crank_C1..G7) — Currently rectangular arms + cylindrical boss. Reference (frame 0007) shows organic V-shaped compound cranks with curved profiles. Arm angles, lengths, and boss diameter affect toggle linkage geometry directly.
- [ ] **Coupling links** (NatLink_*/ShpLink_*) — Simple cylinder + disc clevises. Reference (frame 1209) shows machined parts with specific fork geometry. Length and pivot geometry affect dead-point position.
- [ ] **Disc rotation stops** (NatStop_*/ShpStop_*) — 4mm cubes at 60 deg. Actual stop angle and contact surface determine disc travel limit (~45 deg). Verify against reference frames 0943+.
- [ ] **Rocker levers** (Rocker_C..B) — Simple L-shape at column top. Reference (frame 0943) shows animated bell crank with specific arm ratio. Lever ratio sets pedal-to-disc force multiplication.

## Priority 2: Fit and Assembly (shape affects neighboring parts)

- [ ] **Bearings** (BrgF_*/BrgB_*) — Generic flanged sleeves. Reference (frame 0142) shows specific ball bearing housings (6008/6006/6905/6904 series). OD, width, and flange dimensions should match actual bearing specs from JSON `b` field.
- [ ] **Spindle nuts** (NatNut_*/ShpNut_*) — Cylindrical approximation of hex nuts. Should be hexagonal. Sharp disc nuts need LEFT-HAND thread indication.
- [ ] **Guide rails** (NatRailU/L, ShpRailU/L) — Follow pin line with Y offset. Reference (frame 0134) shows them curving with the neck between action plates, with bracket mounts. Need to verify path and add mounting brackets.
- [ ] **Action plates** (FrontPlate/BackPlate) — Flat rectangles with bearing holes. Reference (frames 0360, 0429) shows contoured plates following the neck curve, with mounting features and cutouts.
- [ ] **Tuning pins** (Pin_C1..G7) — Plain cylinders. Real tuning pins have a tapered tip, a squared drive end, and thread for the string wrap.

## Priority 3: Structural (shape affects appearance)

- [ ] **Column** (Column) — Plain hollow cylinder at x=-50. Real column (visible throughout as dark striped element) is tapered, possibly fluted, and connects to both base and neck with specific joint geometry.
- [ ] **Pedal assembly** (Pedal_*/NotchPlate_*/PedalSpring_*) — Very schematic. Real pedals (reference frames 0943-1118) have forged lever arms, proper spring housings, and cast zigzag notch plates. Standard order D C B | E F G A needs verification.
- [ ] **Soundboard** (Soundboard) — Flat 100mm-wide rectangle at z=0. Should follow limacon profile width (wider at bass, narrower at treble). Thickness taper typical of spruce soundboards. **Blocked by soundbox alignment decision (Option A vs B).**
- [ ] **Grommets** (Grommet_C1..G7) — Simple annular rings. Real grommets have a flanged collar and may be recessed into the soundboard.

## Priority 4: Springs (cosmetic for static model)

- [ ] **Pedal springs** (PedalSpring_*) — Hollow cylinders. Should be helical coil geometry if visual fidelity matters.
- [ ] **Return springs** (ReturnSpring_*) — Hollow cylinders at rocker pivots. Should be torsion spring geometry.

## Still Unresolved

- [ ] **Soundbox alignment** — Option A (straight along X in mm) vs Option B (smooth curve centerline). Blocks soundboard, grommet, and string endpoint corrections. Choose before refining any z=0 parts.
- [ ] **Linkage rod cross-sections** — Buckwell patent notes tension vs compression links have DIFFERENT cross-sections. Currently all 3mm round.
- [ ] **Treble disc prong count** — Camac manual says F7-F0 have only 1 prong (space constraint). Currently all discs have 2 prongs.
