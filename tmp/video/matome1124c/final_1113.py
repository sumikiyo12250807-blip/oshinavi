# -*- coding: utf-8 -*-
# 全編 out_x.mp4 の確かめ：①長さ・大きさ・形式 ②音ずれ（書き出しの音と曲の音の包絡を相関・ずれの秒）
#   ③字幕の塊と USLT の行を並べる（名前・県・時刻の読みを目で照らす）④塊ごとのまん中の秒のコマを書き出しから取り出して1枚に → final_1113.txt・final_contact.png
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
V = D + 'out_x.mp4'
out = []
info = subprocess.run([ff, '-i', V], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
si = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
ms = re.search(r'Duration: (\d+):(\d+):([\d.]+)', si)
sdur = int(ms.group(2)) * 60 + float(ms.group(3))
out.append('長さ %.2f 秒（曲 %.2f 秒）大きさ %.2fMB 1080x1920 %s h264 %s aac %s' % (dur, sdur, os.path.getsize(V) / 1048576, '1080x1920' in info, 'h264' in info, 'aac' in info))


def env(p):
    raw = subprocess.run([ff, '-v', 'error', '-i', p, '-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
    a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
    h = 80   # 10ms
    return np.array([np.sqrt(np.mean(a[i:i + h] ** 2)) for i in range(0, len(a) - h, h)])


ev, es = env(V), env(D + 'song.mp3')
n = min(len(ev), len(es)) - 200
best = max(range(-30, 31), key=lambda k: float(np.corrcoef(ev[100 + k:100 + k + n - 100], es[100:100 + n - 100])[0, 1]))
out.append('音ずれ %+d0 ms（書き出しの音と曲の音の包絡がいちばん合うずれ・0 なら ずれ無し）' % best)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
us = [l.strip() for l in io.open(D + 'uslt.txt', encoding='utf-8').read().splitlines() if l.strip() and not l.startswith('[')]
out.append('== 字幕の塊（秒・行）')
ts = []
for c in S['chunks']:
    rows = [''.join(w + (' ' if s else '') for w, _, s in r) for r in c['lines']]
    out.append('  %6.2f〜%6.2f %s' % (c['show'], c['hide'], ' ／ '.join(rows)))
    ts.append(round((c['show'] + min(c['hide'], c['show'] + 3)) / 2, 2))
out.append('== USLT の行')
out += ['  ' + u for u in us]
os.makedirs(D + 'final', exist_ok=True)
ims = []
for t in ts:
    p = D + 'final/f_%06.2f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', str(t), '-i', V, '-frames:v', '1', p])
    ims.append((t, Image.open(p).convert('RGB').resize((270, 480))))
cols = 8
g = Image.new('RGB', (cols * 280, ((len(ims) + cols - 1) // cols) * 520), (30, 30, 30))
font = ImageFont.truetype('C:/Windows/Fonts/meiryob.ttc', 20)
for i, (t, im) in enumerate(ims):
    x, y = (i % cols) * 280, (i // cols) * 520
    g.paste(im, (x, y + 34))
    ImageDraw.Draw(g).text((x + 4, y + 4), '%.1f秒' % t, fill=(255, 255, 0), font=font)
g.save(D + 'final_contact.png')
io.open(D + 'final_1113.txt', 'w', encoding='utf-8').write('\n'.join(out))
