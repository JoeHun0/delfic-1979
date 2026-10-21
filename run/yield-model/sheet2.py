import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from model import build
from graph import info
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2]); wd=Path(sys.argv[3]); out=sys.argv[4]
EL={30:"Zn",31:"Ga",32:"Ge",33:"As",34:"Se",35:"Br",36:"Kr",37:"Rb",38:"Sr",39:"Y",40:"Zr",41:"Nb",42:"Mo",43:"Tc",44:"Ru",45:"Rh",46:"Pd",47:"Ag",48:"Cd",49:"In",50:"Sn",51:"Sb",52:"Te",53:"I",54:"Xe",55:"Cs",56:"Ba",57:"La",58:"Ce",59:"Pr",60:"Nd",61:"Pm",62:"Sm"}
nm=lambda k: f"{EL.get(info(N[k])['Z'])}-{info(N[k])['A']}{'m' if info(N[k])['M'] else ''}"
def loc(k):
    card=k//5+1; f=k%5+1
    if card<=39: return 205,card+22,f
    if card<=99: return 206,card-38,f
    return 207,card-98,f
items=json.load(open("irreg.json"))
items=[i for i in items if i[0]!="weak"]
items+= [["digits",126,"plain cell with 4 significant digits (deck's plain cells use 3); fits the rule; check the last digits"],
         ["digits",143,"plain cell with 5 significant digits (deck's plain cells use 3); fits the rule; check the last digits"]]
cards=[(205,61,"A=97 chain (Y-97 ... Mo-97): lowest reader confidence of all accepted cards"),(205,56,"A=94 chain (Kr-94 ... Zr-94): second-lowest reader confidence")]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",24)
small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",19)
cache={}
def page(pg):
    if pg not in cache:
        cache[pg]=(json.load(open(wd/"lines"/f"p{pg:03d}.json")), Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L"))
    return cache[pg]
strips=[]
hdr=Image.new("RGB",(1950,40),"white"); ImageDraw.Draw(hdr).text((10,8),"Irregular-looking yield cells, second pass (blue = our reading). Tell me the cell number and what your copy shows.",font=small,fill=(0,0,0)); strips.append(hdr)
order={"split":0,"rule":1,"digits":2}
for kind,k,why in sorted(items,key=lambda i:(order[i[0]],i[1])):
    pg,ln,f=loc(k); J,im=page(pg); m=J["meta"]; L=J["lines"][ln-1]
    x0=int(m["col1_x"]+((f-1)*14)*m["pitch"]-m["pitch"]/2); x1=int(m["col1_x"]+(f*14)*m["pitch"]+m["pitch"]/2)
    c=im.crop((x0,L["y0"]-6,x1,L["y1"]+6)).convert("RGB"); c=c.resize((int(c.width*1.3),int(c.height*1.3)))
    row=Image.new("RGB",(1950,max(c.height,62)+12),"white"); d=ImageDraw.Draw(row)
    d.text((10,4),f"#{k+1} {nm(k)}",font=font,fill=(0,0,0)); d.text((10,34),f"p{pg} L{ln} f{f}  [{kind}]",font=small,fill=(90,90,90))
    row.paste(c,(260,4)); d.text((270+c.width,8),raw[k],font=font,fill=(0,0,160)); d.text((270+c.width,38),why,font=small,fill=(120,0,0))
    strips.append(row)
for pg,ln,why in cards:
    J,im=page(pg); m=J["meta"]; L=J["lines"][ln-1]
    x0=int(m["col1_x"]-m["pitch"]/2); x1=int(m["col1_x"]+73.5*m["pitch"])
    c=im.crop((x0,L["y0"]-6,x1,L["y1"]+6)).convert("RGB"); c=c.resize((int(c.width*0.95),int(c.height*0.95)))
    card=" ".join(raw[(ln-22-1)*5+i] if pg==205 else "" for i in range(5))
    row=Image.new("RGB",(1950,c.height+80),"white"); d=ImageDraw.Draw(row)
    d.text((10,4),f"whole card p{pg} L{ln}  [weak reading]  {why}",font=small,fill=(120,0,0))
    row.paste(c,(10,30)); d.text((10,34+c.height),"ours: "+card,font=font,fill=(0,0,160))
    strips.append(row)
W=max(s.width for s in strips); H=sum(s.height for s in strips)
sheet=Image.new("RGB",(W,H),"white"); y=0
for s in strips: sheet.paste(s,(0,y)); y+=s.height
sheet.save(out); print(out, sheet.size)
