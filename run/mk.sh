#!/bin/sh
# rebuild the DTM/OPM executables from src/dtm.f
B=$(dirname "$0")/..
python3 -I $B/tools/port.py $B --deck dtm >/dev/null
cd $B/run
F="-std=legacy -ffixed-form -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero -g -fcheck=bounds"
gfortran $F -c dtm_port.f -o dtm_port.o 2>/dev/null
gfortran $F dtm_driver.f dtm_port.o icrm_chk.o cdclib.o -o ddtm
gfortran $F opm_driver.f dtm_port.o icrm_chk.o cdclib.o -o dopm
