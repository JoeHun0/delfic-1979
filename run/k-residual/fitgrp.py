import sys, numpy as np
exec(open("score.py").read().split("def score(delta)")[0])   # reuse the data loading
bn={}
for r in ch: bn[int(r[0])]=float(r[4])
tot=O.sum()
def fit1(c):
    v=SH[c]*FISNUM; s=(v@E)/(v@v); return np.linalg.norm(E-s*v)/np.linalg.norm(E), s
print("== single-group fits: group, mass of first nuclide, b, scale (dXRT), as % of that group's XRT, shape residual")
rows=[]
for c in range(1,NC+1):
    if XRT[c]<=0: continue
    r,s=fit1(c); A0=[name(NUC[j]) for j in range(KRM) if MCH[j]==c][0].split("-")[0]
    rows.append((r,c,A0,bn[c],s,100*s/XRT[c]))
rows.sort()
for r,c,A0,b,s,pc in rows[:14]: print(f"  grp {c:2d} A={A0} b={b:+.3f} dXRT={s:+.3e} ({pc:+.1f}% of group) resid {r:.3f}")
print("  ... worst b for reference:", [(f"A={A0}",f"b={b:+.2f}",f"resid {r:.2f}") for r,c,A0,b,s,pc in rows[-3:]])
print("== region J=17..40: J, K, nuclide, group, b, ABUNDO, ERM, contribution, % of K")
for j in range(16,40):
    c=MCH[j]; cont=AB[j]*abs(ERM[j])
    print(f"  J={j+1:3d} K={JRM[j]:3d} {nucname[JRM[j]]:8s} grp {c:2d} b={bn[c]:+.2f} AB={AB[j]:.3e} ERM={ERM[j]:+.3e} contrib={cont:.3e} {100*cont/XRT.sum():.2f}%")
need=E.sum()/FISNUM; print(f"needed dXRT total = {need:+.3e}")
# two-component: best b=-1 group + any single candidate from the candidate list (re-generate quickly: whole-nuclide removals and group scalings)
best=rows[0][1]; v1=SH[best]*FISNUM
print("== two-component fits: group", best, "+ one other group, scales as % of each group")
out=[]
for c in range(1,NC+1):
    if c==best or XRT[c]<=0: continue
    Vm=np.stack([v1,SH[c]*FISNUM],1); s,res,rk,sv=np.linalg.lstsq(Vm,E,rcond=None)
    out.append((np.linalg.norm(E-Vm@s)/np.linalg.norm(E),c,bn[c],100*s[0]/XRT[best],100*s[1]/XRT[c]))
out.sort()
for r,c,b,p1,p2 in out[:8]:
    A0=[name(NUC[j]) for j in range(KRM) if MCH[j]==c][0].split("-")[0]
    print(f"  + grp {c:2d} A={A0} b={b:+.2f}: {p1:+.1f}% of grp {best}, {p2:+.1f}% of grp {c}, resid {r:.3f}")
# soil-shape (FMASS) as second component
fm=np.array([float(r[3]) for r in ch if int(r[0])==1]); fm=fm[np.argsort(-np.array([float(r[2]) for r in ch if int(r[0])==1]))]
Vm=np.stack([v1,fm],1); s,res,rk,sv=np.linalg.lstsq(Vm,E,rcond=None)
print(f"  + FMASS shape (soil): {100*s[0]/XRT[best]:+.1f}% of grp {best}, soil-like term {s[1]:+.3e} (soil total is 9.78e8), resid {np.linalg.norm(E-Vm@s)/np.linalg.norm(E):.3f}")
