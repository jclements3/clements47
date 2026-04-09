#!/usr/bin/env python3
r"""
CLEMENTS47 Lever Positions - Side by Side Comparison

Shows all three lever positions and their disc engagements
"""

def show_all_positions():
    """Display all three lever positions side by side"""
    
    print("=" * 80)
    print("CLEMENTS47 - Lever and Disc Engagement Comparison")
    print("=" * 80)
    print()
    
    # Headers
    print("    FLAT (\\)              NATURAL (|)            SHARP (/)")
    print("    " + "-" * 19 + "   " + "-" * 19 + "   " + "-" * 19)
    print()
    
    # Natural disc row
    print("    Natural Disc:         Natural Disc:         Natural Disc:")
    print("                            | o)                  | o)")
    print("      (o|o)                 |                     |")
    print("        |                 (o|                   (o|")
    print("                            |                     |")
    print()
    
    # Sharp disc row  
    print("    Sharp Disc:           Sharp Disc:           Sharp Disc:")
    print("                                                  | o)")
    print("      (o|o)               (o|o)                   |")
    print("        |                   |                   (o|")
    print("                                                  |")
    print()
    
    # Status
    print("    " + "-" * 19 + "   " + "-" * 19 + "   " + "-" * 19)
    print("    Both disengaged       Natural engaged       Both engaged")
    print("    9/3 o'clock           6/12 o'clock          6/12 o'clock")
    print("    String full length    String shortened      String shortest")
    print("    Pitch: FLAT           Pitch: NATURAL        Pitch: SHARP")
    print()
    print("=" * 80)
    print()
    
    # Explain the transitions
    print("TRANSITIONS:")
    print()
    print("  \\ -> |  :  Flip lever UP")
    print("           Natural chain rotates ~45Â° CW")
    print("           Natural disc prongs engage string (6/12 o'clock)")
    print("           Sharp chain stays at rest (toggle dead center)")
    print()
    print("  | -> /  :  Flip lever UP more")
    print("           Sharp chain rotates ~45Â° CW")
    print("           Sharp disc prongs engage string (6/12 o'clock)")
    print("           Natural disc HELD by toggle geometry")
    print()
    print("  / -> |  :  Flip lever DOWN")
    print("           Sharp chain rotates back to 9/3 o'clock")
    print("           Sharp disc disengages")
    print("           Natural disc still held at 6/12 o'clock")
    print()
    print("  | -> \\ :  Flip lever DOWN to rest")
    print("           Natural chain rotates back to 9/3 o'clock")
    print("           Natural disc disengages")
    print("           Both discs at rest")
    print()
    print("=" * 80)

if __name__ == "__main__":
    show_all_positions()
