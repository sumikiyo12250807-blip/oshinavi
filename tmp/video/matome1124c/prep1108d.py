# -*- coding: utf-8 -*-
# 11/8：衣装替えを「タップまで8等分」にした並びで 絵コンテ → 試し動画（6〜20 秒＝10時の名前・着替え2回）
#  止めた1本目の書き出し（render.py --clip）の子プロセスが残っていたら止める
import io, os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1108d.txt', 'w', encoding='utf-8')
try:
    import psutil
    for p in psutil.process_iter(['pid', 'cmdline']):
        c = ' '.join(p.info['cmdline'] or [])
        if 'matome1124c' in c and ('render' in c or 'shuyaku_video' in c) and p.pid != os.getpid():
            p.kill(); out.write('止めた %s %s\n' % (p.pid, c[:120]))
except Exception as e:
    out.write('psutil %s\n' % e)


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
    out.flush()


run('render.py', '--frames', '0.5')
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
ch = S['chunks']
TS = [1.0]
for i, (t0, name) in enumerate(P):
    t1 = P[i + 1][0] if i + 1 < len(P) else S['dur']
    if t0 < tap <= t1:
        t1 = tap
    m = (t0 + t1) / 2
    for c in ch:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 1.5, 1), 62.3]
TS = sorted(set(t for t in TS if t < S['dur']))
out.write('poses %s\nTS %s\n' % ([[round(t, 1), p] for t, p in P], TS))
s = io.open(D + 'board.py', encoding='utf-8').read()
s, n = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, s, count=1)
assert n == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
run('render.py', '--clip', '6,20')
out.close()
open(D + 'prep1108d.done', 'w').close()
