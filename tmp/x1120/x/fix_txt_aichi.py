# -*- coding: utf-8 -*-
# 11/20 TXT は愛知 2/20〜2/21（バンテリンドーム ナゴヤ）も 11/21 13:00 一般発売だった（カードを取り直して発覚）
#  ＝shu01・mat07 の直し案を post_fix/ に作る（予約済みの本文は触らない・すちこの OK のあとで入れ替える）
import io, os
P = 'C:/Users/user/oshinavi/tmp/x1120/x/post/'
O = 'C:/Users/user/oshinavi/tmp/x1120/x/post_fix/'
os.makedirs(O, exist_ok=True)
R = {
    'shu01.txt': [
        ('明日発売になるのは、12/19(土)と12/20(日)のみずほPayPayドーム福岡の公演と、来年1/30(土)と1/31(日)の京セラドーム大阪の公演だわ。',
         '明日発売になるのは、12/19(土)と12/20(日)のみずほPayPayドーム福岡、来年1/30(土)と1/31(日)の京セラドーム大阪、2/20(土)と2/21(日)のバンテリンドーム ナゴヤの公演だわ。'),
        ('13:00 TOMORROW X TOGETHER／福岡・大阪', '13:00 TOMORROW X TOGETHER／福岡・大阪・愛知'),
    ],
    'mat07.txt': [
        ('TOMORROW X TOGETHERは、12/19(土)と12/20(日)のみずほPayPayドーム福岡と、来年1/30(土)と1/31(日)の京セラドーム大阪の公演が、午後1時に一般発売なの。',
         'TOMORROW X TOGETHERは、12/19(土)と12/20(日)のみずほPayPayドーム福岡、来年1/30(土)と1/31(日)の京セラドーム大阪、2/20(土)と2/21(日)のバンテリンドーム ナゴヤの公演が、午後1時に一般発売なの。'),
        ('13:00 TOMORROW X TOGETHER／福岡・大阪', '13:00 TOMORROW X TOGETHER／福岡・大阪・愛知'),
    ],
}
for f, reps in R.items():
    s = io.open(P + f, encoding='utf-8').read()
    for a, b in reps:
        assert s.count(a) == 1, (f, a[:30])
        s = s.replace(a, b)
    io.open(O + f, 'w', encoding='utf-8').write(s)
print('ok')
