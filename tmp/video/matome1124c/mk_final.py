# -*- coding: utf-8 -*-
# final_1121.py（ロックの形）から 11/23 J-POP・ロックの全編書き出しの道具 final_1123m.py を作る
import io
D = 'C:/Users/user/oshinavi/tmp/video/matome1124c/'
s = io.open(D + 'final_1121.py', encoding='utf-8').read()
for a, b in [('# 11/21 ロックまとめ：すちこ「オッケー」（0.1gの誤算の行はそのまま）→ 全編の書き出し', '# 11/23 J-POP・ロック（ビジュアル系・同じ服で動く）：すちこ「ま　よくなった　うん」→ 全編の書き出し'),
             ('rock_1121.json', 'music_1123.json'), ('oshinavi_1121_rock_matome', 'oshinavi_1123_jpoprock_matome'),
             ('final_1121', 'final_1123m'), ('CUT = 40.967', 'CUT = 44.292')]:
    assert a in s, a
    s = s.replace(a, b)
assert 'rock_1121' not in s
io.open(D + 'final_1123m.py', 'w', encoding='utf-8').write(s)
print('ok')
