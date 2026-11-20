# -*- coding: utf-8 -*-
# すちこ OK「案も入れて作って」＝「こえを からして おうえん したいわ」（49.7 秒）からペンライトのファン w9（oshinavi.jp で検索の行まで）
#   バスケ w8 は「ほかにもあるわ わすれないでね」まで。締めの下の段は ファン→バスケ に替える（同じ本で2回にしない）＝左2人右向き（バスケ・サッカー）・右2人左向き（ラグビー・相撲）
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + "ORDER = ['w7', 'w1', 'w4', 'm4', 'w2', 'w5', 'm3', 'a2', 'w8', 'w9', 'w6']   # 11/16 歌う行と衣装を合わせる・応援の行はペンライトのファン w9・締めはチア w6" + r[b:]
old = "LINE_AT = [0.0, 11.7, 14.9, 19.6, 21.4, 24.6, 31.9, 38.2, 45.1]"
assert old in r
r = r.replace(old, "LINE_AT = [0.0, 11.7, 14.9, 19.6, 21.4, 24.6, 31.9, 38.2, 45.1, 49.7]")
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('w8', _R[0]), ('w2', _R[1]), ('m3', _R[2]), ('m1', _R[3])]   # 11/16 左2人は右向き（バスケ・サッカー）・右2人は左向き（ラグビー・相撲）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
print('ok')
