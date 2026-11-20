# -*- coding: utf-8 -*-
# 11/3：道具の数字を今回に合わせて直し、絵コンテ（board.png）と頭 0〜12 秒の試し動画（clip.mp4）を出す
#   衣装＝座り(a)と立ち(b)を交互に1着1回ずつ。タップ場面（サビ 82 秒〜）までを 11 着で等分（≒4小節ごと・小節の頭）・締めの oshinavi.jp は b5
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep7.txt', 'w', encoding='utf-8')


def sub(f, pairs):
    s = io.open(D + f, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (f, a)
        s = s.replace(a, b)
    io.open(D + f, 'w', encoding='utf-8').write(s)


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


s = io.open(D + 'badge_tap.py', encoding='utf-8').read()
s = re.sub(r"BOXES = \[\[.*?\]\]", "BOXES = [[78, 672, 1018, 908]]", s, count=1)   # 11/3 爆笑問題「2次受付（東京 R9年 2/10公演）11/3 19:00 明日発売」の箱（screen_badge.png を目で測った）
io.open(D + 'badge_tap.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'beat_char.py', encoding='utf-8').read()
s = s.replace("poses/p[1-9].png", "poses/[ab][1-9].png")
s = re.sub(r"TOP, BOT = \d+, \d+", "TOP, BOT = 110, 880", s)
io.open(D + 'beat_char.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'render.py', encoding='utf-8').read()
a = s.index("ORDER = [")
b = s.index("_url_bar = ")
new = """ORDER = ['a3', 'b4', 'a1', 'b8', 'a2', 'b6', 'a7', 'b2', 'a9', 'b1', 'a5', 'b5']   # 11/3 座りと立ちを交互・締めはピンクのパーカーにハートのサングラス b5
_B = json.load(io.open(D + 'beats.json'))['beats']
_shows = [c['show'] for c in S['chunks']]
_PH = min(range(4), key=lambda p: sum(min(abs(b - s) for b in _B[p::4]) for s in _shows))
_bars = _B[_PH::4]
_tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
_url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
_n = [i for i, x in enumerate(_bars) if x < _tap - 1]
_step = (len(_n)) / 11.0
_at = [0.0] + [_bars[int(round(_step * k))] for k in range(1, 11)]   # タップの場面までを 11 着で等分・小節の頭
S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[11]]]
"""
s = s[:a] + new + s[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(s)
# 絵コンテ：各衣装のまん中＋タップの場面＋締め 2 枚＝14 枚（5列×3段）
s = io.open(D + 'board.py', encoding='utf-8').read()
s = re.sub(r"TS = \[.*?\]", "TS = [4.0, 11.0, 18.0, 24.5, 31.0, 38.5, 44.0, 51.0, 56.5, 63.0, 70.0, 77.5, 88.0, 102.0]", s, count=1)
s = s.replace("out = Image.new('RGB', (cols * (W + 10), 2 * (H + 50)), (30, 30, 30))", "out = Image.new('RGB', (cols * (W + 10), 3 * (H + 50)), (30, 30, 30))")
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('make_spec.py')
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read() + '\n')
run('render.py', '--clip', '0,12')
out.close()
