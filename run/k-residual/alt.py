"""Swap one reading in a scratch copy of run/, rebuild, rerun, compare with print.
usage: alt.py <rundir> <label> <file> <line> <old> <new> [<file> <line> <old> <new> ...]   (file: dtm_port.f | icrm_port.f | pam-p239he.txt)"""
import re, subprocess, sys, shutil
from pathlib import Path
rd=Path(sys.argv[1]); label=sys.argv[2]; edits=sys.argv[3:]
F="-std=legacy -ffixed-form -fdefault-real-8 -fdefault-integer-8 -fno-automatic -finit-local-zero".split()
orig={}
def sh(*a, **k): return subprocess.run(list(a), cwd=rd, capture_output=True, text=True, **k)
try:
    for i in range(0,len(edits),4):
        fn,ln,old,new=edits[i],int(edits[i+1]),edits[i+2],edits[i+3]
        p=rd/fn; orig.setdefault(fn,p.read_text()); L=p.read_text().split("\n")
        assert L[ln-1].count(old)==1, (fn,ln,old,L[ln-1]); L[ln-1]=L[ln-1].replace(old,new); p.write_text("\n".join(L))
    if "icrm_port.f" in orig:
        r=sh("gfortran",*F,"driver.f","icrm_port.f","-o","dicrm_s"); assert not r.returncode, r.stderr[-500:]
        icrm=sh("./dicrm_s",input=(rd/"icrm-test-deck.txt").read_text()).stdout
        (rd/"icrm_s.out").write_text(icrm)
        sh("sh","-c","./ddtm_s < dtm-test-deck.txt > /dev/null") if (rd/"ddtm_s").exists() else None
    if "dtm_port.f" in orig or not (rd/"dopm_s").exists() or "icrm_port.f" in orig:
        r=sh("gfortran",*F,"-c","dtm_port.f","-o","dtm_s.o"); assert not r.returncode, r.stderr[-500:]
        sh("gfortran",*F,"dtm_driver.f","dtm_s.o","icrm_chk.o","cdclib.o","-o","ddtm_s")
        sh("gfortran",*F,"opm_driver.f","dtm_s.o","icrm_chk.o","cdclib.o","-o","dopm_s")
    if "icrm_port.f" in orig:
        sh("sh","-c","./ddtm_s < dtm-test-deck.txt > dtm_s.out")
    o=sh("sh","-c","./dopm_s < opm-test-deck.txt").stdout
finally:
    for fn,t in orig.items(): (rd/fn).write_text(t)
K=float(re.search(r"FP TABLE -\s+(\S+)",o).group(1)); M=float(re.search(r"SUM OF MAP ORDINATES =\s+(\S+)",o).group(1))
t=(rd/"printed-opm-checks.txt").read_text().split("PSIZE, FP):")[1].split("sum of map")[0]
pr={p:f for p,f in re.findall(r"(\d\.\d{4}E[-+]\d\d)\??\s+(\d\.\d{4}E\+\d\d)\??",t)}
L=o.splitlines(); i=[n for n,l in enumerate(L) if "PSIZE" in l and "FP" in l][0]
ours={p:f for l in L[i+1:i+10] for p,f in re.findall(r"(\d\.\d{4}E-\d\d)\s+(\d\.\d{4}E\+\d\d)",l)}
r=[float(ours[p])/float(pr[p]) for p in pr if p in ours]
row=[l for l in L if re.match(r"\s+27000\.",l)][0].split()[1:11]
print(f"{label:28s} K {K:.4E} ({K/6.1020e9:.5f})  map {M:.6E} ({M/0.285538e5:.5f})  FP {min(r):.4f}..{max(r):.4f}  row27000 {' '.join(row)}")
