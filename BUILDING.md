# Building, layout and method

## Build and run

Needs gfortran and Python 3 (numpy and Pillow for the checking tools). From a fresh checkout:

```bash
python3 -I tools/build.py .               # ICRM cards + fixes -> src/icrm.f
sh run/mk-icrm.sh                          # port and compile the ICRM (dicrm, icrm_*.o)
python3 -I tools/build.py . --deck dtm     # DTM/OPM cards + fixes -> src/dtm.f
sh run/mk.sh                               # port and compile ddtm, dopm
cd run
./dicrm < icrm-test-deck.txt > icrm.out    # cloud rise (writes jparn.bin)
./ddtm  < dtm-test-deck.txt  > dtm.out     # transport (writes dtm.bin)
./dopm  < opm-test-deck.txt  > opm.out     # map, K factor, activity
grep "K FACTORS\|SUM OF MAP" opm.out       # expect 6.1026E+09 and 0.285554E+05
```

The program has three modules, run in turn: cloud rise (ICRM, the Initialization and Cloud Rise Module), transport (DTM), and the output
processor with the particle activity module (OPM/PAM).

- `tools/build.py .` reports 21 "error lines" for the ICRM deck. They are CDC dialect (`*...*` strings in FORMATs,
  linear subscripts on 2-D arrays), which `tools/port.py` translates; the ported code compiles cleanly.
- `tools/port.py` makes only dialect changes, each logged in `run/port.log`.
- Compile flags: `-std=legacy -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero`. They give
  8-byte words for the CDC 6600's 60-bit ones, and static locals as on the CDC.
- A clean clone, built this way, reproduces `run/icrm.out`, `run/dtm.out` and `run/opm.out` byte for byte.

## Repository layout

| Path | Contents |
|---|---|
| `src/icrm.f`, `src/dtm.f` (+ `.map`) | the transcribed decks; each `.map` gives the PDF page and line of every source line |
| `run/` | ported code, drivers, the test decks, our outputs, comparisons with the printed output |
| `final/`, `merged/`, `ocr*-*/` | per-line OCR of three local models, the vote, and the final card images |
| `corrections.tsv`, `cardfix.tsv`, `rename*.tsv`, `inserts.tsv` | hand readings and code-card fixes |
| `tables/`, `tablefix.tsv`, `pamfix.tsv` | the DATA tables (decay constants, branchings, exposure-rate multipliers, yields) and their fixes |
| `native/`, `lines/` | the 300-dpi page scans (from the public PDF) and the fitted card grid per line |
| `review-sheets/`, `review/` | the proof and hand-check sheets that decided close readings |
| `tools/` | the transcription and checking tools |
| `run/period-data/` | comparisons with the 1968 tape, Crocker 1967 and ENDF/B-IV, and the scripts that made them |
| `run/yield-model/`, `run/k-residual/` | how the 1979 yield table was built; activity and sensitivity tests (`alt.py`) |
| `NOTES.md` | the full history and method |
| `JUDGEMENT-CALLS.txt` | every reading decided from context rather than the glyph alone, with its evidence |
| `CHANGELOG-2026-10-21.md` | the values changed during the last checking round, old → new |
| `CHANGELOG-2026-10-22.md` | DTM/SETTLE misreads found against ORNL's typed listing (TM-2022/2602), old → new |
| `OPEN-QUESTIONS.md` | what is still uncertain |

## How the transcription was checked

- **Reading:** each printed line was read by three local OCR models and voted on, and every disagreement was read
  by hand. Every code line was then proofread on sheets that show the scan with the transcription underneath.
- **Compiling and running:** compiling found the gross errors. Running the test problem found the subtle ones:
  misread variable names that still compile, and broken digits in the data.
- **Data tables:** checked against physics and period sources. Each decay constant should be exactly ln 2 divided
  by a round half-life. Branching fractions must sum to one, and decay chains must stay within their mass number.
  The yields follow the table's own generating rule. The values were also compared with the 1968 data tape,
  Crocker 1967 and ENDF/B-IV.
- **Close calls:** shown on hand-check sheets with samples of every digit from the same page, and read on a second
  printed copy.

## Which files are under which licence

The MIT licence ([LICENSE-CODE](LICENSE-CODE)) covers the code we wrote:
- `tools/`;
- the `*.py` and `*.sh` files under `run/`;
- the Fortran drivers `run/driver.f`, `run/dtm_driver.f`, `run/opm_driver.f` and `run/cdclib.f`;
- the helper programs `run/yield-model/bt.f`, `run/period-data/dumpn.f` and `run/k-residual/resp.f`.

Everything else (the transcription, data, notes and pictures) is under CC BY 4.0 ([LICENSE](LICENSE)).
