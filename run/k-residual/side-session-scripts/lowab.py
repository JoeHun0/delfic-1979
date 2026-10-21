import sys
sys.path.insert(0,'/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/tools')
from pathlib import Path
import tcheck
W=Path('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2'); A=tcheck.arrays(W)
dc=[float(t) for p,l,f,t in A['DCON']]
y=[float(x) for l in open(W/'run/pam-p239he.txt').read().splitlines()[1:] for x in l.split()]
for l in open('fort.77'):
    j,k,n,a,e=l.split(); k=int(k); h,AA,Z,M,low=tcheck.nuclide(int(n))
    T=0.693147/dc[k-1]/3600 if dc[k-1] else 0
    nm=f"{tcheck.SYM[Z]}-{AA}{'m' if M else ''}"
    flag = "  <--" if float(a)<1e-3 and AA<=150 else ""
    print(f"ERM#{int(j):3d} nuc#{k:3d} {nm:9s} T={T:10.4g}h y={y[k-1]:9.4g} ABUNDO={float(a):.3e} ERM={float(e):+.2e}{flag}")
