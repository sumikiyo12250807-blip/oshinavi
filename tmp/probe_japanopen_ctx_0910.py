# -*- coding: utf-8 -*-
"""「完売」「販売終了」がページのどこに、どの公演について出ているかを見る。"""
import re
import sys

sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
import rakuten_harvest as R

U = 'https://ticket.rakuten.co.jp/sports/rtep928/'
body = R.fetch(U)

for w in ['完売', '販売終了']:
    for m in re.finditer(w, body):
        i = m.start()
        ctx = re.sub(r'\s+', ' ', R.strip_tags(body[max(0, i - 700):i + 300]))
        print('=== %s @%d\n%s\n' % (w, i, ctx[-700:]))
