"""Merge the per-line OCR of several models into card images and list the lines that need a human look.

usage: python3 -I merge.py <workdir> <first_page> <last_page>

For each line, each model's code text (columns 1-72) is placed into the inked columns when its count of
non-blank characters equals the number of inked cells. Readings that place are compared:
  AGREE   >= 2 models place identically            -> accepted
  SINGLE  only one model places                    -> accepted provisionally, flagged
  CONFLICT models place differently                -> flagged (majority kept if any)
  NONE    no model places                          -> flagged, blank card
Comment lines (column 1 'C' or '*') are compared the same way.
Sequence fields (73-80) are taken from the per-page majority prefix and rebuilt as consecutive numbers.
Writes <workdir>/merged/p<page>.tsv (line, y0, y1, verdict, card, readings) and review/p<page>-<line>.png.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

MODELS = ("lighton", "dots", "glm")


def place(text, cols, ink=None):
    chars = [c for c in text if not c.isspace()]
    extra = len(cols) - len(chars)
    if extra in (1, 2) and ink:          # ignore up to two tiny specks (<= 12 px)
        specks = sorted((ink.get(str(c), 99), c) for c in cols)
        drop = [c for v, c in specks[:extra] if v <= 12]
        if len(drop) == extra:
            cols = [c for c in cols if c not in drop]
    if len(chars) != len(cols):
        return None
    card = [" "] * 72
    for c, k in zip(chars, cols):
        card[k - 1] = c
    return "".join(card)


def main():
    wd = Path(sys.argv[1]); p0, p1 = int(sys.argv[2]), int(sys.argv[3])
    (wd / "merged").mkdir(exist_ok=True); (wd / "review").mkdir(exist_ok=True)
    stats = Counter()
    for pg in range(p0, p1 + 1):
        J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); meta, lines = J["meta"], J["lines"]
        reads = {}
        for m in MODELS:
            for tag, d in ((m, f"ocr-{m}"), (m + "2", f"ocr2-{m}")):
                f = wd / d / f"p{pg:03d}.tsv"
                if f.exists():
                    reads[tag] = {int(r.split("\t")[0]): r.rstrip("\n").split("\t")[4]
                                  for r in f.read_text().splitlines() if r}
        im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
        seqs = []
        out = []
        for i, L in enumerate(lines, 1):
            ccols = [c for c in L["cols"] if c <= 72]
            placed = {}
            rawcode = {}
            seqtxt = {}
            for m, R in reads.items():
                raw = R.get(i, "")
                parts = raw.split(" || ")
                code = parts[0] if ccols else ""
                seq = parts[-1] if any(c >= 73 for c in L["cols"]) and not m.endswith("2") else ""
                if not ccols:
                    seq = parts[0] if parts and not m.endswith("2") else ""
                if m.endswith("2") and i not in R:
                    continue
                if ccols:
                    p = place(code, ccols, L.get("ink"))
                    if p is None and max(ccols) == 72:   # crop bled into column 73: drop one trailing char
                        ch = [c for c in code if not c.isspace()]
                        if len(ch) == len(ccols) + 1:
                            p = place("".join(ch[:-1]), ccols, L.get("ink"))
                    if p is not None:
                        placed[m] = p
                    rawcode[m] = code
                if seq:
                    seqtxt[m] = re.sub(r"\s+", "", seq)
            firsts = [c.strip()[:1] for c in rawcode.values() if c.strip()]
            alltxt = [c for c in rawcode.values() if c]
            garbage = not any(re.search(r"[A-Z0-9]{2}", c) for c in alltxt)
            starts_c = any(re.match(r"C\s", c.strip() + " ") for c in alltxt)
            is_comment = bool(ccols) and ccols[0] <= 2 and starts_c and not any(c in ccols for c in (6,)) or \
                bool(ccols) and ccols[0] == 1 and (
                any(f in ("C", "*") for f in firsts) or len(ccols) >= 50 or ccols == [1]) and \
                not (firsts and all(f.isdigit() for f in firsts))
            ties = []
            hasseq = any(c >= 73 for c in L["cols"])
            if not hasseq or (garbage and len(ccols) > 20):
                verdict, card = "NOISE", " " * 72
            elif not ccols:
                verdict, card = "SEQONLY", " " * 72
            elif is_comment:
                if placed:
                    card = Counter(placed.values()).most_common(1)[0][0]
                else:
                    txt = max(rawcode.values(), key=len) if rawcode else "C"
                    txt = txt.strip()
                    txt = txt if txt.startswith(("C", "*")) else "C" + txt
                    card = ("C" + txt[1:])[:72].ljust(72)
                verdict = "COMMENT"
            elif not placed:
                verdict, card = "NONE", " " * 72
            else:
                c = Counter(placed.values())
                best, n = c.most_common(1)[0]
                if len(c) == 1:
                    verdict = "AGREE" if n >= 2 else "SINGLE"
                    card = best
                else:   # vote column by column
                    vals = list(placed.values())
                    out_c = []
                    for k in range(72):
                        cc = Counter(v[k] for v in vals)
                        ch, nn = cc.most_common(1)[0]
                        if nn * 2 <= len(vals) and len(cc) > 1:
                            ties.append(k + 1)
                        out_c.append(ch)
                    card = "".join(out_c)
                    verdict = "VOTED" if not ties else "TIE"
            stats[verdict] += 1
            m = Counter()
            for s in seqtxt.values():
                mm = re.match(r"([A-Z0-9]{1,6}?[A-Z])(\d{1,4})$", s)
                if mm:
                    m[(mm.group(1), int(mm.group(2)))] += 1
            seqs.append(m.most_common(1)[0][0] if m else None)
            out.append([i, L["y0"], L["y1"], verdict, card, ",".join(map(str, ties)), " ## ".join(f"{k}={v.rstrip()}" for k, v in placed.items())])
            if verdict not in ("AGREE", "VOTED", "SEQONLY", "COMMENT", "NOISE"):
                y0, y1 = max(L["y0"] - 8, 0), min(L["y1"] + 8, im.height)
                x0 = int(meta["col1_x"] - meta["pitch"]); x1 = int(meta["col1_x"] + 72 * meta["pitch"])
                im.crop((max(x0, 0), y0, min(x1, im.width), y1)).save(wd / "review" / f"p{pg:03d}-{i:02d}.png")
        # sequence: majority prefix per page; numbers consecutive from the best-supported anchor
        prefixes = Counter(s[0] for s in seqs if s)
        for k, row in enumerate(out):
            s = seqs[k]
            row.append(f"{s[0]}{s[1]}" if s else "")
        (wd / "merged" / f"p{pg:03d}.tsv").write_text(
            "".join("\t".join(map(str, r)) + "\n" for r in out))
    print(dict(stats))


if __name__ == "__main__":
    main()
