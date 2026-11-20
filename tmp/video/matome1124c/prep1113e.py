# -*- coding: utf-8 -*-
# 11/13 作り直し：歩く子（cw1〜9 → w1〜9・反転 m1〜9）を主役に・walk_char で歩いて入れ替わる → 絵コンテ → 試し動画
#   並び＝右向き8着を1回ずつ（似たトレンチ w3 と w9 は離す）→ 左向き（反転）で3着もう一度 → 締めはいちばん見栄えのいい w5（I♥NY の袋で両手を広げる子）
#   後奏で下りてくる4人＝1枚目の座っている子（n2・n6・n5・r9）のまま
import io, os, re, shutil, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1113e.txt', 'w', encoding='utf-8')
from PIL import Image, ImageOps
for k in range(1, 10):
    im = Image.open(D + 'poses/cw%d.png' % k)
    im.save(D + 'poses/w%d.png' % k)
    ImageOps.mirror(im).save(D + 'poses/m%d.png' % k)
rd = io.open(D + 'render.py', encoding='utf-8').read()
rd = re.sub(r"ORDER = \['r1', 'r2'.*?\]\n", """# 11/13 第2版（すちこ「立ってる画像をメインに・颯爽と歩くところを続けて」）＝歩く子 w（右向き）／m（反転＝左向き）
#   w1 キャップ／w2 赤い髪の毛皮コート／w3 青い髪のトレンチ／w4 紫の髪の革ジャン／w5 ピンクの髪の I♥NY 袋（締め）／w6 緑の髪のデニムとコーヒー
#   ／w7 NYC ニット帽／w8 ピンクの髪のスーツケース／w9 黒い帽子のトレンチ
ORDER = ['w1', 'w2', 'w8', 'w3', 'w7', 'w4', 'w9', 'w6', 'm2', 'm7', 'm4', 'w5']
""", rd, count=1, flags=re.S)
assert "ORDER = ['w1'" in rd
if 'import walk_char' not in rd:
    rd = rd.replace("import beat_char  # noqa: F401\n", "import beat_char  # noqa: F401\nimport walk_char\nwalk_char.install(S)\n", 1)
assert 'walk_char.install(S)' in rd
io.open(D + 'render.py', 'w', encoding='utf-8').write(rd)


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    out.flush()
    return r.returncode


if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
n = len(P) - 1
TS = [0.7, 4.0]
for i in range(n):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < n else tap)) / 2
    TS.append(round(m, 1))
TS += [round(P[3][0] - 0.3, 1), round(P[3][0] + 0.4, 1), round(P[8][0] + 0.3, 1), round(P[8][0] + 0.9, 1),
       round(tap + 3.0, 1), round(url + 0.8, 1), round(url + 6.0, 1), round(S['dur'] - 2.0, 1)]
TS = sorted(set(TS))
out.write('poses %s\nTS %s\n' % ([[round(t, 2), p] for t, p in P], TS))
bd = io.open(D + 'board.py', encoding='utf-8').read()
bd, k = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, bd, count=1)
assert k == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(bd)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
a = P[3][0] - 6.0
run('render.py', '--clip', '%.2f,%.2f' % (a, a + 14.0))
shutil.copyfile(D + 'clip.mp4', D + 'clip_walk.mp4')
out.write('clip_walk %.2f〜%.2f\n' % (a, a + 14.0))
run('render.py', '--clip', '86.5,101.0')
shutil.copyfile(D + 'clip.mp4', D + 'clip_end.mp4')
out.close()
open(D + 'prep1113e.done', 'w').close()
