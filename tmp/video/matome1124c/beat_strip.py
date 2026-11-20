# -*- coding: utf-8 -*-
# 拍に乗っているかの点検：拍の時刻の前後（-0.14・-0.07・0・+0.07・+0.14 秒）のコマを並べる（キャラの足元に拍の線）
#   → beat_strip.png ／ 3段（かぼちゃの列 185・キャラ・歌詞の上端）の線を引いた1枚 → tiers.png
import io, json, os, subprocess, sys, glob
from PIL import Image, ImageDraw, ImageFont
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
B = json.load(io.open(D + 'beats.json'))['beats']
b = min(B, key=lambda x: abs(x - 25.0))
OFF = [-0.14, -0.07, 0.0, 0.07, 0.14]
TS = [round(b + o, 3) for o in OFF] + [16.0, 45.0]
for f in glob.glob(D + 'frames/h_*.png'):
    os.remove(f)
r = subprocess.run([sys.executable, D + 'render.py', '--frames', ','.join(str(t) for t in TS)], capture_output=True, text=True, encoding='utf-8', errors='replace')
fs = {round(float(os.path.basename(f)[2:-4]), 1): f for f in glob.glob(D + 'frames/h_*.png')}
font = ImageFont.truetype('C:/Windows/Fonts/meiryob.ttc', 30)
cells = []
for o, t in zip(OFF, TS[:5]):
    im = Image.open(D + 'frames/h_%05.1f.png' % t).crop((140, 150, 940, 1000)).resize((400, 425))
    d = ImageDraw.Draw(im)
    y = int((845 - 150) / 2)
    d.line((0, y, 400, y), fill=(0, 255, 255), width=1)
    d.text((6, 4), '拍%+.2f秒' % o, fill=(255, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
    cells.append(im)
out = Image.new('RGB', (5 * 410, 425), (30, 30, 30))
for i, c in enumerate(cells):
    out.paste(c, (i * 410, 0))
out.save(D + 'beat_strip.png')
im = Image.open(D + 'frames/h_016.0.png').convert('RGB')
d = ImageDraw.Draw(im)
for y, lab in ((185, 'かぼちゃの列の下 185'), (245, 'すき間の上 245（列の下＋60）'), (845, 'すき間の下 845（歌詞−60）'), (905, '歌詞3行のいちばん上 905')):
    d.line((0, y, 1080, y), fill=(0, 255, 255), width=3)
    d.text((10, y - 40), lab, fill=(0, 255, 255), font=font, stroke_width=3, stroke_fill=(0, 0, 0))
im.resize((540, 960)).save(D + 'tiers.png')
im2 = Image.open(D + 'frames/h_045.0.png').convert('RGB')
d2 = ImageDraw.Draw(im2)
for y in (185, 245, 845, 980):
    d2.line((0, y, 1080, y), fill=(0, 255, 255), width=3)
im2.resize((540, 960)).save(D + 'tiers2.png')
print('beat', b, r.returncode, r.stderr[-500:])
