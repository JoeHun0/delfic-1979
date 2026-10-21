# K-residual analysis (20 Oct 2026)

Tools for hunting activity-scale differences between our OPM run and the printed FP table.

- `resp.f`: BATMAN unit-yield response at H+1 h (692 runs, 50 ms) -> `resp.txt`; links against run/dtm_port.o.
- `bt.f` / `bt3.f`: BATMAN at t~0 (atoms; multiplicity = ABUNDO/ABEGN) and at 3600 s (activity).
- `score.py`: every single-glyph alternative in the yield, ERM and JRM tables, scored by K and per-class shape
  (needs gx.txt and chains.txt from a dtm_port.f patched with WRITE(77/78) in GXPSR; see the patch in fitgrp/score).
- `fitgrp.py`, `fit2c.py`, `units.py`, `pairs.py`, `fitt.py`: group-resolved fits, soil term, natural units, pairs, time shift.
- `side-session-note.md`, `side-session-scripts/`: the side session's hand-over (Rh-109 fix).

Facts established: K is exactly fractionation-independent; the +0.56% residual has the shape of a b=-1 group.
- curv.py: Gaussian-curvature check of true yields (value x path count) per chain; this found the As-83 false head.
- `alt.py` (21 Oct): swap one or more readings in a *scratch copy* of run/ (copy run/*.f *.o *.bin *-test-deck.txt pam-p239he.txt
  printed-opm-checks.txt into <dir>/run first), rebuild, rerun ICRM/DTM/OPM as needed and print K, map sum, FP range and the
  y=27000 map row against print: `python3 -I alt.py <dir>/run "label" dtm_port.f <line> "<old>" "<new>"`. Restore jparn.bin,
  irise.bin, dtm.bin into the copy after an ICRM test. `hist.py printed-cloud-history.tsv <icrm output>` scores a cloud history.
- `../../tools/cellknn.py` (21 Oct): kNN vote of one DATA-table character against the 7444 glyphs of pp. 174-177. Validated on a clear 9, Te-134 (8) and
  I-135 (0). Unreliable on fragments (ink-box normalisation blows them up); check the ink count first.
