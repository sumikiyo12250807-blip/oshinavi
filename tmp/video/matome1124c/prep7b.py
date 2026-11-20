# -*- coding: utf-8 -*-
# 11/4：make_spec（歌詞の塊と時刻）・render（9着の並び）・badge_tap（箱）を今日の曲に書き換え → 絵コンテ
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')

CH = '''CHUNKS = [
    [('明日 11月4日の', [1.1, 1.9]), ('発売の お笑い', [3.3, 4.0]), ('言うところよ', [4.6])],
    [('9時', [5.4]), ('松浦航大と よよよちゃん 愛知', [5.8, 7.5, 8.8])],
    [('10時', [9.2]), ('金属バットと 黒帯 大阪', [9.9, 11.1, 11.8]), ('ザ・プラン9の のら 東京 ほか', [12.3, 13.3, 13.6, 14.2])],
    [('ジャングルポケットと パンサー 東京', [14.5, 15.7, 16.3]), ('立川志らくと 松元ヒロ 東京', [16.9, 17.9, 18.6])],
    [('しずる 千葉', [19.2, 20.1]), ('NMB48 大阪', [20.7, 22.7]), ('囲碁将棋 千葉', [23.3, 24.2])],
    [('ダブルヒガシ 東京', [25.2, 26.7]), ('フースーヤ 谷口 大阪', [28.2, 29.2, 29.9])],
    [('ダイタクと ヘンダーソン 千葉', [30.4, 31.0, 32.1]), ('野沢輸出 大阪', [32.4, 33.7])],
    [('GAGと うるとらブギーズ 千葉', [34.6, 35.3, 36.7]), ('Dr.ハインリッヒ 大阪', [37.1, 38.2])],
    [('まだまだ ほかにも あるのよ', [39.2, 39.9, 40.5]), ('のぞいてみてね', [41.1])],
    [('売り場まで', [42.1]), ('案内するのは おしなび', [43.2, 44.4])],
    [('明日の 笑いは', [45.7, 47.4]), ('おしなびで 見つけてね', [48.2, 49.7])],
    [('OSHINAVI+.jp なのよ', [50.9, 52.8, 54.1])],
]
LOW = {10}
DUR = 65.5'''
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
s = re.sub(r'CHUNKS = \[.*?\nDUR = 111\.5', lambda m: CH, s, flags=re.S)
for a, b in (("CHORUS_AT, URL_AT = chunks[12]['show'], chunks[14]['show']", "CHORUS_AT, URL_AT = chunks[10]['show'], chunks[11]['show']"),
             ("'when': '明日 11/3(火) 発売'", "'when': '明日 11/4(水) 発売'"),
             ("'name': '爆笑問題カーボーイ30周年ライブ'", "'name': '金属・黒帯のダルガラミ'")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)

r = io.open(D + 'render.py', encoding='utf-8').read()
for a, b in (("ORDER = ['a3', 'b4', 'a1', 'b8', 'a2', 'b6', 'a7', 'b2', 'a9', 'b1', 'a5', 'b5']", "ORDER = ['a1', 'a2', 'a6', 'a8', 'a4', 'a9', 'a7', 'a3', 'a5']   # 11/4 冬の9着・1回ずつ・締めはうさぎを抱いたピンクの子 a5"),
             ('_step = (len(_n)) / 11.0', '_step = (len(_n)) / 8.0'),
             ('for k in range(1, 11)]', 'for k in range(1, 8)]'),
             ('[[_url, ORDER[11]]]', '[[_url, ORDER[8]]]')):
    assert a in r, a
    r = r.replace(a, b)
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

b = io.open(D + 'badge_tap.py', encoding='utf-8').read()
b = re.sub(r'BOXES = \[\[.*', 'BOXES = [[78, 627, 1018, 858]]   # 11/4：42825 金属・黒帯のダルガラミの「一般発売（大阪 12/19公演）11/4 10:00 明日発売」の箱（目で測った）', b)
io.open(D + 'badge_tap.py', 'w', encoding='utf-8').write(b)

o = subprocess.run([sys.executable, D + 'make_spec.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(o.returncode, o.stdout[-2000:], o.stderr[-2000:])
