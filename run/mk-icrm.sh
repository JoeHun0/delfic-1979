#!/bin/sh
# rebuild the ICRM executable (dicrm) and the ICRM objects the DTM/OPM link against, from src/icrm.f
# (run tools/build.py . first if the cards or fixes changed; then run/mk.sh for DTM/OPM)
B=$(dirname "$0")/..
python3 -I $B/tools/port.py $B >/dev/null
cd $B/run
F="-std=legacy -ffixed-form -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero"
gfortran $F -c cdclib.f -o cdclib.o
gfortran $F -c icrm_port.f -o icrm_port.o 2>/dev/null
gfortran $F -g -fcheck=bounds -c icrm_port.f -o icrm_chk.o 2>/dev/null
gfortran $F driver.f icrm_port.o cdclib.o -o dicrm
