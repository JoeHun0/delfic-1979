import sys, numpy as np
from collections import defaultdict
raw=[]
for l in open(sys.argv[2]).read().split("\n")[1:]:
    if not l.strip(): continue
    for k in range(0,70,14): raw.append(l[k:k+14].strip())
byA=defaultdict(lambda: defaultdict(float)); cells=defaultdict(list)
for l in open(sys.argv[1]):
    i,nu,a0,a,d=l.split(); i=int(i); nu=abs(int(nu)); A=nu//8**9; Z=(nu//8**6)%512; low=nu%8**5
    a0=float(a0); a=float(a); m=max(round(a/a0),1) if a0>0 and low not in (0,4) else 1
    byA[A][Z]+=a0*m; cells[(A,Z)].append(f"#{i} {raw[i-1]}x{m}")
sds=[]; trip=[]
for A,zs in sorted(byA.items()):
    ymax=max(zs.values()) if zs else 0
    pts=[(Z,y) for Z,y in sorted(zs.items()) if y>0.03*ymax]
    for k in range(1,len(pts)-1):
        (z0,y0),(z1,y1),(z2,y2)=pts[k-1],pts[k],pts[k+1]
        if z1-z0!=1 or z2-z1!=1: continue
        sd=np.log(y0)-2*np.log(y1)+np.log(y2); sds.append(sd); trip.append((A,z1,sd,y0,y1,y2))
med=np.median(sds); mad=np.median(np.abs(np.array(sds)-med))
print(f"curvature: median {med:.3f}, MAD {mad:.3f}, n={len(sds)}")
bad=[t for t in trip if abs(t[2]-med)>4*mad]
for A,z,sd,y0,y1,y2 in sorted(bad,key=lambda t:-abs(t[2]-med)):
    print(f"  A={A} centre Z={z}: sd {sd:+.2f} ({(sd-med)/mad:+.1f} MAD)  y(Z-1,Z,Z+1) = {y0:.3g}, {y1:.3g}, {y2:.3g}   centre cells: {cells[(A,z)]}")
