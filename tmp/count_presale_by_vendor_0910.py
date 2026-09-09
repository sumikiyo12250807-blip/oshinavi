# -*- coding: utf-8 -*-
"""売り場ごとに「発売前の枠（startDate が明日以降）」を数える。

2026-09-09 の実測は 楽天3枠／ぴあ1,559枠／e+146枠 だった。
今日の入口の作り直しでどう変わったかを、同じ数え方で出す。
"""
import datetime
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))


def vendor(t, e):
    u = t.get('url') or ''
    if 'rakuten' in u or 'linksynergy' in u:
        return 'rakuten'
    if 'eplus' in u:
        return 'eplus'
    if 'pia.jp' in u:
        return 'pia'
    ls = e.get('links') or {}
    for k in ('pia', 'rakuten', 'eplus', 'lawson'):
        if ls.get(k):
            return k
    return '(不明)'


pre, alive = {}, {}
for e in events:
    for t in e.get('tickets') or []:
        v = vendor(t, e)
        alive[v] = alive.get(v, 0) + 1
        sd = t.get('startDate')
        if sd and sd > TODAY:
            pre[v] = pre.get(v, 0) + 1

print('today=%s' % TODAY)
print('%-10s %8s %8s' % ('売り場', '発売前', '全枠'))
for v in sorted(set(list(pre) + list(alive)), key=lambda k: -alive.get(k, 0)):
    print('%-10s %8d %8d' % (v, pre.get(v, 0), alive.get(v, 0)))
