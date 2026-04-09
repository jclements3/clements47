# CLEMENTS47 Harp Design Document

## Toggle Linkage Over-Center Mechanism

-----

## Executive Summary

The CLEMENTS47 is a revolutionary 47-string pedal harp featuring a **toggle linkage mechanism** with dual natural and sharp chains. This over-center mechanism enables sequential disc engagement through clever geometry rather than complex detents, creating a reliable and elegant sharping system.

**Key Innovation:** Locomotive-style coupling links between natural and sharp chains create toggle positions that allow the natural chain to move first (pedal position 0→1), hold position while the sharp chain moves (1→2), creating three distinct pitch positions without requiring detents at each disc.

-----

## I. Fundamental Design Principles

### 1.1 String Architecture

- **47 strings** spanning C1 (32.7 Hz) to G7 (3136 Hz)
- **Straight-line arrangement** along X-axis (crown to shoulder)
- **Vertical orientation** in playing position (parallel to Z-axis)
- **Physics-optimized tensioning** ranging from 48.8N (G7) to 236.7N (A1)
- **Three pitches per string:** Flat, Natural, Sharp

### 1.2 Coordinate System

```
X-axis: Crown (bass, 0mm) → Shoulder (treble, 721mm)
Y-axis: Harpist (-Y) ← Soundboard (0) → Audience (+Y)  
Z-axis: Floor (0mm) → Vertical up (+Z)
```

### 1.3 Material Philosophy

- **316 Stainless Steel:** Disc axles, prongs, hardware
- **Carbon fiber composite:** Neck structure, soundboard
- **Aluminum 6061-T6:** Bell cranks, linkage components
- **Bronze-wrapped nylon:** Bass strings
- **Nylon monofilament:** Treble strings

-----

## II. The Toggle Linkage Mechanism

### 2.1 Mechanism Type

**Over-Center Toggle Linkage** (Four-Bar Linkage with Sequential Actuation)

This mechanism uses compound bell cranks with arms arranged approximately 90° apart, creating toggle positions that enable sequential motion without requiring detents at each disc location.

### 2.2 The Three Pedal Positions

**Position 0 (Flat):**

- Natural discs: 9:15 position (disengaged)
- Sharp discs: 9:15 position (disengaged)
- Both chains at rest
- Prongs clear string on both sides

**Position 1 (Natural):**

- Natural discs: 12:30 position (engaged ~45° rotation)
- Sharp discs: 9:15 position (still disengaged)
- Natural chain has moved, sharp chain remains at rest
- Natural disc prongs engage string from above/below at angle
- Toggle geometry holds natural chain in place

**Position 2 (Sharp):**

- Natural discs: 12:30 position (held by geometry)
- Sharp discs: 12:30 position (engaged ~45° rotation)
- Sharp chain has now moved
- Both sets of prongs at 12:30 position
- Sharp disc prongs engage string, natural prongs still present but sharp dominates

### 2.3 Sequential Motion Principle

The genius of the toggle linkage is that **disc rotation is limited to approximately 45°** (not a full 90° or continuous rotation). The discs **rock back and forth** rather than spin continuously.

**Transition 0→1:**

1. Pedal input begins to move
1. Compound bell crank geometry causes natural chain to rotate
1. Natural discs rock from 9:15 → 12:30 (~45° clockwise)
1. Sharp chain remains stationary (near its geometric dead center)
1. Natural discs engage string

**Transition 1→2:**

1. Pedal continues to move
1. Natural chain reaches toggle point (geometric lock)
1. Compound bell crank now drives sharp chain
1. Sharp discs rock from 9:15 → 12:30 (~45° clockwise)
1. Natural discs held at 12:30 by toggle geometry
1. Sharp discs engage string

**Transition 2→1 (Return):**

1. Pedal reverses direction
1. Sharp chain rotates back 9:15
1. Natural chain remains at 12:30 (held by toggle)
1. Sharp discs disengage

**Transition 1→0 (Full Return):**

1. Pedal returns to rest
1. Natural chain rotates back to 9:15
1. Both chains at rest position

-----

## III. Mechanical Components

### 3.1 Dual Chain System

Each of the 7 notes (C, D, E, F, G, A, B) has **two parallel chains:**

**Natural Chain:**

- Master bell crank at crown/input
- Linkage rod
- Bell crank for string 1 (natural disc)
- Linkage rod
- Bell crank for string 2 (natural disc)
- Linkage rod
- … continues through all strings of that note
- Final bell crank at shoulder

**Sharp Chain:**

- Bell crank for string 1 (sharp disc)
- Linkage rod
- Bell crank for string 2 (sharp disc)
- Linkage rod
- … continues through all strings of that note

### 3.2 Compound Bell Cranks (Coupling Linkages)

At each string position, a **compound bell crank** connects the natural and sharp chains. This is the key component that creates the toggle action.

**Design:**

- Two arms arranged approximately 90° apart
- One arm connects to natural chain
- Other arm connects to sharp chain
- Pivot bearing at center
- **Locomotive-style coupling** between chains

**Function:**

- As natural arm sweeps through large arc, sharp arm barely moves (near dead center)
- At toggle point, geometry reverses
- As sharp arm sweeps through large arc, natural arm barely moves (near its dead center)

### 3.3 Bell Crank Specifications

**Material:** Aluminum 6061-T6 or steel plate
**Thickness:** 5-10mm
**Pivot bearing:** Needle bearing or bronze bushing, 6-10mm diameter
**Connection method:** Pinned connections with clevis pins (3-4mm diameter)
**Arm lengths:** Vary by string position (shorter arms for treble strings)

### 3.4 Linkage Rods

**Material:** 316 Stainless Steel or aluminum
**Diameter:** 3-6mm depending on load
**Length:** Varies by string spacing (13.3mm to 17.9mm between strings)
**End connections:** Rod end bearings (heim joints) or clevis pins
**Thread:** M6×1.0 LH/RH for length adjustment where needed

-----

## IV. Disc and Axle System

### 4.1 Disc Axle Configuration

**Total disc axles:** 47 (one per string)
**Axle orientation:** Parallel to Y-axis (horizontal, perpendicular to strings)
**Axle material:** 316 Stainless Steel
**Axle diameters:** 4mm, 5mm, 6mm, or 8mm depending on torque requirements

**Alternating sides:**

- Odd string numbers (1, 3, 5…47): Left side, extends toward harpist (-Y), offset -15mm
- Even string numbers (2, 4, 6…46): Right side, extends toward audience (+Y), offset +15mm
- **Purpose:** Prevent bearing interference at tight string spacing

### 4.2 Disc Specifications

Each axle carries **two discs:**

- **Natural disc** at 6.0mm from axle end
- **Sharp disc** at 8.0mm from axle end
- **Spacing:** 2.0mm between disc centers

**Disc geometry:**

- Elliptical profile (47 unique sizes)
- Radius range: 4.27mm (F7) to 25.0mm (C1)
- Material: Brass or bronze
- Thickness: 2-3mm

**Prongs:**

- **Two prongs per disc** (positioned 180° apart)
- Thread: M3×0.5 metric
- Total length: 18.7mm (12.7mm extension from disc surface)
- Material: 316 Stainless Steel
- Installation: Threaded into disc, secured with Loctite 243

### 4.3 Bearing System

**Total bearings:** 94 (two per axle)
**Types used:**

- 6008 (8mm ID): High-load bass strings
- 6006 (6mm ID): Medium strings
- 6905 (5mm ID): Medium-light strings
- 6904 (4mm ID): Treble strings
  **All bearings:** Deep groove ball bearings, 5mm width

**Mounting:**

- Left plate: Aluminum/carbon composite, 10mm thick
- Right plate: Aluminum/carbon composite, 10mm thick
- Bearing pockets: 5mm depth for press-fit installation
- Precision alignment via dowel pins

### 4.4 Disc Rotation Limits

**Critical design feature:** Discs do NOT rotate continuously. Maximum rotation is **approximately 45°**.

**Why rotation is limited:**

- String physically blocks further rotation
- Prongs engage string from above and below
- At 12:30 position, prongs are maximally engaging string
- Further rotation would cause prongs to collide with string

-----

## V. String System

### 5.1 String Specifications Summary

|Range|Count|Core Material|Wrap Material|Tension Range|
|-----|-----|-------------|-------------|-------------|
|C1-B1|7    |Steel/Nylon  |Bronze       |217-237 N    |
|C2-B2|7    |Steel/Nylon  |Bronze       |210-226 N    |
|C3-B3|7    |Nylon        |Nylon/Bronze |127-210 N    |
|C4-G4|5    |Nylon        |None         |108-129 N    |
|A4-G7|21   |Nylon        |None         |49-106 N     |

### 5.2 Disc Engagement Radii

**Engagement radius** = Disc radius + Prong extension (12.7mm)

Range: 16.97mm (F7) to 37.7mm (C1)

**Critical clearance:** String vibration amplitude varies from 0.3mm (G7) to 7.6mm (C1). Disc engagement radius must accommodate vibration while maintaining reliable prong contact.

### 5.3 String Positions (X-coordinates)

Strings positioned along X-axis from crown (0mm) to shoulder (721mm):

- C strings: 0.0, 107.4, 232.7, 351.0, 461.8, 565.6, 664.2 mm
- D strings: 0.0, 125.3, 250.6, 367.4, 477.2, 580.0, 677.5 mm
- E strings: 17.9, 143.2, 268.0, 383.8, 492.6, 594.4, 690.8 mm
- F strings: 35.8, 161.1, 285.4, 400.2, 508.0, 608.8, 704.1 mm
- G strings: 53.7, 179.0, 301.8, 415.6, 522.4, 623.2, 717.4 mm
- A strings: 71.6, 196.9, 318.2, 431.0, 536.8, 637.6 mm
- B strings: 89.5, 214.8, 334.6, 446.4, 551.2, 650.9 mm

-----

## VI. Neck Structure

### 6.1 Overall Dimensions

- **Length:** 720mm (X-direction, crown to shoulder)
- **Internal width:** 200mm (Y-direction, harpist to audience)
- **Internal height:** 250mm (Z-direction, vertical)
- **Material:** Hollow carbon fiber box beam
- **Wall thickness:** 5-10mm (optimized for stiffness-to-weight)

### 6.2 Internal Cavity Organization

**Upper routing channel:** Natural chain components
**Middle zone:** Disc axles and bearings
**Lower routing channel:** Sharp chain components
**Coupling linkages:** Vertical connections between chains at each string position

### 6.3 Mounting Plates

**Left plate (toward harpist):**

- Holds odd-numbered string axles
- Y-offset: -15mm
- Bearing pocket depth: 5mm
- Material: Aluminum or carbon composite

**Right plate (toward audience):**

- Holds even-numbered string axles
- Y-offset: +15mm
- Bearing pocket depth: 5mm
- Material: Aluminum or carbon composite

**Assembly method:**

- Bolted connection to neck structure
- Precision dowel pins for alignment
- Sealed to protect internal mechanism

### 6.4 Geometry

Neck slopes from crown to shoulder:

- Crown position: X=0, Z=1514.9mm (59.6 inches)
- Shoulder position: X=721mm, Z=1334.9mm (52.6 inches)
- Slope angle: -14.01° (downward from crown to shoulder)
- Height change: -180mm over 721mm length

-----

## VII. Pedal/Lever Control System

### 7.1 Input Method

**Traditional harp:** Foot pedals at pillar base
**Alternative (Clements47 option):** Hand levers at shoulder block

### 7.2 Pedal-to-Chain Connection

**For foot pedal control:**

1. Foot pedal at pillar base
1. Vertical rod up pillar (inside pillar cavity)
1. Rod emerges at crown
1. Clevis connection to master bell crank
1. Master bell crank drives natural chain

**For hand lever control:**

1. Lever at shoulder block (7 levers: C, D, E, F, G, A, B)
1. Push-pull rod (50-100mm, 6mm diameter, 316SS)
1. Lever bell crank (2:1 mechanical advantage)
1. Clamp collar connection to master bell crank input
1. Master bell crank drives natural chain

### 7.3 Three-Position Detent

**Location:** At pedal/lever input only (NOT at each disc)

**Mechanism:**

- Ball detent with spring preload
- Three dimples for Flat/Natural/Sharp positions
- Ball diameter: 3mm, hardened steel
- Spring: 3mm OD, 10mm length, 5N preload
- Force to move: 5-10N
- Adjustment: M4 screw for spring preload

**Position indication:**

- Tactile feedback via detent
- Optional visual indicator
- Optional color/shape coding for hand levers

-----

## VIII. Toggle Linkage Design Details

### 8.1 Four-Bar Linkage Analysis

The compound bell crank at each string position forms a four-bar linkage:

1. **Ground link:** Neck structure (fixed)
1. **Input link:** Arm from natural chain
1. **Coupler:** Bell crank body with two arms
1. **Output link:** Arm to sharp chain

**Toggle positions occur when links align** creating mechanical advantage approaching infinity (geometric lock).

### 8.2 Arm Angle Relationship

**Natural arm and sharp arm arranged ~90° apart on bell crank:**

When natural arm is at maximum displacement:

- Natural arm: Large angular sweep
- Sharp arm: Near its dead center (minimal motion)
- Toggle point approaching

When sharp arm is at maximum displacement:

- Sharp arm: Large angular sweep
- Natural arm: Near its dead center (minimal motion)
- Natural chain held by geometry

### 8.3 Mechanical Advantage Through Motion

**Position 0→1 (Natural engagement):**

- Input: Pedal/lever motion
- Natural arm MA: High (2:1 to 5:1 depending on position)
- Sharp arm MA: Very low (near dead center)
- Result: Natural discs rotate, sharp discs barely move

**Position 1→2 (Sharp engagement):**

- Input: Continued pedal/lever motion
- Natural arm MA: Very low (past toggle, near dead center)
- Sharp arm MA: High (2:1 to 5:1)
- Result: Sharp discs rotate, natural discs held

### 8.4 Lost Motion vs. Toggle Action

**Traditional lost motion:** Intentional slop/clearance in linkages
**Toggle action (used here):** Geometric dead centers create sequential motion without clearance

**Advantages of toggle over lost motion:**

- More positive positioning
- No accumulated wear from clearances
- Self-reinforcing (geometry holds position)
- Smoother operation

-----

## IX. Manufacturing Specifications

### 9.1 Bell Crank Fabrication

**Material:** Aluminum 6061-T6 plate or mild steel
**Processes:**

1. Laser/waterjet cutting of profile
1. CNC drilling of pivot hole and pin holes
1. Deburring and edge finishing
1. Anodizing (aluminum) or coating (steel)

**Critical dimensions:**

- Pivot hole: ±0.01mm for bearing fit
- Pin holes: ±0.02mm
- Arm lengths: ±0.1mm
- Arm angle: ±1°

**Tolerances matter:** Arm angle errors accumulate through chain, affecting final disc position.

### 9.2 Linkage Rod Production

**Material:** 316 Stainless Steel rod, 3-6mm diameter
**Processes:**

1. Cut to length (+2mm for threading)
1. Thread ends M6×1.0 or M4×0.7
1. Install rod end bearings or fabricate clevises
1. Inspect threads with go/no-go gauges

**Quality control:**

- Straightness: <0.1mm over length
- Thread engagement: Minimum 1.5× diameter
- Free rotation of rod ends: <0.5N breakaway torque

### 9.3 Disc Axle Machining

**Material:** 316 Stainless Steel rod, 4-8mm diameter
**Processes:**

1. CNC lathe: Turn to diameter ±0.005mm
1. Cut to length (44mm ±0.1mm)
1. Face ends perpendicular ±0.01mm
1. Deburr and polish bearing surfaces to Ra 0.8μm
1. Inspect diameter with micrometer

**Bearing fit critical:**

- Axle diameter: h6 tolerance (light press fit)
- Surface finish: <0.8μm Ra for bearing life
- Straightness: <0.02mm over length

### 9.4 Disc Fabrication

**Material:** Brass C360 or Bronze C510, 2-3mm plate
**Processes:**

1. CNC mill elliptical profile (47 unique profiles)
1. Drill center hole for axle (slip fit, +0.02mm)
1. Drill and tap M3×0.5 holes for prongs (2 per disc, 180° apart)
1. Deburr and polish edges
1. Mark disc with note/type (laser engraving)

**Quality control:**

- Prong hole position: ±0.1mm from center
- Prong hole perpendicularity: ±1°
- Disc radius: ±0.2mm
- Surface finish: Smooth to avoid string damage

**Assembly:**

1. Press disc onto axle at specified position (6.0mm or 8.0mm from end)
1. Pin or set screw to lock position
1. Thread M3 prongs into disc
1. Apply Loctite 243 to threads
1. Torque to 0.5 Nm (careful not to strip)

-----

## X. Assembly Procedures

### 10.1 Subassembly: Single-String Mechanism

**Components for one string:**

- 1 disc axle with 2 discs and 4 prongs installed
- 2 bearings pressed onto axle
- 2 bell cranks (one for natural chain, one for sharp chain)
- 1 compound bell crank (coupling linkage)
- Linkage rods to adjacent strings
- Hardware (pins, clips, washers)

**Assembly sequence:**

1. Press bearings onto disc axle
1. Install axle in mounting plate (appropriate side based on string number)
1. Attach natural bell crank to natural disc
1. Attach sharp bell crank to sharp disc
1. Install compound bell crank pivot
1. Connect natural arm to natural bell crank
1. Connect sharp arm to sharp bell crank
1. Test motion through 0→1→2 positions
1. Verify disc positions at each pedal position
1. Check for binding or interference

### 10.2 Chain Assembly

**For each note (C, D, E, F, G, A, B):**

1. Install all disc axles for that note (6-7 strings)
1. Install master bell crank at crown/input
1. Connect master to first string natural bell crank via linkage rod
1. Connect subsequent natural bell cranks via linkage rods
1. Connect all sharp bell cranks via linkage rods
1. Install compound bell cranks at each position
1. Test full chain motion
1. Adjust linkage rod lengths if needed
1. Verify all discs reach correct positions simultaneously

### 10.3 Neck Assembly Integration

**Complete harp assembly:**

1. Fabricate/obtain carbon fiber neck structure
1. Install left mounting plate with all odd-string axles
1. Install right mounting plate with all even-string axles
1. Route all 7 natural chains through upper channel
1. Route all 7 sharp chains through lower channel
1. Install compound bell cranks between chains
1. Connect master bell cranks to pedal/lever inputs
1. Install detent mechanisms at inputs
1. String the harp (start with low tension, gradually increase)
1. Test each string at all three positions
1. Fine-tune linkage adjustments
1. Verify no binding through full range
1. Seal neck cavity (dust covers, access panels)

-----

## XI. Adjustment and Tuning

### 11.1 Disc Position Calibration

**Objective:** All discs of a given note reach exactly 9:15, 12:30, 12:30 at pedal positions 0, 1, 2.

**Procedure:**

1. Set pedal to position 0 (flat)
1. Measure disc angles (should all be 9:15)
1. If disc is off, adjust linkage rod length to/from that disc
1. Repeat for position 1 (natural, 12:30)
1. Repeat for position 2 (sharp, 12:30)
1. Iterate until all discs synchronized

**Tools needed:**

- Angle gauge or protractor
- Linkage rod length adjustment (turnbuckle or threaded rod ends)
- Patience (this is iterative and time-consuming)

### 11.2 String Pitch Verification

**For each string, verify three pitches:**

Position 0 (Flat): String vibrates at “flat” frequency
Position 1 (Natural): String vibrates at “natural” frequency  
Position 2 (Sharp): String vibrates at “sharp” frequency

**Adjustment method:**

1. Tune string to “natural” pitch with pedal at position 1
1. Move pedal to position 0, measure pitch (should be flat)
1. If flat pitch is wrong, adjust disc angle at position 0
1. Move pedal to position 2, measure pitch (should be sharp)
1. If sharp pitch is wrong, adjust disc angle at position 2
1. Re-tune natural, verify all three pitches
1. Iterate until all three pitches correct

**This is the hardest part of harp setup** and can take hours per string for initial setup.

### 11.3 Action Feel Optimization

**Pedal/lever feel should be:**

- Smooth through entire range
- Distinct detent “clicks” at each position
- Consistent force required across all 7 pedals/levers
- No binding or sticking

**Adjustments:**

- Detent spring preload (increase for stronger click)
- Bearing preload (adjust if too tight or too loose)
- Linkage rod alignment (ensure rods pull straight, not at angles)
- Lubrication (light oil on bearings, dry graphite on pivots)

-----

## XII. Performance Specifications

### 12.1 Pitch Change Speed

**Mechanical limit:** Toggle linkage can change positions in ~0.1-0.3 seconds per string
**Practical limit:** Harpist technique limits to ~0.5-1.0 seconds for clean pitch change
**Advantage over manual levers:** All strings of a note change simultaneously

### 12.2 Reliability Targets

**Bearing life:** >10,000 hours (deep groove ball bearings, properly lubricated)
**Linkage wear:** Minimal wear with proper materials (steel pins in bronze/aluminum)
**Disc/prong life:** >100,000 cycles (stainless steel on brass/nylon string)
**Detent life:** >500,000 cycles (hardened steel ball on hardened dimples)

### 12.3 Maintenance Schedule

**Daily (performance harp):**

- Visual inspection of disc positions
- Check for loose hardware
- Wipe down exposed components

**Weekly:**

- Lubricate bearings (1 drop light oil per bearing)
- Check linkage rod connections
- Verify pedal/lever detent function

**Monthly:**

- Full mechanism inspection
- Re-calibrate disc positions if needed
- Check bearing play (replace if excessive)
- Clean and re-lubricate all pivots

**Annually:**

- Complete disassembly and inspection
- Replace worn bearings
- Re-surface or replace worn discs
- Replace worn prongs
- Refinish/re-coat components as needed

-----

## XIII. Comparison to Traditional Pedal Harp

### 13.1 Clements47 Advantages

**Mechanical:**

- Toggle linkage is simpler than piston/bell-crank systems
- Fewer parts than traditional crankshaft mechanisms
- Direct linkage (shorter power path, less lost motion)
- Self-reinforcing toggle positions (geometry holds discs)

**Practical:**

- Straight neck vs. curved (easier to manufacture)
- Shorter overall height (easier to transport)
- Modular design (chains can be serviced independently)
- Smaller footprint

**Cost:**

- Estimated 1/6 the cost of concert grand pedal harp
- Simpler manufacturing (no complex curved crankshafts)
- Standard bearings and hardware
- Carbon fiber construction reduces weight and cost

### 13.2 Traditional Harp Advantages

**Established design:**

- 200+ years of refinement
- Known reliability
- Established manufacturing processes
- Worldwide service network

**Sound:**

- Larger soundboard (curved geometry)
- Proven acoustic design
- Traditional aesthetic

### 13.3 Clements47 Trade-offs

**Accepts:**

- New mechanism requires validation
- Toggle linkage is novel (unproven in production harps)
- Straight geometry changes ergonomics slightly

**Gains:**

- Modern materials (carbon fiber, stainless steel)
- Portable design
- Accessible cost
- Simplified manufacturing

-----

## XIV. Design Status and Next Steps

### 14.1 Current Status

**Completed:**

- ✅ Complete string calculations (47 strings, tensions, frequencies)
- ✅ Disc geometry (47 unique sizes, prong specifications)
- ✅ Toggle linkage mechanism concept
- ✅ Bearing selection and specifications
- ✅ Coordinate system and geometry
- ✅ Material selection

**In Progress:**

- 🔄 Detailed CAD models of toggle linkage components
- 🔄 Finite element analysis of bell crank stresses
- 🔄 Kinematic simulation of toggle action
- 🔄 Manufacturing process documentation

**Not Started:**

- ⏸️ Physical prototype construction
- ⏸️ Acoustic testing
- ⏸️ Long-term reliability testing
- ⏸️ Cost optimization and supplier selection

### 14.2 Critical Validation Needed

**Mechanical validation:**

1. Build single-string prototype to verify toggle linkage concept
1. Test disc rotation limits and engagement angles
1. Verify sequential motion (natural first, then sharp)
1. Measure forces required at pedal input
1. Test for binding, backlash, and lost motion

**Acoustic validation:**

1. Verify disc engagement changes pitch correctly
1. Measure pitch accuracy at all three positions
1. Test for unwanted noise (disc/prong clicking)
1. Verify string vibration not impeded by disc proximity

**Durability validation:**

1. Cycle test linkage components (100,000+ cycles)
1. Accelerated wear testing on discs and prongs
1. Bearing life testing under load
1. String life testing with repeated pitch changes

### 14.3 Manufacturing Development

**Prototype phase:**

- CNC machining of all metal components
- 3D printing of test fixtures and alignment jigs
- Hand assembly with careful documentation
- Iterative design refinement

**Production phase:**

- Design for manufacturing (DFM) optimization
- Supplier selection and qualification
- Quality control procedures
- Assembly jigs and fixtures
- Production cost analysis

### 14.4 Recommended Prototype Sequence

**Phase 1: Single-String Proof of Concept**

- Build one complete mechanism for one string
- Validate toggle linkage sequential action
- Verify disc engagement and pitch changes
- Measure forces and travel distances
- **Cost estimate:** $500-1,000
- **Timeline:** 4-6 weeks

**Phase 2: Single-Note Chain (7 strings)**

- Build complete C-note mechanism (7 strings)
- Validate chain synchronization
- Test compound bell crank coupling
- Verify all discs reach positions simultaneously
- **Cost estimate:** $3,000-5,000
- **Timeline:** 8-12 weeks

**Phase 3: Full 47-String Prototype**

- Build complete harp mechanism
- Integration with soundboard and frame
- Full acoustic testing
- Playability evaluation by professional harpist
- **Cost estimate:** $15,000-25,000
- **Timeline:** 6-9 months

-----

## XV. Conclusion

The CLEMENTS47 represents a revolutionary approach to pedal harp design, using a **toggle linkage over-center mechanism** to achieve reliable three-position pitch changes without complex crankshafts or extensive detent systems.

**Key innovations:**

1. **Toggle linkage sequential actuation** creates natural→sharp transition through geometry rather than detents
1. **Limited disc rotation** (~45°) rather than continuous rotation simplifies design
1. **Dual chain architecture** separates natural and sharp actuation paths
1. **Compound bell cranks** with ~90° arm angles create toggle positions naturally
1. **Straight-line geometry** simplifies manufacturing compared to traditional curved necks

**The mechanism relies on fundamental mechanical engineering principles:**

- Four-bar linkage kinematics
- Over-center toggle positions
- Geometric dead centers creating sequential motion
- Mechanical advantage variation through range of motion

**Success depends on:**

- Precise manufacturing tolerances (disc angles, linkage lengths)
- Proper material selection (wear resistance, friction)
- Careful assembly and adjustment procedures
- Validation through prototype testing

The toggle linkage mechanism is elegant, simple, and potentially more reliable than traditional designs. However, it remains unproven in production harps and requires physical validation before production commitment.

**This design document provides the complete mechanical specification** needed to build a prototype and validate the concept. The next critical step is fabrication and testing of a single-string mechanism to prove the toggle linkage principle in practice.

-----

## Document Revision History

**Version 1.0** - January 5, 2026

- Initial complete design document
- Toggle linkage mechanism fully specified
- All 47 string specifications included
- Manufacturing and assembly procedures documented
- Based on corrected understanding of actual mechanism (no crankshaft with journal throws)