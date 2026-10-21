import sys
SYM=("n H He Li Be B C N O F Ne Na Mg Al Si P S Cl Ar K Ca Sc Ti V Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr Rb Sr "
 "Y Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I Xe Cs Ba La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb Lu Hf").split()
rows=[]
for l in open(sys.argv[1]):
    j,k,n,a,e=l.split(); j=int(j);k=int(k);n=abs(int(n));a=float(a);e=float(e)
    A=n//8**9; Z=(n//8**6)%512; M=(n//8**5)%8
    rows.append((j,k,f"{SYM[Z]}-{A}{'m' if M else ''}",a,e,a*abs(e)))
tot=sum(r[5] for r in rows)
print("total",tot)
for r in sorted(rows,key=lambda r:-r[5])[:45]:
    print(f"{r[0]:4d} {r[1]:4d} {r[2]:10s} A={r[3]:.4e} ERM={r[4]: .3e} contrib={r[5]/tot*100:6.2f}%")
