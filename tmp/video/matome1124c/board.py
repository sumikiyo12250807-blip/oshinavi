# -*- coding: utf-8 -*-
# 絵コンテ：場面ごとの静止画（古いコマを消して出し直す）→ 1枚に並べる（board.png・秒と衣装を書く）
import io, os, glob, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
TS = [38.0] if '--one' in sys.argv else [2.5, 7.0, 12.0, 16.5, 21.5, 26.0, 31.0, 35.5, 40.5, 45.0, 50.0, 54.0, 57.5, 61.0, 63.5, 65.6]   # 11/14：10着＋タップ2つ＋締め＋後奏・最後の2秒（65.6）
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in TS)], capture_output=True, text=True, encoding='utf-8', errors='replace')
pose = {}
for l in r.stdout.splitlines():
    if l.startswith('frame '):
        _, t, p = l.split()
        pose[float(t)] = p
fs = sorted(glob.glob(D + 'frames/h_*.png'))
W, H = 360, 640
cols = 6
out = Image.new('RGB', (cols * (W + 10), ((len(TS) + cols - 1) // cols) * (H + 50)), (30, 30, 30))
font = ImageFont.truetype('C:/Windows/Fonts/meiryob.ttc', 24)
for i, f in enumerate(fs):
    t = float(os.path.basename(f)[2:-4])
    im = Image.open(f).resize((W, H))
    x, y = (i % cols) * (W + 10), (i // cols) * (H + 50)
    out.paste(im, (x, y + 40))
    ImageDraw.Draw(out).text((x + 6, y + 6), '%.1f秒  %s' % (t, pose.get(t, '')), fill=(255, 255, 255), font=font)
out.save(D + 'board.png')
io.open(D + 'board.txt', 'w', encoding='utf-8').write(r.stdout[-1500:] + r.stderr[-1500:])
