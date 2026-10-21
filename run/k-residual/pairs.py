import sys, numpy as np, itertools
exec(open("score.py").read().split("def score(delta)")[0])
bn={int(r[0]):float(r[4]) for r in ch}
need=E.sum()/FISNUM
W=np.abs(ERM); C=np.zeros((INUC,NC+1))
for j in range(KRM): C[:,MCH[j]]+=G[:,j]*W[j]
C*=Y[:,None]
mult={}
for l in open(f"{S}/bt0.txt"):
    i,nu,a0,a,d=l.split(); mult[int(i)]=round(float(a)/float(a0)) if float(a0)>0 else 0
vol=[c for c in range(1,NC+1) if bn.get(c,0)<-0.9 and XRT[c]>1e-9]
units=[]
for c in vol:
    for i in range(INUC):
        v=C[i,c]
        if v>2e-9:
            units.append((v,f"whole yield #{i+1} {nucname[i+1]} (grp {c})"))
            if mult.get(i+1,1)>1: units.append((v/mult[i+1],f"one path of #{i+1} {nucname[i+1]} m={mult[i+1]} (grp {c})"))
for j in range(KRM):
    if MCH[j] in vol and AB[j]*W[j]>2e-9: units.append((AB[j]*W[j],f"whole ERM J={j+1} {nucname[JRM[j]]} (grp {MCH[j]})"))
print(len(units),"units;  need",f"{-need:.3e}")
print("== singles within 10%:")
for v,t in units:
    if abs(v/(-need)-1)<0.10: print(f"  {v/(-need)*100:5.1f}%  {t}")
print("== pairs within 3%:")
for (v1,t1),(v2,t2) in itertools.combinations(units,2):
    if t1.split("#")[-1].split(" ")[0]==t2.split("#")[-1].split(" ")[0] and "#" in t1 and "#" in t2: continue
    if abs((v1+v2)/(-need)-1)<0.03: print(f"  {(v1+v2)/(-need)*100:5.1f}%  {t1}  +  {t2}")
