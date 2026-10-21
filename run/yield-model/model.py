"""Reverse-engineered generator of the 1979 DELFIC P239HE independent-yield block.
true yield per (A,Z) = sum over isomers of file value x path count (stable nuclides: not divided);
y(A,Z) = Y_A * exp(-ln2 (Z-Zp)^2) * r(|Z-Zp|)  with an empirical tail factor r."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import defaultdict
from graph import load, info, path_counts
L2=np.log(2)
def build(bt0, deck):
    N,Y0=load(bt0); P=path_counts(N)
    raw=[]
    for l in open(deck).read().split("\n")[1:]:
        if not l.strip(): continue
        for k in range(0,70,14): raw.append(l[k:k+14].strip())
    raw=raw[:len(N)]
    div=[ (1 if info(v)["low"] in (0,4) else P[k]) if v else 0 for k,v in enumerate(N)]
    chains=defaultdict(lambda: defaultdict(list))
    for k,v in enumerate(N):
        if v: chains[info(v)["A"]][info(v)["Z"]].append(k)
    return N,Y0,P,div,raw,chains
def fit_chain(yz, rfun=None):
    pts=[(Z,y) for Z,y in sorted(yz.items()) if y>0]
    if len(pts)<2: return None
    ymax=max(y for Z,y in pts)
    core=[(Z,y) for Z,y in pts if y>0.3*ymax]
    if len(core)<2: core=sorted(pts,key=lambda p:-p[1])[:2]
    Zc=np.array([p[0] for p in core],float); t=np.log([p[1] for p in core])+L2*Zc**2
    c0,c1=np.linalg.lstsq(np.stack([np.ones_like(Zc),Zc],1),t,rcond=None)[0]
    Zp=c1/(2*L2); amp=np.exp(c0+L2*Zp**2)
    return Zp,amp
if __name__=="__main__":
    N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2])
    pts=[]; bad=[]
    for A in sorted(chains):
        yz={Z:sum(Y0[k]*div[k] for k in ks) for Z,ks in chains[A].items()}
        f=fit_chain(yz)
        if not f: continue
        Zp,amp=f
        for Z,y in yz.items():
            g=amp*np.exp(-L2*(Z-Zp)**2); pts.append((abs(Z-Zp), y/g, A, Z, y, g))
    pts.sort()
    np.save("pts.npy", np.array([p[:2] for p in pts]))
    # empirical tail curve: median ratio in 0.05 bins
    import statistics
    bins=defaultdict(list)
    for d,r,A,Z,y,g in pts: bins[round(d/0.05)*0.05].append(r)
    curve={b:statistics.median(v) for b,v in bins.items()}
    print("tail curve r(|dZ|):", " ".join(f"{b:.2f}:{curve[b]:.3f}" for b in sorted(curve) if 1.7<=b<=2.6))
    out=[]
    for d,r,A,Z,y,g in pts:
        rc=curve[round(d/0.05)*0.05]
        exp_y=g*rc
        if (rc>0.05 and abs(r/rc-1)>0.06) or (rc<=0.05 and y>0.5):
            out.append((abs(y-exp_y),A,Z,d,y,exp_y,r,rc))
    out.sort(reverse=True)
    print("cells off the rule (true yield vs rule), largest absolute deviation first:")
    for dev,A,Z,d,y,e,r,rc in out:
        cells=", ".join(f"#{k+1} {raw[k] or '0'} /{div[k]}" for k in chains[A][Z])
        print(f"  A={A:3d} Z={Z} |dZ|={d:.3f}  true {y:9.4f}  rule {e:9.4f}  diff {y-e:+8.3f}   cells: {cells}")
