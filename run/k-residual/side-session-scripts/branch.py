import sys
sys.path.insert(0,'/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/tools')
from pathlib import Path
import tcheck
W=Path('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2'); A=tcheck.arrays(W)
nuc=[int(t) for p,l,f,t in A['NUCLID']][:692]
br=A['BRANCH']
ab={}
for l in open('fort.81'):
    k,_,n,a,d=l.split(); ab[int(k)]=float(a) if 'E' in a else 0.0
lbr=0
for i,v in enumerate(nuc,1):
    nb=4-abs(v)%8
    if nb>0:
        h,AA,Z,M,low=tcheck.nuclide(v)
        ent=br[lbr:lbr+nb]
        s=sum(float(t) for p,l,f,t in ent)
        print(f"#{i:3d} {tcheck.SYM[Z]}-{AA}{'m' if M else ''} low={oct(low)} n={nb} BRANCH[{lbr+1}..{lbr+nb}] = "+" ".join(f"{t}(p{p}L{l}f{f})" for p,l,f,t in ent)+f"  sum={s:.4g}  ABUNDO={ab[i]:.3e}")
        lbr+=nb
print("total entries used",lbr,"of",len(br))
