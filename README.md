# DELFIC 1979

**The US Department of Defense's nuclear fallout code, brought back from a printed listing and running again.**

DELFIC (Department of Defense Land Fallout Interpretive Code) was the US military's reference model for
radioactive fallout. Given a nuclear explosion and the weather, it calculates how the mushroom cloud rises, how
the radioactive particles drift and settle, and how much radiation they leave on the ground. Through the 1960s
and 70s it served as the reference against which simpler fallout models were checked.

The 1979 version survives only as a printout. Its user's manual reproduces the whole program as about 7,600 lines
of Fortran, printed on a line printer and later scanned:

> H. G. Norment, *DELFIC: Department of Defense Fallout Prediction System, Vol. II — User's Manual*,
> DNA 5159F-2, Atmospheric Science Associates, 1979. DTIC ADA088512, approved for public release.

This project read that printout back into a working program. Every line was read from the scan, checked by hand
where the print was unclear, and compiled with a modern Fortran compiler. The changes are limited to what a
modern compiler needs; the program itself is as printed.

## Does it work?

Yes. The manual includes a worked example, a test explosion with printed results, and the recovered program
reproduces it:

- The fallout map matches the printed map, mostly within one unit in the last printed digit.
- The overall radiation level (the manual's "K factor") is within 0.01% of the printed value.
- The cloud-rise history matches the printed table in 289 of 310 numbers; the rest are digits too faded to read.

The program's data tables (half-lives, decay chains, fission yields) were checked number by number against
documents of the same era: the 1968 version of DELFIC's own data, a 1967 Navy compilation of fission-product decay
chains, the 1974 US nuclear data library (ENDF/B-IV), and Oak Ridge National Laboratory's later documentation of
the 1979 data.

## Faithful to the original

The aim is the program **as it was in 1979**, not an improved one. Mistakes in reading the scan were fixed, each
with evidence. Mistakes the original authors made, such as a few typing slips in the data, a misspelled variable
and some old nuclear data, were kept and documented, because they are part of what the program actually did.
A modernised version would be a separate project.

## You can help

A handful of digits could not be read with certainty, mostly in places where the print is broken. They are listed
in **[OPEN-QUESTIONS.md](OPEN-QUESTIONS.md)**, with pictures of each one. If you have access to a cleaner copy of
the manual (DNA 5159F-2, Vol. II), or to the older reports DELFIC's data came from, a look at those places would
settle them. Please open an issue with what you find.

## Running it

You need a Fortran compiler (gfortran) and Python 3. In short:

```bash
python3 -I tools/build.py . && sh run/mk-icrm.sh
python3 -I tools/build.py . --deck dtm && sh run/mk.sh
cd run
./dicrm < icrm-test-deck.txt > icrm.out
./ddtm  < dtm-test-deck.txt  > dtm.out
./dopm  < opm-test-deck.txt  > opm.out
```

The last step prints the fallout map of the manual's example. **[BUILDING.md](BUILDING.md)** explains each step,
how the repository is organised, and how the transcription was checked. **[NOTES.md](NOTES.md)** tells the full story
of the work.

## Sources

- **The program and its example:** Norment 1979, DNA 5159F-2 Vol. II (DTIC ADA088512).
- **Data checks:** Tompkins 1968, *DELFIC Vol. V: Particle Activity* (DASA-1800-V, DTIC AD0832239); Crocker 1967,
  *Fission Product Decay Chains* (USNRDL-TR-67-111, DTIC AD0659980); ENDF/B-IV (1974), from the IAEA Nuclear Data
  Section; ORNL/TM-2010/220 and ORNL/TM-2022/2602 (Oak Ridge National Laboratory).

These reports are cited, not included, apart from small crops in the hand-check pictures and a list of half-lives
taken from ENDF/B-IV.

## Credit and licence

Transcribed by **Kotnyek József**, with the help of Claude (Anthropic), in October 2026.

You are free to use, share and build on this work, commercially too, **as long as you credit the author**:

- the transcription, data, notes and pictures are under [CC BY 4.0](LICENSE);
- the tools and scripts we wrote are under the [MIT licence](LICENSE-CODE) (see [BUILDING.md](BUILDING.md) for which files).

Suggested credit:

> Kotnyek József (2026). *DELFIC 1979: a transcription of the DoD fallout code from the printed listing.*
> https://github.com/JoeHun0/delfic-1979

The DELFIC program itself was written by its 1979 authors and published in a US government report approved for
public release; these licences cover the transcription work and additions, not the original. The IAEA's
ENDF/B-IV data and the crops of the cited reports should be credited to their sources.
