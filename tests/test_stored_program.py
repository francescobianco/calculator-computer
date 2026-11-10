import unittest

from experiments.stored_program_m import run


class TestStoredProgram(unittest.TestCase):
    def test_countdown_halts_below_zero(self):
        out, _, _ = run("28900000", 5)
        self.assertEqual(out, ["4.", "3.", "2.", "1.", "0.", "-1."])

    def test_collatz_from_6(self):
        out, _, _ = run("47935900", 6, 40)
        integers = [v for v in out if v.endswith(".")]
        # 6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1 (intermediate x.5 values skipped)
        self.assertEqual(integers[:12],
                         ["3.", "3.", "10.", "5.", "5.", "16.", "8.", "4.", "2.", "1.", "1.", "4."])

    def test_powers_of_two(self):
        out, _, _ = run("39000000", 1, 20)
        self.assertEqual(out[:5], ["2.", "4.", "8.", "16.", "32."])

    def test_fetch_keeps_program_and_data(self):
        out, keys, n = run("10000000", 41)  # INC, HALT
        self.assertEqual(out, ["42."])
        self.assertEqual(keys, 2 * 5 + 3)   # two fetches + "+1="


if __name__ == "__main__":
    unittest.main()
