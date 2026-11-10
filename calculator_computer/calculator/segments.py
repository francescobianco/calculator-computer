"""7-segment encoding of the LCD.

Bit order: a b c d e f g (bit 0 = a)::

     aaa
    f   b
     ggg
    e   c
     ddd   .dp

These bits are what the Harness will eventually "see" on the SEG/COM lines,
so they are part of the emulator's output, not just a rendering detail.
"""

from __future__ import annotations

SEG = {
    " ": 0b0000000,
    "0": 0b0111111, "1": 0b0000110, "2": 0b1011011, "3": 0b1001111,
    "4": 0b1100110, "5": 0b1101101, "6": 0b1111101, "7": 0b0000111,
    "8": 0b1111111, "9": 0b1101111,
}
# "6" with segment a and "9" with segment d (tailed digits) match common
# Casio LCDs; whether "7" also lights segment f must be checked on the unit.

SEGMENT_NAMES = "abcdefg"


def seven_segments(text: str, digits: int = 8) -> list[dict]:
    """Turn ``"-0.3333333"`` into 8 right-aligned cells.

    Each cell is ``{"char", "segments", "dp"}``; the minus sign is a separate
    indicator on the HL-820VA and does not use a digit.
    """
    cells: list[dict] = []
    for ch in text.replace("-", ""):
        if ch == ".":
            if not cells:
                cells.append({"char": "0", "dp": False})
            cells[-1]["dp"] = True
        else:
            cells.append({"char": ch, "dp": False})
    while len(cells) < digits:
        cells.insert(0, {"char": " ", "dp": False})
    return [
        {"char": c["char"], "segments": SEG.get(c["char"], 0), "dp": c["dp"]}
        for c in cells[-digits:]
    ]


def lit(segments: int) -> str:
    """Names of the lit segments, e.g. ``lit(SEG['1']) == 'bc'``."""
    return "".join(n for i, n in enumerate(SEGMENT_NAMES) if segments >> i & 1)
