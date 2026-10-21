# How the 1979 P239HE yield block was built (reverse-engineered, 21 Oct 2026)

`graph.py` builds the decay graph from NUCLID and counts decay paths from chain heads (agrees with BATMAN on every
radioactive nuclide). `model.py` fits the rule below and lists the cells that break it.
Usage: `python3 -I model.py bt0.txt ../pam-p239he.txt`, where `bt0.txt` is the output of `bt.f`: BATMAN at t ≈ 0;
link it against `run/dtm_port.o icrm_chk.o cdclib.o`, run it in run/ with `echo 1e-3 |`, and rename fort.7.

The rule (atoms per 10⁴ fissions):
1. True independent yield per (A, Z) = Σ over isomers of (file value × number of decay paths to the nuclide).
   Stable nuclides are **not** divided (ORNL/TM-2010/220 notes this for Kr-86).
2. y(A, Z) = Y_A · 2^−(Z−Zp)² · r(|Z−Zp|), i.e. a Gaussian charge dispersion with fixed width (σ = 0.85,
   ln-curvature −2·ln 2), with Zp and Y_A per chain. Zp values are tidy (33.000, 35.500, 37.400, 42.500, 45.000 …).
3. Tail factor r: 1.00 for |ΔZ| ≤ 1.8, then 0.93 (1.90), 0.92 (1.95), 0.85 (2.00), 0.68 (2.05), 0.55 (2.10),
   0.45 (2.15), 0.36 (2.20), 0.29 (2.25), 0.23 (2.30), 0.19 (2.35), 0.15 (2.40), 0 from 2.45.
4. Isomer splits are mostly 50/50 (Kr-85m/Kr-85, Sb-128m/Sb-128, Cd-117m 2:1 …); the block stops at A=150.
5. Values are then divided by the path count (rule 1), which is why divided cells carry 6 digits.

Cells that do not follow the rule but read exactly so on the scan (hand-set in the original; keep as printed):
Zn-80 0.62 and Ge-84 0.168 (rule mantissa, exponent off by one: likely 1979 typing slips), Ge-85 0.0119,
Kr-85m/Kr-85 3.0647 each, Mo-110 8.12, Rh-113 48.1,
In-119m/In-119, Cd-125 0.70, Te-125m/Te-125, Sn-120 0, Rh-107m/Rh-107 0.

Se-81m was a misread (.396200 for .996200, hand-checked by the user 21 Oct); with it A=81 follows the rule.
`sheet.py` renders `review-sheets/yield-rule-check.png` (scan crop, reading, rule prediction per off-rule cell).
Br-89 was a misread (.573900 for .573000, hand-checked 21 Oct). Rb-91 .135190E+03 (5 digits) is as printed.
Sn-130 was a misread (.609 for .809, hand-checked 21 Oct); with it the whole A=130 chain follows the rule and the block total equals ORNL's TAPE20 (18793.05 vs 18793.03).
`lowconf.py` scores every digit with a leave-own-card-out kNN; `judge.py` tests the classifier's alternative against the chain rule and pair ratios; `zoomcheck.py` renders hand-check zooms.
