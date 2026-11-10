# calculator-computer

Trasformare una calcolatrice economica in un computer programmabile usando il
suo chip originale e il minimo di logica esterna. L'idea completa è in
[IDEA.md](IDEA.md), il piano in [docs/PLAN.md](docs/PLAN.md).

## Calcolatrice di riferimento: Casio HL-820VA

Tascabile Casio a 8 cifre da pochi euro, venduta ovunque (in Europa come
HL-820VER). Ha memoria indipendente, √, %, e la costante `K` (operatore
premuto due volte). Cosa è documentato e cosa resta da verificare su un
esemplare: [docs/calculator-model.md](docs/calculator-model.md).

## Provare l'emulatore

Serve Python 3.10 o successivo, senza altre dipendenze.

```sh
python3 -m calculator_computer          # finestra grafica (tkinter)
python3 -m calculator_computer --tui    # terminale
python3 -m unittest                     # test
```

Su Debian/Ubuntu, se manca tkinter: `sudo apt install python3-tk`.

Da terminale si scrivono sequenze di tasti; i tasti con più lettere vanno tra
parentesi quadre:

```text
hl820va> 1++0=          contatore con costante K: ogni "=" aggiunge 1
hl820va> ===
hl820va> 8*9[M+][MRC]   memoria
```

## Uso come libreria

```python
from calculator_computer.calculator import CasioHL820VA

c = CasioHL820VA()
c.run("1++0=")
c.press("=")["text"]          # '2.'
c.state()["digits"][7]        # {'char': '2', 'segments': 91, 'dp': True}
```

## Licenza

MIT, vedi [LICENSE](LICENSE).
