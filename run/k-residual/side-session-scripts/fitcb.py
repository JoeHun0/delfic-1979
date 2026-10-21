import numpy as np
exec(open('soil.py').read().split('a=(soil[m]')[0])
bs=np.round(np.arange(-1.0,0.001,0.005),3); res=[]
for i,x in enumerate(X):
    if x<=0: continue
    old=FIS*x*shape(Bk[i])
    for b in bs:
        new=FIS*x*shape(b)
        # D = (1+a)*new - old  -> D+old = (1+a)*new
        y=D+old; k=(new[m]@y[m])/(new[m]@new[m]); r=y[m]-k*new[m]
        res.append((np.sqrt((r**2).sum()/(D[m]**2).sum()),i+1,grp[i],Bk[i],b,(k-1)*100,x/sum(X)*100))
res.sort()
for r in res[:12]: print("resid %.4f LC%d A=%d b %+.3f -> %+.3f  chain x%+.1f%%  (share %.2f%%)"%r)
