# -*- coding: utf-8 -*-
# prep1113b の続き（make_spec の折り返しを直したあと）：1コマ → 絵コンテ → 試し動画2本（名前の詰まった所・締め）
import io, os, re, shutil, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1113c.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-3000:], r.stderr[-3000:]))
    out.flush()
    return r.returncode


if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
out.write('poses %s\nchunks %s\n' % ([[round(t, 2), p] for t, p in S['poses']], [(round(c['show'], 2), round(c['hide'], 2)) for c in S['chunks']]))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
n = len(P) - 1
TS = [6.0]
for i in range(n):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < n else tap)) / 2
    for c in S['chunks']:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 3.0, 1), round(url + 1.0, 1), round(url + 6.0, 1), round(url + 10.0, 1), round(S['dur'] - 2.0, 1)]
out.write('TS %s\n' % TS)
bd = io.open(D + 'board.py', encoding='utf-8').read()
bd, k = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, bd, count=1)
assert k == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(bd)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '44.6,58.9')
shutil.copyfile(D + 'clip.mp4', D + 'clip_names.mp4')
run('render.py', '--clip', '86.5,101.0')
shutil.copyfile(D + 'clip.mp4', D + 'clip_end.mp4')
out.close()
open(D + 'prep1113c.done', 'w').close()
