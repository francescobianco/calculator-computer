import unittest

from calculator_computer.calculator import CasioHL820VA
from calculator_computer.calculator.hl820va import AUTO_POWER_OFF_MS
from calculator_computer.calculator.segments import SEG


def run(seq):
    return CasioHL820VA().run(seq)


class TestArithmetic(unittest.TestCase):
    def test_power_on_shows_zero(self):
        self.assertEqual(CasioHL820VA().state()["text"], "0.")

    def test_immediate_execution_no_precedence(self):
        self.assertEqual(run("12+34=")["text"], "46.")
        self.assertEqual(run("2+3*4=")["text"], "20.")
        self.assertEqual(run("1.5*4=")["text"], "6.")

    def test_negative_result(self):
        s = run("10-25=")
        self.assertEqual(s["text"], "-15.")
        self.assertTrue(s["indicators"]["MINUS"])

    def test_results_are_truncated_not_rounded(self):
        self.assertEqual(run("2/3=")["text"], "0.6666666")
        self.assertEqual(run("1/3=")["text"], "0.3333333")
        self.assertEqual(run("2[sqrt]")["text"], "1.4142135")
        self.assertEqual(run("[sqrt]")["text"], "0.")

    def test_entry_limited_to_8_digits(self):
        self.assertEqual(run("123456789")["text"], "12345678.")
        self.assertEqual(run("0.12345678")["text"], "0.1234567")

    def test_operator_correction(self):
        self.assertEqual(run("8+-3=")["text"], "5.")

    def test_repeated_equals_without_k_does_nothing(self):
        self.assertEqual(run("1+1===")["text"], "2.")

    def test_tiny_results_underflow_to_zero(self):
        self.assertEqual(run("1/10000000=")["text"], "0.0000001")
        self.assertEqual(run("1/10000000/10=")["text"], "0.")


class TestConstant(unittest.TestCase):
    def test_double_operator_sets_k(self):
        c = CasioHL820VA()
        c.run("3++")
        self.assertTrue(c.state()["indicators"]["K"])
        self.assertEqual(c.run("2=")["text"], "5.")
        self.assertEqual(c.run("4=")["text"], "7.")
        self.assertEqual(c.run("=")["text"], "10.")

    def test_constant_multiplication(self):
        c = CasioHL820VA()
        self.assertEqual(c.run("3**2=")["text"], "6.")
        self.assertEqual(c.run("4=")["text"], "12.")
        self.assertEqual(c.run("=")["text"], "36.")

    def test_constant_subtraction_and_division(self):
        self.assertEqual(run("3--10=")["text"], "7.")
        self.assertEqual(run("4//12=")["text"], "3.")

    def test_single_operator_clears_k(self):
        c = CasioHL820VA()
        c.run("3++2=+")
        self.assertFalse(c.state()["indicators"]["K"])

    def test_autonomous_counter_primitive(self):
        # The building block of Experiment 001: after "1 + + 0 =",
        # every "=" press increments the display by one.
        c = CasioHL820VA()
        c.run("1++0=")
        seen = [c.state()["text"]]
        for _ in range(9):
            seen.append(c.press("=")["text"])
        self.assertEqual(seen, [f"{i}." for i in range(1, 11)])


class TestMemory(unittest.TestCase):
    def test_manual_example(self):
        c = CasioHL820VA()
        c.run("8*9[M+]")
        self.assertEqual(c.state()["text"], "72.")
        self.assertTrue(c.state()["indicators"]["M"])
        c.run("5*6[M-]")
        c.run("2*3[M+]")
        self.assertEqual(c.run("[MRC]")["text"], "48.")
        c.press("MRC")
        self.assertFalse(c.state()["indicators"]["M"])
        self.assertEqual(c.run("[MRC]")["text"], "0.")

    def test_memory_survives_ac_and_off(self):
        c = CasioHL820VA()
        c.run("5[M+][AC]")
        self.assertTrue(c.state()["indicators"]["M"])
        c.press("OFF")
        self.assertFalse(c.state()["on"])
        c.press("AC")
        self.assertEqual(c.run("[MRC]")["text"], "5.")

    def test_recalled_memory_is_an_operand(self):
        self.assertEqual(run("7[M+][AC]3+[MRC]=")["text"], "10.")


class TestPercentSignClear(unittest.TestCase):
    def test_percent(self):
        self.assertEqual(run("2500*12%")["text"], "300.")
        self.assertEqual(run("2500*12%+")["text"], "2800.")  # add-on
        self.assertEqual(run("2500*12%-")["text"], "2200.")  # discount
        self.assertEqual(run("12/400%")["text"], "3.")       # ratio
        self.assertEqual(run("480+25%")["text"], "640.")     # mark-up
        self.assertEqual(run("300-250%")["text"], "20.")     # change

    def test_sign_change(self):
        self.assertEqual(run("5[+/-]")["text"], "-5.")
        self.assertEqual(run("5[+/-]+8=")["text"], "3.")

    def test_c_clears_entry_keeps_operation(self):
        self.assertEqual(run("100+5[C]7=")["text"], "107.")


class TestErrors(unittest.TestCase):
    def test_overflow_locks_keys_until_c(self):
        c = CasioHL820VA()
        c.run("99999999+1=")
        s = c.state()
        self.assertTrue(s["indicators"]["E"])
        self.assertEqual(s["text"], "1.")
        c.run("5+")
        self.assertEqual(c.state()["text"], "1.")
        c.press("C")
        self.assertFalse(c.state()["indicators"]["E"])
        self.assertEqual(c.run("*2=")["text"], "2.")

    def test_overflow_shows_leading_digits(self):
        s = run("12345678*100=")
        self.assertTrue(s["indicators"]["E"])
        self.assertEqual(s["text"], "12.345678")

    def test_division_by_zero_and_negative_sqrt(self):
        self.assertTrue(run("5/0=")["indicators"]["E"])
        self.assertTrue(run("4[+/-][sqrt]")["indicators"]["E"])


class TestPowerAndDisplay(unittest.TestCase):
    def test_auto_power_off(self):
        c = CasioHL820VA()
        c.run("5[M+]")
        c.tick(AUTO_POWER_OFF_MS - 1)
        self.assertTrue(c.state()["on"])
        c.tick(1)
        self.assertFalse(c.state()["on"])
        self.assertEqual(c.state()["text"], "")
        c.press("AC")
        self.assertTrue(c.state()["indicators"]["M"])

    def test_off_ignores_keys_except_ac(self):
        c = CasioHL820VA()
        c.run("[OFF]123")
        self.assertFalse(c.state()["on"])

    def test_seven_segments(self):
        d = run("1.5")["digits"]
        self.assertEqual(len(d), 8)
        self.assertEqual((d[6]["char"], d[6]["dp"]), ("1", True))
        self.assertEqual(d[7]["segments"], SEG["5"])
        self.assertEqual(d[0]["segments"], 0)


if __name__ == "__main__":
    unittest.main()
