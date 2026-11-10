# Programma memorizzato nella memoria M

Idea: invece di cablare il programma nel Harness, lo si scrive come **numero**
dentro la memoria indipendente M della calcolatrice. Un compilatore su PC
traduce il sorgente CCAsm in un numero a 8 cifre e nella sequenza di tasti che
lo carica. Il Harness diventa un'unità di controllo fissa che legge le
istruzioni da M ed esegue il loro microcodice.

Verifica: `experiments/stored_program_m.py`, test in
`tests/test_stored_program.py`. Per eseguire gli esempi:
`python3 -m experiments.stored_program_m`.

## 1. Capacità di M

M contiene un solo numero del display a 8 cifre. Il valore massimo è
**99.999.999** (e −99.999.999).

| Cosa si usa | Valori distinti | Bit |
|---|---|---|
| Solo interi 0 – 99.999.999 | 10⁸ | **26,6** |
| Più virgola in qualunque posizione e segno | 1.459.999.999 | **30,4** |

Il conteggio: per ogni numero di decimali p da 0 a 7 i valori sono m/10^p con
|m| < 10⁸; per p > 0 sono nuovi solo quelli con m non multiplo di 10. Il
totale positivo è 729.999.999; con negativi e zero si arriva a 1,46 × 10⁹.

**M contiene al massimo circa 30 bit, meno di 4 byte.** Per confronto lo
Zuse Z3 (1941) aveva 64 parole da 22 bit.

## 2. Quante istruzioni entrano

istruzioni = 30,4 bit ÷ bit per istruzione

| Codici operativi | Bit/istr. | Istruzioni massime |
|---|---|---|
| 16 | 4 | 7 |
| 10 (una cifra) | 3,3 | **8** (9 in teoria) |
| 8 | 3 | 10 |
| 4 | 2 | 15 |
| 3 | 1,6 | 19 |
| 2 | 1 | 30 |

Ridurre i codici operativi allunga il programma ma indebolisce ogni
istruzione: la potenza totale del programma non cresce. Lo schema
**una cifra = un'istruzione** perde solo circa un'istruzione rispetto
all'ottimo teorico e ha un vantaggio decisivo: il Harness legge una cifra dal
display con un multiplexer, senza decodifiche. Una codifica più compatta (per
esempio binaria dentro il numero decimale) richiederebbe divisioni successive
fatte dal chip a ogni istruzione: molti tasti in più e A distrutto.

## 3. Ciclo di fetch

Leggere M richiede `MRC`, che sovrascrive A, l'unico registro di lavoro. La
costante K fa da registro di appoggio:

| Passo | Tasti | Effetto |
|---|---|---|
| salva A | `+ +` | K = A (appare `K`) |
| fetch | `MRC` | il display mostra M; il Harness legge la cifra in posizione PC |
| ripristina A | `0 =` | A = 0 + K = A |

Costo: **5 tasti per istruzione** più il microcodice. Verificato: con A = 42 e
M = 31415926, dopo `++ MRC 0=` A vale di nuovo 42 e M è intatto.

Lo stesso trucco mostra che **K è un registro leggibile**: con K additiva
`0 =` restituisce K, con K moltiplicativa `1 =` restituisce K.

### Harness necessario

- contatore PC a 3 bit (8 posizioni);
- multiplexer che seleziona una delle 8 cifre del display;
- decodificatore da 7 segmenti a codice operativo (10 configurazioni valide);
- ROM di microcodice fissa a 10 voci, che non cambia con il programma;
- lettura di due flag: punto decimale sull'ultima cifra (A intero) e segno meno.

Il programma è software, il Harness è un'unità di controllo microprogrammata
e la calcolatrice fa sia da ALU sia da memoria di programma: è un computer a
programma memorizzato.

## 4. Set di istruzioni a una cifra

| Cifra | Istr. | Microcodice | Effetto |
|---|---|---|---|
| 0 | HALT | nessuno | fine |
| 1 | INC | `+1=` | A = A + 1 |
| 2 | DEC | `−1=` | A = A − 1 |
| 3 | DBL | `×2=` | A = 2A |
| 4 | HALF | `÷2=` | A = A / 2 |
| 5 | 3N+1 | `×3+1=` | A = 3A + 1 |
| 6 | SQRT | `√` | A = √A |
| 7 | SKNI | flag del punto decimale | salta la prossima se A non è intero |
| 8 | SKN | flag del segno meno | salta la prossima se A < 0 |
| 9 | LOOP | nessuno | PC = 0 |

## 5. Programmi verificati

| Programma | M | A iniziale | Uscita | Tasti/istr. |
|---|---|---|---|---|
| Conto alla rovescia | `28900000` | 5 | 4 3 2 1 0 −1, poi HALT | 6,3 |
| Collatz | `47935900` | 6 | 3 10 5 16 8 4 2 1 4 2 1 … | 6,9 |
| Potenze di 2 | `39000000` | 1 | 2 4 8 … 65536 … | 6,5 |

Collatz in 6 istruzioni: `HALF`, `SKNI` (se non intero salta il `LOOP`),
`LOOP`, `DBL` (riporta al dispari), `3N+1`, `LOOP`. Sul display compaiono
anche i passaggi intermedi `1.5`, `2.5`, `0.5`.

Con circa 6,5 tasti per istruzione e 50 ms per tasto (scenario nominale di
`docs/ccasm-speed.md`) la velocità è **circa 3 istruzioni al secondo**.

## 6. Caricamento dal PC

Il compilatore produce:

1. il numero, per esempio `47935900`;
2. la sequenza di caricamento: `MRC MRC` per azzerare M, poi
   `AC 47935900 M+ AC`.

La sequenza si può digitare a mano o inviare tramite gli interruttori del
Harness. I programmi sono numeri: si scrivono su un foglio e si caricano su
qualunque HL-820VA.

## 7. Limiti

- **8 istruzioni**, senza operandi immediati.
- **Nessuna memoria dati libera**: M contiene il programma e K serve al
  fetch; resta solo A. Vanno bene programmi su un solo valore (iterazioni,
  serie, timer, contatori).
- Salti limitati a "salta la prossima" e "ricomincia".
- Il ripristino tramite K esclude l'uso di K come costante nel programma.

## 8. Come andare oltre

- **Segno di M**: 1 bit in più (modalità o pagina).
- **Posizione della virgola in M**: circa 3 bit (lunghezza del programma o
  destinazione di salto).
- **Registri nascosti**: K e l'operando in sospeso valgono 8 cifre
  ciascuno, ma oggi K serve al fetch e l'operando in sospeso viene perso da
  quasi ogni operazione (IDEA.md §4.3).
- **Pagine**: programmi più lunghi come più numeri tenuti nel Harness e
  caricati in M uno alla volta, a costo di memoria esterna.

Anche nel caso migliore la calcolatrice offre 2–3 registri da 8 cifre: i
programmi interamente interni restano nell'ordine delle 8–10 istruzioni.
