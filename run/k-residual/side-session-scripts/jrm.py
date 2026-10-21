exec(open('rank.py').read().split('rows=[]')[0])
ab={};nm={}
for l in open('fort.81'):
    k,_,n,a,d=l.split(); k=int(k); n=abs(int(n)); ab[k]=float(a) if "E" in a else 0.0
    nm[k]=f"{SYM[(n//8**6)%512]}-{n//8**9}{'m' if (n//8**5)%8 else ''}"
rows=[l.split() for l in open('fort.77')]
tot=sum(float(r[3])*abs(float(r[4])) for r in rows); need=0.021084*tot
for r in rows:
    j,k,e=int(r[0]),int(r[1]),abs(float(r[4]))
    for k2 in ab:
        dv=(ab[k2]-ab[k])*e
        if abs(dv-need)/need<0.005:
            print(f"ERM#{j} JRM {k}({nm[k]}) -> {k2}({nm[k2]})  d={dv/tot*100:.3f}%")
