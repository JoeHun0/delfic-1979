# The printed sum of map ordinates: .285508E+05 (22 Oct 2026)

The book's OPM test output (PDF p. 53) prints `SUM OF MAP ORDINATES = .2855?8E+05` with the 5th digit broken.
It had been read as 3 (.285538). ORNL/TM-2022/2602 reads .285508 and TM-2010/220 .285505; the last digit is a clear 8,
so .285505 does not fit. The user could not decide 3 or 0 on their copy.
The number is only a reference value (no code reads it), but it can be tested against the book's own map.

## Method

- OPM2 adds every map cell into the sum (`201 FSUM=FSUM+OMAP(K)`) and prints every cell with 4 digits. On our own
  run the printed cells add up to 28556.1 against our printed sum 28555.4 (rounding, about ±0.5).
- The map is linear in each size class's activity (CALC: `F=FP(J)*PMAS(IP)/FMASS(J)/SSAM`). `predict.sh` runs our OPM
  with FP overridden by the book's printed FP-by-class table (`book-fp.txt`, 5 digits). This prints the book's map as our
  transport would deposit it: `opm-bookfp.out`, sum **.285518E+05**. Rounding the book FP moves this by ±0.03 (worst case 0.2).
- Whether our transport deposits like the book's was checked cell by cell. ORNL typed the whole book map
  (TM-2022/2602 Listing 23, `ornl-book-map.tsv`). Every large cell (exponent 2–3, 81% of the total) was checked on our
  scan (`scan-verdicts.tsv`):
  - about 76 of 105 print exactly the predicted digits;
  - 13 print one unit higher in the last digit, and 7 one lower;
  - 3 print 2–3 units lower;
  - 11 are unreadable.
  The clear differences cancel (net 0.0). Two gross ORNL misreads were corrected from the scan: 36000 col 2 is 9.043,
  not 9.843, and 27000 col 2 is 9.957, not 9.552.
- `estimate.py` adds it up. The book's sum is 28549.8–28551.3 (±0.5) from the cells, and 28551.8 from the FP table.

## Verdict

| Reading of the 5th digit | Book sum | Fits? |
|---|---|---|
| 3 | 28553.8 | no: 2–4 above every estimate |
| 0 (ORNL) | 28550.8 | yes |
| 1 | 28551.8 | fits the sum, but not the glyph (no stem, no flat foot) |

The printed value is read as **.285508E+05**. Our run's .285554E+05 is then 1.00016 of print, not 1.00006: the reading
makes our match look worse, so it was not chosen to fit. Sheet: `review-sheets/ornl-mapsum-digit.png`.
