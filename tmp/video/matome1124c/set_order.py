# -*- coding: utf-8 -*-
# 11/16 TikTok スポーツ：出る順（render.py の ORDER・PARADE）を姐さんのスポーツ9人に差し替える
#   w＝シートの向き・m＝反転。w1 相撲は使わない（上半身が裸で胸が見える絵＝載せない）
#   w2 サッカー／w3 ラグビー／w4 女子プロレス／w5 野球／w6 チア（締め）／w7 ボクサー／w8 バスケット／w9 応援のファン
#   タップまで約 59.4 秒＝1人 8 秒以内には 8 人要る＝7着を1回ずつ＋サッカーを反転でもう一度（最初と最後に離す）。向きを交互に
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
old = "ORDER = ['w1', 'b2', 'w4', 'b8', 's6', 'b3', 'w8', 'b6', 'w3', 'b9', 'w2']"
assert old in r
r = r.replace(old, "ORDER = ['w2', 'm3', 'w4', 'm5', 'w8', 'm7', 'w9', 'm2', 'w6']   # 11/16 姐さんのスポーツ（w1 相撲は使わない）・締めはチアの w6")
old2 = "PARADE = [('a7', _R[0]), ('w7', _R[1]), ('b4', _R[2]), ('b5', _R[3])]"
assert old2 in r
r = r.replace(old2, "PARADE = [('w3', _R[0]), ('w5', _R[1]), ('m7', _R[2]), ('m9', _R[3])]   # 11/16 左2人は右向き（ラグビー・野球）・右2人は左向き（ボクサー・応援のファン）＝真ん中を向く")
old3 = "'step': S['beat'] * 2,"
assert old3 in r
r = r.replace(old3, "'step': S['beat'] * 1,")   # 11/16 後奏が約 3 秒しかない＝1拍に1人で4人そろえる
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
print('ok')
