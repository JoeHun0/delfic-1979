"""Apply hand readings (corrections.tsv: page<TAB>line<TAB>text or NOISE) to the merged cards.

usage: python3 -I applyfix.py <workdir> [--check-only]
Each text is placed into the line's inked columns 1-72 (non-blank count must equal the inked cells);
mismatches are reported and not applied. Writes <workdir>/final/p<page>.tsv.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from merge import place

def expand(txt, cols):
    """{*} = as many stars as needed to fill the inked cells."""
    if "{*}" in txt:
        rest = len([c for c in txt.replace("{*}", "") if not c.isspace()])
        txt = txt.replace("{*}", "*" * max(len(cols) - rest, 0))
    return txt


def free(txt, cols):
    """Fallback layout when a reading cannot be matched to the inked cells (touching or faded glyphs):
    a leading number is a label (cols 1-5); a reading whose first inked cell is column 6 is a
    continuation (its first character goes to column 6); the statement starts in column 7 with the
    internal spacing as typed (blanks are not significant in Fortran outside Hollerith fields).
    A leading '&' forces the next character into column 6 (a faded continuation mark)."""
    card = [" "] * 72
    s = txt.strip()
    tok = s.split()[0]
    if s.startswith("&"):                  # continuation mark faded on the scan: forced into column 6
        card[5] = s[1]; body = s[2:].lstrip()
    elif cols and cols[0] == 6:
        card[5] = s[0]; body = s[1:].lstrip()
    elif tok.isdigit() and len(tok) <= 5 and len(s.split()) > 1:
        for k, ch in enumerate(tok.rjust(5)[-5:]):
            card[k] = ch
        body = s[len(tok):].lstrip()
    else:
        body = s
    for k, ch in enumerate(body[:66]):
        card[6 + k] = ch
    return "".join(card)

wd = Path(sys.argv[1]); fixes = {}; bad = 0
for r in (wd / "corrections.tsv").read_text().splitlines():
    if not r.strip() or r.startswith("#"): continue
    pg, ln, txt = r.split("\t", 2)
    fixes[(int(pg.lstrip("p")), int(ln))] = txt
for (pg, ln), txt in sorted(fixes.items()):
    if txt == "NOISE" or txt.startswith("C "): continue
    L = json.load(open(wd / "lines" / f"p{pg:03d}.json"))["lines"][ln - 1]
    cols = [c for c in L["cols"] if c <= 72]
    txt = expand(txt, cols); fixes[(pg, ln)] = txt
    if place(txt, cols, L.get('ink')) is None:
        if txt.startswith("!"):
            continue
        bad += 1
        print(f"MISMATCH p{pg:03d} L{ln}: {len(txt.replace(' ',''))} chars vs {len(cols)} cells  first col {cols[0]}: {txt}")
print(f"{len(fixes)} fixes, {bad} mismatches")
if "--check-only" not in sys.argv and not bad:
    (wd / "final").mkdir(exist_ok=True)
    for f in sorted((wd / "merged").glob("p*.tsv")):
        pg = int(f.stem[1:]); J = json.load(open(wd / "lines" / f"p{pg:03d}.json"))
        out = []
        for r in f.read_text().splitlines():
            row = r.split("\t"); i = int(row[0])
            if (pg, i) in fixes:
                t = fixes[(pg, i)]
                if t == "NOISE": row[3] = "NOISE"; row[4] = " " * 72
                elif t.startswith("C "): row[3] = "HAND"; row[4] = t[:72].ljust(72)
                elif t.startswith("!"):
                    row[3] = "HANDFREE"; row[4] = free(t[1:].replace("~", ""), [c for c in J["lines"][i - 1]["cols"] if c <= 72])
                else:
                    row[3] = "HAND"; row[4] = (place(t, [c for c in J["lines"][i - 1]["cols"] if c <= 72], J["lines"][i - 1].get("ink")) or "").replace("~", " ")
            out.append("\t".join(row))
        (wd / "final" / f.name).write_text("\n".join(out) + "\n")
