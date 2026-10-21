import sys, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
wd=Path(sys.argv[1]); out=sys.argv[2]
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",24)
small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",20)
cache={}
def page(pg):
    if pg not in cache: cache[pg]=(json.load(open(wd/"lines"/f"p{pg:03d}.json")), Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L"))
    return cache[pg]
def crop(pg,ln,c0,c1,sc):
    J,im=page(pg); m=J["meta"]; L=J["lines"][ln-1]
    x0=int(m["col1_x"]+(c0-1)*m["pitch"]-m["pitch"]/2); x1=int(m["col1_x"]+(c1-1)*m["pitch"]+m["pitch"]/2)
    c=im.crop((x0,L["y0"]-6,x1,L["y1"]+6)); return c.resize((int(c.width*sc),int(c.height*sc))).convert("RGB")
DECK=[l for l in (wd/"run"/"pam-p239he.txt").read_text().split("\n")[1:] if l.strip()]
def card_text(pg,ln):
    card={205:ln-22,206:ln+38,207:ln+98}[pg]
    return DECK[card-1] if 1<=card<=len(DECK) else ""
blocks=[]
def block(title, notes, pg, ln, f, digit_pos_in_field, refs):
    hdr=Image.new("RGB",(1800,70),"white"); d=ImageDraw.Draw(hdr)
    d.text((10,6),title,font=font,fill=(0,0,0)); d.text((10,40),notes,font=small,fill=(120,0,0)); blocks.append(hdr)
    c0=(f-1)*14+1; whole=crop(pg,ln,c0,c0+13,4.0)
    row=Image.new("RGB",(1800,whole.height+40),"white"); row.paste(whole,(10,4)); d=ImageDraw.Draw(row)
    d.text((10,whole.height+8),f"the whole field, 4x  (p{pg} L{ln} f{f}); questioned digit = position {digit_pos_in_field} of the field",font=small,fill=(90,90,90)); blocks.append(row)
    x=10; refrow=Image.new("RGB",(1800,210),"white"); d=ImageDraw.Draw(refrow)
    for lab,(rpg,rln,col) in refs:
        cc=crop(rpg,rln,col,col,5.0); refrow.paste(cc,(x,30)); d.text((x,2),lab,font=small,fill=(0,0,160)); x+=cc.width+30
    blocks.append(refrow)
    sp=Image.new("RGB",(1800,24),"white"); blocks.append(sp)
def find(pg,ln,ch,skip_cols=()):
    t=card_text(pg,ln).ljust(70); J,im=page(pg); L=J["lines"][ln-1]
    return [i+1 for i,c in enumerate(t[:70]) if c==ch and (i+1) in L["cols"] and (i+1) not in skip_cols]
def refs_for(pg,ln,q,chars):
    out=[("questioned",(pg,ln,q))]
    for ch in chars:
        n=0
        for l2 in (ln,ln+1,ln-1,ln+2,ln-2):
            for c in find(pg,l2,ch,{q} if l2==ln else ()):
                out.append((f"a '{ch}' (L{l2})",(pg,l2,c))); n+=1
                if n>=2: break
            if n>=2: break
    return out
block("#464 Sn-130: we read .609000E+02 - is the first digit 6 or 8?",
      "If 8 (80.9): all five A=130 cells fit the 1979 formula, and the block total matches ORNL's file (18793.05 vs 18793.03).",206,55,4,5,refs_for(206,55,47,"68"))
block("#157 Br-93: we read .565000E+00 - is the second digit 6 or 4?",
      "LightOn reads .545; the formula slightly prefers .545 (tail cell, weak evidence). No effect on the results either way.",205,54,2,6,refs_for(205,54,20,"64"))
W=max(b.width for b in blocks); H=sum(b.height for b in blocks)
sheet=Image.new("RGB",(W,H),"white"); y=0
for b in blocks: sheet.paste(b,(0,y)); y+=b.height
sheet.save(out); print(out, sheet.size)
