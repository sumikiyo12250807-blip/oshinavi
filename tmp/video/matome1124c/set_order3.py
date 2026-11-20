# -*- coding: utf-8 -*-
# 反転すると服の字が鏡文字になる（サッカー 10→01・野球 Oshinavi・チア Oshi・ボクサー OSHINAVI・バスケ Oshi 23・ファンのタオル OSHINAVI）
#   ＝反転（m）は字の無い子だけ＝相撲 m1・ラグビー m3・女子プロレス m4。ほかは シートの向き（w）のまま
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
r = io.open(D + 'render.py', encoding='utf-8').read()
a = r.index('ORDER = ['); b = r.index('\n', a)
r = r[:a] + "ORDER = ['w2', 'm3', 'w5', 'm4', 'w8', 'm1', 'w7', 'w9', 'w6']   # 11/16 反転は字の無い子だけ（相撲・ラグビー・女子プロレス）＝鏡文字にしない・締めはチア w6" + r[b:]
a = r.index('PARADE = ['); b = r.index('\n', a)
r = r[:a] + "PARADE = [('w2', _R[0]), ('w5', _R[1]), ('m3', _R[2]), ('m1', _R[3])]   # 11/16 左2人は右向き（サッカー・野球）・右2人は左向き（ラグビー・相撲＝字の無い子を反転）＝真ん中を向く" + r[b:]
io.open(D + 'render.py', 'w', encoding='utf-8').write(r)
print('ok')
