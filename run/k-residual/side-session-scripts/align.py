import sys
sys.path.insert(0,'/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/tools')
from pathlib import Path
import tcheck
A=tcheck.arrays(Path('/home/kotnyekjm/book-ocr/books/delfic-1979-vol2'))
nuc=[abs(int(t)) for p,l,f,t in A['NUCLID']][:692]
fr=[]; last=nuc[0]//8**9
for v in nuc:
    name=v//8**6; m=name//512; z=name%512
    if not 27<=z<=66: continue
    if m!=last or not fr: fr.append(m)
    last=m
print("FRATIO chains:",len(fr))
grp=[]
for l in open('fort.77'):
    j,k,n,a,e=l.split(); n=abs(int(n))
    if float(e)<0: grp.append(set())
    grp[-1].add(n//8**9)
print("ERM groups:",len(grp))
for i,g in enumerate(grp,1):
    fm=fr[i-1]
    if g!={fm}: print(i, sorted(g), "FRATIO mass", fm)
print("FRATIO masses with no ERM group:", sorted(set(fr)-set().union(*grp)))
