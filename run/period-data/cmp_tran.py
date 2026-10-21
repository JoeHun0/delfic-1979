"""Readings of the 1968 TRAN cards (OCR models + PDF text layer) vs our cards, aligned by sequence number."""
import sys, re, json, glob, os, math
from collections import defaultdict
B=sys.argv[1]; exp=json.load(open(sys.argv[2]))
UNIT={1:1,2:60,3:3600,4:86400,5:3.15576e7}
fix=lambda s: s.translate(str.maketrans("OoDQUlIi|SBZ,","000001111582."))
def cells_html(t):
    for tr in re.findall(r"<tr.*?</tr>", t, re.S):
        cs=re.findall(r"<(t[hd])[^>]*>(.*?)</t[hd]>", tr, re.S)
        if len(cs)>1 and cs[0][0]=="th" and cs[1][0]=="td": cs=cs[1:]     # pandas index
        elif cs and cs[0][0]=="th" and cs[0][1].strip()=="": cs=cs[1:]
        yield [re.sub(r"<[^>]+>","",c).strip() for _,c in cs]
def cells_text(t):
    for ln in t.splitlines():
        yield ln.replace("|"," ").split()
def card(toks):
    """tokens of one line -> (seq, fields) or None. Last numeric token after TRAN-ish word is seq."""
    toks=[x for x in toks if x!=""]
    w=[i for i,x in enumerate(toks) if re.fullmatch(r"[TIY1][RNP][A4][NMH]N?|TRAN", x)]
    if not w: return None
    i=w[-1]; seq=fix("".join(toks[i+1:i+2]))
    if not seq.isdigit(): return None
    f=[fix(x) for x in toks[:i] if x not in ("",)]
    f=[re.sub(r"^(-?\d*\.\d*)\.", lambda m: m.group(1), x).replace(".", "", x.count(".")-1) if x.count(".")>1 else x for x in f]
    f=[x for x in f if re.fullmatch(r"-?\d+\.?\d*", x)]
    return int(seq), f
def parse(f):
    try:
        A,iso,Z=int(f[0]),int(f[1]),int(f[2])
    except Exception: return None
    if len(f)==3: return dict(A=A,iso=iso,Z=Z,end=True)
    if len(f)!=10: return dict(A=A,iso=iso,Z=Z,bad=f)
    try:
        return dict(A=A,iso=iso,Z=Z,T=float(f[3]),u=int(f[4]),e=int(f[5]),b=float(f[6]),d=[int(f[7]),int(f[8]),int(f[9])])
    except Exception: return dict(A=A,iso=iso,Z=Z,bad=f)
read=defaultdict(dict)
for src,pat,cf in (("lighton",f"{B}/out/lighton/*.md",cells_html),("glm",f"{B}/out/glm/*.md",None),("text",f"{B}/text/*.txt",cells_text)):
    for fn in sorted(glob.glob(pat)):
        t=open(fn).read()
        rows=list(cells_html(t)) if "<tr" in t else list(cells_text(t))
        last=0
        for r in rows:
            c=card(r)
            if not c:
                f=[fix(x) for x in r if x]
                if len(f)==3 and all(re.fullmatch(r"\d+",x) for x in f) and last: c=(last+1,f)
            if c:
                last=c[0]; pr=parse(c[1])
                if pr: pr['file']=os.path.basename(fn)
                read[c[0]].setdefault(src,[]).append(pr)
def same(e,r):
    """which fields of reading r agree with our card e"""
    out={}
    out["id"]= (r["A"],r["iso"],r["Z"])==(e["A"],e["iso"],e["Z"])
    if e["d"] is None: out["rest"]=bool(r.get("end")); return out
    if "T" not in r: return out
    T68=r["T"]*10**r["e"]*UNIT.get(r["u"],float("nan"))
    out["T"]= abs(T68/e["T"]-1)<2e-4
    out["b"]= abs(r["b"]-e["b"])<6e-6
    out["d"]= list(r["d"])==list(e["d"])
    return out
def score(e,r):
    if not r: return -1
    sm=same(e,r); return sum(sm.values())*1.0 + (0.5 if (r["A"],r["Z"])==(e["A"],e["Z"]) else 0)
bycard=defaultdict(dict)
for seq,rs in read.items():
    for s_,rl in rs.items():
     for r in rl:
        cand=[(score(exp[j],r),-abs(j+1-seq),j) for j in range(max(0,seq-6),min(len(exp),seq+5))]
        if not cand: continue
        sc,_,j=max(cand)
        if sc>=1.5 and (s_ not in bycard[j+1] or score(exp[j],bycard[j+1][s_])<sc): bycard[j+1][s_]=r
rep=[]; nconf=0
for i,e in enumerate(exp,1):
    rs=bycard.get(i,{})
    agree={}; 
    for s,r in rs.items():
        if r: 
            for f,v in same(e,r).items(): agree.setdefault(f,[]).append((s,v))
    fields=["id","rest"] if e["d"] is None else ["id","T","b","d"]
    unconf=[f for f in fields if not any(v for s,v in agree.get(f,[]))]
    if unconf: rep.append((i,unconf,e,rs))
    else: nconf+=1
print(f"{len(exp)} cards; {nconf} fully confirmed by >=1 reader; {len(rep)} with unconfirmed fields; seqs read: {len(read)} max {max(read) if read else 0}")
json.dump(rep,open(sys.argv[3],"w"))
strip={}
for i in range(1,len(exp)+1):
    fs=[r["file"] for s_,r in bycard.get(i,{}).items() if r and s_=="glm"]
    if fs: strip[i]=fs[0]
json.dump(strip,open("tran_strip.json","w"))
for i,u,e,rs in rep[:int(sys.argv[4]) if len(sys.argv)>4 else 30]:
    print(i,u, (e['A'],e['iso'],e['Z']), f"T={e['T']}" , e['b'], e['d'], {s:r for s,r in rs.items()})
