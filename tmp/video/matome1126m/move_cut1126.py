# -*- coding: utf-8 -*-
# 11/26 演歌と舞台（ミュージカル調）：1人3コマ＝move_cut1125 の形・シートは1枚ずつ（9人で1枚）
#   2コマ目 Downloads/musical_move2_1126.png → v1〜v9 → e（右向き）・f（反転）
#   3コマ目 Downloads/musical_move3_1126.png → u1〜u9 → g・h
#   cut17 が上下2人を1つにした時（背が他の1.6倍）は、透明の少ない行で上下に分け、抜けた番号に上を入れる
#   → contact_move.png（元・2コマ目・3コマ目を組で並べる）
import io, os, subprocess, sys, shutil
from PIL import Image, ImageOps
sys.stdout.reconfigure(encoding='utf-8')
V = 'C:/Users/user/oshinavi/tmp/video/'
D = V + 'matome1126m/'
P = D + 'poses/'
DL = 'C:/Users/user/Downloads/'
out = io.open(D + 'move_cut1126.txt', 'w', encoding='utf-8')
for k in range(1, 10):
    w = Image.open(P + 'w%d.png' % k)
    w.save(P + 's%d.png' % k)
    ImageOps.mirror(w).save(P + 't%d.png' % k)
def split_merged(px):
    have = {k: P + '%s%d.png' % (px, k) for k in range(1, 10) if os.path.exists(P + '%s%d.png' % (px, k))}
    miss = [k for k in range(1, 10) if k not in have]
    if not miss:
        return
    hs = sorted(Image.open(p).height for p in have.values())
    med = hs[len(hs) // 2]
    for k, p in sorted(have.items()):
        im = Image.open(p).convert('RGBA')
        if im.height > med * 1.6 and miss:
            a = im.split()[3]; w, h = im.size
            rows = [sum(1 for x in range(w) if a.getpixel((x, y)) > 20) for y in range(h)]
            cut = min(range(int(h * .35), int(h * .65)), key=lambda y: rows[y])
            top = im.crop((0, 0, w, cut)); top = top.crop(top.getbbox())
            bot = im.crop((0, cut, w, h)); bot = bot.crop(bot.getbbox())
            m = miss.pop(0)
            # 抜けた番号が上の段（m < k）なら上を m に、下を k に
            (top if m < k else bot).save(P + '%s%d.png' % (px, m))
            (bot if m < k else top).save(P + '%s%d.png' % (px, k))
            out.write('分けた %s%d（高さ %d）→ %s%d と %s%d\n' % (px, k, h, px, m, px, k))
def cut(fname, px):
    shutil.copyfile(DL + fname, D + 'sheet_%s.png' % px)
    for k in range(1, 10):
        if os.path.exists(P + '%s%d.png' % (px, k)):
            os.remove(P + '%s%d.png' % (px, k))
    r = subprocess.run([sys.executable, V + 'shuyaku1117/cut17.py', 'sheet_%s.png' % px, px, D], capture_output=True, text=True, encoding='utf-8', errors='replace')
    out.write('cut %s rc %d %s\n' % (px, r.returncode, r.stderr[-400:]))
    split_merged(px)
cut('musical_move2_1126.png', 'v')
cut('musical_move3_1126t.png', 'u')   # 3コマ目は市松模様の背景を unchecker.py で透明にした版
tiles = []
for k in range(1, 10):
    w = Image.open(P + 'w%d.png' % k).convert('RGBA')
    row = [w]
    for src, a, b in (('v', 'e', 'f'), ('u', 'g', 'h')):
        p = P + '%s%d.png' % (src, k)
        if not os.path.exists(p):
            out.write('無い %s%d\n' % (src, k)); continue
        c = Image.open(p).convert('RGBA')
        rr = w.height / c.height
        c2 = c.resize((round(c.width * rr), round(c.height * rr)), Image.LANCZOS)
        c2.save(P + '%s%d.png' % (a, k))
        ImageOps.mirror(c2).save(P + '%s%d.png' % (b, k))
        out.write('%d %s %s → %s 倍率 %.3f\n' % (k, src, c.size, c2.size, rr))
        row.append(c2)
    tiles.append(row)
th = 300
W = max(sum(int(t.width * th / t.height) + 16 for t in r) for r in tiles) + 32
H = len(tiles) * (th + 24) + 24
sheet = Image.new('RGBA', (W, H), (0, 150, 60, 255))
y = 16
for r in tiles:
    x = 16
    for t in r:
        t2 = t.resize((int(t.width * th / t.height), th), Image.LANCZOS)
        sheet.alpha_composite(t2, (x, y)); x += t2.width + 16
    y += th + 24
sheet.convert('RGB').save(D + 'contact_move.png')
out.close()
print('ok')
