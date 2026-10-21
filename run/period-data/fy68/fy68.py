"""Compare the 1968 P239HE yields (Tompkins 1968 PAM data tape, set-1 FY cards, last column) with our 1979 block."""
import sys, os, re, glob; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import build
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); O=sys.argv[3]
key={}
for k,v in enumerate(N):
    if v: I=info(v); key[(I["A"],I["Z"],I["M"])]=k
def mant(x):
    x=abs(x)
    if x==0: return None
    s=f"{x:.4e}"; m=s.split("e")[0].replace(".","").rstrip("0"); return m[:4]
rows=[]; seen=set()
for p in range(220,232):
    for ln in open(f"{O}/fy{p}.txt"):
        m=re.search(r"([0-9IlS])F[YVI\?i]\b", ln)
        if not m or m.group(1) not in "1Il": continue
        head=ln[:m.start()]
        h=re.match(r"\s*0?(\d{2,3})\s+0?(\d{2})(A?)", head.replace("'","").replace("?","7").replace("O","0"))
        if not h: continue
        A=int(h.group(1)); Z=int(h.group(2)); iso=h.group(3)=="A"
        k=key.get((A,Z,1 if iso else 0))
        if k is None and not iso: k=key.get((A,Z,0))
        if k is None: rows.append((p,A,Z,iso,None,None,ln.strip()[:110],"no such nuclide")); continue
        seen.add(k)
        expected=Y0[k]*div[k]
        toks=re.findall(r"\d*[.:;!]\d+|\d+\.\d*|\d+", head[h.end():])
        toks=[t.replace(":",".").replace(";",".").replace("!",".") for t in toks]
        tail=toks[-3:]
        ok=False
        if expected==0:
            ok = not any(re.search(r"[1-9]",t) for t in toks[-1:]) or len(toks)<6
        else:
            me=mant(expected)
            for t in tail:
                d=t.replace(".","").lstrip("0").rstrip("0")
                if d and me and (d[:len(me)]==me or me.startswith(d[:3]) and len(d)>=3): ok=True
        rows.append((p,A,Z,iso,k,expected,ln.strip()[:120],"ok" if ok else "CHECK"))
bad=[r for r in rows if r[7]!="ok"]
print(f"{len(rows)} FY set-1 lines parsed, {sum(1 for r in rows if r[7]=='ok')} matched, {len(bad)} to check; nuclides covered {len(seen)} of {sum(1 for v in N if v)}")
import json; json.dump(bad, open("fy68_check.json","w"))
missing=[k for k,v in enumerate(N) if v and k not in seen]
json.dump(missing, open("fy68_missing.json","w")); print("nuclides with no parsed line:", len(missing))
