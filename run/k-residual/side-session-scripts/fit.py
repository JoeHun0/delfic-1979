import re, numpy as np
exec(open('rank.py').read().split('rows=[]')[0])
def grid(lines):
    v=[[float(x) for x in re.findall(r'\d\.\d{4}E[+-]\d\d',l)] for l in lines]
    cols=[[],[],[],[]]
    for r in v:
        for c in range(len(r)//2):
            if r[2*c]>0: cols[c].append(r[2*c+1])
    return sum(cols,[])
ours=grid([l for l in open('opm.out').read().splitlines()[72:80]])
pl=[l.replace('?','') for l in open('../../../../../../../../home/kotnyekjm/book-ocr/books/delfic-1979-vol2/run/printed-opm-checks.txt' if False else '/home/kotnyekjm/book-ocr/books/delfic-1979-vol2/run/printed-opm-checks.txt') if '|' in l]
pr=grid(pl)
print(len(ours),len(pr)); ours=np.array(ours); pr=np.array(pr); assert len(ours)==30==len(pr)
D=pr-ours
print("ratio by class:", np.round(ours/pr,4))
# chain membership from ERM sign
chains=[]; 
for l in open('fort.77'):
    j,k,n,a,e=l.split(); n=abs(int(n)); A=n//8**9; Z=(n//8**6)%512; M=(n//8**5)%8
    if float(e)<0: chains.append([])
    chains[-1].append((f"{SYM[Z]}-{A}{'m' if M else ''}",float(a)*abs(float(e))))
C={}; B={}
for l in open('fort.78'):
    lc,ld,b,ps,v=l.split(); C.setdefault(int(lc),np.zeros(30))[int(ld)-1]=float(v); B[int(lc)]=float(b)
tot=ours.sum()
res=[]
for lc,v in C.items():
    a=(v@D)/(v@v); r=D-a*v
    res.append((np.sqrt((r**2).sum()/(D**2).sum()),lc,a,v.sum()/tot))
res.sort()
print("uniform-scale fit resid:", np.sqrt(((D-(ours@D)/(ours@ours)*ours)**2).sum()/(D**2).sum()))
for rr,lc,a,f in res[:12]:
    top=sorted(chains[lc-1],key=lambda x:-x[1])[:3]
    print(f"chain {lc:3d} b={B[lc]:+.3f} share={f*100:5.2f}% scale={a:+.3f} -> adds {a*f*100:+.2f}%  resid={rr:.3f}  {[t[0] for t in top]}")
print("---- continuous b scan (class 21 excluded too)")
ps=np.array([float(l.split()[3]) for l in open('fort.78')][:30])
fm={}
# shape for generic chain: FMASS*(RADIAL*PSIZE^b+STRAIT) ; get FMASS from any chain: v = (R p^b + S)*TNEX*FMASS
lc0=list(C)[0]; b0=B[lc0]
import math
def shape(b,FM):
    cr=1e-4**b; ecf=1/np.sum(FM*ps**b); rad=ecf/(1+cr*ecf); return (rad*ps**b+rad*cr)*FM
# recover FMASS from chain lc0: v/(R p^b+S) up to const
cr=1e-4**b0; FM0=C[lc0]/(ps**b0+cr); FM=FM0/FM0.sum()
for mask_name,mask in (("all",np.ones(30,bool)),("no21",np.arange(30)!=20)):
    best=[]
    for b in np.arange(-1.0,0.001,0.01):
        v=shape(b,FM); a=(v[mask]@D[mask])/(v[mask]@v[mask]); r=D[mask]-a*v[mask]
        best.append((np.sqrt((r**2).sum()/(D[mask]**2).sum()),b,a*v.sum()/ours.sum()))
    best.sort(); print(mask_name,[(round(x,4),round(b,2),round(f*100,3)) for x,b,f in best[:6]])
print("chains by b:")
for lc in sorted(C,key=lambda k:B[k]):
    print(f"{lc}:{B[lc]:+.3f}:{C[lc].sum()/ours.sum()*100:.2f}%", end="  ")
print()
