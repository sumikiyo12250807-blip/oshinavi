# -*- coding: utf-8 -*-
# すちこ「こっちの画像の方がいい」＝あごに水色の剃り跡の姐さん（背景透明）9人に差し替え：w＝シートの向き（右向き）・m＝反転（左向き）
#   w1 相撲／w2 サッカー／w3 ラグビー／w4 女子プロレス／w5 野球／w6 チア（締め）／w7 ボクサー／w8 バスケット／w9 ペンライトのファン
#   タップまで約 59 秒＝8 人を 1 回ずつ（約 7.4 秒）・向きを交互に・締めはチア w6。後奏の4人は前半の子を左2人右向き・右2人左向き
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = [')
b = r.index('\n', a)
r = r[:a] + "ORDER = ['w2', 'm3', 'w1', 'm5', 'w4', 'm8', 'w7', 'm9', 'w6']   # 11/16 あごに剃り跡の姐さんのスポーツ9人を1回ずつ・締めはチアの w6" + r[b:]
a = r.index('PARADE = [')
b = r.index('\n', a)
r = r[:a] + "PARADE = [('w9', _R[0]), ('w2', _R[1]), ('m3', _R[2]), ('m7', _R[3])]   # 11/16 左2人は右向き（ペンライトのファン・サッカー）・右2人は左向き（ラグビー・ボクサー）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
print('ok')
