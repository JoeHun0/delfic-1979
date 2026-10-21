"""Score single-glyph alternatives in the yield / ERM / JRM tables against the printed FP table.
usage: score.py <scratch> <printed-opm-checks.txt> <opm.out>"""
import sys, re
import numpy as np
S=sys.argv[1]
# --- response matrix
L=open(f"{S}/resp.txt").read().split("\n")
INUC,KRM=map(int,L[0].split())
pairs=" ".join(L[1:1+(KRM+9)//10]).split()
JRM=np.array([int(pairs[2*j]) for j in range(KRM)]); ERM=np.array([float(pairs[2*j+1]) for j in range(KRM)])
G=np.array([[float(x) for x in " ".join(L[1+(KRM+9)//10+i*((KRM+9)//10):1+(KRM+9)//10+(i+1)*((KRM+9)//10)]).split()] for i in range(INUC)])
assert G.shape==(INUC,KRM), G.shape
# --- yields
txt=open(f"{S}/yields-deck.txt").read().split("\n")[1:]
raw=[]
for l in txt:
    if not l.strip(): continue
    for k in range(0,70,14): raw.append(l[k:k+14].strip())
raw=raw[:INUC]; Y=np.array([float(r) if r else 0.0 for r in raw])
# --- chain membership (gx.txt: J K MCH NUCLID ABUNDO ERM DCON)
gx=[l.split() for l in open(f"{S}/gx.txt")]
MCH=np.array([int(r[2]) for r in gx]); AB=np.array([float(r[4]) for r in gx]); NUC=[abs(int(r[3])) for r in gx]
NC=MCH.max()
name=lambda nu: f"{nu//8**9}-{(nu//8**6)%512}{'m' if (nu//8**5)%8 else ''}"
nucname={}
for l in open(f"{S}/bt0.txt"):
    i,nu,a0,a,d=l.split(); nucname[int(i)]=name(abs(int(nu)))
XRT=np.zeros(NC+1)
for j in range(KRM): XRT[MCH[j]]+=AB[j]*abs(ERM[j])
# --- per-chain shapes
ch=[l.split() for l in open(f"{S}/chains.txt")]
nld=max(int(r[1]) for r in ch); shape=np.zeros((NC+1,nld)); psz=np.zeros(nld)
for r in ch:
    lc,ld=int(r[0]),int(r[1]); psz[ld-1]=float(r[2]); shape[lc,ld-1]+=float(r[5])
FISNUM=50*1.45e15
for c in range(1,NC+1):
    if XRT[c]>0: shape[c]/=shape[c].sum()
order=np.argsort(-psz)                      # classes by size, largest first
# --- printed and our FP, same order
pr=[]
for l in open(sys.argv[2]):
    if re.match(r"[\d.]+E[-+]\d\d \S+E", l.strip()):
        for part in l.split("|"):
            p=part.split()
            if len(p)==2: pr.append((float(p[0].rstrip("?")),float(p[1].rstrip("?"))))
pr.sort(key=lambda x:-x[0]); P=np.array([v for s,v in pr])
O_=open(sys.argv[3]).read().split("\n"); i0=[k for k,l in enumerate(O_) if "PSIZE          FP" in l][0]
ours={}
for l in O_[i0+1:i0+9]:
    v=[float(x) for x in l.split()]
    for k in range(0,8,2):
        if v[k]: ours[v[k]]=v[k+1]
keys=sorted(ours)
O=np.array([ours[min(keys,key=lambda q:abs(q-psz[i]))] for i in order]); SH=shape[:,order]
E=P-O
print(f"K ours/print {O.sum()/P.sum():.5f}; need dSum(FP) = {E.sum():.4e} ({E.sum()/O.sum()*100:.3f}%)")
def score(delta):           # delta: dXRT per chain (array NC+1)
    dFP=FISNUM*(delta[:,None]*SH).sum(0)
    return np.linalg.norm(E-dFP)/np.linalg.norm(E), dFP.sum()/E.sum()
base=np.linalg.norm(E)
res=[]
# 1. yields: single digit substitutions in the mantissa/exponent
for i in range(INUC):
    s=raw[i]
    if not s or s=="0.": continue
    g=G[i]                        # ABUNDO at JRM nuclides per unit yield
    for p,ch_ in enumerate(s):
        if not ch_.isdigit(): continue
        for d in "0123456789":
            if d==ch_: continue
            s2=s[:p]+d+s[p+1:]
            try: y2=float(s2)
            except ValueError: continue
            dy=y2-Y[i]
            delta=np.zeros(NC+1)
            np.add.at(delta,MCH,dy*g*np.abs(ERM))
            r,f=score(delta); res.append((r,f,f"yield #{i+1} {nucname[i+1]} {s} -> {s2}"))
# 2. ERM values: single digit / exponent
for j in range(KRM):
    s=f"{abs(ERM[j]):.6E}"       # d.ddddddE-dd ; printed has 3 sig digits
    mant,ex=s.split("E"); ex=int(ex)
    cands=set()
    for p,ch_ in enumerate(mant[:4]):
        if not ch_.isdigit(): continue
        for d in "0123456789":
            if d!=ch_: cands.add(float(mant[:p]+d+mant[p+1:]+"E%d"%ex))
    cands.add(float(mant+"E%d"%(ex+1))); cands.add(float(mant+"E%d"%(ex-1)))
    for v in cands:
        delta=np.zeros(NC+1); delta[MCH[j]]=AB[j]*(v-abs(ERM[j]))
        r,f=score(delta); res.append((r,f,f"ERM J={j+1} {nucname[JRM[j]]} {abs(ERM[j]):.3e} -> {v:.3e}"))
# 3. JRM indices: single digit, keep strictly increasing
AB_all={}
for l in open(f"{S}/act.txt"):
    i,nu,a0,a,d=l.split(); AB_all[int(i)]=float(a)
for j in range(KRM):
    s=str(JRM[j]); lo=JRM[j-1] if j else 0; hi=JRM[j+1] if j+1<KRM else 10**6
    for p,ch_ in enumerate(s):
        for d in "0123456789":
            if d==ch_: continue
            k2=int(s[:p]+d+s[p+1:])
            if not (lo<k2<hi) or k2 not in AB_all: continue
            delta=np.zeros(NC+1); delta[MCH[j]]=(AB_all[k2]-AB[j])*abs(ERM[j])
            r,f=score(delta); res.append((r,f,f"JRM J={j+1} {JRM[j]} ({nucname[JRM[j]]}) -> {k2} ({nucname[k2]})"))
res.sort()
import pickle; pickle.dump(res,open("res.pkl","wb"))
print(f"{len(res)} candidates; best 25 by shape residual (resid 1.0 = explains nothing); f = fraction of the K gap explained")
for r,f,t in res[:25]: print(f"resid {r:.3f}  f={f:+.2f}  {t}")
print("-- best with 0.8<f<1.2:")
for r,f,t in [x for x in res if 0.8<x[1]<1.2][:15]: print(f"resid {r:.3f}  f={f:+.2f}  {t}")
