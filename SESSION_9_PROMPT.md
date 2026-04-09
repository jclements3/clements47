# CLEMENTS47 Session 9 - Timing Diagrams and Force Analysis

## Session Goal
Create accurate timing diagrams showing how discs rotate, prongs engage strings, and forces are applied to change pitch. Get the mechanical visualization correct before analyzing dynamics.

## Current Status - What Works
- Complete JSON specifications (clements47.json) with all 47 strings, discs, axles, bearings
- Correct understanding of mechanism: toggle linkage with dual natural/sharp chains
- Hand levers at shoulder (not foot pedals at crown)
- Lever positions: `\` (flat), `|` (natural), `/` (sharp)
- Disc rotation: 0Â° (9/3 o'clock horizontal) â†’ 90Â° (6/12 o'clock vertical) = 45Â° CW rotation
- ASCII diagrams showing correct layout

## Critical Issues to Fix

### 1. Prong Positioning (MOST IMPORTANT)
**WRONG:** Prongs are drawn centered on the disc edge
**CORRECT:** Prongs are TANGENT to the disc edge

Example for disc radius R=10mm, prong radius r=2mm:
- Prong center is at distance (R + r) from disc center
- At 0Â° (3 o'clock): prong center at (12, 0)
- At 90Â° (12 o'clock): prong center at (0, 12)
- At 180Â° (9 o'clock): prong center at (-12, 0)
- At 270Â° (6 o'clock): prong center at (0, -12)

### 2. Neck Position
**WRONG:** Neck drawn at natural disc level
**CORRECT:** Neck is ABOVE the discs - discs are inside/below the neck structure

The neck is the enclosure that contains the mechanism. View from side:
```
    â•â•â•â•â•â•â•â•â•â•â•â•â• Neck (top surface)
         (o|o)    Natural discs (horizontal line, all aligned)
         (o|o)    Sharp discs (staggered diagonally)
         |        Strings pass through
```

### 3. Tuning Pins
**WRONG:** Pins drawn as circles directly above strings
**CORRECT:** Strings come off pins at ~45Â° angle

From tuning pin, string goes diagonally down and back toward the soundboard:
```
    O  â† Tuning pin (round peg)
     \
      \  â† String at 45Â° angle
       |  â† String becomes vertical
```

### 4. Scale Relationships
All dimensions MUST come from clements47.json:
- `dr` = disc radius (4.27mm to 25.0mm)
- `pl` = prong length extension (12.7mm for all)
- Prong radius should scale: ~15% of disc radius
- String width should scale: ~15% of disc radius

## Files Provided in Archive

1. **clements47.json** - Complete specifications (47 strings, discs, axles)
2. **schema.json** - Field abbreviations decoder
3. **clements47.md** - Full design document with ASCII diagrams
4. **lever_positions.py** - Working text-based animation showing three positions
5. **lever_animation.py** - Working animated cycle through positions
6. **harp_profile.py** - BROKEN visualization (needs fixing)
7. **disc_prong_visualization.py** - Earlier attempt (has some useful code)

## What to Do First

### Step 1: Fix the Prong Tangent Geometry
Create a test plot showing ONE disc with TWO prongs correctly positioned as tangent circles:

```python
disc_center = (0, 0)
disc_radius = 10.0  # mm
prong_radius = 2.0  # mm

# Prong centers are at distance (disc_radius + prong_radius) from disc center
# At 0Â° (3 o'clock position):
prong1_center = (disc_radius + prong_radius, 0)

# At 180Â° (9 o'clock position):  
prong2_center = (-(disc_radius + prong_radius), 0)

# Draw disc
disc = Circle(disc_center, disc_radius, fill=False, edgecolor='blue', linewidth=2)

# Draw prongs (tangent to disc edge)
prong1 = Circle(prong1_center, prong_radius, fill=True, facecolor='red', edgecolor='darkred')
prong2 = Circle(prong2_center, prong_radius, fill=True, facecolor='red', edgecolor='darkred')
```

Verify visually that prongs are TANGENT (touching but not overlapping) the disc edge.

### Step 2: Create Correct Harp Profile
Using corrected prong geometry, create side-view showing:

1. **Base** (brown rectangle at bottom, Z=0 to Z=100)
2. **Soundboard** (curved line from base, use 9-point spline from JSON)
3. **Strings** (vertical lines, width scaled by disc size)
4. **Tuning pins** (at top, with strings coming off at 45Â°)
5. **Neck enclosure** (rectangular outline ABOVE the disc positions)
6. **Natural discs** (horizontal line at Z=1400, all aligned)
7. **Sharp discs** (staggered diagonal below naturals)
8. **Prongs** (tangent circles on disc edges)
9. **Lever** (at shoulder, showing `\` `/` or `|` position)

All using ACTUAL dimensions from clements47.json

### Step 3: Three-Position Comparison
Create side-by-side plots showing:
- Flat `\`: Prongs at 0Â°/180Â° (horizontal, 9/3 o'clock)
- Natural `|`: Natural prongs at 90Â°/270Â° (vertical, 6/12 o'clock), sharp still horizontal
- Sharp `/`: Both disc sets with vertical prongs

### Step 4: Timing Diagrams
Once visualization is correct, create plots showing:
- Lever position vs time
- Disc angles vs time (natural and sharp chains)
- Prong position vs time  
- String deflection vs time
- Force applied to string vs time

## Key Data from JSON

All C strings (use these for the profile):
- C1: X=0.0mm, disc_r=25.0mm (largest, bass)
- C2: X=107.4mm, disc_r=21.75mm
- C3: X=232.7mm, disc_r=16.33mm
- C4: X=351.0mm, disc_r=9.42mm
- C5: X=461.8mm, disc_r=6.17mm
- C6: X=565.6mm, disc_r=5.2mm
- C7: X=664.2mm, disc_r=4.41mm (smallest, treble)

All prongs: 12.7mm extension from disc surface

## Success Criteria

You know you've succeeded when:
1. âœ“ Prong circles are tangent to (touching) disc circles
2. âœ“ Disc sizes scale correctly (C1 largest, C7 smallest)
3. âœ“ Prong sizes scale with disc size (~15% of disc radius)
4. âœ“ String widths scale with disc size
5. âœ“ Neck is drawn ABOVE the disc positions
6. âœ“ Tuning pins show strings coming off at 45Â° angle
7. âœ“ Sharp discs stagger diagonally from C7 to C1
8. âœ“ Natural discs all align horizontally
9. âœ“ Visualization matches the ASCII diagram layout

## Questions to Answer in Next Session

1. What force do the prongs apply to the string?
2. How much does the string deflect (1-5mm)?
3. How fast do the discs rotate (timing)?
4. What is the engagement sequence timing (natural first, then sharp)?
5. Does the toggle mechanism properly hold the natural discs while sharp engages?

## Notes

- The mechanism is identical to traditional pedal harps, just driven from shoulder instead of crown
- The JSON is complete and accurate - trust the numbers
- The ASCII diagrams are correct - match them
- Focus on getting ONE disc+prongs correct before doing all 47
- No titles, legends, or labels needed - just the clean visualization

## Previous Session Issues

We struggled with:
1. Prong positioning (kept putting them at wrong radius)
2. Understanding the tangent geometry
3. Scaling all components correctly
4. Removing unnecessary labels/titles
5. Getting the mechanical layout to match ASCII diagram

Don't repeat these mistakes - start with the tangent geometry test first!
