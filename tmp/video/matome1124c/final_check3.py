# -*- coding: utf-8 -*-
# 第3版 out3.mp4 / out3_x.mp4 を確かめる（final_check.py の形）＋場面ごとの静止画 contact3.png
#   長さ・解像度・形式・音の有無・字幕の最後の塊・サビ2回で本物のOSHINAVIの画面が出ているか・X版の大きさ
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()


def dur_of(p):
    s = subprocess.run([ff, '-i', p], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)), s


for V in (D + 'out3.mp4', D + 'out3_x.mp4'):
    d, info = dur_of(V)
    print(os.path.basename(V), '長さ', d, '大きさ %.2fMB' % (os.path.getsize(V) / 1048576), '1080x1920', '1080x1920' in info, 'h264', 'h264' in info, 'aac', 'aac' in info)
print('曲', dur_of(D + 'song.mp3')[0])
V = D + 'out3.mp4'
raw = subprocess.run([ff, '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
rms = [float(np.sqrt(np.mean(a[i:i + 8000] ** 2))) for i in range(0, len(a), 8000)]
print('音の大きさ（1秒ごと）', ' '.join('%.2f' % r for r in rms))
S = json.load(io.open(D + 'sports_1026_v3.json', encoding='utf-8'))
last = S['chunks'][-1]
print('字幕の最後の塊', last['show'], '〜', last['hide'], [''.join(w + (' ' if s else '') for w, _, s in r) for r in last['lines']])


def grab(t, V=V):
    p = D + 'frames/c3_%05.2f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', V, '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGB')


scr = np.asarray(Image.open(D + 'cards/screen_badge.png').convert('RGB').crop((0, 0, 1080, 1290))).astype(int)
for name, t in (('最初のサビ', 43.5), ('最後のサビ', 59.0)):
    f = np.asarray(grab(t).crop((0, 0, 1080, 1290))).astype(int)
    print(name, t, '秒 画面との差（平均）', round(float(np.abs(f - scr).mean()), 1), '（10未満なら出ている）')
shots = []
P = S['poses']
for i, (t0, k) in enumerate(P):
    t1 = P[i + 1][0] if i + 1 < len(P) else S['scenes'][3][0]
    tm = (t0 + t1) / 2
    if S['scenes'][1][0] <= tm < S['scenes'][2][0]:
        tm = (t0 + S['scenes'][1][0]) / 2
    if any(abs(tm - c['show']) < 0.35 for c in S['chunks']):
        tm += 0.6
    shots.append(('%s %.1fs' % (k, tm), tm))
shots.insert(8, ('OSHINAVI 43.5s', 43.5))
shots.append(('OSHINAVI 59.0s', 59.0))
fnt = ImageFont.truetype(r'C:\Windows\Fonts\YuGothB.ttc', 24)
cw, ch, cols = 270, 480, 6
rows = (len(shots) + cols - 1) // cols
out = Image.new('RGB', (cols * (cw + 10) + 10, rows * (ch + 44) + 10), (20, 20, 24))
dr = ImageDraw.Draw(out)
for j, (lab, t) in enumerate(shots):
    x, y = 10 + (j % cols) * (cw + 10), 10 + (j // cols) * (ch + 44)
    out.paste(grab(t).resize((cw, ch), Image.LANCZOS), (x, y))
    dr.text((x + 4, y + ch + 6), lab, font=fnt, fill=(255, 255, 255))
out.save(D + 'contact3.png')
print('contact3', len(shots), '枚')
