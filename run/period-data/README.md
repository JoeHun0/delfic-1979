# DELFIC decay data vs Crocker 1967 (21 Oct 2026)

Source: G. R. Crocker, *Fission Product Decay Chains: Schematics with Branching Fractions, Half-Lives, and Literature
References*, USNRDL-TR-67-111, 24 June 1967 (DTIC AD0659980; Wayback 2012 snapshot, 36 pp; filed in
`~/glasstone-test-data/other/delfic-period-data/crocker-1967-decay-chains-AD0659980/`). Literature through Feb 1967.

Method: `ours.py bt0.txt branch.txt A0 A1` prints DELFIC's decay data per chain (half-life from DCON, branch
fractions, daughters from NUCLID) in Crocker's units; each chain diagram (pp. 9–26, A=72–161) was compared by eye.
`crocker-compare.tsv` logs every difference (122 rows).

Result:
- Most values agree exactly. 89 differences are data vintage: DELFIC's table predates Crocker's 1967 literature update
  (e.g. 129Sn 1.8 h is "the NDS 1961 value" per Crocker; 107mRh 45 s is Katcoff's older value). Each such DCON is exactly
  0.693147/T for DELFIC's own round T, so they are what the 1968/1979 code used. Kept.
- 17 structural differences: isomers or branches Crocker has and DELFIC omits (82mBr, 84mBr, 90mY, 94mNb, 146Pm,
  148mPm, β-n of 85As and 135Sb, ...).
- 3 design: DELFIC caps very long half-lives at λ ≈ 1.0E-15 /s (87Rb, 115In, 138La).
- **2 transcription errors, fixed** (both broken exponent glyphs on the DCON cards):
  104Tc p175 L36 f2 6.418028E-0 → E-4 (18.0 min, = Crocker); 131Sn p176 L23 f2 1.050223E+2 → E-2 (66 s; Crocker 79 s).
- Original-deck oddities, kept as printed (scan checked): 123mSn 1.25 d (Crocker 129 d; probably a decimal slip for
  125 d), 152mEu branch 0.75 EC / 0.25 β⁻ (reversed vs Crocker and modern), 126mSb 0.99 IT / 0.01 (Crocker 0.15/0.85),
  111mPd 0.68/0.32 (Crocker 0.933/0.067). All carry no or negligible activity in the test problem.
- Independent confirmations of earlier fixes: 109Rh 0.5/0.5 to 109mPd/109Pd (Rh-109 code), 122Sb 0.03 EC / 0.97 β⁻
  (Sb-122 code), the whole A=115 and A=111 branch sets (BRANCH alignment).

# DELFIC PAM tape vs Tompkins 1968 (21 Oct 2026)

Source: R. C. Tompkins, *DELFIC: Department of Defense Land Fallout Prediction System, Vol. V – Particle Activity*,
DASA-1800-V, Feb 1968 (DTIC AD0832239; Wayback 2024 snapshot, 261 pp; filed in
`~/glasstone-test-data/other/delfic-period-data/tompkins-1968-dasa-1800-v-particle-activity-AD0832239/`). Its appendix
lists the 1968 PAM data tape: TRAN cards (pp. 208–220, 758 decay cards: A iso Z, half-life value/unit/exponent, branch
fraction, daughter), FY cards (pp. 220–254, true undivided yields for U235/U233/P239 thermal and high energy, then U238...)
and ERM cards (pp. 254–257: A Z, then state code + 3-digit exposure-rate multiplier, e.g. `91 39 1.282E-05` = isomer 1, .282E-05).

Method: pages read with GLM-OCR and LightOnOCR on 10-line strips (plus the PDF text layer); each reading matched to our
cards by content (`exp_tran.py` writes ours as 1968 cards, `cmp_tran.py`, `cmp_erm2.py`); every card without a reader
agreeing with ours was read on the page image. Yields: 1968 value = our 1979 cell x decay-path count (stable x 1).

Result:
- Yields (`fy68-compare.tsv`): all P239HE cells agree. Br-93 fixed (.545); Te-130 changed 60.0 (1968) -> 60.8 (1979), kept.
- Decay data (`tran68-compare.tsv`): 742 of 758 cards identical. **Fixed: Zr-106 and Ru-116 DCON exponents** (p175 L39 f2
  E-1 -> E+1, p175 L57 f2 E+0 -> E+1; both 0.01 s placeholders like their neighbours). Five half-lives were revised between
  1968 and 1979 (Ge-77, In-115m, Sb-128, Sb-129, I-131; all clean ln2/T in 1979) and are kept. Nd-151 looked revised
  (13.6 min) but was a misread of four broken glyphs: it is 8.886500E-4 = 13.0 min, as in 1968 (fixed). The rest are the known
  design cap and original oddities (Sn-123m, Eu-152m).
- ERM (`erm68-compare.tsv`): 171 of 181 identical. **Fixed: Y-93 4.80E-7 -> 4.88E-7; Ga-74 1.87E-5 -> 1.80E-5 and Te-134
  -6.94E-6 -> -6.84E-6, Eu-157 -3.36E-6 -> -3.38E-6 (all three confirmed by the user's hand-check).** I-135's unreadable 4th
  digit was tried 0-9; 0 fits the print best and is kept.
- BOIL (FRATIO's DATA card, 1968 report PDF p. 113): Br 331.8 confirmed; 2*3175 -> 2*3173 and 1754 -> 1764 fixed (user-
  confirmed); BOIL(11) 1650 kept (user reading; 1968 prints 1656). No effect on the test problem (solidification at 2200 K). Rh-109m and Pm-152 changed between 1968 and 1979 (1979 scan clear).
- Effect on the test problem: K 6.1063E+09 -> 6.1026E+09 (print 6.1020E+09, x1.0001), almost all from Te-134 (a chain-start
  ERM); FP by class 0.9993..1.0001 of print; sum of map ordinates .285554E+05 (print .285538E+05).

# DCON recheck (21 Oct 2026)

`dconcheck.py` tests every DCON cell: exact 0.693147/T for a round T, the 1968 value, and a kNN glyph vote with automatic
grid shift (`dcon-check.tsv`). Fixed: Nd-151, Sb-128, Cs-137, Ge-80, Sm-151 (each one or more broken digits; the exact 1968
value). Pd-109m was then fixed
on the ENDF/B-IV evidence (below). I-131 was fixed too (Crocker 1967 and 1968: 8.05 d). Kept as read although not exact: Sb-129 (open for a better copy).
Only Ge-77, In-115m and the long-half-life caps now differ from 1968 for other reasons.

# ENDF/B-IV 1974 (21 Oct 2026)

`endf4.py` compares every DCON with the ENDF/B-IV decay data (extract in
`~/glasstone-test-data/other/delfic-period-data/endfb-iv-fp/`), character by character (`endf4-compare.tsv`). ENDF/B-IV is a
newer evaluation, so most values differ outright; it is evidence only where everything but a doubtful glyph agrees. That
happened once: Pd-109m (2.457956E-3, doubtful "56"; ENDF/B-IV and 1968 both give 2.457968E-3 = 282 s); fixed.
