#!/bin/sh
# Dump DELFIC's PAM tables from the current build (run run/mk.sh first; relink every time, a stale binary gives old values):
#   bt0.txt    BATMAN at t ~ 0: index, NUCLID, yield, atoms, DCON  (used by ours.py, exp_tran.py, ../yield-model/)
#   branch.txt the BRANCH table in consumption order (4 - low octal digit entries per nuclide, in NUCLID order)
# usage: sh dump.sh [outdir]   (default: this directory)
P=$(cd "$(dirname "$0")" && pwd); R=$P/..; O=${1:-$P}; T=$(mktemp -d)
F="-std=legacy -ffixed-form -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero"
gfortran $F $R/yield-model/bt.f $R/dtm_port.o $R/icrm_chk.o $R/cdclib.o -o $T/bt &&
gfortran $F $P/dumpn.f $R/dtm_port.o $R/icrm_chk.o $R/cdclib.o -o $T/dumpn || exit 1
cd $T && cp $R/pam-p239he.txt . && echo 1e-3 | (cd $R && $T/bt >/dev/null && mv fort.7 $O/bt0.txt)
cd $T && ./dumpn && python3 -I -c "
import sys; L=open('nuclid.txt').read().split('IBRA INUC MAXNUC')[1].splitlines()
ibra=int(L[0].split()[0]); v=' '.join(L[1:]).split()[:ibra]; open(sys.argv[1],'w').write(' '.join(v)+'\n')" $O/branch.txt
rm -rf $T; wc -l $O/bt0.txt; wc -w $O/branch.txt
