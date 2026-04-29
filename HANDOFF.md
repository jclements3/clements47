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
- **Whole harp shifted to z >= 0**: changed
  `PEDESTAL_FLOOR_Z = -70.65 -> -39.3948` so floor_z_ped lands at
  exactly 0.  Pedestal lower edge (P0/P1) and column lower edge
  (C0/C1) are now at z = 0 instead of z = -31.26.  The pedestal is
  ~31 mm shorter; everything else is unchanged.  All other harp
  parts (B0/B1/B2/B3, strings, neck) were already above z = 0.

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
