# -*- coding: utf-8 -*-
"""ボタンを埋めるAJAXの行き先を生HTMLから読む。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = R.fetch(U)
for i in [m.start() for m in re.finditer('ajax', body)]:
    seg = body[max(0, i - 600):i + 1200]
    if 'perf' in seg or 'url' in seg:
        print('===== ajax @%d\n%s\n' % (i, seg))
