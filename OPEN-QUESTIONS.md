# Open questions

Readings and facts that could not be settled from our copy of DNA 5159F-2 Vol. II (DTIC ADA088512). Page,
line and field refer to the PDF page and the printed line (see `tables/` and `src/*.map`). None of them
changes the printed test problem at printed precision unless noted, but several matter for other runs
(other fuels, later times). If you have a better copy, or one of the missing sources below, please check them.

## Doubtful characters in the DATA tables

| # | Cell | We read | Alternatives and evidence | Matters for |
|---|---|---|---|---|
| 1 | DCON Sb-129, p176 L20 f1 | 4.195670E-5 (4.589 h) | 4.185670E-5 would be exactly 4.6 h, the 1968 tape's value (glyph vote: 8, 0.67). Crocker 1967 says 4.5 h, ENDF/B-IV 4.34 h. Our value is not an exact ln2/T, which every other DCON is. | Sb-129/Te-129 activity, hours after burst (map sum +0.002% with 8) |
| 2 | DCON In-115m, p175 L56 f3 | 4.268130E-5 | 4th character unreadable (half the ink missing). 8 gives the closest round half-life (16240 s, 4.511 h; 1968: 4.51 h), but no digit gives an exact one. | none at H+1 |
| 3 | ERM Rh-106m, p177 L24 f3 | −8.660000E-6 | 1st and 3rd characters broken; 1968 card 0.86?E-05 confirms 8 and 6; 8.66 or 8.68 open. Rh-106m has no atoms in the test problem, so the output cannot decide. | yield sets that give Rh-106m an independent yield |
| 4 | ERM I-135, p177 L39 f2 | −1.560000E-5 | 4th character unreadable; the 1968 card has only 3 digits (0.156E-04). 0 fits the print best; a glyph vote says 0. | K: 1.565 would add 0.01% |
| 5 | ERM Ba-142, p177 L42 f4 | −4.950000E-6 | Only the bottom edge of the 4th character survives. Every ERM on the page is x.xx0000, and 1968 has 0.495. | negligible |
| 6 | BOIL(11), p185 L32 (FRATIO DATA card) | 1650.0 | The 1968 report's copy of the same card prints 1656.0, and a glyph vote says 6; our reader and all OCR read 1650. | only runs whose solidification temperature lies between 1650 and 1656 K |

Sheets showing each of these with digit samples from the same page are in `review-sheets/` (`dcon-recheck.png`,
`dcon-in115m.png`, `erm-*.png`, `boil-*.png`; for the DTM code cards below, `ornl-*.png`).

## Doubtful characters in the DTM code (from the ORNL listing cross-check, 22 Oct 2026)

ORNL/TM-2022/2602 prints its own typed copy of the 1979 DTM. Where it and our reading disagree and the scan cannot
decide, we kept our reading. None of these is reached by the test problem (one met cell, homogeneous winds).

| # | Card | We read | Alternatives and evidence | Matters for |
|---|---|---|---|---|
| 9 | TRANP p137 L22 | `626 NDTC1=NDATC` | The last glyph is nearly gone. ORNL reads `NDATO`, which with the next card's clear `NDTO1=NDATC` stores the crossed pair for the oscillation test. | channelling |
| 10 | TRANP p135 L17, L32 | label and `GO TO` 160 | The middle glyph is broken in both. Most OCR runs and ORNL read 100. | none (consistent pair) |
| 11 | LAYERS p123 L26, ONEDIN p126 L46, DUMPER p119 L26 | `10X`, `//3X`, `1 3X` | ORNL reads 19X, 8X and 9X. The ONEDIN wind header uses 8X over the same data format, and SPRVS's copy of DUMPER's FORMAT 8024 prints 9X. | printed column layout only |

## Other open points

- **The printed sum of map ordinates** (PDF p. 53) is .2855?8E+05 with the 5th digit broken. We read 3 (.285538). ORNL
  quotes .285508 (TM-2022/2602) and .285505 (TM-2010/220). The last digit is a clear 8. With 0, our run is 1.00016 of print.

- **The last 0.01% of K** (6.1026E+09 against 6.1020E+09; map sum 1.00006). It could be one more misread table
  cell, the CDC's 60-bit arithmetic, or the printed K itself (its third digit is a broken 0; the printed FP
  table sums to 6.1022E+09).
- **21 of 310 cloud-history cells** differ from print (`run/compare-cloud-history.tsv`). Most are faded print
  digits; the late-row rates are differences of nearly equal numbers and may reflect CDC versus IEEE arithmetic
  (untested).
- **About ten P239HE yield cells** break the table's otherwise exact generating rule (`run/yield-model/README.md`).
  They read clearly on the scan and are kept as printed (hand-set in the original?).
- **Ge-77** is 11.30 h in 1979 and 11.33 h on the 1968 tape. Both are exact ln2/T values, so this looks like a
  real revision; a 1970s source would confirm it.

## Missing sources that would help

- Weaver, Strom and Killeen 1963, USNRDL-TR-633 (the yields DELFIC's tables derive from).
- Crocker 1963, USNRDL-TR-642, and Crocker and Turner 1965, USNRDL-TR-1009.
- Tompkins 1971, *Sensitivity Analysis of the DELFIC Particle Activity Module*, BRL 1523 (AD 880619); only a
  catalogue entry has been found.
- A second scan of DNA 5159F-2 Vol. II, especially pp. 174–182 (the DATA tables) and 205–207 (the yields).
