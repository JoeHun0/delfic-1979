exec(open('rank.py').read().split('rows=[]')[0])
R=[]
for l in open('fort.82'):
    i,n,y,s=l.split(); n=abs(int(n)); R.append((int(i),f"{SYM[(n//8**6)%512]}-{n//8**9}{'m' if (n//8**5)%8 else ''}",float(y),float(s) if "E" in s else 0.0))
tot=sum(y*s for _,_,y,s in R); print("linear total",tot, "(fort.77 total 4.107898e-06)")
need=0.021084*tot
print("top sensitivities (share of total):")
for i,nm,y,s in sorted(R,key=lambda r:-r[2]*r[3])[:15]: print(f"  #{i} {nm} y={y} share={y*s/tot*100:.2f}%")
print("single-glyph yield changes within 0.1% of target:")
for i,nm,y,s in R:
    txt=f"{y:.6E}"  # d.ddddddE+ee  (printed as .dddddd E+ee)
    m,e=txt.split('E'); dig=m.replace('.','')
    for p in range(len(dig)):
        for d in "0123456789":
            if d==dig[p]: continue
            nd=dig[:p]+d+dig[p+1:]; v=float(nd[0]+'.'+nd[1:]+'E'+e)
            dv=(v-y)*s
            if abs(dv-need)/need<0.05: print(f"  #{i} {nm} {y} -> {v}  K x{1+dv/tot:.5f} (need 1.02108)")
    for de in (-1,1):
        v=y*10**de; dv=(v-y)*s
        if abs(dv-need)/need<0.05: print(f"  #{i} {nm} {y} -> {v} (exponent)  K x{1+dv/tot:.5f}")
