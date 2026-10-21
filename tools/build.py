"""Build icrm.f from the transcription: final cards + inserts + literal card fixes + safe normalisations,
then compile and map gfortran's errors back to page/line.

usage: python3 -I build.py <workdir> [--deck icrm|dtm]
  icrm (default): Vol. II pp. 55-107 up to *DECK,ADVEC -> src/icrm.f
  dtm:            from *DECK,ADVEC (p. 107) to p. 194 (DTM and OPM) -> src/dtm.f; on the PAMI table pages
                  (174-182) the data cards come from tables/p<page>.tsv (values read by tables.py)

cardfix.tsv: page<TAB>line<TAB>exact card text (columns as typed; '|' may mark column 7 start: the text
after '|' goes to column 7, text before it to columns 1-6).
Normalisations (logged in src/normalize.log): label field letters -> digits (C,O,D,U,Q->0 L,I->1 Z->2
S->5 B->8 G->6), statement '00 <digit>' -> 'DO <digit>', ' GC TO '/'GO 10 ' -> ' GO TO ', '.EC.'->'.EQ.',
'.CR.'->'.OR.', '.LT,' etc. Everything else is left for the error list.
"""
import re
import subprocess
import sys
from pathlib import Path

LAB = str.maketrans({"C": "0", "O": "0", "D": "0", "U": "0", "Q": "0", "L": "0", "I": "1", "Z": "2",
                     "S": "5", "B": "8", "G": "6", "J": "0", "T": "7", "E": "6", "(": "0"})
SUBS = [(r"^(\s*)00(\s+\d)", r"\1DO\2"), (r"^(\s*)(CO|OO|0O|O0|D0|DC|NO|CU)(\s+\d+\s*[A-Z][A-Z0-9]*\s*=)", r"\1DO\3"), (r"\bGC\s+TO\b", "GO TO"), (r"\bGO\s+10\s+(\d)", r"GO TO \1"),
        (r"\bG0\s+TO\b", "GO TO"), (r"\.EC\.", ".EQ."), (r"\.CR\.", ".OR."), (r"\.LT,", ".LT."),
        (r"\.GT,", ".GT."), (r"\.LE,", ".LE."), (r"\.GE,", ".GE."), (r"\.NE,", ".NE."), (r"\.EG\.", ".EQ."),
        (r"^(\s*)(ENO|EN0|FNO|FND|ENC|EHD|ENG|EN3)\s*$", r"\1END"), (r"^(\s*)(RETURK|PETURN|RETURM|RETUFN)\s*$", r"\1RETURN"),
        (r"\bG[O0]\s+T[CU0]\b", "GO TO"), (r"\bGO\s*T0\b", "GO TO"),
        (r"^(\s*)(FORHAT|F0RMAT|FCRMAT|FORMAI|FORNAT)\s*\(", r"\1FORMAT("),
        (r"^(\s*DO\s*\d+\s*[A-Z][A-Z0-9]*\s*=\s*[A-Z0-9]+)\.(\s*[A-Z0-9(][^,]*)$", r"\1,\2")]
ZEROS = str.maketrans({"C": "0", "J": "0", "O": "0", "U": "0", "Q": "0"})
REL = {"EQ": "EQ", "EC": "EQ", "NE": "NE", "LT": "LT", "LE": "LE", "GT": "GT", "QT": "GT", "GE": "GE",
       "AND": "AND", "ANC": "AND", "OR": "OR", "CR": "OR", "NOT": "NOT"}


def numfix_text(t, fmt=False):
    """broken zeros inside numeric constants (1C0 -> 100, J. -> 0., F1C.C -> F10.0) and relational operators
    written with a comma (,GE. -> .GE.). A digit-led token followed by a letter or '(' is a misread
    identifier (2CH(K) = ZCH(K)) and is left alone, except a Hollerith count (1CH...) in FORMAT/DATA."""
    def tok(m):
        nxt = t[m.end():m.end() + 1]
        if nxt and (nxt.isalpha() or nxt == "(") and not fmt:
            return m.group(1)
        return m.group(1).translate(ZEROS)
    t = re.sub(r"(?<![A-Z0-9])(\d[\dCJOUQ]*)", tok, t)
    t = re.sub(r"(?<=[A-Z(])(\d[\dCJOUQ]*)\.([\dCJOUQ]+)", lambda m: m.group(1).translate(ZEROS) + "." + m.group(2).translate(ZEROS), t)
    t = re.sub(r"(?<=[=(,*/+-])(\s*)[JCOUQ]\.(?=\s*([,)*/+\-]|$|[\dJCOUQ]))", r"\g<1>0.", t)
    t = re.sub(r"(\.(?:EQ|NE|LT|LE|GT|GE)\.\s*)[JCOUQ]\.([\dJCOUQ]+)", lambda m: m.group(1) + "0." + m.group(2).translate(ZEROS), t)
    t = re.sub(r"(?<=\d\.)([JCOUQ]+)(?=\s*([,)*/+\-]|$|E|\d))", lambda m: m.group(1).translate(ZEROS), t)
    t = re.sub(r"(?<=[A-Z0-9)])\s*'\s*(?=[A-Z0-9(])", "*", t)          # '*' read as an apostrophe
    t = re.sub(r"([.,])\s*(EQ|EC|NE|LT|LE|GT|QT|GE|AND|ANC|OR|CR|NOT)\s*([.,])",
               lambda m: m.group(0) if m.group(1) == "," and m.group(3) == "," else "." + REL[m.group(2)] + ".", t)
    return t


def numfix(cs, log):
    out = []; fmt = False
    for pg, ln, c in cs:
        if not c.strip() or c[:1] in "C*+-" or re.match(r"\s*[*+-]\s*[DO]ECK", c):
            out.append((pg, ln, c)); continue
        c72 = c.ljust(72); body = c72[6:]; res = []; i = 0
        if c72[5] in " 0":
            fmt = bool(re.match(r"\s*(FORMAT|DATA)\b", body))
        while i < len(body):
            m = re.match(r"(\d+)H", body[i:]) if (i == 0 or not (body[i - 1].isalnum() or body[i - 1] == ".")) else None
            if m:
                n = int(m.group(1)); seg = body[i:i + len(m.group(0)) + n]; res.append(seg); i += len(seg); continue
            j = i
            while j < len(body):
                m2 = re.match(r"(\d+)H", body[j:]) if (j == 0 or not (body[j - 1].isalnum() or body[j - 1] == ".")) else None
                if m2:
                    break
                j += 1
            res.append(numfix_text(body[i:j], fmt)); i = j
        nb = "".join(res)
        if nb != body:
            log.append(f"p{pg:03d}:{ln} numfix {body.strip()!r} -> {nb.strip()!r}")
        out.append((pg, ln, (c72[:6] + nb).rstrip()))
    return out


FULLWIDTH = {0xFF08: "(", 0xFF09: ")", 0xFF0C: ",", 0x3001: ",", 0xFF1D: "=", 0xFF0B: "+", 0xFF0D: "-", 0x3002: ".",
             0xFF0A: "*", 0xFF0F: "/", 0xFF1A: ":"}


def table_cards(wd):
    """(page, line) -> rendered data card from tables/; cards tablefix.tsv marks as not data are dropped."""
    out = {}
    for pg in range(174, 183):
        f = wd / "tables" / f"p{pg:03d}.tsv"
        for r in f.read_text().splitlines():
            x = r.split("\t")
            out[(pg, int(x[0]))] = x[4]
    f = wd / "tablefix.tsv"
    for r in f.read_text().splitlines():
        x = r.split("\t")
        if len(x) >= 4 and x[0].startswith("p") and x[2] == "-":
            out[(int(x[0][1:]), int(x[1]))] = None
    return out


def cards(wd, deck="icrm"):
    inserts, fixes = {}, {}
    for r in (wd / "inserts.tsv").read_text().splitlines():
        if r.strip() and not r.startswith("#"):
            pg, ln, card, note = r.split("\t")
            inserts.setdefault((int(pg.lstrip("p")), int(ln)), []).append(card)
    f = wd / "cardfix.tsv"
    if f.exists():
        for r in f.read_text().splitlines():
            if r.strip() and not r.startswith("#"):
                pg, ln, card = r.split("\t", 2)
                if "|" in card and not card.startswith("s|"):
                    a, b = card.split("|", 1); card = a.ljust(6)[:6] + b
                fixes[(int(pg.lstrip("p")), int(ln))] = card
    out = []
    tabs = table_cards(wd) if deck == "dtm" else {}
    started = deck == "icrm"
    for pg in (range(55, 108) if deck == "icrm" else range(107, 195)):
        for r in (wd / "final" / f"p{pg:03d}.tsv").read_text().splitlines():
            row = r.split("\t"); ln = int(row[0]); card = row[4]
            if re.match(r"\s*\*\s*DECK\s*,?\s*ADVEC", card):
                if deck == "icrm":
                    return out
                started = True
            if not started:
                continue
            if (pg, ln) in tabs:
                if tabs[(pg, ln)] is not None:
                    out.append((pg, ln, tabs[(pg, ln)].rstrip()))
                continue
            if row[3] in ("NOISE", "SEQONLY"):
                continue
            if (pg, ln) in fixes and not (deck != "icrm" and fixes[(pg, ln)].startswith("s|")):
                fx = fixes[(pg, ln)]
                if fx.startswith("s|"):          # s|old|new| [s|old|new| ...] substitutions in the card
                    parts = fx.split("|")
                    for k in range(1, len(parts) - 1, 3):
                        if parts[k] not in card:
                            print(f"SUBST NOT FOUND p{pg:03d}:{ln} {parts[k]!r}")
                        card = card.replace(parts[k], parts[k + 1], 1)
                else:
                    card = fx
            card = card.translate(FULLWIDTH)
            out.append((pg, ln, card.rstrip()))
            for e in inserts.get((pg, ln), []):
                out.append((pg, ln, e.rstrip()))
    return out


def normalize(card, log, where):
    if not card.strip():
        return card
    if card[0] in "C*c+" or re.match(r"\s*[*+-]\s*[DO]ECK", card):
        return "C" + card[1:] if card[0] != "C" else card
    lab, cont, body = card[:5], card[5:6], card[6:]
    nl = lab.translate(LAB) if lab.strip() else lab
    if nl != lab:
        log.append(f"{where} label {lab!r} -> {nl!r}")
    nb = body
    for a, b in SUBS:
        nb = re.sub(a, b, nb)
    if nb != body:
        log.append(f"{where} body {body.strip()!r} -> {nb.strip()!r}")
    return (nl + cont + nb)[:72]


def vote_commons(cs, log):
    """COMMON blocks (with their continuation cards) recur unchanged in many routines: vote column by
    column across all occurrences of the same block and give every occurrence the majority text."""
    from collections import Counter, defaultdict
    groups = defaultdict(list)          # name -> list of (start index, [card indices])
    i = 0
    while i < len(cs):
        c = cs[i][2]
        m = re.match(r"\s{6}\s*C\s*O\s*[MN]\s*[MN]\s*O\s*N\s*/\s*([A-Z0-9]+)\s*/", c.ljust(72))
        if m and c[:1] not in "C*":
            idx = [i]; j = i + 1
            while j < len(cs) and len(cs[j][2]) > 5 and cs[j][2][5] not in " 0" and cs[j][2][:1] not in "C*":
                idx.append(j); j += 1
            groups[m.group(1)].append(idx); i = j
        else:
            i += 1
    for name, occ in groups.items():
        if len(occ) < 3:
            continue
        n = Counter(len(o) for o in occ).most_common(1)[0][0]
        same = [o for o in occ if len(o) == n]
        for k in range(n):
            texts = [cs[o[k]][2].ljust(72)[6:72] for o in same]
            best = "".join(Counter(col).most_common(1)[0][0] for col in zip(*texts))
            for o in same:
                pg, ln, c = cs[o[k]]
                new = c.ljust(72)[:6] + best
                if new.rstrip() != c.rstrip():
                    log.append(f"p{pg:03d}:{ln} COMMON /{name}/ voted")
                    cs[o[k]] = (pg, ln, new.rstrip())
    return cs


def vote_commons2(cs, log):
    """DTM/OPM: COMMON blocks may legitimately name their members differently in different routines
    (/OUTPUT/ ...ITAB...PSIZE... or ...NDSTR...PS...), so occurrences are first clustered by similarity of
    their blank-free text and voted only within a cluster of at least 3: the per-character majority of the
    strings with the modal length, re-laid out on the occurrence's own cards (blanks are not significant)."""
    from collections import Counter, defaultdict
    from difflib import SequenceMatcher
    occ = defaultdict(list)
    i = 0
    while i < len(cs):
        c = cs[i][2]
        m = re.match(r"\s{6}\s*COMMON\s*/\s*([A-Z0-9][A-Z0-9 ]*?)\s*/", c.ljust(72))
        if m and c[:1] not in "C*":
            idx = [i]; j = i + 1
            while j < len(cs) and len(cs[j][2]) > 5 and cs[j][2][5] not in " 0" and cs[j][2][:1] not in "C*":
                idx.append(j); j += 1
            text = "".join(cs[k][2].ljust(72)[6:72] for k in idx).replace(" ", "")
            occ[m.group(1).replace(" ", "")].append((idx, text)); i = j
        else:
            i += 1
    canon = {}
    cf = Path(sys.argv[1]) / "commons-dtm.tsv"
    if cf.exists():
        for r in cf.read_text().splitlines():
            if r.strip() and not r.startswith("#"):
                a, b = r.split("\t"); canon.setdefault(a, []).append(b)

    def toks(t):
        return re.sub(r"^COMMON/[A-Z0-9]+/", "", t).split(",")

    def score(t, v):
        a, b = toks(t), v.split(",")
        return sum(SequenceMatcher(None, x, y).ratio() for x, y in zip(a, b)) - abs(len(a) - len(b))
    for name, os_ in occ.items():
        if name in canon:                    # canonical variants: snap every occurrence to the closest one
            for idx, t in os_:
                v = max(canon[name], key=lambda v: score(t, v))
                best = f"COMMON/{name}/" + v
                if t != best:
                    os_cl = [(idx, t)]
                    relayout(cs, idx, best, log, name, t)
            continue
        clusters = []
        for o in os_:
            for cl in clusters:
                if SequenceMatcher(None, cl[0][1], o[1]).ratio() >= 0.85:
                    cl.append(o); break
            else:
                clusters.append([o])
        for cl in clusters:
            if len(cl) < 3:
                continue
            n = Counter(len(t) for _, t in cl).most_common(1)[0][0]
            same = [t for _, t in cl if len(t) == n]
            best = "".join(Counter(col).most_common(1)[0][0] for col in zip(*same))
            for idx, t in cl:
                if t != best:
                    relayout(cs, idx, best, log, name, t)
    return cs


def relayout(cs, idx, best, log, name, t):
    """lay a blank-free COMMON text out on the occurrence's own cards, breaking after commas, 66 columns
    each; spare cards become blank lines; continuation marks are kept (or set to 1, 2, ...)."""
    parts = re.split(r"(?<=,)", best); cards = [""]
    for prt in parts:
        if len(cards[-1]) + len(prt) > 66 and cards[-1]:
            cards.append("")
        cards[-1] += prt
    if len(cards) > len(idx):
        log.append(f"COMMON /{name}/ does not fit {len(idx)} cards, left as is: {t}"); return
    for k, card_i in enumerate(idx):
        pg, ln, c = cs[card_i]
        head = (c.ljust(72)[:5] + (c.ljust(72)[5] if c.ljust(72)[5] not in " 0" else str(k))) if k else "      "
        new = (head + cards[k]).rstrip() if k < len(cards) else ""
        cs[card_i] = (pg, ln, new)
    log.append(f"p{cs[idx[0]][0]:03d}:{cs[idx[0]][1]} COMMON /{name}/: {t} -> {best}")


def rename(cs, wd, log, deck="icrm"):
    """Whole-word identifier renames (rename.tsv for ICRM, rename-dtm.tsv for DTM/OPM) in code cards,
    skipping comments, FORMAT statements and Hollerith fields."""
    pairs = {}
    for r in (wd / ("rename.tsv" if deck == "icrm" else f"rename-{deck}.tsv")).read_text().splitlines():
        if r.strip() and not r.startswith("#"):
            a, b = r.split("\t")[:2]; pairs[a] = b
    if not pairs:
        return cs
    names = "|".join(sorted(map(re.escape, pairs), key=len, reverse=True))
    if deck == "icrm":
        pat = re.compile(r"(?<![A-Z0-9.])(" + names + r")(?![A-Z0-9])")
    else:                                    # a name may follow .EQ. etc.; only a '.' ending a number is excluded
        pat = re.compile(r"(?<![A-Z0-9])(?<![0-9]\.)(" + names + r")(?![A-Z0-9])")
    out = []
    infmt = False
    for pg, ln, c in cs:
        if not c.strip() or c[:1] in "C*":
            out.append((pg, ln, c)); continue
        c72 = c.ljust(72)
        if c72[5] in " 0":
            infmt = bool(re.match(r"\s*FORMAT\s*\(", c72[6:]))
        if infmt:
            out.append((pg, ln, c)); continue
        body = c72[6:]; res = []; i = 0
        while i < len(body):
            m = re.match(r"(\d+)H", body[i:]) if (i == 0 or not (body[i - 1].isalnum() or body[i - 1] == ".")) else None
            if m:
                n = int(m.group(1)); seg = body[i:i + len(m.group(0)) + n]; res.append(seg); i += len(seg); continue
            j = i
            while j < len(body):
                m2 = re.match(r"(\d+)H", body[j:]) if (j == 0 or not (body[j - 1].isalnum() or body[j - 1] == ".")) else None
                if m2:
                    break
                j += 1
            res.append(pat.sub(lambda mm: pairs[mm.group(1)], body[i:j])); i = j
        nb = "".join(res)
        if nb != body:
            log.append(f"p{pg:03d}:{ln} rename {body.strip()!r} -> {nb.strip()!r}")
        out.append((pg, ln, (c72[:6] + nb).rstrip()))
    return out


def main():
    wd = Path(sys.argv[1]); src = wd / "src"
    deck = sys.argv[sys.argv.index("--deck") + 1] if "--deck" in sys.argv else "icrm"
    cs = cards(wd, deck); log = []; lines = []; where = []
    if deck == "icrm":
        cs = vote_commons(cs, log)
        cs = rename(cs, wd, log)
    else:
        cs = rename(cs, wd, log, deck)
        cs = numfix(cs, log)
        cs = vote_commons2(cs, log)
        cs = rename(cs, wd, log, deck)
    late = {}
    if deck != "icrm":                       # DTM: s|old|new| fixes act on the normalised card (what fix.py shows)
        for r in (wd / "cardfix.tsv").read_text().splitlines():
            if r.strip() and not r.startswith("#"):
                pg, ln, card = r.split("\t", 2)
                if card.startswith("s|"):
                    late.setdefault((int(pg.lstrip("p")), int(ln)), []).append(card)
    for pg, ln, c in cs:
        c = normalize(c, log, f"p{pg:03d}:{ln}")
        for fx in late.get((pg, ln), []):
            parts = fx.split("|")
            for k in range(1, len(parts) - 1, 3):
                if parts[k] not in c:
                    print(f"SUBST NOT FOUND p{pg:03d}:{ln} {parts[k]!r}")
                c = c.replace(parts[k], parts[k + 1], 1)
        lines.append(c); where.append((pg, ln))
    sfx = "" if deck == "icrm" else "-" + deck
    (src / f"{deck}.f").write_text("\n".join(lines) + "\n")
    (src / f"normalize{sfx}.log").write_text("\n".join(log) + "\n")
    (src / f"{deck}.map").write_text("".join(f"{i+1}\tp{w[0]:03d}\t{w[1]}\n" for i, w in enumerate(where)))
    r = subprocess.run(["gfortran", "-std=legacy", "-ffixed-form", "-fdefault-real-8", "-fno-automatic"] + (["-fdefault-integer-8"] if deck != "icrm" else []) + [
                        "-fsyntax-only", f"{deck}.f"], cwd=src, capture_output=True, text=True)
    errs = []
    for m in re.finditer(rf"^{deck}\.f:(\d+):(\d+):\n\n(.*?)\n.*?\n(Error|Warning): (.*?)$", r.stderr, re.M | re.S):
        n = int(m.group(1)); errs.append((n, m.group(4), m.group(5), where[n - 1], lines[n - 1]))
    seen = set(); E = 0
    with open(src / f"errors{sfx}.txt", "w") as f:
        for n, kind, msg, w, txt in errs:
            if (n, kind) in seen or kind != "Error":
                continue
            seen.add((n, kind)); E += 1
            f.write(f"{n}\tp{w[0]:03d}\t{w[1]}\t{msg}\t{txt}\n")
    print(f"{len(lines)} cards, {len(log)} normalisations, {E} error lines")


if __name__ == "__main__":
    main()
