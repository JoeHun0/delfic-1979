"""Grammar-constrained reader for the PAMI DATA tables (Vol. II PDF pp. 174-182).

usage: python3 -I tables.py <workdir> read [pages...] [--tau 0.08]   -> tables/p<page>.tsv + tables/review.tsv
       python3 -I tables.py <workdir> proof <page> <line> <count> [out.png]

A data card is '$' in column 6 and then up to five values written one after another from column 7, each as a
sign column, the value and a comma (the last value of a DATA statement ends in '/'):
  E    s d.ddddddEsd ,       13 columns
  E2   s d.ddddddEsdd,       14 columns: a two-digit exponent pushes the rest of the card one column right
  E5   s d.dddddEsdd ,       13 columns (1.28333E-34)
  Z    s 0.000000    ,       13 columns
  I    s     ddddddd ,       13 columns, right-aligned integer
Inked cells are classified by their 3 nearest verified cells (normalised correlation) within the characters the
grammar allows at that position; the field type is the one whose layout fits the ink best. Training cells:
fields where at least two OCR reads agree (after mapping the broken-zero glyphs J D C U O ) to 0), verified
code cards from the DTM/OPM pages, and the hand-verified PAM cards (pp. 205-207).
A field is accepted when at least two OCR reads give the same value as the classifier, or one does and the
weakest classifier margin is >= tau; everything else goes to review. Hand readings: tablefix.tsv
(page<TAB>line<TAB>full card text from column 1).
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from glyphs import cell_img, load, verified_cards  # noqa: E402

CH = "0123456789.E+-,/"
DIG = "0123456789"
HEAD = re.compile(r"DATA\s*\(*\s*([A-Z0-9]+)")
NUM = re.compile(r"^-?(\d\.\d{6}E[+-]\d\d?|\d\.\d{5}E[+-]\d\d|0\.0{6}|\d+)$")
ZERO = str.maketrans({c: "0" for c in "JDCUOQou)(c"})

TYPES = {   # position (from the sign column) -> allowed characters; then the width including the comma
    "E": ({1: DIG, 2: ".", **{p: DIG for p in range(3, 9)}, 9: "E", 10: "+-", 11: DIG}, 13),
    "E2": ({1: DIG, 2: ".", **{p: DIG for p in range(3, 9)}, 9: "E", 10: "+-", 11: DIG, 12: DIG}, 14),
    "E5": ({1: DIG, 2: ".", **{p: DIG for p in range(3, 8)}, 8: "E", 9: "+-", 10: DIG, 11: DIG}, 13),
    "Z": ({1: "0", 2: ".", **{p: "0" for p in range(3, 9)}}, 13),
}


def norm(tok):
    """map broken-zero glyphs to 0 inside an otherwise numeric token; None if it still is not a number."""
    t = tok.replace(" ", "")
    if not t:
        return None
    s = t[0] + t[1:].translate(ZERO) if t[0] == "-" else t.translate(ZERO)
    s = s.replace("B", "8").replace("e", "E")
    return s if NUM.match(s) else None


def ocr_tokens(wd, pg):
    """line -> list of normalised token lists (one per OCR read), split from the raw text at , and /."""
    out = {}
    for d in ("ocr-lighton", "ocr-glm", "ocr-dots", "ocr2-lighton", "ocr2-glm", "ocr2-dots"):
        f = wd / d / f"p{pg:03d}.tsv"
        if not f.exists():
            continue
        for r in f.read_text().splitlines():
            x = r.split("\t")
            if len(x) < 5 or not x[0].isdigit():
                continue
            t = x[4].split(" || ")[0].strip()
            t = re.sub(r"^[$§S58]\s*(?=[-\d])", "", t)
            out.setdefault(int(x[0]), []).append([norm(a) for a in re.split(r"[,/]", t) if a.strip()])
    return out


def load_fixes(wd):
    """tablefix.tsv: page<TAB>line<TAB>field<TAB>value (field = 1..5), or page<TAB>line<TAB>*<TAB>v1 v2 ... [/]
    for a whole card (a trailing / closes the DATA statement), or page<TAB>line<TAB>-<TAB>why for a card that
    is not data."""
    f = wd / "tablefix.tsv"; out = {}
    if f.exists():
        for r in f.read_text().splitlines():
            x = r.split("\t")
            if len(x) >= 4 and x[0].startswith("p"):
                out.setdefault((int(x[0][1:]), int(x[1])), {})[x[2]] = x[3].strip()
    return out


def render(toks, term):
    """card text from the values, laid out as the listing prints them."""
    card = "     $"
    for n, t in enumerate(toks):
        neg = t.startswith("-"); b = t.lstrip("-")
        f = ("-" if neg else " ") + b.ljust(11) if "." in b else (("-" if neg else "") + b).rjust(12)
        card += f + ("/" if term and n == len(toks) - 1 else ",")
    return card


_LINES = {}


def data_lines(wd, pages):
    """{page: [(line, array, last)]} for the data cards: '$' in column 6, values from column 7. The array
    name is carried across pages (a DATA statement may continue on the next page); last marks the card that
    closes its DATA statement (followed by the next DATA header or FORMAT)."""
    if tuple(pages) in _LINES:
        return _LINES[tuple(pages)]
    fixes = load_fixes(wd); arr = None; seq = []
    for pg in range(174, 183):
        J, _ = load(wd, pg)
        merged = {int(r.split("\t")[0]): r.split("\t")[4] for r in (wd / "merged" / f"p{pg:03d}.tsv").read_text().splitlines()}
        for i, L in enumerate(J["lines"], 1):
            t = merged.get(i, "")
            if "-" in fixes.get((pg, i), {}):
                continue
            if "H" in fixes.get((pg, i), {}):                 # a DATA header the OCR lost
                arr = fixes[(pg, i)]["H"]; seq.append(None); continue
            if "DATA" in t[:15]:
                m = HEAD.search(t); arr = m.group(1) if m else "?"
                seq.append(None); continue
            if t.startswith("C") or "FORMAT" in t:
                if "FORMAT" in t:
                    arr = None; seq.append(None)
                continue
            cols = [c for c in L["cols"] if c <= 72]
            if arr and arr != "TYPE" and [c for c in cols if c >= 8] and min(cols) >= 6 and min(c for c in cols if c != 6) >= 7:
                seq.append((pg, i, arr))
    out = {p: [] for p in range(174, 183)}
    for n, x in enumerate(seq):
        if x:
            out[x[0]].append((x[1], x[2], n + 1 < len(seq) and seq[n + 1] is None))
    _LINES[tuple(pages)] = {p: out[p] for p in pages}
    return _LINES[tuple(pages)]


def tok_layout(tok, pos):
    """normalised token at sign column pos -> ({col: char}, width)."""
    neg = tok.startswith("-"); b = tok.lstrip("-")
    if "." in b:
        lay = {pos + 1 + j: ch for j, ch in enumerate(b)}; w = 14 if len(b) == 12 else 13
        if neg:
            lay[pos] = "-"
    else:
        lay = {pos + 12 - len(b) + j: ch for j, ch in enumerate(b)}; w = 13
        if neg:
            lay[pos + 11 - len(b)] = "-"
    return lay, w


def training(wd, pages):
    X = []; Y = []; S = []

    def add(a, L, meta, col, ch, key):
        v, _ = cell_img(a, L, meta, col)
        if v is not None:
            X.append(((v - v.mean()) / (v.std() + 1e-9)).ravel()); Y.append(ch); S.append(key)
    for pg, lines in data_lines(wd, pages).items():
        J, a = load(wd, pg); ot = ocr_tokens(wd, pg)
        for i, arr, last in lines:
            L = J["lines"][i - 1]; ink = set(c for c in L["cols"] if 7 <= c <= 72)
            reads = ot.get(i, []); n = max((len(r) for r in reads), default=0)
            pos = 7; cells = {}
            for k in range(n):
                v = [r[k] for r in reads if len(r) > k and r[k]]
                tok = max(set(v), key=v.count) if v else None
                if not tok or v.count(tok) < 2:
                    cells = None; break
                lay, w = tok_layout(tok, pos)
                body = {c for c in ink if pos <= c < pos + w - 1}
                if body != set(lay):
                    cells = None; break
                cells.update(lay)
                if pos + w - 1 in ink:
                    cells[pos + w - 1] = "/" if last and k == n - 1 else ","
                pos += w
            if cells:
                for col, ch in cells.items():
                    add(a, L, J["meta"], col, ch, (pg, i))
    cnt = {}
    for pg in range(109, 195):                               # verified code cards: signs, digits, punctuation
        f = wd / "final" / f"p{pg:03d}.tsv"
        if not f.exists() or 174 <= pg <= 182:
            continue
        J, a = load(wd, pg)
        for r in f.read_text().splitlines():
            x = r.split("\t")
            if len(x) < 5 or x[3] not in ("AGREE", "HAND") or x[4][:1] in "C*":
                continue
            L = J["lines"][int(x[0]) - 1]; card = x[4].ljust(72)
            for col in L["cols"]:
                ch = card[col - 1] if col <= 72 else " "
                if ch in CH and cnt.get(ch, 0) < 300:
                    cnt[ch] = cnt.get(ch, 0) + 1; add(a, L, J["meta"], col, ch, (pg, int(x[0])))
    for (pg, i), card in verified_cards(wd).items():          # hand-verified PAM cards
        J, a = load(wd, pg); L = J["lines"][i - 1]
        for col in L["cols"]:
            if col <= len(card) and card[col - 1] in CH:
                add(a, L, J["meta"], col, card[col - 1], (pg, i))
    return np.array(X), np.array(Y), S


def decode(ink, scores, nreads):
    """sequential parse of a card's ink (columns >= 7) -> list of (type, {col: char}, margin, missing, end)."""
    pos = 7; out = []
    while [c for c in ink if c > pos] and pos <= 66:
        best = None
        for typ, (allow, w) in TYPES.items():
            lay = {pos + p: al for p, al in allow.items()}
            body = {c for c in ink if pos < c < pos + w - 1}
            if not body <= set(lay) or (typ == "Z" and {c for c in ink if pos + 9 <= c <= pos + 11}):
                continue
            miss = set(lay) - body
            if len(miss) > 2:
                continue
            best = cand(best, typ, lay, body, miss, w, scores)
        dg = sorted(c for c in ink if pos < c < pos + 12)
        if dg:                                               # right-aligned integer
            lay = {c: DIG + "-" for c in range(dg[0], pos + 12)}
            body = {c for c in ink if pos < c < pos + 12}
            best = cand(best, "I", lay, body, set(lay) - body, 13, scores)
        if best is None:
            return out + [("?", {}, 0.0, set(), pos)]
        q, typ, txt, mg, miss, w = best
        if pos in ink:
            txt[pos] = "-"
        end = pos + w - 1
        if end in ink:                                       # '/' can only close the card
            sc = scores(end); txt[end] = "," if [c for c in ink if c > end] else max(",/", key=lambda c: sc[c])
        out.append((typ, txt, mg, miss, end))
        pos += w
    return out


def cand(best, typ, lay, body, miss, w, scores):
    txt = {}; tot = 0; mg = []
    for c, al in lay.items():
        if c not in body:
            txt[c] = "?"; continue
        sc = scores(c); o = sorted(al, key=lambda ch: -sc[ch])
        txt[c] = o[0]; tot += sc[o[0]]
        if len(o) > 1:
            mg.append(sc[o[0]] - sc[o[1]])
    q = tot / max(len(body), 1) - 0.15 * len(miss)
    if best is None or q > best[0]:
        return (q, typ, txt, min(mg) if mg else 1.0, miss, w)
    return best


def main_read(wd, pages, tau):
    X, Y, S = training(wd, pages)
    print("training cells", len(Y), {c: int((Y == c).sum()) for c in CH})
    Sarr = np.array([p * 1000 + i for p, i in S])
    (wd / "tables").mkdir(exist_ok=True)
    fixes = load_fixes(wd); review = []; stats = {"fields": 0, "ok": 0, "hand": 0}
    for pg, lines in data_lines(wd, pages).items():
        J, a = load(wd, pg); ot = ocr_tokens(wd, pg); rows = []
        for i, arr, last in lines:
            L = J["lines"][i - 1]
            keep = Sarr != pg * 1000 + i                       # never score a cell against itself
            Xk, Yk = X[keep], Y[keep]; cache = {}

            def scores(col):
                if col not in cache:
                    v, _ = cell_img(a, L, J["meta"], col)
                    if v is None:
                        cache[col] = {c: 0.0 for c in CH}
                    else:
                        vn = ((v - v.mean()) / (v.std() + 1e-9)).ravel(); s = Xk @ vn / len(vn)
                        cache[col] = {c: float(np.sort(s[Yk == c])[-3:].mean()) if (Yk == c).any() else -1 for c in CH}
                return cache[col]
            ink = set(c for c in L["cols"] if 7 <= c <= 72)
            status = []; toks = []; term = last
            reads = ot.get(i, []); fx = fixes.get((pg, i), {})
            for n, (typ, txt, mg, miss, end) in enumerate(decode(ink, scores, len(reads))):
                stats["fields"] += 1
                if typ == "I":
                    txt = {c: ch for c, ch in txt.items() if ch != "?"}
                tok = "".join(txt[c] for c in sorted(txt) if txt[c] not in ",/")
                if str(n + 1) in fx:
                    toks.append(fx[str(n + 1)]); status.append(f"{n+1}H"); stats["hand"] += 1
                    continue
                v = [r[n] for r in reads if len(r) > n and r[n]]
                agree = v.count(tok)
                ok = typ != "?" and "?" not in tok and (agree >= 2 or (agree == 1 and mg >= tau))
                status.append(f"{n+1}{typ}:{mg:.2f}/{agree}of{len(v)}" + ("" if ok else "!"))
                stats["ok"] += ok; toks.append(tok)
                if not ok:
                    review.append(f"p{pg}\t{i}\t{n+1}\t{tok}\t{' | '.join(sorted(set(v)))}")
            if "*" in fx:
                w = fx["*"].split(); term = w[-1] == "/"; toks = [t for t in w if t != "/"]; status = ["HAND"]
            rows.append(f"{i}\t{arr}\t{' '.join(status)}\t{' '.join(toks)}{' /' if term else ''}\t{render(toks, term)}")
        (wd / "tables" / f"p{pg:03d}.tsv").write_text("\n".join(rows) + "\n")
        print(f"p{pg}: {len(rows)} cards", flush=True)
    (wd / "tables" / "review.tsv").write_text("\n".join(review) + "\n")
    print(stats, "review fields:", len(review))


def main_proof(wd, pg, a, n, out):
    J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); m = J["meta"]
    im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
    rows = {int(l.split("\t")[0]): l.split("\t") for l in (wd / "tables" / f"p{pg:03d}.tsv").read_text().splitlines()}
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 34)
    strips = []
    for i in range(a, a + n):
        if i not in rows:
            continue
        r = rows[i]; card = r[4].ljust(72); L = J["lines"][i - 1]
        st = r[2].split() if r[2] != "HAND" else []
        card = r[4].ljust(72)
        # colour each field by its status: walk the card's commas to find field spans
        spans = []; start = 6
        for c in range(6, 72):
            if card[c] in ",/":
                spans.append((start, c)); start = c + 1
        bad = {k for k, t in enumerate(st) if t.endswith("!")}
        x0 = int(m["col1_x"] - m["pitch"] / 2); x1 = int(m["col1_x"] + 71.5 * m["pitch"])
        img = im.crop((x0, max(L["y0"] - 4, 0), x1, L["y1"] + 4)).convert("RGB")
        txt = Image.new("RGB", (img.width, 44), (235, 242, 255)); d = ImageDraw.Draw(txt)
        for c, ch in enumerate(card[:72]):
            if ch != " ":
                k = next((j for j, (s0, s1) in enumerate(spans) if s0 <= c <= s1), len(spans))
                hand = r[2] == "HAND" or (k < len(st) and st[k].endswith("H"))
                col = (0, 120, 0) if hand else (200, 0, 0) if k in bad or (k >= len(st) and c > 5) else (0, 0, 160)
                d.text((c * m["pitch"] + 3, 2), ch, font=font, fill=col)
        row = Image.new("RGB", (img.width + 70, img.height + 50), "white")
        ImageDraw.Draw(row).text((4, 10), str(i), fill=(0, 0, 0)); row.paste(img, (70, 0)); row.paste(txt, (70, img.height))
        strips.append(row); print(f"{i}\t{r[2]}\t{card.rstrip()}")
    W = max(s.width for s in strips); H = sum(s.height for s in strips)
    sheet = Image.new("RGB", (W, H), "white"); y = 0
    for s in strips:
        sheet.paste(s, (0, y)); y += s.height
    sheet.resize((int(W * 0.62), int(H * 0.62)), Image.LANCZOS).save(out)


if __name__ == "__main__":
    wd = Path(sys.argv[1])
    if sys.argv[2] == "read":
        tau = float(sys.argv[sys.argv.index("--tau") + 1]) if "--tau" in sys.argv else 0.08
        pages = [int(p) for p in sys.argv[3:] if p.isdigit()] or list(range(174, 183))
        main_read(wd, pages, tau)
    else:
        out = sys.argv[6] if len(sys.argv) > 6 else str(wd / "review-sheets" / "tableproof.png")
        main_proof(wd, int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), out)
