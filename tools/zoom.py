"""Crop one listing line (columns 1-72) at native resolution, optionally zoomed on a column range.
usage: python3 -I zoom.py <workdir> <page> <line> <out.png> [col_from col_to] [scale]"""
import json, sys
from pathlib import Path
from PIL import Image
wd=Path(sys.argv[1]); pg=int(sys.argv[2]); ln=int(sys.argv[3]); out=sys.argv[4]
J=json.load(open(wd/"lines"/f"p{pg:03d}.json")); m=J["meta"]; L=J["lines"][ln-1]
c0=int(sys.argv[5]) if len(sys.argv)>5 else 1; c1=int(sys.argv[6]) if len(sys.argv)>6 else 72; sc=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
im=Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
x0=int(m["col1_x"]+(c0-1)*m["pitch"]-m["pitch"]/2); x1=int(m["col1_x"]+(c1-1)*m["pitch"]+m["pitch"]/2)
c=im.crop((x0,L["y0"]-6,x1,L["y1"]+6)); c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS); c.save(out)
