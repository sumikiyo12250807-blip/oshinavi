# -*- coding: utf-8 -*-
# 11/24 ライブ（J-POP・ロック・アイドル）（0:51・TikTok 先出し）：matome1124c の make_spec・render・shoot_badge・board・mk_page を写して 11/24 ライブ用に差し替える
#   すちこ（11/20 夜）「普段着でおとなしい感じのファッションが最初の曲に合う…2本目に今絵コンテ出してくれたファッション合うわ」
#   ＝1124c のよそ行きの姐さん9人（s/t・動いた絵 e/f/v・size_fix1124 で背をそろえた分）をそのまま使う。背景 38389（黒地に小さな光・7秒）
#   時刻＝lyrics_times2.txt（言葉の頭）。名前は登録の表記：奇妙礼太郎BAND・在日ファンク id45930／DEEN id55672／惡ノ夢・暇潰シ id36182
#     ／東京アイドル劇場（アイゲキ）id53227／きゅ〜くる id54678／革命-DOPENESS- id55948
import io, os, re, shutil, subprocess, glob
import imageio_ffmpeg
C = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
D = 'C:/Users/user/oshinavi/tmp/video/matome1124l/'
# ① 姐さんの切り抜き（1124c の poses をまるごと）と動いた絵の見本
for f in glob.glob(D + 'poses/*.png'):
    os.remove(f)
for f in glob.glob(C + 'poses/*.png'):
    shutil.copyfile(f, D + 'poses/' + os.path.basename(f))
shutil.copyfile(C + 'contact_move.png', D + 'contact_move.png')
# ② 1124c で差し替え済みの道具を写す
for f in ('make_spec.py', 'render.py', 'shoot_badge.py', 'board_1124c.py', 'mk_page_1124c.py', 'contact17.py'):
    s = io.open(C + f, encoding='utf-8').read().replace('matome1124c', 'matome1124l').replace('board_1124c', 'board_1124l')
    io.open(D + f.replace('1124c', '1124l'), 'w', encoding='utf-8').write(s)
ff = imageio_ffmpeg.get_ffmpeg_exe()
e = subprocess.run([ff, '-i', D + 'song.mp3'], capture_output=True, text=True, errors='replace').stderr
m = re.search(r'Duration: (\d+):(\d+):([\d.]+)', e)
DUR = round(int(m.group(2)) * 60 + float(m.group(3)), 2)
print('DUR', DUR)

# ③ 拍（114BPM＝tempo_check のキック 1位）
s = io.open(D + 'beats_1120.py', encoding='utf-8').read()
for a, b in (('END = 107.7', 'END = %.1f' % (DUR - 0.3)), ('np.arange(80.3, 81.31, 0.02)', 'np.arange(113.5, 114.51, 0.02)'),
             ('fit(SN, b, 1, 106.5, 0.002)', 'fit(SN, b, 1, %.1f, 0.002)' % (DUR - 1.5)), ('range(0, 110, 10)', 'range(0, 60, 10)'),
             ("beats_1120.txt", "beats_1124l.txt")):
    assert a in s, a
    s = s.replace(a, b)
io.open(D + 'beats_1124l.py', 'w', encoding='utf-8').write(s)
subprocess.run(['python', D + 'beats_1124l.py'], check=True)

# ④ 歌詞の区切り（言葉の頭の時刻）
ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+24日の', [2.5, 3.2]), ('発売の', [4.5]), ('ライブの', [5.2])],
    [('チケット', [5.7]), ('言うわよ', [6.3])],
    [('朝 10時', [7.2, 8.5]), ('奇妙礼太郎BAND と', [9.9, 12.0])],
    [('在日ファンク 東京', [12.1, 13.2])],
    [('11時', [14.2]), ('DEEN 北海道', [15.0, 15.9]), ('先行', [16.8])],
    [('夕方 6時', [19.1, 20.0]), ('惡ノ夢と', [20.5]), ('暇潰シ 東京', [21.6, 22.2])],
    [('夜 9時', [23.3, 23.7]), ('東京アイドル劇場 東京', [24.0, 25.8])],
    [('きゅ〜くる', [26.6])],
    [('夜 10時すぎ', [27.3, 28.0]), ('革命-DOPENESS-たち', [29.3]), ('東京', [31.2])],
    [('忘れないでね', [33.0])],
    [('売り場まで', [35.2]), ('案内+するのは', [37.2, 37.8]), ('おしなび', [38.5])],
    [('公演と', [39.3]), ('アーティストの', [40.1]), ('紹介も 載せてるわ', [41.1, 42.1])],
    [('oshinavi+.jp', [43.5, 44.6]), ('だわ', [46.1])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
ms = re.sub(r'DUR = [\d.]+', 'DUR = %.2f' % DUR, ms, count=1)
pairs = [("'lines': [[['クラシックと', 999, False]], [['おでかけ', 999, False]], [['11/24(火)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['ライブ', 999, False]], [['11/24(火)', 999, True], ['発売', 999, False]]]"),
         ("'kind': 'クラシック',", "'kind': 'ライブ',"),
         ("'name': 'N響大河ドラマ&名曲コンサート'", "'name': '奇妙礼太郎BAND／在日ファンク'")]
for x, y in pairs:
    assert x in ms, ('make_spec に無い', x)
    ms = ms.replace(x, y)
for must in ('LOW = {10, 11}', "chunks[10]['show'], chunks[12]['show']", "chunks[12]['cy'] = 1080"):
    assert must in ms, must
body = ms.split('CHUNKS = [')[1].split('karaoke = [')[0]
for bad in ('下野', 'クラシック', 'N響'):
    assert bad not in body, bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

# ⑤ 姐さんの順番（きゅ〜くるの行は 0.7 秒＝アイドル劇場の子と同じ出番）
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['s3', 't9', 's4', 't2', 's8', 't5', 's6', 't7', 's9', 's1']   # 11/24 ライブ（1124c のよそ行きの姐さんを回した）："
             "1 赤いドレスでグラス（締めのまん中）／2 花柄の着物で金のバッグ／3 クリーム色のジャケットと帽子（カバー）／4 紺のベルベットのコートとステッキ"
             "／5 白いパンツスーツと帽子／6 エメラルドのドレスでグラス／7 藤色の着物で扇子／8 大正ロマンの袴とトランク／9 水玉のワンピース") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 2.5, 7.2, 12.1, 14.2, 19.1, 23.3, 27.3, 33.0]   # 歌の行・言葉の頭（lyrics_times2）＝1人 8 秒以内" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('s5', _R[0]), ('s2', _R[1]), ('s4', _R[2]), ('s9', _R[3])]   # 11/24 ライブ 下の段＝白いスーツ・花柄の着物・紺のコート・水玉（まん中の赤いドレス s1 と重ねない・グラスの似た子 6 も外す）" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

sb = io.open(D + 'shoot_badge.py', encoding='utf-8').read()
x = "CID, Q, MD = 53841, 'N響大河ドラマ', '11/24'"
assert x in sb
sb = sb.replace(x, "CID, Q, MD = 45930, '奇妙礼太郎', '11/24'")
assert 'new D(2026,10,21,20,0)' in sb   # TikTok 先出し＝11/21 の夜（1124c と同じ）
io.open(D + 'shoot_badge.py', 'w', encoding='utf-8').write(sb)

# ⑥ 絵コンテの撮る秒と試しの範囲（0:51）
bd = io.open(D + 'board_1124l.py', encoding='utf-8').read()
a = bd.index('T = ['); b = bd.index('\n', a)
bd = bd[:a] + "T = [0.0, 2.0, 4.5, 7.5, 10.5, 12.5, 15.0, 18.0, 20.5, 24.0, 27.0, 29.5, 33.5, 36.0, 39.0, 42.0, 44.5, 47.0, 50.5]" + bd[b:]
x = "(('clip_a', 0.0, 30.0), ('clip_b', 66.0, 97.0))"
assert x in bd
bd = bd.replace(x, "(('clip_a', 0.0, 25.0), ('clip_b', 26.0, %.1f))" % DUR)
io.open(D + 'board_1124l.py', 'w', encoding='utf-8').write(bd)
print('ok')
