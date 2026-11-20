# -*- coding: utf-8 -*-
# 11/8 お笑いまとめ：make_spec（歌詞の塊と時刻＝lyrics_times2）・前奏の真ん中の字・render（並び・後奏）→ 絵コンテ → 試し動画
#   曲『わらいのちけっとおしなび』62.9 秒・132.44BPM（1小節 1.81 秒）・前奏 0〜2.1 秒・歌 〜61.4 秒
#   キャラ＝祭りの子 9 ポーズ（k＝元の向き・n＝反転）。すちこ「9種類は全部右向きだから反転して左向きも」＝k と n を交互に・1ポーズ1回ずつ
#   すちこ「おじぎなし」＝頭も締めも拍に合わせて動かす。締めはいちばんかわいい1着＝提灯の子 k8
import io, os, re, subprocess, sys, json
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
out = io.open(D + 'prep1108c.txt', 'w', encoding='utf-8')


def run(f, *a):
    r = subprocess.run([sys.executable, D + f] + list(a), capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    out.write('== %s %s rc %s\n%s\n%s\n' % (f, a, r.returncode, r.stdout[-2500:], r.stderr[-2500:]))
    out.flush()


CH = '''CHUNKS = [
    [('明日 11月8日の', [2.1, 2.9]), ('発売の お笑い', [5.3, 6.5]), ('言うところよ', [7.7])],
    [('10時', [8.8]), ('南海キャンディーズ 石川', [9.5, 10.9]), ('見取り図 広島', [11.3, 11.8])],
    [('ヒコロヒー 東京', [12.9, 13.8]), ('月亭方正 大阪', [14.0, 14.9]), ('R藤本 埼玉', [15.9, 18.6])],
    [('NMB48 大阪', [19.7, 22.2]), ('バッテリィズ 千葉', [23.4, 24.6]), ('すゑひろがりず 埼玉', [25.2, 26.1])],
    [('中野なかるてぃん 千葉', [27.0, 28.4]), ('囲碁将棋 千葉 ほか', [28.8, 29.7, 30.0]), ('桂宮治 東京', [30.6, 32.1])],
    [('11時', [33.0]), ('ロングコートダディ', [34.4]), ('岩手 ほか', [36.4, 37.5])],
    [('ドンデコルテ 東京', [38.1, 39.5]), ('9番街レトロ', [40.4]), ('なかむらしゅん 東京', [42.1, 43.2])],
    [('19時', [43.9]), ('ラランド 東京', [44.9, 45.4]), ('ほかにも まだまだ あるのよ', [45.9, 46.4, 46.8])],
    [('売り場まで', [47.4]), ('案内するのは', [48.9]), ('おしなび', [51.3])],
    [('笑いの チケット', [54.0, 54.9]), ('おしなびで', [55.8]), ('探してね', [56.7])],
    [('OSHINAVI+.jp', [57.8, 59.5]), ('なんだわ', [60.4])],
]
LOW = {9}
DUR = 62.8'''
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
s, n = re.subn(r'CHUNKS = \[.*?\nDUR = 139\.8', lambda m: CH, s, flags=re.S)
assert n == 1
for a, b in (("CHORUS_AT, URL_AT = chunks[12]['show'], chunks[13]['show']", "CHORUS_AT, URL_AT = chunks[9]['show'], chunks[10]['show']"),
             ("['11/7(土)', 999, False]", "['11/8(日)', 999, False]"),
             ("# 11/7 前奏（0〜13.4 秒）", "# 11/8 前奏（0〜2.1 秒）"),
             ("'when': '明日 11/7(土) 発売'", "'when': '明日 11/8(日) 発売'"),
             ("'name': 'ミキ 家でやりなはれ！inルミネtheよしもと'", "'name': '南海キャンディーズ寄席～笑おう！みんなで！～'")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)

r = io.open(D + 'render.py', encoding='utf-8').read()
r, n = re.subn(r"ORDER = \['k4'[^\n]*\n",
               "ORDER = ['k2', 'n5', 'k6', 'n1', 'k4', 'n7', 'k9', 'n3', 'k8']   # 11/8 祭りの子：元の向き k と反転 n を交互に・1ポーズ1回ずつ（k1 と k3 は似た踊り＝離す）・締めは提灯の子 k8\n", r)
assert n == 1
for a, b in (("_step = (len(_n)) / 14.0", "_step = (len(_n)) / 8.0"),
             ("for k in range(1, 14)]", "for k in range(1, 8)]"),
             ("+ [[_url, ORDER[14]]]", "+ [[_url, ORDER[8]]]"),
             ("'names': ['k4', 'k1', 'k7', 'k6', 'k2', 'k8', 'k9', 'k3'],", "'names': ['n2', 'k1', 'n9', 'k7'],"),
             ("_rows = [(135 + 270 * i, 1190, 250) for i in range(4)] + [(135 + 270 * i, 1470, 250) for i in range(4)]",
              "_rows = [(135 + 270 * i, 1470, 250) for i in range(4)]")):
    assert a in r, a
    r = r.replace(a, b)
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

run('render.py', '--frames', '0.5')
S = json.load(io.open(D + 'stage_1118_v.json', encoding='utf-8'))
P = S['poses']
out.write('poses %s\n' % [[round(t, 1), p] for t, p in P])
out.write('chunks %s\n' % [(round(c['show'], 1), round(c['hide'], 1)) for c in S['chunks']])
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
out.write('TS %s\n' % TS)
s = io.open(D + 'board.py', encoding='utf-8').read()
s, n = re.subn(r"TS = \[38\.0\] if '--one' in sys\.argv else \[.*?\]", "TS = [38.0] if '--one' in sys.argv else %s" % TS, s, count=1)
assert n == 1
io.open(D + 'board.py', 'w', encoding='utf-8').write(s)
run('board.py')
run('render.py', '--clip', '6,20')
out.close()
open(D + 'prep1108c.done', 'w').close()
