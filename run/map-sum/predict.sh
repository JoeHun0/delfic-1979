#!/bin/sh
# Predict the book's map from our DTM transport and the book's own printed FP-by-class table (book-fp.txt):
# OPM's map is linear in FP per class (CALC: F=FP(J)*PMAS/FMASS/SSAM), so overriding FP with the printed values
# gives the book's map up to transport differences. Writes opm-bookfp.out here. Needs run/dtm.bin (run ddtm first).
M=$(cd "$(dirname "$0")" && pwd); R=$M/..; T=$(mktemp -d)
cp $R/dtm_port.f $R/opm_driver.f $R/icrm_chk.o $R/cdclib.o $R/opm-test-deck.txt $R/dtm.bin $R/pam-p239he.txt $T/
cp $M/book-fp.txt $T/fpbook.txt
cd $T
python3 - <<'PY'
s=open('dtm_port.f').read(); a="    5 IF(NPRNT(15)) RETURN\n      NTAB=ITAB/4"; assert s.count(a)==1
open('dtm_port.f','w').write(s.replace(a,"    5 CONTINUE\n      OPEN(77,FILE='fpbook.txt',STATUS='OLD')\n      READ(77,*) (FP(I),I=1,30)\n      CLOSE(77)\n      IF(NPRNT(15)) RETURN\n      NTAB=ITAB/4"))
PY
F="-std=legacy -ffixed-form -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero"
gfortran $F -c dtm_port.f -o dtm_port.o 2>/dev/null && gfortran $F opm_driver.f dtm_port.o icrm_chk.o cdclib.o -o dopm && ./dopm < opm-test-deck.txt > $M/opm-bookfp.out 2>/dev/null
grep "SUM OF MAP" $M/opm-bookfp.out; rm -rf $T
