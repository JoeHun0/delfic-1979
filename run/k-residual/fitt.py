import sys, numpy as np
exec(open("score.py").read().split("def score(delta)")[0])
def loadG(f):
    L=open(f).read().split("\n"); n=(KRM+9)//10
    return np.array([[float(x) for x in " ".join(L[1+n+i*n:1+n+(i+1)*n]).split()] for i in range(INUC)])
for t in (3700,3500):
    Gt=loadG(f"resp{t}.txt")
    d=np.zeros(NC+1)
    for j in range(KRM): d[MCH[j]]+=(Y@Gt[:,j]-Y@G[:,j])*abs(ERM[j])
    v=FISNUM*(d[:,None]*SH).sum(0); s=(v@E)/(v@v)
    print(f"TIME {t}: total dXRT {d.sum():+.3e} per {t-3600:+d} s; shape fit scale {s:+.3f} -> implied dt = {s*(t-3600):+.1f} s, resid {np.linalg.norm(E-s*v)/np.linalg.norm(E):.3f}")
