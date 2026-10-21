import numpy as np
exec(open('fit.py').read().split('D=pr-ours')[0])
exec(open('align.py').read().split('print("FRATIO chains')[0])
Bk=np.array([float(l.split()[1]) for l in open('fort.79')])
P=[l.split() for l in open('fort.80')]
ps=np.array([float(x[1]) for x in P[:30]]); FM=np.array([float(x[2]) for x in P[:30]]); FIS=float(P[30][1])
def shape(b):
    ecf=1/np.sum(FM*ps**b); cr=1e-4**b; rad=ecf/(1+cr*ecf); return (rad*ps**b+rad*cr)*FM
grp=[];X=[]
for l in open('fort.77'):
    j,k,n,a,e=l.split(); n=abs(int(n))
    if float(e)<0: grp.append(n//8**9); X.append(0.0)
    X[-1]+=float(a)*abs(float(e))
def fp(bidx):
    return sum(FIS*x*shape(Bk[bi]) for x,bi in zip(X,bidx))
coded=fp(range(len(X)))
mass=fp([fr.index(m) for m in grp])
print("coded reproduces ours:", np.max(np.abs(coded/ours-1)))
for nm,f in (("coded",coded),("mass-aligned",mass)):
    r=f/pr; print(nm, "K=%.4e"%(f.sum()/50), "ratio by class:", np.round(r,4), "spread(sd)=%.4f"%np.std(np.delete(r,20)))
