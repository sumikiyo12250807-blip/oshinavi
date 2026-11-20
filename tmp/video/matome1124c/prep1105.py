# -*- coding: utf-8 -*-
# 11/5 お笑いまとめ：make_spec（歌詞の塊と時刻＝lyrics_times_head / lyrics_times2）・render（9着の並び）・badge_tap（ミキの箱）を今日の曲に → make_spec を回す
import io, os, re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
os.chdir('C:/Users/user/oshinavi')
D = 'tmp/video/matome1124c/'
env = dict(os.environ, PYTHONIOENCODING='utf-8')
CH = '''CHUNKS = [
    [('明日 11月5日の', [1.9, 2.5]), ('発売の お笑い', [5.8, 6.6]), ('言うわね', [7.5])],
    [('10時', [10.9]), ('ミキ 東京 ほか', [11.7, 13.4, 14.4])],
    [('金属バット 大阪 ほか', [14.7, 16.1, 16.9]), ('パンサー 東京', [17.5, 18.6])],
    [('もう中学生 東京', [19.1, 20.1]), ('空気階段 東京 ほか', [20.9, 22.1, 23.3])],
    [('バイク川崎バイク 東京 ほか', [23.8, 25.7, 26.6]), ('ロングコートダディ 東京 ほか', [27.1, 29.2, 29.8])],
    [('トロサーモン 東京', [30.2, 31.6]), ('しずる 千葉 ほか', [32.3, 32.9, 33.3])],
    [('たくろう 東京 ほか', [33.7, 34.8, 36.4]), ('銀シャリ 東京', [37.0, 38.3])],
    [('コロコロチキチキペッパーズ', [40.5]), ('東京 ほか', [42.3, 43.0])],
    [('エバース 東京 ほか', [43.4, 44.9, 46.2]), ('男性ブランコ 東京 ほか', [46.6, 48.3, 49.5])],
    [('ヨネダ2000 東京 ほか', [50.2, 51.4, 52.7])],
    [('忘れないでね', [53.0]), ('ほかにも まだ あるわ', [54.8, 56.0, 56.5])],
    [('売り場まで', [58.4]), ('案内するのは おしなび', [59.8, 61.4])],
    [('笑いたい 日は', [65.9, 67.0]), ('おしなびで 探してね', [67.9, 69.3])],
    [('OSHINAVI+.jp だわ', [72.5, 73.9, 75.8])],
]
LOW = {12}
DUR = 93.5'''
s = io.open(D + 'make_spec.py', encoding='utf-8').read()
s = re.sub(r'CHUNKS = \[.*?\nDUR = 65\.5', lambda m: CH, s, flags=re.S)
for a, b in (("CHORUS_AT, URL_AT = chunks[10]['show'], chunks[11]['show']", "CHORUS_AT, URL_AT = chunks[12]['show'], chunks[13]['show']"),
             ("'when': '明日 11/4(水) 発売'", "'when': '明日 11/5(木) 発売'"),
             ("'name': '金属・黒帯のダルガラミ'", "'name': 'ルミネtheよしもと プレミアム'")):
    assert a in s, a
    s = s.replace(a, b)
assert 'DUR = 93.5' in s
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(s)

r = io.open(D + 'render.py', encoding='utf-8').read()
a = "ORDER = ['a1', 'a2', 'a6', 'a8', 'a4', 'a9', 'a7', 'a3', 'a5']"
assert a in r
r = r.replace(a, "ORDER = ['a1', 'a3', 'a6', 'a2', 'a7', 'a4', 'a8', 'a9', 'a5']   # 11/5 レインボー原宿9着・1回ずつ・締めはうさぎを抱いた子 a5")
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

b = io.open(D + 'badge_tap.py', encoding='utf-8').read()
b = re.sub(r'BOXES = \[\[.*', 'BOXES = [[78, 666, 1018, 899]]   # 11/5：40391 ミキ（ルミネ）「一般発売（東京 R9年 1/10 11:00公演）11/5 10:00 明日発売」の箱（目で測った）', b)
io.open(D + 'badge_tap.py', 'w', encoding='utf-8').write(b)
o = subprocess.run([sys.executable, D + 'make_spec.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
print(o.returncode, o.stdout[-2000:], o.stderr[-2000:])
