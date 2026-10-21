import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import build
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); A0,A1=int(sys.argv[3]),int(sys.argv[4])
line=[]
for k,v in enumerate(N):
    if not v: continue
    I=info(v)
    if A0<=I["A"]<=A1:
        e=Y0[k]*div[k]
        line.append(f"{I['A']} {I['Z']}{'A' if I['M'] else ''}={('%.4g'%e) if e else '-'}")
print("  ".join(line))
