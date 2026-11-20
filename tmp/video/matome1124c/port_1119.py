# -*- coding: utf-8 -*-
# 11/19 クラシックまとめ（1:36・TikTok 先出し）：tiktok1118 の道具を写す（素材は触らない）→ 絵を cut17 の形で切る（w1〜w9・反転 m1〜m9）
#   → 背景のコマ（49445 明るい＝暗くしない・ぼかさない）→ テンポ → 文字起こし（lyrics_times2.txt）→ prep1119.txt
import glob, io, os, shutil, subprocess, sys
V = 'C:/Users/user/oshinavi/tmp/video/'
S, D = V + 'tiktok1118/', V + 'matome1124c/'
for sub in ('poses', 'cards', 'frames', 'bgf'):
    os.makedirs(D + sub, exist_ok=True)
n = 0
for p in glob.glob(S + '*.py'):
    b = os.path.basename(p)
    if os.path.exists(D + b):
        continue
    io.open(D + b, 'w', encoding='utf-8').write(io.open(p, encoding='utf-8').read().replace('tiktok1118', 'matome1124c'))
    n += 1
shutil.copyfile(D + 'bg.mp4', D + 'bg_src.mp4')
io.open(D + 'uslt.txt', 'w', encoding='utf-8').write(io.open(D + 'lyrics_tag.txt', encoding='utf-8').read().split('== USLT', 1)[1].strip() + '\n')
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1119.txt', 'w', encoding='utf-8')
out.write('tools %d\n' % n)
def run(a):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, cwd=D)
    out.write('== %s rc %s\n%s\n%s\n' % (' '.join(a)[-80:], r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
    out.flush()
for f in os.listdir(D + 'poses'):
    os.remove(D + 'poses/' + f)
run([V + 'shuyaku1117/cut17.py', 'sheet.png', 'w', D])
out.write(io.open(D + 'cut17_w.txt', encoding='utf-8').read())
from PIL import Image, ImageOps
for k in range(1, 10):
    p = D + 'poses/w%d.png' % k
    if os.path.exists(p):
        ImageOps.mirror(Image.open(p)).save(D + 'poses/m%d.png' % k)
# 見本：緑の地に9人（頭から靴まで切れているか目で見る）
tiles = [Image.open(D + 'poses/w%d.png' % k).convert('RGBA') for k in range(1, 10) if os.path.exists(D + 'poses/w%d.png' % k)]
th = 360
row = Image.new('RGBA', (sum(int(t.width * th / t.height) + 20 for t in tiles) + 20, th + 40), (0, 150, 60, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * th / t.height), th), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_cut.png')
# 背景のコマ（明るいまま）
b = io.open(D + 'bg_prep.py', encoding='utf-8').read()
run([D + 'bg_prep.py'])
run([D + 'tempo_check.py'])
run([D + 'transcribe2.py'])
out.close()
open(D + 'prep1119.done', 'w').close()
