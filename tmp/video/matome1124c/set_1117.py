# -*- coding: utf-8 -*-
# 11/17 TikTok J-POP（60.9 秒・75.0BPM）：make_spec・render・kara_style を 11/17 用に差し替える（11/16 スポーツの中身は全部消す）
#   時刻＝lyrics_times2.txt（言葉の頭）。文言＝USLT（渡した歌詞と一致）を漢字に・名前はサイトの表記（index.html の登録の範囲）
#   42567 ロックンロールサーカス2027（兵庫 10:00）／42757 木村徹二（愛知 10:00）／45419 尾崎裕哉（東京 10:00）
#   ／50748 高橋優（北海道 11:00 プレリザーブ）／49856 ムツムロ アキラ（東京 12:00）
import io, shutil
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
P = D + 'poses/'
# 楽器を据えた子（スタンドマイク・キーボード・座ってアコギ）は歩かせない＝まん中にふわっと出る s（向きはシートのまま）
for k in (1, 3, 8):
    shutil.copyfile(P + 'w%d.png' % k, P + 's%d.png' % k)

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {')
ms = ms[:a] + """CHUNKS = [
    [('11月+17日', [3.4, 5.0]), ('火曜日の', [6.3]), ('発売の J-POP', [7.9, 9.1]), ('言うわね', [9.8])],
    [('午前 10時は', [12.0, 12.8]), ('ロックンロール', [13.6]), ('サーカス+2027', [14.8, 15.7]), ('兵庫', [17.4])],
    [('木村徹二 愛知', [18.3, 20.1]), ('尾崎裕哉 東京', [20.9, 23.5])],
    [('午前 11時は', [25.0, 25.5]), ('高橋優', [26.8]), ('北海道', [28.5])],
    [('昼 12時は', [31.3, 31.9]), ('ムツムロ アキラの', [33.0, 34.1]), ('ライブ 東京', [35.2, 36.2])],
    [('ほかにも あるわ', [37.9, 39.3]), ('忘れないでね', [39.8])],
    [('好きな 歌を', [41.5, 42.3]), ('生で 聴きたいわ', [43.0, 43.8])],
    [('oshinavi+.jpで', [44.8, 46.0]), ('名前を', [46.8]), ('検索してね', [47.6])],
    [('公演と', [50.4]), ('アーティストの', [51.2]), ('紹介も 載せてるわ', [52.2, 52.8])],
    [('売り場まで', [54.3]), ('案内+するのは', [55.5, 56.0]), ('おしなび', [57.0])],
    [('oshinavi+.jp', [57.8, 58.9]), ('なのよ', [59.8])],   # すちこ 11/13「検索するのは小文字だから小文字で表示して」
]
""" + ms[b:]
pairs = [('LOW = {10, 11}', 'LOW = {8, 9}'), ('DUR = 75.6', 'DUR = 60.9'),
         ("CHORUS_AT, URL_AT = chunks[10]['show'], chunks[12]['show']", "CHORUS_AT, URL_AT = chunks[8]['show'], chunks[10]['show']"),
         ("chunks[12]['cy'] = 1080", "chunks[10]['cy'] = 1080"),
         ("'lines': [[['スポーツ', 999, False]], [['11/16(月)', 999, True], ['発売', 999, False]]]",
          "'lines': [[['J-POP', 999, False]], [['11/17(火)', 999, True], ['発売', 999, False]]]"),
         ("S = {'when': '11/16(月) 発売', 'kind': 'スポーツ', 'name': '大相撲富士宮場所',",
          "S = {'when': '11/17(火) 発売', 'kind': 'J-POP', 'name': '尾崎裕哉Concert2027',")]
for x, y in pairs:
    assert x in ms, x
    ms = ms.replace(x, y)
for bad in ('スポーツ', '大相撲', '11/16'):
    assert bad not in ms.split('CHUNKS = [')[1].split('karaoke = [')[0] or bad == '11/16', bad
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + ("ORDER = ['w4', 'm4', 'w2', 's1', 's8', 'w5', 's3', 'w6', 'w7', 'm7', 'w9']   # 11/17 J-POP：歌う行と衣装を合わせる"
             "（前奏＝金のダンス→その場で向きを変える／ロックンロールサーカス＝エレキ／木村徹二＝スタンドマイク／尾崎裕哉＝座ってアコギ"
             "／午前11時・高橋優＝ハンドマイク／昼12時・ムツムロ アキラ＝キーボード／ほかにも＝ヘッドセット／好きな歌を〜検索＝ペンライトのファン→向きを変える）・締めは両手を広げる w9") + r[b:]
a = r.index('LINE_AT = ['); b = r.index('\n', a)
r = r[:a] + "LINE_AT = [0.0, 6.3, 13.6, 18.3, 20.9, 25.0, 31.3, 37.9, 41.5, 44.8]   # 行が歌われ始める秒（lyrics_times2.txt）" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('w7', _R[0]), ('w4', _R[1]), ('m5', _R[2]), ('m6', _R[3])]   # 11/17 左2人は右向き（ペンライトのファン・金のダンス）・右2人は左向き（ハンドマイク・ヘッドセット）＝真ん中を向く" + r[b:]
old = "{'t0': _url + S['beat'] * 4, 't1': S['dur'] + 1, 'step': S['beat'] * 1,"
assert old in r
# 11/17 この曲は後奏がほぼ無い（歌い終わり 60.4 秒・曲の終わり 60.9 秒）＝締めの場面に入ってすぐ 0.3 秒おきに4人を下ろす（終わりの2秒前には全員着地）
r = r.replace(old, "{'t0': _url + 0.1, 't1': S['dur'] + 1, 'step': 0.3,")
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)

# 背景 7472 は暗い紫（もとから暗い）＝字は白（まだ）→黄（歌った）・縁は濃紺（11/16 の明るい背景用の濃紺／えんじを戻す）
ks = io.open(D + 'kara_style.py', encoding='utf-8').read()
old_k = "        else:     # 11/16 明るい背景＝濃紺／えんじ・縁は白・うっすら影\n            todo, done, stroke, shadow = NAVY, ENJI, WHITE, (80, 30, 90, 90)"
assert old_k in ks
ks = ks.replace(old_k, "        else:     # 11/17 暗い紫の背景＝白／黄・縁は濃紺\n            todo, done, stroke, shadow = WHITE, YEL, (20, 10, 40), (0, 0, 0, 150)")
io.open(D + 'kara_style.py', 'w', encoding='utf-8').write(ks)
print('ok')
