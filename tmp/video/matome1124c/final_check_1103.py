# -*- coding: utf-8 -*-
# 11/3 全編の点検：out.mp4 / out_x.mp4 の長さ・大きさ・形式／音と映像それぞれの長さ／タップ場面が本物の画面か／
#   拍（キャラが沈む時刻）と音のずれ（スネア・キック）／場面ごとの静止画 contact_final.png
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
    print(os.path.basename(V), '長さ', d, '大きさ %.2fMB（%d バイト）' % (os.path.getsize(V) / 1048576, os.path.getsize(V)), '1080x1920', '1080x1920' in info, 'h264', 'h264' in info, 'aac', 'aac' in info, file=log)
print('曲', dur_of(D + 'song.mp3')[0], file=log)
V = D + 'out_x.mp4'
# 音の長さ（デコードしたサンプル数）と映像の長さ（コマ数）
raw = subprocess.run([ff, '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '22050', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
r = subprocess.run([ff, '-v', 'error', '-i', V, '-an', '-f', 'null', '-'], capture_output=True, text=True, errors='replace')
s = subprocess.run([ff, '-i', V, '-an', '-f', 'null', '-'], capture_output=True, text=True, errors='replace').stderr
fm = re.findall(r'frame=\s*(\d+)', s)
nf = int(fm[-1]) if fm else -1
print('音の長さ %.2f 秒／映像 %d コマ＝%.2f 秒（30fps）' % (len(a) / 22050, nf, nf / 30.0), file=log)
rms = [float(np.sqrt(np.mean(a[i:i + 22050] ** 2))) for i in range(0, len(a), 22050)]
print('音の大きさ（1秒ごと）', ' '.join('%.2f' % v for v in rms), file=log)
# 拍と音のずれ
SR, HOP, NFFT = 22050, 64, 2048
y = a
n = 1 + (len(y) - NFFT) // HOP
fr = np.lib.stride_tricks.as_strided(y, shape=(n, NFFT), strides=(y.strides[0] * HOP, y.strides[0]))
S = np.abs(np.fft.rfft(fr * np.hanning(NFFT).astype(np.float32), axis=1))
fq = np.fft.rfftfreq(NFFT, 1 / SR)
T = (np.arange(n) + NFFT / 2 / HOP) / (SR / HOP)
beats = np.array([x for x in json.load(io.open(D + 'beats.json'))['beats'] if 1 <= x < 104])
for name, lo, hi in (('スネア', 150, 4000), ('キック', 30, 150)):
    b = np.log1p(10 * S[:, (fq >= lo) & (fq < hi)])
    k = np.concatenate([[0], np.maximum(0, np.diff(b, axis=0)).sum(axis=1)])
    res = []
    for L in np.arange(-0.08, 0.081, 0.004):
        idx = np.clip(np.searchsorted(T, beats + L), 0, len(k) - 1)
        res.append((float(k[idx].mean() / k.mean()), round(L * 1000)))
    res.sort(reverse=True)
    print('%s：一番合うずれ %d ms（強さ %.2f）・0ms の強さ %.2f' % (name, res[0][1], res[0][0], dict((l, v) for v, l in res)[0]), file=log)
os.makedirs(D + 'frames', exist_ok=True)


def grab(t):
    p = D + 'frames/f_%06.2f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', V, '-frames:v', '1', p], check=True)
    return Image.open(p).convert('RGB')


scr = np.asarray(Image.open(D + 'cards/screen_badge.png').convert('RGB').crop((0, 0, 1080, 1290))).astype(int)
for t in (85.0, 92.0):
    f = np.asarray(grab(t).crop((0, 0, 1080, 1290))).astype(int)
    print('タップ場面', t, '秒 本物の画面との差（平均）', round(float(np.abs(f - scr).mean()), 1), '（小さいほど同じ）', file=log)
T2 = [1.5, 5.0, 10.0, 13.0, 17.0, 21.0, 24.0, 28.0, 31.0, 35.0, 39.0, 43.0, 47.0, 50.0, 54.0, 58.0, 61.0, 64.0,
      69.0, 71.0, 76.0, 80.0, 84.0, 90.0, 97.0, 103.0, 108.0, 111.0]
fnt = ImageFont.truetype(r'C:\Windows\Fonts\YuGothB.ttc', 24)
cw, ch, cols = 216, 384, 7
rows = (len(T2) + cols - 1) // cols
out = Image.new('RGB', (cols * (cw + 8) + 8, rows * (ch + 36) + 8), (20, 20, 24))
dr = ImageDraw.Draw(out)
for j, t in enumerate(T2):
    x, y0 = 8 + (j % cols) * (cw + 8), 8 + (j // cols) * (ch + 36)
    out.paste(grab(t).resize((cw, ch), Image.LANCZOS), (x, y0))
    dr.text((x + 4, y0 + ch + 4), '%.1fs' % t, font=fnt, fill=(255, 255, 255))
out.save(D + 'contact_final.png')
log.close()
print(io.open(D + 'final_check.txt', encoding='utf-8').read())
