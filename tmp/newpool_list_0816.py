# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の _genre / _piaSub 下書きを一覧化。人の判断が要る子（_piaSub空 or その他）に印。"""
import re, json, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

raw = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
pool = [e for e in EVENTS if e.get('genre') == 'new']

print("新着プール %d件" % len(pool))
need = []
for e in pool:
    sub = e.get('_piaSub') or ''
    g = e.get('_genre') or ''
    ex = e.get('_extraGenres') or []
    mark = ''
    if not sub or 'その他' in sub:
        mark = '⚠️'
        need.append(e)
    print("%s id%-5s %-8s %-14s %-22s %s" % (
        mark or '  ', e['id'], g, "+" + ",".join(ex) if ex else "", sub[:20],
        (e.get('artist') or e.get('name') or '')[:36]))

print()
print("_genre内訳:", dict(Counter(e.get('_genre') for e in pool)))
print("人の判断が要る子:", len(need), [e['id'] for e in need])
