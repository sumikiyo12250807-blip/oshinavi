# -*- coding: utf-8 -*-
# 11/22 夕方の X（11/23 発売）の素材と候補の道具を、11/21（11/22 発売）の形から日付だけ進めて写す
import io
R = 'C:/Users/user/oshinavi/tmp/'
s = io.open(R + 'x1121/x/material_1122.py', encoding='utf-8').read()
for a, b in [("TOM, D2, D3 = '2026-11-22', '2026-11-23', '2026-11-24'", "TOM, D2, D3 = '2026-11-23', '2026-11-24', '2026-11-25'"),
             ("'tmp/x1121/x/material_1122.md'", "'tmp/x1122/x/material_1123.md'"),
             ("# 11/22(日)発売 X投稿の素材", "# 11/23(月・祝)発売 X投稿の素材")]:
    assert a in s, a
    s = s.replace(a, b)
io.open(R + 'x1122/x/material_1123.py', 'w', encoding='utf-8').write(s)
p = io.open(R + 'x1121/x/pick.py', encoding='utf-8').read()
io.open(R + 'x1122/x/pick_src.txt', 'w', encoding='utf-8').write(p)
print('ok')
