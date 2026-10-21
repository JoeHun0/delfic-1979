# DELFIC 1979: a transcription of the DoD fallout code from the printed listing

DELFIC (Department of Defense Land Fallout Interpretive Code) is the US government's nuclear fallout
prediction system: cloud rise, particle transport, and the activity and exposure rate on the ground. The
1979 version survives as a line-printer listing in its user's manual:

> H. G. Norment, *DELFIC: Department of Defense Fallout Prediction System, Vol. II — User's Manual*,
> DNA 5159F-2, Atmospheric Science Associates, 31 Dec 1979. DTIC ADA088512, "Approved for public release;
> distribution unlimited."

This repository is a **preservation transcription** of that listing. The whole Fortran source (PDF pp. 55–194,
about 7,600 cards) has been read from the scan, proofread card by card, ported to gfortran with
dialect-only changes, and run. The goal is the **1979 code as it was**, including its own quirks and bugs,
not a modernised model.

## Status (21 Oct 2026)

The full chain, cloud rise (ICRM) → transport (DTM) → output and particle activity (OPM/PAM), reproduces the
manual's printed test problem:

| Quantity | Ours | Printed | Ratio |
|---|---|---|---|
| K factor (R·m²/hr per kt) | 6.1026E+09 | 6.1020E+09 | 1.0001 |
| Sum of fallout-map ordinates | .285554E+05 | .285538E+05 | 1.00006 |
| Activity by particle-size class (FP) | | | 0.9993–1.0001 |
| ICRM cloud history, 310 cells at 4 digits | 289 identical | | rest: faded print |

The data tables were checked cell by cell against period sources: the 1968 DELFIC data tape (Tompkins,
DASA-1800-V), Crocker's 1967 decay chains (USNRDL-TR-67-111), ENDF/B-IV (1974), and ORNL's documentation of the
1979 data (ORNL/TM-2010/220). **A few readings could not be settled from the scan; see
[OPEN-QUESTIONS.md](OPEN-QUESTIONS.md).** If you have a cleaner copy of the volume, those are where help is
most useful.

## Build and run

Needs gfortran and Python 3 (numpy, Pillow for the checking tools).

```bash
python3 -I tools/build.py .               # ICRM cards + fixes -> src/icrm.f
sh run/mk-icrm.sh                          # port and compile the ICRM (dicrm, icrm_*.o)
python3 -I tools/build.py . --deck dtm     # DTM/OPM cards + fixes -> src/dtm.f
sh run/mk.sh                               # port and compile ddtm, dopm
cd run
./dicrm < icrm-test-deck.txt > icrm.out    # cloud rise   (writes jparn.bin)
./ddtm  < dtm-test-deck.txt  > dtm.out     # transport    (writes dtm.bin)
./dopm  < opm-test-deck.txt  > opm.out     # map, K factor, activity
grep "K FACTORS\|SUM OF MAP" opm.out
```

From a fresh checkout, build in this order: `python3 -I tools/build.py .` and `sh run/mk-icrm.sh` (ICRM),
then `python3 -I tools/build.py . --deck dtm` and `sh run/mk.sh` (DTM/OPM).
`tools/build.py .` reports 21 "error lines" for the ICRM deck: these are CDC dialect (`*...*` strings in FORMATs,
linear subscripts on 2-D arrays) that `tools/port.py` translates; the ported code compiles cleanly.
Compile flags: `-std=legacy -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero`
(8-byte words for the CDC 6600's 60-bit ones, static locals as on the CDC).

## What is where

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
| `run/yield-model/`, `run/k-residual/` | how the 1979 yield table was built; tools for activity hunts and sensitivity tests |
| `NOTES.md` | the full history and method |
| `JUDGEMENT-CALLS.txt` | every reading decided from context rather than the glyph alone, with evidence |
| `CHANGELOG-2026-10-21.md` | the values changed during the last checking round, old → new |

## Ground rules of the transcription

- Only our own misreads are fixed, each with evidence: the glyph on the scan, a structural check, another
  period source, and for close calls a reading of a second printed copy.
- The original's own quirks are kept and documented (typing slips in the yield table, `V3AR=VBARC` for
  `VBAR` in TRANP, a chain-index drift between GXPSR and FRATIO, etc.).
- Values that differ from later data are usually what DELFIC actually used, so they are not "updated".
- A reading is never chosen because it brings the result closer to the printed output.

A modernised DELFIC (current nuclear data, fixed bugs) would belong in a separate variant, so that this one
stays the reference.

## Sources and data

- The listing and test problem: DNA 5159F-2 Vol. II (DTIC ADA088512), public release.
- Crocker 1967, USNRDL-TR-67-111 (DTIC AD0659980), public release; cited, not included.
- Tompkins 1968, DASA-1800-V (DTIC AD0832239); cited, not included. Only our readings of its data tape and
  small crops in the review sheets are here.
- ENDF/B-IV fission-product decay data, IAEA Nuclear Data Section (EN4_FP.DAT): `run/period-data/en4-halflives.txt`
  is an extract of its 709 half-lives.
- ORNL/TM-2010/220 and ORNL/TM-2022/2602 (ORNL's documentation and run of the 1979 code): cited, not included.

The transcription and tools were made by Kotnyek József with Claude (Anthropic), Oct 2026. No licence has been
chosen yet for the tools and notes; the transcribed DELFIC code is from a US government report approved for
public release.
