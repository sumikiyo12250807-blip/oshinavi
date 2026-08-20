# -*- coding: utf-8 -*-
"""ジャンル別の件数（表示中のverified=trueのみ）。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
c = {}
for e in EV:
    if e.get('verified') is not True:
        continue
    c[e.get('genre')] = c.get(e.get('genre'), 0) + 1
for k, v in sorted(c.items(), key=lambda x: -x[1]):
    print('%-11s %d' % (k, v))
