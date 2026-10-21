"""Our NUCLID/DCON/BRANCH written as 1968 TRAN cards: (A,iso,Z, T mantissa, unit, exp, branch, dA,diso,dZ)."""
import sys, os, math, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph import load, info, daughters
N,_=load(sys.argv[1]); dcon=[float(l.split()[4]) for l in open(sys.argv[1])]
br=[float(x) for x in open(sys.argv[2]).read().split()]
UNIT={1:1,2:60,3:3600,4:86400,5:3.15576e7}
out=[]; ibr=0
for k,v in enumerate(N):
    if not v: continue
    I=info(v); low=I["low"]; nb=4-(low%8) if low not in (0,4) and low%8<4 else 0
    fr=br[ibr:ibr+nb]; ibr+=nb
    ds=daughters(N,k); T=math.log(2)/dcon[k] if dcon[k]>0 else None
    base=dict(k=k,A=I["A"],iso=I["M"],Z=I["Z"],T=T,lam=dcon[k],head=I["head"])
    if not ds: out.append(dict(base,b=None,d=None)); continue
    for n,j in enumerate(ds):
        J=info(N[j]); out.append(dict(base,b=fr[n] if nb else 1.0,d=(J["A"],J["M"],J["Z"])))
json.dump(out,open(sys.argv[3],"w"))
print(len(out),"cards;", sum(1 for c in out if c["d"] is None),"end-of-chain")
