# -*- coding: utf-8 -*-
# 11/7 お笑いまとめ：make_spec（歌詞の塊と時刻＝lyrics_times_head / lyrics_times2）・前奏の真ん中の字・render（並び・後奏）→ 絵コンテ → 試し動画
#   曲『おしなびどっと (17)』139.9 秒・138.3BPM（1小節 1.74 秒）・前奏 0〜13.4 秒・歌 〜123.4 秒・後奏 約16 秒
#   キャラ＝着物の歌姫シート1枚（k）。k5 は頭のてっぺんが k2 の足とくっついて欠けた＝使わない → 8着
#   タップの場面（105 秒）までが長い（1人 8 秒以内＝14 回要る）＝1巡目は k、2巡目は左右反転（n）で並びを変える・締めは初登場の k3（ウインクで指さし）
import io, os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
from PIL import Image, ImageOps
out = io.open(D + 'prep1107d.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


for k in (1, 2, 4, 6, 7, 8, 9):
    ImageOps.mirror(Image.open(D + 'poses/k%d.png' % k)).save(D + 'poses/n%d.png' % k)

CH = '''CHUNKS = [
    [('明日 11月7日の', [13.4, 14.5]), ('発売の お笑い', [18.7, 21.2]), ('言うわね', [23.8])],
    [('10時', [24.7]), ('ミキ 東京 ほか', [26.3, 28.2, 29.2])],
    [('ジョイマン 東京', [31.0, 32.3]), ('令和ロマンの', [32.8]), ('松井 東京', [36.6, 37.5])],
    [('金属バット', [41.6]), ('大阪 ほか', [43.9, 44.3]), ('レイザーラモン 兵庫', [45.1, 46.8])],
    [('トータルテンボス', [48.3]), ('神奈川', [50.5]), ('レインボー 大阪', [51.5, 53.6])],
    [('アインシュタイン', [57.0]), ('兵庫 ほか', [59.0, 59.7]), ('空気階段 東京', [60.8, 62.4])],
    [('バイク川崎バイク', [63.1]), ('兵庫 ほか', [65.8, 67.2])],
    [('ロングコートダディ', [70.9]), ('三重 ほか', [72.8, 73.4]), ('かが屋 東京 ほか', [74.7, 75.6, 76.2])],
    [('ニューヨーク', [78.2]), ('大阪 ほか', [80.0, 80.9])],
    [('11時', [85.8]), ('コットン 東京', [87.8, 88.7])],
    [('マシンガンズ 愛知', [91.7, 93.1]), ('忘れないでね', [93.8])],
    [('売り場まで', [98.7]), ('案内するのは', [101.3]), ('おしなび', [103.1])],
    [('笑いの チケット', [105.9, 106.9]), ('おしなびで', [107.7]), ('探してね', [109.2])],
    [('OSHINAVI+.jp', [112.1, 114.4]), ('なのよね', [115.3])],
    [('おし なび なのね', [119.0, 120.5, 121.6])],
]
LOW = {12}
DUR = 139.8'''
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
s, n = re.subn(r'CHUNKS = \[.*?\nDUR = 66\.2', lambda m: CH, s, flags=re.S)
assert n == 1
for a, b in (("CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']",
              "CHORUS_AT, URL_AT = chunks[12]['show'], chunks[13]['show']\n"
              "# 11/7 前奏（0〜13.4 秒）も真ん中を空けない＝「明日 11/7(土)／発売の お笑い」を白で出しておく（なぞらない）\n"
              "chunks.insert(0, {'show': 0.3, 'hide': chunks[0]['show'], 'lines': [[['明日', 999, True], ['11/7(土)', 999, False]], [['発売の', 999, True], ['お笑い', 999, False]]], 'low': False})"),
             ("'when': '明日 11/6(金) 発売'", "'when': '明日 11/7(土) 発売'"),
             ("'kind': 'お笑い・落語'", "'kind': 'お笑い'"),
             ("'name': '又吉直樹一人コントライブ「人間」'", "'name': 'ミキ 家でやりなはれ！inルミネtheよしもと'")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)

r = io.open(D + 'render.py', encoding='utf-8').read()
r, n = re.subn(r"ORDER = \['e1'[^\n]*\n",
               "ORDER = ['k1', 'k4', 'k7', 'k6', 'k2', 'k8', 'k9', 'n6', 'n1', 'n4', 'n8', 'n9', 'n7', 'n2', 'k3']   # 11/7 着物の歌姫8着（k5 は頭が欠けた）・1巡目 k／2巡目は左右反転 n で並びを変える・締めは初登場のウインクの子 k3\n", r)
assert n == 1
for a, b in (("_step = (len(_n)) / 8.0", "_step = (len(_n)) / 14.0"),
             ("for k in range(1, 8)]", "for k in range(1, 14)]"),
             ("+ [[_url, ORDER[8]]]", "+ [[_url, ORDER[14]]]"),
             ("'names': ORDER[:8],", "'names': ['k1', 'k4', 'k7', 'k6', 'k2', 'k8', 'k9'],"),
             ("_rows = [(135 + 270 * i, 1190, 250) for i in range(4)] + [(135 + 270 * i, 1470, 250) for i in range(4)]",
              "_rows = [(135 + 270 * i, 1190, 250) for i in range(4)] + [(270 + 270 * i, 1470, 250) for i in range(3)]")):
    assert a in r, a
    r = r.replace(a, b)
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

run('render.py', '--frames', '0.5')
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
out.write('poses %s\n' % [[round(t, 1), p] for t, p in P])
tap = next(sc[0] for sc in S['scenes'] if sc[1] == 'shot:badge')
ch = S['chunks']
TS = [6.0]
for i, (t0, name) in enumerate(P):
    t1 = P[i + 1][0] if i + 1 < len(P) else S['dur']
    if t0 < tap <= t1:
        t1 = tap
    m = (t0 + t1) / 2
    for c in ch:
        if abs(m - c['show']) < 0.4:
            m = c['show'] + 0.6
    TS.append(round(m, 1))
TS += [round(tap + 3.0, 1), 130.0, 137.0]
TS = sorted(set(TS))
out.write('TS %s\n' % TS)
s = io.open(D + 'board.py', encoding='utf-8').read()
s = re.sub(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, s, count=1)
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
out.write(io.open(D + 'board.txt', encoding='utf-8').read()[-800:] + '\n')
out.close()
open(D + 'prep1107d.done', 'w').close()
