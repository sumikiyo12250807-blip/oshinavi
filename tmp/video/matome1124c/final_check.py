# -*- coding: utf-8 -*-
# out.mp4 / out_x.mp4 を確かめる＝長さ・解像度・形式・音・タップ場面で本物の画面・場面ごとの静止画 contact_final.png
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
log = io.open(D + 'final_check.txt', 'w', encoding='utf-8')


def dur_of(p):
    s = subprocess.run([ff, '-i', p], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
    m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', s)
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)), s


for V in (D + 'out.mp4', D + 'out_x.mp4'):
    d, info = dur_of(V)
    print(os.path.basename(V), '長さ', d, '大きさ %.2fMB' % (os.path.getsize(V) / 1048576), '1080x1920', '1080x1920' in info, 'h264', 'h264' in info, 'aac', 'aac' in info, file=log)
print('曲', dur_of(D + 'song.mp3')[0], file=log)
V = D + 'out_x.mp4'
raw = subprocess.run([ff, '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
rms = [float(np.sqrt(np.mean(a[i:i + 8000] ** 2))) for i in range(0, len(a), 8000)]
print('音の大きさ（1秒ごと）', ' '.join('%.2f' % r for r in rms), file=log)
os.makedirs(D + 'frames', exist_ok=True)


def grab(t):
    p = D + 'frames/f_%05.2f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', V, '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGB')


scr = np.asarray(Image.open(D + 'cards/screen_badge.png').convert('RGB').crop((0, 0, 1080, 1290))).astype(int)
for t in (70.0, 76.0):
    f = np.asarray(grab(t).crop((0, 0, 1080, 1290))).astype(int)
    print('タップ場面', t, '秒 本物の画面との差（平均）', round(float(np.abs(f - scr).mean()), 1), '（小さいほど同じ）', file=log)
T = [1.5, 6.0, 10.0, 14.0, 17.0, 21.0, 26.0, 30.0, 34.0, 40.0, 46.0, 51.0, 56.0, 62.0, 66.0, 70.0, 76.0, 82.0]
fnt = ImageFont.truetype(r'C:\Windows\Fonts\YuGothB.ttc', 24)
cw, ch, cols = 216, 384, 9
rows = (len(T) + cols - 1) // cols
out = Image.new('RGB', (cols * (cw + 8) + 8, rows * (ch + 36) + 8), (20, 20, 24))
dr = ImageDraw.Draw(out)
for j, t in enumerate(T):
    x, y = 8 + (j % cols) * (cw + 8), 8 + (j // cols) * (ch + 36)
    out.paste(grab(t).resize((cw, ch), Image.LANCZOS), (x, y))
    dr.text((x + 4, y + ch + 4), '%.1fs' % t, font=fnt, fill=(255, 255, 255))
out.save(D + 'contact_final.png')
log.close()
