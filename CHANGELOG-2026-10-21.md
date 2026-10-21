# Changes to the DELFIC transcription on 21 Oct 2026

Every value changed in the deck today (22). The reasons are in `JUDGEMENT-CALLS.txt` (search for the nuclide). Each edit is in
the fix file named, and a backup of that file was made first (`<file>.bak-<what>`). To undo one change, restore its backup
or edit the row back, then run `tools/tables.py . read <page>` (tables), `tools/build.py . --deck dtm` and `run/mk.sh`.

| # | What | Where (PDF page, line, field) | Old → new | Evidence | Fix file (backup) |
|---|---|---|---|---|---|
| 1 | NUCLID As-83 | p180 L17 f3 | −11148727298 → +11148727298 | no minus on the scan; false chain head | tablefix.tsv (.bak-as83) |
| 2 | P239HE yield Sn-130 | p206 L55 f4 | .609000E+02 → .809000E+02 | user's copy; ORNL TAPE20 total | pamfix.tsv + run/pam-p239he.txt (.bak-handcheck) |
| 3 | P239HE yield Se-81m | p205 L36 f5 | .396200E+00 → .996200E+00 | user's copy | pamfix.tsv + deck |
| 4 | P239HE yield Ge-84 | p205 L40 f5 | .160000E+00 → .168000E+00 | user's copy | pamfix.tsv + deck |
| 5 | P239HE yield Br-89 | p205 L48 f2 | .573900E+02 → .573000E+02 | user's copy | pamfix.tsv + deck |
| 6 | P239HE yield Br-93 | p205 L54 f2 | .565000E+00 → .545000E+00 | 1968 tape; ORNL total | pamfix.tsv + deck |
| 7 | DCON Tc-104 | p175 L36 f2 | 6.418028E-0 → 6.418028E-4 | Crocker 1967, scan | tablefix.tsv (.bak-tc104) |
| 8 | DCON Sn-131 | p176 L23 f2 | 1.050223E+2 → 1.050223E-2 | Crocker 1967, scan | tablefix.tsv |
| 9 | DCON Zr-106 | p175 L39 f2 | 6.931470E-1 → 6.931470E+1 | 1968 tape, sign glyph | tablefix.tsv (.bak-zr106) |
| 10 | DCON Ru-116 | p175 L57 f2 | 6.931470E+0 → 6.931470E+1 | 1968 tape, all OCR | tablefix.tsv (.bak-zr106) |
| 11 | ERM Y-93 | p177 L19 f5 | 4.800000E-7 → 4.880000E-7 | 1968 tape, glyph | tablefix.tsv (.bak-y93) |
| 12 | ERM Ga-74 | p177 L13 f1 | 1.870000E-5 → 1.800000E-5 | user's copy, 1968 | tablefix.tsv (.bak-ga74) |
| 13 | ERM Te-134 | p177 L38 f3 | −6.940000E-6 → −6.840000E-6 | user's copy, 1968 | tablefix.tsv (.bak-te134) |
| 14 | ERM Eu-157 | p177 L47 f5 | −3.360000E-6 → −3.380000E-6 | user's copy, 1968 | tablefix.tsv (.bak-eu157) |
| 15 | BOIL(1),(2) and BOIL(6) | p185 L31 (code card) | 2*3175.0 → 2*3173.0; 1754.0 → 1764.0 | user's copy, 1968 listing, glyph vote | cardfix.tsv (.bak-boil) |
| 16 | DCON Nd-151 | p176 L55 f1 | 8.496507E-4 → 8.886500E-4 | user's copy, exact 13.0 min = 1968 | tablefix.tsv (.bak-nd151) |
| 17 | DCON Sb-128 | p176 L18 f4 | 2.236847E-5 → 2.238847E-5 | user's guess, exact 8.6 h = 1968 | tablefix.tsv (.bak-dconrecheck) |
| 18 | DCON Cs-137 | p176 L34 f2 | 7.522050E-10 → 7.522090E-10 | user's guess, exact 29.2 y = 1968 | tablefix.tsv (.bak-dconrecheck) |
| 19 | DCON Ge-80 | p174 L57 f2 | 2.772586E-2 → 2.772588E-2 | user's guess, exact 25 s = 1968 | tablefix.tsv (.bak-dconrecheck) |
| 20 | DCON Sm-151 | p176 L55 f3 | 2.745553E-10 → 2.745563E-10 | user's revised guess, exact 80 y = 1968 | tablefix.tsv (.bak-sm151) |
| 21 | DCON Pd-109m | p175 L46 f3 | 2.457956E-3 → 2.457968E-3 | exact 282 s = 1968 = ENDF/B-IV; user agreed | tablefix.tsv (.bak-pd109m) |
| 22 | DCON I-131 | p176 L25 f1 | 9.955882E-7 → 9.965882E-7 | exact 8.05 d = Crocker 1967 = 1968; user agreed | tablefix.tsv (.bak-i131) |

Kept as read after checking (no change): ICRM CHANGE=100. and DLTM=0.0; ERM I-135 1.560, Ba-142 4.950, Rh-106m 8.66,
Gd-161 2.03; XLAM(1,13) 1.28333E-34 (the original's stable marker); BOIL Br 331.8 and BOIL(11) 1650; DCON In-115m and Sb-129 (Sb-129 still open: Crocker 4.5 h, 1968 4.6 h, ours 4.589 h, not exact).

Effect on the test problem over the day: K 6.1362E+09 → 6.1026E+09 (print 6.1020E+09), sum of map ordinates 1.00006 of
print, FP by class 0.9993–1.0001 of print. The large steps were As-83 (−0.5%), Tc-104/Sn-131 (+0.03%) and Te-134 (−0.06%).
