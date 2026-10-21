import sys, os, re, html, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import build
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); BK=sys.argv[3]
key={}
for k,v in enumerate(N):
    if v: I=info(v); key[(I["A"],I["Z"],I["M"])]=k
def rows_of(model,p):
    t=open(f"{BK}/out/{model}/p{p:03d}.md").read()
    if "<td>" in t:
        out=[]
        for tr in re.findall(r"<tr>(.*?)</tr>", t, re.S):
            out.append(" ".join(html.unescape(x).strip() for x in re.findall(r"<td>(.*?)</td>", tr, re.S)))
        return out
    return t.split("\n")
def parse(line):
    t=line.replace(",",".").replace(":",".").split()
    fy=[i for i,x in enumerate(t) if re.fullmatch(r"[1Il]?F[YV\?I]|[1Il]F",x) or x.endswith("FY")]
    if not fy or len(t)<3: return None
    i=fy[0]; seq=t[i+1] if i+1<len(t) else ""
    m=re.match(r"0?(\d{2,3})$", t[0]); z=re.match(r"0?(\d{2})(A?)(.*)$", t[1]) if len(t)>1 else None
    if not m or not z: return None
    A=int(m.group(1)); Z=int(z.group(1)); iso=z.group(2)=="A"
    mid=t[2:i]
    if z.group(3): mid=[z.group(3)]+mid
    exp=0
    if mid and re.fullmatch(r"-\d", mid[-1]): exp=-int(mid[-1][1]); mid=mid[:-1]
    elif mid and mid[-1] in ("-","~","—","."): mid=mid[:-1]
    if mid and re.fullmatch(r"-\d", mid[-1]): exp=-int(mid[-1][1]); mid=mid[:-1]
    cand=[x for x in mid if re.search(r"\d",x) and (len(x.replace("-",""))>=3 or "." in x and len(x)>=2)]
    if mid and len(mid)>=1 and len(mid[0])<=2 and mid[0] in cand and len(cand)>1: cand=cand[1:]
    val=None
    if cand:
        s=cand[-1].lstrip("-")
        try: val=float(s)*10**exp
        except: val=None
    return A,Z,iso,val,seq
res={}
for p in range(220,232):
    for model in ("lighton","glm"):
        for line in rows_of(model,p):
            r=parse(line)
            if not r: continue
            A,Z,iso,val,seq=r
            k=key.get((A,Z,1 if iso else 0))
            if k is None: continue
            res.setdefault(k,{}).setdefault(model,(val,p,seq))
out=[]; nmatch=0
for k,v in enumerate(N):
    if not v: continue
    I=info(v); exp=Y0[k]*div[k]
    got=res.get(k,{})
    vals=[g[0] for g in got.values()]
    def same(a,b):
        if a is None: return b==0
        if b==0: return a==0
        return abs(a/b-1)<0.003
    ok=any(same(x,exp) for x in vals) if vals else False
    if ok: nmatch+=1
    else: out.append((k+1,f"{I['A']}-{I['Z']}{'m' if I['M'] else ''}",exp,{m:(g[0],g[1],g[2]) for m,g in got.items()},raw[k],div[k]))
print(f"matched {nmatch} of {sum(1 for v in N if v)} nuclides; {len(out)} to check")
for r in out: print(r)
json.dump(out,open("fy68_mismatch.json","w"))
