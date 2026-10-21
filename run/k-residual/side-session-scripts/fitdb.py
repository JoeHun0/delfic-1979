import numpy as np
exec(open('fit2.py').read().split('res=[]')[0])
def dshape(b,h=1e-4): return (shape(b+h)-shape(b-h))/(2*h)
tot=ours  # includes soil
res=[]
for i,x in enumerate(X):
    if x<=0: continue
    for base_name,base in (("uniform",tot),):
        dv=FIS*x*dshape(Bk[i])
        M=np.stack([base[m],dv[m]],1); c,*_=np.linalg.lstsq(M,D[m],rcond=None); r=D[m]-M@c
        res.append((np.sqrt((r**2).sum()/(D[m]**2).sum()),i+1,grp[i],Bk[i],c[0]*100,c[1],x/sum(X)*100))
res.sort()
for r in res[:10]: print("resid %.4f LC%d A=%d b=%+.3f share %.2f%% : uniform %+.3f%%, db=%+.3f"%(r[0],r[1],r[2],r[3],r[6],r[4],r[5]))
