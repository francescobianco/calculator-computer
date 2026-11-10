"""Tkinter front panel for the Casio HL-820VA emulator.

The LCD is drawn from the 7-segment bits returned by the emulator, the same
signals the Harness will read, so what you see is the emulator's real output.
"""

from __future__ import annotations

import tkinter as tk

from ..calculator import CasioHL820VA, LABELS, LAYOUT
from ..calculator.segments import lit

BODY = "#2b2d31"
FACE = "#3a3d42"
LCD_BG = "#b8c4a8"
LCD_ON = "#1d2418"
LCD_OFF = "#aab79b"
KEY_NUM = "#e9e9e6"
KEY_FN = "#5a5e66"
KEY_AC = "#c8553d"
TEXT_DARK = "#1b1b1b"
TEXT_LIGHT = "#f2f2f2"
PANEL = "#1f2023"

KEYBOARD = {
    **{str(d): str(d) for d in range(10)},
    ".": ".", ",": ".", "+": "+", "-": "-", "*": "*", "x": "*", "/": "/",
    "=": "=", "Return": "=", "KP_Enter": "=", "%": "%", "r": "sqrt",
    "BackSpace": "C", "Escape": "AC", "Delete": "AC", "m": "MRC",
    "p": "M+", "n": "M-", "s": "+/-",
    "KP_Add": "+", "KP_Subtract": "-", "KP_Multiply": "*", "KP_Divide": "/",
    "KP_Decimal": ".", **{f"KP_{d}": str(d) for d in range(10)},
}

# segment polygons for one digit cell, in a 30 x 52 box (a..g)
_W, _H, _T = 30, 52, 5
_SEGS = {
    "a": [(4, 0), (26, 0), (22, _T), (8, _T)],
    "b": [(_W, 2), (_W, 24), (_W - _T, 22), (_W - _T, 6)],
    "c": [(_W, 28), (_W, 50), (_W - _T, 46), (_W - _T, 30)],
    "d": [(4, _H), (26, _H), (22, _H - _T), (8, _H - _T)],
    "e": [(0, 28), (0, 50), (_T, 46), (_T, 30)],
    "f": [(0, 2), (0, 24), (_T, 22), (_T, 6)],
    "g": [(3, 26), (8, 23.5), (22, 23.5), (27, 26), (22, 28.5), (8, 28.5)],
}


class FrontPanel:
    TICK_MS = 1000

    def __init__(self, root: tk.Tk) -> None:
        self.calc = CasioHL820VA()
        self.root = root
        root.title("Casio HL-820VA — Calculator Computer emulator")
        root.configure(bg=PANEL)
        root.resizable(False, False)

        outer = tk.Frame(root, bg=PANEL, padx=16, pady=16)
        outer.pack()

        body = tk.Frame(outer, bg=BODY, padx=14, pady=14, bd=0)
        body.grid(row=0, column=0, sticky="n")

        tk.Label(body, text="CASIO", fg=TEXT_LIGHT, bg=BODY,
                 font=("Helvetica", 13, "bold")).pack(anchor="w")
        tk.Label(body, text="HL-820VA", fg="#9ea3ab", bg=BODY,
                 font=("Helvetica", 8)).pack(anchor="e")

        self.lcd = tk.Canvas(body, width=330, height=86, bg=LCD_BG,
                             highlightthickness=3, highlightbackground="#15171a")
        self.lcd.pack(pady=(6, 14))

        keys = tk.Frame(body, bg=BODY)
        keys.pack()
        for r, row in enumerate(LAYOUT):
            for c, key in enumerate(row):
                if key.isdigit() or key == ".":
                    bg, fg = KEY_NUM, TEXT_DARK
                elif key == "AC":
                    bg, fg = KEY_AC, TEXT_LIGHT
                else:
                    bg, fg = KEY_FN, TEXT_LIGHT
                b = tk.Button(
                    keys, text=LABELS.get(key, key), width=4, height=1,
                    font=("Helvetica", 14, "bold"), bg=bg, fg=fg,
                    activebackground=bg, relief="raised", bd=2,
                    command=lambda k=key: self.press(k),
                )
                b.grid(row=r, column=c, padx=4, pady=4)

        # research panel: hidden registers and key trace
        side = tk.Frame(outer, bg=PANEL, padx=16)
        side.grid(row=0, column=1, sticky="ns")
        tk.Label(side, text="Registri interni", fg=TEXT_LIGHT, bg=PANEL,
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.regs = tk.Label(side, justify="left", fg="#c9d1c0", bg=PANEL,
                             font=("Courier", 10), anchor="w")
        self.regs.pack(anchor="w", pady=(4, 12))
        tk.Label(side, text="Trace tasti", fg=TEXT_LIGHT, bg=PANEL,
                 font=("Helvetica", 11, "bold")).pack(anchor="w")
        self.log = tk.Text(side, width=34, height=16, bg="#141517", fg="#c9d1c0",
                           font=("Courier", 9), bd=0)
        self.log.pack(anchor="w")
        tk.Label(side, justify="left", fg="#7d838c", bg=PANEL, font=("Helvetica", 8),
                 text="Tastiera: cifre . + - * / = %  Invio(=)\n"
                      "Backspace=C  Esc=AC  m=MRC  p=M+  n=M-\n"
                      "r=√  s=+/−").pack(anchor="w", pady=(8, 0))

        root.bind("<Key>", self._on_key)
        self.refresh()
        root.after(self.TICK_MS, self._tick)

    def press(self, key: str) -> None:
        self.calc.press(key)
        s = self.calc.state()
        self.log.insert("end", f"{key:>5}  ->  {s['text'] or '(spenta)'}\n")
        self.log.see("end")
        self.refresh()

    def _on_key(self, event: tk.Event) -> None:
        key = KEYBOARD.get(event.keysym) or KEYBOARD.get(event.char)
        if key:
            self.press(key)

    def _tick(self) -> None:
        was_on = self.calc.on
        self.calc.tick(self.TICK_MS)
        if was_on and not self.calc.on:
            self.log.insert("end", "  auto power off\n")
            self.refresh()
        self.root.after(self.TICK_MS, self._tick)

    def refresh(self) -> None:
        s = self.calc.state()
        cv = self.lcd
        cv.delete("all")
        ind = s["indicators"]
        for i, (name, label) in enumerate((("M", "M"), ("K", "K"), ("E", "E"), ("MINUS", "−"))):
            cv.create_text(14, 12 + i * 19, text=label, anchor="w",
                           font=("Helvetica", 10, "bold"),
                           fill=LCD_ON if ind[name] else LCD_OFF)
        x0, y0 = 36, 17
        for i, cell in enumerate(s["digits"]):
            ox = x0 + i * 36
            on = set(lit(cell["segments"]))
            for name, pts in _SEGS.items():
                cv.create_polygon([(ox + px, y0 + py) for px, py in pts],
                                  fill=LCD_ON if name in on else LCD_OFF, outline="")
            cv.create_oval(ox + 31, y0 + 48, ox + 35, y0 + 52, outline="",
                           fill=LCD_ON if cell["dp"] else LCD_OFF)
        r = s["internal"]
        k = f"{r['k'][0]} {r['k'][1]}" if r["k"] else "-"
        self.regs.configure(text=(
            f"X (display) {r['x']}\n"
            f"Y (operand) {r['y']}\n"
            f"op pendente {r['op'] or '-'}\n"
            f"costante K  {k}\n"
            f"memoria M   {r['memory']}\n"
            f"entry       {r['entry'] if r['entry'] is not None else '-'}"
        ))


def main() -> None:
    root = tk.Tk()
    FrontPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
