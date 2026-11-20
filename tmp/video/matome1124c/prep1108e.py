# -*- coding: utf-8 -*-
# 11/8 すちこの直し「おどってるみたいに頻繁に画像を変えて」→ 絵コンテ（秒は手で）→ 試し動画 20〜30 秒 → art/
import io, os, re, shutil, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1108e.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-1500:], r.stderr[-2000:]))
    out.flush()


run('render.py', '--frames', '0.5')
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
gaps = [round(P[i + 1][0] - P[i][0], 2) for i in range(len(P) - 2)]
out.write('替わる回数 %d 間隔 %.2f〜%.2f\n最初 %s\n' % (len(P), min(gaps), max(gaps), [[round(t, 2), p] for t, p in P[:20]]))
TS = [1.0, 3.6, 10.0, 16.4, 21.0, 21.5, 22.0, 22.5, 28.8, 36.0, 42.3, 48.6, 53.8, 60.2]
s = io.open(D + 'board.py', encoding='utf-8').read()
s, n = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, s, count=1)
assert n == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
run('render.py', '--clip', '19,30')
from PIL import Image
Image.open(D + 'board.png').convert('RGB').save(D + 'art/board.jpg', quality=82)
shutil.copyfile(D + 'clip.mp4', D + 'art/clip.mp4')
out.write('art %d %d\n' % (os.path.getsize(D + 'art/board.jpg') // 1024, os.path.getsize(D + 'art/clip.mp4') // 1024))
out.close()
open(D + 'prep1108e.done', 'w').close()
