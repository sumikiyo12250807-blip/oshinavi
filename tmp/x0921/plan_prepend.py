# -*- coding: utf-8 -*-
"""plan.md の先頭に今朝のセクションを足す（古い分は下に残す＝新しい決定はいちばん上）。"""
import io, sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
head = io.open('tmp/x0921/plan_head.md', encoding='utf-8').read()
old = io.open('plan.md', encoding='utf-8').read()
# 前の「9/21 朝はここから」は役目を終えたので「（済）」を付けて下に残す
old = old.replace('# ▶▶ 9/21(月・祝) 朝はここから',
                  '# ▶▶（済）9/21(月・祝) 朝はここから', 1)
io.open('plan.md', 'w', encoding='utf-8').write(head + old)
print('plan.md の先頭に9/21朝の結果と昼の段取りを足した（%.1fKB → %.1fKB）'
      % (len(old) / 1024, (len(head) + len(old)) / 1024))
