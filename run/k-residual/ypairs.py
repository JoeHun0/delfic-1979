import sys, numpy as np
from collections import defaultdict
exec(open("score.py").read().split("def score(delta)")[0])
TARGET=18793.03; need_y=TARGET-Y[:INUC].sum()
W=np.abs(ERM)
def dfp_for_yield(i,dy):
    delta=np.zeros(NC+1); np.add.at(delta,MCH,dy*G[i]*W); return FISNUM*(delta[:,None]*SH).sum(0)
alts=[]
for i in range(INUC):
    s=raw[i]
    if not s: continue
    for p,ch_ in enumerate(s):
        if not ch_.isdigit(): continue
        for d in "0123456789":
            if d==ch_: continue
            s2=s[:p]+d+s[p+1:]
            try: v=float(s2)
            except ValueError: continue
            alts.append((i,s,s2,v-Y[i]))
    if s=="0.":                                   # a zero cell that might really hold a small value: skip (unbounded)
        pass
print(len(alts),"single-glyph yield alternatives; need dY =",round(need_y,4))
byk=defaultdict(list)
for a,(i,s,s2,dy) in enumerate(alts): byk[round(dy,2)].append(a)
tol=0.006; pairs=[]
for a,(i,s,s2,dy) in enumerate(alts):
    r=need_y-dy
    for key in (round(r-0.01,2),round(r,2),round(r+0.01,2)):
        for b in byk.get(key,[]):
            if b<=a or alts[b][0]==i: continue
            if abs(dy+alts[b][3]-need_y)<tol: pairs.append((a,b))
print(len(pairs),"pairs close the yield total to 0.006")
E0=np.linalg.norm(E)
res=[]
cache={}
def dfp(a):
    if a not in cache: i,s,s2,dy=alts[a]; cache[a]=dfp_for_yield(i,dy)
    return cache[a]
for a,b in pairs:
    v=dfp(a)+dfp(b); res.append((np.linalg.norm(E-v)/E0, v.sum()/E.sum(), a, b))
res.sort()
print("baseline (no change): resid 1.000; best pairs by FP-shape residual:")
for r,f,a,b in res[:15]:
    A=alts[a]; Bb=alts[b]
    print(f"  resid {r:.3f} f={f:+.2f} | #{A[0]+1} {nucname[A[0]+1]} {A[1]}->{A[2]} ({A[3]:+.3f}) + #{Bb[0]+1} {nucname[Bb[0]+1]} {Bb[1]}->{Bb[2]} ({Bb[3]:+.3f})")
