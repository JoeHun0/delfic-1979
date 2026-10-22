# Changes to the DELFIC transcription on 22 Oct 2026

Misreads found by comparing ORNL/TM-2022/2602's typed copy of the 1979 DTM (Listings 1–19) with our decks. Each was checked
on the 300-dpi scan; the evidence is in `JUDGEMENT-CALLS.txt` (22 Oct). The fixes are rows of the "22 Oct 2026" block at the end of `cardfix.tsv`,
plus one edited row each in `cardfix.tsv` (p135 L46), `rename.tsv` and `rename-dtm.tsv`. The backups are `*.bak-ornl2602`. To undo, restore the backups and run
`tools/build.py .`, `tools/build.py . --deck dtm`, `run/mk-icrm.sh` and `run/mk.sh`.

Effect on the test problem: none (K 6.1026E+09, sum of map ordinates .285554E+05; OPM and ICRM output identical; five DTM text lines now read as printed).

| # | Routine | Where (PDF page, line) | Old → new | Fix file |
|---|---|---|---|---|
| 1 | ADVEC | p108 L46 | `.LT. 0.1` → `.LT. 0.0` | cardfix.tsv |
| 2 | ADVEC | p108 L57 | DUMPER arg `J` → `0` | cardfix.tsv |
| 3 | CNTR | p110 L43, p111 L16–24 | `NOBLE` → `NDBLE` | rename-dtm.tsv (old NDBLE→NOBLE rows changed) |
| 4 | NEST | p125 L45 | `NQ=NET(IC,JC)` → `NQ=-NET(IC,JC)` | cardfix.tsv |
| 5 | SPRVS | p130 L27 | `IACCH` → `IACCR` | cardfix.tsv |
| 6 | SPRVS | p131 L4 | `0.,0.,` → `0.,0,` | cardfix.tsv |
| 7 | TRANP | p135 L46 | `301,301,350` → `301,350,350` | cardfix.tsv (row edited) |
| 8 | TRANP | p136 L35, L38 | `GO TO 513` → `GO TO 510`; label `519` → `510` | cardfix.tsv (510→513 row withdrawn) |
| 9 | TRANP | p136 L41 | `1.0E-33` → `1.0E-30` | cardfix.tsv |
| 10 | TRANP | p137 L14 | `ERROR(PROGRM,E1E,ISOUT)` → `616` | cardfix.tsv |
| 11 | TRANP | p137 L19 | `NDATO=NDATO` → `NDATO=NDATC` | cardfix.tsv |
| 12 | SETTLE (ICRM) | p057 L31–49 | `CORR` → `CDRR` (8 cards) | rename.tsv |
| 13 | FORMAT texts | p117 L30/38/60, p118 L3, p121 L52, p123 L29/31, p126 L40, p129 L4/6, p132 L37/42, p134 L50, p139 L11, p142 L54, p143 L8 | CLOLD→CLOUD, FLANE→PLANE, TRANSFORT→TRANSPORT, RATIC CF→RATIO OF, LOACED→LOADED, WINC→WIND, MA)IMUM→MAXIMUM, RAW KIND→RAW WIND, 1HJ→1H0 (×2) and the 8017 text, IMPACTEC→IMPACTED, UPCATE→UPDATE, CFOSSWIND→CROSSWIND, DOWNWINC→DOWNWIND, ZF→ZP, PCINT→POINT, OXSUM/OYSUM→DXSUM/DYSUM | cardfix.tsv |

Open (hand-check sheets `review-sheets/ornl-*.png`, nothing changed yet): TRANP YT/Y1 (p136 L32), V3AR/VBAR (p137 L10), NDTC1=NDATC/NDATO
(p137 L22), label 160/100 (p135 L17, L32), LAYERS 10X/19X (p123 L26), ONEDIN 3X/8X (p126 L46), DUMPER 3X/9X (p119 L26), and the printed
map-sum digit .2855?8 (3 or 0).

`tools/cardsheet.py` gained `--chars` (sample letters instead of digits, e.g. `--chars T1`), and its title line now widens the sheet.
