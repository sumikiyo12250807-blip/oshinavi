# -*- coding: utf-8 -*-
# 11/23 J-POP とロック（1:32・TikTok 先出し）：matome1121r から写した make_spec・render・beats・shoot_badge を 11/23 用に差し替える
#   すちこ「ビジュアル系姐さんでお願い」＝ビジュアル系の姐さん9人（右向き＝s／反転 t）。背景 34210（すちこが渡した）
#   時刻＝lyrics_times2.txt（言葉の頭）。名前は登録の表記：南佳孝 id11080／電脳ヒメカ id38578／Furui Riho id45978／め組 id29848
#     ／猪狩翔一「また、ここで。」id49314／NETH PRIERE CAIN id36186／人格ラヂオ id50809／Solid Statement Soul id51468・51470・51472
import io, re, shutil, subprocess
import imageio_ffmpeg
from PIL import Image, ImageOps
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = D + 'poses/'
for k in range(1, 10):
    shutil.copyfile(P + 'w%d.png' % k, P + 's%d.png' % k)
    ImageOps.mirror(Image.open(P + 'w%d.png' % k)).save(P + 't%d.png' % k)
ff = imageio_ffmpeg.get_ffmpeg_exe()
e = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', e)
DUR = round(int(m.group(2)) * 60 + float(m.group(3)), 2)
print('DUR', DUR)

# 拍（85BPM＝tempo_check のキック 1位）
s = io.open(D + 'beats_1120.py', encoding='utf-8').read()
for a, b in (('END = 107.7', 'END = %.1f' % (DUR - 0.3)), ('np.arange(80.3, 81.31, 0.02)', 'np.arange(84.5, 85.51, 0.02)'),
             ('fit(SN, b, 1, 106.5, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 110, 10)', 'range(0, 90, 10)'),
             ("beats_1120.txt", "beats_1123m.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1123m.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1123m.py'], check=True)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+23日', [2.1, 3.1]), ('月曜日の', [5.8]), ('発売の J-POPと', [7.3, 8.7])],
    [('ロックの', [9.9]), ('チケット', [11.2]), ('言うところよ', [12.1])],
    [('午前 10時は', [17.4, 18.2]), ('南佳孝', [19.1])],
    [('バレンタイン', [20.4]), ('ディナー&ライブ 兵庫', [21.4, 23.2])],
    [('電脳ヒメカ 愛知', [24.2, 26.3])],
    [('昼 12時は', [27.3, 28.0]), ('Furui Riho 東京', [30.0, 31.2])],
    [('め組 東京', [32.1, 32.6]), ('猪狩翔一', [33.2])],
    [('また、ここで。 東京', [34.2, 35.2])],
    [('NETH PRIERE CAIN', [36.0]), ('愛知', [38.7])],
    [('人格ラヂオ 神奈川', [39.7, 42.8])],
    [('夜 10時は', [44.4, 45.1]), ('Solid Statement', [46.2]), ('Soul 東京 ほか', [48.3, 49.0, 49.8])],
    [('ほかにも まだ', [50.2, 51.2]), ('あるわよ', [52.1])],
    [('ライブで 一緒に', [57.0, 57.8]), ('歌いたいわ', [58.6])],
    [('oshinavi+.jpで', [60.1, 61.4]), ('名前を', [62.4]), ('検索してね', [63.6])],
    [('公演と', [65.7]), ('アーティストの', [66.9]), ('紹介も 載せてるわ', [68.2, 69.6])],
    [('売り場まで', [71.7]), ('案内+するのは', [72.8, 73.3]), ('おしなび', [74.3])],
    [('oshinavi+.jp', [75.5, 77.4]), ('だわよ', [78.4])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
ms = re.sub(r'DUR = [\d.]+', 'DUR = %.2f' % DUR, ms, count=1)
pairs = [('LOW = {13, 14}', 'LOW = {14, 15}'),
         ("CHORUS_AT, URL_AT = chunks[13]['show'], chunks[15]['show']", "CHORUS_AT, URL_AT = chunks[14]['show'], chunks[16]['show']"),
         ("chunks[15]['cy'] = 1080", "chunks[16]['cy'] = 1080"),
         ("'lines': [[['ロック', 999, False]], [['11/21(土)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['J-POP・ロック', 999, False]], [['11/23(月・祝)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/21(土) 発売', 'kind': 'ロック', 'name': 'NIGHTMARE',",
          "S = {'when': '11/23(月・祝) 発売', 'kind': 'J-POP・ロック', 'name': 'Furui Riho',"),
         ("'rock_1121.json'", "'music_1123.json'")]
for x, y in pairs:
    assert x in ms, ('make_spec に無い', x)
    ms = ms.replace(x, y)
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('NIGHTMARE', 'ライブハウス'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
r = r.replace("'rock_1121.json'", "'music_1123.json'").replace("'rock_1121_v.json'", "'music_1123_v.json'")
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s2', 't3', 's4', 't5', 's6', 't7', 's8', 't9', 's3', 't2', 's5', 't4', 's7', 's1', 's1']   # 11/23 J-POP・ロック（ビジュアル系の姐さん）："
             "1 黒と赤の髪でマイク（締めのまん中）／2 白金の髪でギター（カバー）／3 青紫の髪でバラ／4 銀と黒の髪でベース／5 ワインレッドのボブ"
             "／6 真っ白の結い上げでステッキ／7 深緑の髪でドラムスティック／8 ピンクと黒の髪でキャンドル／9 金と紫の髪で日傘") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 7.3, 12.1, 17.4, 20.4, 24.2, 27.3, 32.1, 36.0, 39.7, 44.4, 50.2, 57.0, 60.1]   # 歌の行・言葉の頭（lyrics_times2.txt）＝1人 8 秒以内" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s2', _R[0]), ('s3', _R[1]), ('s8', _R[2]), ('s9', _R[3])]   # 11/23 J-POP・ロック 下の段＝白金ギター・青紫バラ・ピンクのキャンドル・金と紫の日傘（まん中の黒と赤のマイク s1 と重ねない）" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 38685, 'NIGHTMARE', '11/21'"
assert x in sb
sb = sb.replace(x, "CID, Q, MD = 45978, 'Furui Riho', '11/23'")
y = 'new D(2026,10,18,20,0)'
assert y in sb
sb = sb.replace(y, 'new D(2026,10,20,20,0)')   # TikTok 先出し＝11/20 の夜
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)
print('ok')
