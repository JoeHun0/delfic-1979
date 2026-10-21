"""Decay graph from the transcribed NUCLID table (BATMAN's encoding) and path counts from chain heads."""
import sys
from functools import lru_cache
def load(bt0):
    N=[]; Y0=[]
    for l in open(bt0):
        i,nu,a0,a,d=l.split(); N.append(int(nu)); Y0.append(float(a0))
    return N,Y0
def info(v):
    a=abs(v); return dict(A=a//8**9, Z=(a//8**6)%512, M=(a//8**5)%8, low=a%8**5, head=v<0)
def daughters(N,k):
    low=abs(N[k])%8**5
    if low in (0,4): return []
    d=[(low//8**p)%8 for p in range(5)]          # d0..d4
    nopt={4:1,2:2,1:3}[d[0]]
    out=[]
    for im,inc in [(4,d[4]),(3,d[3]),(2,d[2])][:nopt]:
        if inc==0: continue
        j=k-inc if d[1]==im else k+inc
        out.append(j)
    return out
def path_counts(N):
    n=len(N); par=[[] for _ in range(n)]
    for k in range(n):
        if N[k]==0: continue
        for j in daughters(N,k): par[j].append(k)
    @lru_cache(None)
    def paths(k):
        return (1 if N[k]<0 else 0)+sum(paths(p) for p in par[k])
    return [paths(k) if N[k] else 0 for k in range(n)]
if __name__=="__main__":
    N,Y0=load(sys.argv[1]); P=path_counts(N)
    # compare with BATMAN multiplicities (atoms at t~0 / ABEGN) for radioactive nuclides
    bad=0
    for k,l in enumerate(open(sys.argv[1])):
        i,nu,a0,a,d=l.split(); a0=float(a0); a=float(a)
        if a0>0 and info(N[k])["low"] not in (0,4):
            m=round(a/a0)
            if m!=P[k]: bad+=1; print("mismatch", i, info(N[k]), "BATMAN", m, "graph", P[k])
    print("radioactive nuclides with yield: graph path counts disagree with BATMAN in", bad, "cases")
    from collections import Counter
    print("path-count distribution:", sorted(Counter(P[k] for k in range(len(N)) if N[k]).items()))
