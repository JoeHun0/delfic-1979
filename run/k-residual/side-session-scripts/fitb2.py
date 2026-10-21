import numpy as np
exec(open('fit2.py').read().split('res=[]')[0])
bs=np.round(np.arange(-1.0,0.001,0.01),2); S={b:FIS*shape(b) for b in bs}
res=[]
for i,b1 in enumerate(bs):
    for b2 in bs[i+1:]:
        M=np.stack([S[b1][m],S[b2][m]],1); c,*_=np.linalg.lstsq(M,D[m],rcond=None); r=D[m]-M@c
        res.append((np.sqrt((r**2).sum()/(D[m]**2).sum()),b1,b2,c[0]*S[b1].sum()/ours.sum()*100,c[1]*S[b2].sum()/ours.sum()*100))
res.sort()
for r in res[:10]: print("resid %.4f b1=%+.2f adds %+.3f%%  b2=%+.2f adds %+.3f%%"%(r[0],r[1],r[3],r[2],r[4]))
# noise floor: 0.5 last digit
noise=0.5*10**(np.floor(np.log10(pr))-4)
print("noise floor resid ~ %.4f"%(np.sqrt((noise[m]**2).sum()/(D[m]**2).sum())))
