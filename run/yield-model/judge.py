import sys, os, json, re, statistics; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import defaultdict
from pathlib import Path
from model import build, fit_chain, L2
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); wd=Path(sys.argv[3])
rows=json.load(open("lowconf.json"))
# OCR tokens (models drop the leading '.')
def ocr_lines(model,pg):
    d={}
    for r in (wd/f"ocr-{model}"/f"p{pg:03d}.tsv").read_text().splitlines():
        x=r.split("\t")
        if len(x)>4: d[int(x[0])]=x[4].split(" || ")[0].split()
    return d
ocr={m:{pg:ocr_lines(m,pg) for pg in (205,206,207)} for m in ("glm","lighton")}
def norm(t):
    t=t.strip()
    if re.fullmatch(r"\d{6}E[+-]\d\d",t): t="."+t
    return t
# chain fits and tail curve
fits={}; pts=[]
for A in chains:
    yz={Z:sum(Y0[k]*div[k] for k in ks) for Z,ks in chains[A].items()}
    f=fit_chain(yz)
    if f: fits[A]=f
for A,(Zp,amp) in fits.items():
    for Z,ks in chains[A].items():
        y=sum(Y0[k]*div[k] for k in ks); pts.append((abs(Z-Zp), y/(amp*np.exp(-L2*(Z-Zp)**2))))
bins=defaultdict(list)
for d,r in pts: bins[round(d/0.05)*0.05].append(r)
curve={b:statistics.median(v) for b,v in bins.items()}
def chain_resid(A, override):
    """refit chain A with one cell value replaced; return rms log-deviation of core cells from the rule"""
    Y=list(Y0); 
    for k,v in override.items(): Y[k]=v
    yz={Z:sum(Y[k]*div[k] for k in ks) for Z,ks in chains[A].items()}
    with np.errstate(all="ignore"): f=fit_chain(yz)
    if not f or not np.isfinite(f[0]) or not np.isfinite(f[1]) or abs(f[0])>200: return None
    Zp,amp=f; dev=[]
    for Z,y in yz.items():
        d=abs(Z-Zp); rc=curve.get(round(d/0.05)*0.05,0); g=amp*np.exp(-L2*(Z-Zp)**2)*rc
        if g>0.5 and y>0: dev.append(np.log(y/g))
        elif g>0.5 and y==0: dev.append(3.0)
    return float(np.sqrt(np.mean(np.square(dev)))) if dev else None
def partners(k):
    I=info(N[k]); return [j for j in chains[I["A"]][I["Z"]] if j!=k and Y0[j]>0]
out=[]
for marg,k1,pg,ln,f,val,pos,ch,alt,_ in rows:
    if marg>0.07: break
    k=k1-1; I=info(N[k])
    s=val; i=f-1
    alt_s=s[:pos-4]+alt+s[pos-3:] if pos else s
    try: av=float(alt_s)
    except: continue
    cur=chain_resid(I["A"],{}); new=chain_resid(I["A"],{k:av})
    pr=partners(k); pair=""
    if pr:
        j=pr[0]; tj=Y0[j]*div[j]; tc=Y0[k]*div[k]; ta=av*div[k]
        rc=tc/tj; ra=ta/tj
        nice=lambda r: min(abs(r-q) for q in (1,2,0.5,3,1/3,4,0.25,1.5,2/3))
        pair=f"pair ratio ours {rc:.4f} alt {ra:.4f}"
        pairok = nice(rc)<0.002 and nice(ra)>0.002
    else: pairok=None
    oc=[]
    for m in ocr:
        t=ocr[m][pg].get(ln,[]); t=[norm(x) for x in t if re.search(r"\d",x)]
        oc.append(f"{m}:{t[i] if i<len(t) else '-'}")
    if pairok: verdict="ours (pair ratio exact)"
    elif cur is not None and new is not None and new>cur*1.5+0.01: verdict="ours (alt breaks the chain rule)"
    elif cur is not None and new is not None and new<cur*0.7-0.005: verdict="ALT fits the rule better: CHECK"
    else: verdict="undecided: CHECK"
    out.append(dict(k=k1,pg=pg,ln=ln,f=f,val=val,alt=alt_s,marg=marg,cur=cur,new=new,pair=pair,ocr=" ".join(oc),verdict=verdict))
for o in out:
    print(f"#{o['k']:3d} p{o['pg']} L{o['ln']} f{o['f']} ours {o['val']:>12s} alt {o['alt']:>12s} margin {o['marg']:+.3f}  rule-rms ours {o['cur'] if o['cur'] is None else round(o['cur'],3)} alt {o['new'] if o['new'] is None else round(o['new'],3)}  {o['pair']}  [{o['ocr']}]  -> {o['verdict']}")
json.dump(out,open("judged.json","w"))
