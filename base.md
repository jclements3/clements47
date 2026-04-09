# Harp Base - Bottom View

This diagram shows the harp pedal mechanism as viewed from **below the harp, looking up from the floor**.

## Pedal Positions and String Pitch

Each pedal has three positions controlled by notches in the pedal slot:

| Position | Pedal State | String Pitch | Disc Rotation | Vertical Rod |
|----------|-------------|--------------|---------------|--------------|
| **Up** | Flat (â™­) | Lowest | 0Â° (disengaged) | Lowest position |
| **Middle** | Natural (â™®) | Middle | 45Â° (first prong engages) | Middle position |
| **Down** | Sharp (â™¯) | Highest | 90Â° (second prong engages) | Highest position |

## Lever Mechanics

The pedal mechanism uses **bell cranks** to convert horizontal pedal motion into vertical rod motion inside the pillar.

### Motion Transfer

```
PEDAL (horizontal)     BELL CRANK (pivot)     VERTICAL ROD (in pillar)
      â†â†’          â†’      â†º              â†’           â†‘â†“
   Push/Pull           Rotate                  Rise/Fall
```

### Mechanical Advantage

| Parameter | Value |
|-----------|-------|
| Pedal travel per notch | ~30mm |
| Vertical rod displacement | ~12mm |
| **Lever ratio** | **2.5:1** |
| Bell crank input arm | 25mm |
| Bell crank output arm | 10mm |

The 2.5:1 ratio means:
- Pressing the pedal **30mm** produces **12mm** of vertical rod travel
- This 12mm is sufficient to rotate the semitone discs through their engagement positions

## What Happens When You Press a Pedal

### Flat â†’ Natural (pedal moves from UP to MIDDLE)

1. Player presses pedal down by ~30mm into middle notch
2. Horizontal pedal rod **pulls inward** toward pillar
3. Bell crank **rotates** around its pivot point
4. Output arm pushes vertical rod **up** by ~12mm
5. Action rod rises through pillar and neck
6. First disc (natural disc) rotates from 0Â° to 45Â°
7. Prong engages string, **shortening vibrating length**
8. String pitch **rises one semitone** (e.g., Câ™­ â†’ Câ™®)

### Natural â†’ Sharp (pedal moves from MIDDLE to DOWN)

1. Player presses pedal down another ~30mm into bottom notch
2. Horizontal rod pulls inward another ~30mm
3. Bell crank rotates further
4. Vertical rod rises another ~12mm (total ~24mm from flat)
5. Second disc (sharp disc) rotates from 45Â° to 90Â°
6. Second prong engages string, **shortening it further**
7. String pitch **rises another semitone** (e.g., Câ™® â†’ Câ™¯)

### Return Springs

Each bell crank has a **torsion spring** that:
- Biases the mechanism toward the "up" (flat) position
- Provides tactile resistance so the player can feel notch positions
- Returns the pedal if released (though pedals lock in notches)

## Diagram Elements

- **Red lines**: Pedal rods from pedal to bell crank input arm
- **Blue arc**: Bell crank pivot points (where cranks mount to pillar base)
- **Blue lines**: Bell crank input arms (toward pedals)
- **Orange lines**: Bell crank output arms (toward pillar center)
- **Orange circle**: Vertical rod entry points into pillar
- **Red polyline**: Base frame structural outline

### Pedal Arrangement

- **Left foot** (3 pedals): D, C, B
- **Right foot** (4 pedals): E, F, G, A

Note: There is a gap between B and E to accommodate the player's feet.

## Coordinate System

- Units: 1/100 mm (so 10000 = 100mm = 10cm)
- ViewBox: 215.9mm x 279.4mm (letter size)
- Origin (0,0): Top-left corner
- Pillar center: approximately (9300, 2100)

## Diagram

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 21590 27940" width="215.9mm" height="279.4mm">
  <!--
    Harp Base - Bottom View (looking up from floor)
    Units: 1/100 mm

    Lever system: Bell cranks at pivot arc convert horizontal pedal
    motion to vertical rod motion in pillar.

    Lever ratio 2.5:1: 30mm pedal travel â†’ 12mm rod displacement
  -->

  <!-- Pillar center reference -->
  <circle cx="9300" cy="2100" r="100" fill="#888" opacity="0.5"/>

  <!-- Bell crank pivot arc (R=1600, where cranks mount) -->
  <path d="M 7700,2100 A 1600 1600 0 0 1 10900,2100"
        stroke="#0066cc" stroke-width="60" fill="none"/>

  <!-- 7 pedal rods (pedal position to bell crank input arm end) -->
  <!-- D: angle -56Â° from pillar -->
  <line x1="2100" y1="5600" x2="7980" y2="2990" stroke="red" stroke-width="51"/>
  <!-- C: angle -42Â° -->
  <line x1="3700" y1="7300" x2="8230" y2="3170" stroke="red" stroke-width="51"/>
  <!-- B: angle -28Â° -->
  <line x1="5750" y1="8600" x2="8550" y2="3310" stroke="red" stroke-width="51"/>
  <!-- E: angle +14Â° -->
  <line x1="8050" y1="9050" x2="9690" y2="3340" stroke="red" stroke-width="51"/>
  <!-- F: angle +30Â° -->
  <line x1="13100" y1="8500" x2="10100" y2="3240" stroke="red" stroke-width="51"/>
  <!-- G: angle +46Â° -->
  <line x1="15100" y1="6950" x2="10450" y2="3050" stroke="red" stroke-width="51"/>
  <!-- A: angle +60Â° -->
  <line x1="16700" y1="5300" x2="10690" y2="2760" stroke="red" stroke-width="51"/>

  <!-- Bell crank pivot points (on the arc) -->
  <circle cx="7980" cy="2590" r="80" fill="#0066cc"/>  <!-- D -->
  <circle cx="8230" cy="2770" r="80" fill="#0066cc"/>  <!-- C -->
  <circle cx="8550" cy="2910" r="80" fill="#0066cc"/>  <!-- B -->
  <circle cx="9690" cy="2940" r="80" fill="#0066cc"/>  <!-- E -->
  <circle cx="10100" cy="2840" r="80" fill="#0066cc"/> <!-- F -->
  <circle cx="10450" cy="2650" r="80" fill="#0066cc"/> <!-- G -->
  <circle cx="10690" cy="2360" r="80" fill="#0066cc"/> <!-- A -->

  <!-- Bell crank input arms (from pivot toward pedal, length=2500) -->
  <line x1="7980" y1="2590" x2="7980" y2="2990" stroke="#0066cc" stroke-width="80"/>
  <line x1="8230" y1="2770" x2="8230" y2="3170" stroke="#0066cc" stroke-width="80"/>
  <line x1="8550" y1="2910" x2="8550" y2="3310" stroke="#0066cc" stroke-width="80"/>
  <line x1="9690" y1="2940" x2="9690" y2="3340" stroke="#0066cc" stroke-width="80"/>
  <line x1="10100" y1="2840" x2="10100" y2="3240" stroke="#0066cc" stroke-width="80"/>
  <line x1="10450" y1="2650" x2="10450" y2="3050" stroke="#0066cc" stroke-width="80"/>
  <line x1="10690" y1="2360" x2="10690" y2="2760" stroke="#0066cc" stroke-width="80"/>

  <!-- Bell crank output arms (from pivot toward pillar center, length=1000) -->
  <line x1="7980" y1="2590" x2="8550" y2="2340" stroke="#cc6600" stroke-width="80"/>
  <line x1="8230" y1="2770" x2="8720" y2="2480" stroke="#cc6600" stroke-width="80"/>
  <line x1="8550" y1="2910" x2="8940" y2="2580" stroke="#cc6600" stroke-width="80"/>
  <line x1="9690" y1="2940" x2="9510" y2="2490" stroke="#cc6600" stroke-width="80"/>
  <line x1="10100" y1="2840" x2="9780" y2="2430" stroke="#cc6600" stroke-width="80"/>
  <line x1="10450" y1="2650" x2="10020" y2="2320" stroke="#cc6600" stroke-width="80"/>
  <line x1="10690" y1="2360" x2="10180" y2="2150" stroke="#cc6600" stroke-width="80"/>

  <!-- Vertical rod entry points (inner circle, where rods go up pillar) -->
  <circle cx="9300" cy="2100" r="600" stroke="#cc6600" stroke-width="40" fill="none"/>

  <!-- Base frame outline -->
  <polyline points="4600,3400 5400,5800 6700,6900 8300,7650 10300,7650 12100,6900 13400,5550 14100,3400 13900,3250 10900,1350 7600,1400 4600,3400"
            stroke="red" stroke-width="51" fill="none"/>

  <!-- Labels -->
  <text x="1800" y="5400" font-size="400" fill="#666">D</text>
  <text x="3400" y="7100" font-size="400" fill="#666">C</text>
  <text x="5450" y="8400" font-size="400" fill="#666">B</text>
  <text x="8100" y="9400" font-size="400" fill="#666">E</text>
  <text x="13300" y="8700" font-size="400" fill="#666">F</text>
  <text x="15300" y="7150" font-size="400" fill="#666">G</text>
  <text x="16900" y="5500" font-size="400" fill="#666">A</text>
</svg>
```

## Physics Summary

### Force Chain

```
Player's foot
    â†“
Pedal (lever arm ~150mm from pivot)
    â†“
Horizontal pedal rod (push/pull)
    â†“
Bell crank input arm (25mm)
    â†“ (pivot rotation)
Bell crank output arm (10mm)
    â†“
Vertical action rod (rises in pillar)
    â†“
Disc axle (rotates disc)
    â†“
Prong engages string (shortens vibrating length)
    â†“
Pitch increases by one semitone
```

### Energy Consideration

- Player exerts ~20-50N on pedal
- Pedal mechanical advantage: ~3:1 (foot lever)
- Bell crank ratio: 2.5:1
- Combined ratio: ~7.5:1
- Force at disc: ~150-375N (sufficient to deflect string ~1.5mm)

### Vibrating Length Change

For a semitone (ratio 2^(1/12) â‰ˆ 1.0595):
- Original length L produces frequency f
- Shortened length L/1.0595 produces frequency f Ã— 1.0595
- For a 1000mm string: ~56mm shorter per semitone
- Disc prong deflection provides this shortening
