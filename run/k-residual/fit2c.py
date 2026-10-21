import sys, numpy as np
exec(open("score.py").read().split("def score(delta)")[0])
bn={int(r[0]):float(r[4]) for r in ch}
# FMASS per class, in the same (largest-first) order
fm_by_ld={int(r[1]):float(r[3]) for r in ch}; fm=np.array([fm_by_ld[i+1] for i in order])
print("sum FMASS =", fm.sum())
v1=SH[17]*FISNUM          # a b=-1 group shape (A=89)
for label,v2 in (("soil/FMASS shape",fm),("refractory b=0 group (A=99)",SH[26]*FISNUM)):
    Vm=np.stack([v1,v2],1); s,res,rk,sv=np.linalg.lstsq(Vm,E,rcond=None)
    r=np.linalg.norm(E-Vm@s)/np.linalg.norm(E)
    print(f"b=-1 group {s[0]:+.3e} XRT ({100*s[0]/XRT[17]:+.1f}% of A=89)  +  {label}: {s[1]:+.3e} (FP units; soil total is 9.78e8; as fraction of ours {s[1]/O.sum()*100:+.2f}%)  resid {r:.3f}")
# residual pattern after the single b=-1 fit, per class (largest first), in units of printed-digit noise (~1e-5*FP)
s=(v1@E)/(v1@v1); R=E-s*v1
print("residual/FP after b=-1 fit, largest->smallest class (x1e4):", np.round(R/P*1e4,1))
