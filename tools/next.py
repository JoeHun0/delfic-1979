"""Make one review sheet of the next N unresolved lines. usage: next.py <workdir> [N]"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw
wd=Path(sys.argv[1]); N=int(sys.argv[2]) if len(sys.argv)>2 else 12
done={tuple(l.split("\t")[:2]) for l in (wd/"corrections.tsv").read_text().splitlines() if l and not l.startswith("#")}
items=[]
for f in sorted((wd/"review-sheets").glob("sheet-*.txt")):
    for l in f.read_text().splitlines():
        x=l.split("\t")
        if (x[1],x[2]) not in done and not (174 <= int(x[1][1:]) <= 182): items.append(x)
items=items[:N]; strips=[]
for k,x in enumerate(items):
    pg=int(x[1][1:]); i=int(x[2]); J=json.load(open(wd/"lines"/f"p{pg:03d}.json")); m=J["meta"]; L=J["lines"][i-1]
    im=Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
    x0=int(m["col1_x"]-m["pitch"]/2)-2; x1=int(m["col1_x"]+71.5*m["pitch"])+2
    c=im.crop((x0,max(L["y0"]-5,0),x1,L["y1"]+5)).convert("RGB")
    row=Image.new("RGB",(c.width+60,c.height),"white"); ImageDraw.Draw(row).text((5,c.height//3),str(k+1),fill=(0,0,0)); row.paste(c,(60,0)); strips.append(row)
    print(f"{k+1}\t{x[1]}\t{x[2]}\t{x[3]}\t{x[4]}\t{x[5]}\t{x[6][:105]}")
if strips:
    W=max(r.width for r in strips); H=sum(r.height for r in strips); s=Image.new("RGB",(W,H),"white"); y=0
    for r in strips: s.paste(r,(0,y)); y+=r.height
    s.resize((int(W*0.72),int(H*0.72)),Image.LANCZOS).save(wd/"review-sheets"/"next.png")
print("remaining", len([1 for f in sorted((wd/'review-sheets').glob('sheet-*.txt')) for l in f.read_text().splitlines() if tuple(l.split('\t')[1:3]) not in done and not (174 <= int(l.split('\t')[1][1:]) <= 182)]))
