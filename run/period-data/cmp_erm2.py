"""1968 ERM cards (GLM-OCR of pp. 254-257) vs our ERM/JRM, aligned by (A, Z, 3-digit value)."""
import re, sys, glob, os, difflib, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph import load, info
B,OCR,BT=sys.argv[1:4]
src=open(f"{B}/run/dtm_port.f").read()
def data(name):
    v=[]
    for m in re.finditer(r"DATA \((%s\s*)\(I\),I=\s*\d+,\s*\d+\s*\)/(.*?)/"%name, src, re.S):
        v+=[x.strip() for x in re.sub(r"\n     \$","",m.group(2)).split(",")]
    return [float(x) for x in v if x]
erm=data("ERM"); jrm=[int(x) for x in data("JRM")]
N,_=load(BT)
ours=[]
for j,(e,k) in enumerate(zip(erm,jrm)):
    if e==0: continue
    I=info(N[k-1]); ours.append((j+1,I["A"],I["Z"],I["M"],f"{abs(e):.2E}",e<0))
fix=lambda s: s.translate(str.maketrans("OoDQlIi,","0000111."))
cards=[]; seen=set()
for fn in sorted(glob.glob(f"{OCR}/*.md")):
    for ln in open(fn):
        m=re.match(r"\s*(\d{2,3})\s+(\d{2})\s+(\S+)", ln)
        if not m: continue
        v=fix(m.group(3)); mm=re.match(r"\d?\.(\d{3})E-?(\d\d)$", v)
        if not mm: continue
        key=(int(m.group(1)),int(m.group(2)),mm.group(1),int(mm.group(2)))
        sq=re.search(r"ERM\s+(\d+)", ln); sq=int(sq.group(1)) if sq else None
        cards.append(key+(sq,fn[-8:-3]))
# drop strip-overlap duplicates (same card twice in a row)
ded=[]
for c in cards:
    if any(d[:4]==c[:4] for d in ded[-6:]): continue
    ded.append(c)
def okey(o):  # 1968 prints 0.xxxE-(n-1) for our x.xxE-n
    m=o[4]; return (o[1],o[2],m[0]+m[2:4],-(int(m.split("E")[1])+1))
A=[c[:4] for c in ded]; Bk=[okey(o) for o in ours]
sm=difflib.SequenceMatcher(a=A,b=Bk,autojunk=False)
same=0; out=[]
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag=="equal": same+=i2-i1; continue
    out.append((tag,[ded[i] for i in range(i1,i2)],[ours[j] for j in range(j1,j2)]))
print(f"1968 ERM cards read: {len(ded)}; ours nonzero: {len(ours)}; identical (A,Z,value): {same}")
for t,a,b in out: print(t,"| 1968:",a,"| ours:",b)
