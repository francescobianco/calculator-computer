"""Stored program in the calculator memory M (see docs/stored-program.md).

The program is an 8-digit number kept in M, one instruction per digit.
A simulated Harness runs the fetch cycle on the emulated HL-820VA:

    ++      save A into the constant K
    MRC     show M on the display, read digit number PC
    0=      restore A (0 + K)

then executes the micro-code of the opcode as key presses.

Run from the repository root:  python3 -m experiments.stored_program_m
"""

from __future__ import annotations

from calculator_computer.calculator import CasioHL820VA, parse_keys

# opcode digit -> key sequence (micro-code ROM of the Harness)
MICRO = {
    "0": "HALT",
    "1": "+1=",      # INC
    "2": "-1=",      # DEC
    "3": "*2=",      # DBL
    "4": "/2=",      # HALF
    "5": "*3+1=",    # 3N+1
    "6": "[sqrt]",   # SQRT
    "7": "SKNI",     # skip next if A is not an integer (decimal point flag)
    "8": "SKN",      # skip next if A < 0 (MINUS flag)
    "9": "LOOP",     # PC = 0
}

FETCH_SAVE, FETCH_READ, FETCH_RESTORE = "++", "[MRC]", "0="


def load_sequence(program: str) -> str:
    """Key sequence that writes `program` into M (M assumed already 0)."""
    return f"[AC]{program}[M+][AC]"


def run(program: str, a: int | str, max_steps: int = 100):
    """Execute `program` from M starting with A = a.

    Returns (displayed values after each executed instruction, keys pressed,
    instructions executed).
    """
    c = CasioHL820VA()
    c.run(load_sequence(program) + str(a))
    pc, keys, executed, skip = 0, 0, 0, False
    out: list[str] = []
    for _ in range(max_steps):
        c.run(FETCH_SAVE + FETCH_READ)
        op = c.state()["digits"][pc]["char"]
        c.run(FETCH_RESTORE)
        keys += len(parse_keys(FETCH_SAVE + FETCH_READ + FETCH_RESTORE))
        pc += 1
        if skip:
            skip = False
            continue
        executed += 1
        micro = MICRO[op]
        if micro == "HALT":
            break
        if micro == "LOOP":
            pc = 0
        elif micro == "SKNI":
            skip = not c.state()["digits"][7]["dp"]
        elif micro == "SKN":
            skip = c.state()["indicators"]["MINUS"]
        else:
            keys += len(parse_keys(micro))
            c.run(micro)
            out.append(c.state()["text"])
        if pc >= 8:
            break
    return out, keys, executed


EXAMPLES = (
    ("countdown", "28900000", 5),
    ("collatz", "47935900", 6),
    ("powers of 2", "39000000", 1),
)

if __name__ == "__main__":
    for name, prog, a in EXAMPLES:
        out, keys, n = run(prog, a, 40)
        print(f"{name:12} M={prog} A={a}: {' '.join(out[:16])}")
        print(f"{'':12} {n} istruzioni, {keys} tasti, {keys / n:.1f} tasti/istr")
