# Velocità di esecuzione delle istruzioni CCAsm

**CCAsm** è il linguaggio macchina del Calculator Computer: un'istruzione
CCAsm è una breve sequenza di pressioni di tasti sulla Casio HL-820VA,
generata dal Harness. Questo documento stima quante istruzioni CCAsm al
secondo può eseguire la macchina.

Codice: `calculator_computer/ccasm/isa.py` (istruzioni) e
`calculator_computer/ccasm/timing.py` (modello dei tempi).
Per rigenerare le tabelle: `python3 -m calculator_computer.ccasm.timing`.

## 1. Ipotesi di partenza

Ipotesi iniziale del progetto: un'istruzione CCAsm costa in media **4–5
operazioni** della calcolatrice. Per verificarla serve prima sapere quali
tasti compongono ciascuna istruzione.

## 2. Il modello di macchina

| Risorsa CCAsm | Dove sta nella calcolatrice |
|---|---|
| `A` accumulatore | registro visualizzato (X) |
| `M` memoria | memoria indipendente (`M+`, `M−`, `MRC`) |
| `K` incrementatore | costante K (operatore premuto due volte) |
| flag `N` | indicatore del segno meno sull'LCD (`A < 0`) |
| flag `E` | indicatore di errore/overflow |

## 3. Bozza di set di istruzioni

Ogni sequenza è verificata sull'emulatore da `tests/test_ccasm.py`.

| Istr. | Tasti | N. tasti | Effetto |
|---|---|---|---|
| `CLR` | `AC` | 1 | A=0 |
| `LDI n` | `AC n` | 1+cifre | A=n |
| `ADDI n` | `+ n =` | 2+cifre | A=A+n |
| `SUBI n` | `− n =` | 2+cifre | A=A−n |
| `MULI n` | `× n =` | 2+cifre | A=A×n |
| `DIVI n` | `÷ n =` | 2+cifre | A=A÷n |
| `LDM` | `MRC` | 1 | A=M |
| `ADDM` | `+ MRC =` | 3 | A=A+M |
| `SUBM` | `− MRC =` | 3 | A=A−M |
| `MULM` | `× MRC =` | 3 | A=A×M |
| `STM` | `+ MRC MRC C = M+` | 6 | M=A, A resta invariato |
| `ACM` | `M+` | 1 | M=M+A |
| `DCM` | `M−` | 1 | M=M−A |
| `NEG` | `+/−` | 1 | A=−A |
| `SQRT` | `√` | 1 | A=√A |
| `SETK n` | `AC n + + 0 =` | 5+cifre | K=+n, A=n |
| `STEP` | `=` | 1 | A=A+K |
| `JN` | nessuno | 0 | salta se il segno meno è acceso |
| `JE` | nessuno | 0 | salta se `E` è acceso |

Due cose emerse costruendo la tabella:

- **`STM` è l'istruzione più cara (6 tasti).** La calcolatrice non ha un
  tasto "memorizza". Per scrivere A in M bisogna mettere A in sospeso come
  operando (`+`), azzerare la memoria (`MRC MRC`), riportare la cifra a zero
  (`C`), ricalcolare A (`=`) e infine sommarlo alla memoria vuota (`M+`).
- **Hazard su `LDM`.** Due `LDM` consecutivi diventano `MRC MRC`, e la
  seconda pressione **azzera** la memoria. Il Harness (o l'assemblatore)
  deve impedirlo, come un hazard di pipeline in una CPU vera.

I salti costano zero tasti: il Harness legge un bit già presente sul display
e sceglie la prossima istruzione. Devono però aspettare che il display sia
stabile.

## 4. Tempi di una pressione di tasto

Il chip non vede il tasto nell'istante in cui si chiude il contatto. Scandisce
la matrice della tastiera periodicamente (di solito in sincronia con il
multiplexing dell'LCD) e accetta il tasto solo dopo averlo visto stabile per
alcune scansioni (debounce). Poi deve vederlo rilasciato prima di accettare
il successivo.

```text
t_tasto = (scansioni_debounce + scansioni_rilascio) × t_scansione
t_istr  = n_tasti × t_tasto + t_ALU + (t_osservazione se legge un flag)
```

`t_ALU` dipende dall'operazione: i chip economici lavorano in BCD una cifra
alla volta con un clock lento, per cui moltiplicazione, divisione e radice
sono molto più lente della somma.

| Parametro | veloce | nominale | lento |
|---|---|---|---|
| periodo di scansione | 5 ms | 10 ms | 16 ms |
| scansioni debounce + rilascio | 2 + 1 | 3 + 2 | 3 + 2 |
| **tempo per tasto** | **15 ms** | **50 ms** | **80 ms** |
| tasti al secondo | 66,7 | 20 | 12,5 |
| ALU somma / molt. / div. / radice | 2 / 10 / 15 / 40 ms | 5 / 30 / 50 / 120 ms | 10 / 80 / 120 / 300 ms |
| attesa di un frame LCD stabile | 16 ms | 32 ms | 64 ms |

**Questi valori non sono misurati.** Sono intervalli plausibili per un chip
CMOS da calcolatrice. Vanno sostituiti con misure sull'esemplare in Phase 5.
Il modello resta lo stesso: cambiano solo i numeri in `SCENARIOS`.

## 5. Risultati

Tempi per istruzione con operandi immediati di 2 cifre:

| Istr. | Tasti | veloce | nominale | lento |
|---|---|---|---|---|
| `CLR`, `LDM`, `NEG` | 1 | 15 ms | 50 ms | 80 ms |
| `STEP`, `ACM`, `DCM` | 1 | 17 ms | 55 ms | 90 ms |
| `SQRT` | 1 | 55 ms | 170 ms | 380 ms |
| `ADDM`, `SUBM` | 3 | 47 ms | 155 ms | 250 ms |
| `MULM` | 3 | 55 ms | 180 ms | 320 ms |
| `ADDI`, `SUBI` | 4 | 62 ms | 205 ms | 330 ms |
| `DIVI` | 4 | 75 ms | 250 ms | 440 ms |
| `STM` | 6 | 92 ms | 305 ms | 490 ms |
| `JN`, `JE` | 0 | 16 ms | 32 ms | 64 ms |

### Media su un programma tipico

Mix di istruzioni ipotizzato (`MIX` in `timing.py`): 30% aritmetica
immediata, 28% traffico con la memoria (`LDM`, `ADDM`, `SUBM`, `ACM`), 10%
`STM`, 13% salti, il resto `LDI`, `STEP`, `CLR`, `MULI`, `DIVI`.

| Scenario | Tasti/istr. | ms/istr. | **CCAsm al secondo** | al minuto |
|---|---|---|---|---|
| veloce | 2,79 | 46 | **21,7** | 1305 |
| nominale | 2,79 | 149 | **6,7** | 402 |
| lento | 2,79 | 244 | **4,1** | 246 |

### Confronto con l'ipotesi 4–5 tasti

Con il set di istruzioni attuale la media è **2,8 tasti per istruzione**,
quindi sotto l'ipotesi. L'ipotesi 4–5 resta un buon **limite superiore
prudente**, e diventa realistica se:

- gli operandi immediati sono più lunghi (ogni cifra è un tasto);
- il programma usa molto `STM` (6 tasti);
- servono tasti in più per evitare l'hazard di `LDM`;
- il Harness aggiunge un tasto di "sincronizzazione" per istruzione
  (per esempio un `C` per ripartire da uno stato noto).

Con 4–5 tasti e scenario nominale si ottengono **3,9–4,9 CCAsm/s**.

**Stima di lavoro: circa 4–7 istruzioni CCAsm al secondo**, con un
intervallo plausibile di 4–22 a seconda dei tempi reali del chip.

## 6. Ordine di grandezza storico

| Macchina | Anno | Somma | Moltiplicazione |
|---|---|---|---|
| Harvard Mark I | 1944 | ~0,3 s | ~6 s |
| Zuse Z3 | 1941 | ~0,8 s | ~3 s |
| **Calculator Computer (nominale)** | — | ~0,2 s (`ADDI`) | ~0,2 s (`MULI`) |

Il Calculator Computer si colloca vicino ai primi calcolatori
elettromeccanici, con 8 cifre decimali per operando (circa 26 bit). La
moltiplicazione costa quasi come la somma perché la fa il chip in hardware;
il costo vero è la tastiera.

## 7. Dove si guadagna velocità

1. **La tastiera è il collo di bottiglia**: il tempo dei tasti pesa circa il
   94% del totale nello scenario nominale (2,79 × 50 ms su 149 ms). Ridurre i tasti per istruzione
   conta più di qualsiasi altra cosa.
2. **Usare la costante K**: `STEP` fa un'operazione aritmetica completa con
   un solo tasto. I cicli di conteggio dovrebbero sempre passare da `K`.
3. **Tenere i valori in A e M** invece di ricaricare immediati.
4. **Evitare `STM`** dove basta `ACM` su una memoria già azzerata.
5. **Misurare la pressione minima accettata**: se il chip accetta 2
   scansioni invece di 3, il tempo per tasto scende del 20%.

## 8. Prossimi passi

- Aggiungere all'emulatore la temporizzazione di pressione e rilascio
  (PLAN, Phase 1), così il Harness simulato sarà vincolato agli stessi tempi.
- Scrivere un assemblatore CCAsm che controlli l'hazard di `LDM`.
- Misurare in Phase 5: periodo di scansione, scansioni di debounce, tempi
  ALU per somma, moltiplicazione, divisione e radice.
