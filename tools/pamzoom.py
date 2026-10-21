"""Zoom PAM lines at native resolution (no downscale). usage: pamzoom.py <wd> <page> <first> <count> <field_from> <field_to> <out>"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
wd=Path(sys.argv[1]); pg,a,n,f0,f1=map(int,sys.argv[2:7]); out=sys.argv[7]
J=json.load(open(wd/"lines"/f"p{pg:03d}.json")); m=J["meta"]
im=Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
x0=int(m["col1_x"]+((f0-1)*14)*m["pitch"]-m["pitch"]/2); x1=int(m["col1_x"]+(f1*14)*m["pitch"]+m["pitch"]/2)
rows=[]
for i in range(a,a+n):
    L=J["lines"][i-1]; c=im.crop((x0,L["y0"]-4,x1,L["y1"]+4)).convert("RGB")
    r=Image.new("RGB",(c.width+50,c.height),"white"); ImageDraw.Draw(r).text((3,8),str(i),fill=(0,0,0)); r.paste(c,(50,0)); rows.append(r)
W=max(r.width for r in rows); H=sum(r.height for r in rows); s=Image.new("RGB",(W,H),"white"); y=0
for r in rows: s.paste(r,(0,y)); y+=r.height
s.save(out)
