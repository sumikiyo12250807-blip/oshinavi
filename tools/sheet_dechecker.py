# -*- coding: utf-8 -*-
"""「透過に見せた市松模様」や白地の背景を、本当の透過に抜く。

  python tools/sheet_dechecker.py <in.png> <out.png>

生成AIのキャラシートは、透過のつもりで**市松模様そのものを描いて**返してくることがある
（2026-08-06 実例）。四隅から外周つながりの「彩度が低く明るい」画素だけを塗り消すので、
キャラの中の白（歯・白目・ハイライト）は残る。
"""
import io, sys, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGBA")
W, H = im.size
px = im.load()

SAT = 26        # これ以下の彩度＝色味がない
VAL = 196       # これ以上の明るさ


def is_bg(x, y):
    r, g, b, a = px[x, y]
    if a < 8:
        return True
    return (max(r, g, b) - min(r, g, b)) <= SAT and max(r, g, b) >= VAL


# 外周から連結している背景だけを塗る（内部の白は守る）
seen = bytearray(W * H)
q = collections.deque()
for x in range(W):
    for y in (0, H - 1):
        if is_bg(x, y) and not seen[y * W + x]:
            seen[y * W + x] = 1
            q.append((x, y))
for y in range(H):
    for x in (0, W - 1):
        if is_bg(x, y) and not seen[y * W + x]:
            seen[y * W + x] = 1
            q.append((x, y))

n = 0
while q:
    x, y = q.popleft()
    px[x, y] = (0, 0, 0, 0)
    n += 1
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and is_bg(nx, ny):
            seen[ny * W + nx] = 1
            q.append((nx, ny))

im.save(dst)
print("背景を %d px 抜いた（全体の %.1f%%） → %s" % (n, 100.0 * n / (W * H), dst))
