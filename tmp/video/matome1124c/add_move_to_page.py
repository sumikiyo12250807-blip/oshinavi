# -*- coding: utf-8 -*-
# 確認ページの試し動画の先頭に「同じ服で動きを入れた版」（26〜42 秒）を足す
import io, base64
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
p = D + 'board_1123m.html'
s = io.open(p, encoding='utf-8').read()
v = base64.b64encode(open(D + 'clip_move_s.mp4', 'rb').read()).decode()
a = '<section><h2>試し動画</h2><div class="vids">\n'
assert a in s
fig = ('<figure><video controls playsinline preload="metadata" src="data:video/mp4;base64,%s"></video>'
       '<figcaption>🆕 同じ服で動きを入れた版 26〜42秒＝2拍ごとに「元の絵」と「同じ服で動いた絵」（叫ぶ・ギターを掲げる・キャンドルを掲げる など）が入れ替わる（すちこ「先のデスメタルみたいにおなじ服のキャラで動きを出してほしい」）。下の2本は動きを入れる前</figcaption></figure>\n') % v
s = s.replace(a, a + fig, 1)
io.open(p, 'w', encoding='utf-8').write(s)
print('ok', len(s) // 1024, 'KB')
