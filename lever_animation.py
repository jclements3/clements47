#!/usr/bin/env python3
r"""
CLEMENTS47 Lever and Disc Engagement Animation

Demonstrates what happens when you flip the lever through the three positions:
- Flat (\): Both discs at 9/3 o'clock (horizontal, disengaged)
- Natural (|): Natural disc at 6/12 o'clock (vertical, engaged), sharp still at 9/3
- Sharp (/): Both discs at 6/12 o'clock (vertical, both engaged)
"""

import time
import sys

def clear_screen():
    """Clear the terminal screen"""
    print("\033[2J\033[H", end='')

def show_disc_position(natural_engaged, sharp_engaged, lever_pos):
    r"""
    Display the disc and prong positions
    
    Args:
        natural_engaged: True if natural disc is engaged (6/12 o'clock)
        sharp_engaged: True if sharp disc is engaged (6/12 o'clock)
        lever_pos: Lever symbol (\, |, or /)
    """
    
    # Define disc assemblies based on engagement
    if natural_engaged:
        # Natural disc rotated 45Â° CW: prongs at 6 and 12 o'clock
        natural = [
            "  | o)  ",  # 12 o'clock prong engaging from above
            "  |     ",
            "(o|     ",  # 6 o'clock prong engaging from below
            "  |     "
        ]
    else:
        # Natural disc at rest: prongs at 9 and 3 o'clock (horizontal)
        natural = [
            "        ",
            "(o|o)   ",  # Both prongs horizontal, clear of string
            "  |     ",
            "        "
        ]
    
    if sharp_engaged:
        # Sharp disc rotated 45Â° CW: prongs at 6 and 12 o'clock
        sharp = [
            "  | o)  ",  # 12 o'clock prong engaging from above
            "  |     ",
            "(o|     ",  # 6 o'clock prong engaging from below
            "  |     "
        ]
    else:
        # Sharp disc at rest: prongs at 9 and 3 o'clock (horizontal)
        sharp = [
            "        ",
            "(o|o)   ",  # Both prongs horizontal, clear of string
            "  |     ",
            "        "
        ]
    
    # Build display
    clear_screen()
    print("=" * 60)
    print("CLEMENTS47 - Lever and Disc Engagement")
    print("=" * 60)
    print()
    print(f"Lever Position: {lever_pos}")
    print()
    
    # Show natural disc
    print("NATURAL DISC:")
    for line in natural:
        print("    " + line)
    print()
    
    # Show sharp disc
    print("SHARP DISC:")
    for line in sharp:
        print("    " + line)
    print()
    
    # Show status
    print("-" * 60)
    if not natural_engaged and not sharp_engaged:
        print("STATUS: FLAT - Both discs disengaged (9/3 o'clock)")
        print("        String vibrates at full length")
        print("        Pitch: FLAT")
    elif natural_engaged and not sharp_engaged:
        print("STATUS: NATURAL - Natural disc engaged (6/12 o'clock)")
        print("        Prongs pinch string from above and below")
        print("        String effective length SHORTENED")
        print("        Pitch: NATURAL")
    elif natural_engaged and sharp_engaged:
        print("STATUS: SHARP - Both discs engaged (6/12 o'clock)")
        print("        Both sets of prongs pinch string")
        print("        String effective length SHORTENED MORE")
        print("        Pitch: SHARP")
    print("=" * 60)

def animate_lever_cycle():
    """Animate a complete lever cycle"""
    
    print("Starting lever animation...")
    print("Press Ctrl+C to stop")
    print()
    time.sleep(2)
    
    try:
        while True:
            # Position 0: Flat (\)
            show_disc_position(natural_engaged=False, sharp_engaged=False, lever_pos="\\")
            time.sleep(1.5)
            
            # Transition 0 -> 1: Natural disc engages
            print("\n\n>>> Flipping lever UP: \\ -> |")
            print(">>> Natural chain moves, natural disc rotates 45Â° CW")
            time.sleep(1.0)
            
            # Position 1: Natural (|)
            show_disc_position(natural_engaged=True, sharp_engaged=False, lever_pos="|")
            time.sleep(1.5)
            
            # Transition 1 -> 2: Sharp disc engages
            print("\n\n>>> Flipping lever UP: | -> /")
            print(">>> Sharp chain moves, sharp disc rotates 45Â° CW")
            print(">>> Natural disc HELD by toggle geometry")
            time.sleep(1.0)
            
            # Position 2: Sharp (/)
            show_disc_position(natural_engaged=True, sharp_engaged=True, lever_pos="/")
            time.sleep(1.5)
            
            # Transition 2 -> 1: Sharp disc disengages
            print("\n\n>>> Flipping lever DOWN: / -> |")
            print(">>> Sharp chain reverses, sharp disc rotates back")
            print(">>> Natural disc STILL HELD by toggle")
            time.sleep(1.0)
            
            # Position 1: Natural (|)
            show_disc_position(natural_engaged=True, sharp_engaged=False, lever_pos="|")
            time.sleep(1.5)
            
            # Transition 1 -> 0: Natural disc disengages
            print("\n\n>>> Flipping lever DOWN: | -> \\")
            print(">>> Natural chain reverses, natural disc rotates back")
            time.sleep(1.0)
            
            # Back to flat
            show_disc_position(natural_engaged=False, sharp_engaged=False, lever_pos="\\")
            time.sleep(2.0)
            
            print("\n\n>>> CYCLE COMPLETE - Repeating...")
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\n\nAnimation stopped.")
        sys.exit(0)

def show_single_transition(from_pos, to_pos):
    """Show a single transition between positions"""
    
    positions = {
        'flat': (False, False, '\\'),
        'natural': (True, False, '|'),
        'sharp': (True, True, '/')
    }
    
    if from_pos not in positions or to_pos not in positions:
        print("Invalid position. Use: flat, natural, sharp")
        return
    
    # Show starting position
    nat1, sharp1, lever1 = positions[from_pos]
    show_disc_position(nat1, sharp1, lever1)
    time.sleep(1.5)
    
    # Show transition
    print(f"\n\n>>> Transitioning: {from_pos.upper()} -> {to_pos.upper()}")
    time.sleep(1.0)
    
    # Show ending position
    nat2, sharp2, lever2 = positions[to_pos]
    show_disc_position(nat2, sharp2, lever2)
    time.sleep(2.0)

def main():
    """Main function"""
    
    if len(sys.argv) == 1:
        # No arguments - run full animation
        animate_lever_cycle()
    elif len(sys.argv) == 3:
        # Two arguments - show single transition
        from_pos = sys.argv[1].lower()
        to_pos = sys.argv[2].lower()
        show_single_transition(from_pos, to_pos)
    else:
        print("Usage:")
        print("  python3 lever_animation.py                  # Run continuous animation")
        print("  python3 lever_animation.py flat natural     # Show single transition")
        print()
        print("Valid positions: flat, natural, sharp")
        sys.exit(1)

if __name__ == "__main__":
    main()
