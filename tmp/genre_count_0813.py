# -*- coding: utf-8 -*-
"""ジャンル別の件数（フィルターの畳み方を決める材料）"""
import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

ev = extract_events_array('index.html')
c = collections.Counter()
for e in ev:
    c[e.get('genre')] += 1
    for g in e.get('extraGenres') or []:
        c[g] += 1
print('全%d件' % len(ev))
for g, n in c.most_common():
    print('%-12s %4d' % (g, n))
