import sys
exec(open('rank.py').read().split('rows=[]')[0])
rows=[]
for l in open('fort.77'):
    j,k,n,a,e=l.split(); n=abs(int(n)); A=n//8**9; Z=(n//8**6)%512; M=(n//8**5)%8
    rows.append((int(j),f"{SYM[Z]}-{A}{'m' if M else ''}",float(a),float(e)))
tot=sum(a*abs(e) for _,_,a,e in rows); need=(6.1020/5.9760-1)*tot
print("need",need)
for j,nm,a,e in rows:
    if a==0: continue
    s=f"{abs(e):.2E}"   # d.ddE-ee
    for i,c in enumerate(s):
        if not c.isdigit(): continue
        for d in "0123456789":
            if d==c: continue
            t=s[:i]+d+s[i+1:]
            dv=(float(t)-abs(e))*a
            if abs(dv-need)/need<0.03:
                print(f"{j:4d} {nm:9s} {s} -> {t}  dSum={dv/tot*100:+.3f}%  (need {need/tot*100:.3f}%)")
