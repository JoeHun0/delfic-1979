"""Per-cell confidence for the P239HE yield block: leave-own-card-out kNN glyph scores plus OCR-model agreement."""
import sys, re, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(sys.argv[1])/"tools"))
import glyphs
wd=Path(sys.argv[1]); deck=Path(sys.argv[2])
cards=[l for l in deck.read_text().split("\n")[1:] if l.strip()]
def loc(card):                      # 1-based card -> page, line
    if card<=39: return 205,card+22
    if card<=99: return 206,card-38
    return 207,card-98
V=glyphs.verified_cards(wd)
# training cells with their card id
X=[];Y=[];ID=[]; cache={}
for (pg,i),card in V.items():
    if pg not in cache: cache[pg]=glyphs.load(wd,pg)
    J,a=cache[pg]; L=J["lines"][i-1]
    for col in L["cols"]:
        if col>70 or col>len(card) or card[col-1]==" ": continue
        v,hh=glyphs.cell_img(a,L,J["meta"],col)
        if v is None: continue
        vn=(v-v.mean())/(v.std()+1e-9); X.append(vn.ravel()); Y.append(card[col-1]); ID.append((pg,i))
X=np.array(X); Y=np.array(Y); ID=np.array([p*1000+i for p,i in ID])
chars=glyphs.CHARS
def scores(v, own):
    vn=((v-v.mean())/(v.std()+1e-9)).ravel(); s=X@vn/len(vn); mask=ID!=own
    out={}
    for c in chars:
        m=s[(Y==c)&mask]
        out[c]=np.sort(m)[-3:].mean() if len(m) else -1
    return out
def ocr_lines(model,pg):
    f=wd/f"ocr-{model}"/f"p{pg:03d}.tsv"; d={}
    for r in f.read_text().splitlines():
        x=r.split("\t")
        if len(x)>5: d[int(x[0])]=x[5].split(" || ")[0]
    return d
ocr={m:{pg:ocr_lines(m,pg) for pg in (205,206,207)} for m in ("glm","lighton")}
num=re.compile(r"\.\d{6}E[+-]\d\d|0\.|[.\d]+E[+-]?\d+")
rows=[]
for ci,card in enumerate(cards,1):
    pg,ln=loc(ci); J,a=cache.get(pg) or glyphs.load(wd,pg); cache[pg]=(J,a); L=J["lines"][ln-1]; c=card.ljust(70)
    toks={m:num.findall(ocr[m][pg].get(ln,"").replace(" ","")) for m in ocr}
    for f in range(5):
        fld=c[f*14:(f+1)*14]; val=fld.strip(); k=(ci-1)*5+f+1
        if k>692 or not val or val=="0.": continue
        worst=(9,None,None,None)
        for p_ in range(f*14,(f+1)*14):
            ch=c[p_]
            if ch not in "0123456789": continue
            col=p_+1
            if col not in L["cols"]: continue
            v,hh=glyphs.cell_img(a,L,J["meta"],col)
            if v is None: continue
            sc=scores(v,pg*1000+ln)
            allowed="0123456789"
            best=sorted(allowed,key=lambda q:-sc[q])
            alt=best[0] if best[0]!=ch else best[1]
            marg=sc[ch]-sc[alt]
            if marg<worst[0]: worst=(marg,col-f*14,ch,alt)
        ag=[]
        for m,t in toks.items():
            ag.append(m+(":ok" if f<len(t) and t[f]==val else (":"+t[f] if f<len(t) else ":-")))
        rows.append((worst[0],k,pg,ln,f+1,val,worst[1],worst[2],worst[3]," ".join(ag)))
rows.sort()
json.dump(rows,open("lowconf.json","w"))
print("lowest glyph margins (negative = the classifier prefers another digit at that position):")
for marg,k,pg,ln,f,val,pos,ch,alt,ag in rows[:40]:
    print(f"#{k:3d} p{pg} L{ln} f{f} {val:>12s}  pos {pos} '{ch}' vs '{alt}' margin {marg:+.3f}   {ag}")
