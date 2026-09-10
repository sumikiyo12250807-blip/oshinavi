# -*- coding: utf-8 -*-
"""plan.md の「9/10 昼〜夜に続けること」を、片づいた形に差し替える。"""
import io
import sys

sys.stdout.reconfigure(encoding='utf-8')

add = io.open('tmp/plan_rakuten_done_0910.md', encoding='utf-8').read()
old = io.open('plan.md', encoding='utf-8').read()
a = old.index('# ✅ 9/10 に片づいたこと')
b = old.index('# 🚨 消さずに残した／直す必要があるもの')
io.open('plan.md', 'w', encoding='utf-8').write(old[:a] + add + '\n' + old[b:])
print('plan.md を差し替えたわ')
