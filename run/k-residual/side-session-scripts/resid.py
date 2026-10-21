import numpy as np
exec(open('fit2.py').read().split('res=[]')[0])
for b in (-0.59,-0.602):
    v=shape(b)*FIS; a=(v[m]@D[m])/(v[m]@v[m]); r=D-a*v
    print("b",b,"adds %.3f%%"%(a*v.sum()/ours.sum()*100))
    print("  resid/printed in units of last printed digit:", np.round(r/(pr/1e4*10**0)/ (10**(np.floor(np.log10(pr))-4)) * (pr/1e4)/ (10**(np.floor(np.log10(pr))-4)),1) if False else np.round(r/10**(np.floor(np.log10(pr))-4),1))
