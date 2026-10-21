import numpy as np
exec(open('soil.py').read().split('a=(soil[m]')[0])
bs=np.round(np.arange(-1.0,0.001,0.01),2); res=[]
for b in bs:
    v=FIS*shape(b); M=np.stack([soil[m],v[m]],1); c,*_=np.linalg.lstsq(M,D[m],rcond=None); r=D[m]-M@c
    res.append((np.sqrt((r**2).sum()/(D[m]**2).sum()),b,c[0],c[1]*v.sum()/ours.sum()*100))
M=np.stack([soil[m],ours[m]],1); c,*_=np.linalg.lstsq(M,D[m],rcond=None); r=D[m]-M@c
print("soil+uniform: resid %.4f soil x%.3f uniform %+.3f%%"%(np.sqrt((r**2).sum()/(D[m]**2).sum()),c[0],c[1]*100))
res.sort()
for r in res[:5]: print("soil+b: resid %.4f b=%+.2f soil x%+.3f chain adds %+.3f%%"%r)
