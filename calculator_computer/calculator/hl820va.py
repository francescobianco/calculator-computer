"""Behavioural emulator of the Casio HL-820VA pocket calculator.

8 digits, independent memory (MRC / M+ / M-), square root, percent,
sign change and constant calculation ("K", operator pressed twice).

This is a LOGICAL model: it reproduces what a user can observe (display,
indicators, key semantics), not the transistors of the chip. Each behaviour
is classified in ``docs/calculator-model.md`` as either documented by Casio
or still to be verified on a physical unit.

Arithmetic is exact (``fractions.Fraction``) until a value is fitted to the
display, where it is truncated toward zero like on basic Casio calculators
(2 / 3 = 0.6666666).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from fractions import Fraction

from .segments import seven_segments

DIGITS = 8
AUTO_POWER_OFF_MS = 6 * 60 * 1000  # "about six minutes" (Casio manual)

OPS = ("+", "-", "*", "/")

# Physical key layout, row by row (see docs/calculator-model.md, section 3).
LAYOUT = (
    ("sqrt", "OFF", "MRC", "M-", "M+"),
    ("%", "7", "8", "9", "/"),
    ("+/-", "4", "5", "6", "*"),
    ("C", "1", "2", "3", "-"),
    ("AC", "0", ".", "=", "+"),
)

KEYS = tuple(k for row in LAYOUT for k in row)

LABELS = {
    "sqrt": "√", "OFF": "OFF", "MRC": "MRC", "M-": "M−", "M+": "M+",
    "%": "%", "/": "÷", "*": "×", "-": "−", "+": "+", "=": "=",
    "+/-": "+/−", "C": "C", "AC": "AC", ".": "·",
}

ZERO = Fraction(0)
HUNDRED = Fraction(100)


class Overflow(Exception):
    pass


def int_digits(v: Fraction) -> int:
    ip = abs(math.trunc(v))
    return 1 if ip == 0 else len(str(ip))


def truncate(v: Fraction, places: int) -> Fraction:
    scale = 10 ** places
    return Fraction(math.trunc(v * scale), scale)


def fit(v: Fraction, digits: int = DIGITS) -> tuple[Fraction, bool]:
    """Fit a value to the display.

    Returns ``(value, overflow)``. On overflow Casio shows the leading digits
    with the decimal point moved 8 places left and the "E" indicator, so the
    returned value is ``v / 10**8`` fitted to the display.
    """
    overflow = False
    if int_digits(v) > digits:
        overflow = True
        v = v / 10 ** digits
        extra = int_digits(v) - digits
        if extra > 0:  # absurdly large: keep the leading digits only
            v = v / 10 ** extra
    return truncate(v, digits - int_digits(v)), overflow


def to_text(v: Fraction) -> str:
    """Render a fitted value the way the LCD shows it: "-12.5", "0.", "48."."""
    neg = v < 0
    v = abs(v)
    ip = math.trunc(v)
    frac = v - ip
    places = 0
    while frac.denominator != 1 and places < 30:
        frac *= 10
        places += 1
    text = str(ip) + "."
    if places:
        text += str(math.trunc(frac)).rjust(places, "0")
    return ("-" if neg else "") + text


def parse_number(text: str) -> Fraction:
    return Fraction(text.rstrip(".") or "0")


def isqrt_trunc(v: Fraction, places: int = 24) -> Fraction:
    scale = 10 ** places
    return Fraction(math.isqrt(math.trunc(v * scale * scale)), scale)


@dataclass
class Constant:
    op: str
    value: Fraction


@dataclass
class TraceEvent:
    t: int
    key: str | None = None
    event: str | None = None


class CasioHL820VA:
    """The calculator. Feed it keys with :meth:`press`, read :meth:`state`."""

    model = "Casio HL-820VA"
    layout = LAYOUT
    keys = KEYS
    labels = LABELS

    def __init__(self) -> None:
        self.memory = ZERO  # independent memory survives AC and OFF
        self.time = 0
        self.trace: list[TraceEvent] = []
        self._power_on()

    # ---------------------------------------------------------------- state

    def _power_on(self) -> None:
        self.on = True
        self.idle = 0
        self._clear_all()

    def _clear_all(self) -> None:
        self.x = ZERO               # displayed register
        self.y = ZERO               # first operand / accumulator
        self.op: str | None = None  # pending operator
        self.k: Constant | None = None  # constant calculation -> "K"
        self.entry: str | None = None   # digits being typed
        self.has_operand = False    # new operand supplied since last operator
        self.error = False
        self.pct: tuple[str, Fraction] | None = None  # context of last %
        self.last_key: str | None = None

    def _set_result(self, v: Fraction | None) -> bool:
        self.entry = None
        if v is None:  # division by zero, sqrt of negative
            self.x = ZERO
            self.error = True
            return False
        self.x, overflow = fit(v)
        if overflow:
            self.error = True
        return not overflow

    @staticmethod
    def _compute(a: Fraction, op: str, b: Fraction) -> Fraction | None:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return None if b == 0 else a / b
        raise ValueError(op)

    def _apply(self, a: Fraction, op: str, b: Fraction) -> bool:
        return self._set_result(self._compute(a, op, b))

    # ------------------------------------------------------------ key input

    def press(self, key: str) -> dict:
        """Press one key (one of :data:`KEYS`) and return the new state."""
        if key not in KEYS:
            raise ValueError(f"unknown key {key!r}")
        self.idle = 0
        self.trace.append(TraceEvent(self.time, key=key))

        if not self.on:
            if key == "AC":
                self._power_on()
            return self.state()

        if self.error and key not in ("AC", "C", "OFF"):
            return self.state()  # keyboard locked until C or AC

        prev, self.last_key = self.last_key, key

        if key.isdigit() or key == ".":
            self._digit(key)
        elif key in OPS:
            self._operator(key, prev)
        elif key == "=":
            self._equals()
        elif key == "%":
            self._percent()
        elif key == "sqrt":
            self._sqrt()
        elif key == "+/-":
            self._change_sign()
        elif key == "MRC":
            self._mrc(prev)
        elif key == "M+":
            self._memory(+1)
        elif key == "M-":
            self._memory(-1)
        elif key == "C":
            self._clear()
        elif key == "AC":
            self._clear_all()
        elif key == "OFF":
            self.on = False
            self._clear_all()
        return self.state()

    def run(self, seq: str | list[str]) -> dict:
        """Press a sequence: a list of keys or a string like ``"12+3="``."""
        keys = parse_keys(seq) if isinstance(seq, str) else seq
        for k in keys:
            self.press(k)
        return self.state()

    def tick(self, ms: int) -> None:
        """Advance simulated time; handles auto power off."""
        self.time += ms
        if not self.on:
            return
        self.idle += ms
        if self.idle >= AUTO_POWER_OFF_MS:
            self.on = False
            self._clear_all()
            self.trace.append(TraceEvent(self.time, event="AUTO_POWER_OFF"))

    def _digit(self, key: str) -> None:
        self.pct = None
        e = self.entry
        if e is None:
            e = "0." if key == "." else key
        elif key == ".":
            if "." not in e:
                e += "."
        elif e in ("0", "-0"):
            e = e.replace("0", key)
        elif len(e.replace("-", "").replace(".", "")) < DIGITS:
            e += key
        self.entry = e
        self.x = parse_number(e)
        self.has_operand = True

    def _operator(self, o: str, prev: str | None) -> None:
        # add-on / discount after "× %": 2500 × 12 % +  -> 2800
        if o in "+-" and prev == "%" and self.pct and self.pct[0] == "*":
            base = self.pct[1]
            self.pct = None
            self._apply(base, o, self.x)
            self.op = None
            self.has_operand = False
            return
        self.pct = None

        if self.op is not None and not self.has_operand:
            if o == self.op and prev == o:
                # operator pressed twice: constant calculation, "K" lights up
                self.k = Constant(o, self.y)
                self.op = None
            else:
                self.op = o  # correcting a wrong operator key
                self.k = None
            return

        if self.op is not None:
            if not self._apply(self.y, self.op, self.x):
                return
        self.y = self.x
        self.op = o
        self.k = None
        self.entry = None
        self.has_operand = False

    def _equals(self) -> None:
        self.pct = None
        if self.k is not None:
            # The constant is the first number entered. For × it is the
            # multiplier (k × x); for + − ÷ it is the second operand (x op k).
            if self.k.op == "*":
                self._apply(self.k.value, "*", self.x)
            else:
                self._apply(self.x, self.k.op, self.k.value)
        elif self.op is not None:
            b = self.x if self.has_operand else self.y
            self._apply(self.y, self.op, b)
            self.op = None
        self.entry = None
        self.has_operand = False

    def _percent(self) -> None:
        if self.op is None:
            return
        a, b, op = self.y, self.x, self.op
        r: Fraction | None
        if op == "*":
            r = a * b / HUNDRED                              # 2500 × 12 %  -> 300
        elif op == "/":
            r = None if b == 0 else a * HUNDRED / b          # 12 ÷ 400 %   -> 3
        elif op == "+":
            r = None if b == HUNDRED else a * HUNDRED / (HUNDRED - b)  # mark-up
        else:
            r = None if b == 0 else (a - b) * HUNDRED / b    # % change
        self.op = None
        self.has_operand = False
        if self._set_result(r):
            self.pct = (op, a)

    def _sqrt(self) -> None:
        self.pct = None
        self._set_result(None if self.x < 0 else isqrt_trunc(self.x))
        self.has_operand = True

    def _change_sign(self) -> None:
        self.pct = None
        if self.entry is not None:
            e = self.entry
            self.entry = e[1:] if e.startswith("-") else "-" + e
            self.x = parse_number(self.entry)
        else:
            self.x = -self.x
        self.has_operand = True

    def _mrc(self, prev: str | None) -> None:
        self.pct = None
        if prev == "MRC":
            self.memory = ZERO  # second consecutive press clears memory
            self.last_key = "MRC:cleared"  # a third press recalls again
            return
        self.x = self.memory
        self.entry = None
        self.has_operand = True

    def _memory(self, sign: int) -> None:
        self.pct = None
        # M+ / M- first complete a pending calculation (8 × 9 M+ -> 72)
        if self.op is not None or self.k is not None:
            self._equals()
            if self.error:
                return
        value, overflow = fit(self.memory + sign * self.x)
        if overflow:
            self.error = True
        else:
            self.memory = value
        self.entry = None
        self.has_operand = False

    def _clear(self) -> None:
        if self.error:
            self.error = False  # clear "E", keep the displayed digits
            self.entry = None
            self.has_operand = True
            return
        self.entry = None
        self.x = ZERO
        self.has_operand = self.op is not None or self.k is not None

    # --------------------------------------------------------------- output

    def display_text(self) -> str:
        if not self.on:
            return ""
        if self.entry is not None:
            t = self.entry if "." in self.entry else self.entry + "."
            return "0." if t == "-0." else t
        return to_text(self.x)

    def state(self) -> dict:
        text = self.display_text()
        return {
            "on": self.on,
            "text": text,
            "digits": seven_segments(text, DIGITS),
            "indicators": {
                "M": self.on and self.memory != 0,
                "K": self.on and self.k is not None,
                "E": self.on and self.error,
                "MINUS": self.on and text.startswith("-"),
            },
            # internal registers, exposed for research (not visible on the LCD)
            "internal": {
                "x": to_text(self.x),
                "y": to_text(self.y),
                "op": self.op,
                "k": None if self.k is None else (self.k.op, to_text(self.k.value)),
                "memory": to_text(self.memory),
                "entry": self.entry,
                "has_operand": self.has_operand,
            },
        }


_TOKEN = re.compile(r"\[([^\]]+)\]|(.)")
_ALIASES = {"x": "*", "×": "*", "÷": "/", "√": "sqrt", "r": "sqrt", "−": "-"}


def parse_keys(text: str) -> list[str]:
    """Parse ``"12+3="``; multi-letter keys go in brackets: ``"5[M+][MRC]"``."""
    out = []
    for word, ch in _TOKEN.findall(text):
        if word:
            out.append(word)
        elif ch.strip():
            out.append(_ALIASES.get(ch, ch))
    return out
