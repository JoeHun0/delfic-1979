import sys, os, statistics; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import defaultdict
from pathlib import Path
from model import build, fit_chain, L2
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); wd=Path(sys.argv[3])
def loc(k):
    card=k//5+1; f=k%5+1
    if card<=39: return 205,card+22,f
    if card<=99: return 206,card-38,f
    return 207,card-98,f
# reader margins per card (pam/pNNN.tsv: line, y0, minmargin, badcols, card, values)
marg={}
for pg in (205,206,207):
    for r in (wd/"pam"/f"p{pg:03d}.tsv").read_text().splitlines():
        x=r.split("\t"); marg[(pg,int(x[0]))]=float(x[2])
handfixed=set()
for r in (wd/"pamfix.tsv").read_text().splitlines():
    x=r.split("\t")
    if len(x)>=3: handfixed.add((int(x[0].lstrip("p")),int(x[1])))
fits={}; pts=[]
for A in sorted(chains):
    yz={Z:sum(Y0[k]*div[k] for k in ks) for Z,ks in chains[A].items()}
    f=fit_chain(yz)
    if f: fits[A]=(f,yz)
for A,((Zp,amp),yz) in fits.items():
    for Z,y in yz.items(): pts.append((abs(Z-Zp), y/(amp*np.exp(-L2*(Z-Zp)**2))))
bins=defaultdict(list)
for d,r in pts: bins[round(d/0.05)*0.05].append(r)
curve={b:statistics.median(v) for b,v in bins.items()}
already={60,70,71,90,96,100,101,275,276,298,323,329,377,378,386,422,427,428,463,465,466,468}
EL={30:"Zn",31:"Ga",32:"Ge",33:"As",34:"Se",35:"Br",36:"Kr",37:"Rb",38:"Sr",39:"Y",40:"Zr",41:"Nb",42:"Mo",43:"Tc",44:"Ru",45:"Rh",46:"Pd",47:"Ag",48:"Cd",49:"In",50:"Sn",51:"Sb",52:"Te",53:"I",54:"Xe",55:"Cs",56:"Ba",57:"La",58:"Ce",59:"Pr",60:"Nd",61:"Pm",62:"Sm"}
nm=lambda k: f"{EL.get(info(N[k])['Z'])}-{info(N[k])['A']}{'m' if info(N[k])['M'] else ''}"
out=[]
# (a) moderate rule deviations, core cells only (|dZ|<1.8, rule ratio ~1)
for A,((Zp,amp),yz) in fits.items():
    for Z,y in yz.items():
        d=abs(Z-Zp); g=amp*np.exp(-L2*(Z-Zp)**2); rc=curve.get(round(d/0.05)*0.05,0)
        if d<1.75 and y>0 and g>1:
            r=y/(g*rc)
            if abs(r-1)>0.03:
                for k in chains[A][Z]:
                    if k+1 not in already: out.append((abs(r-1),"rule",k,f"chain value x{r:.3f} of the rule (core cell, |dZ|={d:.2f}); rule {g*rc*(Y0[k]*div[k]/y)/div[k]:.4g}"))
# (b) isomer splits: fraction of the metastable state in each pair
fr=[]
for (A),zs in chains.items():
    for Z,ks in zs.items():
        if len(ks)==2 and all(Y0[k]>0 for k in ks):
            tm=Y0[ks[0]]*div[ks[0]]; tg=Y0[ks[1]]*div[ks[1]]; fr.append((tm/(tm+tg),ks))
common=[0.5,1/3,2/3,0.25,0.75]
for f,ks in fr:
    if min(abs(f-c) for c in common)>0.01:
        for k in ks:
            if k+1 not in already: out.append((0.5,"split",k,f"isomer split m/(m+g) = {f:.3f} (deck mostly uses 1/2, 1/3, 2/3)"))
# (c) weakest accepted readings (not hand-fixed), nonzero cells
w=[]
for k in range(len(N)):
    if not N[k] or not raw[k] or raw[k]=="0.": continue
    pg,ln,f=loc(k)
    if (pg,ln) in handfixed: continue
    w.append((marg.get((pg,ln),1),k))
w.sort()
for m,k in w[:10]:
    if k+1 not in already: out.append((0.4-m,"weak",k,f"reader margin {m:.3f} on this card (lowest accepted)"))
seen=set(); final=[]
for s,kind,k,why in sorted(out,key=lambda x:-x[0]):
    if k in seen: continue
    seen.add(k); final.append((kind,k,why))
for kind,k,why in final: print(f"{kind:5s} #{k+1:3d} {nm(k):9s} p{loc(k)[0]} L{loc(k)[1]} f{loc(k)[2]}  {raw[k]:>13s}  {why}")
import json; json.dump([(kind,k,why) for kind,k,why in final], open("irreg.json","w"))
