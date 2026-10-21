"""Print DELFIC's decay data per mass chain in Crocker-1967 style: half-life with unit, branch fractions, daughters."""
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graph import load, info, daughters
EL={27:"Co",28:"Ni",29:"Cu",30:"Zn",31:"Ga",32:"Ge",33:"As",34:"Se",35:"Br",36:"Kr",37:"Rb",38:"Sr",39:"Y",40:"Zr",41:"Nb",42:"Mo",43:"Tc",44:"Ru",45:"Rh",46:"Pd",47:"Ag",48:"Cd",49:"In",50:"Sn",51:"Sb",52:"Te",53:"I",54:"Xe",55:"Cs",56:"Ba",57:"La",58:"Ce",59:"Pr",60:"Nd",61:"Pm",62:"Sm",63:"Eu",64:"Gd",65:"Tb",66:"Dy"}
N,_=load(sys.argv[1])
dcon=[float(l.split()[4]) for l in open(sys.argv[1])]
# branch table: BATMAN consumes 4-low pairs in NUCLID order
br=[float(x) for x in open(sys.argv[2]).read().split()] if len(sys.argv)>2 else None
def fmt(lam):
    if lam<=0: return "Stable"
    t=math.log(2)/lam
    for u,s in (("Y",3.15576e7),("D",86400),("H",3600),("M",60)):
        if t>=s*0.999 and not (u=="Y" and t<3.15576e7*1.5): return f"{t/s:.4g} {u}"
    return f"{t:.4g} S"
name=lambda k: f"{info(N[k])['A']}{'m' if info(N[k])['M'] else ''}{EL.get(info(N[k])['Z'],info(N[k])['Z'])}"
A0,A1=int(sys.argv[3]),int(sys.argv[4])
ibr=0; out=[]
for k,v in enumerate(N):
    if v==0: continue
    I=info(v); low=I["low"]; nb=4-(low%8) if low not in (0,4) and low%8<4 else 0
    fr=br[ibr:ibr+nb] if br else []; ibr+=nb
    if A0<=I["A"]<=A1:
        ds=daughters(N,k)
        tgt=", ".join(f"{name(j)}" + (f" ({fr[n]:g})" if fr else "") for n,j in enumerate(ds))
        out.append(f"{'HEAD ' if I['head'] else '     '}{name(k):8s} {fmt(dcon[k]):>12s}  -> {tgt}")
print("\n".join(out))
