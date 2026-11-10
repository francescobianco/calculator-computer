"""Every CCAsm instruction must do what it claims on the emulated chip."""

import unittest

from calculator_computer.calculator import CasioHL820VA
from calculator_computer.ccasm import ISA
from calculator_computer.ccasm.timing import SCENARIOS, mix_average


def machine(a="0", m=None):
    c = CasioHL820VA()
    if m is not None:
        c.run(f"{m}[M+]")
    c.run(f"[AC]{a}")
    return c


def run(c, mnemonic, n=""):
    return c.run(ISA[mnemonic].keys(n))


class TestInstructions(unittest.TestCase):
    def test_load_and_immediates(self):
        self.assertEqual(run(machine("5"), "LDI", "42")["text"], "42.")
        self.assertEqual(run(machine("10"), "ADDI", "7")["text"], "17.")
        self.assertEqual(run(machine("10"), "SUBI", "7")["text"], "3.")
        self.assertEqual(run(machine("12"), "MULI", "3")["text"], "36.")
        self.assertEqual(run(machine("10"), "DIVI", "4")["text"], "2.5")

    def test_memory_operands(self):
        self.assertEqual(run(machine("10", m="3"), "ADDM")["text"], "13.")
        self.assertEqual(run(machine("10", m="3"), "SUBM")["text"], "7.")
        self.assertEqual(run(machine("10", m="3"), "MULM")["text"], "30.")
        self.assertEqual(run(machine("1", m="9"), "LDM")["text"], "9.")

    def test_store_keeps_accumulator(self):
        c = machine("7", m="5")
        s = run(c, "STM")
        self.assertEqual(s["text"], "7.")
        self.assertEqual(s["internal"]["memory"], "7.")

    def test_accumulate_into_memory(self):
        c = machine("4", m="5")
        run(c, "ACM")
        self.assertEqual(c.state()["internal"]["memory"], "9.")
        run(c, "DCM")
        self.assertEqual(c.state()["internal"]["memory"], "5.")

    def test_ldm_hazard(self):
        # two LDM in a row are MRC MRC: the second clears the memory
        c = machine("1", m="9")
        run(c, "LDM")
        run(c, "LDM")
        self.assertEqual(c.state()["internal"]["memory"], "0.")

    def test_step_counter(self):
        c = machine()
        run(c, "SETK", "1")
        self.assertEqual(c.state()["text"], "1.")
        for i in range(2, 6):
            self.assertEqual(run(c, "STEP")["text"], f"{i}.")

    def test_flags(self):
        self.assertTrue(run(machine("3"), "SUBI", "5")["indicators"]["MINUS"])
        self.assertTrue(run(machine("99999999"), "ADDI", "1")["indicators"]["E"])


class TestTiming(unittest.TestCase):
    def test_average_keys_within_hypothesis(self):
        # the 4-5 keys/instruction hypothesis is an upper bound for this mix
        keys, _ = mix_average(SCENARIOS[1])
        self.assertTrue(2 <= keys <= 5, keys)

    def test_scenarios_are_ordered(self):
        speeds = [mix_average(sc)[1] for sc in SCENARIOS]
        self.assertEqual(speeds, sorted(speeds))


if __name__ == "__main__":
    unittest.main()
