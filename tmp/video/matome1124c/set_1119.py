# -*- coding: utf-8 -*-
# 11/19 クラシック（1:36・81BPM）：tiktok1118 から写した make_spec・render・shoot_badge・kara_style を 11/19 用に差し替える
#   演奏家は歩かせない＝全員 s（シートの向き）／t（反転）＝まん中にふわっと現れる（calm）
#   時刻＝lyrics_times2.txt（言葉の頭）。文言＝USLT を漢字に・名前はサイトの表記（index.html の登録）
#   49293 みなとみらい（神奈川）／49287 音楽堂（神奈川）／51547 藤岡幸夫×本堂竣哉「田園」（東京）／50782 CITTADINO歌劇団（東京）
#   ／50780 日本センチュリー交響楽団（大阪）／35673 ワーヘリ（京都）＝全部 11/19 10:00 発売
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

# 拍（81BPM＝スネア 162 の半分・落ち着いた弾み）
s = io.open(D + 'beats_1114.py', encoding='utf-8').read()
for a, b in (('END = 67.5', 'END = %.1f' % (DUR - 0.3)), ('np.arange(100.5, 101.51, 0.05)', 'np.arange(80.5, 81.51, 0.02)'),
             ('fit(SN, b, 1, 66, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 70, 10)', 'range(0, 100, 10)'),
             ("beats_1114.txt", "beats_1119.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1119.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1119.py'], check=True)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+19日', [3.3, 4.3]), ('木曜日の', [6.2]), ('発売の クラシック', [7.4, 8.5]), ('言うわよ', [10.4])],
    [('午前 10時は', [14.4, 15.1]), ('みなとみらい', [16.0]), ('アフタヌーン', [17.4]), ('コンサート 神奈川', [18.5, 19.4])],
    [('前橋汀子', [20.4]), ('千住真理子', [21.6]), ('宮田大も 出るわ', [23.2, 24.6])],
    [('音楽堂 ホリデー', [25.8, 27.3]), ('アフタヌーン', [27.9]), ('コンサート 神奈川', [29.0, 29.9])],
    [('小菅優と', [31.7]), ('葵トリオも', [33.6]), ('出るのよ', [35.1])],
    [('藤岡幸夫と', [38.0]), ('本堂竣哉の', [39.5]), ('田園 東京', [40.9, 41.2])],
    [('CITTADINO', [41.5]), ('歌劇団の', [42.5]), ('オペラ 東京', [43.4, 44.0])],
    [('日本センチュリー', [44.5]), ('交響楽団', [46.2]), ('大阪', [47.5])],
    [('ユーフォニアムと', [49.3]), ('テューバの', [52.6]), ('ワーヘリ 京都', [53.6, 54.6])],
    [('どれも 聴きに', [55.3, 56.7]), ('行きたいわね', [57.6])],
    [('生の 音に', [61.4, 62.5]), ('包まれたいわ', [63.6])],
    [('oshinavi+.jpで', [65.5, 66.8]), ('名前を', [68.0]), ('検索してね', [69.7])],
    [('公演と', [73.1]), ('アーティストの', [74.3]), ('紹介も 載せてるわ', [75.6, 76.9])],
    [('売り場まで', [79.0]), ('案内+するのは', [80.6, 81.4]), ('おしなび', [82.2])],
    [('oshinavi+.jp', [83.0, 84.6]), ('なんだわ', [85.6])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
pairs = [('LOW = {9, 10}', 'LOW = {12, 13}'), ('DUR = 76.1', 'DUR = %.2f' % DUR),
         ("CHORUS_AT, URL_AT = chunks[9]['show'], chunks[11]['show']", "CHORUS_AT, URL_AT = chunks[12]['show'], chunks[14]['show']"),
         ("chunks[11]['cy'] = 1080", "chunks[14]['cy'] = 1080"),
         ("'lines': [[['舞台・トークショー', 999, False]], [['11/18(水)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['クラシック', 999, False]], [['11/19(木)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/18(水) 発売', 'kind': '舞台・トークショー', 'name': 'スウィーニー・トッド',",
          "S = {'when': '11/19(木) 発売', 'kind': 'クラシック', 'name': 'みなとみらい',"),
         ("'stage_1118.json'", "'classic_1119.json'")]
for x, y in pairs:
    assert x in ms, x
    ms = ms.replace(x, y)
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('上原', 'スウィーニー', '舞台・トーク', '11/18'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
r = r.replace("'stage_1118.json'", "'classic_1119.json'").replace("'stage_1118_v.json'", "'classic_1119_v.json'")
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s4', 't5', 's3', 's1', 's2', 't8', 't3', 's9', 's5', 't4', 's6', 's7', 't9', 't2', 't6', 's8']   # 11/19 クラシック（近未来の演奏家・歩かせない）："
             "前奏＝指揮者 s4→「発売のクラシック」オペラ t5／みなとみらい＝ピアノ s3／前橋汀子・千住真理子＝ヴァイオリン s1／宮田大＝チェロ s2"
             "／音楽堂＝フルート t8／小菅優（ピアノ）＝ピアノ t3／藤岡幸夫×本堂竣哉「田園」＝ハープ s9／CITTADINO 歌劇団のオペラ＝オペラ歌手 s5"
             "／日本センチュリー交響楽団＝指揮者 t4／ユーフォニアム＝s6／テューバの ワーヘリ＝s7／どれも聴きに＝ハープ t9／生の音に＝チェロ t2／検索＝ユーフォ t6・締めはフルート s8") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 7.4, 14.4, 20.4, 23.2, 25.8, 31.7, 38.0, 41.5, 44.5, 49.3, 52.6, 55.3, 61.4, 65.5]   # 歌の行・言葉の頭（lyrics_times2.txt）＝1人 8 秒以内" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s1', _R[0]), ('s3', _R[1]), ('t5', _R[2]), ('t7', _R[3])]   # 11/19 左2人は右向き（ヴァイオリン・ピアノ）・右2人は左向き（オペラ・テューバ）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 53651, 'スウィーニー・トッド', '11/18'"
assert x in sb
sb = sb.replace(x, "CID, Q, MD = 49293, 'みなとみらい', '11/19'")
y = 'new D(2026,10,15,20,0)'
assert y in sb
sb = sb.replace(y, 'new D(2026,10,16,20,0)')   # TikTok 先出し＝11/16 の夜に撮る
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)

ks = io.open(D + 'kara_style.py', encoding='utf-8').read()
x = "        else:     # 11/17 暗い紫の背景＝白／黄・縁は濃紺\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)"
assert x in ks
ks = ks.replace(x, "        else:     # 11/19 背景 49445 は明るい青いタイル＝字を暗く：まだ＝濃紺／歌った＝えんじ・縁は白の太め＋うっすら影（11/16 主役と同じ）\n            todo, done, stroke, shadow = NAVY, ENJI, WHITE, (0, 0, 0, 70)")
io.open(D + 'kara_style.py', 'w', encoding='utf-8').write(ks)
print('ok')
