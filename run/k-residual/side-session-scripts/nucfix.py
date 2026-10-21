import sys
sys.path.insert(0,'/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/tools')
from pathlib import Path
import tcheck
W=Path('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2'); A=tcheck.arrays(W)
nuc=A['NUCLID']; pos={(p,l,f):k for k,(p,l,f,t) in enumerate(nuc,1)}
L=open(W/'tablefix.tsv').read().splitlines()
sec=None
for i,l in enumerate(L,1):
    if l.startswith('#'): sec=l[:90]; continue
    if not (1059<=i<=1189): continue
    x=l.split('\t')
    if x[2] in ('-','H','*'): continue
    k=pos.get((int(x[0][1:]),int(x[1]),int(x[2])))
    if not k: continue
    h,AA,Z,M,low=tcheck.nuclide(int(x[3]))
    print(f"#{k:3d} {tcheck.SYM[Z]}-{AA}{'m' if M else ''} low={low:05o} {'HEAD' if h else ''}  [{sec[2:40]}]")
