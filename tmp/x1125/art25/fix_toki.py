# -*- coding: utf-8 -*-
# 独立FC（fc.md）の 🟠1・🟡 を土岐麻子の記事に当てる（当たり1回ずつを確かめる）
import io
p = 'C:/Users/user/oshinavi/tmp/x1125/art25/tokiasako.md'
s = io.open(p, encoding='utf-8', newline='').read()
R = [
    ('公式サイトも、一般発売を「11月29日（日）10:00〜」と案内しているの。\n', ''),
    ('ここからが、これまでの顔ぶれの話。', 'ここからが、これまでの顔ぶれの話（Vol.1〜Vol.6）。'),
    ('そこへ、vol.8として土岐麻子が登場するの。', 'そして Vol.8 に、土岐麻子が登場するの。'),
    ('学生券は2,750円、劇場会員（プレミアム俱楽部）は4,950円なの。', '学生券は一般の半額、劇場会員（プレミアム倶楽部）は10%OFFなの。'),
    ('同じ5月には、北京、上海、深センをまわる中国ツアーも「Sentimental Journey」の名前で開かれたのよ。', '同じ5月には、北京、上海、深センをまわる中国ツアーも「Sentimental Journey」の名前で発表されていたのよ。'),
]
for a, b in R:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
