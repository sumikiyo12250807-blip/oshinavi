# -*- coding: utf-8 -*-
# 11/10：拍（tempo_check＝キック 133.2・全帯域 133.2・スネア 131.6 → 131〜134BPM をスネアで当てる）→ 反転の子 → make_spec → 絵コンテ → 試し動画（サビのタップ〜締め 47.5〜58.8 秒）
import io, os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1110b.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()
    return r.returncode


s = io.open(D + 'beats_snare.py', encoding='utf-8').read()
s = s.replace('END = 92.0', 'END = 58.0   # 11/10 お笑い：曲 58.8 秒・キック／全帯域 133.2 が上位   ').replace('np.arange(130.0, 132.01, 0.02)', 'np.arange(131.0, 134.01, 0.02)')
io.open(D + 'beats_snare.py', 'w', encoding='utf-8').write(s)
run('beats_snare.py')
out.write(io.open(D + 'beats_snare.txt', encoding='utf-8').read())
run('flip_poses.py')
if run('render.py', '--frames', '0.5') != 0:
    out.close(); sys.exit(1)
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
out.write('poses %s\nchunks %s\n' % ([[round(t, 2), p] for t, p in S['poses']], [(round(c['show'], 2), round(c['hide'], 2)) for c in S['chunks']]))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
TS = [1.0]
for i in range(8):
    m = (P[i][0] + (P[i + 1][0] if i + 1 < 8 else tap)) / 2
    for c in S['chunks']:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 3.0, 1), round(url + 1.0, 1), round(url + 2.2, 1), round(S['dur'] - 2.0, 1), round(S['dur'] - 0.3, 1)]
out.write('TS %s\n' % TS)
b = io.open(D + 'board.py', encoding='utf-8').read()
b, n = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, b, count=1)
assert n == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(b)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read())
run('render.py', '--clip', '47.5,58.8')
out.close()
open(D + 'prep1110b.done', 'w').close()
