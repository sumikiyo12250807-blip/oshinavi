# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）の中身を、下書きジャンル(_genre)別に並べて出す。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
pool = [e for e in events if e.get('genre') == 'new']

by = {}
for e in pool:
    by.setdefault(e.get('_genre') or '(下書きなし)', []).append(e)

with open('tmp/newpool_0910.txt', 'w', encoding='utf-8') as f:
    f.write('新着プール %d件\n' % len(pool))
    for g in sorted(by, key=lambda k: -len(by[k])):
        f.write('\n== _genre=%s  %d件\n' % (g, len(by[g])))
        for e in sorted(by[g], key=lambda x: x['id']):
            src = []
            for k in ('pia', 'eplus', 'rakuten', 'lawson'):
                if (e.get('links') or {}).get(k):
                    src.append(k)
            f.write('  id=%-5s %-46s %s %s [%s]\n'
                    % (e['id'], e['name'][:46], e['date'], e.get('prefecture') or '',
                       '/'.join(src) or 'リンク無し'))
print('新着プール %d件 / 下書きジャンル %d種 → tmp/newpool_0910.txt' % (len(pool), len(by)))
for g in sorted(by, key=lambda k: -len(by[k])):
    print('   %-14s %d件' % (g, len(by[g])))
