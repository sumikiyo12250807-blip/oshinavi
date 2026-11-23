# -*- coding: utf-8 -*-
# 11/23 夕方の X（11/24 発売）の素材と候補の道具を、11/22（11/23 発売）の形から日付だけ進めて写す
import io, os
R = 'C:/Users/user/oshinavi/tmp/'
os.makedirs(R + 'x1123/x', exist_ok=True)
s = io.open(R + 'x1122/x/material_1123.py', encoding='utf-8').read()
for a, b in [("TOM, D2, D3 = '2026-11-23', '2026-11-24', '2026-11-25'", "TOM, D2, D3 = '2026-11-24', '2026-11-25', '2026-11-26'"),
             ("'tmp/x1122/x/material_1123.md'", "'tmp/x1123/x/material_1124.md'"),
             ("# 11/23(月・祝)発売 X投稿の素材", "# 11/24(火)発売 X投稿の素材")]:
    assert a in s, a
    s = s.replace(a, b)
io.open(R + 'x1123/x/material_1124.py', 'w', encoding='utf-8').write(s)
p = io.open(R + 'x1122/x/pick.py', encoding='utf-8').read().replace("tmp/x1122/x/", "tmp/x1123/x/")
io.open(R + 'x1123/x/pick.py', 'w', encoding='utf-8').write(p)
r = io.open(R + 'x1122/x/rank_1123.py', encoding='utf-8').read().replace('x1122', 'x1123').replace('1123', '1124')
io.open(R + 'x1123/x/rank_1124.py', 'w', encoding='utf-8').write(r)
