# Piano di lavoro

Questo piano traduce `IDEA.md` in passi concreti. Linguaggio: **Python 3.12,
solo libreria standard** (nessuna dipendenza), test con `unittest`, interfaccia
grafica con `tkinter`.

## Decisioni prese

| Decisione | Scelta | Motivo |
|---|---|---|
| Calcolatrice di riferimento | **Casio HL-820VA** (in Europa HL-820VER) | Economica, diffusissima, si compra ovunque; vedi `docs/calculator-model.md` |
| Linguaggio | Python | Richiesta del progetto; aritmetica esatta con `fractions`, prototipazione rapida |
| Aritmetica | `Fraction` esatta + troncamento a 8 cifre | Riproduce il troncamento Casio senza errori di virgola mobile |
| Livello di emulazione | Comportamentale (Logical Mode) | Come previsto da IDEA §7.1; l'Electrical Mode viene dopo |
| Uscita display | Bit dei 7 segmenti per cifra + indicatori | Sono i segnali che il Harness leggerà davvero |

## Stato

- [x] Phase 0 (parziale): scelta della calcolatrice e confini Core/Harness.
- [x] Phase 1 (prima versione): emulatore HL-820VA con 25 test.
- [ ] Phase 2: simulatore Harness.
- [ ] Phase 3: calcolo autonomo.
- [ ] Phase 4: minimizzazione.
- [ ] Phase 5: modello fisico.
- [ ] Phase 6: prototipo.

## Phase 0: formalizzazione

1. Scrivere `docs/architecture.md`: l'interfaccia tra Core e Harness è
   **solo** `press(key)` / rilascio verso il core e `digits` + `indicators`
   verso il Harness. Il Harness non legge mai `internal`.
2. Definire le metriche di IDEA §10 come codice (`metrics.py`) così ogni
   esperimento le stampa nello stesso formato.
3. Definire cosa conta come "Harness computation": ogni bit di stato e ogni
   porta del circuito esterno vengono contati automaticamente dal simulatore.

## Phase 1: emulatore (fatto, da raffinare)

Fatto:
- `calculator_computer/calculator/hl820va.py`: macchina a stati, registri
  X/Y, operatore in sospeso, costante K, memoria, errori, auto power off.
- `calculator_computer/calculator/segments.py`: codifica a 7 segmenti.
- `tests/test_hl820va.py`: 25 test, uno per ogni comportamento documentato.
- Interfaccia grafica (`python -m calculator_computer`) e da terminale (`--tui`).

Da fare:
1. **Temporizzazione dei tasti**: oggi `press()` è istantaneo. Servono
   pressione e rilascio separati, una durata minima di pressione e un ritardo
   tra pressione e aggiornamento del display (parametri da misurare in Phase 5).
2. Separatori delle migliaia sul display (segmenti in più).
3. Profilo configurabile per i punti marcati **[F]** e **[V]** nel modello,
   così da poter cambiare comportamento senza riscrivere la macchina a stati.
4. Esplorazione automatica della macchina a stati (IDEA §4.3): generare
   sequenze di tasti e cercare stati con lo stesso display ma comportamento
   diverso. Prima candidata già nota: `5` digitato e `5` come risultato.

## Phase 2: simulatore Harness

1. Motore a eventi discreti con tempo intero (µs) e coda di priorità:
   deterministico e riproducibile.
2. Primitive di IDEA §7.3: `WIRE NOT AND OR NAND NOR XOR MUX LATCH DFF TIMER
   EDGE_DETECTOR KEY_SWITCH`.
3. Adattatori:
   - `SegmentProbe(cell, segment)`: un bit dal display.
   - `IndicatorProbe("K")`: un bit da un indicatore.
   - `KeySwitch("=")`: chiude un contatto della tastiera finché l'ingresso è alto.
4. Rilevazione di oscillazioni (stesso stato globale che si ripete in tempo
   zero) e di pressioni multiple simultanee non valide.
5. Tracciamento nel formato di IDEA §13 (`T=0040 KEY(=)` / `DISPLAY(2)`).

## Phase 3: Experiment 001, contatore autonomo

Su questa calcolatrice la soluzione candidata è molto piccola, grazie alla
costante K:

1. Inizializzazione `AC 1 + + 0 =` (consentita come sequenza di avvio).
2. Da qui il Harness deve solo premere `=` ripetutamente.
3. Circuito minimo candidato: un oscillatore (TIMER) che pilota `KeySwitch("=")`.
   Zero bit di stato esterni, nessuna lettura del display.
4. Versione retroazionata: il cambio di un segmento della cifra delle unità
   (EDGE_DETECTOR) fa ripartire il TIMER. Il clock viene così dalla
   calcolatrice e non da un oscillatore libero.

Poi:
- **Experiment 002, ciclo con reset**: rilevare una cifra precisa (per esempio
  il segmento che distingue `9`) e attivare `AC`. Va verificato quanti
  segmenti servono per riconoscere in modo univoco la condizione.
- **Experiment 003, branching**: usare l'indicatore `E` (overflow) o il segno
  `MINUS` come condizione. `MINUS` è un bit singolo, già prodotto dal chip,
  che codifica un confronto `x < 0`: è il candidato più forte per il COMPARE.

## Phase 4: minimizzazione e ricerca automatica

1. Enumerazione esaustiva dei circuiti con ≤ 4 porte e ≤ 2 flip-flop.
2. Funzione di fitness di IDEA §9 con pesi configurabili.
3. Report: per ogni compito, il circuito minimo trovato e le sue metriche.

## Phase 5: esemplare reale

Comprare **una** HL-820VA (o HL-820VER) solo dopo aver ottenuto in simulazione
l'Experiment 001. Lista delle misure in `docs/calculator-model.md` §6.

## Phase 6: prototipo

Solo con logica discreta (CMOS serie 4000 o 74HC), interruttori analogici
(es. 4066) al posto dei tasti, nessun microcontrollore operativo.

## Struttura del repository

```text
calculator_computer/
  calculator/      emulatore HL-820VA e codifica display
  cli/             finestra tkinter e terminale
  harness/         (Phase 2) porte, latch, interruttori
  simulator/       (Phase 2) scheduler a eventi, trace
docs/              piano, modello della calcolatrice, architettura
experiments/       (Phase 3) un file per esperimento
tests/             unittest
```
