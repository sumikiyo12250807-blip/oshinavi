# -*- coding: utf-8 -*-
# 11/6 お笑いまとめ：make_spec（歌詞の塊と時刻＝lyrics_times_head / lyrics_times2）・render（9着の並び・後奏）・badge_tap（又吉直樹の箱）を今日の曲に → make_spec を回す
#   曲『おしなびどっと (15)』66.3 秒・100BPM（1小節 2.4 秒）・歌は 1.0 秒から（前奏なし）〜56.5 秒・後奏 約10 秒
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
CH = '''CHUNKS = [
    [('明日 11月6日の', [1.0, 1.7]), ('発売の お笑い', [3.9, 4.5]), ('言うわよ', [5.0])],
    [('10時', [5.6]), ('ピース 又吉直樹 東京', [6.4, 7.9, 9.5])],
    [('レイザーラモン 東京', [11.0, 12.0]), ('たくろう 東京 ほか', [12.8, 13.4, 14.1])],
    [('ニッポンの社長 東京', [14.4, 15.9]), ('エバース 東京', [16.8, 17.5])],
    [('ヨネダ2000 千葉', [19.3, 20.3]), ('シモリュウ 千葉', [20.7, 21.5]), ('ドンデコルテ 千葉', [21.9, 22.9])],
    [('ダブルヒガシ 千葉', [23.2, 24.1]), ('めぞん 千葉', [24.6, 25.1]), ('春風亭一之輔 静岡', [25.6, 27.4])],
    [('11時', [28.8]), ('コットン 東京', [30.1, 30.8])],
    [('コロコロチキチキ', [31.5]), ('ペッパーズ 東京', [32.6, 33.7]), ('さや香 東京', [34.3, 34.8])],
    [('バッテリィズ 東京', [35.9, 36.7]), ('ほかにも まだまだ あるのよ', [37.5, 38.1, 38.6])],
    [('売り場まで', [39.3]), ('案内するのは おしなび', [40.4, 42.1])],
    [('笑いに 行くなら', [43.7, 44.5]), ('おしなびで 見つけてね', [45.2, 46.4])],
    [('X+フォローも よろしくね', [49.4, 50.1, 50.7])],
    [('OSHINAVI+.jp なのよ', [53.1, 54.5, 56.1])],
]
LOW = {10, 11}
DUR = 66.2'''
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
s = re.sub(r'CHUNKS = \[.*?\nDUR = 93\.5', lambda m: CH, s, flags=re.S)
for a, b in (("CHORUS_AT, URL_AT = chunks[12]['show'], chunks[13]['show']", "CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']"),
             ("'when': '明日 11/5(木) 発売'", "'when': '明日 11/6(金) 発売'"),
             ("'name': 'ルミネtheよしもと プレミアム'", "'name': '又吉直樹一人コントライブ「人間」'")):
    assert a in s, a
    s = s.replace(a, b)
assert 'DUR = 66.2' in s
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)

r = io.open(D + 'render.py', encoding='utf-8').read()
a = "ORDER = ['a1', 'a3', 'a6', 'a2', 'a7', 'a4', 'a8', 'a9', 'a5']"
assert a in r
r = r.replace(a, "ORDER = ['e1', 'e4', 'e2', 'e6', 'e5', 'e3', 'e7', 'e9', 'e8']   # 11/6 バレエコア9着・立つ/座る/歩く/しゃがむ/跳ぶを交互・1回ずつ・締めはハートの子 e8")
a = "'names': ORDER[:8], 'slots': _rows}"
assert a in r
r = r.replace(a, "'names': ORDER[:8], 'slots': _rows, 'step': S['beat']}")   # 11/6 後奏は約8秒＝1拍に1人ずつ落とす
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

b = io.open(D + 'badge_tap.py', encoding='utf-8').read()
b = re.sub(r'BOXES = \[\[.*', 'BOXES = [[78, 617, 1036, 852]]   # 11/6：41806 又吉直樹一人コントライブ「人間」「一般発売（東京 12/12公演）11/6 10:00 明日発売」の箱（shoot_badge が測った）', b)
io.open(D + 'badge_tap.py', 'w', encoding='utf-8').write(b)
o = subprocess.run([sys.executable, D + 'make_spec.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(o.returncode, o.stdout[-2000:], o.stderr[-2000:])
