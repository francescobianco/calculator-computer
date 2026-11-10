"""python -m calculator_computer         -> finestra grafica (tkinter)
python -m calculator_computer --tui   -> terminale
"""

import sys


def main() -> None:
    if "--tui" in sys.argv[1:]:
        from .cli.repl import main as run
    else:
        try:
            from .cli.gui import main as run
        except ImportError:  # tkinter not installed
            print("tkinter non disponibile, avvio la modalità terminale")
            from .cli.repl import main as run
    run()


if __name__ == "__main__":
    main()
