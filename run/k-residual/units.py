import sys, numpy as np
exec(open("score.py").read().split("def score(delta)")[0])
bn={int(r[0]):float(r[4]) for r in ch}
need=E.sum()/FISNUM
W=np.abs(ERM)                                  # weight per J
# contribution of each initial yield i to each group's XRT
C=np.zeros((INUC,NC+1))
for j in range(KRM): C[:,MCH[j]]+=G[:,j]*W[j]
C*=Y[:,None]
vol=[c for c in range(1,NC+1) if bn.get(c,0)<-0.9 and XRT[c]>1e-9]
print("fully volatile groups with activity:", [(c,bn[c]) for c in vol])
print(f"need {need:+.3e}; per-group XRT:", {c:f"{XRT[c]:.2e}" for c in vol})
print("== yield contributions to these groups (atoms-> XRT), with 'per path' = contribution / multiplicity:")
mult={}
for l in open(f"{S}/bt0.txt"):
    i,nu,a0,a,d=l.split(); mult[int(i)]=round(float(a)/float(a0)) if float(a0)>0 else 0
rows=[]
for c in vol:
    for i in range(INUC):
        if C[i,c]>1e-10:
            m=max(mult.get(i+1,1),1); rows.append((C[i,c],c,i+1,nucname[i+1],raw[i],m,C[i,c]/m))
rows.sort(reverse=True)
for v,c,i,nm,s,m,pp in rows[:30]:
    flag=" <-- one path ~ need" if abs(pp/abs(need)-1)<0.08 else (" <-- whole ~ need" if abs(v/abs(need)-1)<0.08 else "")
    print(f"  grp {c:2d} #{i:3d} {nm:8s} Y={s:>12s} m={m} -> {v:.3e}  per path {pp:.3e}  ({v/abs(need)*100:5.0f}% / {pp/abs(need)*100:5.0f}% of need){flag}")
print("== ERM entries in these groups: contribution vs need")
for j in range(KRM):
    if MCH[j] in vol and AB[j]*W[j]>1e-9:
        v=AB[j]*W[j]; print(f"  J={j+1:3d} {nucname[JRM[j]]:8s} grp {MCH[j]:2d} ERM {ERM[j]:+.3e} contrib {v:.3e} ({v/abs(need)*100:4.0f}% of need)")
