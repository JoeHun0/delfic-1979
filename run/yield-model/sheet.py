import sys, os, json, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from collections import defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from model import build, fit_chain, L2
from graph import info
wd=Path(sys.argv[3]); out=sys.argv[4]
N,Y0,P,div,raw,chains=build(sys.argv[1],sys.argv[2])
fits={}; pts=[]
for A in sorted(chains):
    yz={Z:sum(Y0[k]*div[k] for k in ks) for Z,ks in chains[A].items()}
    f=fit_chain(yz)
    if not f: continue
    fits[A]=(f,yz)
    Zp,amp=f
    for Z,y in yz.items():
        g=amp*np.exp(-L2*(Z-Zp)**2); pts.append((abs(Z-Zp),y/g))
bins=defaultdict(list)
for d,r in pts: bins[round(d/0.05)*0.05].append(r)
curve={b:statistics.median(v) for b,v in bins.items()}
def rule(A,Z):
    (Zp,amp),yz=fits[A]; d=abs(Z-Zp); return amp*np.exp(-L2*(Z-Zp)**2)*curve.get(round(d/0.05)*0.05,0.0), d
name=lambda k: f"{info(N[k])['A']}-{info(N[k])['Z']}{'m' if info(N[k])['M'] else ''}"
EL={30:"Zn",31:"Ga",32:"Ge",33:"As",34:"Se",35:"Br",36:"Kr",37:"Rb",38:"Sr",39:"Y",40:"Zr",41:"Nb",42:"Mo",43:"Tc",44:"Ru",45:"Rh",46:"Pd",47:"Ag",48:"Cd",49:"In",50:"Sn",51:"Sb",52:"Te",53:"I",54:"Xe",55:"Cs",56:"Ba",57:"La",58:"Ce",59:"Pr",60:"Nd",61:"Pm",62:"Sm"}
def nm(k):
    I=info(N[k]); return f"{EL.get(I['Z'],I['Z'])}-{I['A']}{'m' if I['M'] else ''}"
def deckfmt(v):
    if v<=0: return "0."
    e=int(np.floor(np.log10(v)))+1; m=v/10**e
    if m>=0.9995: m/=10; e+=1
    return f".{round(m*1000):03d}000E{'+' if e>=0 else '-'}{abs(e):02d}"
rows=[]
for A,((Zp,amp),yz) in fits.items():
    for Z,y in yz.items():
        e,d=rule(A,Z)
        rc=curve.get(round(d/0.05)*0.05,0.0)
        g=amp*np.exp(-L2*(Z-Zp)**2)
        r=y/g if g>0 else 0
        if (rc>0.05 and abs(r/rc-1)>0.06) or (rc<=0.05 and y>0.5) or (y==0 and e>0.3):
            ks=chains[A][Z]
            for k in ks:
                share=(Y0[k]*div[k]/y) if y>0 else 1/len(ks)
                pred=e*share/div[k]
                rows.append((A,Z,k,d,raw[k] or "0.",pred,div[k],y,e))
rows.sort(key=lambda r:r[2])
def loc(k):
    card=k//5+1; f=k%5+1
    if card<=39: return 205,card+22,f
    if card<=99: return 206,card-38,f
    return 207,card-98,f
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",26)
small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",20)
strips=[]; cache={}
hdr=Image.new("RGB",(1500,70),"white"); dh=ImageDraw.Draw(hdr)
dh.text((10,8),"cell / scan                          ours (as read)        1979 rule predicts",font=small,fill=(0,0,0))
dh.text((10,36),"rule = Gaussian charge dispersion fitted to the rest of the chain; value shown as printed (divided by path count)",font=small,fill=(90,90,90))
strips.append(hdr)
for A,Z,k,d,ours,pred,dv,y,e in rows:
    pg,ln,f=loc(k)
    if pg not in cache:
        cache[pg]=(json.load(open(wd/"lines"/f"p{pg:03d}.json")), Image.open(sorted((wd/"native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L"))
    J,im=cache[pg]; m=J["meta"]; L=J["lines"][ln-1]
    x0=int(m["col1_x"]+((f-1)*14)*m["pitch"]-m["pitch"]/2); x1=int(m["col1_x"]+(f*14)*m["pitch"]+m["pitch"]/2)
    c=im.crop((x0,L["y0"]-6,x1,L["y1"]+6)).convert("RGB"); c=c.resize((int(c.width*1.3),int(c.height*1.3)))
    row=Image.new("RGB",(1500,max(c.height,64)+14),"white"); d_=ImageDraw.Draw(row)
    d_.text((10,4),f"#{k+1} {nm(k)}",font=font,fill=(0,0,0))
    d_.text((10,36),f"p{pg} L{ln} f{f}  /{dv} path{'s' if dv>1 else ''}",font=small,fill=(90,90,90))
    row.paste(c,(250,4))
    d_.text((260+c.width,14),ours,font=font,fill=(0,0,160))
    d_.text((260+c.width+300,14),deckfmt(pred),font=font,fill=(170,0,0))
    ratio=(float(ours)/pred) if pred>0 and float(ours)>0 else None
    d_.text((260+c.width+300,44),f"(x{ratio:.2f} off)" if ratio else ("(rule ~0)" if pred<=0 else "(printed 0)"),font=small,fill=(120,120,120))
    strips.append(row)
W=max(s.width for s in strips); H=sum(s.height for s in strips)
sheet=Image.new("RGB",(W,H),"white"); y0=0
for s in strips: sheet.paste(s,(0,y0)); y0+=s.height
for i in range(1,len(strips)):
    pass
sheet.save(out); print(out, sheet.size, len(rows),"cells")
for A,Z,k,d,ours,pred,dv,y,e in rows: print(f"#{k+1:3d} {nm(k):8s} p{loc(k)[0]} L{loc(k)[1]} f{loc(k)[2]}  ours {ours:>13s}  rule {deckfmt(pred):>13s}  |dZ|={d:.2f}")
