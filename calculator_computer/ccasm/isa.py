"""CCAsm: draft instruction set of the Calculator Computer.

A CCAsm instruction is a short sequence of key presses on the Casio HL-820VA.
The machine model is:

    A   accumulator  = the displayed register X
    M   memory       = the independent memory (M+, M-, MRC)
    K   constant     = the "K" constant, used as a hardware incrementer
    N, E flags       = the MINUS and E indicators on the LCD (readable bits)

Every sequence here is checked against the emulator in tests/test_ccasm.py:
the cost model is only as good as these sequences.
"""

from __future__ import annotations

from dataclasses import dataclass

# ALU class of the work the chip does for one instruction (drives timing)
NONE, ADD, MUL, DIV, SQRT = "none", "add", "mul", "div", "sqrt"


@dataclass(frozen=True)
class Instr:
    mnemonic: str
    template: str      # key sequence; "{n}" is the immediate operand
    alu: str           # heaviest arithmetic the chip performs
    reads_flag: bool = False  # Harness must wait for a stable display
    note: str = ""

    def keys(self, n: str = "") -> str:
        return self.template.format(n=n)

    def key_count(self, digits: int = 0) -> int:
        from ..calculator import parse_keys
        return len(parse_keys(self.keys("9" * digits)))


ISA = {
    "CLR":  Instr("CLR",  "[AC]",                  NONE, note="A=0, op/K cleared, M kept"),
    "LDI":  Instr("LDI",  "[AC]{n}",               NONE, note="A=n"),
    "ADDI": Instr("ADDI", "+{n}=",                 ADD,  note="A=A+n"),
    "SUBI": Instr("SUBI", "-{n}=",                 ADD,  note="A=A-n"),
    "MULI": Instr("MULI", "*{n}=",                 MUL,  note="A=A*n"),
    "DIVI": Instr("DIVI", "/{n}=",                 DIV,  note="A=A/n (truncated)"),
    "LDM":  Instr("LDM",  "[MRC]",                 NONE, note="A=M; HAZARD: two LDM in a row clear M"),
    "ADDM": Instr("ADDM", "+[MRC]=",               ADD,  note="A=A+M"),
    "SUBM": Instr("SUBM", "-[MRC]=",               ADD,  note="A=A-M"),
    "MULM": Instr("MULM", "*[MRC]=",               MUL,  note="A=A*M"),
    "STM":  Instr("STM",  "+[MRC][MRC][C]=[M+]",   ADD,  note="M=A, A kept"),
    "ACM":  Instr("ACM",  "[M+]",                  ADD,  note="M=M+A"),
    "DCM":  Instr("DCM",  "[M-]",                  ADD,  note="M=M-A"),
    "NEG":  Instr("NEG",  "[+/-]",                 NONE, note="A=-A"),
    "SQRT": Instr("SQRT", "[sqrt]",                SQRT, note="A=sqrt(A)"),
    "SETK": Instr("SETK", "[AC]{n}++0=",           ADD,  note="K=+n, A=n"),
    "STEP": Instr("STEP", "=",                     ADD,  note="A=A+K (needs SETK)"),
    "JN":   Instr("JN",   "",                      NONE, True, "jump if MINUS lit (A<0)"),
    "JE":   Instr("JE",   "",                      NONE, True, "jump if E lit (overflow)"),
}
