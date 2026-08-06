# -*- coding: utf-8 -*-
"""透過キャラシートを1カットずつに切り分ける（アルファの空白で行と列を割る）。

  python tools/sheet_split.py <sheet.png> <出力ディレクトリ>

透過PNG専用。行→列の順に「アルファが全部0の帯」を境目にして分割し、
各カットを余白なしでトリミングして保存する。手で座標を測らないための道具。
"""
import io, os, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

src, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
im = Image.open(src).convert("RGBA")
W, H = im.size
a = im.getchannel("A")
px = a.load()
print("シート %dx%d" % (W, H))

MIN_A = 8          # これ以下は透明とみなす
GAP = 12           # この幅以上の空白を境目にする


def bands(is_filled, n, gap):
    out, start = [], None
    run = 0
    for i in range(n):
        if is_filled(i):
            if start is None:
                start = i - run if run and start is None and False else i
            run = 0
        else:
            run += 1
            if start is not None and run >= gap:
                out.append((start, i - run + 1))
                start = None
    if start is not None:
        out.append((start, n))
    return [(s, e) for s, e in out if e - s > 20]


def row_filled(y):
    return any(px[x, y] > MIN_A for x in range(0, W, 3))


rows = bands(row_filled, H, GAP)
print("行 %d本: %s" % (len(rows), rows))

n = 0
for ri, (y0, y1) in enumerate(rows, 1):
    def col_filled(x, y0=y0, y1=y1):
        return any(px[x, y] > MIN_A for y in range(y0, y1, 3))
    cols = bands(col_filled, W, GAP)
    print("  行%d → %d カット" % (ri, len(cols)))
    for ci, (x0, x1) in enumerate(cols, 1):
        cut = im.crop((x0, y0, x1, y1))
        bbox = cut.getbbox()
        if bbox:
            cut = cut.crop(bbox)
        p = os.path.join(outdir, "r%dc%d.png" % (ri, ci))
        cut.save(p)
        n += 1
        print("     %s  %dx%d" % (os.path.basename(p), cut.size[0], cut.size[1]))
print("計 %d カット → %s" % (n, outdir))
