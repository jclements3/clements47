# clements47 — 47-string concert pedal harp design

## Current state (end of session 2026-04-27)

Single source of truth: `clements47.py`. Reads `strings.csv` for string physics
(note, OD, lengths, frequency). Computes all geometry and outputs SVG profile.

### Coordinate system
- +x across (treble side), +z up (toward neck), +y depth (away from player)
- Origin at the FLOOR (z=0). Strings rake 7° back from vertical.
- Z_OFFSET = 186.778715 mm: SBB sits at z=Z_OFFSET above the floor.

### Generate the SVG
```
python3 clements47.py -o harp_profile.svg
```

### Key design points

**Soundboard S Bezier (P0..P3)** — unshifted z values; +Z_OFFSET added in code:
- P0=SBB=(0, 0)
- P1=(371.81, 971.14)
- P2=(400.63, 1142.59)
- P3=G7g=(735.29, 1477.0)

**Air gap**: 15 mm. Buffer (clearance) radius: 8 mm.

**Floor segment** (magenta on z=0): from SF (-71.51, 0) to floor_end at
B_floor (466.95, 0). U_FLOOR_LEN=538.46, FLOOR_EXTENSION=0.

**Bass tail front**: SBB → SF Bezier with vertical incoming handle 30 mm at SF.

**SB extension**: G7g → K6 (SBN) Bezier.

### Neck knots (in shifted coords; floor at z=0)
9 knots, K_KNOTS:
- K1: (-50, 1786.78)        column LEFT top
- K2: (102.87, 1866.78)     top arc bass peak
- K3: (434.35, 1796.78)     S-knot
- K4: (735.29, 1753.04)     top arc treble end (touches F7 Nf top buffer)
- K5: (800.11, 1711.78)     U1 (BN)
- K6: (735.29, 1725.06)     SBN (touches G7 Ns bottom buffer)
- K7: (594.37, 1686.78)
- K8: (297.18, 1661.78)     collinear handles at angle (-0.9826, -0.1859) — touches A1 Ns buffer
- K9: (-50, 1506.78)        column LEFT bottom corner; 180° corner (in vertical-down, out vertical-up)

K2 has horizontal-right Catmull-Rom tangent. K1 has vertical-up out tangent.
K4↔K6 distance: 27.98mm (top lima\u00e7on diameter at K6).

K4-K5 segment removed (replaced by lima\u00e7on B-locus).
K5-K6 segment removed (combined neck+S+U into one path).

### Closed path traversal
K6 → K7 → K8 → K9 → K1 → K2 → K3 → K4 → [B-locus] → floor_end → floor → SF → bass_tail_front → SBB → S Bezier → G7g → SB extension → K6.

### Lima\u00e7on series (orange)
- D rides S from SBB up to K6 along sb_bezier + sb_extension (skips bass tail
  to avoid B-locus dipping inward).
- Axis perpendicular to S at each station, B endpoints in chamber side.
- Diameter gradient: linear from base_diam=500 mm (at SBB) to top_diam=K4-K6
  distance (~28 mm) at K6.
- Limaçon r(θ) = a + b·cos(θ), a = 2b (boundary case), D-to-B distance = 4b.
- Floor lima\u00e7on (special): lies flat on floor, D=SF, B=B_floor=(466.95, 0).
  D-B distance 538.46 mm. Drawn as orange line on z=0.

**B-locus (magenta)**: chamber outer wall, traced through all B endpoints
plus prepended floor_end at (466.95, 0).

### Column
- Polygon from CF_l (-50, 0), CF_r (-18, 0), up to K1 along K1-K2 arc.

### Outstanding clearance issues
At time of session end:
- F7 Nf at K3-K4: 4.77 mm (worst)
- E7 Nf at K3-K4: 7.53 mm
- E6 Ns at K6-K7: 7.74 mm
- F6 Ns at K6-K7: 7.62 mm

## Files in this archive
- `clements47.py` — single source of truth (reads strings.csv)
- `harp_profile.svg` — current output
- `strings.csv` — original string physics data
- `ai-tar.py`, `ai-untar.py` — archive tools

## Conventions for next session
- Terse responses, no explanatory prose
- Lead with geometry, dimensions, and numbers
- SVG only (no PNG)
- No clarifying questions when intent is clear
- Manufacturing details belong to the CF shop, not Claude

---

## Session handoff 2026-04-28 (work-laptop -> home-laptop)

### What changed this session

**Pedestal (side view)**
- 4-corner wedge `P0..P3` (CCW) bounded by two purple arcs sharing
  `ARC_CENTER` (intersection of `B0-B1` line extended and the floor line)
- Inner arc (right) from `P1` to `P2`, outer arc (left) from `P0` to `P3`
- Top edge `P3-P2` IS the bass-end limaçon (== `B0-B1`), shared with soundbox
- Floor `P0-P1` still drawn as a straight line (limaçon-cap conversion deferred)
- Two dashed radii: `ARC_CENTER -> P0` and `ARC_CENTER -> P3`
- Pedestal fill: light purple `#a000a0` @ 0.18 opacity, stroke `#a000a0`
- Scoop: white-filled parabolic void restored.  Added
  `CF_WALL_T = 5.0` mm constant (clements47.py); scoop's `rim_center_xz`
  shifted +x by CF_WALL_T so R1/R2 sit ~3.8 mm inside the outer arc
- Frustum (sound path from scoop to soundbox interior): white-filled
  R2-R1-P2-P3 quadrilateral plus the two side lines `R1->P2` and
  `R2->P3`.  Revolved about the scoop axis this is a truncated cone
  connecting the rim chord to the open `B0-B1` cap

**Soundbox**
- Renamed corners to `B0/B1/B2/B3` (CCW): bass-front, bass-back,
  treble-back, treble-front
- Replaced BTF Bezier on the front side with chamber AXIS samples from
  `B0` (s_at_Sprime_b) to `SBB`, then SB Bezier `SBB -> G7g`
- Back wall: stations between `s_at_Sprime_b` and `s_at_St` only, with
  exact `B1` and `B2` bracketed in.  No more wiggle below B1.
- Body fill: `PAL["soundboard"]` @ 0.18 (light-green tint), border
  stroke = soundboard green.  Standalone SB Bezier line removed.
- `B2` snapped to `N6` exactly via `N_KNOTS[6] = (730.38796, 1622.07805)`
  (computed from chamber back wall at s_at_St; distance < 1e-9 mm)
- `B0=P3` and `B1=P2` exact (0 mm)
- `B3=N5` to 0.003 mm

**Column (NEW: curved blue band)**
- Old gray column polygon REMOVED.  Replaced by a blue
  (`#1060d0` @ 0.25 fill, `#1060d0` stroke) curved band between two
  parallel arcs of constant horizontal offset = `col_width`.
- Corners `C0/C1/C2/C3` (CCW from bottom-left): C0 and C1 on the
  P0-P1 floor; C2 = top-right (= old N1 = column inner top); C3 =
  top-left (= old N0 = column outer top).
- `clements47.py` updates:
  - `COL_X_LEFT = -15.75`  (was -43.74; now == old COL_X_RIGHT)
  - `COL_X_RIGHT = 12.24`  (was -15.75; +col_width = +27.99)
  - `N_KNOTS[0] = (-223.34, 1690.42)`  (column outer top, was -251.33)
  - `N_KNOTS[1] = (-195.35, 1690.42)`  (column inner top, was -223.34)
  - `N_KNOTS[2] = (-171.55, 1494.49)`  (column inner face, was -199.54)

**Neck path**
- Loaded from `edit_paths.svg` (hand-edited, primary source; computed
  fallback exists)
- Updated `M` to new N0 and the C-segment endpoint to `(730.38796,
  1622.07805)` (= B2 = N6)
- Updated `N2` endpoint of the neck to `(-182.95693, 1494.49)` ON
  the column inner arc (was at the linear-interpolation point off-arc)
- Adjusted relative N2->N1 handles to `-4.60441,65.27920
  -8.73554,130.59091 -12.39307,195.93` for a gentle tangent landing
- Did NOT smooth the segment-4 handle into N6: with N7 above N6 and
  N5(=B3) above-LEFT of N6, true C1 smoothness at N6 requires segment
  4 to LOOP below N6, which looked worse than the natural corner.
  Kept the user-tweaked H2 = `129.56387,-79.684`.

**Side view rendering cleanup**
- Removed: 15-degree reference line, B1-B2 dashed extension line, BTF
  Bezier as a separate stroke, gold floor limaçon reference, chamber
  station crossbars, bass-end access oval (was inflating index.html's
  auto-fit viewBox), trumpet flare drafting inset (same)
- Kept: scoop chord (`R1-R2`), R1/R2/rc/v dots+labels, ARC_CENTER
  dot+label, two new ARC_CENTER radii dashed, the dashed `aim` line
  from rc to aim_xz

**Other artifacts (this session)**
- `buffer.svg` regenerated fresh via `make_buffer_svg.py` (188 disks +
  envelope path, 21 line segments, 0 arcs).  Locked hand-drawn versions
  preserved as `buffer.svg.LOCKED-handdrawn*`.
- `neck.svg` regenerated via `make_neck_svg.py`
- FreeCAD model `clements47.FCStd` regenerated via `build_freecad.py`
  (255 KB, 5 source objects: Chamber, FloorLimacon, Column, Neck,
  Strings).  Run with `freecadcmd`.
- Engineering drawings `clements47_techdraw.svg` and
  `clements47_shoulder_techdraw.svg` regenerated via
  `build_techdraw.py` (each ~423 KB)
- All 5 view SVGs (side, top, front, rear, sbf) regenerated; SBF
  rotated 90 deg so the soundboard renders VERTICALLY
- `clements47_views.svg` composite regenerated

**Git**
- Old GitHub repo `jclements3/clements47.git` (11 commits with
  mechanism-parts work) was DELETED via `gh repo delete`.
- Fresh empty repo created at the same URL.
- Local main pushed: 2 commits (the original local "Initial commit"
  and this session's `d6e7491` "Rebuild column, soundbox, pedestal").
- Commit author email: `james.l.clements.iii@gmail.com` (one-shot
  override; persistent git config still has the work email).

**Tablet app (../Erand/erandapp)**
- App label changed `Erand` -> `Clements47` in
  `app/src/main/res/values/strings.xml`
- The 6 new view SVGs copied to `../Erand/` (gradle's
  `syncErandAssets` task copies them into `assets/` from there with
  the `erand47_*.svg` filenames the existing app code expects)
- `lever_3d.svg` and the two techdraw SVGs added to
  `syncErandAssets`'s include list
- `../Erand/index.html` replaced with the desktop 5-panel layout
  (side wide, top + 3D-levers in col 2 split, front/rear/sbf in cols
  3/4/5).  Auto-fullscreen-on-load disabled and `< 1300px` media
  query that collapsed to 2 columns removed (tablet WebView reports
  < 1300px in landscape).  Panel-title font reduced 64px -> 13px and
  buttons reduced 50px -> 12px to fit tablet.
- Side-view column widened: `2.4fr 0.8fr 0.6fr 0.6fr 0.5fr`
  (was `1.3fr 0.9fr 0.7fr 0.7fr 1.2fr`)
- APK rebuilt with `./gradlew assembleDebug`, installed via `adb
  install -r`, app force-stopped + data-cleared between installs.
- Tablet device id: `P90YPDU16Y251200164`

### Where I stopped

After the SBF orientation fix and the global z >= 0 shift, regenerated
all 5 views + FCStd + techdraw + tablet APK.  Last item the session
was touching: this HANDOFF.md update + the commit/push.

### Late-session changes (after the original handoff write-up)

- **SBF view rotated correctly** -- bass at the BOTTOM, treble at the
  TOP, matching the perspective from C0 looking face-on at the
  soundboard.  Previous attempt had the centerline on the opposite
  side of zero from the silhouette (off-screen in the auto-fit
  bbox).  Fix in `build_views.py sbf_view_content()`: data y = +s
  (not -s); viewBox set to negative y range so the global
  `scale(1,-1)` g transform lands data correctly.
- **Tablet panel-title and button font sizes reduced** for the
  WebView (from desktop 64px / 50px down to 13px / 12px).
- **`< 1300px` media-query collapse removed** from the tablet
  index.html so the 5-column grid stays active on the tablet
  (Android WebView reports < 1300px even on 1920-wide landscape).
- **Side-view column widened** to `2.4fr 0.8fr 0.6fr 0.6fr 0.5fr`
  (was `1.3fr 0.9fr 0.7fr 0.7fr 1.2fr`).
- **Auto-fullscreen-on-load disabled** -- the desktop's auto-FS was
  racing with SVG fetch on the WebView and showing a blank panel.
- **Attempted z >= 0 shift (REVERTED)**: tried changing
  `PEDESTAL_FLOOR_Z = -70.65 -> -39.3948`.  This shortened the
  pedestal by ~31 mm instead of shifting the harp UP, which the
  user did NOT want -- they want the FULL pedestal preserved with
  the entire harp lifted by 31.26.  Reverted to -70.65; pedestal
  floor is back at z = -31.26.  Proper "lift the whole harp" still
  pending (would require shifting all N_KNOTS z, all string Ng_z /
  Nf_z columns, and SB_P0/P1 z values by +31.26 simultaneously).

- **Column upgraded to HOLLOW ELLIPTICAL CF TUBE.**  The 28 x 32 mm
  rectangular box was undersized for the round/elliptical concert-
  harp pillar the user wanted.  New cross-section: 32 x 36 mm
  ellipse with 4 mm CF wall (constants `COL_OD_X = 32`, `COL_OD_Y =
  36`, `COL_WALL_T = 4` added to clements47.py).  `COL_X_LEFT/RIGHT`
  widened to span the new 32 mm OD (centered on the previous column
  axis: -17.755 to +14.245).  N_KNOTS rows 0/1/2 nudged by -2 / +2 /
  +2 in x to keep the rake relationship.  `build_freecad.py
  build_column()` rewritten to loft a parametric-ellipse wire at
  base and top, then subtract an inner ellipse to make it hollow
  (the previous version lofted rectangles).  Buckling SF improves
  from 2.65 (old hollow box) to ~3.2 (new hollow ellipse, K = 0.7
  clamped base) under the 7079 N axial load.  FCStd, techdraw, all
  views, and tablet APK regenerated to match.

### Outstanding / deferred

1. **Pedestal floor as limaçon** — currently `P0-P1` is straight at
   the floor.  User asked for it to be a limaçon cross-section line,
   matching how `P3-P2` is the chamber bass-cap limaçon.  Needs:
   define `s_at_floor` and a floor diameter; rebuild pedestal corner
   computation.
2. **Soundbox top as clean limaçon cap** — currently the body
   polygon ends at `St_phantom` plus chamber stations near s_at_St.
   The user asked to make this a single straight limaçon-cap line
   from `B3` to `B2`.  Needs body-polygon rewrite.
3. **Acoustic port** — the original ask was whether sound can reach
   the scoop with the soundbox sealed at `B0-B1`.  Verdict from the
   plan agent (transcript above): the scoop today is geometrically
   in the soundbox bass-end wall, NOT in the pedestal.  The frustum
   we drew from `R1-R2` up to `B0-B1` is the throat connecting the
   scoop dish to the open soundbox interior; sound exits through the
   open `B0-B1` chord into the rest of the soundbox and out the
   back-wall holes.  No additional port required if we accept this
   reading.  Open question: does the user want the dish relocated
   into a hollowed pedestal cavity (and a new aperture cut in
   `B0-B1`)?  No code change made for that interpretation.
4. **N2 handle smoothing into N6** — geometric note: with N7
   above-LEFT of N6 and N5 also above-LEFT of N6, true C1 smoothness
   at N6 requires segment 4 to loop below N6 in z, which looked
   worse than the natural corner.  Left as a kink.
5. **R2 wedge between scoop rim and pedestal corner** — the
   frustum quadrilateral white-fill covers the visual area, but
   asked whether the wedges `R1-P2` and `R2-P3` should also be
   hollowed and bridged with limaçon-section ribs (per acoustic plan
   agent recommendation).  Not implemented.

### Files changed this session
clements47.py, build_views.py, edit_paths.svg, buffer.svg, neck.svg,
clements47_side.svg, clements47_top.svg, clements47_front.svg,
clements47_rear.svg, clements47_sbf.svg, clements47_views.svg,
clements47.FCStd, clements47_techdraw.svg,
clements47_shoulder_techdraw.svg, HANDOFF.md (this file).

In ../Erand/: index.html, erand47_*.svg (front/rear/side/top/sbf),
erand47.svg, erand47_techdraw.svg, erand47_shoulder_techdraw.svg,
lever_3d.svg, clements47.FCStd, erandapp/app/src/main/res/values/
strings.xml, erandapp/app/build.gradle.

### How to rebuild from scratch (home laptop)
```
cd /home/james.clements/projects/clements47
python3 build_views.py                # views
echo "_p='$(pwd)/build_freecad.py'; exec(open(_p).read(), {'__file__': _p, '__name__': '__main__'})" | freecadcmd
echo "_p='$(pwd)/build_techdraw.py'; exec(open(_p).read(), {'__file__': _p, '__name__': '__main__'})" | freecadcmd
python3 make_buffer_svg.py            # if you want fresh buffer/neck
python3 make_neck_svg.py
cd ../Erand/erandapp && ./gradlew assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am force-stop com.harp.erandapp
adb shell am start -n com.harp.erandapp/.MainActivity
```

---

## Session 2026-04-29: Acoustic refactor + parameterized scoops + neck color

### Major design changes
- **Both scoops refactored to asymmetric frustum geometry.**  Pe1=R1
  (Pe3=R3 for treble) anchored ON the cap chord at SCOOP_RIM_GAP=5mm
  from the B-corner; Pe2 (Pe4) derived by axis-aim solver so the dish
  axis passes EXACTLY through the soundhole-cluster centroid; R2 (R4)
  is the projection of Pe2 along axis_unit onto the cap chord.  All
  four points (Pe1, Pe2, R1, R2) are exposed in the dict and rendered
  in the side view.
- **Parabolas grown to maximum** while preserving 5mm rim and aim
  accuracy.  SCOOP_RIM_RADIUS 120 -> 163 mm (bass opening 240 -> 326 mm,
  +36%).  SCOOP_TREBLE_RADIUS 35 -> 38 mm (treble opening 70 -> 76 mm,
  +9% from previous; +52% from earlier 25 mm reduction step).  Both
  axis_aim_err = 0 deg.
- **Hole #3 moved s=1078 -> s=1150** to escape the 1st-mode pressure
  node at s=1000 (closed-closed chamber, fundamental ~106 Hz).
- **Bass scoop aim retuned 950 -> 827 mm** (true area-weighted
  centroid of the new 5-hole array).
- **Treble scoop aim retuned 1500 -> 1448 mm** (centroid of
  treble-cluster holes #4 and #5).
- **N5/B3 and N6/B2 coincidence** enforced.  B3 = N_KNOTS[5], B2 =
  N_KNOTS[6] (B2 was already snapped; B3 is now too).  Path
  segments edited so path's knots 4 and 5 land at canonical N6, N5.
- **N0/C3 and N1/C2 coincidence** enforced.  Path M shifted from
  -223.34 to -225.34, segment 8 endpoint adjusted so N1 = canonical
  -193.34.
- **N2 placed on column inner arc** at z=1494.49.  N_KNOTS[2]
  updated from -169.54 to -182.83.  Segment 7 endpoint and segment 8
  handle relatives recomputed so N2, N2o, N1i all sit on the inner arc.
- **N0o aligned along column direction** (parallel to C0->C3 line,
  unit (-0.117, 0.993)) -- handle no longer points at an arbitrary
  angle; it continues the column's outer edge upward into the neck.
- **N5o reduced to 68.85 mm** length (after iterations: 30 -> 60 ->
  100 -> 85 -> 76.5 -> 68.85), still parallel to F7g-G7g soundboard
  tangent, nudged southeast to clear D7s/E7s/F7s/G7s buffers.
- **N9i and N9o lengthened ~2x** (uncommitted experimental edit, but
  user approved -- "neck looks better now") to flatten the top hump.
- **Neck Bezier handles renamed** to N{x}i / N{x}o (incoming /
  outgoing per knot) instead of segment-indexed h{i}a / h{i}b.  Each
  handle name now contains the knot number it attaches to.
- **N4 moved to (582.21, 1682.69)** -- on the C7-sharp clearance
  circle, perpendicular to the buffer envelope at C7's tangent point.
  Combined with h6a (N4o) lowering -20 mm, clears the F6/G6/A6/B6/C7
  sharp-buffer violations along segment 6.
- **Neck path coincides with all 10 knot dots** (parsed from the
  hand-edited path, used as dot positions in the side view).
- **Neck color** changed from #3a2a14 (dark mahogany) to #5d4037
  (walnut) for better contrast against white background.

### Acoustic confirmation
- Chamber volume ~103 L (vs 60-75 L for traditional 47-string concert
  harps; ours +35-70%).
- Total sound-hole area 46 cm^2.
- Helmholtz frequency ~66 Hz (multi-hole formula).  In traditional
  60-90 Hz sweet spot.
- 1st chamber axial mode (closed-closed) at 106 Hz (~G#2).  Pressure
  node at chamber midpoint s=1000.  Holes are now well-separated from
  this node after #3 moved to s=1150.
- All 47 grommets verified ON the soundboard (Ng_x in [0, 643.29]).

### New parameters (clements47.py)
- SCOOP_RIM_GAP        = 5.0 mm     # min flat rim from B-corner along cap
- SCOOP_FRUSTUM_HEIGHT = 30.0 mm    # cap-to-rim depth (used by intersect)
- SCOOP_RIM_RADIUS     = 163.0 mm   # bass parabola radius (was 120)
- SCOOP_TREBLE_RADIUS  = 38.0 mm    # treble parabola radius (was 35)
- SCOOP_AIM_S_BASE     = 827.0 mm   # bass dish aim (was 950)
- SCOOP_TREBLE_AIM_S   = 1448.0 mm  # treble dish aim (was 1500)

### Side-view additions
- All 18 neck-path Bezier handles drawn as labelled dots (N0o..N9i).
- hB0, hB1 (soundbox bass-cap Bezier handles) drawn as dots without
  leader lines (default position on cap chord, so the closing edge
  starts as a straight line).
- Pe1, Pe2 (parabola rim, below cap) and R1, R2 (frustum top, on cap)
  drawn as separate dots in bass scoop.  Same for Pe3, Pe4, R3, R4 in
  treble.
- Frustum walls Pe1->R1 and Pe2->R2 (and treble equivalents) drawn as
  thinner purple lines.
- Dotted axis line now starts from the parabola VERTEX (origin) and
  runs along axis_unit to where it hits the chamber back wall.
  Mathematically perpendicular to rim chord by construction.
- Soundbox cap (B0->B1 closing edge) converted to cubic Bezier with
  hB0/hB1 handles for limacon-shaped bass cap (default straight, but
  now adjustable).
- All trumpet-tuning ports removed from side view; soundholes.csv is
  now the canonical hole list (5 holes after removing the original
  bass-end #1 at s=171).

### Pending / deferred
- (no major outstanding deferred items beyond the limaçon-cap and
  acoustic-port questions from the prior session, which remain open)

### Files changed this session
clements47.py, build_views.py, edit_paths.svg, soundholes.csv,
clements47_side.svg, clements47_top.svg, clements47_front.svg,
clements47_rear.svg, clements47_sbf.svg, clements47_views.svg,
HANDOFF.md (this file).

---

## Session 2026-04-29 (continued, autonomous): FreeCAD boolean cuts, refactor

### FreeCAD scoop boolean cuts
Implemented in `build_freecad.py`:
- **`build_pedestal_solid(doc)`**: lofts a closed solid from the floor
  limaçon at `PEDESTAL_FLOOR_Z` up to the chamber-bottom limaçon at S'b
  through 16 intermediate stations.  Linear interpolation of D, perp,
  diameter between the two endpoints.  Volume ~18.1 ML mm^3.
- **`make_scoop_cut_volume(scoop, frustum_extension_mm=15)`**: returns
  a single closed solid = paraboloid bowl (revolution of 30-pt parabola
  profile in xz about axis_unit) FUSED with a cylinder (R, length 15 mm)
  extending past the rim plane along axis_unit so the cut punches through.
- **`make_scoop(doc, host_obj, scoop, label)`**: rewrites the host's
  shape by `host_obj.Shape.cut(volume)` and adds a new Part::Feature
  `<label>Scooped` (PedestalScooped, NeckScooped) so the original solid
  stays inspectable.
- **`build_neck()`**: spliced K5 (= N_KNOTS[6] = chamber back-wall apex
  at S't = (730.39, 1622.08)) into the polyline between segs 2 and 3.
  Without this splice, c.build_neck_segments() skips i=3 and i=4, so
  the neck polygon's xmax was 660.42 mm and the entire treble scoop
  volume sat outside the neck.  Splicing K5 puts the cap apex back in.
- **`main()`** order: chamber -> floor_limacon -> column -> pedestal
  -> bass scoop cut -> neck -> treble scoop cut -> strings.

Verified cut volumes (mm^3):
| Object           | Volume         |
|------------------|----------------|
| Pedestal         | 18,148,932.95  |
| PedestalScooped  | 14,458,835.65  |
| Neck             |  6,146,837.28  |
| NeckScooped      |  6,112,626.47  |
| (delta bass)     |  3,690,097     |
| (delta treble)   |     34,211     |

`clements47.FCStd` (937 KB) and both TechDraw SVGs (1.37 MB each)
regenerated and copied to `Erand/`.

### Script refactor (clements47.py)
- Removed unused `SCOOP_FRUSTUM_HEIGHT = 30.0` constant (was set during
  the abandoned tilted-rim experiment; never read after the asymmetric
  frustum design landed).
- Extracted `_solve_aim_chord_dir(aim_xz, anchor_pt, tR, cap_chord_dir)`
  helper.  Both `compute_scoop()` and `compute_scoop_treble()` now call
  it instead of duplicating ~12 lines of cos/sin chord-direction solver
  each.  Output verified IDENTICAL to pre-refactor values (Pe2, R2, axis
  for both scoops byte-equal).

### Files changed in this autonomous batch
- `clements47.py` (refactor)
- `build_freecad.py` (boolean cuts)
- `clements47.FCStd` (with PedestalScooped + NeckScooped)
- `clements47_techdraw.svg`, `clements47_shoulder_techdraw.svg`
- `clements47_*.svg` views (already current from earlier in session)
- `Erand/clements47.FCStd`, `Erand/erand47_techdraw*.svg`

### What the home-laptop claude-ai should know
1. **FreeCAD model is now structurally correct** — pedestal and neck are
   closed solids, bass and treble parabolic scoops are properly cut
   into them.  The original Pedestal/Neck features are kept alongside
   PedestalScooped/NeckScooped so you can A/B-compare in the FreeCAD GUI.
2. **The treble scoop only removes 34 K mm^3** because the neck polygon
   is narrow at S't (cap chord only 93 mm) and the rest of the dish
   volume falls into solid-air outside the neck profile.  This is the
   max material removable given the current treble parabola size
   (R=38).  Increasing R further would violate the 5 mm rim constraint.
3. **The neck polyline now includes K5 (= N6 = B2)** at (730.39, 1622.08).
   This was a one-line splice in `build_neck()`, but it changes the neck
   y-extruded prism's silhouette.  If you regenerate the neck, expect
   a slightly larger neck polygon than before.
4. `_solve_aim_chord_dir(aim, anchor, tR, cap_dir)` is the canonical
   solver for putting Pe1=R1 (or Pe3=R3) on the cap chord with the dish
   axis aimed at a target.  Use it for any future scoop variants.
5. **Helmholtz acoustics**: chamber ~103 L, total hole area 46 cm^2,
   multi-hole effective Leff gives f_H ~66 Hz (in traditional 60-90 Hz
   sweet spot).  1st chamber axial mode at 106 Hz (closed-closed),
   pressure node at chamber midpoint s=1000 -- now well clear of all
   five soundholes after #3 was moved s=1078 -> s=1150.

