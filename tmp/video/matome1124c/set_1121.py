# -*- coding: utf-8 -*-
# 11/21 ロック（1:28・TikTok 先出し）：matome1120j から写した make_spec・render・beats・shoot_badge を 11/21 用に差し替える
#   すちこ「７０年代のブラックソウルミュージック風のファッション」＝ソウル風の姐さん9人（右向き＝s／反転 t）・歩かせない
#   背景 91898（すちこが渡した・黒地にネオンの星・暗い）＝字は白／黄・縁は濃紺（暗い背景のいつもの形）
#   時刻＝lyrics_times2.txt（言葉の頭）。名前は登録の表記（tmp/x1118/x/rock_1121.txt＝index.html の 11/21 発売の登録）
#     0.1gの誤算 id37696／NIGHTMARE id38685／HAWAIIAN6 id53497・53498／ザアザア id41903／ニューロティカ id38636・53548／アイリフドーパ id45006・45023
#     ／古墳シスターズ id51188／NICOLAS id21361／山根康広 id53605／奇妙礼太郎 id53534／Plastic Tree id31191／Heavenstamp id45055／パール兄弟 id29610
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

# 拍（107BPM 前後＝tempo_check 107.4）
s = io.open(D + 'beats_1120.py', encoding='utf-8').read()
for a, b in (('END = 107.7', 'END = %.1f' % (DUR - 0.3)), ('np.arange(80.3, 81.31, 0.02)', 'np.arange(106.9, 107.91, 0.02)'),
             ('fit(SN, b, 1, 106.5, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 110, 10)', 'range(0, 80, 10)'),
             ("beats_1120.txt", "beats_1121.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1121.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1121.py'], check=True)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+21日', [1.3, 3.2]), ('土曜日の', [5.1]), ('発売の ロックの', [6.2, 7.4]), ('チケット 言うわよ', [8.0, 8.9])],
    [('午前 10時は', [11.4, 12.3]), ('0.1gの誤算 愛知', [13.4, 15.6])],
    [('NIGHTMARE 愛知', [16.4, 17.1]), ('HAWAIIAN6 東京 ほか', [18.1, 19.8, 20.1])],
    [('ザアザア 東京', [20.6, 21.5]), ('ニューロティカ 東京', [21.9, 23.2])],
    [('アイリフドーパ 東京', [23.7, 24.6]), ('古墳シスターズ 大阪', [25.2, 27.0])],
    [('NICOLAS 東京', [27.5, 28.6]), ('山根康広 大阪', [29.2, 29.8])],
    [('昼 12時は', [30.3, 31.1]), ('奇妙礼太郎 東京', [32.5, 34.1])],
    [('Plastic Tree 神奈川', [34.7, 35.7, 36.3]), ('Heavenstamp 神奈川', [36.7, 38.1])],
    [('パール兄弟 東京 ほか', [38.8, 40.3, 40.8])],
    [('ライブハウスで', [41.2]), ('一緒に 騒ぎましょ', [42.5, 43.3])],
    [('ほかにも まだまだ', [44.3, 45.4]), ('あるわよ', [46.3])],
    [('大きな 音で', [47.5, 48.2]), ('会いたいわ', [49.1])],
    [('oshinavi+.jpで', [51.5, 52.6]), ('名前を', [53.8]), ('検索してね', [54.6])],
    [('公演と', [56.6]), ('アーティストの', [57.0]), ('紹介も 載せてるわ', [58.0, 59.0])],
    [('売り場まで', [60.7]), ('案内+するのは', [61.9, 62.7]), ('おしなび', [63.2])],
    [('oshinavi+.jp', [65.2, 66.3]), ('なんだわ', [67.8])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
pairs = [('LOW = {14, 15}', 'LOW = {13, 14}'), ('DUR = 108.02', 'DUR = %.2f' % DUR),
         ("CHORUS_AT, URL_AT = chunks[14]['show'], chunks[18]['show']", "CHORUS_AT, URL_AT = chunks[13]['show'], chunks[15]['show']"),
         ("chunks[18]['cy'] = 1080", "chunks[15]['cy'] = 1080"),
         ("'lines': [[['J-POP', 999, False]], [['11/20(金)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['ロック', 999, False]], [['11/21(土)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/20(金) 発売', 'kind': 'J-POP', 'name': '世良公則',",
          "S = {'when': '11/21(土) 発売', 'kind': 'ロック', 'name': 'NIGHTMARE',"),
         ("'jpop_1120.json'", "'rock_1121.json'")]
for x, y in pairs:
    assert x in ms, ('make_spec に無い', x)
    ms = ms.replace(x, y)
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('J-POP', '11/20', '世良', '金曜'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
r = r.replace("'jpop_1120.json'", "'rock_1121.json'").replace("'jpop_1120_v.json'", "'rock_1121_v.json'")
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s1', 't2', 's3', 't4', 's5', 't6', 's7', 't8', 's9', 't1', 's4', 't3', 's2', 't5', 's7']   # 11/21 ロック（70年代ソウルの姐さん・歩かせない）："
             "1 アフロのマイクスタンド（カバー）／2 フェザーカットで指を天へ／3 コーンロー／4 黒いアフロのタンバリン／5 えんじのロングに緑のジャンプスーツ"
             "／6 ピンクのアフロパフ／7 オレンジのボブとミラーボール（締めのまん中）／8 スカーフとターコイズのドレス／9 プラチナの髪で蹴り上げる") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 6.2, 11.4, 16.4, 20.6, 23.7, 27.5, 30.3, 34.7, 38.8, 41.2, 44.3, 47.5, 51.5]   # 歌の行・言葉の頭（lyrics_times2.txt）＝1人 8 秒以内" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s1', _R[0]), ('s6', _R[1]), ('s8', _R[2]), ('s9', _R[3])]   # 11/21 下の段＝マイクスタンド・アフロパフ・スカーフ・蹴り上げ（まん中のミラーボール s7 と重ねない・反転も含めて同じ子なし）" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 26834, '世良公則', '11/20'"
assert x in sb
sb = sb.replace(x, "CID, Q, MD = 38685, 'NIGHTMARE', '11/21'")
y = 'new D(2026,10,17,20,0)'
assert y in sb
sb = sb.replace(y, 'new D(2026,10,18,20,0)')   # TikTok 先出し＝11/18 の夜に撮る
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)
print('ok')
