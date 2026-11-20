# -*- coding: utf-8 -*-
# 前のスポーツの姐さん（shuyaku1113/sheetB.png・透明あり）から「R」の帽子でバットを振る野球の姐さん（上の段まん中）だけを alpha のまま切る
#   cut_alpha9 を別の場所（tmp_b/）で回し、その2番目を poses/a2.png（a＝右向きで歩く子）に写す → 元の絵と並べた look_a2.png
import io, os, shutil, subprocess, sys
from PIL import Image, ImageDraw
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
T = D + 'tmp_b/'
os.makedirs(T + 'poses', exist_ok=True)
shutil.copyfile('C:/Users/user/oshinavi/tmp/video/shuyaku1113/sheetB.png', T + 'sheetB.png')
src = io.open(D + 'cut_alpha9.py', encoding='utf-8').read().replace("D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'", "D = '%s'" % T)
io.open(T + 'cut_alpha9.py', 'w', encoding='utf-8').write(src)
r = subprocess.run([sys.executable, T + 'cut_alpha9.py', 'sheetB.png', 'x'], capture_output=True, text=True, encoding='utf-8', errors='replace')
log = io.open(T + 'cut9_x.txt', encoding='utf-8').read()
shutil.copyfile(T + 'poses/x2.png', D + 'poses/a2.png')
import re
m = re.search(r'x2 大きさ .* シート上 \((\d+), (\d+), (\d+), (\d+)\)', log)
x0, y0, x1, y1 = map(int, m.groups())
sh = Image.open(T + 'sheetB.png').convert('RGBA')
blk = Image.alpha_composite(Image.new('RGBA', sh.size, (0, 0, 0, 255)), sh).convert('RGB')
pad = 30
b = (max(0, x0 - pad), max(0, y0 - pad), min(sh.width, x1 + pad), min(sh.height, y1 + pad))
o = blk.crop(b); sc = 700 / o.height; o = o.resize((int(o.width * sc), 700))
cut = Image.open(D + 'poses/a2.png'); c2 = cut.resize((int(cut.width * sc), int(cut.height * sc)))
g = Image.new('RGB', o.size, (0, 150, 60)); g.paste(c2, (int((x0 - b[0]) * sc), int((y0 - b[1]) * sc)), c2)
row = Image.new('RGB', (o.width * 2 + 20, 700), (40, 40, 40)); row.paste(o, (0, 0)); row.paste(g, (o.width + 20, 0))
row.save(D + 'look_a2.png')
io.open(D + 'cut_b2.txt', 'w', encoding='utf-8').write('rc %d\n%s' % (r.returncode, log))
