# -*- coding: utf-8 -*-
# 11/12 お笑い（X 今夜・1:16.4・131.2BPM）：冬雪の子（全員歩く子 w＝右向き／m＝反転＝左向き）・make_spec の塊・render の並び
#   歌詞の時刻＝lyrics_times2.txt（全体）＋ lyrics_part.txt（拾えなかった たかあんどとし・まゆりか を USLT の並びで取り直し）
#   文言＝USLT（すちこがサビを2回に足した）・名前はサイトの表記
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'

ms = io.open(D + 'make_spec.py', encoding='utf-8').read()
a, b = ms.index('CHUNKS = ['), ms.index('LOW = {9}')
ms = ms[:a] + """CHUNKS = [
    [('明日 11月+12日の', [3.0, 3.6, 5.0]), ('発売の お笑い', [6.8, 8.1]), ('言うわね', [9.0])],
    [('午前 10時は', [13.0, 13.9]), ('NON STYLE 東京', [14.5, 15.0, 15.7]), ('中川家 東京', [16.5, 17.5])],
    [('コットン 東京', [18.3, 19.3]), ('見取り図 東京', [20.4, 21.2]), ('ミキ 東京', [22.0, 23.3])],
    [('EXIT 東京', [23.8, 24.3]), ('ジャルジャル 東京', [24.9, 25.4]), ('チョコレート', [25.9]), ('プラネット 東京', [26.4, 27.1])],
    [('タカアンドトシ 東京', [27.7, 28.5]), ('マユリカ 東京', [29.0, 29.5]), ('空気階段 東京', [30.0, 30.8]), ('笑い飯 東京', [31.3, 31.9])],
    [('すゑひろがりず 埼玉', [32.3, 33.7]), ('囲碁将棋 埼玉', [34.6, 35.1]), ('ほかにも あるわ', [35.6, 36.3])],
    [('昼 12時は', [36.8, 37.1]), ('新開地 喜楽館', [38.1, 39.0]), ('兵庫', [40.5])],
    [('年越しは', [41.6]), ('笑って', [43.9]), ('過ごしたいわ', [45.2])],
    [('売り場まで', [48.9]), ('案内+するのは', [49.9, 50.7]), ('おしなび', [51.5])],
    [('OSHINAVI+.jp', [52.3, 53.4]), ('なんだわ', [54.7])],
    [('売り場まで', [56.3]), ('案内+するのは', [57.2, 58.2]), ('おしなび', [58.8])],
    [('OSHINAVI+.jp', [59.6, 60.5]), ('なんだわ', [62.1])],
]
""" + ms[b:]
ms = ms.replace('LOW = {9}', 'LOW = {8, 9}').replace('DUR = 75.7', 'DUR = 76.4')
ms = ms.replace("CHORUS_AT, URL_AT = chunks[9]['show'], chunks[10]['show']", "CHORUS_AT, URL_AT = chunks[8]['show'], chunks[10]['show']   # 11/12 サビ1回目（2行）＝タップの場面・2回目から締め")
ms = ms.replace("chunks[10]['cy'] = 1080", "chunks[10]['cy'] = chunks[11]['cy'] = 1080")
ms = ms.replace("'lines': [[['11/11(水)', 999, False]]", "'lines': [[['11/12(木)', 999, False]]")
ms = ms.replace("S = {'when': '明日 11/11(水) 発売', 'kind': 'お笑い', 'name': 'SUN「新春！よしもと大爆笑2027」',",
                "S = {'when': '明日 11/12(木) 発売', 'kind': 'お笑い', 'name': 'ルミネtheよしもと 年末特別公演',")
for need in ("LOW = {8, 9}", "DUR = 76.4", "chunks[8]['show'], chunks[10]['show']", "chunks[11]['cy'] = 1080", "'11/12(木)'", "年末特別公演'"):
    assert need in ms, need
io.open(D + 'make_spec.py', 'w', encoding='utf-8').write(ms)

# ---- render：タップまで（約 48.6 秒）を 8 人で割る（1人 約 6 秒）＝右向き・左向きを交互／締め＝ピンクのダウンの子 w7
#   後奏＝締めの場面に入って1小節後から 2小節に1人ずつ4人が上から下りて1段に並ぶ＝左の2人は右向き（w）・右の2人は左向き（m）＝みんな真ん中を向く
rd = io.open(D + 'render.py', encoding='utf-8').read()
rd = re.sub(r"ORDER = \['w1', 's4'.*?\]\n", """# 11/12 冬雪の子（全員歩く子・w＝右向き／m＝反転＝左向き）：9着を1回ずつ・向きを交互に・締めはピンクのダウンとハートのヘッドホンの子 w7
ORDER = ['w1', 'm4', 'w2', 'm6', 'w3', 'm8', 'w5', 'm9', 'w7']
""", rd, count=1, flags=re.S)
rd = rd.replace("PARADE = [('s9', _R[0]), ('m7', _R[1]), ('t4', _R[2]), ('w3', _R[3])]   # 11/11 後奏 約 6 秒＝2拍に1人ずつ4人",
                "PARADE = [('w9', _R[0]), ('w3', _R[1]), ('m5', _R[2]), ('m1', _R[3])]   # 11/12 左2人は右向き・右2人は左向き＝真ん中を向く")
rd = rd.replace("outro_parade.install(g['render'], S, [{'t0': _url, 't1': S['dur'] + 1, 'step': S['beat'] * 2,",
                "outro_parade.install(g['render'], S, [{'t0': _url + S['beat'] * 4, 't1': S['dur'] + 1, 'step': S['beat'] * 8,")
for need in ("ORDER = ['w1', 'm4'", "('w9', _R[0])", "'t0': _url + S['beat'] * 4", "S['beat'] * 8,"):
    assert need in rd, need
io.open(D + 'render.py', 'w', encoding='utf-8').write(rd)
print('ok')
