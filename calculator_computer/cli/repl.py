"""Terminal front end: type key sequences, see the LCD and the internal registers.

    $ python -m calculator_computer --tui
    hl820va> 1++0====
    hl820va> [MRC]

Multi-letter keys go in brackets: [M+] [M-] [MRC] [sqrt] [+/-] [C] [AC] [OFF].
"""

from __future__ import annotations

from ..calculator import CasioHL820VA, parse_keys

ART = {  # 3-line 7-segment art built from the a..g bits
    "a": (0, 1, "_"), "f": (1, 0, "|"), "g": (1, 1, "_"), "b": (1, 2, "|"),
    "e": (2, 0, "|"), "d": (2, 1, "_"), "c": (2, 2, "|"),
}
ORDER = "abcdefg"


def render(state: dict) -> str:
    if not state["on"]:
        return "  [ display spento ]"
    rows = [[" "] * 32 for _ in range(3)]
    for i, cell in enumerate(state["digits"]):
        for bit, name in enumerate(ORDER):
            if cell["segments"] >> bit & 1:
                r, c, ch = ART[name]
                rows[r][i * 4 + c] = ch
        if cell["dp"]:
            rows[2][i * 4 + 3] = "."
    ind = state["indicators"]
    flags = " ".join(n if ind[k] else " " for k, n in
                     (("M", "M"), ("K", "K"), ("E", "E"), ("MINUS", "-")))
    lines = ["".join(r) for r in rows]
    lines[0] = flags.ljust(8) + lines[0]
    lines[1] = " " * 8 + lines[1]
    lines[2] = " " * 8 + lines[2]
    return "\n".join(lines)


def main() -> None:
    calc = CasioHL820VA()
    print(f"{calc.model} — emulatore comportamentale. Ctrl-D per uscire.")
    print("Tasti: 0-9 . + - * / = %  [M+] [M-] [MRC] [sqrt] [+/-] [C] [AC] [OFF]")
    print(render(calc.state()))
    while True:
        try:
            line = input("hl820va> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            keys = parse_keys(line)
            for k in keys:
                calc.press(k)
        except ValueError as exc:
            print(f"  errore: {exc}")
            continue
        s = calc.state()
        print(render(s))
        r = s["internal"]
        print(f"  X={r['x']}  Y={r['y']}  op={r['op']}  K={r['k']}  M={r['memory']}")


if __name__ == "__main__":
    main()
