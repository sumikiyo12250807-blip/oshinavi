# -*- coding: utf-8 -*-
"""plan.md の「今日やること」の直後に、楽天まわりの続きを差し込む。"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

add = io.open('tmp/plan_add_0910b.md', encoding='utf-8').read()
old = io.open('plan.md', encoding='utf-8').read()
key = '# 🚨 消さずに残した／直す必要があるもの'
i = old.index(key)
io.open('plan.md', 'w', encoding='utf-8').write(old[:i] + add + '\n' + old[i:])
print('plan.md に差し込んだわ')
