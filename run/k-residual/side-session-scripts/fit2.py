import numpy as np, itertools
exec(open('realign.py').read().split('def fp')[0])
D=pr-ours; m=np.arange(30)!=20
V={i:FIS*x*shape(Bk[i]) for i,x in enumerate(X) if x>0}
names={}
for l in open('fort.77'):
    pass
res=[]
for i,j in itertools.combinations(V,2):
    M=np.stack([V[i][m],V[j][m]],1); c,*_=np.linalg.lstsq(M,D[m],rcond=None)
    if (c<0).any(): continue
    r=D[m]-M@c; res.append((np.sqrt((r**2).sum()/(D[m]**2).sum()),i+1,j+1,c[0],c[1],V[i].sum()*c[0]/ours.sum(),V[j].sum()*c[1]/ours.sum()))
res.sort()
for r in res[:15]:
    print("resid %.4f  LC%d(A=%d) x%.3f adds %.2f%%   LC%d(A=%d) x%.3f adds %.2f%%"%(r[0],r[1],grp[r[1]-1],r[3],r[5]*100,r[2],grp[r[2]-1],r[4],r[6]*100))
