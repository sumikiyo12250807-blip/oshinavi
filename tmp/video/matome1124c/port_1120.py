# -*- coding: utf-8 -*-
# 11/20 J-POP まとめ（1:48・TikTok 先出し）：ゴスロリの姐さん9人を cut17 の形で切る（w1〜w9・反転 m1〜m9）→ 見本 contact_cut.png
#   → テンポ → 文字起こし（lyrics_times2.txt）→ prep1120.txt（背景のコマは bg_prep.py で作り済み＝242696）
import io, os, subprocess, sys
V = 'C:/Users/user/oshinavi/tmp/video/'
D = V + 'matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1120.txt', 'w', encoding='utf-8')
def run(a):
    r = subprocess.run([sys.executable] + a, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env, cwd=D)
    out.write('== %s rc %s\n%s\n%s\n' % (' '.join(a)[-80:], r.returncode, r.stdout[-2500:], r.stderr[-1200:]))
    out.flush()
for f in os.listdir(D + 'poses'):
    os.remove(D + 'poses/' + f)
run([V + 'shuyaku1117/cut17.py', 'sheet.png', 'w', D])
if os.path.exists(D + 'cut17_w.txt'):
    out.write(io.open(D + 'cut17_w.txt', encoding='utf-8').read())
from PIL import Image, ImageOps
for k in range(1, 10):
    p = D + 'poses/w%d.png' % k
    if os.path.exists(p):
        ImageOps.mirror(Image.open(p)).save(D + 'poses/m%d.png' % k)
tiles = [Image.open(D + 'poses/w%d.png' % k).convert('RGBA') for k in range(1, 10) if os.path.exists(D + 'poses/w%d.png' % k)]
th = 360
row = Image.new('RGBA', (sum(int(t.width * th / t.height) + 20 for t in tiles) + 20, th + 40), (0, 150, 60, 255))
x = 20
for t in tiles:
    t2 = t.resize((int(t.width * th / t.height), th), Image.LANCZOS)
    row.alpha_composite(t2, (x, 20)); x += t2.width + 20
row.convert('RGB').save(D + 'contact_cut.png')
run([D + 'tempo_check.py'])
run([D + 'transcribe2.py'])
out.close()
open(D + 'prep1120.done', 'w').close()
