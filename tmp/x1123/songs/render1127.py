# -*- coding: utf-8 -*-
# 11/27(金)発売 J-POP・ロックのまとめ動画（14番の曲 OSHINAVI.wav 44.7秒・背景 96057・サイバーパンクの姐さん9人）
#   上＝見出し／まん中＝発売の行が下から上へ流れる字幕／下＝姐さん3人ずつ（3組を順に）が拍に合わせて跳ねる
#   python render1127.py board  … 絵コンテ（4コマ）board1127.png
#   python render1127.py full   … out.mp4（TikTok 用）と out_x.mp4（X 用・約8MB）
import io, json, math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
D = 'C:/Users/user/oshinavi/tmp/x1123/songs/'
BG = 'C:/Users/user/Downloads/背景動画/96057_640x360.mp4'
WAV = 'C:/Users/user/Downloads/OSHINAVI.wav'
W, H, FPS, DUR = 1080, 1920, 30, 44.72
T0, T1 = 2.3, 41.5           # 字幕が流れる間（前奏のあと〜終わりの3秒前＝最後は oshinavi.jp で止まって見せる）
FB = 'C:/Windows/Fonts/BIZ-UDGothicB.ttc'
FR = 'C:/Windows/Fonts/BIZ-UDGothicR.ttc'
f = lambda p, s: ImageFont.truetype(p, s)
rows = json.load(io.open(D + 'rows1127.json', encoding='utf-8'))
BPM = json.load(io.open(D + 'bpm.json', encoding='utf-8'))['bpm'] if len(sys.argv) > 2 else None

def tempo():
    try:
        import librosa
        y, sr = librosa.load(WAV, sr=22050, mono=True)
        t, beats = librosa.beat.beat_track(y=y, sr=sr)
        bt = librosa.frames_to_time(beats, sr=sr)
        return float(np.atleast_1d(t)[0]), [float(x) for x in bt]
    except Exception as ex:
        return 95.0, []
bpm, beats = tempo()
json.dump({'bpm': bpm, 'beats': beats[:200]}, io.open(D + 'bpm.json', 'w', encoding='utf-8'))
beats = np.array(beats) if beats else np.arange(0, DUR, 60 / bpm)

# ---- 見出し（固定） ----
def glow_text(img, xy, text, font, fill, glow, anchor='mm'):
    g = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).text(xy, text, font=font, fill=glow, anchor=anchor)
    g = g.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(g); img.alpha_composite(g)
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)
head = Image.new('RGBA', (W, H), (0, 0, 0, 0))
dh = ImageDraw.Draw(head)
dh.rounded_rectangle((40, 40, W - 40, 330), 36, fill=(8, 6, 30, 170), outline=(120, 220, 255, 200), width=4)
glow_text(head, (W // 2, 120), '11/27(金) 発売', f(FB, 92), (255, 255, 255, 255), (90, 200, 255, 255))
glow_text(head, (W // 2, 245), 'J-POP・ロック', f(FB, 104), (140, 240, 255, 255), (170, 90, 255, 255))
# 字幕の下敷き（まん中の箱）
TOP, BOT = 370, 1220
dh.rounded_rectangle((40, TOP - 10, W - 40, BOT + 10), 30, fill=(6, 4, 24, 150), outline=(170, 110, 255, 170), width=3)
dh.rectangle((0, H - 92, W, H), fill=(4, 2, 18, 190))
glow_text(head, (W // 2, H - 46), 'oshinavi.jp で発売時刻をチェック', f(FB, 46), (255, 255, 255, 255), (90, 200, 255, 255))

# ---- 流れる字幕（縦長の1枚） ----
RH = 132
PADT, ENDH = 60, 220          # 🆕11/23 すちこ「なにも文字がないことがないように・最後文字が残っててoshinavi.jpで終わり」
strip = Image.new('RGBA', (W - 120, PADT + RH * len(rows) + ENDH), (0, 0, 0, 0))
ds = ImageDraw.Draw(strip)
for i, r in enumerate(rows):
    y = PADT + i * RH
    ds.text((10, y + RH // 2), r['time'], font=f(FB, 60), fill=(110, 235, 255, 255), anchor='lm')
    nm = r['name']
    tail = '／' + r['pref'] + r['pre']
    for size in (66, 60, 54, 48, 42, 36):
        fn = f(FB, size)
        if ds.textlength(nm, font=fn) + ds.textlength(tail, font=f(FR, 40)) <= W - 120 - 210:
            break
    ds.text((200, y + RH // 2), nm, font=fn, fill=(255, 255, 255, 255), anchor='lm')
    ds.text((200 + ds.textlength(nm, font=fn) + 8, y + RH // 2 + 6), tail, font=f(FR, 40), fill=(205, 190, 255, 255), anchor='lm')
    ds.line((10, y + RH - 6, W - 130, y + RH - 6), fill=(120, 90, 220, 90), width=2)
# 最後の行＝oshinavi.jp（光る文字）
ey = PADT + RH * len(rows) + ENDH // 2
g = Image.new('RGBA', strip.size, (0, 0, 0, 0))
ImageDraw.Draw(g).text((strip.width // 2, ey), 'oshinavi.jp', font=f(FB, 104), fill=(90, 200, 255, 255), anchor='mm')
g = g.filter(ImageFilter.GaussianBlur(12))
strip.alpha_composite(g); strip.alpha_composite(g)
ImageDraw.Draw(strip).text((strip.width // 2, ey), 'oshinavi.jp', font=f(FB, 104), fill=(255, 255, 255, 255), anchor='mm')
SH = BOT - TOP
dist = max(0, strip.height - SH)   # 1行目が箱の上にいる所から、oshinavi.jp が箱の下に収まる所まで＝箱が空になる時が無い
fade = np.ones(SH, dtype=np.float32)
k = 50
fade[:k] = np.linspace(0, 1, k); fade[-k:] = np.linspace(1, 0, k)
FADE = Image.fromarray((np.tile(fade[:, None], (1, strip.width)) * 255).astype(np.uint8), 'L')

# ---- 姐さん ----
P = [Image.open(D + 'poses/p%d.png' % i).convert('RGBA') for i in range(1, 10)]
def fit(im, h):
    s = h / im.height
    return im.resize((max(1, int(im.width * s)), h), Image.LANCZOS)
P = [fit(p, 560) for p in P]
for i, p in enumerate(P):
    if p.width > 360:
        P[i] = p.resize((360, int(p.height * 360 / p.width)), Image.LANCZOS)
GROUPS = [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
SEG = (T1 - T0) / 3

def beat_phase(t):
    i = np.searchsorted(beats, t) - 1
    if i < 0 or i + 1 >= len(beats):
        per = 60 / bpm
        return (t % per) / per
    return (t - beats[i]) / max(beats[i + 1] - beats[i], 1e-3)

def frame(t):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    im.alpha_composite(head)
    # 字幕
    if True:
        x = min(1.0, max(0.0, (t - T0) / (T1 - T0)))
        off = int(x * dist)
        win = Image.new('RGBA', (strip.width, SH), (0, 0, 0, 0))
        win.alpha_composite(strip, (0, -off))
        a = np.asarray(win)[:, :, 3].astype(np.float32) * (np.asarray(FADE).astype(np.float32) / 255)
        win.putalpha(Image.fromarray(a.astype(np.uint8)))
        im.alpha_composite(win, (60, TOP))
    # 姐さん3人（組は時間で替わる・替わる時は0.3秒で下から出る）
    g = 0 if t < T0 + SEG else (1 if t < T0 + 2 * SEG else 2)
    gs = T0 + g * SEG if g else 0
    pop = min(1.0, (t - gs) / 0.3) if g else 1.0
    ph = beat_phase(t)
    for j, idx in enumerate(GROUPS[g]):
        p = P[idx]
        jump = int(abs(math.sin(math.pi * ((ph + j * 0.33) % 1))) * 26)
        cx = [190, 540, 890][j]
        y = 1810 - p.height - jump + int((1 - pop) * 300)
        im.alpha_composite(p, (cx - p.width // 2, y))
    return im

if sys.argv[1] == 'board':
    ts = [1.0, 12.0, 26.0, 40.0]
    bgf = []
    for t in ts:
        subprocess.run([FF, '-y', '-v', 'error', '-ss', str(t % 20), '-i', BG, '-frames:v', '1', '-vf', 'scale=-2:%d,crop=%d:%d' % (H, W, H), D + 'bgt.png'])
        b = Image.open(D + 'bgt.png').convert('RGBA'); b.alpha_composite(frame(t)); bgf.append(b.convert('RGB').resize((360, 640)))
    out = Image.new('RGB', (360 * 4 + 30, 640), (20, 20, 30))
    for i, b in enumerate(bgf):
        out.paste(b, (i * 370, 0))
    out.save(D + 'board1127.png')
    io.open(D + 'render1127.txt', 'w', encoding='utf-8').write('bpm %.1f 拍 %d 行 %d\n' % (bpm, len(beats), len(rows)))
else:
    cmd = [FF, '-y', '-v', 'error', '-stream_loop', '-1', '-i', BG,
           '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
           '-i', WAV,
           '-filter_complex', '[0:v]scale=-2:%d,crop=%d:%d,fps=%d,setsar=1[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v]' % (H, W, H, FPS),
           '-map', '[v]', '-map', '2:a', '-t', str(DUR), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-c:a', 'aac', '-b:a', '192k', '-shortest', D + 'out.mp4']
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(DUR * FPS) + 1
    for i in range(n):
        pr.stdin.write(frame(i / FPS).tobytes())
    pr.stdin.close(); pr.wait()
    subprocess.run([FF, '-y', '-v', 'error', '-i', D + 'out.mp4', '-c:v', 'libx264', '-b:v', '1250k', '-maxrate', '1400k', '-bufsize', '2800k', '-c:a', 'aac', '-b:a', '128k', D + 'out_x.mp4'])
    io.open(D + 'render1127.done', 'w').write('done')
