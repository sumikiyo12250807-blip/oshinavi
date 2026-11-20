# -*- coding: utf-8 -*-
# 11/3 第2版の絵コンテ：長い塊を分けた spec で、衣装ごとに1枚（その衣装の区間で歌詞が出ているまん中）＋タップ場面＋締め → board.png、試し動画 0〜12 秒
import io, json, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep8.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


run('render.py', '--frames', '0.5')
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
ch = S['chunks']
TS = []
for i, (t0, name) in enumerate(P):
    t1 = P[i + 1][0] if i + 1 < len(P) else S['dur']
    if t0 < tap <= t1:
        t1 = tap
    m = (t0 + t1) / 2
    # 塊の入れ替え（±0.4秒）に当たらないようにずらす
    for c in ch:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
    out.write('%s %.2f〜%.2f → %.1f\n' % (name, t0, t1, TS[-1]))
TS.insert(-1, round(tap + 6.5, 1))     # タップの場面
TS = sorted(TS)
out.write('TS %s\n' % TS)
s = io.open(D + 'board.py', encoding='utf-8').read()
s = re.sub(r"TS = \[.*?\]", 'TS = %s' % TS, s, count=1)
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read()[-800:] + '\n')
run('render.py', '--clip', '0,12')
out.close()
