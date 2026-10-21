exec(open('rank.py').read().split('rows=[]')[0])
B={}
for l in open('fort.78'):
    lc,ld,b,ps,v=l.split(); B[int(lc)]=float(b)
ch=[];tot=0
for l in open('fort.77'):
    j,k,n,a,e=l.split(); n=abs(int(n)); A=n//8**9; Z=(n//8**6)%512; M=(n//8**5)%8
    if float(e)<0: ch.append([])
    ch[-1].append((int(j),int(k),f"{SYM[Z]}-{A}{'m' if M else ''}",float(a),float(e))); tot+=float(a)*abs(float(e))
need=0.021084*tot
for i,c in enumerate(ch,1):
    b=B.get(i)
    if b is None or not -0.625<b<-0.57: continue
    print(f"chain {i} b={b:+.3f}")
    for j,k,nm,a,e in c:
        print(f"   ERM#{j:3d} nuc#{k:3d} {nm:9s} ABUNDO={a:.4e} ERM={e:+.3e}  dERM needed={need/a if a else 0:.3e}")
