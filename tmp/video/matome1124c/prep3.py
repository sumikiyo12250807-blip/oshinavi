# -*- coding: utf-8 -*-
# 11/2 お笑い動画：道具の数字を今回の曲・絵に合わせて直し、拍→タップ画面→絵コンテ→試し動画まで回す
import io, os, re, subprocess, sys
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep3.txt', 'w', encoding='utf-8')


def sub(f, pairs):
    s = io.open(D + f, encoding='utf-8').read()
    for a, b in pairs:
        assert a in s, (f, a)
        s = s.replace(a, b)
    io.open(D + f, 'w', encoding='utf-8').write(s)


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s rc %s\n%s\n%s\n' % (f, r.returncode, r.stdout[-1200:], r.stderr[-1500:]))
    out.flush()


t = open(D + 'lyrics_tag.txt', 'rb').read().decode('utf-8', 'replace').replace('\x00', '')
io.open(D + 'uslt.txt', 'w', encoding='utf-8').write(t)
s = io.open(D + 'bg_prep.py', encoding='utf-8').read()
s = re.sub(r"vf = '.*?'", "vf = 'scale=-2:1920:flags=lanczos,crop=1080:1920,gblur=sigma=2.5,eq=brightness=-0.20:saturation=0.85'", s)
io.open(D + 'bg_prep.py', 'w', encoding='utf-8').write(s)
run('bg_prep.py')
sub('beats_snare.py', [('END = 86.5', 'END = 67.0'), ('np.arange(124.0, 125.61, 0.02)', 'np.arange(122.0, 126.01, 0.02)')])
sub('beats_kick.py', [('END, W = 86.5, 4.0', 'END, W = 67.0, 4.0')])
if os.path.exists(D + 'beats_snare.json'):
    os.remove(D + 'beats_snare.json')
run('beats_snare.py')
run('beats_kick.py')
sub('shoot_badge.py', [("CID, Q, MD = 31804, 'さらば青春の光', '10/31'", "CID, Q, MD = 40935, '囲碁将棋', '11/2'"), ('new D(2026,9,30,20,0)', 'new D(2026,10,1,20,0)')])
run('shoot_badge.py')
sub('beat_char.py', [('TOP, BOT = 245, 845', 'TOP, BOT = 90, 880')])
sub('dj_text.py', [('Y_WHEN, Y_KIND = 1530, 1660', 'Y_WHEN, Y_KIND = 1560, 1700'), ('Y_URL, Y_TAG = 1540, 1665', 'Y_URL, Y_TAG = 1560, 1700')])
s = io.open(D + 'render.py', encoding='utf-8').read()
a = s.index("ORDER = [")
b = s.index("_url_bar = ")
new = """ORDER = ['p1', 'p6', 'p7', 'p4', 'p8', 'p2', 'p5', 'p9', 'p3']   # 11/2 ディスコ：締めは白いスーツで指を立てる p3
_B = json.load(io.open(D + 'beats.json'))['beats']
_shows = [c['show'] for c in S['chunks']]
_PH = min(range(4), key=lambda p: sum(min(abs(b - s) for b in _B[p::4]) for s in _shows))
_bars = _B[_PH::4]
_tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
_url = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:dj_url')
_n = [i for i, x in enumerate(_bars) if x < _tap - 1]
_step = (len(_n)) / 8.0
_at = [0.0] + [_bars[int(round(_step * k))] for k in range(1, 8)]   # タップの場面までを8着で等分・小節の頭
S['poses'] = [[t, ORDER[i]] for i, t in enumerate(_at)] + [[_url, ORDER[8]]]
"""
s = s[:a] + new + s[b:]
s = s.replace("D + 'stage_1118_v.json'", "D + 'stage_1118_v.json'")
io.open(D + 'render.py', 'w', encoding='utf-8').write(s)
s = io.open(D + 'board.py', encoding='utf-8').read()
s = re.sub(r"TS = \[.*?\]", "TS = [3.0, 9.0, 16.0, 24.0, 30.0, 36.0, 44.0, 49.0, 56.0, 65.0]", s, count=1)
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
run('render.py', '--clip', '7,23')
out.close()
open(D + 'prep3.done', 'w').close()
