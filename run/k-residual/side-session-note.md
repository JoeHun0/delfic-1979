# DELFIC K residual — hand-over (20 Oct 2026)

Fixed: NUCLID Rh-109 (p180 L62 f2) 14641532932 -> 14641533954 (branch code 12002). IBRA=128 vs 126 consumed,
orphan pair 0.73/0.27, every later BRANCH pair was on the wrong nuclide. Applied via tablefix.tsv (last row) +
tables/p180.tsv row 62; src/dtm.f line 4064 is the only diff. Backups: *.bak-rh109, run/opm.out.prev-rh109.

Result: K 5.9760E+09 -> 6.1482E+09 (print 6.1020E+09, x1.0076); map cells 0.980 -> 1.004 +-0.003.
Open: +0.76% in small particles (A=138 group ~7% high + 0.3% at b~-0.3 per two-chain fit). Not resolved.

Debug technique (scripts in delfic-k-scripts/, written for a scratch copy of run/ with WRITE(77..82) dumps
patched into GXPSR — see the python patch snippets in the session, or re-add):
- fort.77: J, JRM, NUCLID, ABUNDO, ERM at H+1; fort.78: per chain x class FP; fort.79: BSUBK/ECF; fort.80: PSIZE/FMASS
- K is exactly proportional to sum ABUNDO*|ERM| (+ soil): RADIAL*(1/ECF+CRISS)=1 per chain, sum FMASS=1.
- fit*.py fit (printed FP - ours) per class against chain shapes FMASS*(RADIAL*PSIZE^b+STRAIT).
- Branch-shift / BRANCH-perturbation runs: FRATIO patched to read shiftp.txt / pert.txt before BATMAN.
