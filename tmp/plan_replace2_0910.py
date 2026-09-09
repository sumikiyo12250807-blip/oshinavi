# -*- coding: utf-8 -*-
"""plan.md の先頭を 9/10 朝の便のあとの形に差し替える（9/9の記録はそのまま残す）。"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

head = io.open('tmp/plan_head2_0910.md', encoding='utf-8').read()
old = io.open('plan.md', encoding='utf-8').read()
key = '# 📚 以下は9/9の記録（そのまま残す）'
i = old.index(key)
io.open('plan.md', 'w', encoding='utf-8').write(head + '\n---\n\n' + old[i:])
print('plan.md を差し替えたわ')
