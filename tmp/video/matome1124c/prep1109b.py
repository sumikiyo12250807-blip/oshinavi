# -*- coding: utf-8 -*-
# 11/9：拍（スネア 130〜132BPM・tempo_check の1位 131.0）→ make_spec → 絵コンテ → 試し動画（後奏の締め 79.5〜90.5 秒）
import io, os, re, shutil, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1109b.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()
    return r.returncode


s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
s = s.replace('END = 62.5', 'END = 92.0').replace('np.arange(131.4, 133.41, 0.02)', 'np.arange(130.0, 132.01, 0.02)')
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
s = s.replace("poses/[kn][1-9].png'))", "poses/[rn][1-9].png'))   # 11/9 雨の子 r（シートの向き）・n（反転）")
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
run('beats_snare.py')
out.write(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
out.write('poses %s\nchunks %s\n' % ([[round(t, 2), p] for t, p in S['poses']], [(round(c['show'], 2), round(c['hide'], 2)) for c in S['chunks']]))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
TS = [1.0]
for i in range(8):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < 8 else tap)) / 2
    for c in S['chunks']:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 3.0, 1), 73.5, 80.5, 85.0, round(S['dur'] - 2.0, 1)]
out.write('TS %s\n' % TS)
b = io.open(D + 'board.py', encoding='utf-8').read()
b, n = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, b, count=1)
assert n == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(b)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '79.5,90.5')
out.close()
open(D + 'prep1109b.done', 'w').close()
