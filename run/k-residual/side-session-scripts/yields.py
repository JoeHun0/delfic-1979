import sys
sys.path.insert(0,'/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/tools')
from pathlib import Path
import tcheck
W=Path('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2')
A=tcheck.arrays(W)
nuc=[int(t) for p,l,f,t in A['NUCLID']][:692]
dc=[float(t) for p,l,f,t in A['DCON']][:692]
y=[float(x) for l in open(W/'run/pam-p239he.txt').read().splitlines()[1:] for x in l.split()][:692]
from collections import defaultdict
tot=defaultdict(float); mem=defaultdict(list)
for i,(n,d,v) in enumerate(zip(nuc,dc,y),1):
    h,a,z,m,low=tcheck.nuclide(n)
    nm=f"{tcheck.SYM[z]}-{a}{'m' if m else ''}"
    tot[a]+=v; mem[a].append((i,nm,v,d,h))
for a in sorted(tot):
    if tot[a]>0: print(a, f"{tot[a]:.4g}", end=" | ")
print()
for a in map(int,sys.argv[1:]):
    for i,nm,v,d,h in mem[a]:
        print(f"  #{i:3d} {nm:9s} {'H' if h else ' '} y={v:.4e} T={0.693147/d/3600 if d else 0:.4g} h")
