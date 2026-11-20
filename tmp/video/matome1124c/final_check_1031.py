# -*- coding: utf-8 -*-
# 全編 out_x.mp4 の点検（check_full の形＋拍・衣装・歌詞の塊の時刻）→ final_check.txt・final_check.png
#   ①長さ・形式・大きさ・音（1秒ごと）②衣装の切り替え時刻が拍（小節の頭）に乗っているか・9着1回ずつ・最後が p6
#   ③歌詞の塊の出る時刻と拍のずれ ④衣装が替わる前後（-0.2秒/+0.2秒）のコマ・タップ場面・締めのコマ
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
ff = imageio_ffmpeg.get_ffmpeg_exe()
V = D + 'out_x.mp4'
info = subprocess.run([ff, '-i', V], capture_output=True, text=True, encoding='utf-8', errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', info)
dur = int(m.group(2)) * 60 + float(m.group(3))
raw = subprocess.run([ff, '-v', 'error', '-i', V, '-vn', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
a = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
rms = [float(np.sqrt(np.mean(a[i:i + 8000] ** 2))) for i in range(0, len(a), 8000)]
L = ['out_x.mp4 長さ %.2f秒 %.2fMB 1080x1920 %s h264 %s aac %s' % (dur, os.path.getsize(V) / 1048576, '1080x1920' in info, 'h264' in info, 'aac' in info),
     'out.mp4 %.2fMB' % (os.path.getsize(D + 'out.mp4') / 1048576),
     '音（1秒ごと） ' + ' '.join('%.2f' % r for r in rms),
     '音が途切れた秒（0.01未満・最後の3秒を除く） %s' % [i for i, r in enumerate(rms[:-3]) if r < 0.01]]
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
B = json.load(io.open(D + 'beats.json'))['beats']
near = lambda t: min(abs(b - t) for b in B)
P = S['poses']
L.append('衣装 ' + ' '.join('%.3f:%s(拍とのずれ %.0fms)' % (t, p, near(t) * 1000) for t, p in P if t > 0))
names = [p for _, p in P]
L.append('9着1回ずつ %s・最後 %s' % (sorted(names) == ['p%d' % i for i in range(1, 10)], names[-1]))
L.append('歌詞の塊 ' + ' '.join('%.2f(%.0fms)' % (c['show'], near(c['show']) * 1000) for c in S['chunks']))
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
L.append('タップ場面 %.2f〜%.2f 箱 %s' % (tap, url, json.load(io.open(D + 'cards/screen_badge.json'))['boxes']))
TS = []
for t, p in P[1:]:
    TS += [(t - 0.2, '前'), (t + 0.2, p)]
TS += [(tap + 3.0, 'タップ'), (url + 1.0, 'URL'), (dur - 1.5, '締め')]
os.makedirs(D + 'frames', exist_ok=True)
fnt = ImageFont.truetype(r'C:\Windows\Fonts\YuGothB.ttc', 20)
cw, ch, cols = 180, 320, 10
rows = (len(TS) + cols - 1) // cols
out = Image.new('RGB', (cols * (cw + 6) + 6, rows * (ch + 30) + 6), (20, 20, 24))
dr = ImageDraw.Draw(out)
for j, (t, lab) in enumerate(TS):
    p = D + 'frames/g_%06.2f.png' % t
    subprocess.run([ff, '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', V, '-frames:v', '1', p], check=True)
    x, y = 6 + (j % cols) * (cw + 6), 6 + (j // cols) * (ch + 30)
    out.paste(Image.open(p).convert('RGB').resize((cw, ch)), (x, y))
    dr.text((x + 4, y + ch + 4), '%.2f %s' % (t, lab), font=fnt, fill=(255, 255, 255))
out.save(D + 'final_check.png')
io.open(D + 'final_check.txt', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print('\n'.join(L))
