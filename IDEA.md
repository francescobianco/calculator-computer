# Calculator Computer
## Costruire un computer usando il chip di una calcolatrice economica

**Concept:** trasformare una comune calcolatrice a quattro operazioni in un computer programmabile, sfruttando il suo circuito integrato originale, i registri interni, la memoria, la tastiera e le uscite del display.

**Principio fondamentale:** il chip della calcolatrice deve costituire il nucleo computazionale del sistema. Tutta l'elettronica aggiuntiva, denominata *Harness*, deve essere ridotta al minimo e implementata preferibilmente attraverso collegamenti passivi, retroazioni, porte logiche elementari, latch e flip-flop.

La prima realizzazione sarà interamente simulata. Solo dopo aver dimostrato la fattibilità del modello costruiremo un prototipo fisico.

---

# 1. Visione del progetto

Una calcolatrice economica contiene già una macchina digitale dotata di:

- Un'unità aritmetica.
- Registri interni.
- Una macchina a stati.
- Una memoria operativa per gli operandi.
- Eventualmente una memoria utente (M+, M-, MR, MC).
- Un'interfaccia di ingresso attraverso una matrice di tasti.
- Un'interfaccia di uscita attraverso un display LCD multiplexato.
- Un circuito di controllo temporale.

Normalmente questa macchina esegue soltanto sequenze di operazioni aritmetiche stabilite dall'utente.

L'obiettivo di Calculator Computer è dimostrare che, aggiungendo una rete esterna minimale di retroazione e controllo, sia possibile trasformarla in un sistema autonomo capace di eseguire programmi.

Non vogliamo simulare una CPU usando un microcontrollore nascosto nel circuito di controllo.

Vogliamo invece sfruttare quanto più possibile le capacità computazionali già presenti nel chip originale.

Il progetto esplorerà fino a che punto possiamo spingerci prima che la logica esterna diventi essa stessa il vero processore.

# 2. Filosofia progettuale

## 2.1 Calculator-first computing

La calcolatrice deve svolgere il lavoro computazionale principale.

Il sistema esterno non dovrebbe eseguire aritmetica generale, interpretare un programma complesso o simulare una CPU convenzionale.

L'Harness deve preferibilmente limitarsi a:

1. Rilevare segnali prodotti dalla calcolatrice.
2. Memorizzare piccole quantità di stato.
3. Applicare trasformazioni logiche elementari.
4. Attivare contatti equivalenti ai tasti.
5. Realizzare retroazioni tra uscite e ingressi.
6. Gestire sincronizzazione e temporizzazione.

## 2.2 Minimizzazione dell'elettronica esterna

La complessità del sistema sarà misurata attraverso:

- Numero di componenti esterni.
- Numero di porte logiche.
- Numero di bit di stato esterni.
- Numero di collegamenti.
- Numero di componenti attivi.
- Consumo energetico.
- Capacità computazionale ottenuta.

L'obiettivo non è semplicemente costruire un computer funzionante, ma individuare l'architettura minima che consenta alla calcolatrice di comportarsi come tale.

## 2.3 Nessun microcontrollore operativo

È consentito utilizzare software e microcontrollori durante sviluppo, simulazione, misurazione e debugging.

Tuttavia, nel dispositivo finale, il funzionamento autonomo non dovrà dipendere da Arduino, ESP8266, Raspberry Pi o processori general-purpose esterni.

L'Harness potrà utilizzare logica discreta e semplici circuiti sequenziali.

## 2.4 Feedback come elemento architetturale

Il principio più importante è la retroazione.

Un segnale generato dalla calcolatrice può essere riportato a un ingresso, direttamente quando elettricamente e temporalmente sicuro, oppure attraverso una trasformazione o un elemento di memoria.

In questo modo possiamo costruire:

- Stati persistenti.
- Oscillatori controllati.
- Contatori.
- Latch.
- Flip-flop.
- Macchine a stati finite.
- Sequenze cicliche di operazioni.
- Eventuali meccanismi di branching.

La retroazione non garantisce automaticamente capacità di calcolo universale: occorre individuare le primitive necessarie e dimostrare quali siano effettivamente implementabili.

---

# 3. Architettura generale

Il sistema è formato da due elementi principali.

## 3.1 Calculator Core

È il chip originale della calcolatrice, con la sua elettronica essenziale.

Comprende:

- ALU o circuito aritmetico equivalente.
- Registri numerici.
- Memoria interna.
- Controller della tastiera.
- Controller del display.
- Logica di interpretazione delle operazioni.

Il chip deve rimanere originale.

Non è previsto modificarne il firmware, sostituirlo o emularlo nel dispositivo fisico.

## 3.2 Harness

L'Harness è il circuito esterno che trasforma la calcolatrice in un sistema autonomo.

Possibili componenti:

- Collegamenti tra segnali.
- Diodi.
- Resistenze.
- Transistor.
- MOSFET.
- Porte logiche.
- Multiplexer.
- Latch e flip-flop.
- Contatori elementari.
- Circuiti RC.
- Oscillatori.
- Interruttori analogici per simulare la pressione dei tasti.

I componenti effettivi saranno scelti dopo la simulazione.

L'Harness non deve essere progettato inizialmente come un processore: dobbiamo prima verificare se la struttura interna della calcolatrice consenta di delegarle parte della gestione degli stati.

### Flusso funzionale

```text
              CALCULATOR COMPUTER

       +-----------------------------+
       |                             |
       |       CALCULATOR CORE       |
       |                             |
       |  Registers / ALU / Memory   |
       |                             |
       |     Keyboard Controller     |
       |                             |
       |      Display Controller     |
       |                             |
       +--------------+--------------+
                      |
                 Output Signals
                      |
                      v
       +-----------------------------+
       |                             |
       |           HARNESS           |
       |                             |
       |  Signal detection           |
       |  Elementary logic           |
       |  State / timing             |
       |  Feedback                   |
       |                             |
       +--------------+--------------+
                      |
                 Key Contacts
                      |
                      +-------> Calculator Core
```

L'Harness costituisce un circuito di controllo retroazionato, non necessariamente un processore.

---

# 4. Utilizzare tutta la memoria disponibile

Un obiettivo centrale è sfruttare i registri interni della calcolatrice come risorse computazionali.

## 4.1 Registri impliciti

Una calcolatrice normalmente mantiene informazioni quali:

- Operando corrente.
- Operando precedente.
- Operazione selezionata.
- Risultato parziale.
- Eventuale costante per operazioni ripetute.
- Stato di inserimento numerico.
- Stato dopo il tasto `=`.
- Stato di errore.
- Memoria utente.

Non tutte queste risorse saranno direttamente leggibili o manipolabili: dobbiamo ricostruirne il comportamento osservabile.

Ogni stato identificabile potrebbe costituire una risorsa utile.

## 4.2 Memoria numerica come memoria di stato

Se la calcolatrice possiede una memoria M+, possiamo sperimentare sequenze capaci di modificarla in maniera deterministica.

Esempio:

```text
MC
1
M+
MR
```

Il risultato dovrebbe essere `1`, per i modelli che implementano la normale semantica di queste operazioni.

La memoria potrebbe rappresentare un contatore, un accumulatore o una variabile del programma.

Dobbiamo verificare se possa contribuire anche al controllo del flusso.

## 4.3 Stato nascosto

Due configurazioni interne potrebbero mostrare lo stesso numero sul display ma comportarsi diversamente alla successiva pressione di un tasto.

Esempio concettuale:

```text
Stato A: 5 appena digitato
Stato B: 5 ottenuto come risultato
```

Se il successivo tasto produce comportamenti differenti, abbiamo identificato due stati interni distinguibili.

Questo suggerisce un approccio di ricerca particolarmente interessante: studiare la macchina a stati della calcolatrice, non soltanto la sua aritmetica.

---

# 5. Retroazione e computazione autonoma

## 5.1 Dal display alla tastiera

Il principio elementare è:

```text
OUTPUT -> HARNESS -> INPUT
```

Una condizione rilevata nelle uscite produce una nuova pressione di un tasto.

Questa pressione modifica lo stato interno della calcolatrice, generando nuove uscite.

Il processo può continuare senza intervento umano.

La sfida è evitare che una retroazione immediata produca oscillazioni incontrollate o pressioni continue.

Servono quindi meccanismi di stabilizzazione, temporizzazione e rilevazione degli eventi.

## 5.2 Display LCD come sorgente di segnali

Molte calcolatrici economiche usano display LCD multiplexati.

I segmenti non sono normalmente pilotati da livelli logici statici: il loro stato dipende dalla differenza di tensione variabile nel tempo tra linee SEG e COM.

Per ottenere un bit utilizzabile dall'Harness sarà necessario sperimentare:

- Rilevazione differenziale.
- Campionamento sincronizzato.
- Raddrizzamento o rilevazione di inviluppo, ove applicabile.
- Riconoscimento di segmenti o combinazioni di segmenti.
- Isolamento elettrico per non alterare la forma d'onda originale.

Non dobbiamo necessariamente decodificare tutto il display.

Potrebbe essere sufficiente rilevare un singolo segmento, una cifra o un indicatore particolare.

Questa ottimizzazione potrebbe ridurre enormemente l'Harness.

## 5.3 Stati lunghi e memoria attraverso retroazione

Una rete retroazionata con elementi bistabili può conservare informazioni anche dopo che il segnale che le ha generate è scomparso.

Possiamo sperimentare circuiti come:

```text
DISPLAY CONDITION
        |
        v
     SET LATCH
        |
        v
    PRESS KEY
        |
        v
 CALCULATOR STATE
        |
        +----> RESET LATCH
```

Questo consente di separare un evento osservato dalla pressione del tasto che esso genera.

Dobbiamo distinguere tre elementi:

- Stato mantenuto internamente dalla calcolatrice.
- Stato mantenuto dall'Harness.
- Stato mantenuto dall'interazione retroazionata tra i due.

La terza categoria è probabilmente la più interessante.

---

# 6. Computazione e controllo del flusso

Il problema centrale non è eseguire somme o moltiplicazioni.

È realizzare un meccanismo capace di selezionare autonomamente operazioni differenti in base allo stato corrente.

Per questo servono primitive equivalenti a:

```text
LOAD
STORE
ADD
SUB
COMPARE
BRANCH
LOOP
```

La calcolatrice fornisce già alcune operazioni aritmetiche.

Dobbiamo capire quali altre funzioni possano emergere dalle sue transizioni di stato e dalla retroazione.

## 6.1 Primo obiettivo: contatore autonomo

Un primo esperimento potrebbe essere un contatore che incrementa un valore senza intervento umano.

Sequenza desiderata:

```text
0 -> 1 -> 2 -> 3 -> 4 -> ...
```

La realizzazione dipenderà dalla semantica della calcolatrice selezionata.

Alcuni modelli supportano operazioni ripetute con `=`, che potrebbero ridurre la sequenza necessaria.

Il programma iniziale potrebbe essere:

```text
INITIALIZE
REPEAT_ADD
REPEAT_ADD
REPEAT_ADD
...
```

L'Harness dovrà generare pressioni distinte e riconoscere quando la calcolatrice ha completato ciascuna operazione.

## 6.2 Secondo obiettivo: ciclo condizionale

Il passo successivo sarà un contatore che cambia comportamento quando raggiunge una determinata condizione.

Esempio:

```text
0 -> 1 -> 2 -> 3 -> 0 -> 1 ...
```

Il controllo può essere ottenuto rilevando un particolare risultato sul display e attivando una sequenza di reset o reinizializzazione.

Il sistema non deve necessariamente implementare una comparazione numerica completa.

Potrebbe essere sufficiente riconoscere una condizione rappresentata da pochi segnali fisici.

## 6.3 Terzo obiettivo: programma con branching

Vogliamo dimostrare che il sistema può scegliere fra almeno due percorsi computazionali.

```text
         STATE
           |
       CONDITION
         /   \
       YES   NO
        |     |
      PATH A PATH B
         \   /
          NEXT
```

La condizione dovrà dipendere da uno stato prodotto dalla calcolatrice, non soltanto da un contatore autonomo nell'Harness.

## 6.4 Quarto obiettivo: macchina programmabile

Solo dopo aver ottenuto i primitivi precedenti valuteremo la costruzione di un'architettura dotata di:

- Un formato di programma.
- Una memoria di istruzioni minimale.
- Un sistema di sequenziamento.
- Un meccanismo di esecuzione.
- Ingresso e uscita.
- Ripetizione condizionale.

L'obiettivo di lungo periodo sarà valutare la possibilità di implementare una macchina universale, eventualmente attraverso un modello computazionale minimale.

Questa proprietà dovrà essere dimostrata, non presunta.

---

# 7. Simulazione prima dell'hardware

L'intero progetto inizierà in un repository software.

**Non compreremo componenti e non costruiremo circuiti prima di aver verificato almeno un comportamento autonomo interessante nella simulazione.**

## 7.1 Emulatore della calcolatrice

Il primo componente sarà un emulatore comportamentale di una calcolatrice economica a quattro operazioni.

Dovrà riprodurre:

- Pressioni e rilasci dei tasti.
- Sequenze di input.
- Registri numerici.
- Operazioni aritmetiche.
- Memoria M+, M-, MR, MC, quando disponibile.
- Stato interno.
- Risultati sul display.
- Temporizzazione delle operazioni.
- Eventuale comportamento delle operazioni ripetute.

Inizialmente useremo un modello comportamentale astratto, non l'emulazione transistor-per-transistor di un chip specifico.

È importante non confondere i due livelli: un comportamento dimostrato nel simulatore generico non garantisce che sia riproducibile su qualunque calcolatrice reale.

## 7.2 Modello dei segnali fisici

L'emulatore avrà due modalità.

**Logical Mode**

Espone direttamente le informazioni logiche del display e gli eventi della tastiera.

Serve a sperimentare rapidamente algoritmi e reti di retroazione.

**Electrical Mode**

Modella l'interfaccia fisica della calcolatrice, almeno a livello di segnali temporizzati:

- Linee COM.
- Linee SEG.
- Scansione della tastiera.
- Pressione e rilascio dei contatti.
- Multiplexing.
- Ritardi.
- Debounce.
- Possibili conflitti di pilotaggio.

Questa modalità è indispensabile prima di passare alla realizzazione fisica.

Non è necessario partire con un simulatore analogico completo. Una simulazione digitale a eventi discreti sarà sufficiente per studiare gran parte della logica, mentre le interfacce analogiche critiche dovranno essere verificate separatamente.

## 7.3 Simulatore Harness

Il secondo componente permetterà di costruire circuiti esterni utilizzando primitive elementari.

Componenti iniziali:

```text
WIRE
NOT
AND
OR
NAND
NOR
XOR
MUX
LATCH
DFF
TIMER
EDGE_DETECTOR
KEY_SWITCH
```

L'ambiente dovrà supportare:

- Connessioni tra porte.
- Retroazioni.
- Circuiti sequenziali.
- Stati persistenti.
- Clock e temporizzazione.
- Analisi dei cicli.
- Rilevazione delle oscillazioni.
- Tracciamento dei segnali.

I componenti passivi analogici saranno rappresentati in una successiva estensione.

## 7.4 Simulazione integrata

L'architettura software prevista:

```text
+-----------------------------------+
|          PROGRAM / TEST           |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|        CALCULATOR EMULATOR        |
|                                   |
|  Arithmetic / State / Memory      |
|  Keyboard / Display / Timing      |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|         SIGNAL INTERFACE          |
+-----------------------------------+
                 |
                 v
+-----------------------------------+
|          HARNESS ENGINE           |
|                                   |
|   Gates / Latches / Feedback      |
+-----------------------------------+
                 |
                 +------> KEYBOARD
```

L'intero sistema dovrà essere deterministico, riproducibile e osservabile.

---

# 8. Struttura iniziale del repository

Nome proposto: `calculator-computer`

```text
calculator-computer/
|
|-- README.md
|-- LICENSE
|-- docs/
|   |-- architecture.md
|   |-- research.md
|   |-- calculator-model.md
|   |-- harness.md
|   |-- experiments.md
|   `-- hardware.md
|
|-- src/
|   |-- calculator/
|   |   |-- core
|   |   |-- registers
|   |   |-- arithmetic
|   |   |-- keyboard
|   |   |-- display
|   |   `-- memory
|   |
|   |-- harness/
|   |   |-- gates
|   |   |-- latches
|   |   |-- flipflops
|   |   |-- switches
|   |   `-- feedback
|   |
|   |-- simulator/
|   |   |-- scheduler
|   |   |-- signal-bus
|   |   |-- events
|   |   `-- tracing
|   |
|   `-- cli/
|
|-- circuits/
|   |-- feedback
|   |-- counter
|   |-- memory
|   `-- branching
|
|-- experiments/
|   |-- 001-keyboard
|   |-- 002-memory
|   |-- 003-repeated-operation
|   |-- 004-display-feedback
|   |-- 005-autonomous-counter
|   `-- 006-conditional-branch
|
|-- tests/
`-- examples/
```

Il linguaggio d'implementazione è ancora da scegliere. C sarebbe interessante per un simulatore leggero e portabile; Rust offrirebbe buone garanzie sul modello di stato, mentre TypeScript faciliterebbe un'interfaccia interattiva.

La scelta deve privilegiare semplicità, determinismo e velocità di sperimentazione.

---

# 9. Ricerca automatizzata delle architetture

Una caratteristica importante sarà la possibilità di esplorare automaticamente diverse configurazioni di Harness.

Invece di progettare manualmente ogni circuito, possiamo costruire un sistema che generi reti logiche candidate e le sottoponga a simulazione.

Per esempio, cerchiamo un circuito che:

1. Inizializzi la calcolatrice.
2. Produca almeno dieci incrementi consecutivi.
3. Non richieda interventi esterni.
4. Utilizzi il minor numero possibile di componenti.
5. Non generi stati elettrici invalidi.
6. Funzioni anche introducendo piccole variazioni temporali.

La funzione obiettivo potrebbe essere:

```text
fitness =
    task_success
    - logic_gate_cost
    - state_bit_cost
    - wiring_cost
    - power_cost
    - timing_risk
```

I pesi dovranno essere configurabili, e il rispetto dei vincoli funzionali ed elettrici sarà prioritario rispetto alla minimizzazione.

Possibili strategie:

- Ricerca esaustiva su circuiti molto piccoli.
- Ricerca combinatoria con pruning.
- SAT/SMT solving.
- Algoritmi genetici.
- Program synthesis.
- Minimizzazione di automi.
- Equivalenza formale tra circuiti.

Questa parte potrebbe diventare uno dei risultati scientificamente più interessanti del progetto: cercare automaticamente il circuito minimo capace di trasformare una macchina non programmabile in una macchina con un determinato comportamento.

---

# 10. Metriche del progetto

Ogni esperimento dovrà produrre dati misurabili.

| Metrica | Descrizione |
|---|---|
| Gate count | Numero di porte logiche esterne |
| State bits | Bit di memoria aggiuntiva |
| Component count | Numero totale di componenti |
| Key events | Pressioni necessarie per operazione |
| Operations/sec | Velocità di esecuzione |
| Feedback depth | Profondità della rete di retroazione |
| Internal memory use | Risorse interne sfruttate |
| Power consumption | Consumo stimato o misurato |
| Autonomy | Operazioni senza input umano |
| Branching capability | Capacità di scelta condizionale |

Vogliamo inoltre distinguere chiaramente:

**Calculator Computation:** operazioni e stati effettivamente prodotti dal chip originale.

**Harness Computation:** operazioni e stati gestiti dalla logica esterna.

Il rapporto tra questi due contributi sarà un indicatore della qualità dell'architettura.

Non sarà però una percentuale assoluta di capacità computazionale: serve soprattutto come strumento comparativo fra soluzioni.

---

# 11. Roadmap

## Phase 0 — Formalizzazione

- Definire i confini tra Calculator Core e Harness.
- Stabilire cosa significa computer programmabile.
- Stabilire quali primitive di controllo sono necessarie.
- Definire criteri oggettivi per distinguere calcolo interno ed esterno.
- Identificare una o più calcolatrici economiche di riferimento.

**Deliverable:** specifica architetturale e modello di calcolo.

## Phase 1 — Calculator Emulator

- Implementare una calcolatrice a quattro operazioni.
- Riprodurre i registri e gli stati.
- Implementare memoria utente opzionale.
- Gestire sequenze di tasti.
- Esporre l'output del display.
- Scrivere test per ogni comportamento.

**Deliverable:** emulatore deterministico con test.

## Phase 2 — Harness Simulator

- Realizzare un motore digitale a eventi discreti.
- Implementare porte logiche e flip-flop.
- Permettere collegamenti retroazionati.
- Collegare output e tastiera della calcolatrice.
- Rilevare oscillazioni e loop instabili.

**Deliverable:** simulatore integrato.

## Phase 3 — Autonomous Computing

- Realizzare una sequenza automatica.
- Sperimentare operazioni ripetute.
- Costruire un contatore autonomo.
- Implementare un ciclo con reset.
- Dimostrare una transizione condizionata dal risultato.

**Deliverable:** primo programma autonomo.

## Phase 4 — Harness Minimization

- Minimizzare le porte.
- Minimizzare i bit esterni.
- Riutilizzare quanto più possibile lo stato interno.
- Individuare segnali del display particolarmente utili.
- Valutare reti di retroazione alternative.
- Introdurre ricerca automatizzata.

**Deliverable:** circuito minimo verificato nel modello.

## Phase 5 — Physical Model

- Selezionare una calcolatrice reale.
- Analizzare la matrice della tastiera.
- Misurare i segnali del display.
- Validare l'eventuale emulatore contro l'hardware.
- Verificare tempi di risposta e livelli elettrici.
- Progettare un'interfaccia di misura non invasiva.

**Deliverable:** specifiche elettriche basate su misure.

## Phase 6 — Hardware Prototype

- Costruire l'Harness.
- Utilizzare componenti economici.
- Evitare microcontrollori operativi.
- Riprodurre gli esperimenti della simulazione.
- Misurare stabilità, autonomia e consumi.

**Deliverable:** Calculator Computer fisico funzionante, almeno per gli esperimenti autonomi dimostrati.

---

# 12. Questioni di ricerca aperte

## Quanto è programmabile una calcolatrice elementare?

La macchina originale possiede una logica di controllo finita, ma manipola anche numeri memorizzati nei registri.

Occorre capire quali comportamenti possano essere ottenuti attraverso sequenze di tasti e retroazione.

## Possiamo ottenere branching sfruttando soltanto il display?

Probabilmente possiamo distinguere alcune condizioni numeriche senza decodificare completamente le cifre.

Per esempio, un particolare segmento o una combinazione di segnali potrebbe identificare un evento utile.

La reale possibilità dipenderà dalla codifica del display e dalla robustezza del circuito di rilevazione.

## Quanta memoria esterna è davvero indispensabile?

Potremmo trovare configurazioni in cui la calcolatrice conserva buona parte dello stato necessario e l'Harness utilizza soltanto uno o due flip-flop.

Questo è uno degli obiettivi prioritari dell'ottimizzazione.

## Possiamo realizzare un sistema senza clock esterno?

Una possibilità è usare i segnali periodici già presenti nella calcolatrice per sincronizzare le operazioni dell'Harness.

In alternativa, il sistema potrebbe adottare un controllo asincrono basato su eventi.

Dobbiamo verificare se ciò sia praticabile senza introdurre instabilità o pressioni spurie.

## Qual è il limite della computazione universale?

Una calcolatrice economica possiede normalmente memoria finita e precisione numerica limitata.

Un sistema fisico con memoria strettamente finita non è una macchina di Turing universale nel senso matematico illimitato.

Possiamo però studiare se l'architettura supporti primitive computazionalmente universali in un modello idealizzato con memoria estensibile, oppure se possa realizzare una CPU finita con un insieme di istruzioni general-purpose.

Questo è un obiettivo teorico distinto dal semplice raggiungimento di cicli autonomi o branching.

---

# 13. Primo esperimento concreto

**Experiment 001 — Autonomous Arithmetic Loop**

Obiettivo: ottenere un circuito simulato che esegua un'operazione aritmetica ripetuta utilizzando il Calculator Core originale del modello.

Vincoli:

- Nessun intervento umano dopo l'avvio.
- Nessuna CPU esterna.
- Nessun interprete di programma nell'Harness.
- Almeno dieci operazioni consecutive corrette.
- Stato interno osservabile.
- Circuito deterministico.
- Numero di componenti esterni misurabile.

Il test dovrà produrre un trace simile a:

```text
T=0000  INIT
T=0010  KEY(1)
T=0020  KEY(+)
T=0030  KEY(1)
T=0040  KEY(=)
T=0050  DISPLAY(2)

T=0060  KEY(=)
T=0070  DISPLAY(3)

T=0080  KEY(=)
T=0090  DISPLAY(4)

...
```

Questa sequenza è soltanto illustrativa: la ripetizione dell'operazione mediante `=` non è uniforme in tutti i modelli e dovrà essere verificata nel profilo della calcolatrice scelta.

L'esperimento avrà successo soltanto se gli eventi KEY successivi all'inizializzazione saranno generati dall'Harness attraverso segnali e stati simulati, non da una lista precostituita di eventi nel test runner.

Dovremo inoltre dimostrare che i risultati numerici provengono dall'emulatore della calcolatrice, non da operazioni aritmetiche eseguite dall'Harness.

---

# 14. Principi non negoziabili

1. **Il chip originale è il cuore del progetto.** Non va sostituito con un microcontrollore.

2. **L'Harness deve essere minimale.** Ogni componente esterno deve avere una funzione giustificata.

3. **Prima si simula, poi si costruisce.** La simulazione deve precedere il prototipo fisico.

4. **La retroazione è una risorsa computazionale.** Non consideriamo il display soltanto un dispositivo per mostrare numeri.

5. **La memoria interna va sfruttata.** Registri, operandi, stati e memoria utente sono risorse da studiare.

6. **Niente CPU nascoste.** Il sistema non deve demandare il calcolo generale a un processore esterno.

7. **Misurare prima di dichiarare.** Autonomia, programmabilità e universalità sono proprietà distinte e devono essere dimostrate separatamente.

8. **L'ottimizzazione è parte della ricerca.** Non basta far funzionare un circuito: dobbiamo cercare di renderlo il più piccolo possibile.

9. **La simulazione deve essere falsificabile.** Ogni comportamento deve essere verificabile con test, trace e, quando disponibile, confronto con una calcolatrice reale.

10. **La semplicità è il risultato principale.** Un Calculator Computer che richiede pochi componenti esterni è più interessante di uno che nasconde un intero processore nell'Harness.

---

# 15. Obiettivo finale

Costruire e documentare un sistema computazionale sperimentale basato su una calcolatrice estremamente economica.

L'esperimento dovrà dimostrare fino a che punto sia possibile convertire un circuito progettato per una funzione specifica in una macchina programmabile mediante l'introduzione di una rete esterna minimale di controllo e retroazione.

La domanda fondamentale del progetto non è:

*Possiamo collegare un microcontrollore a una calcolatrice?*

La domanda è:

**Qual è la minima quantità di logica esterna necessaria per trasformare una calcolatrice non programmabile in un computer autonomo e programmabile?**

Questo sarà il problema centrale di Calculator Computer.

**Project motto:**

*Computing with what is already computing.*
