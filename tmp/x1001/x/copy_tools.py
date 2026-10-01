# -*- coding: utf-8 -*-
# 昨日（tmp/x0930/x）のX素材の道具を 10/2発売用に写す（日付とフォルダだけ置き換え）
import io
root = 'C:/Users/user/oshinavi/'
REP = [('tmp/x0930/x', 'tmp/x1001/x'),
       ("TOM, D2, D3 = '2026-10-01', '2026-10-02', '2026-10-03'", "TOM, D2, D3 = '2026-10-02', '2026-10-03', '2026-10-04'"),
       ("for d in ('2026-10-02', '2026-10-03'):", "for d in ('2026-10-03', '2026-10-04'):"),
       ('material_1001', 'material_1002'), ('10/1(木)発売', '10/2(金)発売')]
for f, g in (('ev.py', 'ev.py'), ('material_1001.py', 'material_1002.py'), ('future_by_post.py', 'future_by_post.py')):
    s = io.open(root + 'tmp/x0930/x/' + f, encoding='utf-8').read()
    for a, b in REP:
        s = s.replace(a, b)
    io.open(root + 'tmp/x1001/x/' + g, 'w', encoding='utf-8').write(s)
print('ok')
