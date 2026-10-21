"""Second OCR pass on the flagged code lines, with a tight crop (columns 1-72 only, everything else white)
and a larger scale.

usage: python3 -I reocr.py <workdir> <model> [--port 8097]
Reads <workdir>/merged/p*.tsv, re-reads lines whose verdict is NONE/SINGLE/TIE, writes
<workdir>/ocr2-<model>/p<page>.tsv in the same format as ocrlines.py (line, y0, status, card, raw).
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path.home() / ".claude/skills/book-ocr/scripts"))
from common import MODELS, MODELS_DIR, SERVER  # noqa: E402
from ocrlines import LINE_PROMPT, ask, clean, place  # noqa: E402


def main():
    wd, model = Path(sys.argv[1]), sys.argv[2]
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8097
    mfile, mmproj, mprompt = MODELS[model]
    prompt = mprompt if model != "lighton" else None
    out = wd / f"ocr2-{model}"; out.mkdir(exist_ok=True)
    todo = {}
    rng = [int(a) for a in sys.argv[3:5] if a.isdigit()] if len(sys.argv) > 4 and sys.argv[3].isdigit() else None
    for f in sorted((wd / "merged").glob("p*.tsv")):
        pg = int(f.stem[1:])
        if rng and not (rng[0] <= pg <= rng[1]):
            continue
        rows = [r.split("\t") for r in f.read_text().splitlines() if r]
        todo[pg] = [int(r[0]) for r in rows if r[3] in ("NONE", "SINGLE", "TIE")]
    log = open(wd / f"server-reocr-{model}.log", "w")
    proc = subprocess.Popen([str(SERVER), "-m", str(MODELS_DIR / mfile), "--mmproj", str(MODELS_DIR / mmproj),
                             "-ngl", "99", "-c", "4096", "--port", str(port), "--no-webui"], stdout=log, stderr=log)
    try:
        for _ in range(300):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2); break
            except Exception:
                time.sleep(1)
        for pg, idx in todo.items():
            if not idx:
                continue
            J = json.load(open(wd / "lines" / f"p{pg:03d}.json")); meta, lines = J["meta"], J["lines"]
            im = Image.open(sorted((wd / "native").glob(f"n-{pg:03d}-*.png"))[0]).convert("L")
            P, x1 = meta["pitch"], meta["col1_x"]
            res = []
            for i in idx:
                L = lines[i - 1]
                cols = [c for c in L["cols"] if c <= 72]
                y0, y1 = max(L["y0"] - 6, 0), min(L["y1"] + 6, im.height)
                xa = int(x1 + (min(cols) - 1) * P - P / 2)
                xb = int(x1 + 71 * P + P / 2 - 2)          # right edge of column 72, nothing beyond
                crop = im.crop((max(xa, 0), y0, min(xb, im.width), y1))
                crop = crop.resize((int(crop.width * 2.5), int(crop.height * 2.5)), Image.LANCZOS)
                pad = Image.new("L", (max(crop.width + 100, 1000), crop.height + 50), 255); pad.paste(crop, (50, 25))
                text = clean(ask(port, pad, prompt or LINE_PROMPT))
                card, st = place(text, cols)
                res.append(f"{i}\t{L['y0']}\t{st}\t{card}\t{text}")
            (out / f"p{pg:03d}.tsv").write_text("\n".join(res) + "\n")
            print(f"p{pg:03d}: {len(res)} lines, {sum('OK' in r.split(chr(9))[2] for r in res)} OK", flush=True)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
