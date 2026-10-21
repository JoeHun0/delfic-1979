import sys, numpy as np
from collections import defaultdict
raw=[]
for l in open(sys.argv[2]).read().split("\n")[1:]:
    if not l.strip(): continue
    for k in range(0,70,14): raw.append(l[k:k+14].strip())
rows=[]
for l in open(sys.argv[1]):
    i,nu,a0,a,d=l.split(); i=int(i); nu=abs(int(nu)); A=nu//8**9; Z=(nu//8**6)%512; M=(nu//8**5)%8; low=nu%8**5
    a0=float(a0); a=float(a)
    m=max(round(a/a0),1) if a0>0 and low not in (0,4) else 1
    rows.append((i,A,Z,M,a0,m,raw[i-1]))
# true yield per (A,Z): sum isomers, value*m
byA=defaultdict(lambda: defaultdict(float)); cells=defaultdict(list)
for i,A,Z,M,a0,m,s in rows:
    byA[A][Z]+=a0*m; cells[(A,Z)].append((i,a0,m,s))
out=[]
for A,zs in byA.items():
    pts=[(Z,y) for Z,y in sorted(zs.items()) if y>0]
    if len(pts)<4: continue
    for k,(Z,y) in enumerate(pts):
        others=[p for j,p in enumerate(pts) if j!=k]
        zz=np.array([p[0] for p in others],float); ly=np.log([p[1] for p in others])
        c=np.polyfit(zz,ly,2)
        pred=np.exp(np.polyval(c,Z)); dev=np.log(y/pred)
        out.append((abs(dev),A,Z,y,pred,dev))
out.sort(reverse=True)
print("largest deviations of true yields from a Gaussian fit of the other members (leave-one-out):")
for d,A,Z,y,pred,dev in out[:25]:
    cl=", ".join(f"#{i} {s}x{m}" for i,a0,m,s in cells[(A,Z)])
    print(f"  A={A:3d} Z={Z} true {y:8.3f} predicted {pred:8.3f} (x{np.exp(dev):.2f})  cells: {cl}")
