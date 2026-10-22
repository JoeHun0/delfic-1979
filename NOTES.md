# DELFIC 1979, Vol. II (User's Manual) — ICRM transcription pilot

Source: H.G. Norment, *DELFIC: Department of Defense Fallout Prediction System, Vol. II — User's Manual*,
DNA 5159F-2, Atmospheric Science Associates, 31 Dec 1979 (DTIC ADA088512, 233 pp;
`~/new-word/sources/fallout/delfic-1979-vol2-ADA088512/`). Section 5 (PDF pp. 55–194) prints the whole
Fortran source of DELFIC for the CDC 6600 (about 7,600 cards, sequence IDs in columns 73–80). Section 4
(PDF pp. 37–53) is a test problem: the card deck and the printed output.

**Pilot scope (20 Oct 2026): the Initialization and Cloud Rise Module (ICRM)** — PDF pp. 55–107, 23 routines
(TRPL, ERROR, SETTLE, ICRMEX, ICM, AIRBRS, DSTBN, MASS, VAPOR, TEMP, TIMEE, ATMR, SHWIND, CPFR, CRM, CRMINT,
CRMW, CXPN, DBG, DCSN, DERIV, RKGILL, RSTR, RSXP, WNDSFT), 2,818 cards, 1,606 code cards. The transport
(DTM) and output (OPM) modules, PDF pp. 107–194, were transcribed next (see "DTM and OPM" below).

## Result

The transcribed ICRM **compiles with gfortran and reproduces the printed test problem at the printed
precision.** Against the printed test output:

| Quantity | Agreement |
|---|---|
| input echo, atmosphere table (30 levels × 6 columns), particle-size table (30 classes) | identical to every printed digit |
| initial cloud: time 4.35715 s, gas temperature 2629 K, condensed mass .2849E+08 kg, energy fraction .4500 | identical |
| cloud trajectory (XC, YC, ZC, TC) | identical to the 6 printed digits in the early rows |
| cloud history, 31 rows × 10 columns | **289 of 310 cells identical at all 4 printed digits**; same termination (CXPN statement 443, U,EK switch), same final row times |
| soil solidification time | 5.0292 s — identical |

The 21 differing cells (`run/compare-cloud-history.tsv`, last column) are: faded printout digits I could not
resolve (3/8, 0/9, 3/7, 1/4 pairs — rows 2, 17, 22–27), one-unit last-digit differences (top 9072 vs 9073,
density .5804 vs .5803), and rates in rows 26–29, which are differences of nearly equal positions over
30–40 s, so a 0.01% position difference shows in their third digit (plausibly CDC 60-bit vs IEEE double
arithmetic; not tested). No remaining code error is indicated.

**The 0.55% offset (found 20 Oct 2026):** the first build had a 0.55% smaller initial cloud volume. The cause
was one digit on the CRMINT soil-heat card (`SOILHT=SSAM*(…+1.3?1E+7*(1./TPR-1./TE))`, the second digit a
3/8 glyph). CRMINT integrates the soil specific heat that DERIV uses, `CS=781.6+0.5612*T-1.881E7/T**2`, so the
constant is 1.881E+7; with it the printed rows 1, 4 and 28 and the solidification time match to every digit.
(The quadratic term 0.2856 is not exactly 0.5612/2 = 0.2806; testing 0.2806, or 0.5712 in DERIV, makes the
match worse, so both are kept as printed.) Method: instrumenting the energy balance showed the print needs
SOILHT 11.7 kJ/kg lower; the 1.881E7 reading lowers it by 11.9 kJ/kg.

`run/printed-cloud-history.tsv` has the printed table as read from the scan.

## How it was done

1. Page images: the native 300-dpi 1-bit scans (`pdfimages`), 10 skewed pages deskewed (`native-orig/` keeps
   the originals; p089 reverted — rotation broke its line detection).
2. `tools/lines.py`: line and 80-column card grid from the bitmap (character pitch fitted, column 80 = the last
   sequence digit, inked cells per line; touching glyphs split).
3. `tools/ocrlines.py`: each line read by LightOnOCR, dots.ocr and GLM-OCR (local llama.cpp), characters
   placed into the inked cells; `tools/reocr.py` second pass with tighter crops; `tools/merge.py` votes
   per column (AGREE / VOTED / TIE / SINGLE / NONE, comments and page noise separated).
4. 396 flagged lines read by hand from review sheets (`corrections.tsv`, `tools/applyfix.py`; `!` = free
   layout where glyphs touch, `~` = dirt).
5. Compile-driven proofreading (`tools/build.py`): COMMON blocks voted across their 7–15 copies, identifier
   repairs (`rename.tsv`, 150 whole-word renames, each checked in context), card fixes (`cardfix.tsv`, 179,
   made against proof sheets that render the transcription under each scan line — `tools/proof.py`), label
   field letter→digit normalisation. Every code card was proofread on these sheets.
6. Two cards that are missing from the scan (CXPN 59–60, page break) were rebuilt from Vol. I eq. (2.2.14a)
   (`inserts.tsv`).
7. `tools/port.py`: CDC dialect only — `*...*` strings in FORMATs → `'...'`, linear EQUIVALENCE subscripts on
   2-D arrays → 2-D, long lines split. Compiled with
   `gfortran -std=legacy -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero`
   (8-byte REAL and INTEGER ≈ CDC 60-bit words; static locals as on the CDC).
8. `run/driver.f` opens the scratch units and calls ICRMEX; `run/icrm-test-deck.txt` is the test deck
   transcribed from PDF pp. 37–39 (formats as printed: atmosphere `(4F10.0,2F1.0)`, winds
   `(F12.0,24X,2F12.0)`, SCALE(3)=100, SCALE(8)=273.16).

`JUDGEMENT-CALLS.txt` lists the 17 readings decided from context rather than the glyphs (undefined labels,
broken digits, one stray `(1` on a card). Files: `src/icrm.f` (transcription, before porting), `src/icrm.map`
(source line → PDF page/line), `run/icrm_port.f` (compiled), `run/icrm.out` (our test output).

## DTM and OPM (20 Oct 2026)

Transport (DTM) and output processor with the particle-activity module (OPM/PAM), PDF pp. 107–194: 4,820 cards
(`src/dtm.f`, `src/dtm.map`), built with `tools/build.py --deck dtm` and ported with `tools/port.py --deck dtm`.
Run the whole chain with `run/dicrm`, then `run/mk.sh`, then `./ddtm < dtm-test-deck.txt`, then
`./dopm < opm-test-deck.txt`.

**Result.** The end-to-end run reproduces the printed test problem's fallout map (PDF pp. 52–53) cell for cell,
to printed precision (K within 0.01%).
- Map cells agree with print to the last printed digit or so (0.980 before the Rh-109 fix, 1.004 before Sb-122, 1.002–1.007 before As-83).
- The plume shape, extent and zero cells agree.
- The sum of map ordinates is .285554E+05 against a printed .285538E+05 (1.00006).
- The PSIZE table is identical.
- FP is 0.9993–1.0001 of print by class.
- K is 6.1026E+09 against a printed 6.1020E+09 (1.0001).

The DTM printed output (winds, layers, Wilkins turbulence) matches the book. See `run/compare-opm.txt`.

**The 2% activity gap was a missing branch node (20 Oct).** The BRANCH table's entries are consumed in NUCLID order,
`4 - (low octal digit)` per nuclide. The DATA statement says IBRA=128, but the transcribed codes used only 126, and
p174 L43 f2/f3 (0.73/0.27) was an orphan pair. Every pair after the missing node was assigned to the wrong nuclide.
The pair sums stayed 1, which is why the sum check never caught it. Rh-109 (A=109 card p180 L62, rebuilt from faint
print with an assumed 10004) is really 12002, branching to Pd-109m/Pd-109. The scan's last glyphs read ...954. With
the fix the branch fractions become physical (In-115m 0.95/0.05, Cs-137→Ba-137m 0.92, Te-127m IT 0.98, Eu-152
0.73/0.27, ...). The Ag-115m..Cd-121 sets that did not sum to 1 now do. Details are in `JUDGEMENT-CALLS.txt` (Rh-109).

**A branch target in the wrong chain (20 Oct).** Sb-122's code read 20532; its first option then pointed at the A=123 head, so the
whole A=123 chain was walked and counted twice (its yields summed to 219 against 105 and 113 for the neighbours). The
code is 21042 (EC to Sn-122, β⁻ to Te-122), one broken 6/8 glyph away. K 6.1482E+09 → 6.1362E+09. Two structural checks
now pass for every node: branch targets stay in their own mass chain (or A−1 for delayed-neutron codes), and every
nuclide's path multiplicity at t≈0 is an integer that makes the independent yields smooth (`run/k-residual/`).

**A false chain head (21 Oct).** As-83 carried a minus sign that is not on the scan, so the A=83 chain was started twice.
Two independent references on a pendrive the user supplied (copied to `~/glasstone-test-data/other/delfic-ornl/`) made it
findable. ORNL/TM-2010/220 explains that the 1979 yields are divided by the number of decay paths, and that dividing turns
the yields into a check of the decay structure: the true yields (file value × path count) follow one exact Gaussian per
chain, curvature 2·ln 2. A=83 was the only activity-carrying outlier; without the false head it fits exactly.
K 6.1362E+09 → 6.1045E+09 (print 6.1020E+09).

**Cross-checks from ORNL.**
- ORNL/TM-2010/220 tabulates the NUCLID decay-code frequencies; ours match every count. Its 24 listed 1979 ERMs match ours.
- ORNL/TM-2022/2602 ran its electronic copy of the 1979 code on the same deck: K 6.0830E+09, map sum .284241E+05. Its FP is
  a constant 3.2E+07 per class below the book, which is the soil-activation term, so that copy evidently runs without soil
  activity. Ours includes it and is closer to the book.
- The P239HE yield block now totals 18793.05 against 18793.03 for ORNL's TAPE20: the gap was one misread cell
  (Sn-130 .609 for .809, a broken 8), found by a per-cell glyph check and confirmed by the user, with Se-81m, Ge-84 and
  Br-89 corrected in the same hand-check. Reverse-engineering the block (`run/yield-model/`) shows a Gaussian
  charge-dispersion table with a fixed tail rule; the ~10 cells still off the rule are hand-set in the original and carry
  no activity.

**Method for activity hunts.**
- K is exactly ∝ Σ ABUNDO·|ERM| plus soil. Each chain's RADIAL·(1/ECF + CRISS) = 1, and ΣFMASS = 1.
- The per-class FP ratio against print shows which fractionation exponent the missing activity has.
- GXPSR groups chains by negative ERM and FRATIO by mass. ERM has no group for A=80/98/110/113/114, so from chain 9
  on, each chain uses a lighter mass's BSUBK. That is original: the print's shape matches only with the drift.

**Semantic misreads that compiled cleanly and were found by running.** These are on top of the
compile-driven proofreading. Each was checked on the scan.
- ICRM RSXP: `KOPS` for `KDPS`, so the wafer loop never ran and there were no parcels.
- TRANP: `Z0` for `ZO`, so the parcel altitude was never set.
- ADVEC: `CXSLM`/`NDATO` for `DXSUM`/`NDATU`.
- CALC: `-8*YREL**2+0` for `-B*YREL**2+D`, the contribution ellipse.
- BATMAN: `R=0.0` for `B=0.0`; `SBR+SCA` for `SBR*SCA`; `MULT(2)` (smeared) taken as `MULT(1)`.
- FRATIO: `MULT(9)` for `MULT(6)`.
- OPM1: `SLDTMP`/`TMSO` spelled differently from the rest of the deck, so the condensation temperature and
  solidification time were zero.
- PAM1 `J=1,632` for 692; PCHECK `YPAR(IF)`; OPM2 `CLROT=0.9` for `0.0`, a broken zero.
- NUCLID: two 8→6 slips (Se-84, Sm-159). The Sm-159 one made BATMAN loop on itself.

Kept as printed:
- `V3AR=VBARC` in TRANP is an original bug (reopened 22 Oct: ORNL's typed listing reads `VBAR=VBARC`; on a hand-check sheet).
- TRANP's dummy `XC`.
- `ZSCL=HOB/W**(1.0/3.4)`.

All of these are in `JUDGEMENT-CALLS.txt`.

**Tools added.**
- `tools/unset.py --setonly`: names assigned but never read.
- `tools/tables.py` and `tools/tcheck.py`: DATA-card reader and physics checks.

Hunting the residual: set NPRNT flags in the OPM deck (card 3, 8L1, explicit F's because gfortran rejects
blank L fields), dump GXPSR terms, and compare against print.

## Cross-check: NBS SP 570 (Spencer et al. 1980), pp. 131–133 (21 Oct 2026)

SP 570 (now in `~/new-word/sources/shelter/nbs-sp570-1980-structure-shielding/`) describes the 1966–70 DELFIC
(DASA-1800 Vols I–VII), not the 1979 code, and only qualitatively. It agrees with the 1979 structure:
- Five modules (Initial Conditions, Cloud Rise, Transport, Particle Activity, Output Processor). In 1979 the first two
  are one deck (ICRM) and PAM sits inside OPM.
- Cloud rise after Huebsch, oblate spheroidal cloud; wafers whose upper and lower boundaries are followed separately.
  This is what the RSXP fix restored (`KDPS=2*KDPST`: two boundary records per wafer, MBT = top/bottom indicator).
- Transport in nested meteorological cells (NET/NETSU, NEST); modified Freiling radial distribution; induced activity.
- It gives the soil melting temperatures (siliceous ~1673 K, calcareous ~2887 K). The 1979 code instead uses
  solidification temperatures, defaults 2200 K / 2800 K, a different quantity; nothing to change.
Its ref. [33], Tompkins 1971, *Sensitivity Analysis of the DELFIC Particle Activity Module* (BRL 1523, AD 880619),
could be a source of independent PAM data.

## Cross-check: McGahan & Kownacki 1974, DNA 3439F (AD/A-002 464) (21 Oct 2026)

A DELFIC-based sensitivity study (SAI for DNA; filed in
`~/new-word/sources/fallout/mcgahan-1974-delfic-sensitivity-DNA-3439F-ADA002464/`). It uses the pre-1979 code, but the
PAM constants it quotes all match our transcription of the 1979 code, read from the text layer (no OCR needed):
- §7.1: DELFIC assumes 17% of emitted neutrons are captured in a surface burst → our `ALBFOM = 1.699999E+3`
  (per 10⁴, as the yields).
- §7.4: soil-activation HOB factor F = 1 − HOBs/√(4.24 HOBs² − 234 HOBs + 4225) for HOBs < 36 ft (cube-root scaled),
  0 above → PAM1 statements 274–287, same constants.
- §6.1: Freiling crossover "D is 100 µ in the PAM" → GXPSR `CROSS = 1.0E-4` m. This confirms the broken-zero reading of
  that cell.
- Appendix A: RSXP's MBT "signifies that both wafer top and bottom have been processed" → the top/bottom wafer loop that
  the `KDPS=2*KDPST` fix restored.
- §7.2: the PAM handles only NTS soil (DELFIC's profile has atomic H fraction 0.42). Its 1974 baseline used a soil
  solidification temperature of 1673 K; the 1979 default is 2200 K (siliceous).
Nothing here bears on the remaining P239HE yield-total gap: the study's baseline fission type is U235HE, and its K-factor
comparisons by fission type exist only as figures.


## Cross-check: decay data vs Crocker 1967 (21 Oct 2026)

Every chain diagram in Crocker's *Fission Product Decay Chains* (USNRDL-TR-67-111, DTIC AD0659980) was compared with
DELFIC's NUCLID/DCON/BRANCH (`run/period-data/`). Most values agree exactly; 89 differences are older data that DELFIC
really used (each DCON is exact for its own half-life). Two were our misreads, both broken DCON exponents: 104Tc
(E-0 for E-4) and 131Sn (E+2 for E-2), now fixed. Four original-deck oddities stay as printed (123mSn 1.25 d, the
152mEu, 126mSb and 111mPd branches). Crocker also confirms the Rh-109 and Sb-122 code fixes and the A=111/115 branch sets.

## Cross-check: the 1968 PAM tape (Tompkins, DASA-1800-V) (21 Oct 2026)

Tompkins' *Particle Activity* manual (DTIC AD0832239) prints DELFIC's 1968 PAM data tape: decay cards, true (undivided)
yields and ERMs. Read with the local OCR models and on the page images, matched to our cards by content
(`run/period-data/README.md`). The tape is nearly identical to the 1979 tables:
- Yields: every P239HE cell equals our cell × decay-path count except Br-93 (our misread, fixed to .545) and Te-130 (60.0 in
  1968, 60.8 in 1979, kept). The block total now equals ORNL's TAPE20 (18793.03).
- Decay cards: 741 of 758 identical. Zr-106 and Ru-116 DCON exponents were our misreads (both 0.01 s placeholders), and
  so were Nd-151 (8.496507 for 8.886500E-4 = 13.0 min), Sb-128, Cs-137, Ge-80, Sm-151, Pd-109m and I-131
  (`run/period-data/dconcheck.py`, ENDF/B-IV, Crocker 1967); all fixed. Sb-129 is not an exact ln2/T value but is kept
  as read (open).
- ERM: 171 of 181 identical. Y-93 (4.80 → 4.88E-7), Ga-74 (1.87 → 1.80E-5), Te-134 (6.94 → 6.84E-6) and Eu-157
  (3.36 → 3.38E-6) were our misreads, now fixed; the last three were confirmed by the user's hand-check.
- BOIL: the report also prints FRATIO's DATA BOIL card. It confirms Br 331.8 and showed two misreads of ours,
  3175 → 3173 and 1754 → 1764 (fixed, user-confirmed). BOIL(11) stays 1650 as the user reads it (1968: 1656).
  None of these affect the test problem, whose solidification temperature is 2200 K.

Te-134 is a chain-start ERM (it sets the A=134 normalisation), and it closed most of the remaining gap: K is now 6.1026E+09
(1.0001 of print) and the sum of map ordinates .285554E+05 (1.00006). In the map row at y = 27000 m, eight of the ten cells match
print to ±1 in the last digit (the others: +0.3% and +0.5%).

All values changed on 21 Oct 2026 are listed in `CHANGELOG-2026-10-21.md`, with locations and backups.

## Cross-check: ORNL's typed DTM listing, TM-2022/2602 (22 Oct 2026)

ORNL/TM-2022/2602 (Krupcale 2023, PDF pp. 85–114, Listings 1–19) prints its own lowercase typed copy of the 1979 DTM routines
(ADVEC … WILKNS, plus SETTLE): an independent transcription of the same printed listing. Compared line by line with
`src/dtm.f` (and `src/icrm.f` for SETTLE), every disagreement checked on the scan. ORNL's copy has its own typos and
modernisations (CHARACTER, quoted strings, /INDEXX/, debug WRITEs, `cji`, `jtipf`, π/2 as 1.5709796327, a dropped
`IF(J.GT.JTOPF)` card), so the scan decided every case.
- **Our misreads, fixed: 11 code cards, 16 FORMAT cards and two renames.** All compiled cleanly, and almost all sit in code the test problem
  never runs (multi-cell nets, channelling, error paths):
  - NEST `NQ=-NET(IC,JC)` (the minus was missing);
  - TRANP `GO TO 510` / label 510 (we had 513 / 519), `301,350,350`, `1.0E-30`, `ERROR(PROGRM,616,…)` (was `E1E`), `NDATO=NDATC`;
  - ADVEC `.LT. 0.0` and DUMPER flag `0` (was `0.1` and `J`);
  - SPRVS `IACCR` and `0.,0,`;
  - the names CNTR `NDBLE` and SETTLE `CDRR`;
  - 16 FORMAT texts (`CLOUD`, `PLANE`, `TRANSPORT`, `RAW WIND`, `DXSUM/DYSUM`, which match the book's printed output, plus `1H0` carriage
    controls and the SPRVS 8017 text).
- **Effect: none on the test problem.** K 6.1026E+09 and the sum of map ordinates .285554E+05 are unchanged, and the OPM and ICRM output are identical.
  The DTM output changes only in five text lines, which now match the book. A layer-by-layer run (MC(4)=1) gives a bit-identical parcel tape: the test
  problem has one met cell, so the fixed multi-cell paths still have no test.
- **Confirmed by the user:** TRANP `BOUN(…,XT,YT,…)` is `YT`, a malformed T (ORNL's `y1` is a misread).
- **Open, on hand-check sheets** (`review-sheets/ornl-*.png`):
  - `V3AR` vs `VBAR`;
  - the faded `NDTC1=NDATC` vs ORNL's `NDATO`;
  - label 160 vs 100;
  - three FORMAT spacings (LAYERS 10X/19X, ONEDIN 3X/8X, DUMPER 3X/9X);
  - the printed map-sum digit: .2855?8, 3 (ours) or 0 (ORNL .285508). TM-2010/220's .285505 does not fit the clear final 8.
- `src/settle.f` and the other per-routine files in `src/` (`advec.f`, `wnosft.f`, …, all 20 Oct 16:43) are raw-OCR output of the early
  `tools/assemble.py` pass. Nothing builds from them; the canonical decks are `src/icrm.f` and `src/dtm.f`.

The details, with the evidence for each card, are in `JUDGEMENT-CALLS.txt` (22 Oct) and `CHANGELOG-2026-10-22.md`.

