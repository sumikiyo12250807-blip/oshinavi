# -*- coding: utf-8 -*-
# 11/24 クラシックとおでかけ（1:37・TikTok 先出し）：matome1123m から写した make_spec・render・beats・shoot_badge を 11/24 用に差し替える
#   すちこが渡した＝曲 おしなびどっと (38).mp3・背景 30729（夕焼けのビル街）。姐さん＝夕暮れの街へ出かけるよそ行き 9人（右向き＝s／反転 t）
#   時刻＝lyrics_times_head.txt（0〜32 秒）＋lyrics_times2.txt（言葉の頭）。名前は登録の表記：下野竜也・高橋英樹 id53841／宮田大・辻本玲 id54945
#     ／川平慈英・伊原剛志・彩乃かなみ id49265／タサン志麻 id55875／珠光茶会 id55879／野村萬斎 id55686／新国立劇場オペラ id54075
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

# 拍（72.8BPM＝tempo_check のキック・スネア 1位）
s = io.open(D + 'beats_1120.py', encoding='utf-8').read()
for a, b in (('END = 107.7', 'END = %.1f' % (DUR - 0.3)), ('np.arange(80.3, 81.31, 0.02)', 'np.arange(72.3, 73.31, 0.02)'),
             ('fit(SN, b, 1, 106.5, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 110, 10)', 'range(0, 100, 10)'),
             ("beats_1120.txt", "beats_1124c.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1124c.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1124c.py'], check=True)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+24日の', [7.0, 8.6]), ('発売の', [10.3]), ('クラシックと', [11.7])],
    [('おでかけの', [13.4]), ('チケット', [14.9]), ('言うわね', [16.1])],
    [('朝 10時', [19.1, 19.8]), ('下野竜也と', [20.5]), ('高橋英樹 東京', [22.4, 24.5])],
    [('宮田大と', [25.7]), ('辻本玲の チェロ', [27.1, 29.0]), ('東京', [29.9])],
    [('川平慈英', [32.5]), ('伊原剛志', [34.2]), ('彩乃かなみ 山口', [35.8, 37.5])],
    [('タサン志麻 大阪', [38.6, 40.0])],
    [('珠光茶会 奈良', [40.9, 42.4]), ('先行', [43.2])],
    [('11時', [47.1]), ('野村萬斎たち', [48.2]), ('東京 先行', [51.3, 51.8])],
    [('夜 7時', [52.7, 53.7]), ('新国立劇場', [54.8]), ('オペラ 東京 先行', [57.1, 57.7, 58.4])],
    [('ほかにも あるわ', [59.3, 62.2]), ('見逃さないでね', [63.3])],
    [('売り場まで', [68.6]), ('案内+するのは', [71.0, 71.5]), ('おしなび', [72.7])],
    [('公演と', [74.7]), ('アーティストの', [76.2]), ('紹介も 載せてるわ', [77.8, 79.0])],
    [('oshinavi+.jp', [83.0, 86.3]), ('なのよ', [87.4])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
ms = re.sub(r'DUR = [\d.]+', 'DUR = %.2f' % DUR, ms, count=1)
pairs = [('LOW = {14, 15}', 'LOW = {10, 11}'),
         ("CHORUS_AT, URL_AT = chunks[14]['show'], chunks[16]['show']", "CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']"),
         ("chunks[16]['cy'] = 1080", "chunks[12]['cy'] = 1080"),
         ("'lines': [[['J-POP・ロック', 999, False]], [['11/23(月・祝)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['クラシックと', 999, False]], [['おでかけ', 999, False]], [['11/24(火)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/23(月・祝) 発売', 'kind': 'J-POP・ロック', 'name': 'Furui Riho',",
          "S = {'when': '11/24(火) 発売', 'kind': 'クラシック・おでかけ', 'name': 'N響大河ドラマ&名曲コンサート',")]
for x, y in pairs:
    assert x in ms, ('make_spec に無い', x)
    ms = ms.replace(x, y)
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('Furui', '南佳孝', 'J-POP'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s6', 't4', 's2', 't5', 's9', 't8', 's3', 't7', 's6', 't9', 's4', 's1']   # 11/24 クラシックとおでかけ（よそ行きの姐さん）："
             "1 赤いドレスでグラス（締めのまん中）／2 花柄の着物で金のバッグ／3 クリーム色のジャケットと帽子／4 紺のベルベットのコートとステッキ"
             "／5 白いパンツスーツと帽子／6 エメラルドのドレスでグラス（カバー）／7 藤色の着物で扇子／8 大正ロマンの袴とトランク／9 水玉のワンピース") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 7.0, 13.4, 19.1, 25.7, 32.5, 38.6, 47.1, 52.7, 59.3, 63.3]   # 歌の行・言葉の頭（lyrics_times_head/2）＝1人 8 秒前後" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s5', _R[0]), ('s2', _R[1]), ('s4', _R[2]), ('s9', _R[3])]   # 11/24 下の段＝白いスーツ・花柄の着物・紺のコート・水玉（まん中の赤いドレス s1 と重ねない・グラスの似た子 6 も外す）" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 45978, 'Furui Riho', '11/23'"
assert x in sb
sb = sb.replace(x, "CID, Q, MD = 53841, 'N響大河ドラマ', '11/24'")
y = 'new D(2026,10,20,20,0)'
assert y in sb
sb = sb.replace(y, 'new D(2026,10,21,20,0)')   # TikTok 先出し＝11/21 の夜
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)
print('ok')
