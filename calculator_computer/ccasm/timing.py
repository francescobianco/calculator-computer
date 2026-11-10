"""Speed model: how many CCAsm instructions per second?

    t(instr) = keys * t_key + t_alu(class) + (t_observe if it reads a flag)
    t_key    = t_press + t_release
    t_press  = debounce_scans * t_scan      (chip must see the key stable)
    t_release= release_scans  * t_scan      (and see it released)

None of these numbers are measured yet: they are ranges typical of cheap
CMOS calculator chips (slow clock, BCD digit-serial arithmetic, keyboard
scanned in step with the LCD multiplexing). Phase 5 replaces them with
measurements on a real HL-820VA; everything else in this file stays.

Run:  python -m calculator_computer.ccasm.timing
"""

from __future__ import annotations

from dataclasses import dataclass

from .isa import ADD, DIV, ISA, MUL, NONE, SQRT


@dataclass(frozen=True)
class Scenario:
    name: str
    t_scan: float           # ms, keyboard scan period
    debounce_scans: int
    release_scans: int
    t_alu: dict             # ms per ALU class
    t_observe: float        # ms, Harness waits for a stable LCD frame

    @property
    def t_key(self) -> float:
        return (self.debounce_scans + self.release_scans) * self.t_scan


SCENARIOS = (
    Scenario("veloce",  t_scan=5,  debounce_scans=2, release_scans=1,
             t_alu={NONE: 0, ADD: 2,  MUL: 10, DIV: 15,  SQRT: 40},  t_observe=16),
    Scenario("nominale", t_scan=10, debounce_scans=3, release_scans=2,
             t_alu={NONE: 0, ADD: 5,  MUL: 30, DIV: 50,  SQRT: 120}, t_observe=32),
    Scenario("lento",   t_scan=16, debounce_scans=3, release_scans=2,
             t_alu={NONE: 0, ADD: 10, MUL: 80, DIV: 120, SQRT: 300}, t_observe=64),
)

# Typical instruction mix of a small program (counting loops, arithmetic,
# memory traffic, branches). Weights sum to 1. Immediate operands: 2 digits.
MIX = {
    "LDI": 0.05, "ADDI": 0.15, "SUBI": 0.10, "MULI": 0.05, "DIVI": 0.02,
    "LDM": 0.10, "ADDM": 0.10, "SUBM": 0.08, "STM": 0.10, "ACM": 0.05,
    "STEP": 0.05, "JN": 0.12, "JE": 0.01, "CLR": 0.02,
}
IMM_DIGITS = 2


def instr_time(mnemonic: str, sc: Scenario, digits: int = IMM_DIGITS) -> float:
    ins = ISA[mnemonic]
    keys = ins.key_count(digits if "{n}" in ins.template else 0)
    t = keys * sc.t_key + sc.t_alu[ins.alu]
    if ins.reads_flag:
        t += sc.t_observe
    return t


def mix_average(sc: Scenario, mix: dict = MIX) -> tuple[float, float]:
    """Return (average keys per instruction, average ms per instruction)."""
    keys = sum(w * ISA[m].key_count(IMM_DIGITS if "{n}" in ISA[m].template else 0)
               for m, w in mix.items())
    ms = sum(w * instr_time(m, sc) for m, w in mix.items())
    return keys, ms


def report() -> str:
    lines = []
    names = [sc.name for sc in SCENARIOS]
    lines.append("Tempo per tasto (pressione + rilascio):")
    for sc in SCENARIOS:
        lines.append(f"  {sc.name:<9} {sc.t_key:5.0f} ms  -> {1000 / sc.t_key:5.1f} tasti/s")
    lines.append("")
    lines.append(f"{'istr':<5} {'tasti':>5}  " + "  ".join(f"{n:>9}" for n in names) + "   (ms)")
    for m, ins in ISA.items():
        k = ins.key_count(IMM_DIGITS if "{n}" in ins.template else 0)
        ts = "  ".join(f"{instr_time(m, sc):9.0f}" for sc in SCENARIOS)
        lines.append(f"{m:<5} {k:>5}  {ts}")
    lines.append("")
    lines.append("Media pesata sul mix di programma:")
    for sc in SCENARIOS:
        keys, ms = mix_average(sc)
        lines.append(f"  {sc.name:<9} {keys:4.2f} tasti/istr  {ms:6.0f} ms/istr  "
                     f"-> {1000 / ms:5.2f} CCAsm/s  ({60000 / ms:4.0f} al minuto)")
    lines.append("")
    lines.append("Ipotesi 4-5 tasti per istruzione, scenario nominale:")
    sc = SCENARIOS[1]
    for k in (4, 5):
        ms = k * sc.t_key + sc.t_alu[ADD]
        lines.append(f"  {k} tasti: {ms:4.0f} ms/istr -> {1000 / ms:4.2f} CCAsm/s")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
