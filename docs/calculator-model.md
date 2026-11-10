# Calcolatrice di riferimento: Casio HL-820VA

## 1. Perché questo modello

Il progetto richiede una calcolatrice **reale, economica, diffusa e facile da
comprare**, non un modello di comodo. La scelta è la **Casio HL-820VA**:

| Criterio | HL-820VA |
|---|---|
| Diffusione | Una delle tascabili Casio più vendute; in Europa la stessa famiglia è venduta come **HL-820VER** (stessa base, in più i tasti di conversione euro) |
| Prezzo | Circa 5–8 € in cartoleria, supermercati e online |
| Reperibilità | Disponibile nei negozi Casio di tutte le regioni (intl, HK, KR, BR, MEA, ecc.) |
| Complessità | Quattro operazioni, memoria indipendente, √, %, costante "K": abbastanza stato interno da sfruttare, ma niente di superfluo |
| Hardware | Display LCD a 8 cifre multiplexato, una pila LR54 (LR1130), chip tipicamente COB (goccia di resina) |

Specifiche pubblicate da Casio: 8 cifre, memoria indipendente, percentuale,
radice quadrata, alimentazione LR54 × 1, 102 × 57 × 6,9 mm, 35 g.

Se in Phase 5 si dovesse preferire la variante europea, la HL-820VER ha la
stessa semantica di calcolo descritta qui: basta ignorare i tasti euro.

## 2. Fonti

- Pagina prodotto Casio HL-820VA: <https://www.casio.com/intl/basic-calculators/product.HL-820VA/>
- Manuale utente Casio HL-820VER (stessa famiglia): <https://www.manualslib.com/manual/905099/Casio-Hl-820ver.html>
- Nota di supporto Casio sul tasto MRC (prima pressione richiama, seconda azzera).
- Manuali Casio di modelli fratelli (SF-6990, PV-250X) per la procedura della costante.

Non è stato possibile scaricare il PDF del manuale HL-820VA in questa sessione.
Per questo ogni comportamento qui sotto ha un livello di confidenza.

## 3. Tastiera

25 tasti. La disposizione nell'emulatore (`LAYOUT` in
`calculator_computer/calculator/hl820va.py`) è:

```text
[ √ ] [OFF] [MRC] [M− ] [M+ ]
[ % ] [ 7 ] [ 8 ] [ 9 ] [ ÷ ]
[+/−] [ 4 ] [ 5 ] [ 6 ] [ × ]
[ C ] [ 1 ] [ 2 ] [ 3 ] [ − ]
[ AC] [ 0 ] [ . ] [ = ] [ + ]
```

**Da verificare:** l'insieme dei tasti è confermato dalle funzioni dichiarate
da Casio, la loro **posizione fisica** no. La posizione conta solo in Phase 5,
quando si mapperà la matrice elettrica della tastiera (righe e colonne di
scansione). Va fotografato un esemplare e corretto `LAYOUT`.

Il tasto `+/−` è presente sulla SL-300SV e su molte tascabili Casio; sulla
HL-820VA va confermato. Se manca, si toglie dal layout e i test relativi
vanno marcati come non applicabili.

## 4. Comportamenti emulati

Legenda: **[D]** documentato da Casio · **[F]** comportamento standard delle
Casio di base, non ancora confermato sul modello · **[V]** scelta
dell'emulatore da verificare sull'esemplare.

### Display
- 8 cifre, punto decimale, segno meno come indicatore separato. **[D]**
- Indicatori `M` (memoria non nulla), `K` (costante), `E` (errore). **[D]**
- Separatori delle migliaia ogni 3 cifre. **[D]** Non ancora emulati: sono
  segmenti in più che il Harness potrebbe leggere.
- Alla accensione mostra `0.`. **[F]**

### Aritmetica
- Esecuzione immediata, nessuna precedenza: `2 + 3 × 4 =` → `20.` **[F]**
- Risultati **troncati** (non arrotondati) a 8 cifre: `2 ÷ 3 =` → `0.6666666`. **[F]**
- Inserimento limitato a 8 cifre; la nona è ignorata. **[F]**
- Premere un operatore diverso subito dopo un altro corregge l'operatore. **[D]**
- Valori più piccoli di 0.0000001 diventano `0.` **[F]**

### Costante (K)
Procedura Casio: si inserisce il numero costante e si preme **due volte**
l'operatore, appare `K`. **[D]**

| Sequenza | Risultato | Significato |
|---|---|---|
| `3 + + 2 =` | `5.` | x + 3 |
| `4 =` | `7.` | nuova x, stessa costante |
| `=` | `10.` | ripete sul risultato |
| `3 × × 2 =` | `6.` | per × la costante è il moltiplicatore |
| `3 − − 10 =` | `7.` | x − 3 |
| `4 ÷ ÷ 12 =` | `3.` | x ÷ 4 |

Il ruolo della costante per × (primo fattore) e per + − ÷ (secondo operando)
è **[F]**. Senza `K`, ripetere `=` **non** ripete l'operazione: `1 + 1 = = =`
resta `2.` **[V]** (su Citizen e Texas Instruments il comportamento è diverso).

**Conseguenza per il progetto:** `1 + + 0 =` seguito da `=` ripetuti è un
contatore 1, 2, 3, ... che richiede al Harness di premere **un solo tasto**.
È la primitiva su cui costruire l'Experiment 001.

### Memoria indipendente
- `M+` / `M−` sommano o sottraggono il valore visualizzato; se c'è un calcolo
  in sospeso lo completano prima (`8 × 9 M+` → 72 in memoria). **[D]**
- `MRC`: prima pressione richiama, seconda pressione consecutiva azzera. **[D]**
- La memoria sopravvive ad `AC` e allo spegnimento. **[D]**

### Percentuale
| Sequenza | Risultato | Uso |
|---|---|---|
| `2500 × 12 %` | `300.` | percentuale **[D]** |
| `2500 × 12 % +` | `2800.` | maggiorazione **[D]** |
| `2500 × 12 % −` | `2200.` | sconto **[D]** |
| `12 ÷ 400 %` | `3.` | rapporto **[D]** |
| `480 + 25 %` | `640.` | mark-up **[F]** |
| `300 − 250 %` | `20.` | variazione % **[F]** |

Il manuale elenca questi casi; le sequenze esatte di mark-up e variazione
vanno confermate sull'esemplare.

### Cancellazione, errori, alimentazione
- `C` cancella il numero appena inserito, l'operazione in sospeso resta. **[D]**
- `AC` cancella tutto tranne la memoria e accende la calcolatrice. **[D]**
- `OFF` spegne. **[D]** Spegnimento automatico dopo circa 6 minuti. **[D]**
- Errore `E`: tastiera bloccata, `C` toglie l'errore e permette di continuare,
  `AC` azzera. **[D]**
- Overflow: `E` più le prime 8 cifre con la virgola spostata di 8 posti
  (`12345678 × 100 =` → `E 12.345678`). **[F]**
- Divisione per zero e radice di un negativo: `E`. **[V]**

## 5. Uscite per il Harness

Lo stato restituito da `CasioHL820VA.state()` contiene:

- `digits`: 8 celle con i bit dei segmenti `a..g` e il punto decimale.
  Sono i segnali che il Harness dovrà rilevare sulle linee SEG/COM.
- `indicators`: `M`, `K`, `E`, `MINUS`.
- `internal`: registri nascosti (X, Y, operatore, costante, memoria). Servono
  solo alla ricerca; il Harness non deve leggerli perché sul chip reale non
  sono accessibili.

## 6. Cosa resta da misurare sull'esemplare (Phase 5)

1. Foto della tastiera e conferma di `LAYOUT` e del tasto `+/−`.
2. Esecuzione di tutte le sequenze di `tests/test_hl820va.py` e confronto.
3. Forma dei numeri 6, 7, 9 sui segmenti.
4. Matrice della tastiera (piste del circuito stampato).
5. Linee COM/SEG dell'LCD, livelli di tensione, frequenza di multiplexing.
6. Tempo di risposta: dopo quanti ms dalla pressione cambia il display.
7. Durata minima di pressione riconosciuta e comportamento del debounce.
